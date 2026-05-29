---
title: "Star Schema vs Snowflake Schema: Which to Use and When"
kicker: "Field Notes"
topic: "Modeling"
description: "Star schema vs snowflake schema comes down to one decision — whether to normalize your dimensions. Here's the trade-off, and why the star usually wins in a modern warehouse."
date: 2026-05-12
---

The difference between a star schema and a snowflake schema is smaller than the
debate around it suggests. Both are dimensional models — facts in the middle,
dimensions around them. The entire distinction is one decision: *do you normalize
your dimension tables, or not?* Everything else follows from that single choice.
Let's make it properly.

## The one real difference

In a **star schema**, each dimension is a single, flat, denormalized table. The
product dimension holds the product, its category, its brand, its supplier — all
in one wide table, even though category and brand repeat across many rows.

In a **snowflake schema**, you normalize those dimensions into a hierarchy. Product
points to a separate category table, which points to a department table; brand
lives in its own table; supplier in another. The single dimension "snowflakes" out
into a branching structure of smaller related tables — which is where the name
comes from.

That's it. Star is denormalized dimensions; snowflake is normalized dimensions. If
you understand [why dimensional models split measurements from
context](/essays/a-field-guide-to-dimensional-modeling/), you already understand
both — snowflaking is just normalization applied to the context tables.

## What snowflaking buys you

Normalizing dimensions isn't crazy; it has genuine, if narrow, advantages.

- **Less storage and less redundancy.** "Electronics" is stored once in a category
  table instead of repeated on ten thousand product rows. On very large dimensions
  this saves space.
- **Cleaner updates to shared attributes.** Rename a category in one row rather than
  in every product that shares it. Fewer places for an update to go wrong.
- **It mirrors how the source system already thinks.** OLTP databases are normalized,
  so a snowflake can feel like a more faithful translation of the upstream model.

These were compelling reasons in 1998, when storage was expensive and warehouses
ran on row-based engines that struggled with wide tables. They are much weaker
reasons today.

## What it costs you

The costs of snowflaking land squarely on the two things analytics cares about
most: query simplicity and performance.

> Every level of normalization is another join the analyst must write and the
> engine must execute. A question that's one join away in a star ("sales by
> category") becomes a three-table traversal in a snowflake.

**Queries get more complex.** Analysts now have to know the shape of the hierarchy
and join through it correctly. More joins mean more chances to get a query subtly
wrong — and more friction for every person who touches the data.

**Performance often degrades, not improves.** This surprises people. The intuition
is that smaller tables are faster, but modern columnar warehouses (BigQuery,
Snowflake the product, Redshift, Databricks) are built to scan wide denormalized
tables efficiently and to compress repeated values away to almost nothing. The
storage you save by snowflaking is marginal, while the extra joins you add are
real work at query time. The denormalized star is usually the *faster* design on
exactly the engines most teams run today.

**Maintenance gets heavier.** More tables, more relationships, more pipeline steps
to keep in sync. The "cleaner" model is often more brittle in practice.

## The practical verdict

For analytics on a columnar cloud warehouse — which is most analytics now — **default
to the star schema.** Denormalize your dimensions. The storage cost is negligible,
the query experience is dramatically simpler, and performance is typically better.
Optimizing for storage by normalizing is solving a 1998 problem with a 2026 bill.

Reach for snowflaking only in specific cases:

- A dimension is **genuinely enormous** (tens of millions of rows) *and* a shared
  attribute is large and highly repetitive, so the storage saving is material.
- You have a **rapidly changing shared attribute** where updating it in one
  normalized place meaningfully reduces error or cost.
- A **compliance or governance** requirement forces a single authoritative table
  for a particular entity.

Even then, snowflake only the dimension that needs it. Mixing is fine — a mostly-star
model with one normalized dimension is a perfectly reasonable, pragmatic design. You
don't owe the schema purity.

## The thing underneath the choice

Notice that "star vs snowflake" is really a proxy for an older question:
**normalize for write-efficiency, or denormalize for read-efficiency?** A warehouse
is overwhelmingly read-heavy — written by a handful of pipelines, queried by
everyone. So it should optimize for reads, which means denormalizing, which means
the star. The snowflake optimizes for the case a warehouse rarely faces.

Pick the star by default. Snowflake a dimension only when you can name the specific
problem it solves. And don't lose an afternoon to the debate — it was only ever one
decision wearing two names.
