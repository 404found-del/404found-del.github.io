---
title: "Data Vault vs Dimensional Modeling: Which Belongs Where"
kicker: "Field Notes"
topic: "Modeling"
description: "Data Vault and dimensional modeling aren't rivals — they solve different problems at different layers. Here's what Data Vault actually is, what it costs, and when its complexity is worth paying."
date: 2026-06-07
---

"Data Vault or dimensional modeling?" gets asked as if the two were rivals for the
same job. They aren't. They're answers to *different questions, asked at different
layers* of a warehouse — and once you see which question each one answers, the
choice mostly makes itself. What's left is an honest judgment about whether your
organization has the problem Data Vault was built for, because its solution is not
free.

## What each one optimizes for

[Dimensional modeling](/essays/a-field-guide-to-dimensional-modeling/) optimizes for
**consumption**. Facts and dimensions, [star schemas](/essays/star-schema-vs-snowflake-schema/),
declared grain — all of it exists so that analysts and BI tools can ask business
questions simply and get consistent answers fast. It's a presentation format: the
shape data should be in when people query it.

Data Vault optimizes for something else entirely: **integration**. It's a modeling
method for the back-room layer of an enterprise warehouse — the place where data from
many volatile source systems is landed, integrated, and kept as a full, auditable
history, *before* anyone shapes it for consumption.

## What Data Vault actually is

The method decomposes everything into three kinds of table:

```
hub_customer        -- one row per business key (customer number)
  customer_hk | customer_bk | load_date | record_source

link_customer_order -- one row per relationship between hubs
  link_hk | customer_hk | order_hk | load_date | record_source

sat_customer_detail -- descriptive attributes, full history
  customer_hk | load_date | name | segment | ... | record_source
```

**Hubs** hold pure business keys — one row per real-world thing. **Links** hold
relationships between hubs. **Satellites** hang off hubs and links, carrying the
descriptive attributes — and every change inserts a new satellite row, so history
accumulates by default, like [SCD Type 2](/essays/slowly-changing-dimensions-explained/)
applied to everything. Identity comes from hashed business keys — a cousin of the
[surrogate key discipline](/essays/surrogate-keys-vs-natural-keys/), tuned so that
independent loads from many sources can generate the same key without coordinating.

That structure buys three real things. **Auditability:** every row carries its source
and load time, and nothing is ever overwritten — you can always reconstruct what was
known, when, from where. **Resilience to change:** a new source system or a new
attribute becomes a new satellite bolted on, not a refactor of existing tables.
**Parallel loading:** hubs, links, and satellites load independently, with no ordering
dependencies between sources.

## What it costs

Now the part the methodology books underplay. A Data Vault is **not queryable by
humans in any pleasant sense.** Splitting every entity into a hub plus several
satellites plus links means even simple questions become six-way joins across
generically-named tables. Nobody points a BI tool at a raw vault.

Which leads to the structural punchline: **a Data Vault shop still builds dimensional
marts on top.** The vault is the integration layer; consumption still happens through
facts and dimensions derived from it. So choosing Data Vault is never choosing it
*instead of* dimensional modeling — it's choosing to add an entire modeled layer
*underneath* your dimensional one, with all the pipelines, discipline, and tooling
that implies.

> Data Vault and dimensional modeling aren't competing answers to the same question.
> One organizes the back room for integration and audit; the other organizes the
> front room for analysis. The real decision is whether you need the back room at all.

## When the vault earns its keep

The complexity is worth paying when the problem it solves is actually yours:

- **Many volatile sources.** You're integrating data from a dozen-plus systems that
  change, merge, and get replaced — the bolt-on-a-satellite property pays off
  constantly.
- **Hard audit and compliance requirements.** Regulated industries that must prove
  what was known, when, and from which source get that for free from the vault's
  insert-only, source-stamped structure.
- **A large team needing parallel work.** The decoupled loading pattern lets many
  engineers build ingestion independently without stepping on each other.

If you recognize your organization in all three, Data Vault is a serious, proven
answer — that's the enterprise it was designed for.

## The honest default for everyone else

Most teams have a handful of reasonably stable sources, no statutory audit burden on
the warehouse itself, and a data team that fits in one meeting. For them, the vault is
machinery without a mission: an extra modeled layer whose benefits they won't collect
and whose joins, naming conventions, and loading discipline they'll pay for daily. The
simpler path — staging the sources, keeping [raw history you can replay
from](/essays/the-medallion-architecture-reconsidered/), and modeling straight into
dimensional facts and dims — covers them completely.

So resolve the "versus" the boring, correct way: dimensional modeling for the
consumption layer, always. Data Vault underneath it *only* if you genuinely carry the
multi-source, audit-heavy, big-team problem it exists to solve. A methodology is a
tool for a problem — and adopting the enterprise tool without the enterprise problem
is how warehouses end up impressively engineered and quietly unusable.
