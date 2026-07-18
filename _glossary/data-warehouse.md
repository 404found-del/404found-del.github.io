---
last_modified_at: 2026-07-06
title: "Data Warehouse"
description: "A data warehouse is a centralized, structured analytical database — modelled, governed, and optimized for reliable BI queries across an organisation."
essay: data-warehouse-vs-data-lake-vs-lakehouse
related_terms:
  - data-lake
  - data-lakehouse
  - olap
---

A **data warehouse** is a centralized analytical database that stores
integrated, modelled, historical data from across an organisation, optimized for
the read-heavy query patterns of BI and reporting — an
[OLAP](/glossary/olap/) workload. Data arrives through pipelines, is conformed
into a deliberate schema (classically [star schemas](/glossary/star-schema/)),
and is served to analysts with strong guarantees: consistent definitions,
transactions, and predictable performance.

The warehouse's defining trade-off is structure up front: everything in it was
modelled on purpose, which is what makes it trustworthy — and what makes it
slower to absorb new, messy, or unstructured data than a
[data lake](/glossary/data-lake/). The [lakehouse](/glossary/data-lakehouse/) is
the current attempt to offer both in one system.
