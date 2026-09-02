---
title: "Data Engineer vs Data Architect vs Analytics Engineer"
kicker: "Field Notes"
topic: "Craft"
description: "Three overlapping data roles, three different jobs: engineers move the data, analytics engineers shape it, architects design the system. The real division."
date: 2026-06-14 13:00:00 +0530
last_modified_at: 2026-08-29
faq:
  - q: "What is the difference between a data engineer and a data architect?"
    a: "A data engineer builds and operates the pipelines and infrastructure that move data reliably from sources into the warehouse. A data architect decides the structure, standards, and principles the whole system follows — where data lives, what it means, who owns it. The engineer builds the system; the architect designs it."
  - q: "What does an analytics engineer do?"
    a: "An analytics engineer transforms the raw data that data engineers have loaded into clean, tested, documented, modeled tables that analysts can use — typically with SQL and version control. The role sits between data engineering and analysis, and it emerged because ELT moved transformation into the warehouse where SQL-fluent people could own it."
  - q: "Do you need all three roles?"
    a: "You need all three functions; you may not need three separate people. Small teams often have one generalist doing all of it. As scale grows, the work splits — engineers for pipelines, analytics engineers for modeling — and a dedicated architect appears when standards must be set across multiple teams."
---

Data engineer, data architect, analytics engineer — three titles, used loosely,
overlapping constantly, and a reliable source of confusion in job descriptions and
team-design arguments alike. On a small team one person often wears all three hats, which
blurs the lines further. But underneath the fuzzy titles there's a real division of
labor, and it's worth getting straight: roughly, **data engineers move the data,
analytics engineers shape it for analysis, and data architects design the system it all
runs in.** Here's what that means in practice.

## Why the titles blur

Part of the confusion is genuine: the roles emerged at different times, companies use
the labels inconsistently, and the work overlaps at the edges. The analytics engineer
title in particular is recent — it barely existed a decade ago. And on a five-person
data team, the same person ingests the data, models it, *and* decides the warehouse
structure, so the distinctions feel academic.

They stop feeling academic the moment a team grows, because the three jobs pull on
different skills and answer to different definitions of "done." So separate them by what
each one actually *owns*.

## The data engineer: moves the data

The data engineer builds and operates the **infrastructure and pipelines** that get data
reliably from source systems into the warehouse or lake. This is the plumbing of the
data platform: ingestion, [change data capture](/essays/what-is-change-data-capture/),
orchestration, the [batch-or-streaming](/essays/batch-vs-streaming/) decision, and
making pipelines [idempotent](/essays/how-to-make-a-data-pipeline-idempotent/) so they
survive retries and backfills.

It's the most **software-engineering-heavy** of the three roles — distributed systems,
pipeline tooling, reliability, performance. The data engineer's definition of done is
that *the data arrives, correctly and on time*, no matter what the source systems throw
at it. They live closest to the raw end of the platform, and when a pipeline breaks at
3 a.m., it's their pager that goes off.

## The analytics engineer: shapes the data

The analytics engineer takes the raw data the data engineers have landed and **transforms
it into clean, tested, documented, modeled tables** that analysts can actually use — the
[dimensional models](/essays/a-field-guide-to-dimensional-modeling/) and metrics the
business consumes. They live in SQL, version control, and transformation tooling, and
their definition of done is that *the data is trustworthy and usable for analysis*.

This role exists for a specific reason: as I covered in [ETL versus
ELT](/essays/etl-vs-elt/), the shift to transforming data inside the warehouse with SQL
pulled transformation out of a niche engineering specialty and into the hands of
anyone fluent in SQL. The analytics engineer is what that person became — a bridge
between raw data engineering and end-user analysis, owning the modeling layer that used
to fall awkwardly between the two.

> Data engineers make the data *available*. Analytics engineers make it *usable*. The
> first is a reliability problem; the second is a modeling and trust problem — and
> they're genuinely different jobs.

## The data architect: designs the system

The data architect isn't primarily building or transforming any single thing. The job is
deciding the **structure, standards, and principles** the whole system follows — [the
shape the data should take](/essays/the-shape-of-data/), where it should live, what it's
allowed to mean, and who owns it. As I argued in [what a data architect actually
does](/essays/what-does-a-data-architect-do/), the work is the *decisions and the
coherence*, not the construction.

It's the **broadest and most cross-cutting** of the three, usually the most senior, and
the most concerned with how everything fits together and whether it'll still make sense
in two years. The architect's definition of done isn't a working pipeline or a clean
table — it's a *coherent system*, with [contracts](/essays/data-contracts-are-a-cultural-problem/),
ownership, and meaning that hold up as the platform grows.

## The clean mental model

Think of building a city:

- **The data engineer** lays the roads and utilities — the infrastructure everything
  depends on. *Moves the data; owns reliability.*
- **The analytics engineer** designs the buildings people actually live and work in —
  what the data becomes for its users. *Shapes the data; owns usability.*
- **The data architect** sets the zoning and the city plan that keeps it all coherent as
  it grows. *Designs the system; owns coherence.*

Move it, shape it, design it. That's the division in five words.

## The reality: overlap, and who wears which hat

In practice the boundaries blur, and that's fine. An analytics engineer who defines the
team's modeling standards is doing architecture. A data engineer who decides the
warehouse's layering is doing architecture. The architect "hat" — the concern for how it
all fits and whether it'll last — can be worn by anyone, but *someone has to wear it*, or
the platform drifts into incoherence one local decision at a time.

Which roles you actually need depends on stage. Early on, you want a **generalist data
engineer** who can do a bit of everything. As you grow, the work naturally splits into
**engineers** running pipelines and **analytics engineers** owning the models. And when
the platform spans multiple teams with conflicting standards, a **dedicated architect**
earns their place by setting the structure everyone builds within.

The titles will keep being used loosely, and the work will keep overlapping. But the
three functions are real and distinct, and you need all of them — whether or not you have
all three titles. Skip the analytics engineering and you get reliable pipelines feeding
badly-modeled data nobody trusts. Skip the architecture and you get beautiful local work
that adds up to an incoherent whole. The roles exist because each one owns a problem the
others don't — and a healthy data team is one where all three problems have an owner.
