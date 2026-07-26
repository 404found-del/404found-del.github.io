---
title: "Kimball vs Inmon: Two Ways to Build a Data Warehouse"
kicker: "Field Notes"
topic: "Architecture"
description: "Kimball and Inmon are the two foundational approaches to building a data warehouse. The difference is one decision: build dimensional marts bottom-up, or a normalized enterprise warehouse top-down. Here's the real trade-off."
date: 2026-06-14
last_modified_at: 2026-07-26
faq:
  - q: "What is the main difference between Kimball and Inmon?"
    a: "Direction. Inmon is top-down: build one normalized, integrated enterprise data warehouse first, then derive dimensional data marts from it. Kimball is bottom-up: build dimensional data marts for individual business processes directly, and integrate them through conformed dimensions. Inmon front-loads integration; Kimball front-loads delivery."
  - q: "Which is better, Kimball or Inmon?"
    a: "Neither universally. Inmon suits large, complex enterprises that need a governed, integrated core and can fund the upfront effort. Kimball suits teams that need business value quickly and iteratively. Most modern builds lean Kimball for the consumption layer, often over an integrated layer underneath — a blend of both."
  - q: "Can you use Kimball and Inmon together?"
    a: "Yes, and many teams do. A common hybrid keeps a normalized or raw integration layer (Inmon-flavored) as the source of truth and serves dimensional marts (Kimball) on top for analytics. The modern layered warehouse is essentially this combination."
---

Two names have defined how organizations build [data warehouses](/glossary/data-warehouse/) for thirty years:
Ralph Kimball and Bill Inmon. The "Kimball vs Inmon" debate has consumed an
absurd amount of practitioner energy, usually framed as a doctrinal war. It's
simpler than that. The two approaches differ on exactly one decision — *what you
build first* — and once you see that decision clearly, choosing between them (or,
more honestly, blending them) becomes a question about your constraints rather than
your allegiances.

## The one decision

Both men wanted the same end state: an organization that can analyze its data
reliably. They disagreed on the order of operations.

**Inmon says top-down.** Build a single, centralized, normalized **enterprise data
warehouse** first — the integrated source of truth for the whole company — and then
spin off dimensional data marts from it for individual departments.

**Kimball says bottom-up.** Build **dimensional data marts** for individual business
processes directly, and let the enterprise warehouse *emerge* from those marts as
they're connected through shared, [conformed dimensions](/glossary/conformed-dimension/).

That's the whole fork. Integrate first and deliver later (Inmon), or deliver first
and integrate as you go (Kimball). Everything else — the schemas, the methodologies,
the famous diagrams — follows from this single choice about sequence.

Both positions are still available in the authors' own words, which is worth
reading before accepting anyone's summary of them — including this one. The
Kimball Group publishes its
[official dimensional modeling techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
in full and for free; Inmon's case is set out in *Building the Data Warehouse*
and the *Corporate Information Factory* books. Most of the heat in this debate
comes from summaries, not from sources.

## Inmon: the integrated core, built first

The Inmon approach treats the warehouse as a feat of enterprise engineering. You
model a **normalized** (third-normal-form) enterprise data warehouse that integrates
data from every source system into one consistent, non-redundant, governed
repository. Only once that integrated core exists do you build dimensional
[marts](/essays/a-field-guide-to-dimensional-modeling/) on top of it for specific
analytical needs.

The appeal is integration and integrity. Because everything flows through one
normalized core with carefully reconciled definitions, you get a genuine
single version of truth, strong consistency, and a structure resilient to change —
the same virtues that make normalized [OLTP schemas](/essays/oltp-vs-olap/)
trustworthy, applied to the warehouse. For a large enterprise wrangling dozens of
overlapping source systems, that disciplined central integration is the point.

The cost is time and effort. You're building a comprehensive enterprise model
*before* the business sees much value, which is slow, expensive, and demands serious
data-modeling maturity. The first useful dashboard can be a long way off.

## Kimball: dimensional marts, connected as you go

The Kimball approach inverts the priority toward **business value, fast**. You build
[star schemas](/essays/star-schema-vs-snowflake-schema/) for one business process at
a time — sales, then shipping, then support — each immediately useful to the people
who need it. The enterprise warehouse isn't built up front; it materializes as those
marts share [conformed dimensions](/essays/conformed-dimensions/), the "bus
architecture" that lets separate stars be compared and combined.

The appeal is speed and accessibility. You deliver a working, query-friendly mart
quickly, the dimensional structure is intuitive for analysts and BI tools, and you
build incrementally rather than betting years on a grand model. Value arrives early
and compounds.

> Inmon builds the whole house and then furnishes the rooms. Kimball furnishes one
> room at a time and makes sure the doors line up. Both end with a finished house —
> the difference is when anyone can start living in it.

The cost is that integration is *your discipline to enforce*. If you don't hold the
line on conformed dimensions, Kimball's bottom-up freedom degrades into a pile of
disconnected marts that each define "customer" differently — the very silos the
approach was supposed to prevent. The conformity is doing the integration work that
Inmon does up front; skip it and the method quietly fails.

## The real trade-off

Strip away the dogma and it's a familiar tension: **integration-first versus
delivery-first.** Inmon pays the integration cost up front and reaps consistency;
Kimball pays it incrementally and reaps speed. Inmon risks never shipping; Kimball
risks never integrating. Each method's signature weakness is exactly the other's
signature strength — which is the surest sign that neither is simply "right."

Choose by your constraints. Inmon fits when you're a **large, complex organization**
with many sources, hard governance requirements, and the time and modeling talent to
build a central core properly. Kimball fits when you need to **show value quickly**,
iterate with the business, and can commit to the conformed-dimension discipline that
keeps the marts coherent.

## Why the cloud softened the war

Here's the part that makes the old debate feel dated. Kimball and Inmon argued in an
era of expensive storage and scarce compute, when *where* you spent your modeling
effort had real hardware consequences. The cloud changed the economics. Storage is
cheap, [ELT](/glossary/elt/) is normal, and most modern teams build a **layered architecture** that
quietly borrows from both: a raw and integrated layer underneath (Inmon's instinct
for an integrated source of truth, even if not strictly 3NF) feeding dimensional
marts on top (Kimball's instinct for business-friendly consumption). The
[medallion architecture](/essays/the-medallion-architecture-reconsidered/) and the
modern [lakehouse](/essays/data-warehouse-vs-data-lake-vs-lakehouse/) are, in effect,
this blend wearing new names — and [Data Vault](/essays/data-vault-vs-dimensional-modeling/)
is a third method aimed squarely at that integration layer. (Inmon's side of the
argument is worth reading on its own terms rather than through Kimball's summary
of it — [the Corporate Information Factory, with a worked
example](/essays/the-inmon-methodology/), is what the top-down method actually
builds.)

So the honest answer to "Kimball or Inmon?" in 2026 is usually *both, at different
layers* — an integrated foundation for trust, dimensional marts for use. And when you
ask which philosophy dominates the layer your analysts actually touch, the answer is
almost always Kimball: for analytics consumption, dimensional models won. The war
became a spectrum, and most teams now live comfortably in the middle of it —
delivering Kimball-style value on an Inmon-style foundation, and arguing about the
labels far less than their predecessors did.
