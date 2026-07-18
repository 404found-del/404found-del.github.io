---
last_modified_at: 2026-07-08
title: "Delta Lake"
description: "Delta Lake is an open table format created by Databricks — native to Databricks and Microsoft Fabric, with UniForm presenting Delta tables as Iceberg."
essay: iceberg-vs-delta-lake
related_terms:
  - open-table-format
  - apache-iceberg
  - data-lakehouse
---

**Delta Lake** is an [open table format](/glossary/open-table-format/) created
by Databricks and governed under the Linux Foundation. Like
[Apache Iceberg](/glossary/apache-iceberg/), it provides ACID transactions,
schema evolution, time travel, and deletion vectors over Parquet files — the two
formats have largely converged on capabilities.

Its strength is platform gravity: Delta is the native format of Databricks and
Microsoft Fabric, where it's the lowest-friction choice by far. Delta Lake 4.0's
Kernel gives non-Spark engines one consistent library, and **UniForm** writes
Iceberg metadata alongside Delta's own, letting a single physical table be read
by Iceberg-expecting engines. The practical 2026 rule: Delta inside
Databricks/Fabric, Iceberg for the open multi-engine world.
