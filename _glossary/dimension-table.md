---
last_modified_at: 2026-07-06
title: "Dimension Table"
description: "A dimension table stores descriptive context: the attributes you filter and group by, like customer, product or date, surrounding the facts in a dimensional model."
essay: fact-table-vs-dimension-table
related_terms:
  - fact-table
  - conformed-dimension
  - slowly-changing-dimension
---

A **dimension table** stores the descriptive context of a business process — the
*who, what, where, when* that measurements are sliced by: customer, product,
store, date. Where a [fact table](/glossary/fact-table/) is long and narrow, a
dimension is wide and comparatively short: many descriptive attributes, far fewer
rows.

Dimensions do the work in analytics: nearly every filter, group-by, and report
label comes from a dimension attribute. Their two design questions are how to key
them (usually a [surrogate key](/glossary/surrogate-key/)) and how to handle
attribute change over time — the
[slowly changing dimension](/glossary/slowly-changing-dimension/) problem. Shared
across fact tables, they become
[conformed dimensions](/glossary/conformed-dimension/), the mechanism that makes
metrics comparable across an organisation.
