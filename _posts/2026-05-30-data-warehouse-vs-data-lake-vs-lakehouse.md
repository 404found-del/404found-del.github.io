---
title: "Data Warehouse vs Data Lake vs Lakehouse: A Clear Comparison"
kicker: "Field Notes"
topic: "Architecture"
description: "A data warehouse stores structured, modeled data for analytics. A data lake stores raw data of any shape, cheaply. A lakehouse tries to be both. Here's the real trade-off and how to choose."
date: 2026-05-30
---

Three terms get used almost interchangeably and mean genuinely different things: the
**data warehouse**, the **data lake**, and the **lakehouse**. The confusion is
understandable, because all three are "places you put data for analytics." But they
make opposite bets about structure, cost, and trust, and choosing well means
understanding the bet each one makes. Here's the clear version.

## Data warehouse: structure first

A data warehouse stores **structured, modeled data**, optimised for analytical
queries. Before data lands in a warehouse, it's cleaned, shaped, and fitted to a
schema — an approach called *schema-on-write*, because the structure is enforced at
the moment you write the data in.

This is the world of [dimensional
models](/essays/a-field-guide-to-dimensional-modeling/),
[star schemas](/essays/star-schema-vs-snowflake-schema/), and curated tables. The
warehouse's whole value proposition is **trust and speed for analytics**: because
everything is modeled and typed up front, queries are fast, results are consistent,
and a business analyst can point a BI tool at it and get reliable answers without
thinking about plumbing.

The costs are real, though. Schema-on-write means **upfront modeling work** before
data is usable, and rigidity afterward — adding a new data source or changing shape
takes deliberate effort. Warehouses also traditionally **couple storage and
compute** and charge accordingly, which gets expensive at scale and makes them a
poor home for huge volumes of raw or semi-structured data (logs, images, free text)
that don't fit neatly into columns.

## Data lake: flexibility first

A data lake makes the opposite bet. It stores **raw data of any shape** — structured,
semi-structured, unstructured — as files in cheap object storage (S3, GCS, Azure
Blob). There's no schema required to *write*; you impose structure later, when you
*read*, an approach called *schema-on-read*.

This buys two things warehouses struggle with. First, **cost**: object storage is
cheap, so you can keep enormous volumes of data affordably. Second, **flexibility**:
you can dump data in now and decide what to do with it later, which suits data
science, machine learning, and any workload that wants raw, untransformed inputs.
The lake is also the natural home for [immutable raw history you can always reprocess
from](/essays/the-medallion-architecture-reconsidered/).

But flexibility has a failure mode, and it has a name: the **data swamp**. With no
enforced schema, no guaranteed quality, and often no clear ownership, a lake can
degrade into a vast pile of files nobody trusts or understands. There's also no
built-in transactional guarantee — no clean notion of "this table is in a consistent
state right now" — which makes lakes hard to use for the reliable, concurrent
analytics that warehouses do effortlessly. A lake gives you everything and promises
nothing.

## Lakehouse: an attempt to have both

The lakehouse is the newer idea, and it's exactly what the name suggests: an attempt
to get **warehouse-like reliability on data-lake economics.** You keep your data in
cheap object storage as files — the lake part — but add a **metadata and table layer
on top** that brings the structure and guarantees a warehouse has.

> The lakehouse bet: keep the cheap, flexible storage of a lake, but add a layer that
> gives it the schema, transactions, and trust of a warehouse — so you don't have to
> run and sync both.

That added layer is delivered by **open table formats** — Apache Iceberg, Delta Lake,
Apache Hudi — which sit over the raw files and provide the things lakes lacked: ACID
transactions (consistent reads and writes), schema enforcement and evolution,
time-travel to past versions, and performance optimisations. The result is a single
system where you can run both the flexible, ML-style workloads of a lake *and* the
reliable, structured BI of a warehouse, without maintaining two separate platforms
and a brittle pipeline copying between them.

The trade-off is **maturity and complexity.** The lakehouse stack is younger and has
more moving parts than a turnkey warehouse; you're assembling storage, a table
format, a query engine, and a catalog rather than buying one integrated product. For
some teams that flexibility is the point; for others it's overhead they don't need.

## How to choose

Strip away the marketing and it comes down to your workload:

- **Choose a warehouse** when your work is overwhelmingly structured analytics and BI,
  you value simplicity and reliability over flexibility, and your data volumes are
  manageable. For a team that mostly builds dashboards and reports, a warehouse is
  still the simplest, most dependable answer — don't over-engineer past it.
- **Choose a lake** when you have large volumes of raw, varied, or unstructured data,
  heavy data-science or ML needs, and the engineering discipline to stop it becoming
  a swamp. Rarely the whole answer on its own anymore.
- **Choose a lakehouse** when you genuinely need both — structured BI *and* raw/ML
  workloads on the same large datasets — and want to avoid running a separate lake and
  warehouse with a sync pipeline between them. This is where many teams are
  converging, but adopt it because you have both needs, not because it's the newest
  word.

## The part none of them solve

One caution worth ending on. Whichever you pick, it answers *where data is stored and
how it's structured* — a physical question. None of the three tells you what your
data *means*: which definition of "revenue" is canonical, who owns the customer
table, how "active user" is defined. That's the job of a [semantic
layer](/essays/what-is-a-semantic-layer/), which sits *above* all three. Teams often
expect a shiny new lakehouse to fix their consistency problems and are surprised when
the same three-different-numbers arguments continue — because storage was never the
thing causing them. Choose the right store for your workload. Then govern the meaning
on top of it. They're different problems, and you need answers to both.
