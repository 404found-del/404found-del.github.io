---
title: "Parquet vs ORC vs Avro Benchmark: Compression and Read Speed"
kicker: "Measured"
topic: "Engineering"
description: "Benchmarked on 3 million rows: Parquet was 23-26% smaller than ORC at matched codecs, contradicting the usual claim. Script published, rerun it yourself."
date: 2026-07-26 14:00:00 +0530
last_modified_at: 2026-08-08
faq:
  - q: "Is Parquet or ORC better for compression?"
    a: "On the dataset measured here, Parquet was smaller at every matched compression codec: 26% smaller than ORC with Snappy, and 23% smaller with DEFLATE. That contradicts the widely repeated claim that ORC compresses better. The honest conclusion isn't that ORC is worse everywhere, but that 'ORC compresses better' is not a default you can assume, and is worth measuring on your own data before it drives a decision."
  - q: "How much faster is Parquet than CSV?"
    a: "On 3 million rows and 11 columns: 6.1 times smaller on disk, and a filtered aggregation through DuckDB ran 13.8 times faster. Reading just 2 of the 11 columns was 9.2 times faster from Parquet than from CSV, because CSV has to parse every byte of every row even when you asked for two fields."
  - q: "Does column pruning actually make queries faster?"
    a: "Yes, and it is the single largest effect measured here. Reading 2 of 11 columns instead of all 11 was 6.9 times faster on Parquet and 4.9 times faster on ORC. On Avro it was 4% slower than reading everything, which is exactly what a row-based layout predicts: the whole record is decoded regardless of what you asked for."
  - q: "Should I use gzip or zstd for Parquet?"
    a: "Zstd, in almost every case. Measured on identical data, gzip produced a file 8% smaller than zstd but took 30 times longer to write. That trade is rarely worth making for analytical tables that are written once and read many times, and never worth making for tables written continuously."
---

**Parquet came out 23–26% smaller than ORC at matched compression codecs** — the
opposite of the claim you'll find in most comparisons, including one I published
on this site. That result is the reason this piece exists.

Every comparison of file formats I have written, including
[the one on this site](/essays/parquet-vs-orc-vs-avro/), asserts things about
compression and scan speed without measuring them. So I measured them.

What follows is one benchmark on one dataset: 3 million rows, 11 columns,
322 MB uncompressed in memory, written to Parquet, ORC, Avro, and CSV and read
back in several ways. [The script is published](/benchmarks/file-format-benchmark.py),
the dataset is generated from a fixed seed, and
[the raw results are in the repo](/benchmarks/results-2026-07-26.json). If you
rerun it and get something different, I want to know.

One result contradicted what I had previously written on this site. That one is
first.

## The result I did not expect

The received wisdom, repeated in most comparisons including my own, is that ORC
usually edges Parquet on compression ratio. On this dataset it didn't — not at
any matched codec, and not by a small margin.

Comparing like with like matters here, because most published comparisons put
Parquet with Snappy against ORC with Zlib and call the difference a format
difference. It isn't; it's a codec difference. Matched properly, at 1,000,000
rows:

| Compression | Parquet | ORC | Difference |
|---|---|---|---|
| **Snappy** | 24.3 MB | 32.9 MB | Parquet **26% smaller** |
| **DEFLATE** (gzip / zlib) | 17.8 MB | 23.1 MB | Parquet **23% smaller** |

I want to be careful about what this does and does not show. It does *not* show
that ORC compresses worse than Parquet in general. It shows that on one
realistically-shaped table, using the ORC writer most people in a Python or
Spark-adjacent stack will actually reach for, at default settings, the claim
went the other way. ORC's reputation was built in tuned Hive stacks on different
data, and it may well hold there.

What it does show is narrower and still useful: **"ORC compresses better" is not
a default you can assume.** It is a claim that needs measuring on your data
before it drives an architectural decision. I had repeated it without measuring
it, which is the point of this essay.

## The main table

3,000,000 rows × 11 columns. Sizes are on disk; times are medians, not
best-of-N. Read times are warm-cache.

| Format | Size | vs CSV | Write | Full scan | 2 of 11 columns |
|---|---|---|---|---|---|
| CSV | 342.6 MB | 1.0× | 1.80 s | 1.398 s | 0.499 s |
| CSV + gzip | 92.1 MB | 3.7× | 13.40 s | — | — |
| ORC (snappy) | 96.2 MB | 3.6× | 1.84 s | 0.676 s | 0.109 s |
| **Parquet (snappy)** | 72.3 MB | 4.7× | 1.35 s | 0.420 s | 0.055 s |
| ORC (zlib) | 68.1 MB | 5.0× | 4.67 s | 1.289 s | 0.262 s |
| **Parquet (zstd)** | **56.6 MB** | **6.1×** | **1.32 s** | **0.377 s** | **0.054 s** |

Parquet with zstd won every column on this dataset: smallest file, fastest
write, fastest full scan, fastest pruned scan. That is an unusually clean
result and I'd treat it with suspicion if I hadn't run it myself.

Note the ORC/zlib row in particular, because zlib is the default a lot of people
never change: it writes **3.5× slower than Parquet/zstd** and still produces a
**20% larger file**.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 340" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="fmt-bench-t fmt-bench-d">
  <title id="fmt-bench-t">Measured file size and pruned-read time by format</title>
  <desc id="fmt-bench-d">Horizontal bars for on-disk size across six format and codec combinations on three million rows: CSV at 342.6 megabytes, gzipped CSV at 92.1, ORC with Snappy at 96.2, Parquet with Snappy at 72.3, ORC with Zlib at 68.1, and Parquet with Zstd smallest at 56.6 megabytes. Beneath, the time to read two of eleven columns: 0.499 seconds for CSV, 0.262 for ORC Zlib, 0.109 for ORC Snappy, and 0.054 for Parquet Zstd, a nine-fold gap between CSV and Parquet.</desc>
  <text x="20" y="22" font-size="12" fill="#1c1a17" font-weight="700">On-disk size — 3M rows, 11 columns</text>
  <text x="150" y="52" font-size="11" fill="#56514a" text-anchor="end">CSV</text>
  <rect x="158" y="41" width="560" height="15" rx="2" fill="#1c1a17"/>
  <text x="726" y="53" font-size="10" fill="#56514a">342.6 MB</text>
  <text x="150" y="76" font-size="11" fill="#56514a" text-anchor="end">ORC snappy</text>
  <rect x="158" y="65" width="157" height="15" rx="2" fill="#cabfac"/>
  <text x="323" y="77" font-size="10" fill="#56514a">96.2</text>
  <text x="150" y="100" font-size="11" fill="#56514a" text-anchor="end">CSV gzip</text>
  <rect x="158" y="89" width="151" height="15" rx="2" fill="#cabfac"/>
  <text x="317" y="101" font-size="10" fill="#56514a">92.1</text>
  <text x="150" y="124" font-size="11" fill="#56514a" text-anchor="end">Parquet snappy</text>
  <rect x="158" y="113" width="118" height="15" rx="2" fill="#c8472b" opacity="0.55"/>
  <text x="284" y="125" font-size="10" fill="#56514a">72.3</text>
  <text x="150" y="148" font-size="11" fill="#56514a" text-anchor="end">ORC zlib</text>
  <rect x="158" y="137" width="111" height="15" rx="2" fill="#cabfac"/>
  <text x="277" y="149" font-size="10" fill="#56514a">68.1</text>
  <text x="150" y="172" font-size="11" fill="#1c1a17" text-anchor="end" font-weight="700">Parquet zstd</text>
  <rect x="158" y="161" width="93" height="15" rx="2" fill="#c8472b"/>
  <text x="259" y="173" font-size="10" fill="#a4391f" font-weight="700">56.6</text>
  <line x1="20" y1="196" x2="780" y2="196" stroke="#ddd6c8" stroke-width="1"/>
  <text x="20" y="220" font-size="12" fill="#1c1a17" font-weight="700">Time to read 2 of 11 columns</text>
  <text x="150" y="250" font-size="11" fill="#56514a" text-anchor="end">CSV</text>
  <rect x="158" y="239" width="560" height="15" rx="2" fill="#1c1a17"/>
  <text x="726" y="251" font-size="10" fill="#56514a">0.499 s</text>
  <text x="150" y="274" font-size="11" fill="#56514a" text-anchor="end">ORC zlib</text>
  <rect x="158" y="263" width="294" height="15" rx="2" fill="#cabfac"/>
  <text x="460" y="275" font-size="10" fill="#56514a">0.262</text>
  <text x="150" y="298" font-size="11" fill="#56514a" text-anchor="end">ORC snappy</text>
  <rect x="158" y="287" width="122" height="15" rx="2" fill="#cabfac"/>
  <text x="288" y="299" font-size="10" fill="#56514a">0.109</text>
  <text x="150" y="322" font-size="11" fill="#1c1a17" text-anchor="end" font-weight="700">Parquet zstd</text>
  <rect x="158" y="311" width="61" height="15" rx="2" fill="#c8472b"/>
  <text x="227" y="323" font-size="10" fill="#a4391f" font-weight="700">0.054 — 9.2× faster than CSV</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">Measured, not asserted. Absolute times are specific to a slow two-core box; the ratios are the finding.</figcaption>
</figure>

## Column pruning is where the money is

Compression gets the attention. Pruning is the bigger effect.

Reading 2 of 11 columns instead of all 11:

- **Parquet: 6.9× faster** (0.377 s → 0.054 s)
- **ORC: 4.9× faster** (1.289 s → 0.262 s)
- **CSV: 2.8× faster** (1.398 s → 0.499 s)
- **Avro: 0.96× — i.e. 4% *slower***

The CSV number is the instructive one, because 2.8× looks like pruning and
isn't. CSV still reads and parses every byte of every row; all it saves is
converting the columns you didn't ask for. The I/O and the parse are unavoidable
because the bytes of `country` are physically interleaved with the bytes of
everything else.

And Avro's result is the cleanest measurement in the whole exercise, because it
compares the same library reading the same file two ways: asking for two fields
out of eleven was *marginally slower* than taking all eleven, since the whole
record is decoded either way and then you throw most of it away. That is not a
defect. It is what row-based means, and it is precisely why Avro belongs on the
write path rather than the scan path.

## Through a query engine

Sizes and raw reads are one thing; what an engine does with them is another.
Same query, same data, DuckDB reading each file directly:

```sql
SELECT country, sum(quantity * unit_price * (1 - discount_pct))
FROM   <file>
WHERE  status = 'delivered'
GROUP  BY country;
```

| Source | Time |
|---|---|
| CSV | 0.879 s |
| Parquet (zstd) | **0.064 s** |

**13.8× faster.** The query touches 4 of 11 columns and filters on one of them,
which is the shape almost every analytical query has, and it is the shape
columnar storage was built for.

## Avro, on its own terms

Avro was measured on a 300,000-row subset, because `fastavro` is pure Python
while Arrow's readers are compiled C++ — mixing them at full scale measures the
library, not the format. For the same reason I am **not** publishing a
Parquet-vs-Avro read-time comparison. It would be a language benchmark wearing a
format benchmark's clothes, and you should be suspicious of anyone who does
publish one without saying so.

Sizes are a fair comparison, though, since bytes are bytes:

| Format (300k rows) | Size |
|---|---|
| Avro, uncompressed | 24.2 MB |
| Avro, snappy | 13.7 MB |
| Avro, deflate | 10.6 MB |
| ORC, zlib | 6.8 MB |
| **Parquet, zstd** | **6.5 MB** |

Even at its best compression, Avro was **63% larger than Parquet** on identical
data. Again: not a defect. Row-based layouts interleave values of different
types and cardinalities, which is exactly the arrangement that defeats the
run-length, dictionary, and delta encodings columnar formats depend on. You
accept that cost to get cheap appends and schema evolution, and on a
[streaming path](/essays/batch-vs-streaming/) that is a good trade.

## Zstd versus gzip: not close

| Codec | Size (1M rows) | Write time |
|---|---|---|
| zstd | 19.3 MB | 0.54 s |
| gzip | 17.8 MB | 16.00 s |

Gzip bought an 8% smaller file for a **30× slower write**. For analytical tables
— written once, read many times — that is a bad trade, and for tables written
continuously it is an indefensible one. Zstd is the sensible default and has
been for a while; a lot of pipelines are still on gzip because nobody revisited
a setting chosen in 2016.

## What this benchmark does not prove

Stating this properly matters more than the numbers, because a benchmark whose
limits aren't declared is marketing.

- **One dataset shape.** Eleven columns mixing low-cardinality strings, sorted
  timestamps, high-cardinality integers, floats, and one free-text column.
  Change the mix and the compression figures move. A test built only from
  low-cardinality columns would flatter every columnar format enormously.
- **One ORC writer.** pyarrow's, at defaults — not Hive's, and not tuned. This
  is a real-world result for a common stack, not a statement about ORC's
  ceiling.
- **No tuning at all.** No sorting or clustering, no bloom filters, no adjusted
  row group or stripe sizes. Every format here can be made to do better, and
  sorting on a filtered column would move the numbers most.
- **Warm page cache**, which *understates* the advantage of the smaller files.
  Cold reads would widen the gaps.
- **A slow two-core laptop CPU.** The absolute seconds mean nothing to you. The
  ratios are the deliverable.

## What I'd take from it

The decision rule from [the earlier essay](/essays/parquet-vs-orc-vs-avro/)
survives, with one correction and one addition.

**Unchanged:** choose the axis first. Read-heavy analytics wants columnar;
write-heavy streaming and cross-system exchange want Avro. That split is
structural, and the Avro pruning result is about as direct a confirmation as a
measurement can give.

**Corrected:** I previously wrote that ORC "often achieves slightly higher
compression." I no longer think that should be stated as a general fact. On this
data, at matched codecs, it was 23–26% larger. ORC remains the right call where
a Hive-centric stack expects it; the compression argument for choosing it should
be measured, not inherited.

**Added:** if you are on Parquet with gzip or ORC with zlib because that was the
default, changing that one setting to zstd is likely the cheapest performance
work available to you. It cost 30× less write time for a file within 8% of
gzip's size, and nothing downstream has to change.

And the broader point, which is why I ran this at all: most of what circulates
about file formats is inherited rather than measured, this site included until
today. The script is thirty lines of real work and
[it's published](/benchmarks/file-format-benchmark.py). Run it on your data. The
answer for your table may differ from the answer for mine, and that is the
finding either way.
