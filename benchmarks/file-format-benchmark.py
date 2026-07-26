#!/usr/bin/env python3
"""
Parquet vs ORC vs Avro vs CSV — a reproducible file-format benchmark.

Companion to https://dataarchitect.studio/essays/parquet-vs-orc-vs-avro-benchmark/

Measures, on one synthetic but realistically-shaped analytical dataset:
  1. on-disk size, per format and codec
  2. write time
  3. full-scan read time (all columns)
  4. column-pruned read time (2 of 11 columns) — the core columnar claim
  5. a filtered aggregation through DuckDB
  6. single-record retrieval (the row-based case)

Design notes, because they determine the results:
  - The row generator is seeded, so the dataset is byte-identical across runs.
  - The column mix is deliberately varied: low-cardinality strings (which
    dictionary-encode almost for free), high-cardinality integers, timestamps,
    floats, and one free-text column with real entropy. A benchmark made only of
    low-cardinality columns flatters columnar formats enormously; one made only
    of free text flatters them barely at all. Most real tables are a mix.
  - Every timing is the MEDIAN of N trials, not the best. Best-of-N benchmarks
    published as headline numbers are how vendors win comparisons.
  - The OS page cache is NOT cleared between trials (this needs root). These are
    therefore warm-cache numbers, which favours the smaller files less than cold
    reads would. Stated plainly rather than quietly.

Usage:
    pip install pyarrow fastavro duckdb cramjam
    python3 file-format-benchmark.py --rows 3000000 --trials 3

    # or one stage at a time, merging into the same results file:
    python3 file-format-benchmark.py --only parquet --rows 3000000
    python3 file-format-benchmark.py --only orc     --rows 3000000
    python3 file-format-benchmark.py --only csv     --rows 3000000
    python3 file-format-benchmark.py --only avro    --rows 3000000
    python3 file-format-benchmark.py --only duckdb  --rows 3000000

Staged runs regenerate the dataset from the same seed each time, so the bytes are
identical; --workdir keeps the written files between stages.
"""

import argparse, json, os, shutil, statistics, string, sys, tempfile, time
from datetime import datetime, timedelta

import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.orc as orc
import pyarrow.csv as pacsv
import numpy as np

SEED = 20260726


# --------------------------------------------------------------------------
# dataset
# --------------------------------------------------------------------------
def build_table(n_rows: int) -> pa.Table:
    """An order-line fact table with a realistic spread of column types."""
    rng = np.random.default_rng(SEED)

    countries = ["US", "GB", "DE", "FR", "IN", "JP", "BR", "CA", "AU", "NL"]
    channels = ["web", "mobile", "partner", "retail"]
    statuses = ["placed", "shipped", "delivered", "returned", "cancelled"]
    words = ["expedite", "gift", "fragile", "backorder", "replacement", "bulk",
             "warranty", "damaged", "resend", "priority", "signature", "hold"]

    base = int(datetime(2024, 1, 1).timestamp() * 1_000_000)
    # timestamps roughly ascending, as they are in an append-only fact table:
    # this is what lets columnar encodings do well on the time column.
    order_ts = base + np.sort(rng.integers(0, 730 * 86_400 * 1_000_000, n_rows))

    # a free-text column with genuine entropy — the anti-columnar case
    idx = rng.integers(0, len(words), (n_rows, 3))
    notes = np.array([" ".join(words[i] for i in row) for row in idx], dtype=object)

    return pa.table({
        "order_id":     pa.array(np.arange(1, n_rows + 1), type=pa.int64()),
        "order_ts":     pa.array(order_ts, type=pa.timestamp("us")),
        "customer_id":  pa.array(rng.integers(1, 400_000, n_rows), type=pa.int64()),
        "product_sku":  pa.array([f"SKU-{i:06d}" for i in rng.integers(0, 50_000, n_rows)]),
        "country":      pa.array(rng.choice(countries, n_rows)),
        "channel":      pa.array(rng.choice(channels, n_rows)),
        "status":       pa.array(rng.choice(statuses, n_rows)),
        "quantity":     pa.array(rng.integers(1, 12, n_rows), type=pa.int32()),
        "unit_price":   pa.array(np.round(rng.uniform(2, 900, n_rows), 2), type=pa.float64()),
        "discount_pct": pa.array(np.round(rng.uniform(0, 0.4, n_rows), 3), type=pa.float64()),
        "notes":        pa.array(notes, type=pa.string()),
    })


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def timed(fn, trials):
    """Median wall-clock seconds over `trials` runs. Median, not best."""
    out = []
    for _ in range(trials):
        t0 = time.perf_counter()
        fn()
        out.append(time.perf_counter() - t0)
    return statistics.median(out)


def mb(path):
    return os.path.getsize(path) / (1024 * 1024)


def write_avro(table, path, codec):
    import fastavro
    schema = {
        "type": "record", "name": "order_line",
        "fields": [
            {"name": "order_id", "type": "long"},
            {"name": "order_ts", "type": {"type": "long", "logicalType": "timestamp-micros"}},
            {"name": "customer_id", "type": "long"},
            {"name": "product_sku", "type": "string"},
            {"name": "country", "type": "string"},
            {"name": "channel", "type": "string"},
            {"name": "status", "type": "string"},
            {"name": "quantity", "type": "int"},
            {"name": "unit_price", "type": "double"},
            {"name": "discount_pct", "type": "double"},
            {"name": "notes", "type": "string"},
        ],
    }
    cols = {c: table.column(c).to_pylist() for c in table.column_names}
    ts = [int(v.timestamp() * 1_000_000) for v in cols["order_ts"]]
    cols["order_ts"] = ts
    records = [dict(zip(cols.keys(), vals)) for vals in zip(*cols.values())]
    with open(path, "wb") as fh:
        fastavro.writer(fh, schema, records, codec=codec)


def read_avro(path, columns=None):
    import fastavro
    n = 0
    with open(path, "rb") as fh:
        for rec in fastavro.reader(fh):
            # Avro is row-based: even wanting two fields, the whole record is
            # decoded. Touching the fields keeps the loop honest.
            if columns:
                for c in columns:
                    _ = rec[c]
            n += 1
    return n


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=3_000_000)
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--avro-rows", type=int, default=300_000,
                    help="Avro is benchmarked on a subset; the pure-Python "
                         "writer/reader is orders of magnitude slower than the "
                         "compiled Arrow paths, so mixing them at full scale "
                         "measures the library, not the format.")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--out", default="benchmark-results.json")
    ap.add_argument("--only", default="all",
                    choices=["all", "parquet", "orc", "csv", "avro", "duckdb"],
                    help="run one stage and merge into --out")
    ap.add_argument("--workdir", default=None,
                    help="reuse a directory for written files across staged runs")
    ap.add_argument("--codec", default=None,
                    help="restrict a stage to one codec, e.g. --only parquet --codec gzip")
    args = ap.parse_args()
    stage = args.only
    keep_codec = (lambda c: args.codec is None or c.lower() == args.codec.lower())

    d = args.workdir or tempfile.mkdtemp(prefix="fmtbench-")
    os.makedirs(d, exist_ok=True)

    # merge into an existing results file when running staged
    if os.path.exists(args.out):
        results = json.load(open(args.out))
    else:
        results = {"config": {}, "size_mb": {}, "write_s": {},
                   "read_full_s": {}, "read_2col_s": {}}
    results["config"].update({
        "rows": args.rows, "avro_rows": args.avro_rows, "trials": args.trials,
        "seed": SEED, "pyarrow": pa.__version__, "python": sys.version.split()[0],
    })

    print(f"building {args.rows:,} rows ...", flush=True)
    t = build_table(args.rows)
    results["config"]["columns"] = len(t.column_names)
    results["config"]["in_memory_mb"] = round(t.nbytes / 1024 / 1024, 1)
    print(f"  {t.num_rows:,} rows x {len(t.column_names)} cols, "
          f"{t.nbytes/1024/1024:.0f} MB uncompressed in memory\n", flush=True)

    two = ["country", "unit_price"]   # 2 of 11 columns

    # ---- Parquet, three codecs -------------------------------------------
    for codec in ([c for c in ["snappy","zstd","gzip"] if keep_codec(c)] if stage in ("all","parquet") else []):
        p = os.path.join(d, f"data-{codec}.parquet")
        key = f"parquet/{codec}"
        results["write_s"][key] = timed(
            lambda: pq.write_table(t, p, compression=codec), args.trials)
        results["size_mb"][key] = mb(p)
        results["read_full_s"][key] = timed(lambda: pq.read_table(p), args.trials)
        results["read_2col_s"][key] = timed(
            lambda: pq.read_table(p, columns=two), args.trials)
        print(f"parquet/{codec:6s} {results['size_mb'][key]:8.1f} MB", flush=True)

    # ---- ORC, two codecs --------------------------------------------------
    for codec in ([c for c in ["ZLIB","SNAPPY"] if keep_codec(c)] if stage in ("all","orc") else []):
        p = os.path.join(d, f"data-{codec}.orc")
        key = f"orc/{codec.lower()}"
        results["write_s"][key] = timed(
            lambda: orc.write_table(t, p, compression=codec), args.trials)
        results["size_mb"][key] = mb(p)
        results["read_full_s"][key] = timed(lambda: orc.read_table(p), args.trials)
        results["read_2col_s"][key] = timed(
            lambda: orc.read_table(p, columns=two), args.trials)
        print(f"orc/{codec.lower():10s} {results['size_mb'][key]:8.1f} MB", flush=True)

    # ---- CSV, raw and gzipped --------------------------------------------
    p = os.path.join(d, "data.csv")
    if stage in ("all", "csv"):
        results["write_s"]["csv/none"] = timed(lambda: pacsv.write_csv(t, p), args.trials)
        results["size_mb"]["csv/none"] = mb(p)
        results["read_full_s"]["csv/none"] = timed(lambda: pacsv.read_csv(p), args.trials)
        # CSV cannot prune: reading 2 columns still parses every byte of every row.
        results["read_2col_s"]["csv/none"] = timed(
            lambda: pacsv.read_csv(p, convert_options=pacsv.ConvertOptions(include_columns=two)),
            args.trials)
        print(f"csv/none      {results['size_mb']['csv/none']:8.1f} MB", flush=True)

        import gzip
        pgz = os.path.join(d, "data.csv.gz")
        def gz():
            with open(p, "rb") as fi, gzip.open(pgz, "wb", compresslevel=6) as fo:
                shutil.copyfileobj(fi, fo, 1024 * 1024)
        results["write_s"]["csv/gzip"] = timed(gz, 1)
        results["size_mb"]["csv/gzip"] = mb(pgz)
        print(f"csv/gzip      {results['size_mb']['csv/gzip']:8.1f} MB", flush=True)

    # ---- Avro, on a subset -----------------------------------------------
    sub = t.slice(0, args.avro_rows)
    avro = results.get("avro_subset") or {"rows": args.avro_rows, "size_mb": {},
                                          "write_s": {}, "read_full_s": {}, "read_2col_s": {}}
    for codec in ([c for c in ["null","deflate","snappy"] if keep_codec(c)] if stage in ("all","avro") else []):
        p2 = os.path.join(d, f"data-{codec}.avro")
        try:
            avro["write_s"][codec] = timed(lambda: write_avro(sub, p2, codec), 1)
        except Exception as e:
            print(f"avro/{codec}: skipped ({e})"); continue
        avro["size_mb"][codec] = mb(p2)
        avro["read_full_s"][codec] = timed(lambda: read_avro(p2), 1)
        avro["read_2col_s"][codec] = timed(lambda: read_avro(p2, two), 1)
        print(f"avro/{codec:9s} {avro['size_mb'][codec]:8.1f} MB "
              f"({args.avro_rows:,} rows)", flush=True)
    if stage in ("all", "avro"):
        # Parquet + ORC on the identical subset, so the Avro comparison is fair.
        for name, fn in [("parquet/zstd", lambda pth: pq.write_table(sub, pth, compression="zstd")),
                         ("orc/zlib",     lambda pth: orc.write_table(sub, pth, compression="ZLIB"))]:
            pth = os.path.join(d, "sub-" + name.replace("/", "-"))
            fn(pth); avro["size_mb"][name + " (same subset)"] = mb(pth)
        results["avro_subset"] = avro

    # ---- DuckDB: a filtered aggregation, Parquet vs CSV -------------------
    if stage in ("all", "duckdb"):
        import duckdb
        con = duckdb.connect()
        q_pq = (f"SELECT country, sum(quantity*unit_price*(1-discount_pct)) "
                f"FROM read_parquet('{os.path.join(d,'data-zstd.parquet')}') "
                f"WHERE status='delivered' GROUP BY country")
        q_csv = (f"SELECT country, sum(quantity*unit_price*(1-discount_pct)) "
                 f"FROM read_csv_auto('{os.path.join(d,'data.csv')}') "
                 f"WHERE status='delivered' GROUP BY country")
        results["duckdb_agg_s"] = {
            "parquet/zstd": timed(lambda: con.execute(q_pq).fetchall(), args.trials),
            "csv/none":     timed(lambda: con.execute(q_csv).fetchall(), args.trials),
        }

    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=2)
    print(f"\nwrote {args.out}")
    if not args.keep and not args.workdir:
        shutil.rmtree(d)
    else:
        print(f"data kept in {d}")


if __name__ == "__main__":
    main()
