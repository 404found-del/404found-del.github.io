---
title: "What Does a Data Architect Actually Do?"
kicker: "Essay"
topic: "Craft"
description: "A data architect's job isn't drawing diagrams or picking tools. It's making the deliberate decisions about how data is shaped, defined, owned, and trusted — and defending them against entropy."
date: 2026-06-06
last_modified_at: 2026-07-05
---

Ask ten people what a data architect does and you'll get two common answers, both
wrong. The first: it's a senior engineer who chooses the database and the tools. The
second: it's the person who makes the boxes-and-arrows diagrams. Both mistake the
*residue* of the work for the work. What a data architect actually does is make a
long sequence of deliberate decisions about how an organization's data is shaped,
defined, owned, and trusted — and then defend those decisions against the constant
pressure to erode them. The title sounds like it's about systems. It's really about
decisions.

## The job is a sequence of decisions

Strip away the tooling and the diagrams and the role comes down to repeatedly
answering questions that have no purely technical answer — questions where the
architect's job is to choose, and to make the choice stick. A few of the recurring
ones:

**What shape should this data take?** The foundational act, and the one I keep coming
back to: data either has [a shape someone chose, or a shape that happened to
it](/essays/the-shape-of-data/). The architect chooses — declaring the grain,
designing the [dimensional models](/essays/a-field-guide-to-dimensional-modeling/),
deciding which [type of fact table](/essays/fact-table-types/) fits which question.

**Where should this data live?** Deciding between [a warehouse, a lake, or a
lakehouse](/essays/data-warehouse-vs-data-lake-vs-lakehouse/); keeping
[transactional and analytical workloads apart](/essays/oltp-vs-olap/) so one doesn't
strangle the other. Not "which vendor is best" but "which storage model fits this
workload."

**What is this data allowed to mean?** Establishing the [semantic
layer](/essays/what-is-a-semantic-layer/) — the one governed place where "revenue" and
"active user" are defined once, so the organization can agree on its own numbers.

**Who owns it, and what do they owe?** Setting the [contracts between producers and
consumers](/essays/data-contracts-are-a-cultural-problem/) and the ownership that
makes them real — because, as it turns out, [most data-quality problems are org-chart
problems](/essays/data-quality-problems-are-org-chart-problems/), and the architect is
often the one who has to name that out loud.

Each of these is a small act of governance. Each closes off options that felt
convenient. And each, made well, saves a hundred downstream people from
re-litigating the same ambiguity forever.

## The core skill isn't technical

Notice what those decisions have in common: the hard part of each is rarely the
technology. It's getting people to *agree*, and having the spine to choose when they
won't. The marketing team's definition of "customer" and finance's definition cannot
both win; someone has to broker a single answer and then defend it against a hundred
well-meaning requests for "just this one exception."

> Good architecture is mostly the courage to make decisions explicit, and the
> discipline to keep them that way when the pressure is to let them slide.

That's the part no diagram captures and no tool provides. A data architect is, more
than anything, the person who makes the ambiguous explicit — and then holds the line.

## What it is *not*

It helps to be precise about the boundaries:

- **It's not the diagram.** The diagram is documentation of decisions already made.
  Producing one isn't architecture; making the choices it depicts is.
- **It's not tool selection.** Which warehouse, which orchestrator — these matter, but
  they're *downstream* of the structural decisions. Pick the tools to serve the
  architecture, not the other way around. A team that starts from the tool is
  letting the vendor's defaults make its design decisions.
- **It's not a one-time design.** Architecture isn't a document you deliver and walk
  away from. Data accretes, definitions drift, exceptions pile up. The job is
  ongoing *defense against entropy* as much as initial design.

## How it differs from the roles next to it

Briefly, because the lines blur: a **data engineer** builds and runs the pipelines and
infrastructure. An **analytics engineer** models cleaned data into the tables analysts
use. A **data architect** decides the structure, standards, and principles that both
operate within — the shape of the whole, not the construction of each part. On a small
team one person wears all three hats; the *architecture* hat is the one concerned with
how it all fits together and whether it'll still make sense in two years. (The
three roles get a [full comparison of their own](/essays/data-engineer-vs-data-architect-vs-analytics-engineer/).)

## The real description

So if you want the honest job description, it isn't "designs data systems." It's
something closer to: *decides what the organization's data means and how it's
structured, gets people to agree, and keeps it coherent as everything pushes toward
chaos.* The systems are how the decisions get expressed. But the decisions — and the
trust they produce — are the actual work. Everything else is plumbing in service of
it.
