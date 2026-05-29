---
title: "The Medallion Architecture, Reconsidered"
kicker: "Reconsidered"
topic: "Architecture"
date: 2026-05-27
description: "Bronze, silver, gold is a useful default and a dangerous dogma. A second look at what the layers get right, and where they quietly fall apart."
---

The medallion architecture — bronze, silver, gold — has become the default mental
model for organising a data lakehouse, and for good reason. It's memorable, it maps
to an intuition everyone shares, and it gives a sprawling pile of data a sense of
direction. I've recommended it. I still do, sometimes. But defaults have a way of
hardening into dogma, and this one has hardened more than most. It's worth a second,
honest look.

## What the layers get right

Stripped to its essence, the pattern says: data should flow through stages of
increasing refinement and trust. **Bronze** is raw, as-ingested, untouched —
history you can always replay from. **Silver** is cleaned, conformed, deduplicated
— the validated, queryable middle. **Gold** is business-ready — the curated,
aggregated tables that feed dashboards and decisions.

Two things here are genuinely valuable and worth keeping no matter what you call
the layers.

The first is **provenance**. Keeping raw data immutable in bronze means you can
always answer "where did this number come from?" and, crucially, *reprocess* when
you discover a bug in your logic. Throwing away raw data to save space is one of
the few truly irreversible mistakes in this field. Bronze, as a discipline, guards
against it.

The second is **progressive refinement** as an explicit idea — the recognition that
raw data and decision-ready data are different things with different consumers, and
that the transformation between them deserves to be a deliberate, staged, testable
process rather than one heroic query.

Those two ideas are good architecture. Hold onto them.

## Where it quietly falls apart

The trouble starts when the three layers stop being a *guideline* and start being a
*rule* — when every table must belong to a tier and every problem must be solved by
adding another one. Several failure modes recur.

**Gold sprawls.** "Business-ready" has no natural boundary, so gold becomes a
dumping ground of one-off aggregates, each built for a single dashboard, each
subtly re-deriving metrics the others already computed. You end up with the exact
inconsistency the architecture was supposed to prevent, now wearing a gold badge.
Three tables claim to hold "monthly revenue" and all three disagree.

**Silver becomes a swamp.** Without a clear contract for what "cleaned and
conformed" means, silver fills with tables that are *sort of* clean — half-modeled,
inconsistently grained, owned by no one. It's no longer raw and not yet trustworthy,
which is the worst of both worlds: a layer everyone reads from and no one believes.

**The layers masquerade as a semantic layer.** This is the deepest problem. Medallion
describes *physical refinement* — how raw bytes become clean tables. It says nothing
about *meaning* — what a "customer" is, how "active" is defined, which metric is
canonical. Teams keep trying to solve semantic problems by adding more gold tables,
and it never works, because the layers were never about semantics. A bronze→silver→
gold pipeline with no governed definitions on top is just a very tidy way to produce
inconsistent numbers.

> Medallion answers "how clean is this data?" It does not answer "what does this
> data mean, and who decides?" — and most data disasters are failures of the
> second question, not the first.

## A more honest framing

I've stopped presenting medallion as *the* architecture and started presenting it
as what it actually is: a useful convention for **refinement**, which must be paired
with two things it doesn't supply.

The first is **ownership per dataset**, not per layer. The question that matters
isn't "which tier is this in?" but "who owns this table's shape and meaning?" A gold
table no one owns is more dangerous than a bronze one, because people *trust* it.
Tiers are a property of data; ownership is a property of teams. Don't confuse them.

The second is **a semantic layer that sits across the tiers** — a single governed
place where business concepts and metrics are defined once, regardless of which
physical table they're computed from. This is the part medallion structurally
cannot give you, and it's the part that actually determines whether your
organisation agrees on what its numbers mean.

So: keep bronze's immutable provenance. Keep the discipline of staged refinement.
But hold the three-layer model loosely. It's a sketch of *how data gets cleaner*,
not a theory of *how data gets meaning*. Treat it as the former and it serves you
well. Mistake it for the latter — as a surprising number of teams do — and you'll
spend a year building gold tables to solve a problem that was never about gold at
all.
