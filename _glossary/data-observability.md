---
title: "Data Observability"
description: "Data observability is automated monitoring of data health in production — freshness, volume, schema, and distribution — so teams detect bad data before consumers do."
related_terms:
  - data-lineage
  - data-contract
  - data-catalog
---

**Data observability** is the practice of monitoring the *health of data
itself* in production — not whether the pipeline ran, but whether what it
delivered is right. The standard signals: **freshness** (did the table update on
schedule?), **volume** (did row counts swing abnormally?), **schema** (did a
column change or vanish?), and **distribution** (did nulls, duplicates, or value
ranges drift?).

Observability tools learn baselines from history and alert on anomalies, using
[lineage](/glossary/data-lineage/) to trace an incident to its upstream cause
and its downstream blast radius. It complements, not replaces, explicit quality
rules and [data contracts](/glossary/data-contract/): contracts catch the
violations you anticipated; observability catches the ones you didn't.
