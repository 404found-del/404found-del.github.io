---
title: "OLTP vs OLAP: Why You Shouldn't Run Analytics on Your App Database"
kicker: "Field Notes"
topic: "Architecture"
description: "OLTP systems handle many small transactions fast. OLAP systems scan huge volumes for analysis. They're optimized for opposite things — which is why querying your production database for analytics is a trap."
date: 2026-05-23
last_modified_at: 2026-07-18
faq:
  - q: "What is the difference between OLTP and OLAP?"
    a: "OLTP (online transaction processing) runs the business: many small, concurrent reads and writes of individual records, on normalized schemas built for integrity. OLAP (online analytical processing) analyses the business: few large queries scanning millions of rows, on denormalized models built for reads. The two shapes conflict in one engine."
  - q: "Why shouldn't I run analytics on my production database?"
    a: "Because analytical scans lock resources transactions need, and the normalized schema that keeps writes safe makes analytical queries slow and join-heavy. Past trivial scale, analytics moves to a replica at minimum — properly, to a warehouse or lakehouse modelled for the purpose."
  - q: "Can one database do both OLTP and OLAP?"
    a: "Hybrid (HTAP) engines exist and keep improving, but the mainstream answer remains separation: an operational database plus an analytical store fed by CDC or batch loads. The bottleneck isn't technology so much as modelling — the same schema genuinely cannot be optimal for both access patterns."
---

Every data architecture eventually runs into the difference between OLTP and OLAP,
usually the hard way: someone runs a big analytical query against the production
application database, and the app slows to a crawl for everyone. The two acronyms
describe two kinds of database workload that are optimised for *opposite* things, and
understanding why is the foundation under nearly every decision about where analytics
should live.

## Two opposite jobs

**OLTP** — Online Transaction Processing — is the workload your *application* runs. It's
defined by **many small, fast operations**: a user places an order, updates their
profile, adds an item to a cart. Thousands of these happen concurrently, each
touching a handful of rows, mixing reads and writes. The database behind your app —
Postgres, MySQL, SQL Server — is an OLTP system, and it's tuned to do this well:
insert a row, update a record, look up a single customer by ID, all in milliseconds.

**OLAP** — Online Analytical Processing — is the workload your *analytics* runs. It's
defined by **few large, complex operations**: "total revenue by product category by
month for the last three years." A single such query might scan millions or billions
of rows, aggregate them, and join across large tables. There are far fewer of these
queries, they're almost entirely reads, and each one is enormous compared to an OLTP
operation.

> OLTP is many people each touching a little data. OLAP is a few people each touching
> a lot of data. Almost every difference between the two follows from that.

## Why the same database can't do both well

The two workloads don't just differ in size — they pull the underlying design in
incompatible directions. Three differences matter most.

**Row storage vs column storage.** OLTP databases store data *by row*, because a
transaction typically wants a whole record at once (give me everything about this
order). OLAP systems store data *by column*, because an analytical query typically
wants one or two columns across a vast number of rows (give me the `amount` column for
ten million orders, and sum it). Reading a single column from row-stored data means
touching every row to extract one field — slow. Column storage reads just that
column — fast. The storage layout that's right for one workload is actively wrong for
the other.

**Normalized vs denormalized.** OLTP schemas are *normalized* — data split across many
tables to avoid redundancy and keep writes consistent and cheap. That's ideal for
transactions but painful for analysis, where answering a business question means
joining a dozen normalized tables together every time. OLAP systems are
*denormalized* — data deliberately pre-joined into wide tables and
[dimensional models](/essays/a-field-guide-to-dimensional-modeling/) like
[star schemas](/essays/star-schema-vs-snowflake-schema/) — so analytical queries are
simple and fast. Again: opposite choices, each correct for its own job.

**Contention.** This is the one that bites you in production. A heavy OLAP query
scanning millions of rows consumes huge amounts of memory, CPU, and I/O, and can hold
locks or saturate the database while it runs. On a dedicated analytical system,
fine — that's what it's for. On your *production OLTP database*, that same query
starves the fast little transactions your application depends on, and real users feel
it: checkouts hang, pages time out. You've made your app slow to compute a report.

## The architectural answer

Because one system can't serve both workloads well, the standard architecture is to
**keep them separate and move data from one to the other.** Your application writes to
its OLTP database, optimised for transactions. On some cadence — batch jobs, or
[change data capture](/essays/what-is-change-data-capture/) streaming
changes continuously — that data is copied into a separate analytical store (a
warehouse or [lakehouse](/glossary/data-lakehouse/)) optimised for OLAP, where it's reshaped into denormalized,
column-stored, analytics-friendly models.

This separation is why the modern data stack looks the way it does. The warehouse
isn't a second copy of your database for no reason — it exists precisely *because* the
analytical workload needed its own home, with the opposite storage model, the
opposite schema design, and its own compute that can't slow down your app. The
[pipelines that keep it in sync](/essays/how-to-make-a-data-pipeline-idempotent/) are
the bridge between the two worlds.

## The rule of thumb

When you catch yourself about to run analytics against a production application
database, stop and recognise the workload mismatch. A little reporting on a small app
is survivable; real analytics at scale is not. The instinct to "just query the prod
DB" is the instinct that takes the site down at month-end close.

Keep transactions on OLTP. Keep analytics on OLAP. Move data deliberately between
them. It looks like more infrastructure than necessary right up until the moment a
single analyst's query would have frozen your checkout flow — and then it looks like
exactly the right amount.
