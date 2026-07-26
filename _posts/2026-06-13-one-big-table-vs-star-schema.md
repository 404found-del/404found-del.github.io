---
title: "One Big Table vs the Star Schema: The Real Trade-off"
kicker: "Field Notes"
topic: "Modeling"
description: "One Big Table denormalizes everything into one wide table; the star schema keeps facts and dimensions apart. What each costs, and why the answer is usually both."
date: 2026-06-13
last_modified_at: 2026-07-26
faq:
  - q: "What is One Big Table (OBT)?"
    a: "A modeling approach that flattens facts and all their related dimensions into a single wide, denormalized table — so a query needs no joins. It trades storage and some flexibility for query simplicity and speed, and is popular for feeding specific dashboards on columnar warehouses."
  - q: "Is OBT better than a star schema?"
    a: "Neither is universally better; they optimize for different things. A star schema is a flexible, maintainable foundation that serves many questions; OBT is a fast, simple serving layer for known queries. Most mature setups keep a star schema as the core and build OBTs on top for specific consumers."
  - q: "Do columnar warehouses make joins cheap enough to skip OBT?"
    a: "Modern columnar engines handle star-schema joins efficiently, so the performance gap is much smaller than it used to be. OBT still helps for very high-concurrency dashboards or BI tools that struggle with joins, but it's an optimization, not a default."
---

A genuine modeling debate has been quietly running for years: should you model
analytics data as a **star schema** — facts and dimensions kept separate, joined at
query time — or as **One Big Table** (OBT), where everything is flattened into a
single wide, denormalized table with no joins at all? Partisans on both sides talk
past each other, usually because they're optimizing for different things without
saying so. Here's the actual trade-off, and why the right answer is less either/or
than the debate implies.

## The two approaches

The [star schema](/essays/star-schema-vs-snowflake-schema/) is the classic
[dimensional model](/essays/a-field-guide-to-dimensional-modeling/): a central
[fact table](/essays/fact-table-types/) of measurements surrounded by dimension
tables of context, joined on keys when you query. Sales facts here; customer,
product, and date dimensions there; assembled per question.

One Big Table throws out the separation. You pre-join the fact and all its dimensions
once, in the pipeline, and store the result as a single wide table — every order line
already carrying its customer name, product category, store region, and date
attributes inline. The query then touches one table and joins nothing.

That's the whole distinction: the star **normalizes context into separate tables and
joins on read**; OBT **denormalizes everything into one table and joins on write.**

## What OBT buys you

The case for OBT is real, and it's about simplicity at the point of consumption.

**No joins for the analyst.** Every question is a single-table `SELECT` with a filter
and a group-by. There's no schema to learn, no risk of getting a join wrong, no
fan-out traps. For self-serve BI and less technical users, this is a genuine
reduction in friction.

**Fast, predictable queries — for that table.** With everything pre-joined, the engine
just scans one columnar table. On high-concurrency dashboards, or with BI tools that
generate clumsy join SQL, that predictability is valuable.

**It fits how columnar storage works.** Wide, denormalized tables compress well and
scan efficiently on modern warehouses — repeated values like "Electronics" cost
almost nothing once compressed. The old penalty for very wide tables has largely
evaporated.

## What it costs

The costs are the mirror image, and they show up over time rather than on day one.

**Explosive redundancy and rigidity.** Every attribute is repeated on every row, and —
the deeper problem — the table is built for the questions you *anticipated*. A new
question that needs an attribute you didn't flatten in means going back to rebuild the
pipeline, not just writing a different query. The star's separation is what keeps it
flexible; OBT trades that flexibility for the convenience of the pre-join.

**History gets awkward.** Handling [slowly changing
dimensions](/essays/slowly-changing-dimensions-explained/) in a flattened table is
clumsy — you lose the clean versioning that a separate dimension with validity dates
gives you almost for free.

**Combinatorial sprawl.** Because each OBT is shaped for a set of questions, teams end
up building *many* of them — one per dashboard or use case — and now the same measure
is computed in a dozen wide tables that quietly drift apart. You've recreated the
"three different revenue numbers" problem, one big table at a time.

> A star schema is a flexible foundation that answers questions you haven't thought of
> yet. One Big Table is a fast answer to questions you already know. Confuse the two
> and you'll either over-engineer a dashboard or under-build a platform.

## The honest answer: both, at different layers

Framing this as a winner-takes-all choice is the actual mistake. In most mature
setups, the two are **layers, not rivals.**

Keep a **star schema as your core model** — the flexible, maintainable,
single-source-of-truth foundation where facts and dimensions live cleanly and history
is handled properly. Then, where a specific high-traffic dashboard or a join-averse
BI tool needs it, **build One Big Table on top** as a *serving layer* — a denormalized,
pre-joined projection derived *from* the star, optimized for that consumption.

This gives you both properties without the trap: the star preserves flexibility,
governance, and a single place where each measure is defined; the OBT delivers
join-free speed and simplicity to the consumers that benefit from it. Crucially, the
OBT is *derived*, so it can't drift into its own private definition of revenue — it
inherits the star's.

So don't pick a tribe. Recognize what each tool is for. If you have one dashboard and
a small team, an OBT alone may genuinely be all you need — don't build a star schema to
feed a single report. If you're building a platform that many people query many ways,
the star is your foundation, with OBTs as fast projections where they earn their keep.
The question was never "star or OBT?" It was "which layer am I building right now?" —
and that one usually answers itself.
