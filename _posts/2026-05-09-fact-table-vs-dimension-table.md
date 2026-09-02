---
title: "Fact Table vs Dimension Table: The Core Distinction"
kicker: "Field Notes"
topic: "Modeling"
description: "A fact table stores the measurements you analyze; a dimension table stores the context you analyze them by. The distinction every dimensional model rests on."
date: 2026-05-09
last_modified_at: 2026-08-29
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
happened (a sale, a shipment, a click) and carries two kinds of column: the numeric
**measures** you'll aggregate, and the **foreign keys** that point out to the context.

```
fact_sales
sale_id | date_key | customer_key | product_key | quantity | net_amount
--------+----------+--------------+-------------+----------+-----------
 90112  | 20260509 |     4401     |     228     |    3     |   149.97
```

`quantity` and `net_amount` are the measures: the numbers anyone will sum, average,
or count. The `_key` columns don't describe anything themselves; they're pointers to
dimension tables. Fact tables are typically **tall and skinny**: few columns, but
millions or billions of rows, one per event. They grow forever, and that's correct:
a fact table is the historical record of what occurred.

## The dimension table: the context you measure by

A dimension table is the opposite shape: **short and wide**. It holds the descriptive
attributes you filter and group by, with relatively few rows but many columns.

```
dim_product
product_key | product_name      | category     | brand     | is_active
------------+-------------------+--------------+-----------+----------
    228     | Noise-Cancel Buds | Electronics  | Acme      |   true
```

None of these columns are things you'd *sum*. They're things you'd *slice by*:
"revenue by `category`," "units by `brand`." The dimension exists to give the bare
numbers in the fact table their human meaning, turning `product_key = 228` into "Acme
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

The shape of the model matches the shape of the question: measure, sliced by
context, over a filter. That's the entire ergonomic payoff of dimensional modeling,
and it falls directly out of putting facts and dimensions in different tables. This
fact-in-the-middle, dimensions-around-it arrangement is what forms a
[star schema](/essays/star-schema-vs-snowflake-schema/).

<figure style="margin:2rem auto;text-align:center;">
<svg class="dia-mob" viewBox="0 0 400 444" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="fvd-mt fvd-md">
  <title id="fvd-mt">How fact and dimension tables work together</title>
  <desc id="fvd-md">A central fact_sales table holding measures — quantity, amount, discount — and foreign keys, attached to four dimension tables: dim_date, dim_customer, dim_product and dim_store, each holding descriptive attributes. The measures are what you aggregate; the dimension attributes are what you filter and group by. Every connection is one join from a measurement to its context.</desc>
  <rect x="40" y="30" width="320" height="80" rx="6" fill="#c8472b"/>
  <text x="200" y="57" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">fact_sales</text>
  <text x="200" y="78" font-size="11" fill="#f6f3ec" text-anchor="middle">quantity · amount · discount</text>
  <text x="200" y="97" font-size="10" fill="#f6f3ec" text-anchor="middle">+ foreign keys</text>
  <text x="200" y="128" font-size="10" fill="#a4391f" text-anchor="middle">MEASURES — the things you SUM</text>
  <text x="200" y="156" font-size="10" fill="#8b857a" text-anchor="middle">ATTRIBUTES — the things you FILTER and GROUP BY</text>
  <line x1="24" y1="170" x2="24" y2="384" stroke="#cabfac" stroke-width="2"/>
  <line x1="24" y1="193" x2="40" y2="193" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="170" width="320" height="46" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="190" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">dim_date</text>
  <text x="200" y="207" font-size="11" fill="#56514a" text-anchor="middle">day · month · quarter · holiday</text>
  <line x1="24" y1="249" x2="40" y2="249" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="226" width="320" height="46" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="246" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">dim_customer</text>
  <text x="200" y="263" font-size="11" fill="#56514a" text-anchor="middle">name · segment · region</text>
  <line x1="24" y1="305" x2="40" y2="305" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="282" width="320" height="46" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="302" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">dim_product</text>
  <text x="200" y="319" font-size="11" fill="#56514a" text-anchor="middle">sku · category · brand</text>
  <line x1="24" y1="361" x2="40" y2="361" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="338" width="320" height="46" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="358" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">dim_store</text>
  <text x="200" y="375" font-size="11" fill="#56514a" text-anchor="middle">store · city · country</text>
  <text x="200" y="412" font-size="10" fill="#8b857a" text-anchor="middle">would you SUM it? it's a measure.</text>
  <text x="200" y="430" font-size="10" fill="#8b857a" text-anchor="middle">would you GROUP BY it? it's an attribute.</text>
</svg>
<svg class="dia-desk" viewBox="0 0 800 340" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="fact-vs-dim-t fact-vs-dim-d">
  <title id="fact-vs-dim-t">How fact and dimension tables work together</title>
  <desc id="fact-vs-dim-d">A central fact_sales table holding measures — quantity, amount, discount — and foreign keys, surrounded by four dimension tables: dim_date, dim_customer, dim_product and dim_store, each holding descriptive attributes. The measures are what you aggregate; the dimension attributes are what you filter and group by. Every arrow is one join from a measurement to its context.</desc>
  <rect x="300" y="128" width="200" height="84" rx="6" fill="#c8472b"/>
  <text x="400" y="156" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">fact_sales</text>
  <text x="400" y="176" font-size="10" fill="#f6f3ec" text-anchor="middle">quantity · amount · discount</text>
  <text x="400" y="194" font-size="10" fill="#f6f3ec" text-anchor="middle">+ foreign keys</text>
  <text x="400" y="234" font-size="10" fill="#a4391f" text-anchor="middle">MEASURES — the things you SUM</text>
  <line x1="300" y1="150" x2="200" y2="92" stroke="#cabfac" stroke-width="2"/>
  <line x1="500" y1="150" x2="600" y2="92" stroke="#cabfac" stroke-width="2"/>
  <line x1="300" y1="190" x2="200" y2="248" stroke="#cabfac" stroke-width="2"/>
  <line x1="500" y1="190" x2="600" y2="248" stroke="#cabfac" stroke-width="2"/>
  <rect x="110" y="58" width="180" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="80" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">dim_date</text>
  <text x="200" y="98" font-size="11" fill="#56514a" text-anchor="middle">day · month · quarter · holiday</text>
  <rect x="510" y="58" width="180" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="600" y="80" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">dim_customer</text>
  <text x="600" y="98" font-size="11" fill="#56514a" text-anchor="middle">name · segment · region</text>
  <rect x="110" y="230" width="180" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="252" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">dim_product</text>
  <text x="200" y="270" font-size="11" fill="#56514a" text-anchor="middle">sku · category · brand</text>
  <rect x="510" y="230" width="180" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="600" y="252" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">dim_store</text>
  <text x="600" y="270" font-size="11" fill="#56514a" text-anchor="middle">store · city · country</text>
  <text x="400" y="30" font-size="11" fill="#8b857a" text-anchor="middle">ATTRIBUTES — the things you FILTER and GROUP BY</text>
  <text x="400" y="316" font-size="12" fill="#8b857a" text-anchor="middle">would you SUM it? it's a measure. would you GROUP BY it? it's an attribute.</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">Measurements in the middle, context around the outside — and every question is a measure sliced by an attribute.</figcaption>
</figure>

## Telling them apart

When you're modeling a new source and unsure whether a column belongs in a fact or a
dimension, two quick tests resolve almost every case:

- **Would you aggregate it?** If you'd `SUM`, `AVG`, or `COUNT` it (revenue, quantity,
  duration, balance), it's a **measure**, and it belongs in a fact table.
- **Would you filter or group by it?** If you'd put it in a `WHERE` or `GROUP BY` (region,
  category, status, month, customer name), it's an **attribute**, and it
  belongs in a **dimension**.

A reliable secondary tell: measures are usually numeric and additive; dimension
attributes are usually descriptive text (and the numbers that *do* live in dimensions,
like a product's list price, are ones you'd group by, not sum across rows). The
Kimball Group's own catalogue draws the line the same way and worries at the
edge case explicitly, under
[numeric values as attributes or facts](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/numeric%20-attribute-fact)
— when a number is genuinely both, the standard answer is to model it in both
places rather than to pick.

There's nuance underneath: facts come in [several
types](/essays/fact-table-types/), dimensions handle [change over
time](/essays/slowly-changing-dimensions-explained/) and get [surrogate
keys](/essays/surrogate-keys-vs-natural-keys/), but all of that sits on top of this
one split. Measurements in facts; context in dimensions. Once that distinction is
automatic, you can read, design, and reason about almost any dimensional model,
because every one of them is just a variation on the same two-part idea.
