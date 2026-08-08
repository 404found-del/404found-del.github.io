---
title: "How to Choose an Iceberg Catalog: Unity vs Polaris vs Glue vs Nessie"
kicker: "Field Notes"
topic: "Architecture"
description: "The table format war is settled; the catalog decides governance and lock-in now. How Iceberg catalogs work, compared honestly — and a decision rule that holds."
date: 2026-07-08 19:00:00 +0530
last_modified_at: 2026-08-08
faq:
  - q: "What does an Iceberg catalog actually do?"
    a: "It holds the authoritative pointer to each table's current metadata file and swaps that pointer atomically on every commit — which is what makes transactions work. On top of that mechanical job, catalogs layer the governance: who may read, write, or commit to which table, from which engine, with what audit trail."
  - q: "Is an Iceberg catalog the same as a data catalog like Atlan or Collibra?"
    a: "No — unfortunate naming collision. An Iceberg catalog is technical infrastructure: it's in the write path of every transaction. A data catalog is a discovery and documentation layer for humans. You'll likely have both, and the data catalog will read from the Iceberg catalog."
  - q: "Can I switch Iceberg catalogs later?"
    a: "Yes, but it's the painful migration in a lakehouse. The data files don't move, but every engine's connection config, all access-control policies, and any audit or lineage history live in the catalog. That switching cost — not the table format — is where lock-in lives in 2026, so choose deliberately."
  - q: "Which Iceberg catalog should I default to?"
    a: "Match your platform gravity: Unity if you're Databricks-centred, Glue if you're deep in AWS, Polaris (or Snowflake's managed Open Catalog) for a neutral, multi-engine REST catalog, Nessie if you specifically want git-like branching of your whole catalog. Neutral-by-default: Polaris."
  - q: "Unity Catalog vs Glue Catalog — how do they compare?"
    a: "They're the two gravity choices, and the trade is governance depth versus cloud convenience. Glue is IAM-native, serverless, and near-zero setup inside AWS, but its governance is thinner and it deepens your commitment to one cloud. Unity brings much richer governance — lineage, fine-grained policies, audit in one place — priced in Databricks commitment. Teams running Databricks on AWS commonly use both: Unity as the governing catalog, with Glue federated in for legacy tables."
---

The [table format decision](/essays/iceberg-vs-delta-lake/) got easy in 2026 —
which means the hard decision moved. Every Iceberg table has exactly one
authoritative record of "which metadata file is current," and the component that
holds it — the **catalog** — is now where governance, auditability, and the real
lock-in of a [lakehouse](/glossary/data-lakehouse/) live. The main contenders: **Unity Catalog**
(Databricks), **Apache Polaris** (open-sourced by Snowflake), **AWS Glue**, and
**Nessie**. The decision rule, up front: **follow your platform gravity — Unity
for Databricks estates, Glue for deep-AWS shops — and when you want genuine
engine neutrality, default to Polaris.** The rest of this essay is why, and what
each choice costs.

## What a catalog actually is

Strip away the marketing and an Iceberg catalog does one mechanical thing: for
every table, it stores a pointer to the current metadata file, and it swaps that
pointer **atomically** when a commit happens. That single atomic swap is what
gives an [open table format](/essays/what-is-an-open-table-format/) ACID
guarantees on dumb object storage. Everything else a catalog offers — access
control, credential vending, auditing, lineage — is governance layered onto its
position in the write path.

That position is why the choice matters: every engine, every pipeline, every
commit goes through it. (Don't confuse it with a
[data catalog](/essays/what-is-a-data-catalog/) like Atlan or Collibra — same
word, different layer: one is transaction infrastructure, the other is
documentation for humans.)

## Unity vs Polaris vs Glue vs Nessie, compared

| | Unity Catalog | Apache Polaris | AWS Glue | Nessie |
|---|---|---|---|---|
| **Steward** | Databricks (OSS core) | Apache Software Foundation | AWS | Dremio-backed OSS |
| **Formats** | Delta, Iceberg, Hudi | Iceberg only | Iceberg + others | Iceberg |
| **Iceberg REST spec** | Yes, endpoint | Yes — reference implementation | Yes | Yes |
| **Access control** | Strong, platform-integrated | Granular, engine-neutral | IAM-based | Basic |
| **Managed offering** | Databricks | Snowflake Open Catalog | AWS | Dremio |
| **Distinctive strength** | Lineage + governance in one platform | Neutrality | Zero-effort if you're on AWS | Git-like branches and tags |
| **Gravity** | Databricks | None — that's the point | AWS | Dremio / advanced teams |

The structural fact underneath the table: the **Iceberg REST catalog
specification** is what every engine now standardises against, so any
spec-faithful catalog can serve Spark, Trino, Flink, and friends. The
differences are in governance depth, ecosystem gravity, and who you're
comfortable depending on.

## What connecting looks like

The catalog is one config block per engine — which is also the honest preview of
a future migration:

```properties
# Spark: attach a REST catalog (Polaris, Unity's endpoint, Glue — same shape).
# Set at session start, not in SQL: catalog config is Spark configuration, and
# anything passed through SET lands in the Spark UI, event logs, and query history.
spark.sql.extensions = org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
spark.sql.catalog.lake = org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.lake.type = rest
spark.sql.catalog.lake.uri = https://catalog.example.com/api/catalog
spark.sql.catalog.lake.warehouse = my_warehouse          # which warehouse this catalog serves
spark.sql.catalog.lake.rest.auth.type = oauth2           # token exchange, not a static secret
spark.sql.catalog.lake.oauth2-server-uri = https://idp.example.com/oauth/token
# The client secret is injected from a secret manager at submit time —
# it never appears in a notebook cell, a repo, or a log line.
spark.sql.catalog.lake.token = ${ICEBERG_CATALOG_TOKEN}
```

The `spark.sql.extensions` line is the one people omit and then spend an
afternoon on: without it, `MERGE`, `CALL`, and time-travel syntax simply don't
parse. Note also where the credential *isn't* — a catalog that is your security
boundary is a poor place to start by leaking its own credential into query
history.

With that config in place, the SQL is vendor-neutral:

```sql
-- Identical against any spec-faithful catalog answering that URI:
CREATE TABLE lake.sales.orders (
  order_id BIGINT, order_ts TIMESTAMP, amount DECIMAL(12,2)
) USING iceberg
PARTITIONED BY (days(order_ts));
```

Identical SQL, whichever catalog answers that URI. The switching pain is never
the tables — it's re-plumbing every engine's config and rebuilding every access
policy and audit trail that accumulated in the old catalog.

The Iceberg REST catalog spec defines both this wire protocol and the OAuth2
token exchange above; the
[open specification](https://iceberg.apache.org/spec/) and the
[REST catalog OpenAPI definition](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml)
are the authoritative reference when a vendor's docs and your engine's behaviour
disagree.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="how-to-choose-an-iceberg-catalog-t how-to-choose-an-iceberg-catalog-d">
  <title id="how-to-choose-an-iceberg-catalog-t">Choosing an Iceberg catalog by platform gravity</title>
  <desc id="how-to-choose-an-iceberg-catalog-d">A decision tree from the question of where your platform gravity sits. Databricks estates lead to Unity Catalog, deep-AWS estates to Glue, and mixed or deliberately neutral estates to Apache Polaris. A separate box covers the special case: teams needing git-like branching of the catalog choose Nessie.</desc>
  <rect x="250" y="16" width="300" height="52" rx="6" fill="#1c1a17"/>
  <text x="400" y="38" font-size="13" fill="#f6f3ec" text-anchor="middle">Where is your platform gravity?</text>
  <text x="400" y="56" font-size="11" fill="#8b857a" text-anchor="middle">(engines, identity, people)</text>
  <line x1="300" y1="68" x2="140" y2="120" stroke="#cabfac" stroke-width="2"/>
  <line x1="400" y1="68" x2="400" y2="120" stroke="#cabfac" stroke-width="2"/>
  <line x1="500" y1="68" x2="660" y2="120" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="120" width="200" height="60" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="140" y="145" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Databricks</text>
  <text x="140" y="166" font-size="12" fill="#56514a" text-anchor="middle">→ Unity Catalog</text>
  <rect x="300" y="120" width="200" height="60" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="400" y="145" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Deep AWS</text>
  <text x="400" y="166" font-size="12" fill="#56514a" text-anchor="middle">→ Glue</text>
  <rect x="560" y="120" width="200" height="60" rx="6" fill="#c8472b"/>
  <text x="660" y="145" font-size="13" fill="#f6f3ec" text-anchor="middle" font-weight="700">Mixed / neutral</text>
  <text x="660" y="166" font-size="12" fill="#f6f3ec" text-anchor="middle">→ Polaris</text>
  <rect x="200" y="220" width="400" height="52" rx="6" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="400" y="242" font-size="12" fill="#1c1a17" text-anchor="middle">special case: need git-like branching of the catalog?</text>
  <text x="400" y="260" font-size="12" fill="#1c1a17" text-anchor="middle">→ Nessie</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">The catalog decision follows gravity — with neutrality as the deliberate exception.</figcaption>
</figure>

## The honest trade-offs

**Unity** buys the deepest integrated governance — lineage, policies, audit in
one place — priced in Databricks gravity. **Glue** is the lowest-effort answer
inside AWS and the least interesting outside it. **Polaris** is the neutral
choice: ASF-governed, REST-native, granular permissions, no engine agenda — but
younger, and you'll assemble more of the surrounding tooling yourself.
**Nessie** gives you catalog-level branches and tags (test a whole pipeline
against a branch of production data, then merge) — a genuinely distinctive
capability that most teams don't need yet.

Two of these pairings come up often enough to deserve their own treatment:
[Unity Catalog vs AWS Glue](/essays/unity-catalog-vs-glue-catalog/), where the
answer for Databricks-on-AWS estates is usually *both*, and
[Apache Polaris vs Nessie](/essays/apache-polaris-vs-nessie/), where the merger
announced in 2024 still has not happened despite most guidance assuming it did.

Whichever you pick, pick it *deliberately*. In a
[lakehouse](/essays/data-lake-vs-lakehouse/) built on open formats, the catalog
is the one component you can't casually swap — it's exactly where the next five
years of governance decisions will accumulate.
