---
title: "Natural Key"
description: "A natural key is an identifier that comes from the business or source system itself — like an email, SKU, or account number — as opposed to a generated surrogate key."
essay: surrogate-keys-vs-natural-keys
related_terms:
  - surrogate-key
  - dimension-table
---

A **natural key** (or business key) is an identifier that already exists in the
business domain: an account number, SKU, email address, or national ID. It
arrives with the data, means something to users, and is how source systems refer
to the entity.

Natural keys remain essential in the warehouse — they're how you match incoming
records to existing dimension rows — but they make poor primary keys for
dimensions: they get recycled, reformatted, and duplicated across systems, and
they can't represent history. Standard practice keeps the natural key as an
attribute for lookups and joins to source data, while a generated
[surrogate key](/glossary/surrogate-key/) serves as the actual primary key.
