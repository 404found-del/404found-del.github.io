---
title: "What Is an Open Table Format? Iceberg, Delta, and Hudi Explained"
kicker: "Field Notes"
topic: "Architecture"
description: "An open table format is a metadata spec that turns raw files in object storage into real tables — with ACID transactions, schema evolution, and time travel."
date: 2026-07-05 09:00:00 +0530
last_modified_at: 2026-07-26
faq:
  - q: "What is an open table format in simple terms?"
    a: "It's a published specification for a metadata layer that sits on top of data files in object storage and makes them behave like a database table — tracking which files belong to the table, what schema they follow, and what the table looked like at any point in time. Apache Iceberg, Delta Lake, and Apache Hudi are the three main ones."
  - q: "Is an open table format the same thing as a file format like Parquet?"
    a: "No. Parquet defines how bytes are laid out inside one file. A table format defines how many files together form a table — which files are current, what schema applies, and how changes commit atomically. Iceberg, Delta, and Hudi all typically store their data in Parquet underneath."
  - q: "Which open table format should I choose in 2026?"
    a: "Apache Iceberg has become the de facto neutral standard — Databricks, Snowflake, BigQuery, and Fabric all read and write it. Delta Lake remains excellent inside the Databricks ecosystem, and interop layers like UniForm blur the line. For a new multi-engine lakehouse, Iceberg is the safe default; the more consequential choice now is the catalog."
  - q: "Do I need an open table format if I use a data warehouse?"
    a: "If all your data lives happily inside one warehouse and one engine, no — the warehouse's internal format already does this job. Table formats earn their keep when you want cheap object storage as the single copy of data and multiple engines querying it without replication."
---

An **open table format** is a metadata layer that turns a pile of files in object
storage into a real table — one with ACID transactions, an enforced schema, and a
queryable history. The data stays as ordinary Parquet files in S3, ADLS, or GCS; the
table format is a small tree of metadata files alongside them that records, for every
version of the table, exactly which data files belong to it and under what schema.
"Open" means the spec is published and engine-neutral: Spark, Trino, Flink, Snowflake,
and BigQuery can all read and write the *same* table without a proprietary gatekeeper. (If you're unsure how a
table format differs from the Parquet files underneath it, start with
[Iceberg vs Parquet](/essays/apache-iceberg-vs-parquet/); for the file layer
itself, [Parquet vs ORC vs Avro](/essays/parquet-vs-orc-vs-avro/), and for the
measured version of that comparison,
[the benchmark](/essays/parquet-vs-orc-vs-avro-benchmark/).)
The three names that matter are **[Apache Iceberg](/glossary/apache-iceberg/)**, **[Delta Lake](/glossary/delta-lake/)**, and **Apache
Hudi** — and as of 2026, the industry has largely converged on Iceberg as the neutral
standard.

This is the ingredient that turns a [data lake into a
lakehouse](/essays/data-lake-vs-lakehouse/). Everything else in the lakehouse story
depends on it.

## What problem does a table format solve?

A bare [data lake](/glossary/data-lake/) is just files. Nothing says which files form the "orders" table,
whether a half-finished write should be visible, or what the table contained
yesterday. Two jobs writing at once can corrupt each other; a schema change means
hoping every reader notices. A table format fixes all four failures at once:

| | Bare files in a lake | With an open table format |
|---|---|---|
| **What is the table?** | A folder, by convention | An explicit manifest of files |
| **Concurrent writes** | Unsafe, last-write wins | ACID commits, optimistic concurrency |
| **Schema changes** | Break readers silently | Versioned, safe evolution |
| **History** | Gone on overwrite | Snapshots + time travel |
| **Deletes/updates** | Rewrite everything | Row-level, via delete files or vectors |

## How it works: a tree of metadata

Every table format is, at heart, the same trick: an atomic pointer to an immutable
snapshot. A catalog holds one tiny pointer per table; the pointer names a metadata
file; the metadata file names the snapshot; the snapshot lists the data files.
Committing a change means writing new files and swapping one pointer — which is why a
commit is atomic even on eventually-consistent object storage.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 380" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="what-is-an-open-table-format-t what-is-an-open-table-format-d">
  <title id="what-is-an-open-table-format-t">The metadata tree shared by every open table format</title>
  <desc id="what-is-an-open-table-format-d">A four-level chain: the catalog holds one atomic pointer per table; the pointer names a table metadata file holding schema, partitioning and snapshots; the metadata names a snapshot and its manifests; the snapshot lists the underlying Parquet data files and delete files. A commit writes new files and swaps one pointer.</desc>
  <rect x="290" y="16" width="220" height="48" rx="6" fill="#1c1a17"/>
  <text x="400" y="45" font-size="15" fill="#f6f3ec" text-anchor="middle">catalog</text>
  <text x="620" y="45" font-size="12" fill="#8a7f6d">one atomic pointer per table</text>
  <line x1="400" y1="64" x2="400" y2="96" stroke="#cabfac" stroke-width="2"/>
  <rect x="290" y="96" width="220" height="48" rx="6" fill="#c8472b"/>
  <text x="400" y="125" font-size="15" fill="#f6f3ec" text-anchor="middle">table metadata</text>
  <text x="620" y="125" font-size="12" fill="#8a7f6d">schema, partitioning, snapshots</text>
  <line x1="400" y1="144" x2="400" y2="176" stroke="#cabfac" stroke-width="2"/>
  <rect x="290" y="176" width="220" height="48" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="400" y="205" font-size="15" fill="#1c1a17" text-anchor="middle">snapshot / manifests</text>
  <text x="620" y="205" font-size="12" fill="#8a7f6d">which files, with stats</text>
  <line x1="400" y1="224" x2="220" y2="266" stroke="#cabfac" stroke-width="2"/>
  <line x1="400" y1="224" x2="400" y2="266" stroke="#cabfac" stroke-width="2"/>
  <line x1="400" y1="224" x2="580" y2="266" stroke="#cabfac" stroke-width="2"/>
  <rect x="130" y="266" width="180" height="44" rx="6" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="220" y="293" font-size="13" fill="#1c1a17" text-anchor="middle">data-001.parquet</text>
  <rect x="310" y="266" width="180" height="44" rx="6" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="400" y="293" font-size="13" fill="#1c1a17" text-anchor="middle">data-002.parquet</text>
  <rect x="490" y="266" width="180" height="44" rx="6" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="580" y="293" font-size="13" fill="#1c1a17" text-anchor="middle">delete-003.puffin</text>
  <text x="400" y="352" font-size="12" fill="#8a7f6d" text-anchor="middle">a commit = write new files, swap one pointer — atomic even on object storage</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8a7f6d;margin-top:0.6rem;">The metadata tree every table format shares: pointer → metadata → snapshot → files.</figcaption>
</figure>

Because every snapshot is preserved until expired, you get **time travel** for free:

```sql
CREATE TABLE lake.sales.orders (
  order_id   BIGINT,
  customer_id BIGINT,
  order_ts   TIMESTAMP,
  amount     DECIMAL(12,2)
) USING iceberg
PARTITIONED BY (days(order_ts));

-- yesterday's numbers, exactly as they were.
-- The timestamp must be a literal: Spark requires a deterministic, foldable
-- expression here, so current_timestamp - INTERVAL '1' DAY is rejected.
SELECT sum(amount)
FROM lake.sales.orders
FOR TIMESTAMP AS OF '2026-07-04 00:00:00';

-- Or pin the exact snapshot, which is what you want in a reproducible job:
SELECT sum(amount) FROM lake.sales.orders FOR VERSION AS OF 3821550127947089000;

-- row-level change, committed atomically
MERGE INTO lake.sales.orders t
USING staged_orders s ON t.order_id = s.order_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

That `MERGE` is the operation a bare lake never had — and it's what makes patterns
like [change data capture](/essays/what-is-change-data-capture/) and an honest
[medallion architecture](/essays/the-medallion-architecture-reconsidered/) practical
on files. It also raises the question every format has to answer: since the data
files are immutable, does that `MERGE` rewrite them or annotate them? That's
[merge-on-read vs copy-on-write](/essays/merge-on-read-vs-copy-on-write/), and
it's the setting that decides what this convenience costs you.

## Iceberg vs Delta vs Hudi — where the war ended

For years this was a genuine three-way fight. It isn't anymore. **Iceberg** became
the neutral standard the moment every major platform adopted it: Databricks writes
Iceberg through Unity Catalog, Snowflake ships first-class Iceberg tables and
open-sourced its Polaris catalog, BigQuery reads it through BigLake, and Fabric
bridges to it from Delta. **Delta Lake** remains a superb format and the native
tongue of Databricks; UniForm lets a Delta table present itself as Iceberg. **Hudi**
retains a niche for high-frequency upsert ingestion but has faded as a default
choice. The 2026 spec work (Iceberg v3: deletion vectors, the variant type for
semi-structured data, geo types) landed in both Snowflake and Databricks the same
year — the formats are converging on the same capabilities. If you're facing the
choice directly, the [Iceberg vs Delta decision](/essays/iceberg-vs-delta-lake/)
gets its own field note.

Which is why the real architectural decision has moved up a layer: not *which
format*, but *which catalog* — the component that holds those atomic pointers and
governs who may swap them. That fight (Polaris, Unity, Glue, Snowflake Open
Catalog, Nessie) is still live, and it's where lock-in now hides.

## When you don't need one

If your data lives in one warehouse, queried by one engine, an open table format
adds moving parts and buys you little — the warehouse's internal format already
provides transactions and history. The format earns its complexity when the
[lakehouse premise](/essays/data-warehouse-vs-data-lake-vs-lakehouse/) applies: one
cheap copy of data on object storage, many engines reading it, no
[per-engine ETL](/essays/etl-vs-elt/) to keep copies in sync. That premise is why
the [modern data stack debate](/essays/is-the-modern-data-stack-dead/) keeps
circling back to open storage: whatever happens to the tools above, tables that no
single vendor owns are the part everyone has agreed to keep.
