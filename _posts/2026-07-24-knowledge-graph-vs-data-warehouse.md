---
title: "Knowledge Graph vs Data Warehouse: Aggregation vs Connection"
kicker: "Field Notes"
topic: "Architecture"
description: "A warehouse answers how much; a knowledge graph answers how things connect. They're different query shapes, not rivals — and most serious estates end up with both."
date: 2026-07-24 11:00:00 +0530
last_modified_at: 2026-07-26
faq:
  - q: "What is the difference between a knowledge graph and a data warehouse?"
    a: "A data warehouse stores modelled, mostly tabular data optimized for aggregation — sum, group, filter across millions of rows. A knowledge graph stores entities and the relationships between them, optimized for traversal — following connections several hops out. The warehouse answers 'how much, by what'; the graph answers 'what connects to what, and how.'"
  - q: "Does a knowledge graph replace a data warehouse?"
    a: "No, and the framing is the mistake. They serve different query shapes and usually coexist: the warehouse stays the system of record for reporting and metrics, while the graph sits alongside as a relationship and context layer. Replacing a warehouse with a graph means doing aggregate analytics on an engine that wasn't built for it."
  - q: "When is a knowledge graph actually worth it?"
    a: "When relationships are the analytical product rather than context for a measure — fraud rings, supply-chain dependency, entity resolution across systems, drug interactions, org hierarchies — or when questions need many hops and the SQL becomes a tangle of self-joins. If your questions are 'revenue by region by quarter,' the warehouse is not the problem."
  - q: "Why are knowledge graphs coming up in AI conversations?"
    a: "Because retrieval quality collapses on multi-entity questions. Vector search finds text that looks similar; a graph traverses actual relationships, which is why GraphRAG approaches hold up on questions involving many connected entities where pure vector retrieval degrades. The graph supplies the structure that embeddings alone can't recover."
---

The comparison is usually framed as a contest, and that framing is why teams get
it wrong. **A data warehouse is built to aggregate: sum, group, and filter across
enormous numbers of rows. A knowledge graph is built to traverse: follow the
relationships between entities, several hops out, without knowing the path in
advance.** Those are different query *shapes*, not competing products — and the
right question isn't which to buy, it's which shape your hard questions actually
have. Most mature estates end up with both: the
[warehouse](/glossary/data-warehouse/) as the system of record for metrics, the
graph as the layer that understands how things connect.

## Data warehouse vs knowledge graph, side by side

| | Data warehouse | Knowledge graph |
|---|---|---|
| **Optimized for** | Aggregation over many rows | Traversal across relationships |
| **Answers** | How much, by what, over what period | What connects to what, and how far |
| **Shape** | Tables, [facts and dimensions](/essays/fact-table-vs-dimension-table/) | Nodes and edges, both first-class |
| **Schema** | Declared up front, enforced | Flexible, extended as you learn |
| **Query language** | SQL | Cypher, SPARQL, GQL |
| **Multi-hop questions** | Painful — self-joins pile up | Native — that's the design |
| **Aggregate questions** | Native and fast | Possible, rarely as fast |
| **Meaning lives in** | Models + [semantic layer](/essays/what-is-a-semantic-layer/) | The graph itself, plus its ontology |
| **Typical role** | System of record for reporting | Reasoning and context layer |

## The query shape is the whole argument

The clearest way to feel the difference is to write the same business question
both ways. *"Which suppliers are we exposed to through our suppliers' suppliers?"*
In SQL, unknown depth means either a recursive CTE or a stack of self-joins that
grows with every hop:

```sql
-- Warehouse: multi-hop needs recursion, and gets awkward fast
WITH RECURSIVE chain AS (
  SELECT supplier_id, depends_on_id, 1 AS hop
  FROM   fact_supplier_dependency
  WHERE  supplier_id = :root
  UNION ALL
  SELECT c.supplier_id, d.depends_on_id, c.hop + 1
  FROM   chain c
  JOIN   fact_supplier_dependency d ON d.supplier_id = c.depends_on_id
  WHERE  c.hop < 5                       -- depth you must guess in advance
)
SELECT DISTINCT depends_on_id FROM chain;
```

```cypher
// Graph: depth is a parameter of the traversal, not a rewrite of the query
MATCH (s:Supplier {id: $root})-[:DEPENDS_ON*1..5]->(exposed:Supplier)
RETURN DISTINCT exposed;
```

Now reverse it. *"What was revenue by region by quarter?"* is one clean
`GROUP BY` in the warehouse and an awkward, slower aggregation in most graphs.
Neither engine is better; each is built for a different question, and choosing
by hype rather than by query shape is how teams end up with an expensive graph
serving dashboards, or a warehouse full of self-joins nobody can maintain.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 330" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="knowledge-graph-vs-data-warehouse-t knowledge-graph-vs-data-warehouse-d">
  <title id="knowledge-graph-vs-data-warehouse-t">Aggregation versus traversal</title>
  <desc id="knowledge-graph-vs-data-warehouse-d">On the left, a warehouse: stacked rows collapsing into a single aggregated number via SUM and GROUP BY. On the right, a knowledge graph: a starting node with edges followed outward through intermediate nodes to entities three hops away. Choose by the shape of your hardest question.</desc>
  <text x="200" y="30" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Warehouse — aggregation</text>
  <rect x="70" y="46" width="260" height="22" rx="3" fill="#c8472b"/>
  <rect x="70" y="72" width="260" height="14" rx="3" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.2"/>
  <rect x="70" y="90" width="260" height="14" rx="3" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.2"/>
  <rect x="70" y="108" width="260" height="14" rx="3" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.2"/>
  <rect x="70" y="126" width="260" height="14" rx="3" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.2"/>
  <rect x="70" y="144" width="260" height="14" rx="3" fill="#f6f3ec" stroke="#ddd6c8" stroke-width="1.2"/>
  <text x="200" y="186" font-size="11" fill="#56514a" text-anchor="middle">millions of rows ↓ one number</text>
  <text x="200" y="206" font-size="11" fill="#8b857a" text-anchor="middle">SUM(amount) GROUP BY region, quarter</text>
  <text x="600" y="30" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Knowledge graph — traversal</text>
  <circle cx="600" cy="70" r="16" fill="#c8472b"/>
  <text x="600" y="74" font-size="11" fill="#f6f3ec" text-anchor="middle">you</text>
  <circle cx="520" cy="120" r="14" fill="#1c1a17"/>
  <circle cx="680" cy="120" r="14" fill="#1c1a17"/>
  <circle cx="470" cy="176" r="12" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <circle cx="570" cy="176" r="12" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <circle cx="660" cy="176" r="12" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <circle cx="730" cy="176" r="12" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <line x1="600" y1="86" x2="520" y2="106" stroke="#cabfac" stroke-width="2"/>
  <line x1="600" y1="86" x2="680" y2="106" stroke="#cabfac" stroke-width="2"/>
  <line x1="520" y1="134" x2="470" y2="164" stroke="#ddd6c8" stroke-width="1.5"/>
  <line x1="520" y1="134" x2="570" y2="164" stroke="#ddd6c8" stroke-width="1.5"/>
  <line x1="680" y1="134" x2="660" y2="164" stroke="#ddd6c8" stroke-width="1.5"/>
  <line x1="680" y1="134" x2="730" y2="164" stroke="#ddd6c8" stroke-width="1.5"/>
  <text x="600" y="206" font-size="11" fill="#8b857a" text-anchor="middle">follow edges → exposure three hops out</text>
  <text x="400" y="262" font-size="12" fill="#8b857a" text-anchor="middle">choose by the shape of your hardest question, not by which technology is fashionable</text>
  <text x="400" y="288" font-size="12" fill="#8b857a" text-anchor="middle">"how much, by what" → warehouse ·  "what connects to what" → graph</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">Two engines, two query shapes: collapsing rows into a number, or walking edges into context.</figcaption>
</figure>

## Where the graph genuinely wins

Four situations, and they share a signature — *the relationships are the
product*, not context for a measure:

- **Fraud and risk rings** — the suspicious thing isn't any account, it's the
  shape of the connections between accounts.
- **Entity resolution across systems** — the same customer under four
  identifiers, discovered by how records relate rather than by matching strings.
- **Dependency and impact analysis** — supply chains, and the
  [data lineage](/essays/what-is-data-lineage/) graph you already rely on, which
  is a knowledge graph whether or not anyone calls it one.
- **Domains where connection *is* the science** — drug interactions, genomics,
  org and identity hierarchies.

If your hardest questions are none of those, the honest answer is that your
warehouse isn't the problem and a graph won't fix it.

## The AI angle, without the hype

Graphs re-entered the conversation through retrieval. Vector search finds
passages that *look* semantically similar, which works well for
"find documents about the refund policy" and degrades badly on questions that
span several connected entities — the retriever has no way to know that these
five facts belong to one chain of reasoning.
[GraphRAG](https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/)
approaches supply that structure explicitly, building an entity graph from the
corpus first and traversing it at query time — which is why they hold up on
multi-entity and whole-corpus questions where pure vector retrieval falls apart.

But notice what's actually doing the work: not the graph database — the
*explicit relationships*. That's the same asset an
[ontology](/essays/ontology-vs-data-model/) provides, the same asset
[conformed dimensions](/essays/conformed-dimensions/) provide inside a
warehouse, and the same reason a governed
[semantic layer](/essays/what-is-a-semantic-layer/) improves text-to-SQL
accuracy. Machines reason better when meaning and structure are declared instead
of inferred. Graphs are one good way to declare them; they are not the only one,
and buying one won't substitute for the modelling discipline underneath.

## The pragmatic architecture

For nearly every organisation the answer is **both, with clear roles**: the
warehouse or [lakehouse](/glossary/data-lakehouse/) remains the governed system
of record where metrics are defined and history is kept; the graph is built
*from* it as a derived layer serving relationship questions and AI grounding.
That ordering matters. A graph fed by an ungoverned warehouse inherits every
definitional argument you never settled — you end up with beautifully connected
wrong answers, which are harder to detect than plainly wrong ones, because the
traversal looks so convincing.

Get the meaning right first. Then choose the engine that matches the question.
