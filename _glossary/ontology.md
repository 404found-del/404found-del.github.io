---
last_modified_at: 2026-07-24
title: "Ontology"
description: "An ontology is a formal, application-independent definition of what concepts mean and how they relate in a domain — machine-readable meaning, not storage structure."
essay: ontology-vs-data-model
related_terms:
  - semantic-layer
  - data-contract
  - conformed-dimension
---

An **ontology** is a formal specification of the concepts in a domain, their
properties, and the relationships between them — expressed precisely enough that
a machine can reason over it, and deliberately independent of any single system
that stores the data.

That independence is the distinguishing feature. A
[data model](/glossary/dimension-table/) is built for one warehouse or
application; an ontology is meant to be reused by many, defining *what a customer
is* rather than *which table holds customers*. Its formal axioms — this class is
a subtype of that one, these two are disjoint, this property must hold — let
software derive facts rather than merely retrieve them. In practice most teams
get the essential benefit from a governed
[semantic layer](/glossary/semantic-layer/); formal ontologies earn their extra
cost when meaning must be shared across many systems, when relationships are the
analytical product, or when machines must reason over the model.
