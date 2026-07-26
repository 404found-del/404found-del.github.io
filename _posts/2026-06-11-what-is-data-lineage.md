---
title: "What Is Data Lineage, and What Is It Actually For?"
kicker: "Field Notes"
topic: "Governance"
description: "Data lineage is the record of where data comes from, how it's transformed, and where it goes. Here's what it's genuinely for — impact analysis, root cause, audit — and the limits the tool demos skip."
date: 2026-06-11
last_modified_at: 2026-07-26
faq:
  - q: "What is data lineage in simple terms?"
    a: "The traced path of data through your systems: where each field came from, what transformed it along the way, and which tables, dashboards, and models depend on it downstream. It answers 'can I trust this number?' backward and 'what breaks if I change this?' forward."
  - q: "How is data lineage captured?"
    a: "Mostly automatically: parsing SQL from transformation code, reading orchestrator metadata, and mining warehouse query logs. Column-level lineage — which specific fields feed which — is the useful granularity, and it's typically surfaced in a data catalog rather than as a standalone tool."
  - q: "What is data lineage actually used for?"
    a: "Three things earn its keep: impact analysis before schema changes (what breaks downstream), root-cause during incidents (what fed this wrong number), and audit evidence (prove where a regulated figure came from). If none of those are live problems, lineage tooling can wait; the problems usually arrive with scale."
---

Data lineage is the family tree of your data: a record of where each dataset comes
from, what transformations it passes through, and everything downstream that depends
on it. Pick any column in the warehouse and lineage answers two directions of
question — *upstream*, where did this come from and what shaped it; *downstream*,
what would break if I changed it. Simple idea, genuinely valuable, and currently
sold with enough mystique that it's worth stating plainly what it's for and what it
cannot do.

## The two questions it answers

**Downstream: blast radius.** You want to drop a column, change a type, refactor a
model. Lineage tells you every table, dashboard, and consumer that transitively
depends on the thing you're about to touch — turning "I hope nothing uses this" into
a list. This is impact analysis, and it's the single most practical use of lineage:
changes stop being archaeology-plus-prayer.

**Upstream: root cause.** A dashboard number looks wrong. Lineage gives you the path
to walk backwards — which model fed it, which staging table fed that, which source it
came from — so you can find *where the wrongness entered* instead of guessing across
the whole platform. When [a pipeline isn't idempotent](/essays/how-to-make-a-data-pipeline-idempotent/)
and a re-run doubled some rows three hops upstream, lineage is how you find the hop.

Add the audit case — regulations that require showing where personal or financial
data flows — and that's the honest, complete list of what lineage is *for*.

## Table-level vs column-level

A distinction that matters more than vendors let on. **Table-level** lineage says
"model B reads from table A" — easy to capture, and too coarse for the questions
above: knowing a dashboard reads from a 200-column table doesn't tell you whether
*your* column matters to it. **Column-level** lineage traces individual fields
through every transformation, and it's the resolution at which impact analysis
actually works. It's also much harder to extract — every `SELECT *`, every template,
every dynamic query is a place column tracking goes dark. When evaluating tooling,
this is the question to press on.

As for where lineage comes from: it's either **parsed** from your transformation code
and SQL, **observed** from query logs at runtime, or **documented by hand**. The first
two can stay current automatically. The third is stale by next sprint — a lineage
diagram maintained manually is a drawing of how the pipeline used to work.

## What lineage cannot do

Here's the part the demos skip. Lineage is **descriptive, not corrective**. It maps
the structure you have; it does not improve it.

> A lineage graph of a swamp is a very accurate map of a swamp. Lineage tells you the
> blast radius of a change — it does nothing to make the radius smaller.

If everything depends on everything, lineage will render that tangle beautifully, and
every impact analysis will return "all of it." The fixes for *that* are architectural —
deliberate layers, [contracts at the boundaries](/essays/data-contracts-are-a-cultural-problem/),
[defined meaning](/essays/what-is-a-semantic-layer/) — not observational.

Lineage also tells you what depends on a dataset, but not **who answers for it**. A
graph without owners attached is trivia: you can see that thirty things break, but
there's no one to call. This is the same hole underneath most data-quality programs —
[the org-chart problem](/essays/data-quality-problems-are-org-chart-problems/) — and
lineage doesn't fill it; it just makes the unowned middle of your platform visible.
Useful, but only if someone then assigns the names.

And one forward-looking note: as AI systems start [consuming your data and answering
questions from it](/essays/your-ai-is-only-as-good-as-your-data-architecture/),
lineage becomes the provenance trail behind those answers — the only way to audit
*what* an AI-served number was actually computed from. Another place where an old
discipline quietly becomes load-bearing.

## When to invest

You need real lineage when the platform has outgrown any one person's head: enough
models, layers, and consumers that "what breaks if I change this?" can't be answered
from memory, or a compliance regime that demands the trail. Below that threshold, a
disciplined layered structure and tidy transformation code *are* your lineage —
readable directly from the repo.

When you do invest: prefer lineage that's **extracted automatically** from code and
logs, insist on **column-level** where it counts, and treat the graph as an input to
ownership and architecture decisions rather than an outcome in itself. Lineage is the
map. The map is genuinely useful. But nobody ever fixed a city by mapping it — and the
teams that get value from lineage are the ones who treat the map as the beginning of
the work, not the deliverable.

Lineage is also the first thing worth automating if you're
[building a data catalog](/essays/how-to-build-a-data-catalog/) — it's the
metadata that stays current without anyone remembering to update it, which is
precisely why hand-maintained catalogs rot and extracted ones don't.
