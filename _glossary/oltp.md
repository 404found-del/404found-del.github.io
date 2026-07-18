---
last_modified_at: 2026-07-06
title: "OLTP (Online Transaction Processing)"
description: "OLTP systems run the business in real time — many small, concurrent reads and writes of individual records, on normalized schemas optimized for integrity."
essay: oltp-vs-olap
related_terms:
  - olap
  - data-warehouse
---

**OLTP** — online transaction processing — is the workload of systems that *run*
the business: placing orders, updating balances, booking seats. Its shape is many
small, concurrent operations touching individual records, where correctness and
speed of single-row reads and writes are everything. OLTP databases use
normalized schemas precisely to make those writes safe and non-redundant.

Its counterpart, [OLAP](/glossary/olap/), is the workload of systems that
*analyse* the business — few, large, read-heavy queries scanning millions of
rows. The two shapes conflict in one engine, which is why operational data is
replicated into a [warehouse](/glossary/data-warehouse/) or lakehouse for
analytics instead of being analysed in place.
