---
title: "Fact Table"
description: "A fact table stores the measurements of a business process — one row per event at a declared grain, carrying numeric measures and foreign keys to dimensions."
essay: fact-table-vs-dimension-table
related_terms:
  - dimension-table
  - grain
  - factless-fact-table
---

A **fact table** is the table in a dimensional model that stores measurements:
the numeric events a business wants to analyse, such as sales amounts, quantities,
or durations. Each row records one measurement event at a declared
[grain](/glossary/grain/) — one order line, one payment, one sensor reading — and
carries the numeric **measures** plus foreign keys to the
[dimension tables](/glossary/dimension-table/) that give those numbers context.

Fact tables are long and narrow: billions of rows, few columns. They come in three
types — transaction, periodic snapshot, and accumulating snapshot — distinguished
entirely by what one row represents. The discipline that keeps a fact table
trustworthy is grain: every measure in the table must be true at the declared
grain, or aggregates silently double-count.
