---
layout: page
title: "Start here"
kicker: "Reading paths"
permalink: /start-here/
description: "Curated reading paths through the essays: dimensional modeling, the lakehouse, pipelines and the craft, in the order that builds understanding."
---

This site is a working reference on data architecture, and references read best
in order. Below are four paths through the essays, each sequenced so that every
piece builds on the one before it. Pick the one that matches your question — or
start at the top and treat it as a course.

If you want lookups rather than essays: the
[glossary](/glossary/) defines the vocabulary in a paragraph each, and the
[patterns catalog](/patterns/) is a structured reference of the major
architectures with honest trade-offs.

## Path 1 — Dimensional modeling, from zero

The foundation. How analytical data is shaped, and why the fifty-year-old ideas
still run most analytics on earth.

1. [A field guide to dimensional modeling](/essays/a-field-guide-to-dimensional-modeling/) — the three ideas that carry everything.
2. [Fact table vs dimension table](/essays/fact-table-vs-dimension-table/) — measurements versus context, made concrete.
3. [The grain of a fact table](/essays/fact-table-grain/) — the first decision that decides everything else.
4. [Star schema vs snowflake schema](/essays/star-schema-vs-snowflake-schema/) — the shape debate, settled in one decision.
5. [Slowly changing dimensions, explained](/essays/slowly-changing-dimensions-explained/) — what to do when context changes.
6. [The three types of fact table](/essays/fact-table-types/) — transaction, snapshot, accumulating.

Then, when the fundamentals feel solid:
[conformed dimensions](/essays/conformed-dimensions/),
[surrogate vs natural keys](/essays/surrogate-keys-vs-natural-keys/), and the
modern argument —
[one big table vs the star schema](/essays/one-big-table-vs-star-schema/).

## Path 2 — Warehouse, lake, lakehouse

Where data should live, and what the storage wars were actually about.

1. [Data warehouse vs data lake vs lakehouse](/essays/data-warehouse-vs-data-lake-vs-lakehouse/) — the map of the whole territory.
2. [Data lake vs lakehouse](/essays/data-lake-vs-lakehouse/) — the one missing ingredient.
3. [What is an open table format?](/essays/what-is-an-open-table-format/) — that ingredient, examined.
4. [The medallion architecture, reconsidered](/essays/the-medallion-architecture-reconsidered/) — the default layering, and where it quietly fails.

## Path 3 — Pipelines that don't wake you up

How data moves, and the properties that make moving it boring.

1. [ETL vs ELT](/essays/etl-vs-elt/) — where transformation belongs.
2. [What is change data capture?](/essays/what-is-change-data-capture/) — reading the log instead of polling the tables.
3. [How to make a data pipeline idempotent](/essays/how-to-make-a-data-pipeline-idempotent/) — the property that makes retries safe.
4. [Batch vs streaming](/essays/batch-vs-streaming/) — the latency spectrum, honestly priced.

## Path 4 — The craft and the org chart

The opinions. Why most data problems aren't technology problems.

1. [The shape of data](/essays/the-shape-of-data/) — the founding essay.
2. [Data contracts are a cultural problem](/essays/data-contracts-are-a-cultural-problem/) — the YAML is the easy part.
3. [Data quality problems are org chart problems](/essays/data-quality-problems-are-org-chart-problems/) — same thesis, sharper edge.
4. [What does a data architect do?](/essays/what-does-a-data-architect-do/) — the role, and [how it differs from the ones next to it](/essays/data-engineer-vs-data-architect-vs-analytics-engineer/).

## For the AI-curious

[What GenAI changes about data architecture](/essays/what-genai-changes-about-data-architecture/),
[your AI is only as good as your data architecture](/essays/your-ai-is-only-as-good-as-your-data-architecture/),
[what is a vector database?](/essays/what-is-a-vector-database/), and
[what is a semantic layer?](/essays/what-is-a-semantic-layer/) — the last one
being, quietly, the most important of the four.
