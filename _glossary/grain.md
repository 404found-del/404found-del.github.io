---
title: "Grain"
description: "The grain is the business definition of what one row in a fact table represents — declared first, before dimensions and measures, in dimensional modeling."
essay: fact-table-grain
related_terms:
  - fact-table
  - dimension-table
---

The **grain** of a fact table is the precise business definition of what a single
row represents: *one row per order line*, *one row per account per month*, *one
row per boarding-pass scan*. It is declared first in dimensional design — before
choosing dimensions or measures — because it is the test everything else must
pass: a dimension belongs only if it's single-valued at the grain; a measure
belongs only if it's true at the grain.

Mixing two grains in one table is the classic dimensional modeling bug, and the
root cause of most double-counting. The standard advice is to declare the most
*atomic* grain the source produces: detail can always be aggregated up, but a
coarse grain can never be drilled back down.
