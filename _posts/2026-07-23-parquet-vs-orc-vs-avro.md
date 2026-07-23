---
title: "Parquet vs ORC vs Avro: Which Data File Format, and When"
kicker: "Field Notes"
topic: "Architecture"
description: "Parquet and ORC are columnar formats for analytics; Avro is row-based for streaming and schema evolution. A clear comparison and a decision rule that holds."
date: 2026-07-23 11:00:00 +0530
faq:
  - q: "What is the difference between Parquet, ORC, and Avro?"
    a: "Parquet and ORC are columnar formats — they store all of one column together, which makes analytical queries that read a few columns fast and highly compressible. Avro is row-based — it stores whole records together, which makes it fast to write and ideal for streaming and data exchange. Columnar wins for reads and analytics; row-based wins for writes, streaming, and schema evolution."
  - q: "Which is better, Parquet or ORC?"
    a: "Both are columnar and both are excellent; the difference is ecosystem more than capability. Parquet is the de facto default across Spark, the cloud warehouses, and most of the modern data stack, and it's what open table formats reach for. ORC often achieves slightly higher compression and has deep roots in the Hive/Hadoop world, including ACID support there. For a new lakehouse, Parquet is the safe default; ORC pays off mainly where a Hive-centric stack or its compression edge specifically matters."
  - q: "When should I use Avro instead of Parquet?"
    a: "Use Avro when writes dominate reads: streaming pipelines (it's the standard in the Kafka ecosystem), event logs, and any place records are written whole and often, or where schema evolution across systems matters. Avro's row-based layout and rich schema-evolution support make it ideal for moving data; its weakness is analytical queries, where columnar Parquet or ORC is far faster."
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
| **Compression** | Excellent | Excellent (often highest) | Moderate |
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
compress hard. That's exactly the shape of an [OLAP](/glossary/olap/) analytical
scan, and it's why both dominate the warehouse and lakehouse world.

A **row-based** format (Avro) stores each record whole: all of row 1's fields
together, then row 2. Writing an event is one contiguous append; reading one
record back is cheap. But an analytical query that wants one column still has to
read past every other field in every row — the opposite of what analytics wants.
Avro's home is therefore *movement*: the Kafka streaming ecosystem, event logs,
and cross-system exchange, where records are written whole and schema evolution
across producers and consumers is a first-class concern.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
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
- **ORC** grew up in the **Hive/Hadoop** world, often edges Parquet on compression
  ratio, and has mature ACID support *within Hive*. It remains the natural choice
  where a Hive- or Trino-centric stack already favours it, or where its compression
  advantage is worth optimizing for at scale.

For a greenfield [lakehouse](/glossary/data-lakehouse/), Parquet is the safe
default and ORC is a deliberate, situational choice — not a mistake, just one you
should be able to justify.

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
