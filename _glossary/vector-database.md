---
title: "Vector Database"
description: "A vector database stores embeddings — numeric representations of meaning — and retrieves items by similarity, powering semantic search and RAG in AI systems."
essay: what-is-a-vector-database
related_terms:
  - semantic-layer
  - data-catalog
---

A **vector database** stores *embeddings* — arrays of numbers that represent the
meaning of text, images, or other content — and retrieves items by similarity:
given a query vector, find the stored vectors nearest to it. That
nearest-neighbour search is what powers semantic search ("find documents about
refund policy" without matching the words) and retrieval-augmented generation
(RAG), where an AI model is fed the most relevant context before answering.

Architecturally it's a new kind of index rather than a replacement for
analytical storage: production systems pair it with the warehouse or lakehouse,
where the governed source data lives, and treat embeddings as derived data —
rebuilt when models change, governed like any other pipeline output.
