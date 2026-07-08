---
title: "Reverse ETL"
description: "Reverse ETL syncs modelled data from the warehouse back into operational tools — CRMs, ad platforms, support systems — so business teams act on it where they work."
related_terms:
  - etl
  - elt
  - semantic-layer
---

**Reverse ETL** moves data in the opposite direction from every other pipeline:
*out* of the warehouse and back *into* operational tools — customer segments to
the CRM, churn scores to the support desk, audiences to ad platforms. The
warehouse stops being a read-only endpoint and becomes the source feeding the
tools where business teams actually work.

The pattern's value depends entirely on what it ships: it puts your best,
modelled data (ideally definitions from the
[semantic layer](/glossary/semantic-layer/)) where decisions happen — but it
also turns dashboard bugs into operational incidents. A wrong number on a chart
misleads someone; a wrong number synced into the CRM emails ten thousand
customers. Treat reverse ETL pipelines with production-grade rigour.
