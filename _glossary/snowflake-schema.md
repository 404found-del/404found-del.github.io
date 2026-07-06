---
title: "Snowflake Schema"
description: "A snowflake schema is a dimensional model whose dimensions are normalized into multiple related sub-tables instead of kept flat as in a star schema."
essay: star-schema-vs-snowflake-schema
related_terms:
  - star-schema
  - dimension-table
---

A **snowflake schema** is a dimensional model in which dimension tables are
normalized into multiple related sub-tables — product splitting into category and
brand tables, geography into city, region, and country. The branching shape gives
it the name.

The entire difference from a [star schema](/glossary/star-schema/) is that one
decision: normalized versus flat dimensions. Snowflaking saves some storage and
centralises repeated attribute values, but every level adds a join to every query
that touches it. On modern columnar warehouses, where compression makes the
storage saving negligible, the star's simplicity usually wins; snowflake a
dimension only when you can name the specific problem it solves.
