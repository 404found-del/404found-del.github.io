---
last_modified_at: 2026-07-06
title: "OLAP (Online Analytical Processing)"
description: "OLAP is the analytical workload — large, read-heavy queries aggregating millions of rows — served by warehouses and columnar engines rather than operational databases."
essay: oltp-vs-olap
related_terms:
  - oltp
  - data-warehouse
  - star-schema
---

**OLAP** — online analytical processing — is the workload of analysis: queries
that scan and aggregate millions of rows to answer questions like *revenue by
region by quarter*. Few queries, each large; overwhelmingly reads; latency
measured in seconds rather than milliseconds.

OLAP systems — warehouses, columnar engines, lakehouse query engines — optimize
for this shape with columnar storage, compression, and denormalized models like
the [star schema](/glossary/star-schema/). The contrast with
[OLTP](/glossary/oltp/) (many small transactional operations) is the founding
distinction of data architecture: one shape runs the business, the other
understands it, and each needs storage designed for its own access pattern.
