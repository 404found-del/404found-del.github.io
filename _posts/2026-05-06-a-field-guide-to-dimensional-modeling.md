---
title: "A Field Guide to Dimensional Modeling"
kicker: "Field Notes"
topic: "Modeling"
date: 2026-05-06
description: "Facts, dimensions, and grain — the three ideas that quietly run most analytics, explained without the dogma."
---

Dimensional modeling has a reputation problem. To newcomers it sounds like a relic
— star schemas, Kimball, slowly changing dimensions, the kind of vocabulary that
suggests a beige conference room in 2004. But strip away the era and the jargon
and you're left with three ideas that quietly run most analytics on earth. They're
worth understanding properly, not as ritual but as tools.

## The first idea: measurements versus context

Look at any business question and you'll find it splits cleanly into two kinds of
thing. There are the things you **measure** — revenue, quantity, duration, a count
of clicks. And there are the things that give those measurements **context** — the
customer, the product, the store, the day.

Dimensional modeling takes this split seriously. Measurements go in **fact tables**.
Context goes in **dimension tables**. That's the whole foundation. A fact table is
a long, narrow log of events, each row a thing that happened, carrying its numbers
and a set of foreign keys. A dimension table is a wide, shorter reference of
descriptive attributes you filter and group by.

```sql
-- Fact: one row per order line, carrying measures + keys
fact_order_line (
  order_line_id   bigint,
  date_key        int,        -- → dim_date
  customer_key    int,        -- → dim_customer
  product_key     int,        -- → dim_product
  quantity        int,        -- measure
  net_amount      numeric,    -- measure
  discount_amount numeric     -- measure
)

-- Dimension: wide, descriptive, the things you slice by
dim_product (
  product_key   int,
  product_name  text,
  category      text,
  brand         text,
  is_active     boolean
)
```

Queries then become almost embarrassingly readable: *sum `net_amount` from the
fact, joined to dimensions, filtered by `category` and `date`, grouped by `brand`.*
The shape of the model matches the shape of the questions.

## The second idea: grain is everything

Before you write a single column, you answer one question: **what does one row of
this fact table represent?** This is the *grain*, and getting it wrong is the most
common — and most expensive — modeling mistake there is.

> Declare the grain in a single sentence, in plain language, before anything else.
> "One row per order line." "One row per shipment." "One row per daily account
> balance." If you can't say it cleanly, you don't understand the fact yet.

Grain discipline prevents the classic disaster: mixing levels of detail in one
table so that a naïve `SUM()` double-counts. If some rows are per-order and others
are per-line, every aggregate is silently wrong, and no amount of dashboard
polish will save you. Pick the finest grain you can afford — you can always roll
*up* from detail, but you can never recover detail you didn't keep.

## The third idea: dimensions change, and you must decide how

Customers move cities. Products get recategorised. A store changes region. The
question is: when an attribute changes, do you want history to reflect the new
value, or preserve the old one? This is the entire content of **slowly changing
dimensions**, and it's less arcane than it sounds. In practice you mostly choose
between two behaviours:

- **Overwrite (Type 1).** Keep only the current value. Simple. You lose history —
  last year's sales will appear under the customer's *current* city, not where
  they lived at the time.
- **Add a new row (Type 2).** Keep a full history by inserting a new version of the
  dimension row, with validity dates and a current-flag. Now a fact joins to the
  version that was true *when the fact happened*. History stays honest.

The right choice is a business question disguised as a technical one. "Do we want
to attribute this customer's old orders to their old segment or their new one?"
The model can't answer that. The business has to.

## When *not* to reach for it

Dimensional modeling is a hammer, and not everything is a nail. It earns its keep
when many people query the same data for analytics and you value consistency,
readability, and predictable performance. It's a poor fit for a few cases worth
naming:

- **Operational, transactional workloads** where you're reading and writing single
  records at high frequency — that's what normalised OLTP schemas are for.
- **Exploratory, one-off analysis** on data nobody will touch again — modeling it
  is wasted ceremony.
- **Genuinely document-shaped or graph-shaped data**, where forcing a star schema
  fights the grain of the problem.

The skill isn't applying the pattern everywhere. It's recognising the shape of the
question and reaching for the model that fits it.

## The quiet payoff

When a dimensional model is done well, something subtle happens: people stop
arguing about numbers. The grain is declared, the measures live in one place, the
dimensions mean one thing, and "revenue by category last quarter" returns the same
answer no matter who asks. That consistency is the real product. The star schema is
just the machinery that delivers it — old, unglamorous, and still quietly
indispensable.
