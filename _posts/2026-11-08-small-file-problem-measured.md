---
title: "The Small File Problem, Measured: When Compaction Pays"
kicker: "Measured"
topic: "Engineering"
description: "Splitting the same rows across more files costs 2.6x the storage and 45x the query time. But under a hundred files it is free. Where the knee actually is."
date: 2026-11-08 07:00:00 +0530
last_modified_at: 2026-11-08
faq:
  - q: "What is the small file problem?"
    a: "A table stored as many small files instead of fewer large ones becomes slower to query and larger on disk, even though the data is identical. Each file carries a footer and metadata that must be opened and parsed, compression works worse on smaller blocks, and the per-file fixed cost gets paid once per file regardless of how little data each one holds. Measured on 2 million rows, splitting the same data from 1 file into 5,000 cost 2.6 times the storage and made a column-pruned read 45 times slower."
  - q: "How small is too small for a Parquet file?"
    a: "Measured on this dataset the knee is in the hundreds of files, not the tens. At 10 files averaging 3.2 MB there was no penalty at all — the full scan was marginally faster than a single file, because multiple files parallelise. At 100 files averaging 428 KB the column-pruned read was already 2.2 times slower. At 46 KB per file it was 12.9 times slower. Target file sizes in the hundreds of megabytes if you can; the damage starts once average file size falls into the hundreds of kilobytes."
  - q: "Do small files hurt full scans or selective queries more?"
    a: "Selective queries, by roughly five to one. Going from 1 file to 5,000 made a full scan 8.8 times slower but a two-of-eleven-column read 45.3 times slower. That is the uncomfortable part: column pruning is the main reason to use a columnar format at all, and fragmentation attacks it specifically. A full scan amortises per-file overhead across a lot of useful work; a selective read pays the same overhead for far less."
  - q: "Do small files make a table bigger on disk?"
    a: "Yes, and by more than most people expect. The same 2 million rows occupied 24.9 MB as one file and 64.9 MB as 5,000 — a 2.6 times increase for identical data. Compression and dictionary encoding operate on blocks, so smaller blocks mean less context to compress against, and every file carries its own footer and schema. You are paying for storage twice: once in bytes, again in the extra bytes you have to read back."
  - q: "Does compaction always help?"
    a: "No, and running it on a table that does not need it is pure cost. At 10 files there was nothing to gain, because there was no measurable penalty to remove. Compaction rewrites data, which costs compute, invalidates caches and churns storage. The question is not whether your table has multiple files but whether average file size has dropped into the range where the penalty starts — which on this data was the hundreds of kilobytes."
  - q: "Why do streaming and CDC pipelines create small files?"
    a: "Because they commit on a time interval rather than a size threshold. A job that writes every minute produces 1,440 files a day regardless of whether a minute's worth of data is a megabyte or a kilobyte, and quiet periods produce the smallest files. Frequent small commits are also how merge-on-read tables accumulate delete files. The fix is to decouple write frequency from file size: commit often for freshness, then compact on a schedule that targets a file size rather than a file count."
  - q: "Is the small file problem worse on object storage?"
    a: "Considerably, and these numbers understate it. This benchmark ran on local disk, where opening a file is cheap. On S3 or equivalent, each file is an HTTP request with latency in the tens of milliseconds, and that cost is paid per file with no relation to file size. Treat the measurements here as a floor: the shape of the curve is right, the magnitude on object storage is larger."
---

"Small files kill query performance, so compact your tables" is one of the most
repeated claims in lakehouse writing. It is repeated on this site too — the word
*compaction* appears in about twenty places here, and until today not one of them
was backed by a measurement.

So here is the measurement. Same 2,000,000 rows, same eleven columns, same zstd
codec, written once as a single file and then split across 10, 100, 1,000 and
5,000 files. **Nothing varies except the file count.** The
[script is published](/benchmarks/) and runs in about a minute.

## The results

| Files | Avg file size | Total on disk | Full scan | 2 of 11 columns | DuckDB aggregation |
|---|---|---|---|---|---|
| **1** | 24 MB | 24.9 MB | 0.289 s | 0.028 s | 0.026 s |
| **10** | 3.2 MB | 32.4 MB | 0.244 s | 0.028 s | 0.028 s |
| **100** | 428 KB | 43.9 MB | 0.292 s | 0.061 s | 0.039 s |
| **1,000** | 46 KB | 47.2 MB | 0.887 s | 0.354 s | 0.169 s |
| **5,000** | 12.7 KB | **64.9 MB** | 2.544 s | 1.247 s | 0.954 s |
| | | **2.6× more** | **8.8× slower** | **45.3× slower** | 36× slower |

Three things in there are worth separating, because they are usually collapsed
into one vague warning.

<figure style="margin:2rem auto;text-align:center;">
<svg class="dia-mob" viewBox="0 0 400 560" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="sf-mt sf-md">
  <title id="sf-mt">Selective reads degrade far faster than full scans</title>
  <desc id="sf-md">Slowdown relative to storing the same two million rows in a single file, on a logarithmic scale. At 10 files neither full scans nor two-column reads are affected. At 100 files the full scan is unchanged while the two-column read is 2.2 times slower. At 1,000 files the full scan is 3.1 times slower and the two-column read 12.9 times. At 5,000 files the full scan is 8.8 times slower while the two-column read is 45.3 times slower, roughly five times worse.</desc>
  <text x="200" y="20" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">Slowdown vs a single file (log scale)</text>
  <rect x="36" y="34" width="14" height="10" fill="#cabfac"/><text x="56" y="43" font-size="10" fill="#56514a">full scan</text>
  <rect x="166" y="34" width="14" height="10" fill="#c8472b"/><text x="186" y="43" font-size="10" fill="#56514a">2 of 11 columns</text>
  <line x1="60" y1="300" x2="380" y2="300" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="92" y="318" font-size="10" fill="#56514a" text-anchor="middle">10</text>
  <rect x="78" y="298" width="12" height="2" fill="#cabfac"/><rect x="92" y="298" width="12" height="2" fill="#c8472b"/>
  <text x="92" y="292" font-size="10" fill="#8b857a" text-anchor="middle">no penalty</text>
  <text x="170" y="318" font-size="10" fill="#56514a" text-anchor="middle">100</text>
  <rect x="156" y="298" width="12" height="2" fill="#cabfac"/>
  <rect x="170" y="267" width="12" height="33" fill="#c8472b"/><text x="176" y="261" font-size="10" fill="#a4391f" text-anchor="middle">2.2x</text>
  <text x="248" y="318" font-size="10" fill="#56514a" text-anchor="middle">1,000</text>
  <rect x="234" y="253" width="12" height="47" fill="#cabfac"/><text x="240" y="247" font-size="10" fill="#8b857a" text-anchor="middle">3.1x</text>
  <rect x="248" y="193" width="12" height="107" fill="#c8472b"/><text x="254" y="187" font-size="10" fill="#a4391f" text-anchor="middle">12.9x</text>
  <text x="326" y="318" font-size="10" fill="#56514a" text-anchor="middle">5,000</text>
  <rect x="312" y="209" width="12" height="91" fill="#cabfac"/><text x="318" y="203" font-size="10" fill="#8b857a" text-anchor="middle">8.8x</text>
  <rect x="326" y="140" width="12" height="160" fill="#c8472b"/><text x="332" y="134" font-size="10" fill="#a4391f" text-anchor="middle">45.3x</text>
  <text x="200" y="340" font-size="10" fill="#56514a" text-anchor="middle">number of files holding the same 2,000,000 rows</text>
  <line x1="20" y1="368" x2="380" y2="368" stroke="#ddd6c8" stroke-width="1"/>
  <text x="200" y="396" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">Selective reads degrade about</text>
  <text x="200" y="414" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">five times faster than full scans.</text>
  <text x="200" y="444" font-size="10" fill="#8b857a" text-anchor="middle">Column pruning is the reason to use a</text>
  <text x="200" y="459" font-size="10" fill="#8b857a" text-anchor="middle">columnar format. Fragmentation attacks</text>
  <text x="200" y="474" font-size="10" fill="#8b857a" text-anchor="middle">that specifically.</text>
  <text x="200" y="504" font-size="10" fill="#a4391f" text-anchor="middle">Storage also rises 2.6x for identical rows.</text>
  <text x="200" y="532" font-size="10" fill="#8b857a" text-anchor="middle">Local disk. On object storage every file is</text>
  <text x="200" y="547" font-size="10" fill="#8b857a" text-anchor="middle">an HTTP request — treat this as a floor.</text>
</svg>
<svg class="dia-desk" viewBox="0 0 800 330" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="sf-t sf-d">
  <title id="sf-t">Selective reads degrade far faster than full scans</title>
  <desc id="sf-d">Slowdown relative to storing the same two million rows in a single file, on a logarithmic scale. At 10 files neither full scans nor two-column reads are affected. At 100 files the full scan is unchanged while the two-column read is 2.2 times slower. At 1,000 files the full scan is 3.1 times slower and the two-column read 12.9 times. At 5,000 files the full scan is 8.8 times slower while the two-column read is 45.3 times slower, roughly five times worse. Storage also rises 2.6 times for identical rows.</desc>
  <text x="400" y="22" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Slowdown vs a single file, same 2,000,000 rows (log scale)</text>
  <rect x="300" y="36" width="14" height="10" fill="#cabfac"/><text x="320" y="45" font-size="11" fill="#56514a">full scan</text>
  <rect x="420" y="36" width="14" height="10" fill="#c8472b"/><text x="440" y="45" font-size="11" fill="#56514a">2 of 11 columns</text>
  <line x1="90" y1="250" x2="730" y2="250" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="160" y="268" font-size="11" fill="#56514a" text-anchor="middle">10 files</text>
  <rect x="140" y="248" width="18" height="2" fill="#cabfac"/><rect x="162" y="248" width="18" height="2" fill="#c8472b"/>
  <text x="160" y="240" font-size="11" fill="#8b857a" text-anchor="middle">no penalty</text>
  <text x="320" y="268" font-size="11" fill="#56514a" text-anchor="middle">100 files</text>
  <rect x="300" y="248" width="18" height="2" fill="#cabfac"/>
  <rect x="322" y="217" width="18" height="33" fill="#c8472b"/><text x="331" y="210" font-size="11" fill="#a4391f" text-anchor="middle">2.2x</text>
  <text x="480" y="268" font-size="11" fill="#56514a" text-anchor="middle">1,000 files</text>
  <rect x="460" y="203" width="18" height="47" fill="#cabfac"/><text x="469" y="196" font-size="11" fill="#8b857a" text-anchor="middle">3.1x</text>
  <rect x="482" y="143" width="18" height="107" fill="#c8472b"/><text x="491" y="136" font-size="11" fill="#a4391f" text-anchor="middle">12.9x</text>
  <text x="640" y="268" font-size="11" fill="#56514a" text-anchor="middle">5,000 files</text>
  <rect x="620" y="159" width="18" height="91" fill="#cabfac"/><text x="629" y="152" font-size="11" fill="#8b857a" text-anchor="middle">8.8x</text>
  <rect x="642" y="90" width="18" height="160" fill="#c8472b"/><text x="651" y="83" font-size="11" fill="#a4391f" text-anchor="middle">45.3x</text>
  <text x="400" y="294" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">Selective reads degrade about five times faster than full scans.</text>
  <text x="400" y="316" font-size="11" fill="#8b857a" text-anchor="middle">Storage also rises 2.6x for identical rows. Local disk, so treat this as a floor.</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">Log scale, because a linear one would hide everything below a thousand files. Fragmentation attacks column pruning specifically.</figcaption>
</figure>

## 1. Selective reads suffer about five times more than full scans

Full scans got **8.8× slower**. Reading two columns of eleven got **45.3×
slower.**

That gap is the real finding, and it is the opposite of reassuring. **Column
pruning is the main reason to use a columnar format at all.** A full scan
amortises the per-file cost across a lot of useful work — you were going to read
every byte anyway. A selective read pays the same per-file overhead for a
fraction of the payload, so the overhead dominates sooner.

Put differently: fragmentation attacks the specific thing you chose
[Parquet](/essays/apache-iceberg-vs-parquet/) for. Measured as the benefit that
column pruning still delivers:

| Files | Pruning still pays |
|---|---|
| 1 | **10.5× faster** than a full scan |
| 10 | 8.6× faster |
| 100 | 4.8× faster |
| 1,000 | 2.5× faster |
| 5,000 | **2.0× faster** |

Pruning never stops helping — it just stops helping *much*. You keep the format
and lose most of the advantage.

**A correction, since this site's rule is that published numbers are measured
numbers.** The first run of this benchmark showed the 5,000-file pruned read at
4.51 s, *slower* than its own full scan — pruning going negative. It was a
striking result and it was about to be the headline here. It does not replicate:
three further runs at five trials each gave 1.257, 1.242 and 1.252 s, within one
percent of each other. The original was an outlier, almost certainly memory
pressure during the first large write. The honest finding is the duller one in
the table above.

## 2. The same data costs 2.6× the storage

This one I nearly missed, because I had assumed total bytes would be constant and
wrote that assumption into the script's own caveats before checking it.

They are not constant. **24.9 MB as one file, 64.9 MB as 5,000** — identical
rows, 2.6 times the disk.

The cause is not mysterious. Compression and dictionary encoding work on blocks,
so a smaller block has less context to compress against: a dictionary of country
codes that pays for itself across a million rows is dead weight across four
hundred. On top of that every file carries its own footer, schema and statistics.

You therefore pay twice. Once in storage, and again in the read path, because
part of that 8.8× slowdown is simply **more bytes to move.** This benchmark does
not separate "more bytes" from "per-file overhead", and I would not trust anyone
who claims a clean split without isolating it deliberately.

## 3. Under a hundred files, there is nothing to fix

Look at the 10-file row again. The full scan was **0.244 s against 0.289 s for a
single file** — marginally *faster*, because several files parallelise where one
does not.

At 100 files averaging 428 KB, the pruned read is 2.2× slower: measurable, rarely
urgent. The damage becomes serious between there and 1,000 files, as average size
falls through the tens of kilobytes.

**So "compact everything" is as wrong as ignoring the problem.** Compaction
rewrites data. It costs compute, churns storage, invalidates caches, and on a
table format it generates new snapshots that themselves need expiring. Running it
against a table with forty healthy files is pure cost for no benefit.

The useful question is not *how many files does this table have* but **what is
the average file size, and has it fallen into the range where the penalty
starts.** On this data that range began in the hundreds of kilobytes.

## Why tables end up here

Almost always because **write frequency is decoupled from file size, and nobody
reconnected them.**

A streaming or [CDC](/essays/what-is-change-data-capture/) job that commits every
minute writes 1,440 files a day whether a minute carries a megabyte or a
kilobyte, and the quietest hours produce the worst files. Over-partitioning does
the same thing structurally: partition by day *and* region *and* product and most
partitions hold almost nothing. And frequent small commits are exactly how
[merge-on-read](/essays/merge-on-read-vs-copy-on-write/) tables accumulate delete
files alongside the data.

None of these is a mistake at the moment it is made. Each is a reasonable
freshness decision whose storage consequence shows up months later.

## What to actually do

- **Measure average file size, not file count.** It is the number that predicts
  the penalty. File count alone tells you nothing without total volume.
- **Set a target size and compact toward it**, rather than compacting on a fixed
  schedule. Hundreds of megabytes is a common target and a reasonable default.
- **Commit for freshness, compact for size.** They are different jobs with
  different triggers and should not be the same job.
- **Expect it to be worse than this on object storage.** These numbers are local
  disk, where opening a file is nearly free. On S3 every file is an HTTP request
  with latency in the tens of milliseconds, paid per file regardless of size.
  **Treat this curve as a floor.**
- **If selective queries matter to you, care sooner.** They degrade five times
  faster than the full scans you might be benchmarking with.

## The honest limits of this

One dataset shape, eleven columns, zstd, default row-group sizes, local disk,
warm page cache, single writer, no concurrency. A single 2-million-row file still
contains many row groups internally, so the one-file case is not an artificially
perfect baseline.

What transfers is the **shape**: selective reads degrade far faster than full
scans, storage inflates meaningfully, and the knee sits in the hundreds of files
rather than the tens. The absolute seconds are a property of a two-core machine
and are worth nothing to you. [Rerun it](/benchmarks/) on your own data, which
takes about a minute and will tell you something the generic advice cannot.
