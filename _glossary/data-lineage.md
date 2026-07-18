---
last_modified_at: 2026-07-06
title: "Data Lineage"
description: "Data lineage is the traced path of data through systems — where each field came from, what transformed it, and what depends on it downstream."
essay: what-is-data-lineage
related_terms:
  - data-catalog
  - data-contract
---

**Data lineage** is the record of where data came from and what happened to it
along the way: which source produced a field, which transformations touched it,
and which tables, dashboards, and models depend on it downstream. Column-level
lineage answers the two questions every data team asks weekly — *"can I trust
this number?"* (trace it back) and *"what breaks if I change this?"* (trace it
forward).

Lineage is typically harvested automatically from SQL parsing, orchestrator
metadata, and warehouse query logs, and surfaced in a
[data catalog](/glossary/data-catalog/). Its practical value is impact analysis,
incident debugging, and audit — provenance you can query instead of tribal
knowledge you have to ask around for.
