---
title: "Merge-on-Read vs Copy-on-Write: The Lakehouse Decision With Numbers"
kicker: "Field Notes"
topic: "Engineering"
description: "Copy-on-write rewrites whole files on update; merge-on-read annotates them and resolves at read time. The trade is write cost against read cost, with arithmetic."
date: 2026-07-26 09:00:00 +0530
faq:
  - q: "What is the difference between merge-on-read and copy-on-write?"
    a: "Copy-on-write rewrites every data file that contains a changed row, so the table is always clean for readers and expensive for writers. Merge-on-read leaves the original files alone and writes small delete files or deletion vectors alongside them, so writes are cheap and readers pay to reconcile the deletes at query time. It is a straight trade of write cost against read cost."
  - q: "When should I use merge-on-read instead of copy-on-write?"
    a: "Use merge-on-read when updates are frequent and scattered — streaming CDC, hourly upserts, corrections landing across old partitions — because copy-on-write's file rewrites multiply badly when few changed rows touch many files. Use copy-on-write when updates are rare or arrive in large batches confined to recent partitions, and read latency matters more than write latency."
  - q: "Does merge-on-read make queries slower?"
    a: "Yes, and the slowdown grows with every un-compacted write. Each read must apply the accumulated delete files or deletion vectors before returning rows, so latency degrades roughly in proportion to how many delete files have piled up since the last compaction. Compaction is not optional maintenance on a merge-on-read table; it is part of the design."
  - q: "Do Iceberg and Delta Lake both support merge-on-read?"
    a: "Both do, with different vocabulary and defaults. Iceberg exposes it per operation through table properties like write.update.mode and write.delete.mode, defaulting to copy-on-write. Delta Lake implements the same idea through deletion vectors, enabled with delta.enableDeletionVectors. The mechanism differs; the trade-off is identical."
---

Every [open table format](/essays/what-is-an-open-table-format/) has to answer one
awkward question: the data files are **immutable**, so what happens when a row
changes? There are exactly two answers, and choosing between them is the most
consequential operational decision in a lakehouse that nobody writes about.

**Copy-on-write** rewrites every data file that contains a changed row. The table
stays clean; the writer pays. **Merge-on-read** leaves the original files
untouched and records the change separately — a delete file, or a deletion vector
marking which rows in which file are no longer live — and makes the *reader*
reconcile them at query time. Writers get cheap; queries get slower until
someone compacts.

That's the whole trade. What follows is why it bites harder than it sounds, and
the arithmetic that tells you which side you're on.

## Copy-on-write vs merge-on-read, side by side

| | Copy-on-write | Merge-on-read |
|---|---|---|
| **On update, the writer** | Rewrites whole files containing changed rows | Writes new rows + delete files / deletion vectors |
| **Write cost** | High, and disproportionate to rows changed | Low, roughly proportional to rows changed |
| **Read cost** | Baseline — files are already correct | Baseline + reconciling accumulated deletes |
| **Read cost over time** | Flat | Degrades until compaction |
| **Compaction** | Optional tuning | **Structural requirement** |
| **Storage churn** | Rewrites amplify; old files await expiry | Small files accumulate instead |
| **Best when** | Updates rare, batched, recent-partition | Updates frequent, small, scattered |
| **Iceberg** | Default (`write.*.mode = copy-on-write`) | `write.update.mode = merge-on-read` |
| **Delta Lake** | Default | `delta.enableDeletionVectors = true` |
| **Fails by** | Write amplification | Read amplification + small-file sprawl |

## Why copy-on-write hurts more than it looks

The intuition that breaks people is this: **copy-on-write's cost tracks the number
of files touched, not the number of rows changed.** Change one row in a 128 MB
Parquet file and you rewrite 128 MB. Change one row each in nine hundred files and
you rewrite 112 GB — to modify a few hundred kilobytes of actual data.

This is why the pattern that most reliably destroys a copy-on-write table is
[change data capture](/essays/what-is-change-data-capture/). CDC updates are
small, continuous, and — crucially — *scattered*: a customer amends an order from
four months ago and your writer reaches into a partition it hasn't touched since
April. Batch loads confined to yesterday's partition are fine. Corrections
sprayed across two years of history are not.

Merge-on-read inverts it. The writer appends the new row versions and records
which old rows are dead. Nothing gets rewritten, so write cost scales with rows
changed rather than files touched. The bill moves to the reader, who now has to
subtract the dead rows from every file they scan.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 340" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="mor-cow-t mor-cow-d">
  <title id="mor-cow-t">Copy-on-write versus merge-on-read</title>
  <desc id="mor-cow-d">Two panels showing what happens when one row changes. Under copy-on-write, the entire data file containing that row is rewritten as a new file, so the writer pays and the reader gets a clean table. Under merge-on-read, the original file is left in place and a small deletion vector is written alongside it, so the writer is cheap and the reader must apply the deletion vector at query time until compaction folds it in.</desc>
  <text x="200" y="28" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Copy-on-write</text>
  <text x="600" y="28" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Merge-on-read</text>
  <text x="400" y="58" font-size="11" fill="#8b857a" text-anchor="middle">one row changes in a 128 MB file</text>
  <rect x="70" y="76" width="260" height="46" rx="5" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="98" font-size="11" fill="#1c1a17" text-anchor="middle">part-001.parquet · 128 MB</text>
  <text x="200" y="114" font-size="10" fill="#8b857a" text-anchor="middle">marked for expiry</text>
  <line x1="200" y1="122" x2="200" y2="152" stroke="#cabfac" stroke-width="2"/>
  <text x="248" y="142" font-size="10" fill="#a4391f">rewrite all</text>
  <rect x="70" y="152" width="260" height="46" rx="5" fill="#c8472b"/>
  <text x="200" y="174" font-size="11" fill="#f6f3ec" text-anchor="middle">part-009.parquet · 128 MB</text>
  <text x="200" y="190" font-size="10" fill="#f6f3ec" text-anchor="middle">128 MB written for one row</text>
  <text x="200" y="232" font-size="11" fill="#56514a" text-anchor="middle">writer pays · reader sees a clean table</text>
  <rect x="470" y="76" width="260" height="46" rx="5" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="600" y="98" font-size="11" fill="#1c1a17" text-anchor="middle">part-001.parquet · 128 MB</text>
  <text x="600" y="114" font-size="10" fill="#8b857a" text-anchor="middle">untouched</text>
  <line x1="600" y1="122" x2="600" y2="152" stroke="#cabfac" stroke-width="2"/>
  <text x="648" y="142" font-size="10" fill="#a4391f">annotate</text>
  <rect x="470" y="152" width="120" height="46" rx="5" fill="#1c1a17"/>
  <text x="530" y="174" font-size="10" fill="#f6f3ec" text-anchor="middle">deletes.puffin</text>
  <text x="530" y="190" font-size="9" fill="#8b857a" text-anchor="middle">~KB</text>
  <rect x="606" y="152" width="124" height="46" rx="5" fill="#c8472b"/>
  <text x="668" y="174" font-size="10" fill="#f6f3ec" text-anchor="middle">new rows</text>
  <text x="668" y="190" font-size="9" fill="#f6f3ec" text-anchor="middle">~KB</text>
  <text x="600" y="232" font-size="11" fill="#56514a" text-anchor="middle">writer is cheap · reader subtracts at query time</text>
  <line x1="400" y1="70" x2="400" y2="250" stroke="#ddd6c8" stroke-width="1.5" stroke-dasharray="4 4"/>
  <text x="400" y="286" font-size="12" fill="#8b857a" text-anchor="middle">the cost doesn't disappear — it moves, from the writer to the reader</text>
  <text x="400" y="310" font-size="12" fill="#8b857a" text-anchor="middle">and compaction is the bill coming due on a schedule you choose</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">Same change, two places to put the cost: rewrite now, or reconcile on every read until you compact.</figcaption>
</figure>

## A worked scenario, with the arithmetic shown

**This scenario is constructed, not measured.** The figures below are chosen to
be plausible and are worked through so you can check the reasoning and substitute
your own numbers — they are not a benchmark, and no system was run to produce
them. What matters is the *shape* of the arithmetic, which holds regardless of
the exact inputs.

Take an `orders` table on object storage:

- **2 TB**, Parquet, partitioned by day, two years of history
- Target file size **128 MB** → roughly **16,000 data files**
- CDC delivers **400,000 changed rows per day**, applied **hourly**
- So each batch carries about **16,700 rows**, averaging **1 KB** → **~17 MB** of
  genuinely changed data per hour
- Because corrections land across history, those 16,700 rows are scattered across
  about **900 distinct files**

Now price each strategy per hourly batch.

**Copy-on-write.** Every one of those 900 files gets rewritten in full:

```text
900 files × 128 MB          = 115,200 MB  ≈ 112.5 GB written
actual changed data                        ≈ 17 MB
write amplification         = 112.5 GB / 17 MB  ≈ 6,800×
```

Across 24 batches that's roughly **2.7 TB rewritten per day** to apply 400 MB of
changes — on a 2 TB table. You are rewriting more than the table, daily.

**Merge-on-read.** The writer appends the new row versions and a deletion vector
per touched file:

```text
new row data                              ≈ 17 MB
deletion vectors, 900 files × ~2 KB       ≈  1.8 MB
total written                             ≈ 19 MB
write amplification                       ≈ 1.1×
```

Three orders of magnitude less written. That is the entire reason merge-on-read
exists, and why streaming and CDC workloads reach for it.

**Then the reader's bill arrives.** Every scan must apply the accumulated
deletes. After one batch, a query touching those partitions resolves 900 deletion
vectors; after a full day without compaction, it may face **21,600**. Read
latency degrades roughly in step with that accumulation — a scan that was
comfortable in the morning is noticeably slower by evening, and the degradation
is gradual enough that people blame the query rather than the table.

**Compaction is what closes the loop.** Rewriting the affected files *once
nightly* rather than 24 times a day:

```text
distinct files touched across the whole day  ≈ 4,000
nightly rewrite                              = 4,000 × 128 MB ≈ 500 GB
vs copy-on-write's 24 × 112.5 GB             ≈ 2.7 TB
```

Same correctness, roughly **five times less data rewritten**, and reads reset to
baseline every morning. Merge-on-read plus scheduled compaction isn't a
compromise between the two strategies — it's copy-on-write's work, batched, with
the scheduling under your control instead of the CDC stream's.

## The decision rule

```text
Are updates rare, large, and confined to recent partitions?
   → Copy-on-write. Reads stay flat, writers rarely suffer.

Are updates frequent, small, or scattered across old partitions?
   → Merge-on-read — AND schedule compaction before you ship it.

Do you not know yet?
   → Copy-on-write (the default), and instrument write volume.
     If bytes-written per batch dwarfs rows-changed, you have your answer.
```

The threshold worth watching is the ratio in that last line: **bytes rewritten
divided by bytes actually changed.** Below roughly 10× copy-on-write is fine.
Somewhere past 100× it is quietly burning your compute budget, and past 1,000× it
is the reason your hourly job now takes fifty minutes.

## How to set it

Iceberg exposes the choice per operation, which is more useful than it first
appears — deletes and updates often have different profiles from merges:

```sql
ALTER TABLE lake.sales.orders SET TBLPROPERTIES (
  'write.delete.mode'  = 'merge-on-read',
  'write.update.mode'  = 'merge-on-read',
  'write.merge.mode'   = 'merge-on-read'
);

-- Compaction is the other half of the decision, not an afterthought:
CALL lake.system.rewrite_data_files(
  table => 'sales.orders',
  options => map('target-file-size-bytes', '134217728')
);
CALL lake.system.rewrite_position_delete_files(table => 'sales.orders');
```

Delta reaches the same place through deletion vectors:

```sql
ALTER TABLE lake.sales.orders
  SET TBLPROPERTIES ('delta.enableDeletionVectors' = true);

-- Fold the soft deletes back into the data files:
REORG TABLE lake.sales.orders APPLY (PURGE);
```

The mechanisms differ in detail — Iceberg's modes are documented in the
[table specification](https://iceberg.apache.org/spec/), Delta's behaviour and
the version in which each operation gained support in the
[deletion vectors docs](https://docs.delta.io/latest/delta-deletion-vectors.html)
— but the trade-off underneath is identical, which is a good sign it's a property
of the problem rather than of either implementation.

## The part that actually goes wrong

Almost nobody chooses merge-on-read badly. They choose it *correctly* and then
don't schedule compaction, because in the first week the table is fast and the
setting looks free. The degradation is gradual, it lands on readers rather than
on the pipeline that caused it, and by the time anyone investigates, the small
files have multiplied and the metadata planning cost has grown alongside the scan
cost.

So treat it as one decision with two halves. Turning on merge-on-read without a
compaction schedule isn't a tuning choice; it's a deferred cost with no due date,
which is the same category of mistake as
[a pipeline that isn't idempotent](/essays/how-to-make-a-data-pipeline-idempotent/)
— it works until precisely the moment it matters.

Pick the side your update pattern puts you on. Then pay the bill on a schedule
you chose, rather than one your CDC stream chose for you.
