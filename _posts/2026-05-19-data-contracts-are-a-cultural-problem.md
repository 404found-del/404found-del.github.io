---
title: "Data Contracts Are a Cultural Problem"
kicker: "Essay"
topic: "Governance"
date: 2026-05-19
last_modified_at: 2026-07-26
description: "A schema check is the easy 10% of a data contract. The other 90% is an organizational agreement that no YAML file can enforce for you."
faq:
  - q: "What is a data contract?"
    a: "An agreement between the team that produces a dataset and the teams that consume it, covering what fields exist, what they mean, what guarantees hold, and how change will be communicated. The schema file people point to is the encoding of that agreement, not the agreement itself."
  - q: "Why do data contracts fail?"
    a: "Because teams adopt the artefact without the agreement. A schema check written by a consumer and imposed on a producer who never consented is a tripwire, not a contract; it fails the consumer's pipeline while the producer keeps shipping. The technology works fine. What is missing is that nobody negotiated."
  - q: "What is the difference between a data contract and a schema?"
    a: "A schema describes structure a machine can validate. A contract adds the parts a machine cannot supply: who owns the data, what they have committed to, what notice consumers get before a breaking change, and what happens when the commitment is broken. Every contract contains a schema; a schema on its own commits nobody to anything."
  - q: "How do you start implementing data contracts?"
    a: "Start with the relationship, not the tooling. Find the single upstream-downstream pair where breakage costs the most, get both teams together, and write down in plain language what the producer can commit to and what the consumer actually needs. Make the producer a co-author. Only then encode it and wire up a check that fails their pipeline, not just yours."
---

The phrase "data contract" makes the hard thing sound easy. It conjures a tidy
artefact — a YAML file, a JSON schema, a validation step in CI — and implies that
once you have the artefact, you have the contract. You do not. The artefact is the
easy ten percent. The other ninety percent is an agreement between human beings
about who owes what to whom, and no schema validator has ever enforced *that*.

## What a contract actually is

A data contract is a promise from a **producer** to a **consumer**. The producer
says: this data will arrive, in this shape, with this meaning, at this cadence,
with these guarantees — and if any of that is going to change, you'll hear about it
before it breaks you.

Read that promise again and notice how little of it is about types. "In this shape"
is the schema part, and it's genuinely useful — catching a column rename before it
reaches production is a real win. But "with this meaning," "at this cadence,"
"you'll hear about it before it breaks you" — these are *commitments*, not
constraints. They describe a relationship. And relationships are not enforced by
files; they're enforced by accountability.

> A schema tells you the `status` column is a string. It cannot tell you that
> `status = 'closed'` quietly started meaning two different things last March
> because an upstream team shipped a feature and told no one.

That second failure — the semantic drift, the silent change of meaning — is the one
that actually destroys trust in data. And it's precisely the failure a schema check
sails straight past.

## Why contracts fail

When data contract initiatives fail, and many do, the autopsy almost always finds
the same three causes. None of them are technical.

**No one owns the producing system.** The data is emitted by a service whose team
considers analytics someone else's problem. They didn't agree to a contract; a
contract was *declared at them* by a downstream team with no leverage. The first
time shipping velocity conflicts with the contract, the contract loses, because no
one on the producing side ever signed up to defend it.

**There's no consequence for breaking it.** A promise with no cost for breaking it
is not a promise; it's a suggestion. If a producer can break the contract and the
only result is a Slack message from an annoyed analyst, the contract has no teeth.
Real contracts are backed by something — a failing build that blocks *their*
deploy, an SLA tied to a team's objectives, a review gate they actually have to
pass.

**It was written by the wrong people.** Contracts drafted entirely by the data team
encode what the data team *wishes* were true, not what the producer can actually
commit to. A contract the producer didn't help write is a wish list, and wish
lists rot.

## The cultural prerequisites

This is why I've come to think of data contracts as a cultural problem with a
technical surface. Before the YAML is worth writing, three things have to be true
in the organisation:

- **Producers accept that their output is a product.** The moment a team emits data
  that another team depends on, they are running a product whether they like it or
  not. The contract just makes the existing dependency explicit. Cultures that
  resist this resist the contract.
- **Ownership is unambiguous.** Every important dataset has a name attached — a team
  that is genuinely responsible for its shape and meaning, with the authority to
  make and defend decisions about it. Shared ownership is no ownership.
- **Breaking changes have a cost the producer feels.** Until the producer has skin
  in the game, the contract is decoration.

Get those right and the technical part becomes almost trivial — a schema in version
control, a check in CI, a changelog, a deprecation window. Get them wrong and the
most beautiful contract tooling in the world will sit unused while data quietly
breaks in production exactly as before.

## What to actually do

If you're trying to introduce contracts, resist the urge to start with the tooling.
Start with the relationship. Find the one upstream–downstream pair where breakage
hurts the most, and get *both* teams in a room. Write down, in plain language, what
the producer can commit to and what the consumer truly needs. Make the producer a
co-author, not a target. Then — and only then — encode the agreement in a schema and
wire up a check that fails *their* pipeline, not just yours.

The file you produce at the end will look like every "data contract" example on the
internet. But it will work, because underneath it sits the thing those examples
never show: two teams who actually agreed.

The same confusion between artefact and outcome shows up one layer over, in the
difference between
[data observability and data quality](/essays/data-observability-vs-data-quality/):
one is a set of instruments, the other is a property of the data, and buying the
first does not produce the second.

The schema is the artefact. The agreement is the contract. Don't mistake one for
the other.
