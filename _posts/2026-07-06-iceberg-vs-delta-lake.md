---
title: "Iceberg vs Delta Lake: How to Actually Choose in 2026"
kicker: "Field Notes"
topic: "Architecture"
description: "Iceberg and Delta Lake have converged on capabilities — ACID, time travel, deletion vectors. The real decision is your platform and catalog, not the format."
date: 2026-07-06 09:00:00 +0530
faq:
  - q: "Which is better, Apache Iceberg or Delta Lake?"
    a: "Neither, on raw capabilities — with Iceberg v3 and Delta Lake 4.0 both provide ACID transactions, schema evolution, time travel, and deletion vectors. The practical answer is platform fit: Delta is the frictionless choice inside Databricks and Fabric; Iceberg is the safer default for open, multi-engine lakehouses because every major platform reads and writes it."
  - q: "What is Delta UniForm?"
    a: "A Delta Lake feature that writes Iceberg (and Hudi) metadata alongside Delta's own, so one physical table can be read by engines expecting any of the three formats. It's Databricks' answer to Iceberg's rise as the neutral standard — write Delta, present Iceberg."
  - q: "Is the Iceberg vs Delta decision permanent?"
    a: "Much less than it used to be. UniForm and Apache XTable can translate metadata between formats over the same Parquet files, so a migration no longer means rewriting data. Optimize for your dominant platform today and let interoperability cover the rest."
  - q: "What matters more than the table format?"
    a: "The catalog — the component that holds each table's pointer and decides who may commit to it. Formats have converged; catalogs (Unity, Polaris, Glue, Horizon, Nessie) are where governance and the remaining lock-in now live. Choose the catalog as carefully as you once chose the format."
---

For years, choosing between **Apache Iceberg** and **Delta Lake** was the defining
architecture decision of a lakehouse. In 2026, it mostly isn't. The two
[open table formats](/essays/what-is-an-open-table-format/) have converged on
capabilities — ACID commits, schema evolution, time travel, row-level deletes via
deletion vectors — and interop layers can present one format as the other. The
honest decision rule now fits in two sentences: **inside Databricks or Microsoft
Fabric, use Delta — it's the native format and everything is tuned for it.
Everywhere else, or for anything multi-engine, default to Iceberg — it has become
the neutral standard that every major platform reads and writes.**

Here's the reasoning, and the one decision that still deserves your attention
more than the format.

## The comparison, honestly

| | Apache Iceberg | Delta Lake |
|---|---|---|
| **Governance** | Apache Software Foundation, multi-vendor | Linux Foundation, Databricks-led |
| **Core guarantees** | ACID, schema evolution, time travel | Same |
| **Row-level deletes** | Deletion vectors (v3) | Deletion vectors |
| **Semi-structured** | Variant type (v3) | Variant type |
| **Native home** | Snowflake, BigQuery, AWS, Trino, Flink | Databricks, Microsoft Fabric |
| **Multi-engine story** | Native — REST catalog spec | Delta Kernel (4.0), UniForm |
| **Interop escape hatch** | Read/written by nearly everything | UniForm presents Delta as Iceberg |
| **Choose it when** | Open, multi-engine, vendor-neutral | Databricks/Fabric-centred platform |

The capability rows are the point: they're nearly identical. Both store data as
Parquet; both added deletion vectors and a variant type in their 2025–2026 spec
cycles (Iceberg v3, Delta 4.0). Performance differences are workload- and
engine-specific, not categorical. Anyone selling you a decisive feature gap is
reading from an old slide.

## What actually differs: gravity

**Delta's gravity is Databricks.** It's the native tongue of the platform where a
majority of Fortune-500 data teams already run, and Fabric adopted it too. Inside
that world, Delta is simply less friction — and UniForm lets a Delta table
publish Iceberg metadata so outside engines can still read it.

**Iceberg's gravity is everyone else.** Snowflake ships first-class Iceberg
tables, BigQuery reads it through BigLake, AWS backs it across Glue and
Athena, and the Iceberg REST catalog spec is what engines standardise against.
Even Databricks now writes Iceberg through Unity Catalog. When the whole industry
needs one table language to interoperate, it picked Iceberg.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 320" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
  <rect x="250" y="20" width="300" height="54" rx="6" fill="#1c1a17"/>
  <text x="400" y="43" font-size="13" fill="#f6f3ec" text-anchor="middle">Where does your compute live,</text>
  <text x="400" y="62" font-size="13" fill="#f6f3ec" text-anchor="middle">today and in 3 years?</text>
  <line x1="320" y1="74" x2="185" y2="130" stroke="#cabfac" stroke-width="2"/>
  <line x1="480" y1="74" x2="615" y2="130" stroke="#cabfac" stroke-width="2"/>
  <text x="205" y="115" font-size="11" fill="#8b857a">mostly Databricks / Fabric</text>
  <text x="480" y="115" font-size="11" fill="#8b857a">mixed / multi-engine / unsure</text>
  <rect x="60" y="130" width="250" height="64" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="185" y="157" font-size="14" fill="#1c1a17" text-anchor="middle" font-weight="700">Delta Lake</text>
  <text x="185" y="178" font-size="11" fill="#56514a" text-anchor="middle">+ UniForm for outside readers</text>
  <rect x="490" y="130" width="250" height="64" rx="6" fill="#c8472b"/>
  <text x="615" y="157" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">Apache Iceberg</text>
  <text x="615" y="178" font-size="11" fill="#f6f3ec" text-anchor="middle">the neutral default</text>
  <line x1="185" y1="194" x2="360" y2="250" stroke="#ddd6c8" stroke-width="2"/>
  <line x1="615" y1="194" x2="440" y2="250" stroke="#ddd6c8" stroke-width="2"/>
  <rect x="220" y="250" width="360" height="50" rx="6" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="400" y="272" font-size="12" fill="#1c1a17" text-anchor="middle">either way: choose the CATALOG deliberately —</text>
  <text x="400" y="290" font-size="12" fill="#1c1a17" text-anchor="middle">that's where lock-in lives now</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">The 2026 decision tree is short — and its last box matters more than its first.</figcaption>
</figure>

## Day-to-day, they feel the same

The SQL is nearly interchangeable — which is itself the argument that the format
war is over:

```sql
-- Iceberg (Spark SQL)
CREATE TABLE lake.sales.orders (
  order_id BIGINT, order_ts TIMESTAMP, amount DECIMAL(12,2)
) USING iceberg PARTITIONED BY (days(order_ts));

SELECT * FROM lake.sales.orders
FOR TIMESTAMP AS OF current_timestamp - INTERVAL '1' DAY;

-- Delta (Spark SQL)
CREATE TABLE lake.sales.orders (
  order_id BIGINT, order_ts TIMESTAMP, amount DECIMAL(12,2)
) USING delta;

SELECT * FROM lake.sales.orders TIMESTAMP AS OF date_sub(current_date(), 1);
```

Same guarantees, slightly different spellings. Your engineers will not care
which one they're on within a month.

## The decision that still matters: the catalog

Because the formats converged, the strategic weight moved up a layer — to the
**catalog** that holds each table's atomic pointer and governs who may commit:
Unity (Databricks), Polaris and Horizon (Snowflake's open-source and managed),
Glue (AWS), Nessie, and others. The catalog is where access control, auditing,
and cross-engine governance actually happen, and switching catalogs is far more
painful than translating table metadata. If you're building a
[lakehouse](/essays/data-lake-vs-lakehouse/) in 2026, spend your evaluation
weeks there — [choosing the catalog](/essays/how-to-choose-an-iceberg-catalog/)
is its own decision, and the format choice, pleasantly, has become the easy
part.
