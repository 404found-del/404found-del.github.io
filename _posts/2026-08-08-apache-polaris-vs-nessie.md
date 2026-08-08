---
title: "Apache Polaris vs Nessie: The Merger That Never Happened"
kicker: "Field Notes"
topic: "Architecture"
description: "Polaris and Nessie were announced as merging in 2024. They didn't. Here's where each actually stands in 2026, and which one your estate should run."
date: 2026-08-08 11:00:00 +0530
faq:
  - q: "What is the difference between Apache Polaris and Nessie?"
    a: "Both are open-source Iceberg catalogs, but they optimize for different things. Polaris is built around the Iceberg REST specification, centralized role-based access control, and credential vending, aimed at broad multi-engine interoperability. Nessie adds a Git-like model over the catalog: branches, tags, commits, and multi-table transactions, so you can isolate and roll back changes across many tables at once."
  - q: "Did Apache Polaris and Nessie merge?"
    a: "No. The merge was announced in 2024, with the stated intention that Nessie's capabilities would be contributed to Polaris and Nessie eventually retired. As of mid-2026 it has not happened. Polaris graduated from incubation and ships on a regular release train; Nessie continues independently serving the git-for-data niche. A lot of comparison content still repeats the 2024 plan as though it were current."
  - q: "Which Iceberg catalog should I choose, Polaris or Nessie?"
    a: "Default to Polaris. It is the neutral, spec-faithful REST catalog with the broader engine ecosystem and the more conventional governance model, and it now has ASF graduation behind it. Choose Nessie when you specifically want catalog-level branching — testing a pipeline against a branch of production data, or committing changes across several tables atomically. That capability is genuinely distinctive and most teams do not need it."
  - q: "Is Apache Polaris the same as Snowflake Open Catalog?"
    a: "Snowflake Open Catalog is Snowflake's managed service built on Polaris; Apache Polaris is the open-source project it came from and which Snowflake donated to the ASF. Running Open Catalog means running Polaris without operating it yourself. Snowflake Horizon, often listed alongside these, is the governance suite rather than the catalog."
---

Start with the thing most comparisons of these two get wrong. In 2024 it was
announced that
[Polaris and Nessie would merge](https://www.dremio.com/newsroom/polaris-catalog-to-be-merged-with-nessie-now-available-on-github/),
with Nessie's capabilities folded into Polaris and Nessie eventually retired.
**It did not happen.** As of mid-2026 both projects are alive and separate:
[Polaris graduated from incubation](https://amdatalakehouse.substack.com/p/the-state-of-apache-polaris-in-july)
and ships on a regular release train, while Nessie continues to serve the
git-for-data niche it invented.

That matters practically, because a fair amount of the guidance you'll find is
still written against the 2024 plan — advising people to pick Polaris on the
grounds that Nessie is going away. Nessie isn't going away. Choose on what each
actually does.

**The short version: default to Polaris. Choose Nessie only if you want Git-like
branching of the catalog itself, which is a real capability that most estates
don't need.**

## Polaris vs Nessie, side by side

| | Apache Polaris | Nessie |
|---|---|---|
| **Origin** | Donated by Snowflake, now ASF | Dremio-backed, open source |
| **Status, mid-2026** | Graduated, monthly release train | Independent, active |
| **Core idea** | Spec-faithful REST catalog + RBAC | Git semantics over the catalog |
| **Access control** | Granular table and namespace privileges | Branch- and commit-oriented |
| **Credential vending** | Yes | Limited |
| **Multi-table transactions** | No | Yes — that is the point |
| **Branch / tag / rollback** | No | Yes |
| **Engine ecosystem** | Broad: Spark, Flink, Trino, Doris, DuckDB, Presto, Starburst | Narrower, Dremio-centred |
| **Managed option** | Snowflake Open Catalog | Dremio |
| **Choose it when** | You want a neutral default | You want data as branchable state |
| **Fails by** | Being unremarkable, which is the goal | Solving a problem you don't have |

## What Nessie actually gives you

Nessie's distinctive claim is not access control or interop. It's that the catalog
behaves like Git: you can branch it, commit to the branch, test against it, and
merge or discard. Because the branch covers the *whole catalog* rather than one
table, you get something genuinely hard to obtain otherwise — **atomic changes
across several tables at once.**

The workflow that justifies it looks like this:

```sql
-- Branch the entire catalog, not one table
CREATE BRANCH etl_run_2026_08_08 IN nessie FROM main;
USE REFERENCE etl_run_2026_08_08 IN nessie;

-- Rewrite several related tables; nothing is visible on main yet
MERGE INTO sales.orders   ...;
MERGE INTO sales.line_item ...;
MERGE INTO sales.customer  ...;

-- Validate the branch, then publish all three tables atomically
MERGE BRANCH etl_run_2026_08_08 INTO main IN nessie;
```

Anyone who has shipped a pipeline that half-updated three tables and left the
warehouse internally inconsistent for forty minutes can see the appeal. It is the
same instinct as
[idempotent pipelines](/essays/how-to-make-a-data-pipeline-idempotent/), pushed up
to the catalog: make the unsafe window not exist rather than making it short.

## What Polaris actually gives you

Polaris is deliberately less interesting, and that is its argument. It implements
the [Iceberg REST catalog specification](https://iceberg.apache.org/spec/)
faithfully, vends credentials so the catalog can act as the real security
boundary, and applies conventional role-based privileges at table and namespace
level. Every spec-faithful engine talks to it without special handling.

Its second argument is governance of the project rather than of the data. It sits
with the Apache Software Foundation with contributions from multiple vendors, it
has graduated, and it has a predictable release cadence. If your reason for
avoiding Unity Catalog and Glue is that you don't want a single vendor holding the
component you cannot casually swap, Polaris is the answer that reasoning points
to. Snowflake's managed
[Open Catalog](https://www.snowflake.com/en/blog/polaris-catalog-open-source/) is
the same codebase operated for you.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 340" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="polaris-nessie-t polaris-nessie-d">
  <title id="polaris-nessie-t">Polaris and Nessie optimize for different things</title>
  <desc id="polaris-nessie-d">Two panels. Polaris is shown as a single main line of commits with role-based privileges applied per table and namespace, serving many engines through the Iceberg REST specification. Nessie is shown as a main line with a branch drawn off it, where three tables are rewritten in isolation and then merged back atomically, illustrating catalog-level branching and multi-table transactions. A note beneath records that the 2024 announcement to merge the two projects has not happened as of 2026 and both remain active.</desc>
  <text x="200" y="26" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Polaris — one governed line</text>
  <text x="600" y="26" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Nessie — branchable catalog</text>
  <line x1="60" y1="110" x2="340" y2="110" stroke="#1c1a17" stroke-width="2.5"/>
  <circle cx="110" cy="110" r="7" fill="#c8472b"/>
  <circle cx="200" cy="110" r="7" fill="#c8472b"/>
  <circle cx="290" cy="110" r="7" fill="#c8472b"/>
  <text x="200" y="136" font-size="10" fill="#56514a" text-anchor="middle">main — commits land directly</text>
  <rect x="60" y="156" width="280" height="26" rx="4" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.2"/>
  <text x="200" y="174" font-size="10" fill="#56514a" text-anchor="middle">RBAC per table + namespace</text>
  <rect x="60" y="190" width="280" height="26" rx="4" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.2"/>
  <text x="200" y="208" font-size="10" fill="#56514a" text-anchor="middle">credential vending · REST spec</text>
  <text x="200" y="240" font-size="10" fill="#8b857a" text-anchor="middle">Spark · Flink · Trino · DuckDB · Presto</text>
  <line x1="460" y1="110" x2="740" y2="110" stroke="#1c1a17" stroke-width="2.5"/>
  <circle cx="500" cy="110" r="7" fill="#1c1a17"/>
  <circle cx="710" cy="110" r="7" fill="#c8472b"/>
  <path d="M540 110 C 570 110, 570 176, 600 176" fill="none" stroke="#c8472b" stroke-width="2"/>
  <path d="M660 176 C 690 176, 690 110, 710 110" fill="none" stroke="#c8472b" stroke-width="2"/>
  <circle cx="600" cy="176" r="6" fill="#c8472b"/>
  <circle cx="630" cy="176" r="6" fill="#c8472b"/>
  <circle cx="660" cy="176" r="6" fill="#c8472b"/>
  <text x="630" y="200" font-size="10" fill="#a4391f" text-anchor="middle">branch: 3 tables rewritten together</text>
  <text x="712" y="98" font-size="10" fill="#a4391f" text-anchor="end">merged atomically →</text>
  <text x="600" y="240" font-size="10" fill="#8b857a" text-anchor="middle">multi-table transactions · rollback · zero-copy test envs</text>
  <line x1="400" y1="46" x2="400" y2="258" stroke="#ddd6c8" stroke-width="1.5" stroke-dasharray="4 4"/>
  <rect x="140" y="276" width="520" height="42" rx="6" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="400" y="294" font-size="11" fill="#1c1a17" text-anchor="middle">announced 2024: Nessie merges into Polaris, Nessie retired</text>
  <text x="400" y="311" font-size="11" fill="#a4391f" text-anchor="middle">mid-2026: it has not happened. Both projects are active and separate.</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">One line versus branchable state. And a merger announcement that guidance still repeats two years on.</figcaption>
</figure>

## Why the merger stalled, and why you shouldn't plan around it resuming

The two projects were never as complementary as the announcement implied. Polaris
is organised around a single authoritative pointer per table with privileges
layered on top — the model the
[Iceberg REST spec](/essays/what-is-an-open-table-format/) assumes. Nessie is
organised around versioned references, where "current" is a property of the branch
you're reading. Merging them is not a matter of porting features; it means
choosing which of two models of catalog state is the real one.

Practical implication: **do not choose either catalog on the assumption they will
converge.** If branching is what you need, run Nessie and accept a narrower engine
ecosystem. If it isn't, run Polaris and don't pay for a capability you won't use.

## The decision rule

```text
Do you need atomic changes across MULTIPLE tables,
or branch-and-test against a copy of production catalog state?
   → Nessie. Nothing else does this cleanly.

Do you want a neutral, spec-faithful catalog with broad engine support
and conventional RBAC?
   → Polaris. Managed: Snowflake Open Catalog.

Not sure, and no multi-table transaction has ever hurt you?
   → Polaris. The branching model has real operational cost,
     and inventing a use for it after the fact is how estates
     accumulate machinery nobody maintains.
```

And the honest framing that applies to
[every catalog decision](/essays/how-to-choose-an-iceberg-catalog/): the data
files never move, so this feels like a reversible choice. It isn't. Every engine
config, every access policy, and all accumulated audit history live in the
catalog, which is exactly why it deserves the evaluation weeks the format choice
no longer needs.
