---
last_modified_at: 2026-07-06
title: "Data Contract"
description: "A data contract is an explicit, enforced agreement between a data producer and its consumers covering schema, semantics, quality, and change management."
essay: data-contracts-are-a-cultural-problem
related_terms:
  - data-catalog
  - data-lineage
---

A **data contract** is an explicit agreement between a data producer and its
consumers: the schema that will be delivered, what the fields mean, the quality
and freshness guarantees, and how changes will be communicated and versioned.
Ideally it's machine-readable and enforced in CI — a producer can't merge a
change that breaks a promise a consumer depends on.

Contracts exist because the implicit alternative — downstream teams discovering
schema changes when dashboards break — makes every producer change everyone
else's incident. The technology is the easy part; the hard part is
organisational: contracts only hold when producers accept ownership of what they
publish, which is a cultural change wearing a YAML file.
