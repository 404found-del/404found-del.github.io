---
title: "How to Make a Data Pipeline Idempotent"
kicker: "Field Notes"
topic: "Engineering"
description: "An idempotent data pipeline produces the same result whether it runs once or five times. Here are the concrete patterns — partition overwrite, merge on keys, delete-insert — that make retries and backfills safe."
date: 2026-05-29
---

A data pipeline that can't be safely re-run is a liability waiting for a bad night.
Jobs fail halfway. Schedulers retry. Someone kicks off a backfill over a range that
already partly ran. If any of those scenarios can corrupt your data — duplicate
rows, double-counted revenue, inconsistent state — you don't have a pipeline, you
have a trap. The property that defuses all of it is **idempotency**, and building
it in is more about a few disciplined patterns than about clever code.

## What idempotency actually means

An operation is idempotent if running it many times produces the same result as
running it once. Press a floor button in an elevator five times; the elevator still
goes to the floor once. For a pipeline, it means: *re-running the same job with the
same input leaves the data in exactly the same correct state, no matter how many
times it executes.*

This is not the same as "exactly-once processing," which is a hard distributed-systems
guarantee about each input being handled precisely one time. Idempotency is more
achievable and, for most batch and many streaming pipelines, more useful: you stop
trying to guarantee the job runs once, and instead make it *safe to run any number
of times.* Retries become boring. Backfills become safe. That's the whole prize.

> Don't try to guarantee your job runs exactly once. Make it not matter how many
> times it runs.

## The anti-pattern to eliminate first

The single most common idempotency killer is the **blind append**:

```sql
INSERT INTO fact_sales
SELECT * FROM staging_sales WHERE sale_date = '2026-05-29';
```

Run this twice and you have every row twice. The job has no notion of "I already
did this date" — it just appends. Every pattern below is, at heart, a way to replace
blind appends with operations that can absorb a re-run without duplicating.

## Pattern 1: Overwrite by partition

The simplest and most robust pattern: make your unit of work a **partition** (most
often a date), and have the job *replace* that partition rather than add to it.

```sql
DELETE FROM fact_sales WHERE sale_date = '2026-05-29';
INSERT INTO fact_sales
SELECT * FROM staging_sales WHERE sale_date = '2026-05-29';
```

Or, in a partitioned lake/warehouse, overwrite the single partition atomically
(`INSERT OVERWRITE`, `replaceWhere`, dynamic partition overwrite — the syntax varies
by engine). Now re-running the job for 2026-05-29 produces the same result every
time: it clears the day and rebuilds it. Retries and backfills over any date range
are automatically safe, because each date is rebuilt from scratch from its source.

This works beautifully when your data is naturally partitioned by an immutable
processing window and you can fully recompute a partition from its inputs. Make the
delete-and-load atomic so a failure mid-way can't leave the partition empty.

## Pattern 2: Merge (upsert) on a key

When you're maintaining mutable state — a dimension, a "current status per entity"
table — overwriting partitions doesn't fit. Here the tool is a **merge** keyed on a
stable identifier:

```sql
MERGE INTO dim_customer AS t
USING staging_customer AS s
  ON t.customer_id = s.customer_id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...;
```

Because the merge keys on `customer_id`, running it twice with the same input is a
no-op the second time — matched rows are updated to the same values, and nothing new
is inserted. This is why a [stable surrogate or business
key](/essays/surrogate-keys-vs-natural-keys/) matters so much: idempotent upserts
are only possible if every row has a reliable identity to match on. No key, no safe
merge.

## Pattern 3: Deterministic output keys

For systems without merge, you can lean on the storage layer's uniqueness. Compute a
**deterministic primary key** for each output row from its inputs — say, a hash of
the natural key plus the event timestamp — and write with insert-or-ignore / upsert
semantics. Because the same input always produces the same key, a re-run collides
with the rows it wrote last time instead of duplicating them. The key *is* the
idempotency.

## The rule for side effects

Transformations on data inside your warehouse are the easy case. The dangerous case
is **external side effects** — sending an email, posting to an API, incrementing a
counter, dropping a message on a queue. These are rarely idempotent by default:
retry the step and you send the email twice.

The fixes are the same family of ideas applied outward: attach an **idempotency key**
to each external action and have the receiving system de-duplicate on it (most
serious payment and messaging APIs support exactly this); or **record what you've
already done** in a state table and check it before acting. The principle holds —
make the *effect* of running twice identical to running once.

## A checklist

Before you call a pipeline safe to re-run, confirm:

- Re-running the same job for the same window produces identical output — verify it,
  don't assume it.
- There are no blind `INSERT`s; every write is an overwrite, a merge, or keyed.
- Mutable tables are merged on a stable key.
- Every external side effect carries an idempotency key or a "have I done this?" check.
- A job that fails mid-run leaves no partial, half-correct state behind.

Get these right and the 3 a.m. retry stops being an incident. The scheduler can hammer
the job, an engineer can rerun last month's backfill without flinching, and the data
lands in exactly one correct state every time — which is the entire point of building
the thing carefully in the first place.
