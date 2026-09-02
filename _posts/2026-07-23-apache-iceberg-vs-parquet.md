---
title: "Apache Iceberg vs Parquet: They're Not the Same Layer"
kicker: "Field Notes"
topic: "Architecture"
description: "Parquet is a file format, Iceberg is a table format that manages Parquet files. The difference, what Iceberg costs, and how to migrate without rewriting."
date: 2026-07-23 09:00:00 +0530
last_modified_at: 2026-08-29
faq:
  - q: "What is the difference between Apache Iceberg and Parquet?"
    a: "Parquet is a file format — it defines how the bytes of a single file are laid out on disk, column by column, compressed. Apache Iceberg is a table format — it defines how many files together form one logical table, tracking which files are current, what schema applies, and how changes commit atomically. Iceberg tables are almost always made of Parquet files, so it's not a choice between them; it's two layers of the same stack."
  - q: "Do I use Iceberg or Parquet?"
    a: "Usually both, together. You store your data as Parquet files for efficient columnar compression and scanning, and you put Iceberg on top to turn a folder of those files into a real table with ACID transactions, schema evolution, and time travel. Choosing 'Parquet or Iceberg' is like choosing 'pages or a book' — the book is made of pages."
  - q: "Can Iceberg use file formats other than Parquet?"
    a: "Yes. The Iceberg spec supports Parquet, ORC, and Avro as underlying data files, and the choice is configurable per table. Parquet is the overwhelmingly common default for analytical workloads, but Iceberg's design deliberately separates the table layer from the file layer, so the file format is a swappable implementation detail."
  - q: "Is Parquet being replaced by Iceberg?"
    a: "No — Iceberg makes Parquet more useful, not obsolete. Iceberg needs a file format underneath it to actually store the rows, and Parquet is the one it reaches for most. The trend isn't Parquet being replaced; it's bare folders of Parquet files being wrapped in a table format so they behave like databases."
  - q: "How do I convert existing Parquet files to an Iceberg table?"
    a: "Without rewriting the data, in most cases. Iceberg ships Spark procedures for exactly this: add_files registers existing Parquet files into an Iceberg table by reading their footers and writing metadata; migrate converts a registered Hive or Spark table in place; snapshot creates an Iceberg table that shares the original files, so you can test before committing. All three write metadata rather than data, so a terabyte of Parquet becomes an Iceberg table in minutes, not hours."
  - q: "What does Apache Iceberg cost you?"
    a: "Four things the vendor comparisons rarely mention. Metadata accumulates, so snapshots need expiring or planning slows down. Frequent small commits create small files that must be compacted. Failed writes leave orphan files that need collecting. And the catalog becomes a hard runtime dependency in the write path of every transaction, which is also where lock-in now lives. None is a reason to avoid Iceberg; all four are maintenance you must schedule rather than discover."
---

The question "Apache Iceberg vs Parquet" contains a hidden mistake, and clearing
it up is most of the answer: **they are not competitors, because they operate at
different layers of the stack.** Parquet is a **file format** — it defines how the
bytes inside a *single* file are arranged (columnar, compressed, with embedded
statistics). [Apache Iceberg](/glossary/apache-iceberg/) is a
**table format** — it defines how *many* files together form one logical table,
tracking which files are current, what schema applies, and how a change commits
atomically. An Iceberg table is, in the overwhelming majority of cases, *made of
Parquet files.* So you don't choose between them any more than you choose between
"pages" and "a book." The useful question is what each layer does, and this is
the essay that untangles it.

## The one-sentence version

**Parquet is how one file stores rows; Iceberg is how a pile of files becomes a
table.** Everything else follows from that.

| | Apache Parquet | Apache Iceberg |
|---|---|---|
| **Layer** | File format | Table format |
| **Scope** | One file | Many files = one table |
| **Defines** | Byte layout, columnar, compression | Which files are the table, schema, snapshots |
| **Gives you** | Small size, fast column scans | ACID commits, schema evolution, time travel |
| **Transactions** | None | Yes — atomic commits |
| **History** | None | Snapshots + time travel |
| **Row-level updates** | Rewrite the whole file | MERGE / deletes via metadata |
| **Made of** | Raw columnar bytes | Metadata + data files (usually Parquet) |
| **Analogy** | A page | The book, and its table of contents |

## What Parquet actually does

Parquet is a **columnar file format**: instead of storing row 1, then row 2, it
stores all of column A, then all of column B. That single decision is why it's the
backbone of analytics — a query that needs two columns out of fifty reads only
those two, and columns of like values compress far better than mixed rows.

Those claims are usually asserted. Here they are measured, on 3 million rows and
11 columns, from a [benchmark whose script is published](/essays/parquet-vs-orc-vs-avro-benchmark/):

| | CSV | Parquet (zstd) | Difference |
|---|---|---|---|
| **On disk** | 342.6 MB | 56.6 MB | **6.1× smaller** |
| **Full scan** | 1.398 s | 0.377 s | 3.7× faster |
| **Read 2 of 11 columns** | 0.499 s | 0.054 s | **9.2× faster** |
| **Filtered aggregation (DuckDB)** | 0.879 s | 0.064 s | **13.8× faster** |

The row that matters most is the third. CSV's apparent "column pruning" saves
only the conversion of columns you didn't ask for — it still parses every byte of
every row, because the bytes of one column are physically interleaved with all
the others. Parquet reads two column chunks and skips the rest of the file. That
is the whole argument for columnar storage, and it is worth roughly an order of
magnitude on the shape every [OLAP](/glossary/olap/) query has.

But a Parquet file knows nothing beyond itself. It cannot tell you which *other*
files belong to the same table, whether a write finished, or what the data looked
like yesterday. Put a thousand Parquet files in a folder and you have a thousand
files — not a table. Two jobs writing at once can leave it half-updated; a schema
change means hoping every reader notices. That gap is exactly what a table format
exists to close.

## What Iceberg adds on top

Iceberg treats those Parquet files as immutable data and layers a **tree of
metadata** over them: a catalog holds one atomic pointer per table, the pointer
names a metadata file, the metadata names a snapshot, and the snapshot lists the
data files. Committing a change writes new files and swaps one pointer — atomic
even on eventually-consistent object storage.

<figure style="margin:2rem auto;text-align:center;">
<svg class="dia-mob" viewBox="0 0 400 470" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="aivp-mt aivp-md">
  <title id="aivp-mt">Iceberg and Parquet occupy different layers</title>
  <desc id="aivp-md">Apache Iceberg as a table format on top, chaining catalog to metadata to snapshot to file list and supplying ACID, schema evolution and time travel. Beneath it, three self-contained columnar Parquet files holding the actual bytes. The files store the data; Iceberg decides which of them are the table right now.</desc>
  <rect x="20" y="16" width="360" height="72" rx="6" fill="#c8472b"/>
  <text x="200" y="42" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">Iceberg — table format</text>
  <text x="200" y="62" font-size="10" fill="#f6f3ec" text-anchor="middle">catalog → metadata → snapshot</text>
  <text x="200" y="78" font-size="10" fill="#f6f3ec" text-anchor="middle">→ file list</text>
  <text x="200" y="108" font-size="10" fill="#8b857a" text-anchor="middle">ACID · schema evolution · time travel</text>
  <line x1="200" y1="118" x2="200" y2="146" stroke="#cabfac" stroke-width="2"/>
  <text x="248" y="138" font-size="10" fill="#8b857a">manages ↓</text>
  <rect x="20" y="150" width="360" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="173" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">part-001.parquet</text>
  <text x="200" y="192" font-size="10" fill="#56514a" text-anchor="middle">columnar bytes</text>
  <rect x="20" y="212" width="360" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="235" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">part-002.parquet</text>
  <text x="200" y="254" font-size="10" fill="#56514a" text-anchor="middle">columnar bytes</text>
  <rect x="20" y="274" width="360" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="297" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">part-003.parquet</text>
  <text x="200" y="316" font-size="10" fill="#56514a" text-anchor="middle">columnar bytes</text>
  <text x="200" y="352" font-size="10" fill="#1c1a17" text-anchor="middle">Parquet — file format: each box is one</text>
  <text x="200" y="368" font-size="10" fill="#1c1a17" text-anchor="middle">self-contained columnar file</text>
  <text x="200" y="400" font-size="10" fill="#8b857a" text-anchor="middle">the files store the data; Iceberg decides</text>
  <text x="200" y="416" font-size="10" fill="#8b857a" text-anchor="middle">which of them <tspan font-style="italic">are</tspan> the table, right now</text>
  <text x="200" y="444" font-size="10" fill="#8b857a" text-anchor="middle">swap the pointer at the top and the</text>
  <text x="200" y="460" font-size="10" fill="#8b857a" text-anchor="middle">whole table changes atomically</text>
</svg>
<svg class="dia-desk" viewBox="0 0 800 320" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="apache-iceberg-vs-parquet-t apache-iceberg-vs-parquet-d">
  <title id="apache-iceberg-vs-parquet-t">Iceberg and Parquet occupy different layers</title>
  <desc id="apache-iceberg-vs-parquet-d">Apache Iceberg as a table format on top, chaining catalog to metadata to snapshot to file list and supplying ACID, schema evolution and time travel. Beneath it, three self-contained columnar Parquet files holding the actual bytes. The files store the data; Iceberg decides which of them are the table right now.</desc>
  <rect x="250" y="16" width="300" height="60" rx="6" fill="#c8472b"/>
  <text x="400" y="42" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">Iceberg — table format</text>
  <text x="400" y="62" font-size="11" fill="#f6f3ec" text-anchor="middle">catalog → metadata → snapshot → file list</text>
  <text x="600" y="100" font-size="11" fill="#8b857a">ACID · schema evolution · time travel</text>
  <line x1="400" y1="76" x2="400" y2="120" stroke="#cabfac" stroke-width="2"/>
  <text x="430" y="112" font-size="11" fill="#8b857a">manages ↓</text>
  <rect x="120" y="120" width="180" height="70" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="210" y="150" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">part-001.parquet</text>
  <text x="210" y="172" font-size="10" fill="#56514a" text-anchor="middle">columnar bytes</text>
  <rect x="310" y="120" width="180" height="70" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="400" y="150" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">part-002.parquet</text>
  <text x="400" y="172" font-size="10" fill="#56514a" text-anchor="middle">columnar bytes</text>
  <rect x="500" y="120" width="180" height="70" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="590" y="150" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">part-003.parquet</text>
  <text x="590" y="172" font-size="10" fill="#56514a" text-anchor="middle">columnar bytes</text>
  <text x="400" y="230" font-size="12" fill="#1c1a17" text-anchor="middle">Parquet — file format: each box is one self-contained columnar file</text>
  <text x="400" y="270" font-size="12" fill="#8b857a" text-anchor="middle">the files store the data; Iceberg decides which of them <tspan font-style="italic">are</tspan> the table, right now</text>
  <text x="400" y="292" font-size="12" fill="#8b857a" text-anchor="middle">swap the pointer at the top and the whole table changes atomically</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">Two layers, not two choices: Parquet holds the bytes, Iceberg holds the truth about which bytes count.</figcaption>
</figure>

Because the data files stay immutable Parquet, everything Iceberg adds is
metadata bookkeeping — which is what makes an atomic `MERGE` or a time-travel read
possible on storage that, underneath, is still just Parquet:

```sql
-- The table is Iceberg; the files it writes are Parquet by default.
CREATE TABLE lake.sales.orders (
  order_id BIGINT, order_ts TIMESTAMP, amount DECIMAL(12,2)
) USING iceberg
TBLPROPERTIES ('write.format.default' = 'parquet');   -- the file layer, chosen here

-- Time travel — impossible on bare Parquet, trivial with Iceberg's snapshots.
-- The timestamp must be a literal; Spark rejects non-deterministic expressions here.
SELECT sum(amount) FROM lake.sales.orders
FOR TIMESTAMP AS OF '2026-07-22 00:00:00';
```

Note the `write.format.default` line: the file format is a *table property*.
Iceberg can sit on ORC or Avro instead — Parquet is simply the near-universal
default for analytics. The same properties mechanism carries a more consequential
setting: because those Parquet files are immutable, Iceberg has to decide whether
an update rewrites them or annotates them, which is
[merge-on-read vs copy-on-write](/essays/merge-on-read-vs-copy-on-write/).

## Converting existing Parquet to Iceberg, without rewriting it

This is the question that actually follows the comparison, and most write-ups
skip it: *I already have terabytes of Parquet in object storage. What does
adopting Iceberg cost me?*

Usually far less than people expect, because **Iceberg can adopt files it did not
write.** All three of the standard routes produce metadata rather than data, so
the conversion is measured in minutes rather than in a full rewrite:

```sql
-- 1. Try it first. Creates an independent Iceberg table that SHARES the
--    original files, so the source is untouched and you can query both.
CALL lake.system.snapshot('legacy_db.orders', 'lake.sales.orders_iceberg');

-- 2. Adopt files in place. Reads each Parquet footer for schema and stats,
--    then writes Iceberg metadata pointing at the files where they already are.
CALL lake.system.add_files(
  table       => 'lake.sales.orders',
  source_table => '`parquet`.`s3://bucket/warehouse/orders/`'
);

-- 3. Convert a registered Hive/Spark table in place. The original is retained
--    under a backup name so the change is reversible.
CALL lake.system.migrate('legacy_db.orders');
```

Two caveats worth knowing before you run any of them. `add_files` trusts what the
footers say, so files whose schema drifted from the table definition will fail or
import wrong. And the imported files keep whatever layout they already had — if
the legacy folder is fifty thousand 2 MB files, Iceberg will faithfully record
fifty thousand 2 MB files. Adoption is not compaction. Plan a
`rewrite_data_files` pass afterwards.

## What Iceberg actually costs

Every comparison of these two on the first page of Google is published by a
vendor, and none of them tells you this part. Iceberg is worth adopting, and it
is not free. Four ongoing costs, all of them maintenance you should schedule
rather than discover:

- **Metadata accumulates.** Every commit writes a new metadata file and snapshot.
  Left alone on a busy table, query planning slows as the manifest list grows.
  `expire_snapshots` is not optional housekeeping; it is part of running the table.
- **Small files multiply.** Frequent commits produce many small data files, and
  scan cost tracks file count as much as byte count. This is the same trap as
  [merge-on-read without compaction](/essays/merge-on-read-vs-copy-on-write/).
- **Orphans are left behind.** Failed or cancelled writes leave data files that no
  snapshot references. They cost storage silently until `remove_orphan_files`
  collects them.
- **The catalog becomes a hard dependency.** Bare Parquet has no runtime
  dependency at all: point any reader at the path and it works. An Iceberg table
  cannot be read without the catalog that holds its pointer, which puts that
  component in the write path of every transaction and makes
  [choosing it](/essays/how-to-choose-an-iceberg-catalog/) the decision where
  lock-in now lives.

```sql
-- The maintenance three. Schedule them; don't wait for symptoms.
CALL lake.system.rewrite_data_files(table => 'sales.orders');
CALL lake.system.expire_snapshots(table => 'sales.orders', older_than => TIMESTAMP '2026-07-01 00:00:00');
CALL lake.system.remove_orphan_files(table => 'sales.orders');
```

None of this argues for staying on bare Parquet. It argues for adopting Iceberg
with the maintenance jobs written at the same time as the migration, rather than
six months later when planning latency has quietly tripled.

## So when does the comparison even come up?

It comes up because tutorials and vendor pages talk about "storing data in
Parquet" and "storing data in Iceberg" as if they were alternatives, and they read
as parallel. They aren't. The honest decision tree:

- **Just need efficient files on disk / in object storage?** Parquet, on its own,
  is a complete and excellent answer — for one-off exports, ML feature files,
  archival snapshots, or anything written once and read whole. It has no catalog
  to run, no snapshots to expire, and no maintenance jobs. That is a real
  advantage and it gets undersold because nobody sells Parquet.
- **Need those files to behave as a table** — concurrent writers, safe schema
  changes, updates and deletes, reproducible history? Wrap them in a table format.
  That's the jump from a [data lake](/glossary/data-lake/) to a
  [lakehouse](/glossary/data-lakehouse/), and it's the entire point of an
  [open table format](/essays/what-is-an-open-table-format/).

If your next question is "then which table format" — that's
[Iceberg vs Delta Lake](/essays/iceberg-vs-delta-lake/), a real same-layer choice.
And if it's "which file format underneath" — that's
[Parquet vs ORC vs Avro](/essays/parquet-vs-orc-vs-avro/), or the narrower
[Parquet vs ORC](/essays/parquet-vs-orc/), both real same-layer choices one rung
down. But *Iceberg vs Parquet* isn't a choice at all.
It's two layers of one stack, and the moment you see them stacked instead of
side-by-side, the confusion dissolves.
