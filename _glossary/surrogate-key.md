---
title: "Surrogate Key"
description: "A surrogate key is a meaningless, system-generated identifier used as a dimension table's primary key instead of the source system's natural key."
essay: surrogate-keys-vs-natural-keys
related_terms:
  - natural-key
  - dimension-table
  - slowly-changing-dimension
---

A **surrogate key** is a meaningless, system-generated identifier — an integer
sequence or hash — used as the primary key of a
[dimension table](/glossary/dimension-table/) in place of the source system's own
identifier (the [natural key](/glossary/natural-key/)).

Surrogates exist because source keys can't be trusted with history: they get
recycled, change format, collide across systems, and can't represent multiple
versions of the same entity. A surrogate key decouples the warehouse from all of
that — most importantly, it's what allows a Type 2
[slowly changing dimension](/glossary/slowly-changing-dimension/) to hold several
rows for one customer, each version with its own key, so facts join to the
version that was true when the fact happened.
