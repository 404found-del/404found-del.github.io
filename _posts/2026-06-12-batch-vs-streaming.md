---
title: "Batch vs Streaming: How to Actually Decide"
kicker: "Field Notes"
topic: "Engineering"
description: "Batch vs streaming isn't legacy vs modern. The real question: what latency does the decision consuming the data actually require? Default to batch; promote pipelines to streaming one named use case at a time."
date: 2026-06-12
---

The batch-vs-streaming question is usually framed as legacy versus modern — batch as
the old nightly habit, streaming as what serious teams do now. That framing has
pushed a lot of teams into real-time infrastructure they didn't need and now
maintain at considerable cost. The framing is wrong. Batch and streaming are both
fine; the choice belongs not to fashion but to a single question: **what latency does
the *decision* consuming this data actually require?**

## Start from the decision, not the pipeline

Data exists to change what someone — or something — does. So the freshness
requirement comes from the consuming decision, and from nowhere else. A weekly
business review needs weekly data. A daily dashboard, checked each morning, needs
data from last night. A fraud check that approves or blocks a payment needs data
from seconds ago.

> The freshness requirement belongs to the decision, not the pipeline. If no decision
> changes more than once a day, a sub-second pipeline is engineering for an audience
> that isn't there.

Walk through what your data actually feeds and an awkward fact emerges: most
analytical consumption runs on *human* cadences — daily, weekly, monthly. Humans
don't re-decide continuously. For all of that, batch isn't the legacy option; it's
the correctly-sized one.

## What batch gives you for free

Batch — processing accumulated data on a schedule — has virtues that don't make
conference talks:

- **Simplicity you can reason about.** A job with a defined input window, a start,
  and an end. When it fails, you re-run it; you can hold the whole thing in your head.
- **Natural idempotency.** The [partition-overwrite pattern](/essays/how-to-make-a-data-pipeline-idempotent/)
  — rebuild the day, atomically — makes retries and re-runs boringly safe.
- **Trivial backfills.** Found a logic bug from March? Re-run March. Backfilling a
  *stream*, by contrast, is a small research project.
- **Cheaper everything:** simpler infrastructure, easier testing, fewer specialist
  skills on call.

## What streaming actually costs

Streaming — processing events continuously as they arrive — buys latency, and the
bill is complexity of a specific, permanent kind. Events arrive **late and out of
order**, so correctness requires watermarks and a policy for stragglers.
Aggregations require **managed state** that must survive failures and restarts.
Delivery is typically at-least-once, so consumers must handle duplicates. Testing,
debugging, and *changing* a streaming job — replaying history through new logic —
are all categorically harder than their batch equivalents. None of this is a tooling
gap that the next framework fixes; it's inherent to computing on an unbounded,
disordered flow of events. You pay it forever, in operations and on-call.

So the question is never "is streaming better?" It's "which decisions are worth that
permanent tax?"

## Where streaming genuinely earns it

The honest list is short and operational. Streaming pays for itself when data feeds a
decision made by a **machine, inside a feedback loop measured in seconds or
minutes**: fraud and risk checks inline with transactions, live personalization and
recommendations, operational monitoring and alerting, inventory or pricing that
reacts within minutes. The common thread — the consumer is a system acting *now*,
not a person looking later.

Two clarifications that defuse most confusion. First, **micro-batch** — small batches
every few minutes — covers a surprising share of "real-time" asks at a fraction of
streaming's complexity; much of what's marketed as streaming is micro-batch under the
hood, and that's a compliment. Second, **using [change data
capture](/essays/what-is-change-data-capture/) does not obligate you to stream-process.**
CDC is a *source* of changes; landing that change stream into micro-batches is a
perfectly good architecture. How you capture and how you process are separate
decisions.

## The rule

Default to batch. Then promote *individual pipelines* to streaming when — and only
when — someone can name the decision, name who or what makes it, and name the latency
it requires. "We want real-time" is not a requirement; "the risk engine must score
transactions within two seconds" is. The first justifies nothing; the second
justifies exactly one streaming pipeline.

This is the same discipline as [every other architecture choice](/essays/is-the-modern-data-stack-dead/):
adopt machinery for the problems you demonstrably have, not the ones a reference
architecture implies you should. The teams that get this right usually end up in the
same place — a platform that is batch almost everywhere, streaming in two or three
named places where it earns its keep, and dramatically easier to run than the
all-real-time alternative. Boring on purpose, fast where it matters.
