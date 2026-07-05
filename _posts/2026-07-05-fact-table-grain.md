---
title: "The Grain of a Fact Table: The First Decision That Decides Everything Else"
kicker: "Field Notes"
topic: "Modeling"
description: "The grain is the business definition of what one fact table row represents. Declare it first — every dimension, measure, and bug traces back to it."
date: 2026-07-05 10:30:00 +0530
faq:
  - q: "What is the grain of a fact table?"
    a: "The grain is the precise business definition of what a single row in the fact table represents — for example, 'one row per order line' or 'one row per account per month.' It's declared in business terms, before choosing dimensions or measures, and every element of the table must honor it."
  - q: "How do I choose the right grain?"
    a: "Start at the most atomic grain the source system produces — the individual measurement event, like an order line or a sensor reading. Atomic grain answers unpredictable questions and can always be aggregated up; a coarser grain can never be drilled back down. Only pre-aggregate as a deliberate performance layer on top."
  - q: "Can one fact table have two grains?"
    a: "No — mixing grains in one table is the classic dimensional modeling bug. If a business process produces measurements at two grains (order lines and order-level shipping fees, say), either allocate the coarser fact down to the fine grain or build two fact tables. Never store both grains in the same table."
  - q: "What's the difference between grain and granularity?"
    a: "In dimensional modeling they're used interchangeably, but 'grain' is the Kimball term of art for the declared meaning of one row. 'Granularity' more loosely describes how detailed data is. The discipline lies in the declaration: writing the grain down as a sentence and rejecting anything that violates it."
---

The **grain** of a fact table is the business definition of what exactly one row
represents. Not the list of columns — a sentence: *one row per order line*, *one row
per account per month*, *one row per boarding-pass scan*. Declaring that sentence is
the first design decision in dimensional modeling, made before you pick a single
dimension or measure, because it is the test every later choice must pass. A
dimension belongs in the table only if it's single-valued at that grain; a measure
belongs only if it's true at that grain. Skip the declaration and both mistakes walk
in unnoticed — which is why nearly every double-counting bug in a warehouse traces
back to a grain violation.

Kimball's design method makes this order explicit: choose the business process,
**declare the grain**, then — and only then — choose
[dimensions and facts](/essays/fact-table-vs-dimension-table/). The grain sits second
because everything downstream inherits from it.

## Atomic grain first, always

The safest declaration is the most **atomic** one — the finest level of detail the
source's measurement event actually produces. For a retail order that's the order
*line*, not the order; for web traffic, the page view, not the session.

| | Atomic grain (order line) | Coarse grain (order) |
|---|---|---|
| **"Sales by product?"** | Yes — product is a line attribute | Impossible — products vary within an order |
| **Unanticipated questions** | Survives them | Fails the first new one |
| **Roll up / drill down** | Aggregates up freely | Can never drill back down |
| **Row volume** | Larger | Smaller |
| **Right role** | The foundation fact table | A derived aggregate on top |

The asymmetry is the whole argument: atomic data can always become coarse, coarse
data can never become atomic again. If query cost hurts, add an aggregate table (or
let a [semantic layer](/essays/what-is-a-semantic-layer/) manage one) — as a *second*
table with its own declared grain, not a compromise in the first.

## The classic bug: two grains in one table

Here's how the mistake usually arrives. Orders have lines (product, quantity, price)
— but the source also carries an order-level shipping fee. Someone helpfully adds
`shipping_fee` to the line-grain table, repeated on every line:

```sql
-- Grain: one row per order line ... except one column isn't
SELECT
  order_id, product_key, quantity,
  line_amount,     -- true at line grain ✓
  shipping_fee     -- true at ORDER grain ✗ (repeated on every line)
FROM fact_order_line;

-- The inevitable report, quietly wrong:
SELECT sum(line_amount) AS revenue,
       sum(shipping_fee) AS shipping   -- 3-line orders count fees 3x
FROM fact_order_line;
```

The fix is never "remember not to sum that column." It's one of two structural moves:

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 360" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
  <rect x="250" y="16" width="300" height="52" rx="6" fill="#c8472b"/>
  <text x="400" y="41" font-size="14" fill="#f6f3ec" text-anchor="middle">order-level fact arrives</text>
  <text x="400" y="59" font-size="12" fill="#f6f3ec" text-anchor="middle">(shipping fee, at the wrong grain)</text>
  <line x1="310" y1="68" x2="200" y2="120" stroke="#cabfac" stroke-width="2"/>
  <line x1="490" y1="68" x2="600" y2="120" stroke="#cabfac" stroke-width="2"/>
  <rect x="60" y="120" width="280" height="88" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="148" font-size="14" fill="#1c1a17" text-anchor="middle" font-weight="700">Fix 1 — allocate down</text>
  <text x="200" y="172" font-size="12" fill="#1c1a17" text-anchor="middle">split the fee across lines</text>
  <text x="200" y="192" font-size="12" fill="#1c1a17" text-anchor="middle">table stays at line grain</text>
  <rect x="460" y="120" width="280" height="88" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="600" y="148" font-size="14" fill="#1c1a17" text-anchor="middle" font-weight="700">Fix 2 — second fact table</text>
  <text x="600" y="172" font-size="12" fill="#1c1a17" text-anchor="middle">fact_order, one row per order</text>
  <text x="600" y="192" font-size="12" fill="#1c1a17" text-anchor="middle">its own declared grain</text>
  <line x1="200" y1="208" x2="200" y2="252" stroke="#ddd6c8" stroke-width="2"/>
  <line x1="600" y1="208" x2="600" y2="252" stroke="#ddd6c8" stroke-width="2"/>
  <rect x="60" y="252" width="280" height="52" rx="6" fill="#1c1a17"/>
  <text x="200" y="283" font-size="13" fill="#f6f3ec" text-anchor="middle">sums are safe at every grain</text>
  <rect x="460" y="252" width="280" height="52" rx="6" fill="#1c1a17"/>
  <text x="600" y="283" font-size="13" fill="#f6f3ec" text-anchor="middle">each table sums correctly alone</text>
  <text x="400" y="340" font-size="12" fill="#8a7f6d" text-anchor="middle">what never works: storing both grains in one table and hoping analysts remember</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8a7f6d;margin-top:0.6rem;">Two honest fixes for a fact at the wrong grain — allocation, or a separate fact table.</figcaption>
</figure>

```sql
-- Fix 1: allocate the order fact down to line grain
shipping_fee * line_amount / sum(line_amount) OVER (PARTITION BY order_id)
  AS allocated_shipping_fee
```

Allocation keeps one table and makes every column summable; a second fact table keeps
each measurement honest at its natural grain. Both work. Hoping people remember
doesn't.

## Grain declares the fact table's type

Say the grain sentence out loud and you've usually also named which of the
[three fact table types](/essays/fact-table-types/) you're building: *one row per
event* is a transaction fact, *one row per thing per period* is a periodic snapshot,
*one row per process lifecycle* is an accumulating snapshot. Even
[factless fact tables](/essays/factless-fact-tables/) — rows with no measures at all —
still have a perfectly crisp grain; the row itself is the fact.

The grain also disciplines dimensions. Ask of each candidate: *is it single-valued at
this grain?* Product is single-valued per order line but multivalued per order — so a
line grain earns the product dimension and an order grain forfeits it. That one test,
applied ruthlessly, is most of what separates a
[star schema that holds up](/essays/a-field-guide-to-dimensional-modeling/) from a
[wide table that slowly stops being true](/essays/one-big-table-vs-star-schema/).

Declare the grain in one sentence. Write it at the top of the model file. Reject
anything that violates it. It is the cheapest correctness guarantee in all of data
architecture.
