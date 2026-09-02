---
title: "Unity Catalog vs AWS Glue Data Catalog: How to Choose"
kicker: "Field Notes"
topic: "Architecture"
description: "Glue is the zero-effort default inside AWS; Unity Catalog buys deeper governance for platform commitment. Both now speak Iceberg REST, and they federate."
date: 2026-08-08 09:00:00 +0530
faq:
  - q: "What is the difference between Unity Catalog and AWS Glue Data Catalog?"
    a: "Glue Data Catalog is a serverless metastore native to AWS, governed by IAM, with crawlers that register tables automatically. Unity Catalog is Databricks' governance layer, now open-sourced under the Linux Foundation, offering fine-grained access control, lineage, and audit across data and AI assets in one place. Glue is the lower-effort choice inside AWS; Unity is the deeper governance choice, priced in platform commitment."
  - q: "Can Unity Catalog and AWS Glue work together?"
    a: "Yes, and this is the detail that dissolves most of the either-or framing. Unity Catalog includes federation connectors for AWS Glue and Hive Metastore, so Glue catalogs can be mounted as foreign catalogs inside Unity. AWS added federation in the other direction too. Teams running Databricks on AWS commonly use Unity as the governing catalog with Glue federated in for legacy tables."
  - q: "Does Unity Catalog support Apache Iceberg?"
    a: "Yes. Unity Catalog implements the Iceberg REST Catalog API, including credential vending, so Iceberg clients like Spark, Flink, and Trino can read and write Unity-managed tables. Glue also exposes an Iceberg REST endpoint. Iceberg support is no longer a differentiator between them."
  - q: "Is Unity Catalog open source?"
    a: "The core is. Databricks open-sourced Unity Catalog under Apache 2.0 with a published OpenAPI spec, and it sits with the LF AI and Data Foundation. The open-source project and the managed Databricks service are not the same thing, though, and the governance depth people associate with Unity Catalog largely lives in the managed product."
---

Both of these hold the pointer that makes an
[Iceberg table](/essays/what-is-an-open-table-format/) a table, and the choice
between them is not really a technical one. **AWS Glue Data Catalog is the
zero-effort default if your compute lives in AWS: serverless, IAM-governed, with
crawlers that register tables for you. Unity Catalog buys materially deeper
governance — fine-grained access control, lineage, and audit for data and AI
assets in one place — and charges for it in platform commitment.**

The decision rule is short: **follow your compute.** Deep-AWS shops take Glue.
Databricks-centred estates take Unity. And the case that trips people up — running
Databricks *on* AWS — usually ends with both, which is the part most comparisons
miss entirely.

## Unity Catalog vs Glue, side by side

| | AWS Glue Data Catalog | Unity Catalog |
|---|---|---|
| **Steward** | AWS | Databricks; core is Apache 2.0 under LF AI & Data |
| **Operating model** | Serverless, no infrastructure | Managed in Databricks, or self-hosted OSS |
| **Access control** | IAM, plus Lake Formation for finer grain | Native fine-grained: catalog, schema, table, row, column |
| **Lineage** | Limited | First-class, captured automatically |
| **Audit** | CloudTrail | Unified across data and AI assets |
| **Table registration** | Crawlers discover and register automatically | Explicit registration |
| **Iceberg REST API** | Yes | Yes, with credential vending |
| **Non-tabular assets** | Tables | Tables, volumes, models, functions |
| **Gravity** | AWS | Databricks |
| **Costs you** | Cloud lock-in | Platform commitment |
| **Fails by** | Governance thinning out as the estate grows | Being overkill without the platform around it |

## What Glue is actually good at

Glue's advantage is that it is *already there*. If your estate is Athena, EMR,
Redshift Spectrum, and Glue ETL, the catalog requires no decision, no deployment,
and no separate bill of its own. Crawlers infer schemas and register tables
without anyone writing DDL, which for a lake accumulating files from many
producers is a genuine reduction in toil.

The governance is IAM-shaped, which is a real strength if your organisation
already runs on IAM and a real limit otherwise. Table- and column-level control
means adding Lake Formation on top, and the lineage story is thin. That's fine
until the estate has enough consumers that "who can see this column, and who
touched it last quarter" becomes a question someone has to answer in writing.

## What Unity Catalog is actually good at

Unity's advantage is that governance is one surface rather than four. Permissions,
lineage, and audit cover tables, files, ML models, and functions together, which
matters once AI assets stop being a side project. Where Glue tells you IAM allowed
a call, Unity tells you which notebook read which column and what it fed.

It's also less closed than its reputation suggests. Databricks
[open-sourced the core under Apache 2.0](https://www.databricks.com/blog/open-sourcing-unity-catalog)
with a published spec, and the project sits with the LF AI & Data Foundation.
Worth being precise about what that means, though: the OSS project and the managed
Databricks service are not the same thing, and most of the governance depth people
buy Unity Catalog *for* lives in the managed product. Treat "it's open source" as a
statement about lock-in risk, not a statement about features.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 330" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="uc-glue-t uc-glue-d">
  <title id="uc-glue-t">Choosing between Unity Catalog and AWS Glue Data Catalog</title>
  <desc id="uc-glue-d">A decision tree starting from where compute lives. Estates centred on AWS services such as Athena, EMR and Redshift branch to Glue Data Catalog, which is serverless and IAM-governed. Estates centred on Databricks branch to Unity Catalog, which provides fine-grained access control, lineage and audit. A third path shows Databricks running on AWS, which commonly ends with both: Unity as the governing catalog with Glue federated in for legacy tables. A final note records that both now expose an Iceberg REST endpoint, so Iceberg support no longer separates them.</desc>
  <rect x="250" y="16" width="300" height="50" rx="6" fill="#1c1a17"/>
  <text x="400" y="38" font-size="13" fill="#f6f3ec" text-anchor="middle">Where does your compute live?</text>
  <text x="400" y="56" font-size="10" fill="#8b857a" text-anchor="middle">not: which catalog has more features</text>
  <line x1="310" y1="66" x2="150" y2="110" stroke="#cabfac" stroke-width="2"/>
  <line x1="400" y1="66" x2="400" y2="110" stroke="#cabfac" stroke-width="2"/>
  <line x1="490" y1="66" x2="650" y2="110" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="110" width="220" height="72" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="150" y="134" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">Athena · EMR · Redshift</text>
  <text x="150" y="155" font-size="11" fill="#c8472b" text-anchor="middle" font-weight="700">→ Glue Data Catalog</text>
  <text x="150" y="173" font-size="11" fill="#56514a" text-anchor="middle">serverless · IAM · crawlers</text>
  <rect x="290" y="110" width="220" height="72" rx="6" fill="#c8472b"/>
  <text x="400" y="134" font-size="12" fill="#f6f3ec" text-anchor="middle" font-weight="700">Databricks on AWS</text>
  <text x="400" y="155" font-size="11" fill="#f6f3ec" text-anchor="middle" font-weight="700">→ usually BOTH</text>
  <text x="400" y="173" font-size="11" fill="#f6f3ec" text-anchor="middle">Unity governs · Glue federated in</text>
  <rect x="540" y="110" width="220" height="72" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="650" y="134" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">Databricks-centred</text>
  <text x="650" y="155" font-size="11" fill="#c8472b" text-anchor="middle" font-weight="700">→ Unity Catalog</text>
  <text x="650" y="173" font-size="11" fill="#56514a" text-anchor="middle">lineage · fine-grained · audit</text>
  <rect x="170" y="216" width="460" height="46" rx="6" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="400" y="236" font-size="11" fill="#1c1a17" text-anchor="middle">both now expose an Iceberg REST endpoint</text>
  <text x="400" y="253" font-size="10" fill="#8b857a" text-anchor="middle">Iceberg support stopped being the differentiator</text>
  <text x="400" y="294" font-size="12" fill="#8b857a" text-anchor="middle">the middle box is the case most comparisons leave out, and it is the common one</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">Follow the compute. And notice that the middle branch is not a compromise, it is the usual answer.</figcaption>
</figure>

## The case nobody writes about: both

Running Databricks on AWS is not an edge case, and it does not force a choice.
Unity Catalog ships federation connectors for Glue and Hive Metastore, so an
existing Glue catalog mounts as a foreign catalog inside Unity, and
[AWS built federation in the other direction](https://aws.amazon.com/blogs/big-data/access-databricks-unity-catalog-data-using-catalog-federation-in-the-aws-glue-data-catalog/)
so Glue-side engines can reach Unity-governed tables.

The pattern that works: **Unity as the governing catalog for anything new, Glue
federated in for the legacy estate**, migrating tables when there's a reason
rather than as a project. You get one governance surface without a big-bang
migration, which matters because
[switching catalogs is the painful migration in a lakehouse](/essays/how-to-choose-an-iceberg-catalog/)
— the data files never move, but every engine config, every access policy, and
all accumulated audit history do.

## Where the Iceberg story landed

This used to be a real differentiator and isn't anymore. Unity Catalog implements
the [Iceberg REST Catalog API](https://iceberg.apache.org/spec/) including
credential vending, so Spark, Flink, Trino and anything else spec-faithful can
read and write Unity-managed tables. Glue exposes an Iceberg endpoint too.

```properties
# Same Spark client, either catalog behind the URI.
spark.sql.extensions = org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
spark.sql.catalog.lake = org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.lake.type = rest
spark.sql.catalog.lake.uri = https://<unity-or-glue-endpoint>/iceberg
spark.sql.catalog.lake.warehouse = my_warehouse
spark.sql.catalog.lake.rest.auth.type = oauth2
# token injected from a secret manager at submit time, never in a notebook cell
spark.sql.catalog.lake.token = ${ICEBERG_CATALOG_TOKEN}
```

That config is nearly identical either way, which is the point: **the wire
protocol converged, so the decision moved entirely to governance and gravity.**

## The decision rule

```text
Compute is Athena / EMR / Redshift, governance needs are IAM-shaped?
   → Glue. Stop optimising; it is already there.

Compute is Databricks, and you need lineage, column-level control,
or one audit surface across data AND AI assets?
   → Unity Catalog.

Databricks on AWS with a legacy Glue estate?
   → Both. Unity governs, Glue federates in. This is the common case.

Deliberately avoiding both vendors' gravity?
   → Neither — that is the Polaris question, one layer over.
```

The trap worth naming: choosing Unity Catalog for governance you have no
organisational capacity to operate. Fine-grained access control is only worth its
setup cost if someone owns the policies and reviews them. Absent that, you've
bought a more expensive metastore and inherited the same
[org-chart problem](/essays/data-quality-problems-are-org-chart-problems/) you
started with. Glue plus genuine ownership beats Unity plus nobody, every time.
