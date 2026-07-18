---
last_modified_at: 2026-07-06
title: "Change Data Capture (CDC)"
description: "Change data capture streams every insert, update, and delete out of a database by reading its transaction log, instead of repeatedly querying for changes."
essay: what-is-change-data-capture
related_terms:
  - open-table-format
  - idempotent-pipeline
---

**Change data capture** (CDC) is the technique of extracting changes from a
database — every insert, update, and delete — by reading the transaction log the
database already writes, rather than polling tables with timestamp filters. The
log is ground truth: changes come out complete, ordered, and including deletes,
with near-zero load on the source.

CDC is how operational data reaches analytical systems with minutes-level
freshness, and log-based CDC (e.g. Debezium) is the standard modern
implementation. The capture itself is the easy half; applying the stream to a
target correctly requires an
[idempotent](/glossary/idempotent-pipeline/) merge, schema-change handling, and
an initial snapshot — the operational machinery around the log reader.
