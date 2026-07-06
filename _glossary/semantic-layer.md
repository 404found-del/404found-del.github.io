---
title: "Semantic Layer"
description: "A semantic layer is a shared definition layer between the warehouse and its consumers, where metrics like revenue are defined once and queried consistently everywhere."
essay: what-is-a-semantic-layer
related_terms:
  - data-catalog
  - star-schema
---

A **semantic layer** is a definition layer that sits between the warehouse and
everything that queries it, where business concepts — *revenue*, *active user*,
*churn* — are defined once, in one place, and every dashboard, notebook, and AI
assistant gets the same answer. Consumers ask for metrics by name; the layer
compiles them to correct SQL against the underlying
[star schemas](/glossary/star-schema/).

It exists because definitions scattered across BI tools drift, and drifting
definitions are how organisations end up with four numbers for revenue. The
semantic layer is increasingly load-bearing in the AI era: it's the vocabulary a
text-to-SQL system needs if its answers are to match the CFO's.
