---
last_modified_at: 2026-07-24
title: "Knowledge Graph"
description: "A knowledge graph stores entities and the relationships between them, optimized for traversing connections rather than aggregating rows."
essay: knowledge-graph-vs-data-warehouse
related_terms:
  - ontology
  - data-warehouse
  - vector-database
---

A **knowledge graph** represents information as **nodes** (entities) and
**edges** (relationships), with both treated as first-class. Its optimization is
traversal: following connections several hops out — customer to account to
transaction to counterparty — without knowing the path in advance, which is
awkward and slow to express as SQL self-joins.

That makes it complementary to, not a replacement for, a
[data warehouse](/glossary/data-warehouse/): the warehouse aggregates rows into
measures, the graph walks relationships into context. Graphs earn their place
where connection *is* the analysis — fraud rings, entity resolution, supply-chain
dependency, [lineage](/glossary/data-lineage/) — and they've returned to
prominence for AI grounding, because retrieval over explicit relationships holds
up on multi-entity questions where pure
[vector search](/glossary/vector-database/) degrades. A knowledge graph is
usually governed by an [ontology](/glossary/ontology/) that defines what its
nodes and edges mean.
