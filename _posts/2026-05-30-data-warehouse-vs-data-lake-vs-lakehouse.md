---
title: "Data Warehouse vs Data Lake vs Lakehouse: A Clear Comparison"
kicker: "Field Notes"
topic: "Architecture"
description: "A data warehouse stores structured, modeled data. A data lake stores raw data of any shape, cheaply. A lakehouse tries to be both. Here's a side-by-side comparison, a diagram, and how to choose."
date: 2026-05-30
last_modified_at: 2026-06-20
faq:
  - q: "What is the difference between a data warehouse, a data lake, and a lakehouse?"
    a: "A data warehouse stores structured, modeled data with schema enforced on write, optimized for reliable analytics. A data lake stores raw data of any shape cheaply, with schema applied on read. A lakehouse adds a metadata and table layer over cheap lake storage to deliver warehouse-like reliability on lake economics."
  - q: "Can a lakehouse fully replace a data warehouse?"
    a: "For many teams, yes — open table formats give lake storage the transactions and schema enforcement that BI needs. But a turnkey warehouse is still simpler when your workload is purely structured analytics. Replace only if you genuinely also need lake-style raw and ML workloads."
  - q: "Is a data lake cheaper than a data warehouse?"
    a: "Storage, yes — object storage costs far less per terabyte. Total cost depends on the engineering needed to keep the lake organized and trustworthy; an ungoverned lake saves on storage and pays it back in confusion."
  - q: "What are open table formats like Iceberg and Delta Lake?"
    a: "Metadata layers that sit over files in object storage and add what raw lakes lack: ACID transactions, schema enforcement and evolution, and time travel. They are the technology that makes the lakehouse pattern possible."
---

Three terms get used almost interchangeably and mean genuinely different things. In
one sentence: a **data warehouse** stores structured, modeled data for analytics; a
**data lake** stores raw data of any shape, cheaply; and a **lakehouse** adds a table
layer over cheap lake storage to get warehouse-like reliability on lake economics.
They make opposite bets about structure, cost, and trust — here's the comparison, a
diagram, and how to choose.

## At a glance

| | Data warehouse | Data lake | Lakehouse |
|---|---|---|---|
| **Stores** | Structured, modeled data | Raw data, any shape | Raw data + a table layer |
| **Schema** | On write (enforced up front) | On read (applied later) | On write, over lake files |
| **Storage cost** | Higher | Lowest | Low (object storage) |
| **Reliability** | High (ACID, consistent) | Low (no guarantees) | High (ACID via table formats) |
| **Best for** | Structured BI & reporting | Raw data, ML, flexibility | Both, in one system |
| **Main risk** | Cost & rigidity at scale | Becoming a "data swamp" | Younger, more moving parts |

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
  <!-- Panel 1: Warehouse -->
  <rect x="20" y="54" width="236" height="226" rx="8" fill="#fdfcf9" stroke="#cabfac"/>
  <text x="138" y="44" text-anchor="middle" font-size="13" fill="#c8472b" font-weight="600" letter-spacing="1">WAREHOUSE</text>
  <g>
    <rect x="78" y="96" width="120" height="30" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="78" y="96" width="120" height="9" rx="3" fill="#c8472b" opacity="0.75"/>
    <rect x="78" y="138" width="120" height="30" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="78" y="138" width="120" height="9" rx="3" fill="#c8472b" opacity="0.75"/>
    <rect x="78" y="180" width="120" height="30" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="78" y="180" width="120" height="9" rx="3" fill="#c8472b" opacity="0.75"/>
  </g>
  <text x="138" y="248" text-anchor="middle" font-size="10" fill="#56514a">structured tables</text>
  <text x="138" y="264" text-anchor="middle" font-size="10" fill="#56514a">schema-on-write</text>
  <!-- Panel 2: Lake -->
  <rect x="282" y="54" width="236" height="226" rx="8" fill="#fdfcf9" stroke="#cabfac"/>
  <text x="400" y="44" text-anchor="middle" font-size="13" fill="#c8472b" font-weight="600" letter-spacing="1">DATA LAKE</text>
  <g fill="#e7e1d4" stroke="#cabfac">
    <rect x="318" y="100" width="40" height="26" rx="3"/>
    <rect x="372" y="112" width="34" height="34" rx="17"/>
    <rect x="420" y="98" width="44" height="22" rx="3"/>
    <rect x="332" y="150" width="46" height="30" rx="3"/>
    <rect x="398" y="158" width="30" height="30" rx="3" transform="rotate(45 413 173)"/>
    <rect x="446" y="148" width="38" height="26" rx="3"/>
    <rect x="356" y="196" width="50" height="22" rx="3"/>
  </g>
  <text x="400" y="248" text-anchor="middle" font-size="10" fill="#56514a">raw files, any shape</text>
  <text x="400" y="264" text-anchor="middle" font-size="10" fill="#56514a">schema-on-read · cheap</text>
  <!-- Panel 3: Lakehouse -->
  <rect x="544" y="54" width="236" height="226" rx="8" fill="#fdfcf9" stroke="#cabfac"/>
  <text x="662" y="44" text-anchor="middle" font-size="13" fill="#c8472b" font-weight="600" letter-spacing="1">LAKEHOUSE</text>
  <!-- top: tables -->
  <g>
    <rect x="592" y="92" width="64" height="26" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="592" y="92" width="64" height="8" rx="3" fill="#c8472b" opacity="0.75"/>
    <rect x="668" y="92" width="64" height="26" rx="3" fill="#f0ece2" stroke="#cabfac"/><rect x="668" y="92" width="64" height="8" rx="3" fill="#c8472b" opacity="0.75"/>
  </g>
  <!-- table-format band -->
  <rect x="568" y="134" width="188" height="26" rx="4" fill="#c8472b" opacity="0.14" stroke="#c8472b" stroke-dasharray="3 3"/>
  <text x="662" y="151" text-anchor="middle" font-size="9.5" fill="#a4391f">table format · Iceberg / Delta</text>
  <!-- bottom raw files -->
  <g fill="#e7e1d4" stroke="#cabfac">
    <rect x="586" y="178" width="36" height="22" rx="3"/>
    <rect x="634" y="184" width="26" height="26" rx="13"/>
    <rect x="676" y="176" width="40" height="20" rx="3"/>
    <rect x="606" y="210" width="44" height="18" rx="3"/>
    <rect x="668" y="206" width="34" height="22" rx="3"/>
  </g>
  <text x="662" y="252" text-anchor="middle" font-size="10" fill="#56514a">cheap storage +</text>
  <text x="662" y="266" text-anchor="middle" font-size="10" fill="#56514a">ACID &amp; schema</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#8b857a;margin-top:0.5rem;">The lakehouse keeps the lake's cheap raw storage and adds a table-format layer that gives it a warehouse's structure and guarantees.</figcaption>
</figure>

## Data warehouse: structure first

A data warehouse stores **structured, modeled data**, cleaned and fitted to a schema
*before* it lands — an approach called schema-on-write. This is the world of
[dimensional models](/essays/a-field-guide-to-dimensional-modeling/) and
[star schemas](/essays/star-schema-vs-snowflake-schema/). Its value is **trust and
speed for analytics**: because everything is modeled and typed up front, queries are
fast, results are consistent, and a BI tool gets reliable answers without thinking
about plumbing. The costs are upfront modeling effort, rigidity afterward, and — for
traditional designs — expensive coupled storage and compute that suit structured data
far better than huge volumes of raw logs, text, or images.

## Data lake: flexibility first

A data lake makes the opposite bet: store **raw data of any shape** — structured,
semi-structured, unstructured — as files in cheap object storage, with structure
applied later, on read. This buys **cost** (object storage is cheap, so you keep
enormous volumes affordably) and **flexibility** (dump data in now, decide what to do
with it later), which suits data science and ML. But with no enforced schema, no
guaranteed quality, and often no clear ownership, a lake can rot into a **data
swamp** — a vast pile of files nobody trusts. It also lacks transactional guarantees,
which makes reliable, concurrent analytics hard.

## Lakehouse: both

The lakehouse keeps your data in cheap object storage as files — the lake part — but
adds a **metadata and table layer** on top that brings the structure and guarantees a
warehouse has. That layer is delivered by **open table formats** — Apache Iceberg,
Delta Lake, Apache Hudi — which provide what raw lakes lacked: ACID transactions,
schema enforcement and evolution, and time travel. The result is one system that runs
both flexible ML-style workloads *and* reliable structured BI, without maintaining a
separate lake and warehouse with a brittle pipeline copying between them. The
trade-off is **maturity and complexity** — a younger stack with more moving parts than
a turnkey warehouse.

## When to choose each

- **Choose a warehouse** when your work is overwhelmingly structured analytics and BI,
  you value simplicity and reliability over flexibility, and volumes are manageable.
  For a team that mostly builds dashboards, a warehouse is still the simplest, most
  dependable answer — don't over-engineer past it.
- **Choose a lake** when you have large volumes of raw, varied, or unstructured data,
  heavy ML needs, and the discipline to stop it becoming a swamp. Rarely the whole
  answer on its own anymore.
- **Choose a lakehouse** when you genuinely need both — structured BI *and* raw/ML on
  the same large datasets — and want to avoid running two systems with a sync pipeline
  between them. This is where many teams are converging.

If your decision is specifically between the lake and the lakehouse — the most common
modern version of this question — that finer comparison has [its own
deep-dive](/essays/data-lake-vs-lakehouse/).

## The part none of them solve

Whichever you pick, it answers *where data is stored and how it's structured* — a
physical question. None of the three tells you what your data *means*: which
definition of "revenue" is canonical, who owns the customer table, how "active user"
is defined. That's the job of a [semantic layer](/essays/what-is-a-semantic-layer/),
which sits above all three. Teams often expect a shiny new lakehouse to fix their
consistency problems and are surprised when the same three-different-numbers arguments
continue — because storage was never what caused them. Choose the right store for your
workload; then govern the meaning on top of it. They're different problems, and you
need answers to both.
