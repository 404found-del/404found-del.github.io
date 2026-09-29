---
title: "HOOK vs Data Vault: What the Hook Pattern Actually Is"
kicker: "Field Notes"
topic: "Modeling"
description: "HOOK is not a Data Vault pattern. It is a separate, lighter alternative built by someone who found Data Vault too heavy. What it is, and where each fits."
date: 2026-09-29 07:00:00 +0530
last_modified_at: 2026-09-29
faq:
  - q: "Is HOOK part of Data Vault?"
    a: "No. This is the most common misunderstanding, and the phrasing 'hook pattern in Data Vault' contains a category error. HOOK is a separate data warehousing approach created by Andrew Foad, explicitly as an alternative to Data Vault rather than an extension of it. Data Vault has hubs, links and satellites; it has no construct called a hook. Foad describes HOOK as his attempt to solve problems he encountered on Data Vault projects, which makes the two competitors rather than components."
  - q: "What is a hook in the HOOK methodology?"
    a: "A hook is a structure that records the business keys identifying instances of a business concept. If you have a Customer concept, a Customer hook records all the business keys for customers. Hooks can also represent relationships between concepts, so a Sales hook might associate Customer and Product. Importantly, hooks can be physical tables but do not have to be: their existence may simply be implied by the keys projected onto the data."
  - q: "What are bags and keysets in HOOK?"
    a: "A bag is a virtual construct, usually a view, that aligns raw source-aligned data to concepts in the business glossary without changing the underlying data. A keyset qualifies business keys so that Customer #123 from System X is never confused with Customer #123 from System Y; each keyset has its own identifier used to prefix keys from that source. Together with the business glossary and hooks, they are the four components of the method. Note that Foad's later talks call the bag a frame; it is the same construct under a newer name."
  - q: "How is HOOK different from Data Vault in practice?"
    a: "Data Vault restructures incoming data into hubs, links and satellites, so modelling happens before loading and the physical model is the deliverable. HOOK leaves the source structure alone and adds qualified business keys as extra columns, usually through a view, so loading and modelling stay independent. Foad summarises it as ELO rather than ELT: extract, load, organise, with no transformation step. The practical trade is that HOOK defers structural work to the consumption layer instead of doing it up front."
  - q: "Should I use HOOK instead of Data Vault?"
    a: "For most teams, probably not yet, and the reason is adoption rather than design. Data Vault has two decades of books, certification, consultancies and automation tooling behind it, and hiring for it is possible. HOOK is largely one person's body of work with a small community, so you would be adopting it without a hiring pool, a certification path or mature tooling. The ideas are worth reading regardless, particularly if Data Vault's rigour is failing on your project, which is the exact problem HOOK was built to address."
  - q: "Does HOOK turn a data lake into a lakehouse?"
    a: "Foad argues it does, on the reasoning that data lake storage already satisfies Inmon's non-volatile and time-variant criteria, and that HOOK supplies the subject-oriented and integrated criteria without moving any data. That claim is contested in the comments on his own cookbook, on the grounds that the four criteria describe one integrated layer rather than a checklist to be satisfied piecemeal. Treat it as an interesting argument rather than a settled definition, particularly since 'lakehouse' is defined loosely by most vendors anyway."
  - q: "Who created HOOK and where is it documented?"
    a: "Andrew Foad, who publishes it as The Hook Cookbook, a chapter-by-chapter Substack, alongside a series of HOOK vs Data Vault articles. It is a single-author body of work rather than a standards-backed methodology, which is both its strength, since it is coherent and readable, and its weakness, since there is no independent body maintaining it."
---

If you search for the "hook pattern in Data Vault", you will find very little, and
the reason is that the question contains a category error. **Data Vault has no
construct called a hook.** It has hubs, links and satellites, and that is the
whole vocabulary.

HOOK is a *different* data warehousing approach, created by
[Andrew Foad](https://hookcookbook.substack.com/), explicitly as an alternative to
Data Vault rather than an extension of it. In his own words, "HOOK is my attempt
to solve problems that I encountered with data vault." The two are competitors.

That confusion is worth clearing up properly, because the underlying question
people are actually asking — *is there a lighter way to do what Data Vault does?*
— is a good one.

## Why HOOK exists

Foad is unusually candid about the motivation, and about the originality of the
idea. From the cookbook:

> There is nothing inherently wrong with the current data warehousing approaches;
> Data Vault and Dimensional modelling work well if done right. Unfortunately,
> they are rarely done right.

His argument is not that Data Vault is wrong. It is that Data Vault demands a
level of rigour that real projects abandon the moment delivery pressure arrives,
and a method that only works when followed perfectly is a method that mostly
fails. He also says plainly that HOOK "is nothing new, not really... a
re-imagining of ideas put forward by" Inmon, Linstedt and Kimball.

That is a more honest framing than most methodology pitches manage, and it sets
up the actual design goal: keep the integration benefits, drop the up-front
restructuring.

## The four components

HOOK has four parts, and genuinely only four.

**The business glossary** is the foundation, and it is a hard gate: you may only
align data to a business concept once that concept has been formally defined. If
the organisation cannot say what it means by *Customer*, HOOK's position is that
you have no business integrating customer data yet. This is the same instinct as a
[semantic layer](/essays/what-is-a-semantic-layer/), applied earlier.

**A hook** is a structure recording the business keys that identify instances of a
concept. A Customer hook records all the business keys for customers. Hooks can
also express relationships — a Sales hook associating Customer and Product. The
detail that surprises people: **hooks can be physical tables but do not have to
be.** Their existence may simply be implied by the keys projected onto the data.

**A bag** is a virtual construct — normally a view — that aligns raw,
source-shaped data to glossary concepts without changing it. The source table
stays exactly as it landed; the bag wraps it and exposes qualified business keys
alongside the original columns.

A note on vocabulary, because the sources disagree: the cookbook (2022) calls this
construct a **bag**. Foad's more recent talks call it a **frame**. Same thing,
newer name. If you read both and think you have missed a fifth component, you
haven't.

**A keyset** qualifies business keys across sources. Customer #123 in System X is
very probably not Customer #123 in System Y, so each keyset has an identifier that
prefixes the keys originating from that system. This is the same problem that
[surrogate keys](/essays/surrogate-keys-vs-natural-keys/) solve in a dimensional
model, handled by qualification rather than by substitution.

## The actual difference from Data Vault

<figure style="margin:2rem auto;text-align:center;">
<svg class="dia-mob" viewBox="0 0 400 600" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="hvd-mt hvd-md">
  <title id="hvd-mt">Data Vault restructures; HOOK annotates</title>
  <desc id="hvd-md">Two approaches shown one above the other from the same source tables. Data Vault, first, transforms source data into hubs, links and satellites, so the physical model is rebuilt before loading and modelling must happen up front. HOOK, below, leaves the source tables unchanged and defines a bag view over each one that adds qualified business keys, so the structure is untouched and modelling is deferred to the consumption layer.</desc>
  <text x="200" y="22" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Data Vault — restructure</text>
  <rect x="40" y="36" width="320" height="26" rx="4" fill="#1c1a17"/>
  <text x="200" y="54" font-size="11" fill="#f6f3ec" text-anchor="middle">source tables</text>
  <line x1="200" y1="62" x2="200" y2="88" stroke="#cabfac" stroke-width="2"/>
  <text x="248" y="80" font-size="10" fill="#a4391f">transform</text>
  <rect x="40" y="88" width="96" height="40" rx="4" fill="#c8472b"/>
  <text x="88" y="113" font-size="11" fill="#f6f3ec" text-anchor="middle">hubs</text>
  <rect x="152" y="88" width="96" height="40" rx="4" fill="#c8472b"/>
  <text x="200" y="113" font-size="11" fill="#f6f3ec" text-anchor="middle">links</text>
  <rect x="264" y="88" width="96" height="40" rx="4" fill="#c8472b"/>
  <text x="312" y="113" font-size="11" fill="#f6f3ec" text-anchor="middle">satellites</text>
  <text x="200" y="152" font-size="10" fill="#56514a" text-anchor="middle">the physical model IS the deliverable</text>
  <text x="200" y="170" font-size="10" fill="#a4391f" text-anchor="middle">modelling happens before loading</text>
  <line x1="20" y1="196" x2="380" y2="196" stroke="#ddd6c8" stroke-width="1.5" stroke-dasharray="4 4"/>
  <text x="200" y="232" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">HOOK — annotate</text>
  <rect x="40" y="246" width="320" height="26" rx="4" fill="#1c1a17"/>
  <text x="200" y="264" font-size="11" fill="#f6f3ec" text-anchor="middle">source tables</text>
  <line x1="200" y1="272" x2="200" y2="298" stroke="#cabfac" stroke-width="2"/>
  <text x="252" y="290" font-size="10" fill="#8b857a">wrap in a view</text>
  <rect x="40" y="298" width="320" height="56" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="320" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">bag (a view over the source)</text>
  <text x="200" y="340" font-size="10" fill="#56514a" text-anchor="middle">same columns + qualified business keys</text>
  <rect x="40" y="372" width="150" height="34" rx="4" fill="#c8472b"/>
  <text x="115" y="393" font-size="10" fill="#f6f3ec" text-anchor="middle">hook: customer</text>
  <rect x="210" y="372" width="150" height="34" rx="4" fill="#c8472b"/>
  <text x="285" y="393" font-size="10" fill="#f6f3ec" text-anchor="middle">hook: product</text>
  <text x="200" y="430" font-size="10" fill="#56514a" text-anchor="middle">source structure untouched</text>
  <text x="200" y="448" font-size="10" fill="#a4391f" text-anchor="middle">modelling deferred to consumption</text>
  <line x1="20" y1="476" x2="380" y2="476" stroke="#ddd6c8" stroke-width="1"/>
  <text x="200" y="504" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">The trade</text>
  <text x="200" y="526" font-size="10" fill="#8b857a" text-anchor="middle">Data Vault pays up front and delivers</text>
  <text x="200" y="542" font-size="10" fill="#8b857a" text-anchor="middle">a queryable integrated model.</text>
  <text x="200" y="566" font-size="10" fill="#8b857a" text-anchor="middle">HOOK pays later and delivers</text>
  <text x="200" y="582" font-size="10" fill="#8b857a" text-anchor="middle">annotated source data.</text>
</svg>
<svg class="dia-desk" viewBox="0 0 800 330" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="hvd-t hvd-d">
  <title id="hvd-t">Data Vault restructures; HOOK annotates</title>
  <desc id="hvd-d">Two approaches from the same source tables, side by side. Data Vault, on the left, transforms source data into hubs, links and satellites, so the physical model is rebuilt before loading and modelling must happen up front. HOOK, on the right, leaves the source tables unchanged and defines a bag view over each one that adds qualified business keys, so the structure is untouched and modelling is deferred to the consumption layer.</desc>
  <text x="200" y="24" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">Data Vault — restructure</text>
  <rect x="50" y="40" width="300" height="28" rx="4" fill="#1c1a17"/>
  <text x="200" y="59" font-size="11" fill="#f6f3ec" text-anchor="middle">source tables</text>
  <line x1="200" y1="68" x2="200" y2="98" stroke="#cabfac" stroke-width="2"/>
  <text x="250" y="88" font-size="11" fill="#a4391f">transform</text>
  <rect x="50" y="98" width="90" height="44" rx="4" fill="#c8472b"/>
  <text x="95" y="125" font-size="11" fill="#f6f3ec" text-anchor="middle">hubs</text>
  <rect x="155" y="98" width="90" height="44" rx="4" fill="#c8472b"/>
  <text x="200" y="125" font-size="11" fill="#f6f3ec" text-anchor="middle">links</text>
  <rect x="260" y="98" width="90" height="44" rx="4" fill="#c8472b"/>
  <text x="305" y="125" font-size="11" fill="#f6f3ec" text-anchor="middle">satellites</text>
  <text x="200" y="172" font-size="11" fill="#56514a" text-anchor="middle">the physical model IS the deliverable</text>
  <text x="200" y="194" font-size="11" fill="#a4391f" text-anchor="middle">modelling happens before loading</text>
  <line x1="400" y1="34" x2="400" y2="250" stroke="#ddd6c8" stroke-width="1.5" stroke-dasharray="4 4"/>
  <text x="600" y="24" font-size="13" fill="#1c1a17" text-anchor="middle" font-weight="700">HOOK — annotate</text>
  <rect x="450" y="40" width="300" height="28" rx="4" fill="#1c1a17"/>
  <text x="600" y="59" font-size="11" fill="#f6f3ec" text-anchor="middle">source tables</text>
  <line x1="600" y1="68" x2="600" y2="98" stroke="#cabfac" stroke-width="2"/>
  <text x="652" y="88" font-size="11" fill="#8b857a">wrap in a view</text>
  <rect x="450" y="98" width="300" height="52" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="600" y="120" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">bag (a view over the source)</text>
  <text x="600" y="140" font-size="10" fill="#56514a" text-anchor="middle">same columns + qualified business keys</text>
  <rect x="450" y="166" width="142" height="32" rx="4" fill="#c8472b"/>
  <text x="521" y="187" font-size="10" fill="#f6f3ec" text-anchor="middle">hook: customer</text>
  <rect x="608" y="166" width="142" height="32" rx="4" fill="#c8472b"/>
  <text x="679" y="187" font-size="10" fill="#f6f3ec" text-anchor="middle">hook: product</text>
  <text x="600" y="222" font-size="11" fill="#56514a" text-anchor="middle">source structure untouched</text>
  <text x="600" y="244" font-size="11" fill="#a4391f" text-anchor="middle">modelling deferred to consumption</text>
  <line x1="40" y1="272" x2="760" y2="272" stroke="#ddd6c8" stroke-width="1"/>
  <text x="400" y="300" font-size="12" fill="#8b857a" text-anchor="middle">Data Vault pays up front and delivers a queryable integrated model.</text>
  <text x="400" y="320" font-size="12" fill="#8b857a" text-anchor="middle">HOOK pays later and delivers annotated source data.</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">The same integration idea, on opposite sides of the load. One restructures; the other annotates.</figcaption>
</figure>

[Data Vault](/patterns/data-vault/) restructures. Source data is decomposed into
hubs (business keys), links (relationships) and satellites (descriptive attributes
over time). The physical model is the deliverable, and it has to be designed
before you can load anything into it.

HOOK annotates. The source table lands and stays as it is. A bag view sits on top
and adds qualified business keys as extra columns. Foad's summary is **ELO rather
than ELT** — extract, load, organise, with no transformation step. Loading and
modelling become independent: the model is a layer of definitions over loaded
data, not a structure maintained alongside it.

| | Data Vault | HOOK |
|---|---|---|
| **Core objects** | Hubs, links, satellites | Glossary, hooks, bags, keysets |
| **Source structure** | Decomposed | Preserved |
| **When you model** | Before loading | Deferred to consumption |
| **Physical footprint** | New tables | Usually just views |
| **Changing your mind** | Refactor the model | Add or drop a column |
| **What you hand a consumer** | An integrated model | Annotated source data |
| **Maturity** | 20 years, certification, tooling | One author, small community |

The last row is the one that decides most real decisions, and I'll come back to it.

## Where the argument is strongest

The genuinely good idea here is **decoupling integration from restructuring.**

Data Vault's integration value comes from agreeing business keys and recording
relationships. Almost none of that value strictly requires physically splitting
tables into hubs and satellites — that is an implementation choice which happens
to be expensive, and which has to be right before the first load. HOOK's claim is
that you can get the subject-orientation and integration by *qualifying and
projecting keys*, leaving the bytes alone.

That is a real insight, and it maps onto something the industry already learned
elsewhere: [open table formats](/essays/what-is-an-open-table-format/) also won by
adding a metadata layer over untouched files rather than by rewriting data into a
proprietary shape.

It also makes being wrong cheap. Getting a business key wrong in Data Vault means
refactoring hubs and reloading satellites. In HOOK it means editing a view.

## Where I would be careful

**The lakehouse claim is contested, including by his own readers.** Foad argues
that data lake storage already satisfies Inmon's non-volatile and time-variant
criteria, so layering HOOK on top supplies the remaining two and yields a
[lakehouse](/glossary/data-lakehouse/). A commenter on that very chapter pushes
back that Inmon's four criteria describe one integrated layer rather than a
checklist to tick off separately, and that storing files immutably does not make
them a warehouse. I find the objection reasonable. It does not damage HOOK as a
method; it just means the equation is rhetoric rather than a definition.

**Deferring modelling is not the same as avoiding it.** The structural work moves
to the consumption layer under the banner of "just enough modelling". For a small
number of well-understood consumers that is a genuine saving. For many consumers
with conflicting requirements, it may just relocate the cost — and relocate it to
the layer where it is least likely to be governed. Data Vault's rigour is
expensive precisely because it forces that conversation early.

**Adoption is the real constraint.** Data Vault has two decades of books,
certification, consultancies and automation tooling, and you can hire for it.
HOOK is essentially one person's body of work. Adopting it means no hiring pool,
no certification path, no mature tooling, and a bus factor of one for the
methodology itself. That is a serious cost for a warehouse expected to outlive
several teams.

## So which should you use

For most organisations, **Data Vault if you need Data Vault's guarantees and can
actually sustain its discipline; dimensional modelling if you cannot.** That
second clause is doing a lot of work, and it is the same conclusion as
[Data Vault vs dimensional modelling](/essays/data-vault-vs-dimensional-modeling/):
Data Vault earns its keep on auditability and multi-source integration, and is
overkill almost everywhere else.

HOOK is worth reading rather than adopting wholesale, and it is *most* worth
reading if Data Vault's rigour is currently failing on your project — because
that is the precise failure mode it was designed around. The keyset idea in
particular transfers cleanly into other methods. You can qualify business keys
across source systems without adopting anything else.

What you should not do is go looking for hooks in your Data Vault
implementation. They are not in there.
