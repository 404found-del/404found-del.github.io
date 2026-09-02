---
title: "Parquet vs ORC vs Avro: Which Data File Format, and When"
kicker: "Field Notes"
topic: "Architecture"
description: "Parquet and ORC are columnar formats for analytics; Avro is row-based for streaming and schema evolution. A clear comparison and a decision rule that holds."
date: 2026-07-23 11:00:00 +0530
last_modified_at: 2026-08-29
faq:
  - q: "What is the difference between Parquet, ORC, and Avro?"
    a: "Parquet and ORC are columnar formats — they store all of one column together, which makes analytical queries that read a few columns fast and highly compressible. Avro is row-based — it stores whole records together, which makes it fast to write and ideal for streaming and data exchange. Columnar wins for reads and analytics; row-based wins for writes, streaming, and schema evolution."
  - q: "Which is better, Parquet or ORC?"
    a: "Both are columnar and both are excellent; the difference is ecosystem more than capability. Parquet is the de facto default across Spark, the cloud warehouses, and most of the modern data stack, and it's what open table formats reach for. ORC has deep roots in the Hive/Hadoop world, including ACID support there. ORC is often said to compress better, but a benchmark on this site found Parquet 23-26% smaller at matched codecs, so treat that claim as something to measure rather than assume. For a new lakehouse, Parquet is the safe default."
  - q: "When should I use Avro instead of Parquet?"
    a: "Use Avro when writes dominate reads: streaming pipelines (it's the standard in the Kafka ecosystem), event logs, and any place records are written whole and often, or where schema evolution across systems matters. Avro's row-based layout and rich schema-evolution support make it ideal for moving data; its weakness is analytical queries, where columnar Parquet or ORC is far faster."
  - q: "What is the difference between Parquet and Avro?"
    a: "Layout, and everything follows from it. Parquet is columnar: it stores all of one column together, so a query reading a few columns touches only those, and similar values sitting next to each other compress hard. Avro is row-based: it stores each record whole, so writing an event is one append and the schema travels with the data. Measured on an identical 300,000-row table, Parquet at zstd was 6.47 MB against Avro at deflate's 10.55 MB — 39% smaller. Parquet reads 2 of 11 columns about 7x faster than it reads all 11; Avro reads 2 of 11 slightly slower than all 11, because there is nothing to prune."
  - q: "Is Parquet or Avro better?"
    a: "They are not competing for the same job, so the honest answer is that it depends on direction of travel. If you are querying data — scanning many rows and aggregating a few columns — Parquet, by a wide margin: it is smaller on disk and its column pruning is roughly a 7x speedup where Avro's is nothing at all. If you are moving data — streaming through Kafka, exchanging records between systems owned by different teams, evolving a schema over time — Avro, because it carries a rich schema with the data and writes records whole. Most serious platforms run both: Avro on the wire, Parquet at rest."
  - q: "Is Avro faster than Parquet?"
    a: "For analytical reads, no, and not marginally. Column pruning is the reason: reading 2 of 11 columns from Parquet was about 7x faster than reading all 11, while the same query against Avro was fractionally slower than reading everything, since a row-based reader must walk each whole record and discard the fields you did not ask for. Avro is often said to write faster, and that is plausible from its layout, but the benchmark on this site cannot confirm it — Avro was written with a pure-Python library against pyarrow's C++ Parquet writer, which measures the implementations rather than the formats."
  - q: "Do open table formats like Iceberg use Parquet, ORC, or Avro?"
    a: "All three are supported as underlying data files by Apache Iceberg, and the choice is a per-table property — but Parquet is the overwhelming default for analytical tables. Interestingly, Avro often appears inside the table format's own metadata layer even when the data files are Parquet, because manifest files are written whole and benefit from Avro's row-based, evolvable format."
---

Three formats, one recurring question: *which file format should this data live
in?* The clean answer starts with a single split. **Parquet and ORC are columnar
— built for reading and analytics. Avro is row-based — built for writing,
streaming, and moving data between systems.** Get that axis right and the choice
is nearly made; the Parquet-vs-ORC decision that remains is mostly about
ecosystem, not capability. Here's the full comparison and a decision rule you can
apply without re-reading it.

## The comparison, at a glance

| | Parquet | ORC | Avro |
|---|---|---|---|
| **Layout** | Columnar | Columnar | Row-based |
| **Best for** | Analytics / reads | Analytics / reads (Hive-centric) | Streaming / writes / exchange |
| **Compression** | Excellent ([measured smallest](/essays/parquet-vs-orc-vs-avro-benchmark/)) | Excellent | Moderate |
| **Column-pruning reads** | Yes — fast | Yes — fast | No (reads whole rows) |
| **Write speed** | Slower (columnar encode) | Slower (columnar encode) | Fast |
| **Schema evolution** | Good | Good | Excellent — its signature strength |
| **Ecosystem home** | Spark, cloud warehouses, lakehouse default | Hive / Hadoop, Trino | Kafka, streaming, RPC |
| **Stores schema** | In file footer | In file footer | With the data, richly |
| **Typical role** | Default analytical data files | Analytical files in Hive stacks | Event/message payloads, table metadata |

## Columnar vs row-based — the decision that drives everything

The split is physical. A **columnar** format (Parquet, ORC) stores all of column A
together, then all of column B. A query touching two of fifty columns reads only
those two, and columns of like values — all timestamps, all country codes —
compress hard. That pruning effect is not a small one: measured on 3 million
rows, [reading 2 of 11 columns was 6.9× faster](/essays/parquet-vs-orc-vs-avro-benchmark/)
than reading all of them. That's exactly the shape of an [OLAP](/glossary/olap/) analytical
scan, and it's why both dominate the warehouse and lakehouse world.

A **row-based** format (Avro) stores each record whole: all of row 1's fields
together, then row 2. Writing an event is one contiguous append; reading one
record back is cheap. But an analytical query that wants one column still has to
read past every other field in every row — the opposite of what analytics wants.
Avro's home is therefore *movement*: the Kafka streaming ecosystem, event logs,
and cross-system exchange, where records are written whole and schema evolution
across producers and consumers is a first-class concern.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="parquet-vs-orc-vs-avro-t parquet-vs-orc-vs-avro-d">
  <title id="parquet-vs-orc-vs-avro-t">Columnar versus row-based file layout</title>
  <desc id="parquet-vs-orc-vs-avro-d">Two panels. Columnar formats Parquet and ORC store all values of one column together, so reading one column touches one stripe and like values compress hard, giving fast reads for analytics. Row-based Avro stores each record whole, so writing is one append and the schema travels with the data, giving fast writes for streaming and exchange.</desc>
  <text x="210" y="34" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Columnar — Parquet / ORC</text>
  <rect x="70" y="50" width="280" height="34" rx="4" fill="#c8472b"/>
  <text x="210" y="72" font-size="11" fill="#f6f3ec" text-anchor="middle">all order_id ┃ all amount ┃ all ts</text>
  <rect x="70" y="92" width="280" height="26" rx="4" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="210" y="110" font-size="10" fill="#56514a" text-anchor="middle">read 1 column → touch 1 stripe</text>
  <rect x="70" y="126" width="280" height="26" rx="4" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="210" y="144" font-size="10" fill="#56514a" text-anchor="middle">like values → compress hard</text>
  <text x="210" y="184" font-size="11" fill="#8b857a" text-anchor="middle">→ fast reads, small size, analytics</text>
  <text x="590" y="34" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Row-based — Avro</text>
  <rect x="450" y="50" width="280" height="34" rx="4" fill="#1c1a17"/>
  <text x="590" y="72" font-size="11" fill="#f6f3ec" text-anchor="middle">row1{all fields} ┃ row2{all fields}</text>
  <rect x="450" y="92" width="280" height="26" rx="4" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="590" y="110" font-size="10" fill="#56514a" text-anchor="middle">write a record → one append</text>
  <rect x="450" y="126" width="280" height="26" rx="4" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="590" y="144" font-size="10" fill="#56514a" text-anchor="middle">schema travels with the data</text>
  <text x="590" y="184" font-size="11" fill="#8b857a" text-anchor="middle">→ fast writes, streaming, exchange</text>
  <text x="400" y="240" font-size="12" fill="#8b857a" text-anchor="middle">the layout is the whole argument: columnar optimizes reading a few columns,</text>
  <text x="400" y="262" font-size="12" fill="#8b857a" text-anchor="middle">row-based optimizes writing and moving whole records</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">Choose the axis first — columnar for analytics, row-based for streaming — and the rest is ecosystem.</figcaption>
</figure>

## Parquet vs ORC: the narrower call

Once you've chosen columnar, Parquet vs ORC is a closer, more ecosystem-driven
decision. Both store the schema in a file footer, both prune columns and skip data
using embedded statistics, both compress excellently. The practical differences:

- **Parquet** is the *default of the modern data stack* — Spark, the cloud
  warehouses, dbt, and every [open table format](/essays/what-is-an-open-table-format/)
  reach for it first. If you want the path of least resistance and maximum
  interoperability, it's Parquet.
- **ORC** grew up in the **Hive/Hadoop** world and has mature ACID support
  *within Hive*. It remains the natural choice where a Hive- or Trino-centric
  stack already favours it.

The head-to-head gets its own field note:
[Parquet vs ORC](/essays/parquet-vs-orc/), with the measured numbers.

**A correction.** An earlier version of this essay said ORC "often edges Parquet
on compression ratio," which is the conventional claim. I then
[benchmarked it](/essays/parquet-vs-orc-vs-avro-benchmark/) and got the opposite
result: at matched codecs on a realistic table, Parquet was 23–26% *smaller*.
That was one dataset and pyarrow's ORC writer at defaults, so it doesn't settle
the question everywhere — but it's enough that I no longer state the compression
advantage as fact. Measure it on your data before it decides anything.

For a greenfield [lakehouse](/glossary/data-lakehouse/), Parquet is the safe
default and ORC is a deliberate, situational choice — not a mistake, just one you
should be able to justify.

## Parquet vs Avro: the head-to-head

Parquet vs ORC is a choice between two things in the same slot. **Parquet vs Avro
is not** — they sit on opposite sides of the columnar/row-based split above, and
a well-built platform usually runs both. But the question gets asked directly and
constantly, so here is the direct answer, with the measured numbers.

### Size, measured on the same rows

From the [benchmark](/essays/parquet-vs-orc-vs-avro-benchmark/), on an identical
300,000-row subset of the same 11-column table:

| Format · codec | Size |
|---|---|
| **Parquet · zstd** | **6.47 MB** |
| ORC · zlib | 6.81 MB |
| Avro · deflate | 10.55 MB |
| Avro · snappy | 13.70 MB |
| Avro · uncompressed | 24.21 MB |

Parquet is **39% smaller than Avro at deflate** and **53% smaller at snappy**.
That gap is not about compression algorithms — the same codecs are available to
both. It is the layout. Columnar puts a million similar values next to each other,
which is exactly what a compressor wants; row-based interleaves eleven different
types and gives it far less to work with.

### The number that actually decides it

Compression is the smaller half. Here is what column pruning does, with each
format measured against **itself** on its own data — reading 2 of 11 columns
versus reading all 11:

| Format | Full scan | 2 of 11 columns | Effect |
|---|---|---|---|
| Parquet · zstd | 0.377 s | 0.054 s | **6.9× faster** |
| Parquet · snappy | 0.420 s | 0.055 s | **7.6× faster** |
| Avro · deflate | 1.353 s | 1.415 s | **1.05× slower** |
| Avro · snappy | 1.307 s | 1.427 s | **1.09× slower** |

Asking Avro for two columns is *very slightly worse* than asking it for all
eleven. There is no pruning to do: the reader walks every record and discards the
nine fields you didn't want, plus a little bookkeeping for the discarding. That is
the whole argument in one row of a table. **Analytical queries read a few columns
from many rows, and Avro cannot make that cheap.**

The two blocks above measure different row counts (3M for Parquet, 300k for
Avro), so read them as **ratios within each format**, which is what they are —
not as a head-to-head of absolute seconds.

### What I am deliberately not claiming

The conventional line is that Avro writes faster. **This benchmark cannot support
that**, and I am not going to pretend otherwise in either direction. Avro was
written with `fastavro`, a pure-Python library, against pyarrow's C++ Parquet
writer — that is an implementation gap, not a format gap, and it is also why Avro
runs on a 300k subset rather than the full 3M rows. The write timings are in the
[published results](/essays/parquet-vs-orc-vs-avro-benchmark/) if you want them,
but I would not draw a format conclusion from them, and neither should you.

### Where Avro genuinely wins

None of the above makes Avro the loser. It makes it a different tool:

- **Schema evolution across independent systems.** Avro carries a full schema with
  the data and has the richest reader/writer resolution rules of the three. When a
  producer and a consumer are deployed by different teams on different days, that
  is worth more than scan speed.
- **Streaming and message payloads.** Avro is the default in the Kafka ecosystem,
  and pairs with a schema registry. Records arrive one at a time and are written
  whole — the shape row-based is built for.
- **Write-once, read-whole workloads.** Event logs and change records that are
  replayed in full rather than aggregated by column.
- **Inside table formats.** Iceberg stores its own *manifest metadata* in Avro
  while the data files are Parquet — a neat illustration that this was never an
  either/or.

**The rule:** if the question is "what do I query," it is Parquet. If the question
is "what do I move," it is Avro. Most real platforms answer both questions and so
run both formats, with Avro on the wire and Parquet at rest.

## The decision rule

```text
Is the workload read-heavy analytics (scan columns, aggregate)?
   → Columnar.
       On a modern / cloud / lakehouse stack?      → Parquet
       Deep in Hive/Hadoop, or compression-critical? → ORC

Is the workload write-heavy / streaming / cross-system exchange,
or is schema evolution across producers the hard part?
   → Row-based → Avro
```

## The twist: it's rarely either/or

Mature stacks use all three, each where it fits. Avro carries events through
[Kafka streaming](/essays/batch-vs-streaming/) pipelines; those events land and
are rewritten as Parquet for the analytical layer; a Hive-heavy corner might keep
ORC. And here's the detail that surprises people: even when your *data* files are
Parquet, the table format's own **metadata manifests are often Avro** — because
manifest files are written whole and benefit from exactly Avro's row-based,
schema-evolvable design. The formats aren't rivals fighting for one slot; they're
specialists, and a well-built platform hires all three. The skill is matching the
format to the layer — which, one rung up, is the same instinct behind choosing
[a table format over bare files](/essays/apache-iceberg-vs-parquet/) in the first
place.
