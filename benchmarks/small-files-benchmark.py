#!/usr/bin/env python3
"""
The small-file problem, measured.

STATUS: WRITTEN BUT NOT YET RUN. Do not publish any numbers from this file, and
do not link it from an essay, until it has been executed on a reference machine
and a results JSON exists beside it. The site's rule is that published figures
are measured figures.

--------------------------------------------------------------------------------

"Small files kill query performance, so compact your tables" is one of the most
repeated claims in lakehouse writing, including on this site, where compaction is
asserted roughly twenty times and measured zero times. This script measures it.

The design holds the DATA CONSTANT and varies only the FILE COUNT. Same rows,
same columns, same codec, same total bytes -- written once as a single file, then
as 10, 100, 1000 and 5000 files. Anything that changes is therefore attributable
to fragmentation rather than to volume.

Four things are timed at each file count:

  1. open/plan   -- just discovering and opening the dataset, no rows read.
                    This is where per-file overhead should show up most clearly:
                    every file means a footer read and a metadata parse.
  2. full scan   -- read every column, every row.
  3. column scan -- read 2 of N columns. Columnar pruning should still work, but
                    the per-file fixed cost is paid once per file regardless.
  4. duckdb agg  -- a filtered GROUP BY through DuckDB, i.e. what a query engine
                    actually does, rather than a raw Arrow read.

The interesting quantity is not absolute seconds, which are a property of this
machine, but WHERE THE KNEE IS: the file count at which per-file overhead starts
to dominate the useful work. That is the number that tells you whether your
compaction job is earning its runtime or just burning money on schedule.

Requires:
    pip install pyarrow duckdb

Run:
    python3 small-files-benchmark.py                    # default 2,000,000 rows
    python3 small-files-benchmark.py --rows 5000000
    python3 small-files-benchmark.py --counts 1,10,100  # fewer configs, faster

Local disk only. Nothing uploaded, no credentials.

A caveat to state in any essay built on this: LOCAL DISK UNDERSTATES THE PROBLEM.
On object storage every file is an HTTP request with latency measured in tens of
milliseconds, so the per-file cost there is far higher than anything measurable
here. Treat these numbers as a floor, not an estimate.
"""

import argparse
import datetime
import json
import os
import shutil
import statistics
import sys
import tempfile
import time

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq


def make_table(n, seed=20260929):
    """Eleven columns, mixed cardinality -- same shape as the format benchmark
    so the two are comparable."""
    import random

    rnd = random.Random(seed)
    countries = ["US", "GB", "IN", "DE", "BR", "JP", "AU", "CA"]
    statuses = ["new", "paid", "shipped", "returned", "cancelled"]
    return pa.table(
        {
            "order_id": pa.array(range(n), pa.int64()),
            "customer_id": pa.array([rnd.randrange(250_000) for _ in range(n)], pa.int64()),
            "product_id": pa.array([rnd.randrange(5_000) for _ in range(n)], pa.int64()),
            "country": pa.array([countries[i % len(countries)] for i in range(n)]),
            "status": pa.array([statuses[rnd.randrange(len(statuses))] for _ in range(n)]),
            "quantity": pa.array([rnd.randrange(1, 12) for _ in range(n)], pa.int32()),
            "unit_price": pa.array([round(rnd.uniform(1, 500), 2) for _ in range(n)], pa.float64()),
            "discount": pa.array([round(rnd.uniform(0, 0.4), 3) for _ in range(n)], pa.float64()),
            "ts": pa.array([1750000000 + i for i in range(n)], pa.int64()),
            "channel": pa.array(["web" if i % 3 else "store" for i in range(n)]),
            "note": pa.array(["order note %d padding padding" % i for i in range(n)]),
        }
    )


def write_as(table, root, n_files, codec):
    """Write the same table split evenly across n_files Parquet files."""
    os.makedirs(root, exist_ok=True)
    rows = table.num_rows
    per = (rows + n_files - 1) // n_files
    for i in range(n_files):
        chunk = table.slice(i * per, min(per, rows - i * per))
        if chunk.num_rows == 0:
            break
        pq.write_table(chunk, os.path.join(root, f"part-{i:06d}.parquet"), compression=codec)


def dir_bytes(root):
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(root) for f in fs)


def timed(fn, trials):
    """Median of n trials. One warm-up run is discarded."""
    fn()
    out = []
    for _ in range(trials):
        t0 = time.perf_counter()
        fn()
        out.append(time.perf_counter() - t0)
    return statistics.median(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=2_000_000)
    ap.add_argument("--counts", default="1,10,100,1000,5000")
    ap.add_argument("--codec", default="zstd")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--workdir", default=None)
    args = ap.parse_args()

    counts = [int(c) for c in args.counts.split(",")]
    workdir = args.workdir or tempfile.mkdtemp(prefix="smallfiles-")
    table = make_table(args.rows)

    try:
        import duckdb
        duckdb_version = duckdb.__version__
    except ImportError:
        duckdb = None
        duckdb_version = None

    results = []
    for n_files in counts:
        root = os.path.join(workdir, f"n{n_files}")
        shutil.rmtree(root, ignore_errors=True)
        write_as(table, root, n_files, args.codec)

        total = dir_bytes(root)
        actual = len([f for f in os.listdir(root) if f.endswith(".parquet")])

        # 1. open/plan only -- no rows read
        def plan():
            d = ds.dataset(root, format="parquet")
            d.schema
            list(d.get_fragments())

        # 2. full scan
        def full():
            ds.dataset(root, format="parquet").to_table()

        # 3. two columns
        def cols():
            ds.dataset(root, format="parquet").to_table(columns=["customer_id", "unit_price"])

        row = dict(
            files=actual,
            bytes=total,
            avg_file_kb=round(total / actual / 1024, 1),
            plan_s=round(timed(plan, args.trials), 4),
            full_scan_s=round(timed(full, args.trials), 4),
            two_col_s=round(timed(cols, args.trials), 4),
        )

        # 4. what an engine actually does
        if duckdb:
            con = duckdb.connect()
            q = (f"select country, count(*) c, sum(quantity*unit_price) rev "
                 f"from read_parquet('{root}/*.parquet') "
                 f"where status = 'paid' group by country")

            def agg():
                con.execute(q).fetchall()

            row["duckdb_agg_s"] = round(timed(agg, args.trials), 4)
            con.close()

        results.append(row)
        print(f"  {actual:>6} files  {row['avg_file_kb']:>9.1f} KB avg  "
              f"plan {row['plan_s']:.4f}s  full {row['full_scan_s']:.4f}s  "
              f"2col {row['two_col_s']:.4f}s"
              + (f"  duckdb {row['duckdb_agg_s']:.4f}s" if duckdb else ""))
        shutil.rmtree(root, ignore_errors=True)

    base = results[0]
    for r in results:
        for k in ("plan_s", "full_scan_s", "two_col_s", "duckdb_agg_s"):
            if k in r and base.get(k):
                # strip only the trailing "_s", not every occurrence of it --
                # a naive replace turns "full_scan_s" into "full_can_vs_single_file"
                r[k[:-2] + "_vs_single_file"] = round(r[k] / base[k], 1)
        # Storage is a result in its own right, not a constant. See caveats.
        r["bytes_vs_single_file"] = round(r["bytes"] / base["bytes"], 2)
        # Does column pruning still pay? <1.0 means reading 2 of 11 columns
        # costs MORE than reading all 11.
        r["pruning_speedup"] = round(r["full_scan_s"] / r["two_col_s"], 2)

    meta = {
        "rows": args.rows,
        "columns": table.num_columns,
        "codec": args.codec,
        "trials": args.trials,
        "in_memory_mb": round(table.nbytes / 1e6, 1),
        "pyarrow": pa.__version__,
        "duckdb": duckdb_version,
        "python": sys.version.split()[0],
        "generated": datetime.date.today().isoformat(),
        "caveats": [
            "Local disk. On object storage each file is an HTTP round trip, so "
            "per-file overhead is far higher there. These numbers are a floor.",
            "Warm page cache; clearing it needs root. Cold reads would widen the "
            "gap between few large files and many small ones.",
            "ROW COUNT is held constant; TOTAL BYTES ARE NOT, and that is a "
            "result rather than a flaw. Splitting the same rows across more "
            "files inflates total size, because compression and dictionary "
            "encoding work on smaller blocks and every file carries its own "
            "footer. The read slowdown is therefore partly more bytes to read "
            "and partly per-file overhead; this benchmark does not separate "
            "the two.",
            "Default row group sizes. A single 2M-row file still contains many "
            "row groups, which is why the one-file case is not a pathological "
            "best case.",
        ],
    }

    dest = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"results-small-files-{meta['generated']}.json",
    )
    with open(dest, "w") as fh:
        json.dump({"config": meta, "results": results}, fh, indent=1)
    print(f"\nwrote {dest}")
    shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
