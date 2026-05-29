---
title: "The Shape of Data"
kicker: "Manifesto"
topic: "Architecture"
date: 2026-04-22
summary: "Every dataset has a shape. The only question is whether you chose it, or whether it happened to you."
---

Every dataset has a shape. The columns it carries, the grain it's recorded at, the
relationships it admits and forbids, the names it goes by in six different teams —
all of this is *shape*. The only real question in our field is whether that shape
was chosen, or whether it simply happened to you.

Most data has the second kind of shape. It accreted. A column was added in a hurry
to ship a feature. A status field grew a seventh value that nobody documented. Two
teams independently invented "active user" and both were right, locally, and
catastrophically incompatible, globally. Nobody designed any of this. It is the
data equivalent of a city with no zoning — organic, alive, and almost impossible
to reason about.

Data architecture is the practice of choosing the shape on purpose.

## Structure is a decision, not a diagram

It is tempting to think architecture lives in diagrams — boxes, arrows, a tasteful
choice of pastel. But the diagram is just the residue. The actual work is a long
sequence of decisions, most of them uncomfortable:

- What is the *one* definition of a customer, and who is allowed to change it?
- At what grain do we record an order — the order, the line item, the fulfilment event?
- Which facts are immutable history and which are mutable state, and why are we so often confusing the two?
- What is this system *not* responsible for?

Each of these is a small act of governance. Each one closes off possibilities that
felt convenient. And each one, made well, saves a hundred downstream people from
re-litigating the same ambiguity forever. The diagram is easy. The decisions are
the job.

## The cost of accidental shape

Accidental shape is expensive, but the expense is hidden, which is why it survives
so long. It shows up as:

> A number that is correct in three dashboards and subtly different in all three,
> because each one re-derived it from raw events using slightly different
> assumptions that no one wrote down.

It shows up as the new analyst who takes three weeks to ship their first query,
not because the SQL is hard, but because the *meaning* is hard — because they must
first reconstruct, by archaeology, what every table actually represents. It shows
up as the warehouse that has quietly become a museum: a hundred tables, each a
fossil of a decision nobody wanted to own.

The deepest cost is epistemic. When data has no deliberate shape, the organisation
slowly loses the ability to know things about itself. Two executives cite two
numbers for the same metric and the meeting derails into a debate about whose
extract is correct. That is not a tooling failure. That is a structural one.

## Good architecture is mostly courage

Here is the uncomfortable truth at the center of this work: most data problems are
not technology problems. They are problems of **structure and agreement**.

The technology to store, move, and transform data has never been better or cheaper.
What remains scarce is the willingness to say: *this is what a customer is, this is
who owns it, this is what it is allowed to mean, and we will keep it that way even
when it's inconvenient.* That sentence is architecture. Everything else is
plumbing in service of it.

Courage, because the decision will be wrong for someone. The marketing team's
definition and the finance team's definition cannot both win, and the architect's
job is to broker a single answer and then defend it against the slow entropy of a
hundred well-meaning exceptions. The pressure is always toward more shape, more
special cases, more "just this once." Architecture is the discipline of pushing
back.

## What this site is for

This is a notebook about choosing shape on purpose. Some of it will be opinionated
to the point of being wrong — that's the price of being useful. Some of it will be
practical: how to model a dimension, where a contract belongs, when a layered
architecture starts working against you. All of it circles the same conviction.

Data does not have to be something that happens to you. It can be designed. And
the difference between an organisation that knows things and one that merely
stores them is, almost always, whether someone had the nerve to decide.

Let's decide well.
