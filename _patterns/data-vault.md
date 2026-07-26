---
last_modified_at: 2026-07-18
title: "Data Vault"
intent: "Model the integration layer as hubs (business keys), links (relationships), and satellites (history), so the warehouse absorbs change without remodelling."
description: "The data vault pattern: hubs, links, and satellites, what it buys you in auditability and agility, its real costs, and when dimensional modeling is the better choice."
essays:
  - data-vault-vs-dimensional-modeling
  - kimball-vs-inmon
terms:
  - data-vault
  - data-warehouse
  - surrogate-key
  - natural-key
faq:
  - q: "What are hubs, links, and satellites in data vault?"
    a: "Hubs store just the business keys of entities (customer, order). Links store relationships between hubs. Satellites store the descriptive attributes and their full history, attached to a hub or link. Everything is append-only and stamped with load time and source."
  - q: "When should I use data vault instead of dimensional modeling?"
    a: "When you have many volatile sources, hard audit requirements, and the cost of remodelling marts on every source change has become unbearable — data vault absorbs change by adding tables. With few sources and no audit mandate, dimensional modeling alone is simpler and sufficient."
  - q: "Can you query a data vault directly?"
    a: "In practice, no — the hub/link/satellite split means even simple questions need many joins. A data vault is an integration layer; you build a presentation layer, usually star schemas, on top of it for analysts and BI tools."
---

## Intent

Build a warehouse integration layer that survives constant source-system change
and regulatory audit: every business key, relationship, and attribute history is
stored separately, append-only, with full lineage of where and when each fact
arrived.

## Context

Many volatile source systems feed one warehouse; auditability is a hard
requirement; and the cost of remodelling downstream marts every time a source
changes has become unbearable. Data vault deliberately splits *integration*
(the vault) from *presentation* (usually [star schemas](/patterns/star-schema/)
built on top).

## Structure

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="data-vault-t data-vault-d">
  <title id="data-vault-t">Data Vault structure: hubs, links, and satellites</title>
  <desc id="data-vault-d">Two hub tables holding only business keys, hub_customer and hub_order, joined by a link table representing the relationship between them. Satellite tables hang off each hub carrying descriptive attributes and their history. Hubs are keys, links are relationships, satellites are descriptive history.</desc>
  <rect x="60" y="110" width="170" height="70" rx="6" fill="#c8472b"/>
  <text x="145" y="140" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">hub_customer</text>
  <text x="145" y="162" font-size="11" fill="#f6f3ec" text-anchor="middle">business key only</text>
  <rect x="570" y="110" width="170" height="70" rx="6" fill="#c8472b"/>
  <text x="655" y="140" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">hub_order</text>
  <text x="655" y="162" font-size="11" fill="#f6f3ec" text-anchor="middle">business key only</text>
  <rect x="315" y="110" width="170" height="70" rx="6" fill="#1c1a17"/>
  <text x="400" y="140" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">link_places</text>
  <text x="400" y="162" font-size="11" fill="#f6f3ec" text-anchor="middle">relationship</text>
  <line x1="230" y1="145" x2="315" y2="145" stroke="#cabfac" stroke-width="2"/>
  <line x1="485" y1="145" x2="570" y2="145" stroke="#cabfac" stroke-width="2"/>
  <rect x="60" y="220" width="170" height="56" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="145" y="245" font-size="12" fill="#1c1a17" text-anchor="middle">sat_customer_details</text>
  <text x="145" y="264" font-size="11" fill="#56514a" text-anchor="middle">attributes + history</text>
  <line x1="145" y1="180" x2="145" y2="220" stroke="#ddd6c8" stroke-width="2"/>
  <rect x="570" y="220" width="170" height="56" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="655" y="245" font-size="12" fill="#1c1a17" text-anchor="middle">sat_order_status</text>
  <text x="655" y="264" font-size="11" fill="#56514a" text-anchor="middle">attributes + history</text>
  <line x1="655" y1="180" x2="655" y2="220" stroke="#ddd6c8" stroke-width="2"/>
  <text x="400" y="60" font-size="12" fill="#8b857a" text-anchor="middle">hubs = keys · links = relationships · satellites = descriptive history</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">Hubs hold keys, links hold relationships, satellites hold descriptive history — so sources can change shape without breaking the model.</figcaption>
</figure>

New sources or attributes mean *adding* tables — a new satellite, a new link —
never altering existing ones. Everything is append-only and stamped with load
time and record source.

## Trade-offs

**Gains:** insulation from source churn; complete, auditable history by
construction; highly parallel loads; new sources integrate without remodelling.

**Costs:** table count explodes (one entity becomes three-plus tables); queries
need many joins, so you *must* build a presentation layer on top — the vault is
not queryable by humans in practice; and the methodology demands real training
and discipline. It's an integration-layer pattern for large, regulated,
multi-source estates — not a default.

## When not to use it

Few sources, moderate change rate, no audit mandate, or a small team: go
[straight to dimensional](/essays/data-vault-vs-dimensional-modeling/). A vault
whose discipline lapses is the worst of both worlds — all the joins, none of the
guarantees.
