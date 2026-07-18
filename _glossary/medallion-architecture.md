---
last_modified_at: 2026-07-06
title: "Medallion Architecture"
description: "The medallion architecture organises a lakehouse into bronze (raw), silver (cleaned), and gold (consumable) layers of increasing refinement and trust."
essay: the-medallion-architecture-reconsidered
related_terms:
  - data-lakehouse
  - data-lake
---

The **medallion architecture** is a convention for organising a
[lakehouse](/glossary/data-lakehouse/) into three layers: **bronze** holds data
raw and immutable, exactly as ingested; **silver** holds it cleaned, typed,
deduplicated, and conformed; **gold** holds modelled, business-ready tables that
consumers actually query. Trust increases left to right, and every downstream
table can be rebuilt by replaying from bronze.

Its value is shared vocabulary and provenance; its danger is false completeness —
the layers say nothing about modelling, ownership, or definitions, which is where
analytics actually fails. Treat the three layers as a default to adapt (collapse
them for clean sources, add stages for complex ones), not a law.
