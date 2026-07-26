---
title: "Factless Fact Tables, Explained"
kicker: "Field Notes"
topic: "Modeling"
description: "A factless fact table records that an event happened, or could have, without any numeric measure. Why a fact table with no facts is useful, and the two types."
date: 2026-05-25
last_modified_at: 2026-07-26
faq:
  - q: "What is a factless fact table?"
    a: "A fact table that records the occurrence of an event but contains no numeric measures — just the foreign keys to the dimensions involved. The 'fact' is that the combination of dimensions happened, which you analyze by counting rows rather than summing a measure."
  - q: "Why would a fact table have no facts?"
    a: "Because some events are worth tracking even though there's nothing to add up — a student attending a class, a promotion being in effect, a customer logging in. You analyze them by counting occurrences and slicing by dimensions, and the row's mere existence is the information."
  - q: "What are the two types of factless fact tables?"
    a: "Event-tracking tables, which record that something happened (attendance, logins, page views); and coverage or condition tables, which record what was possible or in effect (which products were on promotion on a given day), often used to analyze what did not happen."
---

The name sounds like a contradiction — a fact table with no facts — and that's exactly
why it trips people up. But the *factless fact table* is a genuine, useful pattern in
[dimensional modeling](/essays/a-field-guide-to-dimensional-modeling/), and once the
idea clicks it solves a class of problems that ordinary fact tables handle awkwardly.
The trick is realizing that sometimes the most important thing to record is simply
*that something happened* — no measure required.

## A fact table with no measures

Recall that an ordinary [fact table](/essays/fact-table-vs-dimension-table/) carries
numeric measures (amounts, quantities) plus the foreign keys that give them context. A
factless fact table keeps the keys and **drops the measures entirely**:

```
fact_attendance
date_key | student_key | course_key | room_key
---------+-------------+------------+---------
20260525 |    1142     |    88      |   12
```

There's nothing to sum here. The row carries no amount, no quantity — it records only
that, on this date, this student attended this course in this room. The *information is
the existence of the row itself.* You analyze it not by summing a measure but by
**counting rows** and slicing by the dimensions: how many students attended each
course, attendance by room, by day, by student segment.

> A normal fact table answers "how much?" A factless fact table answers "how many
> times did this happen?" — and sometimes, "what could have happened but didn't?" The
> count of rows is the measure.

## Type one: tracking events

The most common use is recording **events that have no natural measure**. Plenty of
things worth analyzing just... occur, with no number attached:

- A student attends a class.
- A user logs in, or views a page.
- An employee completes a training.
- A customer contacts support (the *fact* of contact, separate from any ticket
  measures).

Each is a meaningful event you'll want to count and slice — logins per day by user
segment, page views by product by week — but none has an amount to record. Forcing a
fake measure (a column of all `1`s) is the clumsy workaround; the clean model is a
factless fact table whose rows you simply `COUNT`. The dimensions provide all the
analytical richness; the fact is the event's occurrence.

## Type two: coverage, and the things that *didn't* happen

The second, subtler type records **what was possible or in effect** rather than what
happened — often precisely so you can analyze the *absence* of an event. This is called
a coverage table.

The classic example is promotions. Suppose you want to know which products were *on
promotion but sold nothing* — a genuinely important question, and an impossible one to
answer from a sales fact alone, because if there were no sales, there are no rows to
find. The promotion left no trace in the sales fact.

A factless coverage table fixes this by recording the promotion *coverage* itself —
one row per product per day that a promotion was in effect, regardless of whether
anything sold:

```
fact_promotion_coverage
date_key | product_key | promotion_key | store_key
```

Now the question is answerable: take the products covered by a promotion (from the
coverage table) and subtract the products that actually sold (from the sales fact).
What's left is "promoted but didn't sell." The factless table supplies the universe of
*what could have happened*, against which you measure what did. Analyzing
non-events — the dog that didn't bark — almost always needs a coverage table, because
non-events by definition leave no rows in an ordinary fact.

## When to reach for one

Two signals tell you a factless fact table is the right tool:

- **You're tracking an event with no measure** and find yourself wanting to invent a
  dummy `1` column just to have something to count. Drop the dummy; make it factless
  and count rows.
- **You need to analyze what *didn't* happen** — coverage, eligibility, "in effect but
  unused." Record the universe of possibilities in a coverage table so the absence
  becomes measurable.

Everything else about it is normal dimensional modeling — it sits in a
[star](/essays/star-schema-vs-snowflake-schema/), it shares
[conformed dimensions](/essays/conformed-dimensions/), it's just another
[type of fact table](/essays/fact-table-types/) in the toolkit. The only mental hurdle
is the name. Once you accept that the existence of a row can itself be the fact, the
factless fact table stops sounding like a paradox and starts looking like the obvious
answer to "how do I model an event that has nothing to add up?"
