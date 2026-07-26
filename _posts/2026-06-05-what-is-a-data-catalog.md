---
title: "What Is a Data Catalog, and Do You Need One?"
kicker: "Field Notes"
topic: "Governance"
description: "A data catalog is a searchable inventory of your data: what exists, where it lives, what it means, who owns it. What it's for, and when you actually need one."
date: 2026-06-05
last_modified_at: 2026-07-26
faq:
  - q: "What is the difference between a data catalog and a semantic layer?"
    a: "A catalog is an inventory — it documents what data exists, where it lives, and who owns it. A semantic layer defines what metrics mean and computes them consistently at query time. The catalog helps you find and understand data; the semantic layer governs and serves the definitions."
  - q: "Is a data catalog the same as data lineage?"
    a: "Lineage is one feature a good catalog often includes, not a synonym. Lineage traces how data flows from source to consumer; a catalog is the broader searchable inventory of datasets, owners, definitions, and metadata, of which lineage may be one part."
  - q: "When is a data catalog overkill?"
    a: "A small team that can hold its handful of tables in its head doesn't need one — a well-organized warehouse and a README do the job. A catalog earns its keep once nobody can answer 'what data do we have and what does it mean?' from memory."
---

A data catalog is, at its simplest, a searchable inventory of an organization's
data: a single place that answers *what data do we have, where does it live, what
does it mean, and who owns it?* As a company's data sprawls across hundreds or
thousands of tables, that question stops being answerable from memory, and the
catalog is the tool that answers it. Useful idea, and, like most governance tools,
one that's oversold in ways worth pulling apart before you buy.

## What a catalog actually holds

Walk up to a mature data catalog and you can search for a dataset the way you'd
search a library. For each table it typically records the **technical metadata**
(schema, types, where it physically lives, how big it is, when it last updated), the
**business metadata** (a plain-language description of what the table represents, what
each column means, which business terms apply), and the **operational metadata** (who
owns it, who uses it, how fresh it is, and often its [lineage](/essays/what-is-data-lineage/)
— where it came from and what depends on it).

The payoff is **discovery and understanding**. A new analyst who would otherwise spend
three weeks reconstructing, by archaeology, what every table means can instead search
the catalog, read the description, see the owner, and get to work. The catalog is the
institutional memory that a sprawling data estate otherwise loses.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 330" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="data-catalog-t data-catalog-d">
  <title id="data-catalog-t">What a data catalog holds, and what rots</title>
  <desc id="data-catalog-d">Three bands of metadata in a catalog. Technical metadata — schema, types, size, last updated — is harvested automatically and stays current on its own. Operational metadata such as usage, freshness and lineage is also machine-extractable. Business metadata — descriptions, meaning, ownership — is the valuable band and the only one humans must maintain, which is why it is filled in once during rollout and then rots.</desc>
  <rect x="140" y="30" width="520" height="62" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="400" y="56" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">technical metadata</text>
  <text x="400" y="78" font-size="10" fill="#56514a" text-anchor="middle">schema · types · size · last updated</text>
  <text x="700" y="66" font-size="9" fill="#8b857a">auto ✓</text>
  <rect x="140" y="104" width="520" height="62" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="400" y="130" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">operational metadata</text>
  <text x="400" y="152" font-size="10" fill="#56514a" text-anchor="middle">usage · freshness · lineage</text>
  <text x="700" y="140" font-size="9" fill="#8b857a">auto ✓</text>
  <rect x="140" y="178" width="520" height="62" rx="6" fill="#c8472b"/>
  <text x="400" y="204" font-size="12" fill="#f6f3ec" text-anchor="middle" font-weight="700">business metadata</text>
  <text x="400" y="226" font-size="10" fill="#f6f3ec" text-anchor="middle">descriptions · meaning · ownership</text>
  <text x="686" y="214" font-size="9" fill="#a4391f">humans</text>
  <text x="400" y="272" font-size="12" fill="#8b857a" text-anchor="middle">the top two bands stay current by themselves; the bottom one is the reason people</text>
  <text x="400" y="294" font-size="12" fill="#8b857a" text-anchor="middle">bought the catalog — and the only one that needs a named, ongoing owner</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">The machine-maintained bands stay current on their own. The valuable band is the one that rots.</figcaption>
</figure>

## What it is *not*

Two confusions cause most disappointed catalog rollouts.

**It is not a [semantic layer](/glossary/semantic-layer/).** A catalog *documents* that a `revenue` column exists
and describes it in prose. A [semantic layer](/essays/what-is-a-semantic-layer/)
*defines and computes* revenue consistently for every consumer at query time. One
helps you find and understand data; the other governs and serves the actual numbers.
A catalog full of beautiful descriptions of three conflicting `revenue` columns has
documented your inconsistency, not resolved it.

> A catalog tells you what data exists and what it's supposed to mean. It does not
> make the data correct, consistent, or trustworthy; it describes the estate, it
> doesn't govern it.

**It is not a quality tool.** The catalog can display a freshness or quality score,
but it doesn't *produce* quality. Which leads to the failure mode that sinks most
catalog projects.

## The way catalogs fail

A catalog is only as good as the metadata in it, and metadata rots. The classic
project buys a catalog, runs a crawler to auto-populate technical schema, and then
asks humans to fill in the descriptions and ownership, the *valuable* part. Those
fields are filled in once, during the rollout, and never again. Six months later the
catalog is a confident, comprehensive, and badly out-of-date map: descriptions for
columns that changed, owners who left, terms nobody uses anymore.

This is, underneath, the same thing that sinks data quality programs, [an org-chart
problem](/essays/data-quality-problems-are-org-chart-problems/) wearing a tooling
costume. A catalog with no one accountable for keeping entries current is a
documentation graveyard, exactly as unowned datasets become orphaned tables. The tool
doesn't supply the discipline; it only stores it.

## When you actually need one

The honest threshold: you need a catalog when the data estate has **outgrown human
memory.** Concretely —

- **Scale.** Hundreds of tables across multiple systems and teams, where no single
  person can answer "what do we have and what does it mean?"
- **Onboarding pain.** New people routinely lose weeks just locating and understanding
  data before they can produce anything.
- **Compliance.** You must demonstrate what sensitive data you hold and where it flows
  — a catalog with lineage is often the system of record for that.

Below that threshold (a focused team with a few dozen well-named tables in one
warehouse) a catalog is machinery without a mission. A tidy schema, consistent
naming, and a maintained README in the repo *are* your catalog, and they won't rot
the way an under-loved tool will.

## If you do adopt one

The sequencing matters more than the tool choice, and it has its own field note:
[how to build a data catalog](/essays/how-to-build-a-data-catalog/) walks the
order that works: automate first, assign ownership second, buy last.
Make it work by attacking the failure mode directly. **Auto-populate everything that
can be** (schema, lineage, usage stats, freshness) straight from your systems, so the
machine-maintainable metadata stays current on its own. Then make the human
metadata, descriptions and ownership, *someone's explicit, ongoing job*, ideally tied to
the same [ownership and contracts](/essays/data-contracts-are-a-cultural-problem/) that
make the underlying data trustworthy in the first place. A catalog isn't a substitute
for governance; it's a place to *see* the governance you've already done. Get the
ownership right and the catalog becomes genuinely valuable. Skip it, and you've bought
a very searchable record of how your data used to be organized.

One practical note on the "auto-populate" half: the harvesting problem is now
largely standardised, and you can read the standard rather than trusting a
vendor's account of it. [OpenLineage](https://openlineage.io/docs/) defines the
event model that pipelines emit, and the open-source
[DataHub](https://docs.datahub.com/) and
[OpenMetadata](https://docs.open-metadata.org/) projects publish their metadata
models in full, useful as an evaluation yardstick even if you end up buying.
