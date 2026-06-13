---
title: "Fact Table vs Dimension Table: The Core Distinction"
kicker: "Field Notes"
topic: "Modeling"
description: "A fact table stores the measurements — the numbers you analyze. A dimension table stores the context you analyze them by. Here's the distinction every dimensional model is built on, and how to tell which is which."
date: 2026-05-09
faq:
  - q: "What is the difference between a fact table and a dimension table?"
    a: "A fact table stores measurements — the numeric events you analyze, like sales amounts or quantities — at a defined grain, along with foreign keys. A dimension table stores descriptive context you filter and group by, like customer, product, or date. Facts are what you measure; dimensions are how you slice those measurements."
  - q: "Can a table be both a fact and a dimension?"
    a: "Rarely as the same table, but a fact table can act as a dimension for a higher-grain fact — a pattern sometimes called a fact-dimension. In most models the roles stay distinct: keep measurements in facts and descriptive attributes in dimensions."
  - q: "How do I know if something is a fact or a dimension?"
    a: "Ask whether you sum or average it, or filter and group by it. Things you aggregate (revenue, quantity, duration) are facts. Things you slice by (region, category, month, customer) are dimensions. A useful tell: facts are usually numeric and additive; dimensions are usually descriptive text."
---

If you read just one idea out of [dimensional
modeling](/essays/a-field-guide-to-dimensional-modeling/), make it this one, because
everything else is built on top of it: data splits cleanly into the things you
**measure** and the things that give those measurements **context**. Measurements go
in *fact tables*. Context goes in *dimension tables*. Get this distinction firmly in
hand and the rest of dimensional modeling stops being a vocabulary test and starts
being obvious.

## The fact table: what you measure

A fact table is a long, narrow log of measurements. Each row records something that
happened — a sale, a shipment, a click — and carries two kinds of column: the numeric
**measures** you'll aggregate, and the **foreign keys** that point out to the context.

```
fact_sales
sale_id | date_key | customer_key | product_key | quantity | net_amount
--------+----------+--------------+-------------+----------+-----------
 90112  | 20260509 |     4401     |     228     |    3     |   149.97
```

`quantity` and `net_amount` are the measures — the numbers anyone will sum, average,
or count. The `_key` columns don't describe anything themselves; they're pointers to
dimension tables. Fact tables are typically **tall and skinny**: few columns, but
millions or billions of rows, one per event. They grow forever, and that's correct —
a fact table is the historical record of what occurred.

## The dimension table: the context you measure by

A dimension table is the opposite shape — **short and wide**. It holds the descriptive
attributes you filter and group by, with relatively few rows but many columns.

```
dim_product
product_key | product_name      | category     | brand     | is_active
------------+-------------------+--------------+-----------+----------
    228     | Noise-Cancel Buds | Electronics  | Acme      |   true
```

None of these columns are things you'd *sum*. They're things you'd *slice by*:
"revenue by `category`," "units by `brand`." The dimension exists to give the bare
numbers in the fact table their human meaning — to turn `product_key = 228` into "Acme
noise-cancelling earbuds in Electronics."

> A fact answers *how much* and *how many*. A dimension answers *who, what, where,
> when, and which*. Facts are the verbs of your data; dimensions are the adjectives.

## How they work together

The point of the split is the query. Because measures live in the fact and context
lives in dimensions, an analytical question becomes a simple, readable join: take the
measure from the fact, join out to the dimensions, filter and group by their
attributes.

```sql
SELECT p.category, SUM(f.net_amount) AS revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_date d    ON f.date_key = d.date_key
WHERE d.year = 2026
GROUP BY p.category;
```

The shape of the model matches the shape of the question — measure, sliced by
context, over a filter. That's the entire ergonomic payoff of dimensional modeling,
and it falls directly out of putting facts and dimensions in different tables. This
fact-in-the-middle, dimensions-around-it arrangement is what forms a
[star schema](/essays/star-schema-vs-snowflake-schema/).

## Telling them apart

When you're modeling a new source and unsure whether a column belongs in a fact or a
dimension, two quick tests resolve almost every case:

- **Would you aggregate it?** If you'd `SUM`, `AVG`, or `COUNT` it — revenue, quantity,
  duration, balance — it's a **measure**, and it belongs in a fact table.
- **Would you filter or group by it?** If you'd put it in a `WHERE` or `GROUP BY` —
  region, category, status, month, customer name — it's an **attribute**, and it
  belongs in a **dimension**.

A reliable secondary tell: measures are usually numeric and additive; dimension
attributes are usually descriptive text (and the numbers that *do* live in dimensions,
like a product's list price, are ones you'd group by, not sum across rows).

There's nuance underneath — facts come in [several
types](/essays/fact-table-types/), dimensions handle [change over
time](/essays/slowly-changing-dimensions-explained/) and get [surrogate
keys](/essays/surrogate-keys-vs-natural-keys/) — but all of that sits on top of this
one split. Measurements in facts; context in dimensions. Once that distinction is
automatic, you can read, design, and reason about almost any dimensional model,
because every one of them is just a variation on the same two-part idea.
