#!/usr/bin/env python3
"""
Copy-on-write delete amplification, and the merge-on-read availability gap.

Companion to https://dataarchitect.studio/essays/merge-on-read-vs-copy-on-write/

Two things are measured here.

1.  COPY-ON-WRITE DELETE AMPLIFICATION.  Deleting a small fraction of rows from
    a columnar table does not rewrite a small fraction of bytes.  It rewrites
    every data file that contains at least one matching row.  This script
    measures the ratio of bytes written to bytes logically removed, across
    three selectivities and two engines.

2.  WHETHER MERGE-ON-READ IS AVAILABLE AT ALL from Python.  Both engines accept
    a merge-on-read setting.  Neither honours it, as of the versions pinned in
    the results file.  pyiceberg says so out loud; delta-rs does not.  The
    script records what each one actually did rather than what it was asked to
    do, because that difference is the point.

Requires:
    pip install pyarrow deltalake "pyiceberg[sql-sqlite,pyarrow]"

Run:
    python3 delete-mode-benchmark.py                  # default 200k rows
    python3 delete-mode-benchmark.py --rows 1000000
    python3 delete-mode-benchmark.py --only delta     # or: iceberg

Everything runs against local disk in a temp directory; nothing is uploaded and
no cloud credentials are needed.  Results print as a table and are written to
results-delete-mode-<date>.json next to this script.
"""

import argparse
import datetime
import json
import os
import shutil
import sys
import tempfile
import warnings

import pyarrow as pa

# Selectivity -> (label, delta-rs SQL predicate, pyiceberg predicate).
# Predicates are chosen so the matching rows are spread across EVERY data file
# rather than clustered in one.  That is the realistic case: a GDPR erasure or
# a late-arriving correction does not conveniently land in a single file.
CASES = [
    ("0.1%", "sel1000 = 5", "sel1000 == 5"),
    ("1%", "grp = 7", "grp == 7"),
    ("10%", "grp < 10", "grp < 10"),
]


def make_table(n):
    """A deliberately ordinary table: two ints, a float, a short string."""
    return pa.table(
        {
            "id": pa.array(range(n), pa.int64()),
            "grp": pa.array([i % 100 for i in range(n)], pa.int64()),
            "sel1000": pa.array([i % 1000 for i in range(n)], pa.int64()),
            "val": pa.array([float(i) * 1.5 for i in range(n)], pa.float64()),
            "txt": pa.array(["row-%d-padding-padding" % i for i in range(n)]),
        }
    )


def data_bytes(root, exts=(".parquet", ".bin", ".puffin", ".avro")):
    """Bytes on disk, split into data files and everything else.

    Delete files matter as much as data files here: a merge-on-read engine is
    supposed to write a small delete artifact instead of a large data file, so
    counting only .parquet would hide exactly the thing being measured.
    """
    data = other = 0
    names = []
    for r, _, fs in os.walk(root):
        for f in fs:
            size = os.path.getsize(os.path.join(r, f))
            if f.endswith(".parquet"):
                data += size
                names.append(f)
            elif f.endswith((".bin", ".puffin")):
                data += size
                names.append(f)
            else:
                other += size
    return data, other, names


def run_delta(rows, tbl, label, predicate, workdir):
    from deltalake import DeltaTable, write_deltalake

    results = []
    for mode, props in (
        ("copy-on-write", None),
        ("merge-on-read", {"delta.enableDeletionVectors": "true"}),
    ):
        path = os.path.join(workdir, f"delta-{mode}-{label}")
        write_deltalake(path, tbl, configuration=props)
        dt = DeltaTable(path)
        declared = dt.metadata().configuration.get("delta.enableDeletionVectors", "unset")

        before, _, files_before = data_bytes(path)
        n_before = len(files_before)
        dt.delete(predicate)
        after, _, files_after = data_bytes(path)

        # Bytes the delete operation added. Old files are tombstoned but remain
        # on disk until VACUUM, so the delta in total size is what was written.
        written = after - before
        dv = any(f.endswith((".bin", ".puffin")) for f in files_after)
        results.append(
            dict(
                engine="delta-rs",
                requested_mode=mode,
                declared_property=declared,
                selectivity=label,
                bytes_before=before,
                bytes_written=written,
                files_before=n_before,
                files_after=len(files_after),
                wrote_delete_file=dv,
            )
        )
        shutil.rmtree(path, ignore_errors=True)
    return results


def run_iceberg(rows, tbl, label, predicate, workdir):
    from pyiceberg.catalog.sql import SqlCatalog

    results = []
    for mode in ("copy-on-write", "merge-on-read"):
        wh = os.path.join(workdir, f"ice-{mode}-{label}")
        os.makedirs(wh, exist_ok=True)
        cat = SqlCatalog(
            "bench",
            **{"uri": f"sqlite:///{wh}/cat.db", "warehouse": f"file://{wh}"},
        )
        cat.create_namespace("b")
        t = cat.create_table(
            "b.t", schema=tbl.schema, properties={"write.delete.mode": mode}
        )
        t.append(tbl)
        root = t.location().replace("file://", "")

        before, _, files_before = data_bytes(root)
        # pyiceberg warns rather than raises when it cannot honour the mode.
        # Capture the warning instead of letting it scroll past, because
        # "it fell back" is a result, not noise.
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            t.delete(predicate)
            notes = [str(w.message) for w in caught]
        after, _, files_after = data_bytes(root)

        results.append(
            dict(
                engine="pyiceberg",
                requested_mode=mode,
                declared_property=t.properties.get("write.delete.mode", "unset"),
                selectivity=label,
                bytes_before=before,
                bytes_written=after - before,
                files_before=len(files_before),
                files_after=len(files_after),
                wrote_delete_file=any(
                    f.endswith((".bin", ".puffin")) for f in files_after
                ),
                engine_warning=notes[0] if notes else None,
            )
        )
        shutil.rmtree(wh, ignore_errors=True)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=200_000)
    ap.add_argument("--only", choices=["all", "delta", "iceberg"], default="all")
    ap.add_argument("--workdir", default=None)
    args = ap.parse_args()

    workdir = args.workdir or tempfile.mkdtemp(prefix="delmode-")
    os.makedirs(workdir, exist_ok=True)
    tbl = make_table(args.rows)

    import deltalake
    import pyiceberg

    meta = {
        "rows": args.rows,
        "columns": tbl.num_columns,
        "in_memory_mb": round(tbl.nbytes / 1e6, 1),
        "pyarrow": pa.__version__,
        "deltalake": deltalake.__version__,
        "pyiceberg": pyiceberg.__version__,
        "python": sys.version.split()[0],
        "generated": datetime.date.today().isoformat(),
        "note": (
            "bytes_written is the increase in on-disk data-file bytes caused by "
            "the delete. Tombstoned files are not vacuumed, so this is the cost "
            "of the operation, not the steady-state table size."
        ),
    }

    rows_out = []
    for label, delta_pred, ice_pred in CASES:
        if args.only in ("all", "delta"):
            rows_out += run_delta(args.rows, tbl, label, delta_pred, workdir)
        if args.only in ("all", "iceberg"):
            rows_out += run_iceberg(args.rows, tbl, label, ice_pred, workdir)

    # amplification: bytes written per byte of data logically removed
    frac = {"0.1%": 0.001, "1%": 0.01, "10%": 0.10}
    for r in rows_out:
        logical = r["bytes_before"] * frac[r["selectivity"]]
        r["bytes_logically_removed"] = round(logical)
        r["write_amplification"] = round(r["bytes_written"] / logical, 1) if logical else None

    print(f"\n{'engine':<11}{'requested':<15}{'sel':>6}{'before MB':>11}"
          f"{'written MB':>12}{'amplif.':>9}{'delete file?':>14}")
    print("-" * 78)
    for r in rows_out:
        print(f"{r['engine']:<11}{r['requested_mode']:<15}{r['selectivity']:>6}"
              f"{r['bytes_before']/1e6:>11.2f}{r['bytes_written']/1e6:>12.3f}"
              f"{str(r['write_amplification'])+'x':>9}"
              f"{str(r['wrote_delete_file']):>14}")

    warned = {r.get("engine_warning") for r in rows_out if r.get("engine_warning")}
    if warned:
        print("\nengine warnings:")
        for w in warned:
            print("  -", w)

    out = {"config": meta, "results": rows_out}
    dest = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        f"results-delete-mode-{meta['generated']}.json",
    )
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {dest}")
    shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
