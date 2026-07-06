---
title: "Conformed Dimension"
description: "A conformed dimension is a dimension shared with identical meaning across multiple fact tables, letting metrics from different processes be compared correctly."
essay: conformed-dimensions
related_terms:
  - dimension-table
  - star-schema
---

A **conformed dimension** is a [dimension](/glossary/dimension-table/) that is
defined once and shared, with identical keys, attributes, and meaning, across
multiple [fact tables](/glossary/fact-table/). When sales, inventory, and support
tickets all join to the *same* customer dimension, "by customer" means the same
thing in every report — and numbers from different processes can be laid
side-by-side truthfully.

Conformed dimensions are the integration backbone of a dimensional warehouse
(Kimball's "bus architecture"). They're less a technical feature than an
organisational agreement: getting three departments to accept one definition of
customer is the hard part, and the value.
