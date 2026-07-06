---
title: "Star Schema"
description: "A star schema is a dimensional model with a central fact table joined directly to flat, denormalized dimension tables — the default shape for analytics."
essay: star-schema-vs-snowflake-schema
related_terms:
  - snowflake-schema
  - fact-table
  - dimension-table
---

A **star schema** is the standard shape of a dimensional model: a central
[fact table](/glossary/fact-table/) of measurements joined directly to a set of
flat, denormalized [dimension tables](/glossary/dimension-table/). Drawn on a
whiteboard, the fact sits in the middle with dimensions radiating outward — hence
the star.

The design optimizes for reads: every query is the same simple join shape, one
hop from fact to any context. Its counterpart, the
[snowflake schema](/glossary/snowflake-schema/), normalizes dimensions into
related sub-tables — trading query simplicity for storage normalization, a trade
that rarely pays on modern columnar warehouses. The star is the sensible default
for analytical models.
