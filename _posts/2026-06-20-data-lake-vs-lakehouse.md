---
title: "Data Lake vs Lakehouse: What Changed and Which to Use"
kicker: "Field Notes"
topic: "Architecture"
description: "A data lake stores raw files cheaply and guarantees nothing. A lakehouse adds a table layer over the same files for ACID, schema, and trust. When each fits."
date: 2026-06-20 10:00:00 +0530
last_modified_at: 2026-08-29
faq:
  - q: "What is the difference between a data lake and a lakehouse?"
    a: "A data lake is raw files in cheap object storage with no transactions, no enforced schema, and no guarantees. A lakehouse keeps those same files but adds an open table format on top — Iceberg, Delta Lake, or Hudi — that provides ACID transactions, schema enforcement, and time travel. The lakehouse is a data lake plus a table layer."
  - q: "Is a lakehouse just a data lake with extra features?"
    a: "Essentially, yes — and that's the point. The lakehouse doesn't replace the lake's cheap file storage; it layers metadata over it so the same data gains the reliability and structure that analytics needs, without copying everything into a separate warehouse."
  - q: "What is a data swamp?"
    a: "A data lake that has degraded into an unusable pile of files — no consistent schema, no quality, no clear ownership, so nobody trusts what's in it. The lack of structure and governance that makes a lake cheap and flexible is also what lets it rot."
  - q: "Do I still need a data lake if I have a lakehouse?"
    a: "No — the lakehouse is built on lake storage, so it is your lake, with a table layer added. You don't run both. You may still keep a raw, untabled zone for landing data before it's promoted into managed tables."
---

The most common version of the storage question today isn't warehouse-versus-anything
: **data lake versus lakehouse.** The short answer: a data lake stores raw files
cheaply but gives you no guarantees about them; a lakehouse keeps those *same* files
and adds a table layer on top that brings transactions, schema, and reliability. The
lakehouse is, almost literally, a data lake plus one missing ingredient. Here's what
that ingredient is, why it changed everything, and when a plain lake is still enough.

## Lake vs lakehouse, at a glance

| | Data lake | Lakehouse |
|---|---|---|
| **Storage** | Raw files, object storage | Raw files, object storage (same) |
| **Transactions** | None | ACID, via table formats |
| **Schema** | On read, unenforced | Enforced, with evolution |
| **Concurrent writes** | Unsafe | Safe |
| **Time travel / history** | No | Yes |
| **Reliability for BI** | Low | High |
| **Main risk** | Becoming a data swamp | Younger, more moving parts |

## What a data lake is, and where it breaks

A data lake is a large store of **raw files in cheap object storage**. You land data of
any shape (tables, JSON, logs, images) as files, and apply structure later, on read.
This is genuinely useful: storage is cheap, so you keep enormous volumes affordably,
and you don't have to model anything up front, which suits data science and ML.

The problem is everything a bare pile of files *doesn't* give you. There are **no
transactions**, so two jobs writing at once can leave data half-updated and corrupt.
There is **no enforced schema**, so a malformed file silently poisons downstream reads.
There is **no reliable history**, so you can't cleanly reproduce yesterday's numbers.
Absent quality checks and ownership, the lake drifts into a **data swamp**: a vast
store nobody trusts. The very looseness that makes a lake cheap and flexible is what
lets it rot.

## What a lakehouse adds: the table format

The lakehouse fixes this without giving up cheap storage. It keeps your data as files
in object storage and adds a **metadata layer on top**: an
[*open table format*](/essays/what-is-an-open-table-format/) such as
[Apache Iceberg](/glossary/apache-iceberg/), [Delta Lake](/glossary/delta-lake/), or Apache Hudi. That layer tracks which files make up a
table, in what version, under what schema, and in doing so retrofits the guarantees a
lake never had.

<figure style="margin:2rem auto;text-align:center;">
<svg class="dia-mob" viewBox="0 0 400 600" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="dlvl-mt dlvl-md">
  <title id="dlvl-mt">Data lake versus lakehouse</title>
  <desc id="dlvl-md">The same object-storage files shown twice, one above the other: first as a bare lake of files with no transactions, schema or guarantees, and below with an open table format layered on top that turns the same pile of cheap files into reliable, versioned, transactional tables.</desc>
  <text x="200" y="24" text-anchor="middle" font-size="13" fill="#c8472b" font-weight="600" letter-spacing="1">DATA LAKE</text>
  <rect x="20" y="36" width="360" height="184" rx="8" fill="#fdfcf9" stroke="#cabfac"/>
  <g fill="#e7e1d4" stroke="#cabfac">
    <rect x="60" y="70" width="56" height="30" rx="3"/>
    <rect x="140" y="76" width="38" height="38" rx="19"/>
    <rect x="204" y="66" width="62" height="26" rx="3"/>
    <rect x="290" y="74" width="46" height="30" rx="3"/>
    <rect x="70" y="124" width="52" height="34" rx="3" transform="rotate(45 96 141)"/>
    <rect x="152" y="130" width="66" height="30" rx="3"/>
    <rect x="244" y="124" width="46" height="32" rx="3"/>
    <rect x="86" y="176" width="66" height="24" rx="3"/>
    <rect x="180" y="172" width="50" height="28" rx="3"/>
    <rect x="258" y="176" width="58" height="24" rx="3"/>
  </g>
  <text x="200" y="244" text-anchor="middle" font-size="10" fill="#56514a">just files — no transactions,</text>
  <text x="200" y="260" text-anchor="middle" font-size="10" fill="#56514a">no schema, no guarantees</text>
  <text x="200" y="298" text-anchor="middle" font-size="22" fill="#cabfac">↓</text>
  <text x="200" y="336" text-anchor="middle" font-size="13" fill="#c8472b" font-weight="600" letter-spacing="1">LAKEHOUSE</text>
  <rect x="20" y="348" width="360" height="196" rx="8" fill="#fdfcf9" stroke="#cabfac"/>
  <rect x="44" y="366" width="312" height="30" rx="4" fill="#c8472b" opacity="0.14" stroke="#c8472b" stroke-dasharray="3 3"/>
  <text x="200" y="385" text-anchor="middle" font-size="10" fill="#a4391f">table format: ACID · schema · time travel</text>
  <g>
    <rect x="52" y="412" width="94" height="28" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="52" y="412" width="94" height="8" rx="3" fill="#c8472b" opacity="0.7"/>
    <rect x="156" y="412" width="94" height="28" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="156" y="412" width="94" height="8" rx="3" fill="#c8472b" opacity="0.7"/>
    <rect x="260" y="412" width="90" height="28" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="260" y="412" width="90" height="8" rx="3" fill="#c8472b" opacity="0.7"/>
  </g>
  <g fill="#e7e1d4" stroke="#cabfac">
    <rect x="56" y="464" width="48" height="24" rx="3"/>
    <rect x="120" y="466" width="30" height="30" rx="15"/>
    <rect x="168" y="462" width="54" height="22" rx="3"/>
    <rect x="240" y="464" width="52" height="26" rx="3"/>
    <rect x="308" y="466" width="44" height="24" rx="3"/>
    <rect x="82" y="502" width="56" height="20" rx="3"/>
    <rect x="158" y="500" width="44" height="24" rx="3"/>
    <rect x="222" y="502" width="58" height="20" rx="3"/>
    <rect x="300" y="500" width="52" height="24" rx="3"/>
  </g>
  <text x="200" y="568" text-anchor="middle" font-size="10" fill="#56514a">same cheap files + a metadata</text>
  <text x="200" y="584" text-anchor="middle" font-size="10" fill="#56514a">layer that makes them tables</text>
</svg>
<svg class="dia-desk" viewBox="0 0 760 320" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="data-lake-vs-lakehouse-t data-lake-vs-lakehouse-d">
  <title id="data-lake-vs-lakehouse-t">Data lake versus lakehouse</title>
  <desc id="data-lake-vs-lakehouse-d">The same object-storage files shown twice: as a bare lake of files, and with an open table format layered on top that turns the pile into reliable, versioned, transactional tables.</desc>
  <text x="180" y="34" text-anchor="middle" font-size="13" fill="#c8472b" font-weight="600" letter-spacing="1">DATA LAKE</text>
  <text x="565" y="34" text-anchor="middle" font-size="13" fill="#c8472b" font-weight="600" letter-spacing="1">LAKEHOUSE</text>
  <!-- LAKE panel -->
  <rect x="40" y="52" width="280" height="234" rx="8" fill="#fdfcf9" stroke="#cabfac"/>
  <g fill="#e7e1d4" stroke="#cabfac">
    <rect x="78" y="96" width="48" height="30" rx="3"/>
    <rect x="146" y="108" width="40" height="40" rx="20"/>
    <rect x="208" y="92" width="54" height="26" rx="3"/>
    <rect x="92" y="150" width="44" height="38" rx="3" transform="rotate(45 114 169)"/>
    <rect x="170" y="158" width="58" height="30" rx="3"/>
    <rect x="244" y="150" width="40" height="30" rx="3"/>
    <rect x="100" y="208" width="60" height="24" rx="3"/>
    <rect x="186" y="206" width="44" height="28" rx="3"/>
  </g>
  <text x="180" y="262" text-anchor="middle" font-size="10" fill="#56514a">just files — no transactions,</text>
  <text x="180" y="277" text-anchor="middle" font-size="10" fill="#56514a">no schema, no guarantees</text>
  <!-- arrow -->
  <text x="370" y="174" text-anchor="middle" font-size="22" fill="#cabfac">→</text>
  <!-- LAKEHOUSE panel -->
  <rect x="420" y="52" width="300" height="234" rx="8" fill="#fdfcf9" stroke="#cabfac"/>
  <!-- table-format layer -->
  <rect x="446" y="78" width="248" height="30" rx="4" fill="#c8472b" opacity="0.14" stroke="#c8472b" stroke-dasharray="3 3"/>
  <text x="570" y="97" text-anchor="middle" font-size="10" fill="#a4391f">table format: ACID · schema · time travel</text>
  <!-- structured tables emerging -->
  <g>
    <rect x="470" y="124" width="74" height="26" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="470" y="124" width="74" height="8" rx="3" fill="#c8472b" opacity="0.7"/>
    <rect x="560" y="124" width="74" height="26" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="560" y="124" width="74" height="8" rx="3" fill="#c8472b" opacity="0.7"/>
    <rect x="648" y="124" width="46" height="26" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="648" y="124" width="46" height="8" rx="3" fill="#c8472b" opacity="0.7"/>
  </g>
  <!-- same raw files underneath -->
  <g fill="#e7e1d4" stroke="#cabfac">
    <rect x="470" y="170" width="40" height="24" rx="3"/>
    <rect x="522" y="176" width="30" height="30" rx="15"/>
    <rect x="566" y="168" width="46" height="22" rx="3"/>
    <rect x="492" y="206" width="48" height="20" rx="3"/>
    <rect x="556" y="202" width="38" height="24" rx="3"/>
    <rect x="612" y="172" width="44" height="26" rx="3"/>
    <rect x="624" y="206" width="48" height="20" rx="3"/>
  </g>
  <text x="570" y="262" text-anchor="middle" font-size="10" fill="#56514a">same cheap files +</text>
  <text x="570" y="277" text-anchor="middle" font-size="10" fill="#56514a">a metadata layer that makes them tables</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#8b857a;margin-top:0.5rem;">A lakehouse is the same lake storage with an open table format layered on top — turning a pile of files into reliable, versioned tables.</figcaption>
</figure>

Concretely, the table format gives you **ACID transactions** (writes are all-or-nothing,
so concurrent jobs can't corrupt a table), **schema enforcement and evolution** (bad
data is rejected, and columns can change safely over time), and **time travel** (every
change is versioned, so you can query the table as it was at any past point and
reproduce old results exactly). None of that requires moving the data; it's
*metadata over the files you already have.* That's the whole trick, and it's why the
lakehouse arrived as an evolution of the lake rather than a replacement for it.

## A worked scenario

Picture a nightly job rewriting an `orders` table while a dashboard queries it. **On a
plain lake**, the dashboard can read a half-written state (some new files present,
some old ones already deleted) and return numbers that never actually existed. There's
no concept of a transaction to hide the in-progress write. **On a lakehouse**, the table
format makes the rewrite a single atomic commit: the dashboard sees either the
complete old version or the complete new one, never a torn mixture. Same files, same
storage cost, but now the read is trustworthy. That gap is the entire reason
lakehouses exist.

## When a plain lake is still enough

You don't always need the table layer. A bare lake is fine when you're **landing raw
data** that will be processed downstream anyway, doing **exploratory data science**
where occasional inconsistency is acceptable, or **archiving** large volumes cheaply.
In fact, most lakehouses keep a raw, untabled landing zone, the immutable bottom of
[the medallion architecture](/essays/the-medallion-architecture-reconsidered/), and
promote data into managed tables only as it's cleaned and trusted.

What you should *not* do is run reliable, concurrent **BI and analytics directly on a
bare lake** and expect warehouse-grade trust. That's precisely the workload the table
format was invented for, and skipping it is how teams end up debugging numbers that
quietly changed mid-query.

## The bottom line

If you want the original argument rather than the marketing version of it, the
2021 CIDR paper
[*Lakehouse: A New Generation of Open Platforms*](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)
is where the term was formalised, complete with the TPC-DS numbers its authors
put behind the claim.

A data lake gives you cheap, flexible storage and no guarantees. A lakehouse keeps the
cheap, flexible storage and adds the guarantees, through an [open table format](/glossary/open-table-format/) layered
over the same files. For most teams doing serious analytics on large data, the
lakehouse is now the default, because it removes the lake's biggest liability, trust,
at almost no extra storage cost. Keep a raw zone for landing and exploration; put a
table format over anything you actually want to depend on. And remember that, like
[every storage choice](/essays/data-warehouse-vs-data-lake-vs-lakehouse/), it decides
where your data lives and how reliable it is, not what it *means*, which is still a
[semantic-layer](/essays/what-is-a-semantic-layer/) problem sitting one level up.
