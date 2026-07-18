---
last_modified_at: 2026-07-06
title: "ELT (Extract, Load, Transform)"
description: "ELT loads raw data into the warehouse first and transforms it there with SQL — the modern default, keeping raw history and putting logic where analysts work."
essay: etl-vs-elt
related_terms:
  - etl
  - medallion-architecture
  - data-lakehouse
---

**ELT** — extract, load, transform — loads raw data into the warehouse or
lakehouse *first* and transforms it there, in SQL, using the destination's own
compute. It became the default when cloud warehouses made storage and compute
cheap and elastic: land everything, keep the raw history, and let transformation
be versioned SQL (the dbt model) that analysts can read and change.

Keeping raw data means any table can be rebuilt by replay — the same instinct as
the bronze layer of a
[medallion architecture](/glossary/medallion-architecture/). The trade-off
versus [ETL](/glossary/etl/) is that ungoverned raw data and compute bills both
accumulate; ELT shifts the discipline problem downstream rather than
eliminating it.
