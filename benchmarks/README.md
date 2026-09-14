---
layout: page
title: "Benchmarks"
kicker: "Reproducible measurements"
description: "The benchmark scripts behind the numbers published on this site, with their raw results. Seeded datasets, so a rerun operates on identical bytes."
permalink: /benchmarks/
---

Reproducible measurements backing essays on dataarchitect.studio. Every number
published on the site that comes from a benchmark comes from a script in here,
along with the raw results file it produced.

## file-format-benchmark.py

Parquet vs ORC vs Avro vs CSV — size, write time, full-scan read, column-pruned
read, and a filtered aggregation through DuckDB.

Essay: <https://dataarchitect.studio/essays/parquet-vs-orc-vs-avro-benchmark/>
Raw results: [`results-2026-07-26.json`](results-2026-07-26.json)

```bash
pip install pyarrow fastavro duckdb cramjam
python3 file-format-benchmark.py --rows 3000000 --trials 3
```

On a memory-constrained machine, run it a stage at a time:

```bash
python3 file-format-benchmark.py --only parquet --codec zstd --rows 3000000 \
    --workdir ./wd --out results.json
python3 file-format-benchmark.py --only orc --codec ZLIB --rows 3000000 \
    --workdir ./wd --out results.json
# ... and so on for csv, avro, duckdb
```

The dataset is generated from a fixed seed, so staged runs operate on identical
bytes and results merge into one file.

### What the 2026-07-26 run was measured on

Intel Core i5-10210U @ 1.60 GHz, 2 vCPU, 3 GB RAM, Linux, pyarrow 25.0.0,
Python 3.10.12. Warm page cache. 3,000,000 rows × 11 columns, 322 MB
uncompressed in memory. Matched-codec comparisons were re-run at 1,000,000 rows
because gzip at 3M exceeded available memory.

**The absolute numbers are worthless to you.** This is a low-power two-core
laptop CPU. The ratios are the point, and the ratios are what the essay reports.

### Known limitations, stated up front

- **One dataset shape.** Eleven columns mixing low-cardinality strings,
  high-cardinality integers, sorted timestamps, floats, and one free-text
  column. Change the mix and the compression numbers move. A benchmark made
  only of low-cardinality columns flatters columnar formats enormously.
- **pyarrow's ORC writer, not Hive's.** ORC's reputation for compression comes
  largely from tuned Hive stacks. This measures the ORC most people in a Python
  or Spark-adjacent stack will actually get, at default settings, which is a
  different question from what ORC can do at its best.
- **fastavro is pure Python; Arrow's readers are compiled C++.** Cross-library
  read times are therefore *not* compared, and the essay does not report them.
  The Avro result that matters is same-library: Avro full-scan vs Avro
  column-pruned, on the same file.
- **Warm page cache.** Clearing it requires root. Cold reads would widen the
  gap between small and large files, so these numbers understate the advantage
  of the smaller formats.
- **Defaults everywhere.** No sorting, clustering, bloom filters, or tuned row
  group / stripe sizes. Every format here can be made to do better.

If you rerun it and get materially different results, that's worth knowing —
open an issue on [GitHub](https://github.com/404found-del/404found-del.github.io/issues).

## delete-mode-benchmark.py

Copy-on-write delete amplification, and whether merge-on-read is available at all
from Python.

Essay: <https://dataarchitect.studio/essays/merge-on-read-vs-copy-on-write/>
Raw results: [`results-delete-mode-2026-09-14.json`](results-delete-mode-2026-09-14.json)

```bash
pip install pyarrow deltalake "pyiceberg[sql-sqlite,pyarrow]"
python3 delete-mode-benchmark.py --rows 1000000
```

Runs in about a minute on local disk. No cloud credentials, nothing uploaded.

### What it found

Deleting rows scattered across every data file, measured as bytes written per
byte actually removed:

| Rows deleted | delta-rs | pyiceberg |
|---|---|---|
| 0.1% | **259×** | **1,073×** |
| 1% | 24× | 105× |
| 10% | 2.2× | 9.4× |

And the part worth checking on your own versions: **neither client honoured a
merge-on-read request.** Identical bytes written either way, no delete file
produced. pyiceberg 0.12.0 warns *"Merge on read is not yet supported, falling
back to copy-on-write"*. deltalake 1.6.3 stores `delta.enableDeletionVectors`
in the table metadata and then ignores it, with no warning at all — so the table
advertises a property it is not honouring.

### Known limitations, stated up front

- **Two Python clients, not the JVM engines.** Spark with the Iceberg or Delta
  runtime does implement merge-on-read. This measures what the pure-Python path
  does, because that is what a lot of pipelines actually run.
- **Default file sizes and codecs.** delta-rs and pyiceberg chose different ones,
  which is most of why their amplification figures differ. That is the honest
  lesson rather than a defect: amplification tracks file size, so the comparison
  between the two engines is less meaningful than the trend within each.
- **Local disk, single writer, no concurrency.** Object-storage latency and
  competing writers both change the picture and neither is simulated.
- **Amplification is measured against the pre-delete table size**, with
  tombstoned files left in place (no VACUUM / expire_snapshots). That is the cost
  of the operation, not the steady-state size of the table.
- **Versions date fast.** Both projects are moving quickly and may well ship
  merge-on-read soon. The script prints what *your* versions do, which is the
  only answer that matters.
