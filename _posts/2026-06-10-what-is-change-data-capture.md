---
title: "What Is Change Data Capture (CDC), and When Do You Need It?"
kicker: "Field Notes"
topic: "Engineering"
description: "Change data capture identifies inserts, updates, and deletes in a source database and delivers them downstream. Here's how log-based, trigger-based, and query-based CDC compare — and when a nightly batch is still fine."
date: 2026-06-10
faq:
  - q: "What is the best CDC method?"
    a: "Log-based CDC, where available. Reading the database's transaction log captures every change including deletes, in commit order, with minimal load on the source and no application changes. Triggers and timestamp polling are compromises for when log access isn't possible."
  - q: "Does change data capture capture deletes?"
    a: "Log-based and trigger-based CDC do. Query-based polling on an updated-at column does not — a deleted row leaves nothing behind to poll, which is that method's biggest structural weakness."
  - q: "Is CDC real-time?"
    a: "Capture is near-real-time — changes appear in the stream seconds after commit. End-to-end latency then depends on how you process the stream, which can be continuous streaming or micro-batches, depending on what the consuming decision needs."
---

Somewhere between your application's database and your warehouse sits an unglamorous
question: *how do changes get from one to the other?* The naive answer — re-extract
the whole table on a schedule — works until tables get large, freshness expectations
tighten, and the nightly full pull starts hammering the very database your
application depends on. **Change data capture (CDC)** is the family of techniques
that answers the question properly: identify just the changes — inserts, updates,
deletes — as they happen in the source, and deliver them downstream.

## The problem it solves

Recall [why transactional and analytical systems are kept
separate](/essays/oltp-vs-olap/): the OLTP database serves the application; analytics
lives elsewhere; data must move between them. Full-table extracts move that data by
brute force — re-reading everything to find out what's new. CDC moves it
surgically: only what changed, soon after it changed, with far less load on the
source. The output is a stream of change events, each saying roughly *this row, this
operation, these values, this moment*:

```json
{ "op": "update",
  "table": "customers",
  "before": { "id": 1077, "segment": "Small Business" },
  "after":  { "id": 1077, "segment": "Enterprise" },
  "ts": "2026-06-10T08:14:03Z" }
```

That stream can then feed the warehouse, [maintain Type 2 dimension
history](/essays/slowly-changing-dimensions-explained/) (note the before/after pair —
exactly what an SCD pipeline wants), invalidate caches, or publish events to other
systems.

## The three ways to capture changes

CDC is implemented three broad ways, and they are not equally good.

**Log-based CDC** reads the database's own transaction log — the write-ahead log that
the engine already keeps for durability. Every committed change appears there, so a
log reader captures *everything*: inserts, updates, and crucially **deletes**, in
commit order, with essentially no extra load on the source and no application
changes. This is the gold standard, and it's what serious CDC tooling does.

**Trigger-based CDC** attaches database triggers that copy every change into audit
tables, which you then read. It works on engines where log access is awkward, but the
triggers add write overhead to every transaction — you've taxed the production
workload to feed analytics, which is the exact thing we were trying to avoid.

**Query-based CDC** polls the table for rows where an `updated_at` column is newer
than the last extract. It's the easy hack, and it has two structural holes: it
**misses deletes entirely** (a vanished row leaves nothing to poll), and it misses
intermediate states between polls. It also silently depends on every writer
faithfully maintaining that timestamp column. Acceptable for low-stakes tables;
quietly wrong in ways you discover late.

Default to log-based where you can; treat the other two as compromises you've
consciously accepted.

## The caveat nobody puts on the box

CDC feels like it removes your dependency on the source team. It does the opposite.

> CDC doesn't remove the coupling to the source system — it industrializes it. You
> are now reading another team's *internal schema*, change by change, at the speed
> of their deploys.

The producing team renames a column, splits a table, changes an enum — and your
pipeline learns about it as breakage, because their internal schema was never an
interface anyone promised to keep stable. This is precisely the territory of
[data contracts](/essays/data-contracts-are-a-cultural-problem/): plugging CDC into a
database whose owners haven't agreed to treat its schema as a contract is building on
land you don't own. The technique is sound; the agreement still has to exist.

Two more practicalities. First, CDC pipelines typically deliver **at-least-once** —
events can repeat after retries and recoveries — so the consumer must be
[idempotent](/essays/how-to-make-a-data-pipeline-idempotent/), merging on keys rather
than blindly appending. Second, a change stream needs an **initial snapshot** to
start from; getting snapshot-plus-stream ordering right is where naive
implementations corrupt themselves.

## When you actually need it

CDC earns its complexity when at least one of these is true: the source tables are
**large enough** that full extracts strain the database or the window; the business
genuinely needs **freshness in minutes**, not tomorrow morning; you must **capture
deletes** or every intermediate state for audit or history; or you want one change
stream feeding **many consumers** beyond the warehouse.

And the honest converse: if your tables are modest and the business runs on
yesterday's data — which describes more organizations than will admit it — a nightly
batch extract is simpler, easier to reason about, and entirely respectable. CDC is
the right tool for a real problem, not a maturity badge. Adopt it when the problem
shows up, wire it to a source whose schema someone has actually promised to keep
stable, and make the consumer idempotent — and it will quietly become the most
dependable bridge in your platform.
