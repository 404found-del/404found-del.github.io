---
title: "How to Build a Data Catalog That People Actually Use"
kicker: "Field Notes"
topic: "Governance"
description: "A tool-neutral guide to building a data catalog: start from query logs, document the fifty tables that matter, assign owners, automate the rest — in that order."
date: 2026-07-17 10:30:00 +0530
faq:
  - q: "How do I start building a data catalog?"
    a: "Not with a tool. Mine your warehouse query logs for the fifty most-queried tables, write honest descriptions and assign a named owner for each, and publish that anywhere searchable — even a wiki page. That's a working catalog covering the majority of real usage, built in about two weeks, and it tells you exactly what to automate next."
  - q: "Do I need to buy a data catalog tool?"
    a: "Eventually, probably — automated schema harvesting, lineage, and search beat any wiki at scale. But a tool populated before ownership and descriptions exist becomes an expensive empty shelf. Prove the curation habit on your top fifty tables first; then a tool amplifies something that already works."
  - q: "Who should own the data catalog?"
    a: "Two levels: every entry needs a named owner — a person, not a team — who answers for that table's description and quality. The catalog itself needs a curator whose actual job includes keeping coverage and freshness up. Catalogs die when curation is everyone's side task and no one's responsibility."
  - q: "Why do most data catalog projects fail?"
    a: "They automate the easy 80% — schemas, column names, lineage — and skip the human 20% that makes a catalog trustworthy: descriptions, ownership, and certification. Users arrive, find auto-generated stubs with no context, and never come back. Adoption dies in the gap between inventory and meaning."
---

Most data catalog projects start with a vendor evaluation and end as an
expensive, auto-populated shelf nobody visits. That's because the failure mode
of catalogs isn't technical — [a catalog](/essays/what-is-a-data-catalog/) is
only useful when humans trust its answers, and trust comes from the curated 20%
(descriptions, owners, certification) that no tool can harvest. So build in
this order: **find what's actually used, document and assign owners to that,
prove the curation habit — and only then automate and scale.** Here's the
sequence, tool-neutral.

## Step 1 — Let query logs tell you what matters

Your warehouse already knows which tables the organisation depends on. Ask it:

```sql
-- Snowflake flavour; every warehouse has an equivalent log
SELECT
  obj.value:objectName::string            AS table_name,
  count(DISTINCT query_id)                AS queries_90d,
  count(DISTINCT user_name)               AS distinct_users
FROM snowflake.account_usage.access_history,
     LATERAL FLATTEN(base_objects_accessed) obj
WHERE query_start_time > dateadd('day', -90, current_timestamp)
GROUP BY 1
ORDER BY queries_90d DESC
LIMIT 50;
```

The distribution is always brutally skewed: ~50 tables carry most of the
analytical traffic. That's your catalog's scope for the next month — not the
40,000 tables the scanner found.

## Step 2 — Document the fifty, and name an owner for each

For each table: a two-sentence honest description (what one row is — the
[grain](/essays/fact-table-grain/) — where it comes from, what it must *not* be
used for), the refresh schedule, and a **named human owner**. Not "the platform
team" — a person. This step is where the project succeeds or dies, because it's
where the org chart gets involved:
[data problems are ownership problems](/essays/data-quality-problems-are-org-chart-problems/)
wearing metadata clothing.

Publish it anywhere searchable. A wiki table is a legitimate v1 catalog.

## Step 3 — Add trust signals, not just facts

Introduce a small certification ladder — e.g. **certified** (owned, tested,
safe for decisions), **internal** (usable, caveats apply), **deprecated** (stop;
here's the replacement). Three tiers, applied to the fifty. This single feature
is most of a catalog's daily value: it converts "I found a table" into "I know
whether to trust it."

## Step 4 — Now automate: harvest, lineage, search

With the human layer proven, a tool earns its keep: automated schema and
freshness harvesting, [column-level lineage](/essays/what-is-data-lineage/) from
query logs, usage stats, and proper search. Open-source (DataHub, OpenMetadata,
Amundsen) or commercial — the selection matters less than arriving at it with
descriptions, owners, and tiers already alive, because migration imports a
working catalog instead of launching an empty one.

## Step 5 — Make curation a job, and wire it into change

Coverage decays the day you stop. Two mechanisms keep it alive: a curator whose
actual job includes catalog health (coverage %, stale descriptions, orphaned
tables), and hooks into change management — a new table doesn't ship to
production without an owner and description, ideally enforced the same way
[data contracts](/essays/data-contracts-are-a-cultural-problem/) are.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 250" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
  <rect x="20" y="60" width="136" height="70" rx="6" fill="#c8472b"/>
  <text x="88" y="90" font-size="12" fill="#f6f3ec" text-anchor="middle" font-weight="700">1 query logs</text>
  <text x="88" y="110" font-size="10" fill="#f6f3ec" text-anchor="middle">find the real 50</text>
  <line x1="156" y1="95" x2="176" y2="95" stroke="#cabfac" stroke-width="2"/>
  <rect x="176" y="60" width="136" height="70" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="244" y="90" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">2 owners +</text>
  <text x="244" y="110" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">descriptions</text>
  <line x1="312" y1="95" x2="332" y2="95" stroke="#cabfac" stroke-width="2"/>
  <rect x="332" y="60" width="136" height="70" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="400" y="90" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">3 certification</text>
  <text x="400" y="110" font-size="10" fill="#56514a" text-anchor="middle">certified / internal / deprecated</text>
  <line x1="468" y1="95" x2="488" y2="95" stroke="#cabfac" stroke-width="2"/>
  <rect x="488" y="60" width="136" height="70" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="556" y="90" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">4 automate</text>
  <text x="556" y="110" font-size="10" fill="#56514a" text-anchor="middle">harvest · lineage · search</text>
  <line x1="624" y1="95" x2="644" y2="95" stroke="#cabfac" stroke-width="2"/>
  <rect x="644" y="60" width="136" height="70" rx="6" fill="#1c1a17"/>
  <text x="712" y="90" font-size="12" fill="#f6f3ec" text-anchor="middle" font-weight="700">5 keep alive</text>
  <text x="712" y="110" font-size="10" fill="#f6f3ec" text-anchor="middle">curator + change hooks</text>
  <text x="400" y="200" font-size="12" fill="#8b857a" text-anchor="middle">the order is the method: humans and trust first, tooling second — reverse it and you build the empty shelf</text>
</svg>
</figure>

## The honest summary

| Phase | Effort | What you get |
|---|---|---|
| Query-log mining | Days | The real scope: ~50 tables |
| Descriptions + owners | 2–4 weeks | A trustworthy v1 (wiki is fine) |
| Certification tiers | Days | The trust signal users actually need |
| Tooling + lineage | Weeks–months | Scale, search, automation |
| Curation as a job | Forever | The difference between a catalog and a graveyard |

The pattern behind every catalog that works: it was never a software project.
It was an ownership project with a search box on top.
