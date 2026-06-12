---
title: "Slowly Changing Dimensions, Explained Without the Jargon"
kicker: "Field Notes"
topic: "Modeling"
description: "Slowly changing dimensions answer one question: when a dimension attribute changes, do you overwrite history or preserve it? Here are SCD Types 1, 2, and 3, and exactly when to use each."
date: 2026-05-31
faq:
  - q: "What is the difference between SCD Type 1 and Type 2?"
    a: "Type 1 overwrites the old value in place, keeping no history. Type 2 expires the old row and inserts a new versioned row with validity dates, preserving full history so facts can join to the version that was true when they happened."
  - q: "Is SCD Type 2 always the best choice?"
    a: "No. Type 2 adds pipeline complexity and grows the dimension over time, so use it where history genuinely matters for analysis. Corrections and attributes where only the current value is meaningful are better served by Type 1."
  - q: "Can one dimension mix different SCD types?"
    a: "Yes — the choice is per attribute, not per table. A customer's segment can be Type 2 for historical reporting while a typo fix to their name is Type 1, inside the same dimension."
---

"Slowly changing dimensions" is an intimidating name for a simple idea. A dimension
describes context — a customer, a product, a store. Over time, that context changes:
the customer moves city, the product gets recategorised, the store switches region.
A slowly changing dimension, or SCD, is just a *strategy for what happens to history
when one of those attributes changes.* That's the entire concept. The types — 1, 2,
3 — are only different answers to one question: do you keep the old value, or
overwrite it?

If you've read the [field guide to dimensional
modeling](/essays/a-field-guide-to-dimensional-modeling/), you've met this idea in
passing. Here's the full version.

## The question every dimension eventually asks

Say you have a customer dimension, and the customer `C-1077` was in the "Small
Business" segment when they placed an order last year. This year they've grown and
been moved to "Enterprise." Someone now runs a report: *sales by segment, last
year.* Should `C-1077`'s old orders count under "Small Business" (what they were at
the time) or "Enterprise" (what they are now)?

There is no universally correct answer — only a business decision. SCD types are the
menu of ways to implement whichever answer your business needs.

> An SCD type is a technical setting that encodes a business choice: when reality
> changes, does our history change with it, or stay as it was?

## Type 1 — Overwrite (forget the past)

The simplest strategy: when an attribute changes, you just update the value in
place. The old value is gone.

```sql
UPDATE dim_customer
   SET segment = 'Enterprise'
 WHERE customer_id = 'C-1077';
```

Now *all* of `C-1077`'s orders — past and future — report under "Enterprise,"
because that's the only value the dimension remembers. Last year's "sales by
segment" will retroactively change.

**Use Type 1 when history doesn't matter for that attribute** — correcting a
misspelled name, fixing a data-entry error, or tracking a value where only the
current state is ever meaningful. It's cheap and easy. The cost is amnesia: you can
never again ask what things looked like before.

## Type 2 — Add a new row (keep full history)

This is the important one, the strategy people usually mean when they say "SCD." On
change, you don't overwrite — you *expire the old row and insert a new one*. The
customer now exists as two rows: the historical version and the current version,
each valid for a span of time.

```sql
dim_customer
+-------------+-------------+------------+------------+------------+------------+
| customer_key| customer_id | segment    | valid_from | valid_to   | is_current |
+-------------+-------------+------------+------------+------------+------------+
| 4401        | C-1077      | Small Bus. | 2024-02-01 | 2026-03-14 | false      |
| 8902        | C-1077      | Enterprise | 2026-03-15 | 9999-12-31 | true       |
+-------------+-------------+------------+------------+------------+------------+
```

Each fact (each order) points to the `customer_key` that was current *when the order
happened.* Last year's orders reference key `4401` ("Small Business"); this year's
reference `8902` ("Enterprise"). History stays honest — "sales by segment, last
year" returns what was actually true then, and it never changes.

Two things make Type 2 work, and both are worth noticing. First, the validity
columns (`valid_from`, `valid_to`, `is_current`) are what let two versions of "the
same" customer coexist and be queried by date. Second — and this is why I keep
linking them — Type 2 is *only possible* because of a [surrogate
key](/essays/surrogate-keys-vs-natural-keys/). The natural key `C-1077` is identical
on both rows; it's the meaningless surrogate (`4401` vs `8902`) that distinguishes
the versions and gives facts something stable to point at. Without a surrogate key,
you simply cannot represent history this way.

The cost of Type 2 is that the dimension grows over time and your pipeline gets more
complex — it has to detect changes, expire old rows, and insert new ones correctly.
For most analytics where history matters, that complexity is worth paying.

## Type 3 — Add a column (keep limited history)

A middle option, used far less often. Instead of a new row, you keep both the old
and new value side by side in *columns*:

```
customer_id | current_segment | previous_segment | segment_changed_on
C-1077      | Enterprise      | Small Business   | 2026-03-15
```

This preserves exactly *one* step of history — you can see the current and the
immediately prior value, but nothing further back. Type 3 fits the narrow case where
you care about "before and after" a single known transition (a re-org, a
re-branding) and don't need full history. It's a specialist tool; reach for Type 2
when you want history in general, and Type 3 only for this specific shape of
question.

## Which to use

The choice is per-attribute, not per-table — a single dimension can mix strategies.
A customer's `segment` might be Type 2 (you want historical accuracy for reporting),
while a typo correction in their `name` is Type 1 (no one wants to preserve the
misspelling). Decide attribute by attribute:

- **Type 1** — you only ever care about the current value, or you're fixing an error.
- **Type 2** — you need to report on history as it actually was. This is the
  workhorse; when in doubt, this is usually the right default for attributes that
  carry analytical meaning.
- **Type 3** — you need exactly one prior value around a specific, known change.

## The trap to avoid

The classic mistake isn't choosing the wrong type — it's *not choosing at all.*
Teams default to silent Type 1 (overwriting) simply because that's what a plain
`UPDATE` does, and only discover the problem months later when someone asks for a
historical breakdown and finds the past has been quietly rewritten. By then the old
values are gone and unrecoverable.

So make the decision deliberately, attribute by attribute, before the data starts
flowing. That act — deciding what history means *before* you need it — is exactly
the kind of small, deliberate choice that separates a designed dimension from one
that merely accumulated. Slowly changing dimensions aren't arcane. They're just the
place where you decide, on purpose, what your data is allowed to forget.
