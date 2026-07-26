---
title: "What Is a Vector Database, and Do You Need One?"
kicker: "Field Notes"
topic: "AI"
description: "A vector database stores embeddings and finds items by meaning rather than exact match. Here's what that's actually for, how it relates to your existing stack, and when a dedicated one is worth it."
date: 2026-06-08
last_modified_at: 2026-07-26
faq:
  - q: "What is a vector database used for?"
    a: "Searching by meaning rather than exact match. It stores embeddings — numerical representations of text, images, or other data — and finds the items closest in meaning to a query. Its most common use is powering retrieval-augmented generation (RAG), where relevant context is fetched to ground a language model's answer."
  - q: "What is the difference between a vector database and a regular database?"
    a: "A regular database finds rows by exact or range matches on values. A vector database finds rows by similarity in a high-dimensional space, returning the nearest items by meaning. They answer different questions and are usually used together, not as substitutes."
  - q: "Do I need a dedicated vector database?"
    a: "Often not. Many existing databases — Postgres with pgvector, and most major warehouses — now offer vector search built in, which is simpler if your volumes are modest. A dedicated vector database earns its place at large scale or when similarity search is a core, high-performance workload."
---

A vector database stores **embeddings** — numerical representations of data — and
retrieves items by *similarity in meaning* rather than by exact match. That one
capability is why vector databases went from obscure to ubiquitous in the space of a
couple of years: they're the storage layer underneath most retrieval-augmented
generation. But "vector database" gets discussed with more mystique than it
deserves, and the practical questions — what it's for, how it fits your existing
stack, and whether you need a *dedicated* one — have clear answers.

## The problem it solves: search by meaning

A normal database is brilliant at exact questions. *Find the customer with id 1077.*
*Find orders where amount > 500.* It matches values precisely. What it can't do is
answer *find documents that mean roughly the same thing as this question* — because
meaning isn't an exact value.

The trick that makes semantic search possible is the **embedding**: a model converts a
piece of text (or an image, or audio) into a long list of numbers — a vector — such
that things with similar meaning end up close together in that numerical space.
"How do I reset my password" and "I forgot my login credentials" land near each other,
despite sharing almost no words.

A vector database is the system built to store those vectors and, given a query
vector, **find the nearest ones fast** — the items closest in meaning. At small scale
you could compare against every stored vector by brute force; the database exists to
do approximate nearest-neighbour search efficiently across millions of them.

Almost every product in this category is, underneath, an implementation of the
same handful of index structures — most commonly
[HNSW](https://arxiv.org/abs/1603.09320), the hierarchical proximity-graph
algorithm from Malkov and Yashunin's 2016 paper, which gets logarithmic search
scaling by starting the walk in a sparse top layer and descending. Knowing that
is useful when you evaluate vendors: the differentiator is rarely the search
algorithm, because they are largely running the same one.

## What it's actually for

The dominant use is **retrieval-augmented generation**. As covered in [why your AI is
only as good as your data architecture](/essays/your-ai-is-only-as-good-as-your-data-architecture/),
RAG works by fetching relevant context and letting a model reason over it rather than
relying on its training. The vector database is the "fetch relevant context" step: you
embed your documents and store them, then embed the user's question and ask the vector
database for the most similar chunks to feed the model.

Beyond RAG, the same meaning-based retrieval powers semantic search over a knowledge
base, recommendation ("items like this one"), deduplication, and anomaly detection.
Anywhere the question is *what's similar to this?* rather than *what exactly equals
this?*, vectors are the tool.

## Where it fits in your stack

Here's the part that cuts through the hype. As I argued in [what GenAI actually
changes about data architecture](/essays/what-genai-changes-about-data-architecture/),
vector storage is a genuine *addition* to the stack — a new access pattern — but it
sits *alongside* your existing data, it doesn't replace it.

> A vector database answers "what's similar in meaning?" Your warehouse answers "what
> are the exact facts?" These are different questions, and a serious system usually
> needs both — the vector store for retrieval, the structured store for truth.

In practice the embeddings often *derive* from data you already manage — product
descriptions, support articles, documents sitting in your [lake or
lakehouse](/essays/data-warehouse-vs-data-lake-vs-lakehouse/). The vector database is a
specialised index over meaning, not a new source of truth. And it inherits every
weakness of the data it's built from: embed duplicated, stale, or contradictory
documents and similarity search faithfully retrieves duplicated, stale, contradictory
context. Vectors don't clean your data; they encode whatever you hand them.

## Do you need a *dedicated* one?

This is the question that actually saves money. "Do I need vector *search*?" and "Do I
need a dedicated vector *database*?" are different questions, and people conflate them.

You likely need vector **search** if you're building RAG or semantic search. You may
**not** need a separate product for it, because vector capability has been absorbed
into tools you already run: Postgres has `pgvector`, and most major warehouses and
search engines now offer native vector indexing. For modest volumes, adding vector
search to your existing database is far simpler than standing up, securing, and
syncing a whole new system.

A **dedicated** vector database earns its place when similarity search is a *core,
high-scale workload* — many millions of vectors, high query throughput, demanding
latency — where specialised indexing and operational tuning genuinely outperform a
bolt-on. That's a real need for some products and overkill for most.

So the honest decision tree is short. Building RAG or semantic search? You need vector
search. Modest scale and an existing database with vector support? Use that. Massive
scale with similarity search as a central, performance-critical function? A dedicated
vector database is worth it. As with [every other piece of the
stack](/essays/is-the-modern-data-stack-dead/), adopt the specialised tool for the
problem you can actually demonstrate — not because it's the component the AI era told
you to buy.

*(Vector search finds what looks similar; when questions span many connected
entities, explicit relationships do better — see
[knowledge graph vs data warehouse](/essays/knowledge-graph-vs-data-warehouse/).)*
