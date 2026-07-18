---
last_modified_at: 2026-07-08
title: "Data Vault"
description: "Data vault is a warehouse modeling method splitting entities into hubs (keys), links (relationships), and satellites (history) to absorb change and support audit."
essay: data-vault-vs-dimensional-modeling
related_terms:
  - data-warehouse
  - star-schema
---

**Data vault** is a modeling methodology for the warehouse *integration* layer
that splits every entity into three parts: **hubs** (just the business keys),
**links** (relationships between keys), and **satellites** (descriptive
attributes with full history). Everything is append-only and stamped with load
time and source, so the vault absorbs new sources and schema change by *adding*
tables, never altering them — and history is auditable by construction.

The cost is table count and joins: a vault is not meant to be queried by humans,
so a presentation layer of [star schemas](/glossary/star-schema/) is built on
top. It earns its complexity in large, regulated, many-source estates; smaller
shops usually go straight to dimensional.
