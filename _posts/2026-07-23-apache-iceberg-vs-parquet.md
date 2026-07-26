---
title: "Apache Iceberg vs Parquet: They're Not the Same Layer"
kicker: "Field Notes"
topic: "Architecture"
description: "Iceberg and Parquet aren't rivals — Parquet is a file format, Iceberg is a table format that manages Parquet files. Here's the difference, and why it matters."
date: 2026-07-23 09:00:00 +0530
last_modified_at: 2026-07-26
faq:
  - q: "What is the difference between Apache Iceberg and Parquet?"
    a: "Parquet is a file format — it defines how the bytes of a single file are laid out on disk, column by column, compressed. Apache Iceberg is a table format — it defines how many files together form one logical table, tracking which files are current, what schema applies, and how changes commit atomically. Iceberg tables are almost always made of Parquet files, so it's not a choice between them; it's two layers of the same stack."
  - q: "Do I use Iceberg or Parquet?"
    a: "Usually both, together. You store your data as Parquet files for efficient columnar compression and scanning, and you put Iceberg on top to turn a folder of those files into a real table with ACID transactions, schema evolution, and time travel. Choosing 'Parquet or Iceberg' is like choosing 'pages or a book' — the book is made of pages."
  - q: "Can Iceberg use file formats other than Parquet?"
    a: "Yes. The Iceberg spec supports Parquet, ORC, and Avro as underlying data files, and the choice is configurable per table. Parquet is the overwhelmingly common default for analytical workloads, but Iceberg's design deliberately separates the table layer from the file layer, so the file format is a swappable implementation detail."
  - q: "Is Parquet being replaced by Iceberg?"
    a: "No — Iceberg makes Parquet more useful, not obsolete. Iceberg needs a file format underneath it to actually store the rows, and Parquet is the one it reaches for most. The trend isn't Parquet being replaced; it's bare folders of Parquet files being wrapped in a table format so they behave like databases."
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
those two, and columns of like values compress far better than mixed rows. On a
[benchmark run for this site](/essays/parquet-vs-orc-vs-avro-benchmark/), that
came to 6.1× smaller than the equivalent CSV and a filtered aggregation 13.8×
faster — the shape of every [OLAP](/glossary/olap/) query there is.

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
<svg viewBox="0 0 800 320" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="apache-iceberg-vs-parquet-t apache-iceberg-vs-parquet-d">
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

## So when does the comparison even come up?

It comes up because tutorials and vendor pages talk about "storing data in
Parquet" and "storing data in Iceberg" as if they were alternatives, and they read
as parallel. They aren't. The honest decision tree:

- **Just need efficient files on disk / in object storage?** Parquet, on its own,
  is a complete and excellent answer — for one-off exports, ML feature files, or
  data you'll read as a whole.
- **Need those files to behave as a table** — concurrent writers, safe schema
  changes, updates and deletes, reproducible history? Wrap them in a table format.
  That's the jump from a [data lake](/glossary/data-lake/) to a
  [lakehouse](/glossary/data-lakehouse/), and it's the entire point of an
  [open table format](/essays/what-is-an-open-table-format/).

If your next question is "then which table format" — that's
[Iceberg vs Delta Lake](/essays/iceberg-vs-delta-lake/), a real same-layer choice.
And if it's "which file format underneath" — that's
[Parquet vs ORC vs Avro](/essays/parquet-vs-orc-vs-avro/), a real same-layer
choice one rung down. But *Iceberg vs Parquet* isn't a choice at all.
It's two layers of one stack, and the moment you see them stacked instead of
side-by-side, the confusion dissolves.
