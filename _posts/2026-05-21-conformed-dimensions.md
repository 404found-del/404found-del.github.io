---
title: "What Are Conformed Dimensions, and Why Do They Matter?"
kicker: "Field Notes"
topic: "Modeling"
description: "A conformed dimension is one dimension shared identically across several fact tables, so different business processes can be compared on the same terms."
date: 2026-05-21
last_modified_at: 2026-07-26
faq:
  - q: "What is a conformed dimension?"
    a: "A conformed dimension is a dimension table used identically across multiple fact tables or data marts — the same keys, same attributes, same meaning. Because every process references the same customer or date dimension, you can compare and combine metrics from different processes consistently."
  - q: "Why are conformed dimensions important?"
    a: "They're what make a warehouse coherent rather than a set of disconnected silos. Sharing one customer dimension across sales, support, and marketing lets you analyze all three on the same customers and segments. Without conformity, each mart defines 'customer' its own way and the numbers can't be compared."
  - q: "What is the difference between a conformed dimension and the bus matrix?"
    a: "A conformed dimension is the shared table itself. The bus matrix is the planning grid that maps which business processes (fact tables) use which conformed dimensions — a blueprint for building marts incrementally while keeping them integrated."
---

[Dimensional modeling](/essays/a-field-guide-to-dimensional-modeling/) is usually
taught one star at a time — a [fact table](/glossary/fact-table/), its dimensions, done. But real
organizations have *many* business processes, each with its own fact table: sales,
shipping, support tickets, web sessions. The question that decides whether those
separate stars add up to a coherent warehouse or a pile of disconnected silos is
this: do they **share their dimensions?** A dimension shared identically across many
fact tables is a *conformed dimension*, and conformity is the single most important
idea for making a multi-process warehouse hang together.

## The definition

A conformed dimension is a [dimension table](/glossary/dimension-table/) that is used **identically** across
multiple fact tables — the same [surrogate keys](/glossary/surrogate-key/), the same attributes, the same
meanings. There is one `dim_customer`, one `dim_product`, one
[`dim_date`](/essays/date-dimension-table/), and *every* fact table that needs
customer, product, or date points at that same shared table.

The opposite — each business process building its own private customer dimension, with
its own keys and its own slightly different definition of "segment" — is how you end up
with the [three-different-numbers problem](/essays/what-is-a-semantic-layer/) baked
into the warehouse's very structure.

## Why conformity is the whole game

Here's what sharing a dimension actually buys you, and why Kimball treated it as the
cornerstone of enterprise dimensional modeling.

**You can compare processes on the same terms.** If sales and support both reference
the *same* `dim_customer`, you can ask "do customers in the Enterprise segment file
more support tickets?" — joining a sales fact and a support fact through the shared
customer dimension and trusting that "Enterprise" means the same thing on both sides.
The instant each process has its own customer dimension, that question becomes
unanswerable: you'd be comparing two different definitions of customer and segment.

> Conformed dimensions are what turn a collection of separate stars into a single
> warehouse. Without them you don't have a warehouse — you have several small ones
> that happen to share a database and can't be compared.

**Consistency by construction.** "Revenue by region" and "tickets by region" use the
*same* region attribute from the *same* dimension, so they're automatically
comparable and consistent. The conformity isn't enforced by a downstream tool; it's
built into the model.

**A drill-across becomes possible.** Querying multiple fact tables and lining their
results up by a shared dimension — "monthly sales *and* monthly support volume by
product" — is called drilling across, and it only works because the dimensions
conform. It's how you build a unified view of the business from separate processes.

## The bus matrix: conformity as a plan

Because conformed dimensions are about *sharing across processes*, they come with a
planning tool: the **bus matrix**. It's a simple grid — business processes (future fact
tables) down the side, dimensions across the top — with a mark wherever a process uses
a dimension.

```
                  Date  Customer  Product  Store  Employee
Sales              ✓       ✓         ✓       ✓
Shipping           ✓       ✓         ✓       ✓
Support Tickets    ✓       ✓                         ✓
Web Sessions       ✓       ✓         ✓
```

The columns that recur — Date, Customer, Product — are your conformed dimensions, the
ones worth building once, carefully, and sharing. The matrix lets you build the
warehouse **incrementally, one process at a time**, while guaranteeing the pieces
integrate: each new fact table reuses the dimensions already built rather than
inventing its own. It's the architecture that lets you ship a sales mart now and a
support mart next quarter and have them work together on day one.

## Getting conformity right

The practical discipline is to identify the dimensions used across many processes —
almost always date, customer, and product, plus whatever is central to your business —
and treat them as **shared assets owned deliberately**, not as something each team
rebuilds locally. This is as much an [ownership question](/essays/data-quality-problems-are-org-chart-problems/)
as a modeling one: a conformed dimension only stays conformed if someone is
responsible for keeping it the single, authoritative version.

Do that, and your separate stars become a genuine warehouse — one where any process
can be compared to any other because they all speak the same dimensional language.
Skip it, and you get the thing that looks like a warehouse on the schema diagram but
behaves like a dozen incompatible spreadsheets the moment someone asks a question that
crosses two processes. Conformed dimensions are the difference, and they're worth the
deliberate effort they take.
