---
title: "Parquet vs ORC: What the Benchmark Actually Showed"
kicker: "Field Notes"
topic: "Engineering"
description: "Received wisdom says ORC compresses better. Measured at matched codecs on 3M rows, Parquet was 23-26% smaller and faster on every axis. Here's the honest call."
date: 2026-08-08 07:00:00 +0530
last_modified_at: 2026-08-08
faq:
  - q: "Is Parquet or ORC better?"
    a: "For a new lakehouse, Parquet, and by a wider margin than the usual advice suggests. Benchmarked at matched compression codecs on a realistic 3-million-row table, Parquet was 23-26% smaller than ORC, wrote faster, and scanned faster. ORC remains the right choice where a Hive-centric stack already expects it, or where you need Hive's ACID support, but the common claim that ORC compresses better did not survive measurement."
  - q: "Does ORC compress better than Parquet?"
    a: "Not on the data measured here, and the claim is repeated far more often than it is tested. Most published comparisons pit Parquet with Snappy against ORC with Zlib, which compares codecs rather than formats. Matched properly: Snappy to Snappy, Parquet was 26% smaller; DEFLATE to DEFLATE, 23% smaller. This was one dataset with pyarrow's ORC writer at defaults, so measure your own data before it drives a decision."
  - q: "When should I still use ORC?"
    a: "When the surrounding stack expects it. ORC has deep roots in Hive and Trino deployments and supports ACID transactions within Hive, so an established Hive-centric platform is a legitimate reason to stay. What is no longer a good reason is an inherited belief about compression ratio."
  - q: "Are Parquet and ORC both columnar?"
    a: "Yes. Both store values column by column rather than row by row, both prune columns at read time, and both skip data using embedded statistics. That shared design is why the practical differences come down to ecosystem, tooling maturity, and measured behaviour on your data rather than to architecture."
---

Both are columnar, both prune columns, both skip data with embedded statistics.
The architecture is close enough that the choice usually gets settled by a piece
of received wisdom instead: *ORC compresses a bit better, Parquet has the better
ecosystem.*

The second half is true. **The first half did not survive measurement.**
[Benchmarked at matched compression codecs](/essays/parquet-vs-orc-vs-avro-benchmark/)
on a realistic 3-million-row table, Parquet was **23–26% smaller than ORC**, and
it also wrote faster and scanned faster. Not marginally, and not in the direction
the guidance predicts.

**For a new lakehouse: Parquet. Choose ORC when a Hive-centric stack expects it,
not because you believe it compresses better.**

## Where the compression claim comes from

Most published comparisons compare **Parquet with Snappy** against **ORC with
Zlib**. Zlib compresses harder than Snappy, so ORC's file comes out smaller, and
the difference gets written up as a format difference. It's a codec difference.

Matched properly, at 1,000,000 rows:

| Compression | Parquet | ORC | Difference |
|---|---|---|---|
| **Snappy** | 24.3 MB | 32.9 MB | Parquet **26% smaller** |
| **DEFLATE** (gzip / zlib) | 17.8 MB | 23.1 MB | Parquet **23% smaller** |

And at 3,000,000 rows across the full set of measurements:

| Format | Size | Write | Full scan | 2 of 11 columns |
|---|---|---|---|---|
| ORC (snappy) | 96.2 MB | 1.84 s | 0.676 s | 0.109 s |
| Parquet (snappy) | 72.3 MB | 1.35 s | 0.420 s | 0.055 s |
| ORC (zlib) | 68.1 MB | 4.67 s | 1.289 s | 0.262 s |
| **Parquet (zstd)** | **56.6 MB** | **1.32 s** | **0.377 s** | **0.054 s** |

The row worth staring at is ORC with zlib, because zlib is the default nobody
changes: it writes **3.5× slower** than Parquet with zstd and still produces a
**20% larger file**.

I want to be careful about the scope of this. It is one dataset shape, using
pyarrow's ORC writer at default settings — not Hive's, and not tuned. ORC's
reputation was built in tuned Hive stacks on different data and may well hold
there. What the measurement supports is narrower and still useful: **"ORC
compresses better" is not a default you can assume.**

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="pq-orc-t pq-orc-d">
  <title id="pq-orc-t">Parquet versus ORC at matched compression codecs</title>
  <desc id="pq-orc-d">Paired bars at one million rows. With Snappy, Parquet is 24.3 megabytes against ORC's 32.9, making Parquet 26 percent smaller. With DEFLATE, Parquet is 17.8 megabytes against ORC's 23.1, making Parquet 23 percent smaller. A note explains that most published comparisons instead pit Parquet with Snappy against ORC with Zlib, which measures a codec difference and reports it as a format difference.</desc>
  <text x="20" y="24" font-size="12" fill="#1c1a17" font-weight="700">Matched codec, 1M rows — smaller is better</text>
  <text x="150" y="62" font-size="11" fill="#56514a" text-anchor="end">Parquet · snappy</text>
  <rect x="160" y="50" width="243" height="17" rx="2" fill="#c8472b"/>
  <text x="411" y="63" font-size="10" fill="#a4391f" font-weight="700">24.3 MB</text>
  <text x="150" y="88" font-size="11" fill="#56514a" text-anchor="end">ORC · snappy</text>
  <rect x="160" y="76" width="329" height="17" rx="2" fill="#cabfac"/>
  <text x="497" y="89" font-size="10" fill="#56514a">32.9 MB — Parquet 26% smaller</text>
  <text x="150" y="128" font-size="11" fill="#56514a" text-anchor="end">Parquet · DEFLATE</text>
  <rect x="160" y="116" width="178" height="17" rx="2" fill="#c8472b"/>
  <text x="346" y="129" font-size="10" fill="#a4391f" font-weight="700">17.8 MB</text>
  <text x="150" y="154" font-size="11" fill="#56514a" text-anchor="end">ORC · DEFLATE</text>
  <rect x="160" y="142" width="231" height="17" rx="2" fill="#cabfac"/>
  <text x="399" y="155" font-size="10" fill="#56514a">23.1 MB — Parquet 23% smaller</text>
  <line x1="20" y1="182" x2="780" y2="182" stroke="#ddd6c8" stroke-width="1"/>
  <text x="20" y="208" font-size="11" fill="#1c1a17" font-weight="700">How the usual comparison gets it backwards</text>
  <text x="20" y="230" font-size="11" fill="#56514a">Parquet + Snappy  vs  ORC + Zlib  →  ORC looks smaller</text>
  <text x="20" y="250" font-size="11" fill="#a4391f">but that compares CODECS, not formats. Zlib compresses harder than Snappy.</text>
  <text x="20" y="276" font-size="11" fill="#8b857a">Match the codec and the result reverses. One dataset, pyarrow's ORC writer, defaults.</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">The comparison everyone runs measures the codec. Match it, and the ranking flips.</figcaption>
</figure>

## What genuinely separates them

Strip out the compression argument and three real differences remain.

**Ecosystem gravity.** Parquet is the default across Spark, the cloud warehouses,
dbt, and every [open table format](/essays/what-is-an-open-table-format/). ORC's
home is Hive and Trino. This is the difference that actually decides most cases,
and it always was.

**Hive ACID.** ORC supports ACID transactions *within Hive*, which mattered a great
deal before table formats existed. It matters much less now that
[Iceberg and Delta](/essays/iceberg-vs-delta-lake/) provide transactions over any
underlying file format — including ORC, but conventionally Parquet.

**Tooling depth.** More readers, more writers, more debugging tools, more people
who have hit your problem before. Unglamorous and worth a lot at 2am.

## The codec choice matters more than the format choice

This is the part of the measurement with the largest practical payoff, and it
applies to both formats:

| Codec (Parquet, 1M rows) | Size | Write time |
|---|---|---|
| zstd | 19.3 MB | 0.54 s |
| gzip | 17.8 MB | 16.00 s |

Gzip bought an 8% smaller file for a **30× slower write**. For analytical tables,
written once and read many times, that is a bad trade; for continuously written
tables it is an indefensible one.

```sql
-- Usually a bigger win than switching format:
ALTER TABLE lake.sales.orders
  SET TBLPROPERTIES ('write.parquet.compression-codec' = 'zstd');
```

If you're on Parquet with gzip or ORC with zlib because that was the default when
the pipeline was written, changing that one property is probably the cheapest
performance work available to you, and nothing downstream has to change.

## The decision rule

```text
Greenfield lakehouse, or any Spark / cloud-warehouse / dbt stack?
   → Parquet, with zstd. Do not deliberate.

Established Hive or Trino platform that already standardised on ORC,
or you depend on Hive ACID?
   → Stay on ORC. Migrating for a compression claim that
     did not survive measurement is not worth the churn.

Choosing ORC because you read that it compresses better?
   → Measure it on your data first. On mine it was 23-26% larger.
```

The broader point, which is why this essay exists at all: the ORC compression
claim is repeated in nearly every comparison of the two formats, including one
I published on this site before I measured anything. It propagated because it
sounds plausible and because the benchmark that would test it takes an afternoon
that nobody spends. [The script is published](/benchmarks/file-format-benchmark.py)
and the dataset is seeded. If your table behaves differently, that is worth
knowing, and I'd rather be corrected than repeated.
