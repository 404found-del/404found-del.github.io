---
title: "The Inmon Methodology: The Corporate Information Factory, with an Example"
kicker: "Field Notes"
topic: "Architecture"
description: "Inmon's method builds one normalized enterprise warehouse first, then serves dimensional marts from it. How the CIF works, a worked example, and where it fits today."
date: 2026-07-17 09:00:00 +0530
faq:
  - q: "What is the Inmon methodology in simple terms?"
    a: "Build the enterprise data warehouse first, as a normalized (3NF) integration of all source systems — the single version of the truth — and only then derive department-facing data marts from it, usually as star schemas. Top-down: integrate once, serve many. Kimball inverts this, building dimensional marts first."
  - q: "What is the Corporate Information Factory (CIF)?"
    a: "Inmon's name for the full architecture around the warehouse: source systems feed staging, staging feeds the normalized enterprise warehouse, and the warehouse feeds dependent data marts, exploration warehouses, and operational data stores. The EDW sits at the centre as the integrated system of record for analytics."
  - q: "Why does Inmon insist on a normalized warehouse?"
    a: "Because the integration layer's job is correctness under change, not query speed. Third normal form stores each fact once, absorbs new sources and relationships gracefully, and avoids baking any department's query patterns into the enterprise's single copy of history. Read performance is the marts' job, downstream."
  - q: "Is the Inmon approach still relevant in the lakehouse era?"
    a: "The vocabulary aged; the idea won. An integrated, governed layer that serves consumer-facing models downstream is exactly what a lakehouse's silver and gold layers do — and data vault is essentially an Inmon-style integration layer rebuilt for volatile sources. Few teams build a strict CIF today, but most modern architectures are Inmon-shaped."
---

Bill Inmon's methodology — the **top-down** approach, the **Corporate Information
Factory (CIF)** — answers one question before all others: *what does the
enterprise's single version of the truth look like?* His answer: build the
**enterprise data warehouse (EDW)** first, as a **normalized (3NF)**, integrated,
historical store of everything the business does — and only then derive the
department-facing **data marts** (usually [star schemas](/patterns/star-schema/))
from it. Integrate once, upstream; serve many, downstream. Kimball famously
inverts the order, and that inversion is
[the whole debate](/essays/kimball-vs-inmon/) — but to evaluate it fairly you
have to understand what Inmon's method actually builds, and most summaries
don't. Here it is, with an example.

## The architecture: what the CIF actually is

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 330" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
  <rect x="30" y="40" width="130" height="44" rx="6" fill="#1c1a17"/>
  <text x="95" y="67" font-size="12" fill="#f6f3ec" text-anchor="middle">orders app</text>
  <rect x="30" y="104" width="130" height="44" rx="6" fill="#1c1a17"/>
  <text x="95" y="131" font-size="12" fill="#f6f3ec" text-anchor="middle">CRM</text>
  <rect x="30" y="168" width="130" height="44" rx="6" fill="#1c1a17"/>
  <text x="95" y="195" font-size="12" fill="#f6f3ec" text-anchor="middle">billing</text>
  <line x1="160" y1="62" x2="230" y2="115" stroke="#cabfac" stroke-width="2"/>
  <line x1="160" y1="126" x2="230" y2="126" stroke="#cabfac" stroke-width="2"/>
  <line x1="160" y1="190" x2="230" y2="140" stroke="#cabfac" stroke-width="2"/>
  <rect x="230" y="96" width="120" height="60" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="290" y="122" font-size="12" fill="#1c1a17" text-anchor="middle">staging /</text>
  <text x="290" y="140" font-size="12" fill="#1c1a17" text-anchor="middle">integration</text>
  <line x1="350" y1="126" x2="410" y2="126" stroke="#cabfac" stroke-width="2"/>
  <rect x="410" y="76" width="170" height="100" rx="6" fill="#c8472b"/>
  <text x="495" y="112" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">EDW — 3NF</text>
  <text x="495" y="134" font-size="11" fill="#f6f3ec" text-anchor="middle">integrated, historical,</text>
  <text x="495" y="152" font-size="11" fill="#f6f3ec" text-anchor="middle">single version of truth</text>
  <line x1="580" y1="100" x2="650" y2="60" stroke="#cabfac" stroke-width="2"/>
  <line x1="580" y1="126" x2="650" y2="126" stroke="#cabfac" stroke-width="2"/>
  <line x1="580" y1="152" x2="650" y2="192" stroke="#cabfac" stroke-width="2"/>
  <rect x="650" y="38" width="120" height="44" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="710" y="65" font-size="11" fill="#1c1a17" text-anchor="middle">sales mart ★</text>
  <rect x="650" y="104" width="120" height="44" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="710" y="131" font-size="11" fill="#1c1a17" text-anchor="middle">finance mart ★</text>
  <rect x="650" y="170" width="120" height="44" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="710" y="197" font-size="11" fill="#1c1a17" text-anchor="middle">marketing mart ★</text>
  <text x="400" y="280" font-size="12" fill="#8b857a" text-anchor="middle">the CIF: integrate everything into a normalized EDW first; marts are derived, dependent views</text>
  <text x="400" y="302" font-size="12" fill="#8b857a" text-anchor="middle">★ = dimensional star schemas — Inmon and Kimball agree on the serving layer's shape</text>
</svg>
</figure>

Four properties define the EDW at the centre, in Inmon's own terms: it is
**subject-oriented** (organised by business concept — customer, product, order —
not by source system), **integrated** (one customer definition, reconciled from
every system that disagrees), **non-volatile** (loaded, never edited in place),
and **time-variant** (history is kept, not overwritten). The marts downstream
are *dependent*: they contain nothing that isn't derived from the EDW, which is
what makes every department's numbers reconcilable by construction.

## A worked example

A retailer has three sources that all disagree about customers: the orders app
(customer as email), the CRM (customer as lead with a salesperson's spelling),
and billing (customer as account number). The Inmon move is to model the
*enterprise* concept once, normalized:

```sql
-- EDW, 3NF: each fact stored once, relationships explicit
CREATE TABLE edw.customer (
  customer_id     BIGINT PRIMARY KEY,     -- enterprise key, not any source's
  legal_name      TEXT NOT NULL
);
CREATE TABLE edw.customer_identifier (    -- every source's ID maps here
  customer_id     BIGINT REFERENCES edw.customer,
  source_system   TEXT,                   -- 'orders' | 'crm' | 'billing'
  source_key      TEXT,
  PRIMARY KEY (source_system, source_key)
);
CREATE TABLE edw.customer_address (       -- history, not overwrite
  customer_id     BIGINT REFERENCES edw.customer,
  address_type    TEXT,
  valid_from      DATE,
  valid_to        DATE,
  city            TEXT
);
```

Note what this is *not*: it's not queryable comfort. Answering "revenue by city
last quarter" against 3NF means a pile of joins. That's deliberate — the EDW
optimizes for integration and change-absorption
([normalization's actual job](/essays/normalization-vs-denormalization/)), and
the sales mart derived from it flattens everything into a star for analysts.
Correctness upstream, speed downstream.

## Trade-offs, honestly

**What the method buys:** one reconciled truth, marts that agree by
construction, resilience to source churn, audit-friendly history.
**What it costs:** the up-front integration effort is enormous, value arrives
late (the business waits while you model the enterprise), and it demands
sustained political will — the hardest part of "one customer definition" was
never the SQL. This is precisely the cost profile
[Kimball's bottom-up method](/essays/kimball-vs-inmon/) was designed to avoid,
at the price of integration debt later.

## Where it stands today

Strict CIFs are rare now, but squint at a modern platform and the shape is
everywhere: the silver layer of a
[medallion lakehouse](/patterns/medallion-architecture/) is an integration layer
serving derived gold marts; [data vault](/patterns/data-vault/) is an
Inmon-style integration layer re-engineered for volatile sources; even
[warehouse-vs-lakehouse](/essays/data-warehouse-vs-data-lake-vs-lakehouse/)
debates assume an integrated layer feeding consumer models. Inmon lost the
vocabulary war and won the architecture. Understanding his method is
understanding why your platform is shaped the way it is.
