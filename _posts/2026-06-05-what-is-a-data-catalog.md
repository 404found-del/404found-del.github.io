---
title: "What Is a Data Catalog, and Do You Need One?"
kicker: "Field Notes"
topic: "Governance"
description: "A data catalog is a searchable inventory of an organization's data — what exists, where it lives, what it means, and who owns it. Here's what it's for, what it isn't, and when you actually need one."
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
catalog is the tool that answers it. Useful idea — and, like most governance tools,
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

## What it is *not*

Two confusions cause most disappointed catalog rollouts.

**It is not a [semantic layer](/glossary/semantic-layer/).** A catalog *documents* that a `revenue` column exists
and describes it in prose. A [semantic layer](/essays/what-is-a-semantic-layer/)
*defines and computes* revenue consistently for every consumer at query time. One
helps you find and understand data; the other governs and serves the actual numbers.
A catalog full of beautiful descriptions of three conflicting `revenue` columns has
documented your inconsistency, not resolved it.

> A catalog tells you what data exists and what it's supposed to mean. It does not
> make the data correct, consistent, or trustworthy — it describes the estate, it
> doesn't govern it.

**It is not a quality tool.** The catalog can display a freshness or quality score,
but it doesn't *produce* quality. Which leads to the failure mode that sinks most
catalog projects.

## The way catalogs fail

A catalog is only as good as the metadata in it, and metadata rots. The classic
project buys a catalog, runs a crawler to auto-populate technical schema, and then
asks humans to fill in the descriptions and ownership — the *valuable* part. Those
fields are filled in once, during the rollout, and never again. Six months later the
catalog is a confident, comprehensive, and badly out-of-date map: descriptions for
columns that changed, owners who left, terms nobody uses anymore.

This is, underneath, the same thing that sinks data quality programs — [an org-chart
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

Below that threshold — a focused team with a few dozen well-named tables in one
warehouse — a catalog is machinery without a mission. A tidy schema, consistent
naming, and a maintained README in the repo *are* your catalog, and they won't rot
the way an under-loved tool will.

## If you do adopt one

The sequencing matters more than the tool choice, and it has its own field note:
[how to build a data catalog](/essays/how-to-build-a-data-catalog/) walks the
order that works — automate first, assign ownership second, buy last.
Make it work by attacking the failure mode directly. **Auto-populate everything that
can be** — schema, lineage, usage stats, freshness — straight from your systems, so the
machine-maintainable metadata stays current on its own. Then make the human
metadata — descriptions, ownership — *someone's explicit, ongoing job*, ideally tied to
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
models in full — useful as an evaluation yardstick even if you end up buying.
