---
title: "Kimball vs Inmon: Two Ways to Build a Data Warehouse"
kicker: "Field Notes"
topic: "Architecture"
description: "Kimball and Inmon differ on one decision: build dimensional marts bottom-up, or a normalized enterprise warehouse top-down. The trade-off, and the modern blend."
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
simpler than that. The two approaches differ on exactly one decision, *what you
build first*, and once you see that decision clearly, choosing between them (or,
more honestly, blending them) becomes a question about your constraints rather than
your allegiances.

## The one decision

Both men wanted the same end state: an organization that can analyze its data
reliably. They disagreed on the order of operations.

**Inmon says top-down.** Build a single, centralized, normalized **enterprise data
warehouse** first, the integrated source of truth for the whole company, and then
spin off dimensional data marts from it for individual departments.

**Kimball says bottom-up.** Build **dimensional data marts** for individual business
processes directly, and let the enterprise warehouse *emerge* from those marts as
they're connected through shared, [conformed dimensions](/glossary/conformed-dimension/).

That's the whole fork. Integrate first and deliver later (Inmon), or deliver first
and integrate as you go (Kimball). Everything else, from the schemas to the methodologies to
the famous diagrams, follows from this single choice about sequence.

Both positions are still available in the authors' own words, which is worth
reading before accepting anyone's summary of them, including this one. The
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
single version of truth, strong consistency, and a structure resilient to change:
the same virtues that make normalized [OLTP schemas](/essays/oltp-vs-olap/)
trustworthy, applied to the warehouse. For a large enterprise wrangling dozens of
overlapping source systems, that disciplined central integration is the point.

The cost is time and effort. You're building a comprehensive enterprise model
*before* the business sees much value, which is slow, expensive, and demands serious
data-modeling maturity. The first useful dashboard can be a long way off.

## Kimball: dimensional marts, connected as you go

The Kimball approach inverts the priority toward **business value, fast**. You build
[star schemas](/essays/star-schema-vs-snowflake-schema/) for one business process at
a time (sales, then shipping, then support), each immediately useful to the people
who need it. The enterprise warehouse isn't built up front; it materializes as those
marts share [conformed dimensions](/essays/conformed-dimensions/), the "bus
architecture" that lets separate stars be compared and combined.

The appeal is speed and accessibility. You deliver a working, query-friendly mart
quickly, the dimensional structure is intuitive for analysts and BI tools, and you
build incrementally rather than betting years on a grand model. Value arrives early
and compounds.

> Inmon builds the whole house and then furnishes the rooms. Kimball furnishes one
> room at a time and makes sure the doors line up. Both end with a finished house;
> the difference is when anyone can start living in it.

The cost is that integration is *your discipline to enforce*. If you don't hold the
line on conformed dimensions, Kimball's bottom-up freedom degrades into a pile of
disconnected marts that each define "customer" differently, the very silos the
approach was supposed to prevent. The conformity is doing the integration work that
Inmon does up front; skip it and the method quietly fails.

<figure style="margin:2rem auto;text-align:center;">
<svg class="dia-mob" viewBox="0 0 400 640" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="kvi-mt kvi-md">
  <title id="kvi-mt">Inmon top-down versus Kimball bottom-up</title>
  <desc id="kvi-md">Two build orders from the same sources. Inmon, shown first, integrates every source into a normalized enterprise warehouse first and derives dependent dimensional marts from it afterwards. Kimball, shown below, builds dimensional marts per business process directly, and the enterprise view emerges as those marts come to share conformed dimensions. Integration first and delivery later, or delivery first and integration as you go.</desc>
  <text x="200" y="22" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Inmon — top-down</text>
  <rect x="40" y="36" width="320" height="28" rx="4" fill="#1c1a17"/>
  <text x="200" y="55" font-size="11" fill="#f6f3ec" text-anchor="middle">source systems</text>
  <line x1="200" y1="64" x2="200" y2="92" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="92" width="320" height="60" rx="6" fill="#c8472b"/>
  <text x="200" y="117" font-size="12" fill="#f6f3ec" text-anchor="middle" font-weight="700">enterprise warehouse — 3NF</text>
  <text x="200" y="137" font-size="10" fill="#f6f3ec" text-anchor="middle">built first · integrated · governed</text>
  <line x1="100" y1="152" x2="88" y2="186" stroke="#cabfac" stroke-width="2"/>
  <line x1="200" y1="152" x2="200" y2="186" stroke="#cabfac" stroke-width="2"/>
  <line x1="300" y1="152" x2="312" y2="186" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="186" width="96" height="34" rx="4" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.4"/>
  <text x="88" y="208" font-size="10" fill="#1c1a17" text-anchor="middle">mart</text>
  <rect x="152" y="186" width="96" height="34" rx="4" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.4"/>
  <text x="200" y="208" font-size="10" fill="#1c1a17" text-anchor="middle">mart</text>
  <rect x="264" y="186" width="96" height="34" rx="4" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.4"/>
  <text x="312" y="208" font-size="10" fill="#1c1a17" text-anchor="middle">mart</text>
  <text x="200" y="244" font-size="10" fill="#8b857a" text-anchor="middle">marts are dependent — derived from the core</text>
  <text x="200" y="266" font-size="10" fill="#a4391f" text-anchor="middle">value arrives late · consistency by construction</text>
  <line x1="30" y1="292" x2="370" y2="292" stroke="#ddd6c8" stroke-width="1.5" stroke-dasharray="4 4"/>
  <text x="200" y="322" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Kimball — bottom-up</text>
  <rect x="40" y="336" width="320" height="28" rx="4" fill="#1c1a17"/>
  <text x="200" y="355" font-size="11" fill="#f6f3ec" text-anchor="middle">source systems</text>
  <line x1="88" y1="364" x2="88" y2="392" stroke="#cabfac" stroke-width="2"/>
  <line x1="200" y1="364" x2="200" y2="392" stroke="#cabfac" stroke-width="2"/>
  <line x1="312" y1="364" x2="312" y2="392" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="392" width="96" height="52" rx="4" fill="#c8472b"/>
  <text x="88" y="414" font-size="10" fill="#f6f3ec" text-anchor="middle">sales</text>
  <text x="88" y="432" font-size="11" fill="#f6f3ec" text-anchor="middle">star</text>
  <rect x="152" y="392" width="96" height="52" rx="4" fill="#c8472b"/>
  <text x="200" y="414" font-size="10" fill="#f6f3ec" text-anchor="middle">shipping</text>
  <text x="200" y="432" font-size="11" fill="#f6f3ec" text-anchor="middle">star</text>
  <rect x="264" y="392" width="96" height="52" rx="4" fill="#c8472b"/>
  <text x="312" y="414" font-size="10" fill="#f6f3ec" text-anchor="middle">support</text>
  <text x="312" y="432" font-size="11" fill="#f6f3ec" text-anchor="middle">star</text>
  <line x1="88" y1="444" x2="88" y2="478" stroke="#cabfac" stroke-width="2"/>
  <line x1="200" y1="444" x2="200" y2="478" stroke="#cabfac" stroke-width="2"/>
  <line x1="312" y1="444" x2="312" y2="478" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="478" width="320" height="46" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="498" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">conformed dimensions</text>
  <text x="200" y="516" font-size="10" fill="#56514a" text-anchor="middle">the bus that makes the marts one warehouse</text>
  <text x="200" y="552" font-size="10" fill="#8b857a" text-anchor="middle">the enterprise view emerges from the marts</text>
  <text x="200" y="574" font-size="10" fill="#a4391f" text-anchor="middle">value arrives early · consistency is your discipline</text>
  <text x="200" y="608" font-size="10" fill="#8b857a" text-anchor="middle">each method's signature weakness</text>
  <text x="200" y="624" font-size="10" fill="#8b857a" text-anchor="middle">is the other's signature strength</text>
</svg>
<svg class="dia-desk" viewBox="0 0 800 360" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="kimball-vs-inmon-t kimball-vs-inmon-d">
  <title id="kimball-vs-inmon-t">Inmon top-down versus Kimball bottom-up</title>
  <desc id="kimball-vs-inmon-d">Two build orders from the same sources. Inmon, on the left, integrates every source into a normalized enterprise warehouse first and derives dependent dimensional marts from it afterwards. Kimball, on the right, builds dimensional marts per business process directly, and the enterprise view emerges as those marts come to share conformed dimensions. Integration first and delivery later, or delivery first and integration as you go.</desc>
  <text x="200" y="26" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Inmon — top-down</text>
  <text x="600" y="26" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Kimball — bottom-up</text>
  <rect x="60" y="44" width="280" height="30" rx="4" fill="#1c1a17"/>
  <text x="200" y="64" font-size="11" fill="#f6f3ec" text-anchor="middle">source systems</text>
  <line x1="200" y1="74" x2="200" y2="104" stroke="#cabfac" stroke-width="2"/>
  <rect x="60" y="104" width="280" height="66" rx="6" fill="#c8472b"/>
  <text x="200" y="130" font-size="13" fill="#f6f3ec" text-anchor="middle" font-weight="700">enterprise warehouse — 3NF</text>
  <text x="200" y="152" font-size="10" fill="#f6f3ec" text-anchor="middle">built first · integrated · governed</text>
  <line x1="120" y1="170" x2="105" y2="204" stroke="#cabfac" stroke-width="2"/>
  <line x1="200" y1="170" x2="200" y2="204" stroke="#cabfac" stroke-width="2"/>
  <line x1="280" y1="170" x2="295" y2="204" stroke="#cabfac" stroke-width="2"/>
  <rect x="62" y="204" width="86" height="34" rx="4" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.4"/>
  <text x="105" y="226" font-size="10" fill="#1c1a17" text-anchor="middle">mart</text>
  <rect x="157" y="204" width="86" height="34" rx="4" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.4"/>
  <text x="200" y="226" font-size="10" fill="#1c1a17" text-anchor="middle">mart</text>
  <rect x="252" y="204" width="86" height="34" rx="4" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.4"/>
  <text x="295" y="226" font-size="10" fill="#1c1a17" text-anchor="middle">mart</text>
  <text x="200" y="266" font-size="10" fill="#8b857a" text-anchor="middle">marts are dependent — derived from the core</text>
  <text x="200" y="290" font-size="10" fill="#a4391f" text-anchor="middle">value arrives late · consistency by construction</text>
  <rect x="460" y="44" width="280" height="30" rx="4" fill="#1c1a17"/>
  <text x="600" y="64" font-size="11" fill="#f6f3ec" text-anchor="middle">source systems</text>
  <line x1="505" y1="74" x2="505" y2="104" stroke="#cabfac" stroke-width="2"/>
  <line x1="600" y1="74" x2="600" y2="104" stroke="#cabfac" stroke-width="2"/>
  <line x1="695" y1="74" x2="695" y2="104" stroke="#cabfac" stroke-width="2"/>
  <rect x="462" y="104" width="86" height="52" rx="4" fill="#c8472b"/>
  <text x="505" y="127" font-size="10" fill="#f6f3ec" text-anchor="middle">sales</text>
  <text x="505" y="144" font-size="11" fill="#f6f3ec" text-anchor="middle">star</text>
  <rect x="557" y="104" width="86" height="52" rx="4" fill="#c8472b"/>
  <text x="600" y="127" font-size="10" fill="#f6f3ec" text-anchor="middle">shipping</text>
  <text x="600" y="144" font-size="11" fill="#f6f3ec" text-anchor="middle">star</text>
  <rect x="652" y="104" width="86" height="52" rx="4" fill="#c8472b"/>
  <text x="695" y="127" font-size="10" fill="#f6f3ec" text-anchor="middle">support</text>
  <text x="695" y="144" font-size="11" fill="#f6f3ec" text-anchor="middle">star</text>
  <line x1="505" y1="156" x2="505" y2="192" stroke="#cabfac" stroke-width="2"/>
  <line x1="600" y1="156" x2="600" y2="192" stroke="#cabfac" stroke-width="2"/>
  <line x1="695" y1="156" x2="695" y2="192" stroke="#cabfac" stroke-width="2"/>
  <rect x="460" y="192" width="280" height="46" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="600" y="212" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">conformed dimensions</text>
  <text x="600" y="230" font-size="11" fill="#56514a" text-anchor="middle">the bus that makes the marts one warehouse</text>
  <text x="600" y="266" font-size="10" fill="#8b857a" text-anchor="middle">the enterprise view emerges from the marts</text>
  <text x="600" y="290" font-size="10" fill="#a4391f" text-anchor="middle">value arrives early · consistency is your discipline</text>
  <line x1="400" y1="40" x2="400" y2="300" stroke="#ddd6c8" stroke-width="1.5" stroke-dasharray="4 4"/>
  <text x="400" y="334" font-size="12" fill="#8b857a" text-anchor="middle">each method's signature weakness is the other's signature strength</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">One decision, two orders: integrate first and deliver later, or deliver first and integrate as you go.</figcaption>
</figure>

## The real trade-off

Strip away the dogma and it's a familiar tension: **integration-first versus
delivery-first.** Inmon pays the integration cost up front and reaps consistency;
Kimball pays it incrementally and reaps speed. Inmon risks never shipping; Kimball
risks never integrating. Each method's signature weakness is exactly the other's
signature strength, which is the surest sign that neither is simply "right."

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
this blend wearing new names, and [Data Vault](/essays/data-vault-vs-dimensional-modeling/)
is a third method aimed squarely at that integration layer. (Inmon's side of the
argument is worth reading on its own terms rather than through Kimball's summary
of it — [the Corporate Information Factory, with a worked
example](/essays/the-inmon-methodology/), is what the top-down method actually
builds.)

So the honest answer to "Kimball or Inmon?" in 2026 is usually *both, at different
layers*: an integrated foundation for trust, dimensional marts for use. And when you
ask which philosophy dominates the layer your analysts actually touch, the answer is
almost always Kimball: for analytics consumption, dimensional models won. The war
became a spectrum, and most teams now live comfortably in the middle of it —
delivering Kimball-style value on an Inmon-style foundation, and arguing about the
labels far less than their predecessors did.
