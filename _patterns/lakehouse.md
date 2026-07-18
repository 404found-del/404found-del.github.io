---
last_modified_at: 2026-07-18
title: "Lakehouse"
intent: "Keep one copy of data as open-format tables on cheap object storage, and let every engine — SQL, Spark, ML — read and write it with warehouse-grade guarantees."
description: "The lakehouse pattern: open table formats over object storage, one copy of data for every engine, trade-offs, and when a plain warehouse is still right."
essays:
  - what-is-an-open-table-format
  - data-warehouse-vs-data-lake-vs-lakehouse
  - data-lake-vs-lakehouse
  - iceberg-vs-delta-lake
  - how-to-choose-an-iceberg-catalog
terms:
  - data-lakehouse
  - open-table-format
  - apache-iceberg
  - delta-lake
faq:
  - q: "What is a data lakehouse in simple terms?"
    a: "One copy of data, stored as open-format tables (Iceberg, Delta) on cheap object storage, with warehouse-grade guarantees — ACID transactions, schema enforcement, time travel — queryable by any engine: SQL for BI, Spark for ML, streaming for pipelines."
  - q: "Do I need a lakehouse if I already have a data warehouse?"
    a: "Only when the second workload actually appears. If all your work is structured BI in one engine, a warehouse is simpler and easier to run. The lakehouse earns its moving parts when ML, data science, or multi-engine access would otherwise force a second copy of the data."
  - q: "Which table format should a lakehouse use?"
    a: "Apache Iceberg has become the neutral standard — Databricks, Snowflake, BigQuery, and Fabric all read and write it. Delta Lake remains excellent inside Databricks, with UniForm bridging the two. The more consequential choice now is the catalog that governs the tables."
---

## Intent

End the two-copy world — one lake for ML, one warehouse for BI — by storing data
once, in an [open table format](/essays/what-is-an-open-table-format/) on object
storage, with ACID transactions and schema enforcement, queryable by any engine.

## Context

You run both structured analytics *and* lake-style workloads (ML, data science,
semi-structured data), and keeping copies in sync between a lake and a warehouse
has become its own engineering programme. Vendor lock-in on the storage layer is
a real concern.

## Structure

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
  <rect x="80" y="30" width="150" height="50" rx="6" fill="#1c1a17"/>
  <text x="155" y="60" font-size="13" fill="#f6f3ec" text-anchor="middle">SQL / BI</text>
  <rect x="325" y="30" width="150" height="50" rx="6" fill="#1c1a17"/>
  <text x="400" y="60" font-size="13" fill="#f6f3ec" text-anchor="middle">Spark / ML</text>
  <rect x="570" y="30" width="150" height="50" rx="6" fill="#1c1a17"/>
  <text x="645" y="60" font-size="13" fill="#f6f3ec" text-anchor="middle">Streaming</text>
  <line x1="155" y1="80" x2="330" y2="130" stroke="#cabfac" stroke-width="2"/>
  <line x1="400" y1="80" x2="400" y2="130" stroke="#cabfac" stroke-width="2"/>
  <line x1="645" y1="80" x2="470" y2="130" stroke="#cabfac" stroke-width="2"/>
  <rect x="200" y="130" width="400" height="56" rx="6" fill="#c8472b"/>
  <text x="400" y="157" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">open table format + catalog</text>
  <text x="400" y="176" font-size="11" fill="#f6f3ec" text-anchor="middle">ACID · schema · time travel · governance</text>
  <line x1="400" y1="186" x2="400" y2="216" stroke="#cabfac" stroke-width="2"/>
  <rect x="200" y="216" width="400" height="50" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="400" y="246" font-size="13" fill="#1c1a17" text-anchor="middle">object storage — one copy, Parquet files</text>
  <text x="400" y="290" font-size="12" fill="#8b857a" text-anchor="middle">every engine reads and writes the same tables; no replication between systems</text>
</svg>
</figure>

The load-bearing component is the table format (Iceberg, Delta) plus the
**catalog** that holds each table's atomic pointer and enforces who may commit —
which is where governance, and the remaining lock-in risk, now live.

## Trade-offs

**Gains:** one copy of data; engine choice per workload; cheap storage economics;
open formats outlive any vendor; time travel and safe schema evolution by
default.

**Costs:** more moving parts than a turnkey warehouse (format, catalog, engines,
maintenance jobs like compaction); performance tuning is *your* job; and the
convenience gap with a mature warehouse, while narrowing, is real. Organising
what goes where becomes its own discipline — usually the
[medallion pattern](/patterns/medallion-architecture/).

## When not to use it

Purely structured BI at moderate scale with one engine: a
[plain warehouse](/essays/data-warehouse-vs-data-lake-vs-lakehouse/) is simpler,
faster to run, and easier to staff. Adopt the lakehouse when the second copy or
the second engine actually appears — not before.
