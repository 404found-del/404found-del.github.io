---
title: "Open Table Format"
description: "An open table format is a published metadata spec — Iceberg, Delta Lake, Hudi — that turns files in object storage into tables with ACID transactions and time travel."
essay: what-is-an-open-table-format
related_terms:
  - data-lakehouse
  - data-lake
  - change-data-capture
---

An **open table format** is a published, engine-neutral metadata specification
that makes a collection of files in object storage behave like a database table:
tracking which files belong to the table, under what schema, across which
versions. The three names are **Apache Iceberg**, **Delta Lake**, and **Apache
Hudi** — with Iceberg having emerged as the industry's neutral standard.

The mechanism is a small tree of metadata committed by atomic pointer swap, which
yields ACID transactions, safe schema evolution, row-level updates and deletes,
and time travel — on plain Parquet files. It is the ingredient that turns a
[data lake](/glossary/data-lake/) into a
[lakehouse](/glossary/data-lakehouse/), and "open" is the point: no single
vendor owns your tables.
