---
last_modified_at: 2026-07-18
title: "Star Schema"
intent: "Model analytical data as central fact tables of measurements surrounded by flat, denormalized dimension tables of context."
description: "The star schema pattern: fact and dimension structure, why it optimizes for reads and readability, trade-offs, and when a star is the wrong shape."
essays:
  - star-schema-vs-snowflake-schema
  - a-field-guide-to-dimensional-modeling
  - fact-table-vs-dimension-table
  - one-big-table-vs-star-schema
terms:
  - star-schema
  - fact-table
  - dimension-table
  - grain
faq:
  - q: "What is a star schema in simple terms?"
    a: "A central fact table of measurements (one row per event, like an order line) joined directly to flat dimension tables of context (customer, product, date). Every query is the same shape: aggregate measures from the fact, filtered and grouped by dimension attributes."
  - q: "Should I use a star schema or a snowflake schema?"
    a: "Default to the star. The only difference is whether dimensions stay flat (star) or are normalized into sub-tables (snowflake), and on modern columnar warehouses the snowflake's storage saving is negligible while its extra joins are permanent. Snowflake a dimension only for a specific, nameable problem."
  - q: "Is the star schema still relevant in the lakehouse era?"
    a: "Yes. Storage formats changed; the query shape of analytics didn't. Gold-layer tables in a lakehouse are very often star schemas, and semantic layers compile metrics down to them. The star survives because it matches how business questions are asked."
---

## Intent

Make analytics fast, readable, and consistent by separating **measurements**
(fact tables) from **context** (dimension tables), keeping each dimension flat
and denormalized so queries are simple joins from one central table.

## Context

Many people query the same data for analysis. Questions follow a stable shape —
*aggregate a measure, filtered and grouped by context* — and you value
consistency and predictable performance over write efficiency. The warehouse is
read-heavy: written by a few pipelines, queried by everyone.

## Structure

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 340" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
  <rect x="310" y="130" width="180" height="80" rx="6" fill="#c8472b"/>
  <text x="400" y="165" font-size="15" fill="#f6f3ec" text-anchor="middle" font-weight="700">fact_sales</text>
  <text x="400" y="188" font-size="11" fill="#f6f3ec" text-anchor="middle">measures + foreign keys</text>
  <line x1="310" y1="150" x2="205" y2="80" stroke="#cabfac" stroke-width="2"/>
  <line x1="490" y1="150" x2="595" y2="80" stroke="#cabfac" stroke-width="2"/>
  <line x1="310" y1="190" x2="205" y2="260" stroke="#cabfac" stroke-width="2"/>
  <line x1="490" y1="190" x2="595" y2="260" stroke="#cabfac" stroke-width="2"/>
  <rect x="80" y="40" width="180" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="170" y="72" font-size="13" fill="#1c1a17" text-anchor="middle">dim_date</text>
  <rect x="540" y="40" width="180" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="630" y="72" font-size="13" fill="#1c1a17" text-anchor="middle">dim_customer</text>
  <rect x="80" y="248" width="180" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="170" y="280" font-size="13" fill="#1c1a17" text-anchor="middle">dim_product</text>
  <rect x="540" y="248" width="180" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="630" y="280" font-size="13" fill="#1c1a17" text-anchor="middle">dim_store</text>
  <text x="400" y="326" font-size="12" fill="#8b857a" text-anchor="middle">one hop from fact to any context — every query is the same simple join shape</text>
</svg>
</figure>

The fact table is long and narrow: one row per measurement event at a
[declared grain](/essays/fact-table-grain/), carrying numeric measures and
foreign keys. Dimensions are wide and short: descriptive attributes you filter
and group by, kept flat rather than normalized into sub-tables.

## Trade-offs

**Gains:** queries mirror business questions; every metric lives in one place;
dimensions are reusable across facts (the basis of
[conformed dimensions](/essays/conformed-dimensions/)); columnar warehouses
compress the redundancy cheaply.

**Costs:** modelling discipline up front — grain declarations,
[key management](/essays/surrogate-keys-vs-natural-keys/), and
[slowly changing dimension](/essays/slowly-changing-dimensions-explained/)
policies; ETL complexity moves into the dimension maintenance; and it fights you
on genuinely document- or graph-shaped data.

## When not to use it

Operational OLTP workloads (normalize instead), one-off exploratory analysis
(modelling is wasted ceremony), or very small teams querying one flat export —
where [one big table](/essays/one-big-table-vs-star-schema/) is honestly
sufficient until scale or team growth breaks it.
