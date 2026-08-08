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
