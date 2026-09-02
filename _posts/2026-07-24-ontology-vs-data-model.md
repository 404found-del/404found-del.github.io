---
title: "Ontology vs Data Model: Meaning vs Structure"
kicker: "Field Notes"
topic: "Modeling"
description: "A data model shapes data for one system; an ontology defines what concepts mean, independent of any system — and machines now read your schema."
date: 2026-07-24 09:00:00 +0530
last_modified_at: 2026-08-29
faq:
  - q: "What is the difference between an ontology and a data model?"
    a: "A data model defines how data is structured for a particular system — tables, columns, keys, constraints, optimized for storing and querying. An ontology formally defines what concepts mean and how they relate, independent of any system that stores them. The data model answers 'how do I store and query this here'; the ontology answers 'what is a customer, in this business, everywhere.'"
  - q: "Is an ontology just a conceptual data model?"
    a: "It's the closest classical analogue, but two things differ. An ontology is deliberately application-independent — it's meant to be reused across systems rather than implemented once — and it carries formal semantics: machine-readable axioms about class hierarchy and properties from which a reasoner can derive new facts. A conceptual model usually stops at a diagram; an ontology keeps going until a machine can act on it. Note that deriving facts (OWL) and validating data (SHACL) are separate jobs — conflating them is the most common first mistake."
  - q: "Do I need an ontology if I already have a semantic layer?"
    a: "Often no. A semantic layer already does the essential job — defining business concepts once, in one governed place, so every consumer gets the same answer. An ontology is the heavier, more formal version, and it earns its cost when meaning must be shared across many systems and organisations, when relationships matter as much as measures, or when machines need to reason over the model rather than just query it."
  - q: "Why are ontologies suddenly relevant again in the AI era?"
    a: "Because LLMs need grounding. A model given raw table names guesses at meaning; a model given explicit, machine-readable definitions of concepts and relationships doesn't have to. That's the same argument dimensional modelers have made about declared grain and conformed dimensions for thirty years — the audience changed from analysts to machines, and the requirement got stricter."
---

Here is the distinction, before the philosophy: **a data model defines how data
is structured so a particular system can store and query it. An ontology defines
what concepts *mean* and how they relate, independently of any system that
stores them.** The data model is committed to an implementation — these tables,
these keys, this warehouse. The ontology is deliberately not: it's meant to be
reused by many applications, and to be formal enough that a machine can reason
over it rather than merely read it.

That distinction has been an academic footnote for twenty years. It stopped being
one the moment we started pointing language models at enterprise schemas and
asking them to interpret meaning they were never given.

## The comparison, honestly

| | Data model | Ontology |
|---|---|---|
| **Answers** | How is this stored and queried? | What does this mean, and how does it relate? |
| **Scope** | One system or application | A domain, across systems |
| **Optimized for** | Storage, integrity, query performance | Shared meaning, reuse, inference |
| **Typical artifacts** | Tables, columns, keys, constraints | Classes, properties, relationships, axioms |
| **Expressed in** | DDL, ERDs, dbt models | OWL/RDFS, SHACL, or a formal spec |
| **Change driver** | New query patterns, new sources | New understanding of the domain |
| **Reused across apps** | Rarely — it's built for one | By design — that's the point |
| **Machine can infer from it** | No (it can only execute queries) | Yes (that's what the axioms are for) |
| **Validates data by** | Constraints, in the database | A separate shape language (SHACL) |
| **Fails by** | Being wrong for new questions | Being too abstract to implement |

## The same problem, two altitudes

Take the case every data architect has lived: three systems disagree about what
a customer is. Billing has accounts, the CRM has leads that sometimes become
accounts, the product database has users. The *data model* solution is
structural — reconcile them into one dimension with a
[surrogate key](/glossary/surrogate-key/), keep each source's
[natural key](/glossary/natural-key/) as an attribute, and you have something
queryable:

```sql
-- Data model: a structure optimized for this warehouse's queries
CREATE TABLE dim_customer (
  customer_key    BIGINT PRIMARY KEY,   -- surrogate, warehouse-owned
  billing_acct_id TEXT,                 -- natural keys retained
  crm_lead_id     TEXT,
  product_user_id TEXT,
  segment         TEXT,
  valid_from      DATE,  valid_to  DATE -- SCD Type 2 history
);
```

The ontology solution is semantic — it doesn't tell you where to put the rows,
it tells you what the concepts *are* and how they relate, so any system can
implement it consistently:

```text
Ontology (informally rendered, OWL-flavoured):

Class:    Party
Class:    CompletedOrder ⊑ Order
Property: placedOrder  Party → Order
Property: hasAccount   Party → Account

-- Defined classes: membership is DERIVED, not asserted
Customer ≡ Party ⊓ ∃ placedOrder.CompletedOrder
Prospect ≡ Party ⊓ ¬∃ placedOrder.CompletedOrder
-- note: disjointness now follows from the definitions.
-- It doesn't need declaring, and declaring it separately is how
-- people accidentally make their ontology inconsistent.
```

Those two `≡` lines are the tell. They aren't columns, and they aren't
constraints on a table — they're *definitions*, and a reasoner given a Party with
one completed order will classify it as a Customer on its own. Nobody writes that
logic again in the next system. A data model can enforce a rule inside one
database; an ontology states what a thing *is*, once, for everywhere.

The subtlety that trips up most first ontologies is worth stating plainly,
because it's the difference between a model that works and one that quietly
does nothing. **OWL derives; it does not validate.** It is *monotonic* — new
facts can only add conclusions, never retract them — so if you assert
`Customer disjointWith Prospect` and then hand the reasoner a Prospect who has
placed an order, you don't get a helpful reclassification. You get a logical
inconsistency, and the reasoner stops being useful. And because OWL is
*open-world*, an axiom like "every Customer has at least one Account" does not
flag a Customer whose Account is missing from your data; it cheerfully infers
that one exists somewhere. If what you wanted was a check that fails, that's a
different tool:

```text
Shape (SHACL — validation, closed over your data):

CustomerShape
  targetClass:  Customer
  property hasAccount  { minCount: 1 }   -- FAILS if the data omits it
  property hasContact  { minCount: 1; class: Person }
```

Same vocabulary, opposite jobs: OWL says what follows, SHACL says what must be
present. Reach for the first when you want a machine to conclude something, the
second when you want it to complain — and the
[OWL 2 primer](https://www.w3.org/TR/owl2-primer/) and
[SHACL specification](https://www.w3.org/TR/shacl/) are the authoritative
references when a vendor's "semantic layer" blurs the two.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 350" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="ontology-vs-data-model-t ontology-vs-data-model-d">
  <title id="ontology-vs-data-model-t">One ontology above many data models</title>
  <desc id="ontology-vs-data-model-d">A single ontology at the top defines Customer as a kind of Party, disjoint from Prospect, with a hasAccount property. Below it sit three separate implementations of that same meaning: a warehouse star schema with dim_customer, a CRM object model with Lead and Account, and an application's third-normal-form users table.</desc>
  <rect x="230" y="16" width="340" height="64" rx="6" fill="#c8472b"/>
  <text x="400" y="42" font-size="14" fill="#f6f3ec" text-anchor="middle" font-weight="700">Ontology — meaning</text>
  <text x="400" y="63" font-size="11" fill="#f6f3ec" text-anchor="middle">Customer ⊑ Party · hasAccount · disjointWith Prospect</text>
  <text x="400" y="102" font-size="11" fill="#8b857a" text-anchor="middle">one definition, application-independent, machine-reasonable</text>
  <line x1="300" y1="80" x2="150" y2="150" stroke="#cabfac" stroke-width="2"/>
  <line x1="400" y1="80" x2="400" y2="150" stroke="#cabfac" stroke-width="2"/>
  <line x1="500" y1="80" x2="650" y2="150" stroke="#cabfac" stroke-width="2"/>
  <rect x="50" y="150" width="200" height="72" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="150" y="177" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">warehouse model</text>
  <text x="150" y="198" font-size="10" fill="#56514a" text-anchor="middle">dim_customer, star schema</text>
  <rect x="300" y="150" width="200" height="72" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="400" y="177" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">CRM model</text>
  <text x="400" y="198" font-size="10" fill="#56514a" text-anchor="middle">Lead, Account objects</text>
  <rect x="550" y="150" width="200" height="72" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="650" y="177" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">app model</text>
  <text x="650" y="198" font-size="10" fill="#56514a" text-anchor="middle">users table, 3NF</text>
  <text x="400" y="256" font-size="12" fill="#1c1a17" text-anchor="middle">Data models — structure: three implementations of one meaning</text>
  <text x="400" y="296" font-size="12" fill="#8b857a" text-anchor="middle">the ontology is what they should all agree on; the models are how each system honours it</text>
  <text x="400" y="318" font-size="12" fill="#8b857a" text-anchor="middle">get the meaning wrong once and all three inherit the mistake</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">One ontology, many data models: meaning above, structure below.</figcaption>
</figure>

## What your semantic layer already is

Here's the part most ontology writing misses, and most data teams need to hear:
if you have a well-built [semantic layer](/essays/what-is-a-semantic-layer/),
you already own a lightweight ontology. Defining *revenue* once, in one governed
place, so every dashboard and notebook returns the same number, is an act of
ontology in everything but formalism —
[conformed dimensions](/essays/conformed-dimensions/) are the same instinct
applied to dimensions, and a [data contract](/essays/data-contracts-are-a-cultural-problem/)
is that agreement made enforceable.

What a true ontology adds beyond a semantic layer is threefold: **formal
semantics** (axioms a reasoner can act on), **relationship modelling as a
first-class citizen** (not just measures sliced by dimensions), and
**application independence** (meaning that outlives the warehouse it was first
implemented in). Each of those has a cost, which is why the honest answer for
most teams is *strengthen the semantic layer first, and reach for formal
ontology only when one of those three is genuinely the binding constraint.*

## Why this stopped being academic

Ontologies had a long winter for a good reason: they were expensive to build,
hard to keep in sync with reality, and mostly consumed by other ontologists. What
changed is the reader. When the consumer of your schema was an analyst, tribal
knowledge filled the gaps — everyone knew that `cust_flg_2` meant enterprise
tier. When the consumer is a language model generating SQL, there is no tribal
knowledge; there is only what the model can read. This is measurable, not
rhetorical: the [BIRD text-to-SQL benchmark](https://bird-bench.github.io/) was
built specifically to test queries over messy real-world schemas, and its
headline finding is that supplying external knowledge — the human explanation of
what a column actually means — moves execution accuracy substantially, while
accuracy still degrades sharply on questions spanning several entities and
relationships. That is exactly the territory where a data model is silent and an
ontology speaks.

That's the real thesis, and it's older than the technology: **the discipline of
declaring meaning explicitly, before anyone queries anything, is the thing that
makes data trustworthy.** Kimball called it declaring the
[grain](/essays/fact-table-grain/) and conforming dimensions. The semantic layer
calls it defining a metric once. Ontologists call it formalising a domain. Same
instinct, three vocabularies, and the machines just made it non-optional.

## When to reach for which

**Build a data model** — always. It's not optional; something has to store the
rows, and structural discipline ([declared grain](/essays/fact-table-grain/),
[star schemas](/patterns/star-schema/), keys) is what keeps analytics honest.

**Build a semantic layer** when more than one tool queries the same data and you
need one definition to win.

**Build a formal ontology** when meaning must be shared across many systems or
organisations, when the *relationships* between entities are the analytical
product (fraud rings, supply chains, drug interactions), when regulation
requires machine-checkable definitions, or when you're grounding AI systems that
must reason over connections rather than scan columns.

And beware the failure mode that gave ontologies their reputation: a beautiful,
formally correct model of a domain that no system implements and no query
touches. A data model can be wrong for tomorrow's questions; an ontology can be
too abstract to ever be right about today's. The strongest architectures use
both, at their proper altitudes — meaning declared once above, structure
optimised deliberately below.
