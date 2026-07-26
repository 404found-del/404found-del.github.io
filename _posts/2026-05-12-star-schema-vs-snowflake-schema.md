---
title: "Star Schema vs Snowflake Schema: Which to Use and When"
kicker: "Field Notes"
topic: "Modeling"
description: "Star schema vs snowflake schema comes down to one decision — whether you normalize your dimensions. Here's the difference, a worked example, a diagram, and why the star usually wins on a modern warehouse."
date: 2026-05-12
last_modified_at: 2026-07-26
faq:
  - q: "What is the difference between a star schema and a snowflake schema?"
    a: "A star schema keeps each dimension in a single flat, denormalized table. A snowflake schema normalizes those dimensions into multiple related sub-tables. That one choice — denormalized versus normalized dimensions — is the entire distinction; the fact table is the same in both."
  - q: "Which is faster, star schema or snowflake schema?"
    a: "On modern columnar warehouses, usually the star. Denormalized dimensions mean fewer joins at query time, and columnar compression shrinks the repeated values that normalization was meant to eliminate, so the snowflake's storage saving rarely outweighs its extra join cost."
  - q: "When should you use a snowflake schema?"
    a: "When a dimension is genuinely enormous and a shared attribute is large and highly repetitive, when a rapidly changing shared attribute is cheaper to update in one normalized place, or when a compliance rule forces a single authoritative table. Even then, snowflake only the dimension that needs it."
  - q: "Is the snowflake schema related to the Snowflake data warehouse?"
    a: "No. The schema pattern is decades older than the vendor and unrelated to it — you can build star or snowflake schemas on any warehouse, including Snowflake, BigQuery, or Redshift."
---

The difference between a star schema and a snowflake schema is smaller than the
debate around it suggests. Both are dimensional models — a central
[fact table surrounded by dimensions](/essays/fact-table-vs-dimension-table/) — and the *entire* distinction is one decision: **do you
keep each dimension in a single flat table (star), or normalize it into related
sub-tables (snowflake)?** For analytics on a modern cloud warehouse, the star is
almost always the better default. Here's why, with a worked example and a diagram.

## Star vs snowflake, at a glance

| | Star schema | Snowflake schema |
|---|---|---|
| **Dimensions** | Denormalized — one flat table each | Normalized into sub-tables |
| **Joins per query** | Fewer (fact → dimension) | More (fact → dimension → sub-tables) |
| **Query simplicity** | High — easy to read and write | Lower — must traverse the hierarchy |
| **Storage** | Slightly more (repeated values) | Slightly less (values stored once) |
| **Query speed (columnar)** | Usually faster | Usually slower |
| **Maintenance** | Simpler | More tables to keep in sync |
| **Best for** | Most analytics on cloud warehouses | Very large or compliance-bound dimensions |

## The one real difference

In a **star schema**, each dimension is a single, wide, denormalized table — the
product dimension holds the product, its category, its brand, and its supplier all in
one place, even though "Electronics" repeats across many rows. In a **snowflake
schema**, you normalize that dimension into a branching hierarchy: product points to a
separate category table, which points to a department table, and so on. The single
dimension "snowflakes" out into smaller related tables, which is where the name comes
from.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 360" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="star-schema-vs-snowflake-schema-t star-schema-vs-snowflake-schema-d">
  <title id="star-schema-vs-snowflake-schema-t">Star schema versus snowflake schema</title>
  <desc id="star-schema-vs-snowflake-schema-d">Two layouts side by side. In the star, dimension tables attach directly to the central fact table, one hop away. In the snowflake, the product dimension is normalized into further sub-tables, adding hops.</desc>
  <text x="195" y="28" text-anchor="middle" font-size="15" fill="#c8472b" font-weight="600" letter-spacing="2">STAR</text>
  <text x="600" y="28" text-anchor="middle" font-size="15" fill="#c8472b" font-weight="600" letter-spacing="2">SNOWFLAKE</text>
  <line x1="400" y1="44" x2="400" y2="340" stroke="#ddd6c8" stroke-width="1" stroke-dasharray="4 5"/>
  <!-- STAR lines -->
  <g stroke="#cabfac" stroke-width="1.5">
    <line x1="195" y1="190" x2="195" y2="108"/>
    <line x1="195" y1="190" x2="195" y2="272"/>
    <line x1="195" y1="190" x2="95" y2="190"/>
    <line x1="195" y1="190" x2="295" y2="190"/>
  </g>
  <!-- STAR boxes -->
  <g font-size="12" fill="#1c1a17">
    <rect x="150" y="168" width="90" height="44" rx="4" fill="#fdfcf9" stroke="#c8472b" stroke-width="2"/><text x="195" y="194" text-anchor="middle" font-weight="600">fact_sales</text>
    <rect x="150" y="74" width="90" height="34" rx="4" fill="#fdfcf9" stroke="#cabfac"/><text x="195" y="95" text-anchor="middle">dim_date</text>
    <rect x="150" y="272" width="90" height="34" rx="4" fill="#fdfcf9" stroke="#cabfac"/><text x="195" y="293" text-anchor="middle">dim_store</text>
    <rect x="20" y="172" width="92" height="36" rx="4" fill="#fdfcf9" stroke="#cabfac"/><text x="66" y="194" text-anchor="middle">dim_customer</text>
    <rect x="280" y="172" width="92" height="36" rx="4" fill="#fdfcf9" stroke="#cabfac"/><text x="326" y="194" text-anchor="middle">dim_product</text>
  </g>
  <!-- SNOWFLAKE lines -->
  <g stroke="#cabfac" stroke-width="1.5">
    <line x1="600" y1="190" x2="600" y2="108"/>
    <line x1="600" y1="190" x2="600" y2="272"/>
    <line x1="600" y1="190" x2="510" y2="190"/>
    <line x1="600" y1="190" x2="690" y2="190"/>
    <line x1="736" y1="174" x2="770" y2="128"/>
    <line x1="736" y1="194" x2="772" y2="250"/>
  </g>
  <!-- SNOWFLAKE boxes -->
  <g font-size="12" fill="#1c1a17">
    <rect x="555" y="168" width="90" height="44" rx="4" fill="#fdfcf9" stroke="#c8472b" stroke-width="2"/><text x="600" y="194" text-anchor="middle" font-weight="600">fact_sales</text>
    <rect x="555" y="74" width="90" height="34" rx="4" fill="#fdfcf9" stroke="#cabfac"/><text x="600" y="95" text-anchor="middle">dim_date</text>
    <rect x="555" y="272" width="90" height="34" rx="4" fill="#fdfcf9" stroke="#cabfac"/><text x="600" y="293" text-anchor="middle">dim_store</text>
    <rect x="418" y="172" width="92" height="36" rx="4" fill="#fdfcf9" stroke="#cabfac"/><text x="464" y="194" text-anchor="middle">dim_customer</text>
    <rect x="690" y="172" width="92" height="36" rx="4" fill="#fdfcf9" stroke="#cabfac"/><text x="736" y="194" text-anchor="middle">dim_product</text>
    <rect x="730" y="104" width="68" height="30" rx="4" fill="#f0ece2" stroke="#cabfac"/><text x="764" y="123" text-anchor="middle" font-size="10.5">category</text>
    <rect x="732" y="238" width="62" height="30" rx="4" fill="#f0ece2" stroke="#cabfac"/><text x="763" y="257" text-anchor="middle" font-size="10.5">brand</text>
  </g>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#8b857a;margin-top:0.5rem;">In a star, dimensions sit directly on the fact. In a snowflake, a dimension (here, product) is normalized into further sub-tables.</figcaption>
</figure>

If you understand [why dimensional models split measurements from
context](/essays/a-field-guide-to-dimensional-modeling/), you already understand both —
snowflaking is just [normalization](/essays/normalization-vs-denormalization/) applied
to the [dimension tables](/glossary/dimension-table/).

## A worked example

Say you want sales by product category. In a **star**, `category` lives right on the
product dimension, so it's one join:

```sql
-- STAR: one join, category is on the dimension
SELECT p.category, SUM(f.net_amount) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category;
```

In a **snowflake**, `category` has been normalized into its own table, so the same
question now traverses the hierarchy:

```sql
-- SNOWFLAKE: an extra hop to reach category
SELECT c.category, SUM(f.net_amount) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_category c ON p.category_key = c.category_key
GROUP BY c.category;
```

Every level of normalization is another join the analyst must write and the engine
must execute. Multiply that across a real schema and the snowflake's "tidiness"
becomes a steady tax on every query.

## When to use a star schema

For analytics on a columnar cloud warehouse — which is most analytics today —
**default to the star.** Denormalize your dimensions. The storage cost is negligible
because columnar engines compress repeated values away to almost nothing, queries are
dramatically simpler, and performance is typically *better* than the snowflake, not
worse. Optimizing for storage by normalizing is solving a 1998 problem with a 2026
bill.

## When to use a snowflake schema

Reach for snowflaking only in specific cases, and even then only for the dimension
that needs it:

- A dimension is **genuinely enormous** (tens of millions of rows) *and* a shared
  attribute is large and highly repetitive, so the storage saving is material.
- A **rapidly changing shared attribute** is meaningfully cheaper and safer to update
  in one normalized place.
- A **compliance or governance** rule forces a single authoritative table for an
  entity.

Mixing is fine — a mostly-star model with one snowflaked dimension is a perfectly
reasonable, pragmatic design. You don't owe the schema purity.

## The thing underneath the choice

"Star vs snowflake" is really a proxy for an older question: normalize for
write-efficiency, or denormalize for read-efficiency? A warehouse is overwhelmingly
read-heavy — written by a few pipelines, queried by everyone — so it should optimize
for reads, which means denormalizing, which means the star. (If you want the deeper
version of that trade-off, see [normalization vs
denormalization](/essays/normalization-vs-denormalization/); if you want the even more
aggressive end of denormalization, see [one big table vs the star
schema](/essays/one-big-table-vs-star-schema/).)

Worth noting that this isn't a contested reading: the Kimball Group's own
technique catalogue treats
[denormalized flattened dimensions](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/denormalized-flattened-dimension)
as the default and files
[snowflaked dimensions](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/snowflake-dimension)
as the exception you justify.

Pick the star by default. Snowflake a dimension only when you can name the specific
problem it solves. And don't lose an afternoon to the debate — it was only ever one
decision wearing two names.
