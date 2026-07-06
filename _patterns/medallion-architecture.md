---
title: "Medallion Architecture"
intent: "Organise a lakehouse into layers of increasing refinement and trust: bronze (raw), silver (cleaned), gold (consumable)."
description: "The medallion architecture pattern: structure, the problems each layer solves, honest trade-offs, and the situations where bronze/silver/gold is the wrong default."
essays:
  - the-medallion-architecture-reconsidered
  - data-lake-vs-lakehouse
  - how-to-make-a-data-pipeline-idempotent
---

## Intent

Give a sprawling lakehouse a default shape: land data raw and immutable
(**bronze**), standardise and deduplicate it (**silver**), and serve
business-ready, modelled data (**gold**). Each layer has one job, and trust
increases as data moves right.

## Context

You're building on a [lakehouse](/essays/data-lake-vs-lakehouse/) — cheap object
storage with an [open table format](/patterns/lakehouse/) — and many teams land,
transform, and consume data in the same platform. Without a convention, pipelines
read from arbitrary points and every incident becomes archaeology.

## Structure

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 220" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
  <rect x="30" y="60" width="200" height="100" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="130" y="100" font-size="16" fill="#1c1a17" text-anchor="middle" font-weight="700">Bronze</text>
  <text x="130" y="126" font-size="12" fill="#56514a" text-anchor="middle">raw, immutable,</text>
  <text x="130" y="144" font-size="12" fill="#56514a" text-anchor="middle">replayable history</text>
  <line x1="230" y1="110" x2="290" y2="110" stroke="#cabfac" stroke-width="2"/>
  <rect x="290" y="60" width="200" height="100" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="390" y="100" font-size="16" fill="#1c1a17" text-anchor="middle" font-weight="700">Silver</text>
  <text x="390" y="126" font-size="12" fill="#56514a" text-anchor="middle">cleaned, conformed,</text>
  <text x="390" y="144" font-size="12" fill="#56514a" text-anchor="middle">deduplicated</text>
  <line x1="490" y1="110" x2="550" y2="110" stroke="#cabfac" stroke-width="2"/>
  <rect x="550" y="60" width="200" height="100" rx="6" fill="#c8472b"/>
  <text x="650" y="100" font-size="16" fill="#f6f3ec" text-anchor="middle" font-weight="700">Gold</text>
  <text x="650" y="126" font-size="12" fill="#f6f3ec" text-anchor="middle">modelled, aggregated,</text>
  <text x="650" y="144" font-size="12" fill="#f6f3ec" text-anchor="middle">consumer-facing</text>
  <text x="400" y="200" font-size="12" fill="#8b857a" text-anchor="middle">trust and refinement increase left to right; consumers read only gold</text>
</svg>
</figure>

Bronze stores data exactly as ingested, append-only, so any downstream table can
be rebuilt by replay — which is also what makes
[idempotent pipelines](/essays/how-to-make-a-data-pipeline-idempotent/) practical.
Silver applies types, deduplication, and conformance. Gold holds dimensional
models or aggregates that consumers actually query.

## Trade-offs

**Gains:** provenance (raw history survives), a shared vocabulary across teams,
clear blast-radius when a pipeline fails, and a natural place to enforce quality
gates between layers.

**Costs:** three copies of much of your data; latency added at every hop; and a
false sense of completion — the layers say nothing about *modelling*, ownership,
or definitions, which is where warehouses actually fail. Teams routinely ship a
perfect bronze/silver/gold pipeline that still delivers numbers nobody trusts.

## When not to use it

Skip or collapse the layers when the source is already clean and structured (a
CDC feed of a well-modelled OLTP system may not need a separate silver), when
latency budgets are tight, or when the team is small enough that convention
overhead outweighs archaeology risk. The layer count is a default, not a law —
what matters is immutable raw history plus a declared, modelled serving layer.
