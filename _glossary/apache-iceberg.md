---
title: "Apache Iceberg"
description: "Apache Iceberg is an open table format for data lakes — vendor-neutral, ASF-governed, and in 2026 the industry's default standard for multi-engine lakehouse tables."
essay: iceberg-vs-delta-lake
related_terms:
  - open-table-format
  - delta-lake
  - data-lakehouse
---

**Apache Iceberg** is an [open table format](/glossary/open-table-format/) that
turns Parquet files in object storage into database-grade tables — ACID commits,
schema evolution, hidden partitioning, and time travel — governed by the Apache
Software Foundation rather than any single vendor.

Its distinguishing achievement is neutrality: Snowflake, Databricks, BigQuery,
AWS, Trino, and Flink all read and write Iceberg, and its REST catalog
specification is what engines standardise against. The v3 spec (GA across major
platforms in 2026) added deletion vectors, a variant type for semi-structured
data, and geospatial types. For an open, multi-engine
[lakehouse](/glossary/data-lakehouse/), Iceberg is the default choice; the
livelier question is which catalog governs it.
