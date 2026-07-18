---
last_modified_at: 2026-07-06
title: "Data Lake"
description: "A data lake is a large store of raw files in cheap object storage — any shape, structured later on read, with no transactions or enforced schema of its own."
essay: data-lake-vs-lakehouse
related_terms:
  - data-lakehouse
  - data-warehouse
  - open-table-format
---

A **data lake** is a large store of raw files in cheap object storage: tables,
JSON, logs, images — any shape, landed as-is, with structure applied later, on
read. Its economics are the appeal: storage is cheap enough to keep everything,
and nothing needs modelling up front, which suits data science and ML.

Its weakness is everything a bare pile of files doesn't provide — no
transactions, no enforced schema, no reliable history. Ungoverned, a lake drifts
into a *data swamp* nobody trusts. The modern fix is layering an
[open table format](/glossary/open-table-format/) over the same files, which
turns the lake into a [lakehouse](/glossary/data-lakehouse/).
