---
title: "Idempotent Pipeline"
description: "An idempotent pipeline produces the same correct result whether run once or five times — the property that makes retries, backfills, and replays safe."
essay: how-to-make-a-data-pipeline-idempotent
related_terms:
  - change-data-capture
  - medallion-architecture
---

An **idempotent pipeline** produces the same correct end state whether it runs
once or five times over the same input. Rerunning yesterday's load doesn't
double yesterday's rows; replaying a week after an incident converges on the
same tables as if nothing had failed. Idempotency is the property that makes
retries, backfills, and [CDC](/glossary/change-data-capture/) replays *boring* —
which is exactly what you want at 3 a.m.

The standard techniques: overwrite deterministic partitions instead of
appending, `MERGE` on stable keys instead of blind inserts, and derive
everything from immutable raw inputs (the bronze layer of a
[medallion architecture](/glossary/medallion-architecture/)) so any table can be
rebuilt from history.
