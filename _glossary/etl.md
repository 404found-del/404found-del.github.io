---
title: "ETL (Extract, Transform, Load)"
description: "ETL extracts data from sources, transforms it before loading, and loads the finished result into the warehouse — transformation happens outside the destination."
essay: etl-vs-elt
related_terms:
  - elt
  - data-warehouse
---

**ETL** — extract, transform, load — is the pipeline pattern in which data is
transformed *before* it reaches the destination: pulled from sources, reshaped
and cleaned on separate processing infrastructure, and loaded into the warehouse
already finished. Only prepared data lands.

ETL made sense when warehouse compute was scarce and expensive; its costs are
that transformation logic lives outside the warehouse (harder for analysts to
see or change) and raw data is often discarded, so history can't be
re-derived. Its modern successor, [ELT](/glossary/elt/), loads raw data first
and transforms inside the warehouse — but ETL survives wherever data must be
cleaned, masked, or contracted before it's allowed to land.
