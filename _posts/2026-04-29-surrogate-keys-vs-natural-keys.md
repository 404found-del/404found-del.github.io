---
title: "Surrogate Keys vs Natural Keys: A Practical Rule"
kicker: "Field Notes"
topic: "Modeling"
description: "Surrogate key vs natural key is a decision every data model faces. The practical rule: surrogate keys for dimensions, natural key kept as an attribute."
date: 2026-04-29
last_modified_at: 2026-07-26
faq:
  - q: "What is the difference between a surrogate key and a natural key?"
    a: "A natural key comes from the business itself — an email, SKU, or account number. A surrogate key is a meaningless, system-generated identifier the warehouse assigns. The practical rule: use surrogates as dimension primary keys, and keep the natural key as an ordinary attribute for matching back to source systems."
  - q: "Why not just use natural keys as primary keys?"
    a: "Because source systems recycle them, reformat them, and duplicate them across systems — and because a natural key can only ever identify one version of an entity. A Type 2 slowly changing dimension needs multiple rows for the same customer, each with its own key, which only a surrogate can provide."
  - q: "Are surrogate keys still needed in modern cloud warehouses?"
    a: "Yes, wherever dimensional history matters. Cheap compute didn't change the logical problem: source keys aren't stable and can't version history. Hash-based surrogates have joined sequence numbers as a common implementation, but the role of the surrogate is unchanged."
---

Every table needs a way to identify a row, and you have two choices for what that
identifier is. A **natural key** is a value that already means something in the
business — an email address, a product SKU, an order number from the source system.
A **surrogate key** is a meaningless integer or UUID that you mint yourself,
existing only to identify the row. The surrogate-vs-natural question comes up in
every data model, and most of the confusion around it dissolves once you separate
two jobs a key is being asked to do.

## Two jobs, often confused

A key is doing identity work: *which row is this?* But a natural key is also doing
business work: it *carries meaning*. The trouble starts when you let one value do
both, because the requirements pull in opposite directions.

Identity wants the key to be **stable, compact, and never-changing** — because every
relationship in your model depends on it. Business meaning, by contrast, is
**mutable**: a customer changes their email, a product gets re-SKU'd in a system
migration, an "order number" turns out not to be unique across two merged regions.
The moment a value that means something also serves as your identifier, every
business change becomes a structural earthquake.

> A natural key promises to be unique and permanent. The business almost never
> keeps that promise.

## The rule for dimensional models

If you're building [a dimensional model](/essays/a-field-guide-to-dimensional-modeling/),
the rule is clear and nearly unconditional: **give every dimension a surrogate
primary key, and keep the natural key as a regular attribute.**

```sql
dim_customer (
  customer_key   bigint,      -- surrogate PK: meaningless, stable, yours
  customer_id    text,        -- natural key from the source, kept as an attribute
  email          text,
  segment        text,
  valid_from     date,
  valid_to       date,
  is_current     boolean
)
```

Your [fact tables](/glossary/fact-table/) then carry `customer_key`, not `customer_id`. This buys you several
things that are hard to get any other way.

**[Slowly changing dimensions](/glossary/slowly-changing-dimension/) become possible.** To keep history with [SCD Type
2](/essays/a-field-guide-to-dimensional-modeling/), you insert a *new row* each time
a customer's attributes change — same `customer_id`, new `customer_key`. The
surrogate key is what lets two versions of "the same" customer coexist as distinct
rows that facts can point to correctly. With a natural key as your PK, you simply
cannot represent this.

**You're insulated from source chaos.** The source system changes its ID scheme,
two systems merge with colliding IDs, an upstream "unique" identifier turns out not
to be — none of it touches your fact tables, because they reference your surrogate,
not the source's value. Your model has its own stable spine.

**Joins are faster and smaller.** A 64-bit integer key joins and indexes more
cheaply than a long composite natural key like `(region_code, order_number,
line_no)`. On large facts this is a real, measurable win.

## When a natural key is fine

The surrogate rule isn't dogma. Natural keys are perfectly acceptable in a few
situations:

- **Stable reference data** where the key is genuinely immutable and standardized —
  ISO country codes, currency codes, a calendar's date key (`20260429`). These
  won't change and carry no SCD requirement, so a surrogate adds ceremony for
  nothing.
- **Staging and raw layers**, where you're faithfully mirroring the source and
  *want* its native keys for reconciliation and debugging.
- **Quick, throwaway analysis** that no one will build on.

The pattern to avoid is the opposite extreme — surrogate keys *everywhere*, including
on tiny static lookups, purely out of habit. Use the surrogate where it earns its
keep: dimensions that change, that come from messy sources, or that sit on the hot
path of large joins.

## Keep the natural key — always

One mistake worth calling out: adopting a surrogate key and then *discarding* the
natural key. Don't. The natural key is how you trace a row back to its source, how
you reconcile counts against the originating system, and how you debug when a
pipeline does something strange. The surrogate is for the machine; the natural key
is for the humans and the audits. Keep both — surrogate as the primary key, natural
key as a first-class attribute beside it.

That's the whole practical rule. Mint a meaningless, stable identifier for identity.
Keep the meaningful one for traceability. Let each value do the one job it's
actually good at, and stop asking a business value to be a permanent address it was
never going to be.
