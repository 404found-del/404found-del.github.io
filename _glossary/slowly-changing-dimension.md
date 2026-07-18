---
last_modified_at: 2026-07-06
title: "Slowly Changing Dimension (SCD)"
description: "A slowly changing dimension is a dimension whose attributes change over time; SCD types define whether to overwrite history (Type 1) or preserve it (Type 2)."
essay: slowly-changing-dimensions-explained
related_terms:
  - dimension-table
  - surrogate-key
---

A **slowly changing dimension** (SCD) is any
[dimension](/glossary/dimension-table/) whose descriptive attributes change over
time — customers move cities, products get recategorised — forcing a choice about
history. The SCD *types* name the standard answers.

**Type 1** overwrites: keep only the current value, lose history — last year's
sales appear under the customer's current city. **Type 2** versions: insert a new
row for each change, with validity dates and its own
[surrogate key](/glossary/surrogate-key/), so facts join to the version true at
the time. Type 2 keeps history honest at the cost of more rows and careful ETL.
The right type per attribute is a business decision disguised as a technical
one: do old orders belong to the old segment, or the new?
