---
title: "What Is Change Data Capture (CDC), and When Do You Need It?"
kicker: "Field Notes"
topic: "Engineering"
description: "Change data capture identifies inserts, updates, and deletes in a source database and delivers them downstream. How the three methods compare, and when batch wins."
date: 2026-06-10
last_modified_at: 2026-07-26
faq:
  - q: "What is the best CDC method?"
    a: "Log-based CDC, where available. Reading the database's transaction log captures every change including deletes, in commit order, with minimal load on the source and no application changes. Triggers and timestamp polling are compromises for when log access isn't possible."
  - q: "Does change data capture capture deletes?"
    a: "Log-based and trigger-based CDC do. Query-based polling on an updated-at column does not — a deleted row leaves nothing behind to poll, which is that method's biggest structural weakness."
  - q: "Is CDC real-time?"
    a: "Capture is near-real-time — changes appear in the stream seconds after commit. End-to-end latency then depends on how you process the stream, which can be continuous streaming or micro-batches, depending on what the consuming decision needs."
---

Somewhere between your application's database and your warehouse sits an unglamorous
question: *how do changes get from one to the other?* The naive answer, re-extracting
the whole table on a schedule, works until tables get large, freshness expectations
tighten, and the nightly full pull starts hammering the very database your
application depends on. **Change data capture (CDC)** is the family of techniques
that answers the question properly: identify just the changes (inserts, updates,
deletes) as they happen in the source, and deliver them downstream.

## The problem it solves

Recall [why transactional and analytical systems are kept
separate](/essays/oltp-vs-olap/): the [OLTP](/glossary/oltp/) database serves the application; analytics
lives elsewhere; data must move between them. Full-table extracts move that data by
brute force, re-reading everything to find out what's new. CDC moves it
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

**Log-based CDC** reads the database's own transaction log, the write-ahead log that
the engine already keeps for durability. Every committed change appears there, so a
log reader captures *everything*: inserts, updates, and crucially **deletes**, in
commit order, with essentially no extra load on the source and no application
changes. This is the gold standard, and it's what serious CDC tooling does.
[Debezium's architecture docs](https://debezium.io/documentation/reference/stable/architecture.html)
are the clearest free description of the mechanics, down to which log each engine
exposes (MySQL's binlog, Postgres's logical replication stream).

**Trigger-based CDC** attaches database triggers that copy every change into audit
tables, which you then read. It works on engines where log access is awkward, but the
triggers add write overhead to every transaction; you've taxed the production
workload to feed analytics, which is the exact thing we were trying to avoid.

**Query-based CDC** polls the table for rows where an `updated_at` column is newer
than the last extract. It's the easy hack, and it has two structural holes: it
**misses deletes entirely** (a vanished row leaves nothing to poll), and it misses
intermediate states between polls. It also silently depends on every writer
faithfully maintaining that timestamp column. Acceptable for low-stakes tables;
quietly wrong in ways you discover late.

Default to log-based where you can; treat the other two as compromises you've
consciously accepted.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 320" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="cdc-methods-t cdc-methods-d">
  <title id="cdc-methods-t">The three ways to capture changes, compared</title>
  <desc id="cdc-methods-d">Three capture methods read the same source database differently. Log-based CDC reads the transaction log the engine already writes, catching inserts, updates and deletes in commit order with no extra load. Trigger-based CDC attaches triggers that copy changes into audit tables, taxing every production write. Query-based CDC polls an updated-at column, which misses deletes entirely because a vanished row leaves nothing to poll, and misses intermediate states between polls.</desc>
  <rect x="300" y="16" width="200" height="42" rx="6" fill="#1c1a17"/>
  <text x="400" y="42" font-size="12" fill="#f6f3ec" text-anchor="middle">source database</text>
  <line x1="340" y1="58" x2="150" y2="106" stroke="#cabfac" stroke-width="2"/>
  <line x1="400" y1="58" x2="400" y2="106" stroke="#cabfac" stroke-width="2"/>
  <line x1="460" y1="58" x2="650" y2="106" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="106" width="220" height="96" rx="6" fill="#c8472b"/>
  <text x="150" y="130" font-size="12" fill="#f6f3ec" text-anchor="middle" font-weight="700">log-based</text>
  <text x="150" y="150" font-size="11" fill="#f6f3ec" text-anchor="middle">reads the write-ahead log</text>
  <text x="150" y="170" font-size="11" fill="#f6f3ec" text-anchor="middle">inserts · updates · DELETES</text>
  <text x="150" y="190" font-size="11" fill="#f6f3ec" text-anchor="middle">in commit order · no source load</text>
  <rect x="290" y="106" width="220" height="96" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="400" y="130" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">trigger-based</text>
  <text x="400" y="150" font-size="11" fill="#56514a" text-anchor="middle">triggers write audit tables</text>
  <text x="400" y="170" font-size="11" fill="#56514a" text-anchor="middle">catches deletes</text>
  <text x="400" y="190" font-size="11" fill="#a4391f" text-anchor="middle">taxes every production write</text>
  <rect x="540" y="106" width="220" height="96" rx="6" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="650" y="130" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">query-based</text>
  <text x="650" y="150" font-size="11" fill="#56514a" text-anchor="middle">polls updated_at</text>
  <text x="650" y="170" font-size="11" fill="#a4391f" text-anchor="middle">misses deletes entirely</text>
  <text x="650" y="190" font-size="11" fill="#a4391f" text-anchor="middle">misses states between polls</text>
  <text x="400" y="242" font-size="12" fill="#8b857a" text-anchor="middle">a deleted row leaves nothing behind to poll — which is why the log is the gold standard</text>
  <text x="400" y="272" font-size="12" fill="#8b857a" text-anchor="middle">default to log-based; treat the other two as compromises you consciously accepted</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">Same source, three taps: only the log sees deletes, ordering, and every intermediate state.</figcaption>
</figure>

## The caveat nobody puts on the box

CDC feels like it removes your dependency on the source team. It does the opposite.

> CDC doesn't remove the coupling to the source system; it industrializes it. You
> are now reading another team's *internal schema*, change by change, at the speed
> of their deploys.

The producing team renames a column, splits a table, changes an enum, and your
pipeline learns about it as breakage, because their internal schema was never an
interface anyone promised to keep stable. This is precisely the territory of
[data contracts](/essays/data-contracts-are-a-cultural-problem/): plugging CDC into a
database whose owners haven't agreed to treat its schema as a contract is building on
land you don't own. The technique is sound; the agreement still has to exist.

And one downstream consequence worth knowing before you turn CDC on: scattered
small updates are the worst possible input to a lakehouse table configured for
copy-on-write, because the rewrite cost scales with *files touched* rather than
rows changed. If your CDC target is an Iceberg or Delta table, read
[merge-on-read vs copy-on-write](/essays/merge-on-read-vs-copy-on-write/) before
the first backfill, not after the compute bill.

Two more practicalities. First, CDC pipelines typically deliver **at-least-once**;
events can repeat after retries and recoveries, so the consumer must be
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
yesterday's data, which describes more organizations than will admit it, a nightly
batch extract is simpler, easier to reason about, and entirely respectable. CDC is
the right tool for a real problem, not a maturity badge. Adopt it when the problem
shows up, wire it to a source whose schema someone has actually promised to keep
stable, and make the consumer idempotent — and it will quietly become the most
dependable bridge in your platform.
