---
last_modified_at: 2026-07-06
title: "Data Lakehouse"
description: "A lakehouse is a data lake with an open table format layered on top — one copy of data on object storage, with warehouse-grade guarantees, queryable by any engine."
essay: data-lake-vs-lakehouse
related_terms:
  - data-lake
  - data-warehouse
  - open-table-format
  - medallion-architecture
---

A **data lakehouse** is an architecture that keeps data as files in cheap object
storage — the [lake](/glossary/data-lake/) part — while an
[open table format](/glossary/open-table-format/) layered on top provides what
the lake lacked: ACID transactions, schema enforcement and evolution, and time
travel. The result aims to be one system serving both warehouse workloads
(reliable BI) and lake workloads (ML, data science) from a single copy of data.

The load-bearing component is the table format and its catalog; the usual
organising convention is the
[medallion architecture](/glossary/medallion-architecture/). The honest caveat:
more moving parts than a turnkey
[warehouse](/glossary/data-warehouse/), which remains simpler when workloads are
purely structured BI.
