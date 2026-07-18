---
last_modified_at: 2026-07-06
title: "Factless Fact Table"
description: "A factless fact table records that an event or condition occurred — with no numeric measures — such as attendance, eligibility, or a promotion being active."
essay: factless-fact-tables
related_terms:
  - fact-table
  - grain
---

A **factless fact table** is a [fact table](/glossary/fact-table/) with no
numeric measures: each row simply records that an event happened or a condition
held — a student attended a class, a product was on promotion on a date, a
customer was eligible for an offer. The row itself is the fact; counting rows is
the analysis.

The pattern covers two cases: **events** (things that occurred but have no
natural magnitude) and **coverage** (what *could* have happened — which, compared
against an activity fact, answers questions like "which promoted products didn't
sell?"). A factless table still needs a rigorously declared
[grain](/glossary/grain/); it just carries context keys and no measures.
