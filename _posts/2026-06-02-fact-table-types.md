---
title: "Fact Table Types: Transaction, Periodic Snapshot, and Accumulating"
kicker: "Field Notes"
topic: "Modeling"
description: "There are three kinds of fact table, distinguished by what one row represents over time: transaction, periodic snapshot, and accumulating snapshot. Here's how each works and how to pick the right one."
date: 2026-06-02
last_modified_at: 2026-07-05
---

Most people who've built [a dimensional model](/essays/a-field-guide-to-dimensional-modeling/)
know what a fact table is — measurements at a
[declared grain](/essays/fact-table-grain/), surrounded by
dimensions in a [star schema](/essays/star-schema-vs-snowflake-schema/). Fewer know
that fact tables come in three distinct flavours, and that
choosing the wrong one quietly makes a whole class of questions awkward or
impossible to answer. The three types — transaction, periodic snapshot, and
accumulating snapshot — differ in one thing: *what a single row represents over
time.* Get that match right and the model does your analysis for you.

## Transaction fact tables

The default, and the one most people picture. **One row per event, recorded as it
happens** — a sale, a payment, a click, a login. The grain is the individual
transaction.

```
fact_sales: one row per sale
sale_id | date_key | customer_key | product_key | quantity | amount
```

Transaction facts are the workhorse. They're fully *additive* — you can sum `amount`
across any combination of dimensions and get a meaningful number — and they capture
maximum detail, which means you can roll them up almost any way you like later. The
table grows forever, one row per event, which is exactly as it should be: it's an
immutable log of things that occurred.

Reach for this whenever the question is about discrete events: how many, how much,
how often. It's the right answer most of the time.

## Periodic snapshot fact tables

Now a different shape of question: not "what happened?" but "what was the *state* of
things at regular intervals?" A periodic snapshot has **one row per entity per fixed
time period** — a daily account balance, a month-end inventory level, a weekly
subscriber count.

```
fact_account_balance_daily: one row per account per day
date_key | account_key | balance | days_overdue
```

The crucial feature is that a row exists *for every period whether or not anything
changed.* Even on a day with no transactions, the account still has a balance, and
the snapshot records it. This is what makes "average balance in March" or "inventory
on hand at each month-end" trivial — the state is captured at a regular cadence, ready
to be queried.

> A transaction fact records the events. A periodic snapshot records the *state the
> events left behind*, sampled on a clock. Different questions; you often need both.

One trap to flag: snapshot measures are usually **semi-additive** — you can average a
balance across time, but you must not *sum* it. Adding Monday's balance to Tuesday's
balance is meaningless. Snapshots add up cleanly across dimensions like account or
region, but not across the time dimension. Knowing which measures are semi-additive
is most of what keeps snapshot reporting honest.

## Accumulating snapshot fact tables

The least-used and most interesting. An accumulating snapshot has **one row per
instance of a process with a defined beginning and end**, and — unlike the other two —
*that row gets updated repeatedly* as the instance moves through its milestones.

Think of an order moving through a pipeline: placed → paid → shipped → delivered. One
row represents one order, with a date column for each stage:

```
fact_order_fulfillment: one row per order, updated as it progresses
order_key | date_placed | date_paid | date_shipped | date_delivered | days_to_ship
```

When the order is placed, the row is inserted with `date_placed` set and the rest
null. As each milestone occurs, the row is *updated* to fill in the next date and
recompute lag measures like `days_to_ship`. This is the one fact table you
deliberately revisit and mutate, because it's tracking a lifecycle rather than
logging events.

Accumulating snapshots are built for **process and pipeline analysis** — measuring
durations between stages, finding bottlenecks, seeing how many instances are stuck at
each step. Whenever you care about a multi-step workflow and the time between its
steps, this is the shape that makes those questions easy.

## How to choose

The decision is, as always, a question about the grain — *what does one row mean?*

- **An event that happened** → transaction fact. (Most cases.)
- **The state of something, captured on a regular schedule** → periodic snapshot.
- **One run of a multi-step process you track to completion** → accumulating snapshot.

And these aren't mutually exclusive. A mature model often has all three side by side:
transaction facts logging every order line, a daily periodic snapshot of inventory,
and an accumulating snapshot tracking fulfilment. Each answers questions the others
can't.

The reason this matters is the reason most modeling matters: the structure either
fits the question or fights it. A transaction table forced to answer "what was the
balance each day?" requires painful running-sum gymnastics; a snapshot makes it a
`SELECT`. Pick the fact type that matches the shape of the question, and the
analysis stops being clever and starts being obvious — which is exactly where you
want it.
