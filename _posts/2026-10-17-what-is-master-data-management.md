---
title: "What Is Master Data Management, and Why Does MDM Fail?"
kicker: "Field Notes"
topic: "Governance"
description: "Master data management is sold as a product category. It is an organisational agreement with software attached, which is why buying the tool first fails."
date: 2026-10-17 07:00:00 +0530
last_modified_at: 2026-10-17
faq:
  - q: "What is master data management?"
    a: "Master data management is the practice of maintaining one agreed version of the entities a business shares across systems — customer, product, supplier, location, employee. It combines matching records that refer to the same real-world thing, merging them under survivorship rules into a golden record, and governing who may change that record and on what authority. The software does the matching and merging; the agreement about what counts as a customer and whose definition wins is the part that is not software."
  - q: "What is a golden record in MDM?"
    a: "The single most trustworthy version of a master entity, assembled rather than found. Records referring to the same real-world thing are matched across source systems, then survivorship rules decide attribute by attribute which value survives — typically by ranking sources per field, so ERP wins on legal name and tax identifiers while CRM wins on contact preferences. The golden record is therefore a constructed artefact reflecting a set of decisions, not a record that existed somewhere waiting to be found."
  - q: "What are the four MDM implementation styles?"
    a: "Registry keeps a thin index of IDs and match keys and leaves the data in the source systems. Consolidation copies data into a hub, cleanses it and publishes a golden record for analytics, with no write-back. Coexistence keeps master records in both the hub and the sources and synchronises them. Centralized, also called a transaction hub, makes the hub the system of record where master data is authored directly. The order matters: each step increases both integration value and organisational commitment, and most programmes that jump straight to a transaction hub are underestimating the second."
  - q: "Why do MDM projects fail?"
    a: "Because they are run as software implementations when the hard part is a negotiation. Matching, merging and survivorship all require someone with authority to decide whose definition of a customer wins, which source is more trustworthy per attribute, and who may overrule a merge. If that authority does not exist before the tool arrives, the project stalls at exactly the point where those decisions become unavoidable — usually after the licence is signed. The common failure is not a bad product; it is a good product waiting on an answer nobody is empowered to give."
  - q: "What is the difference between MDM and a data catalog?"
    a: "A data catalog tells you what data exists, where it lives and what it means. MDM decides which record is correct and makes other systems use it. The catalog is descriptive and read-only over your estate; MDM is prescriptive and writes back. They are complementary, and a catalog is often the cheaper first step because it surfaces how many conflicting definitions of customer you have before you commit to resolving them."
  - q: "Is MDM the same as data governance?"
    a: "No, though they are frequently sold together. Data governance is the broader practice of deciding ownership, policy and accountability across all data. MDM is a specific application of that to shared master entities, with software that enforces the result. MDM without governance is a matching engine producing golden records nobody has agreed to honour, which is the most common way to spend a lot of money and change nothing."
  - q: "Do I need an MDM tool?"
    a: "Later than most vendors suggest, and possibly not at all. If the organisation cannot yet name an owner for customer, a dedicated tool will not create one. The cheap diagnostics first: count how many systems claim to define your most contested entity, and ask who is allowed to overrule the others. If that question has a clear answer, a tool will accelerate you. If it does not, the tool will surface the disagreement at enormous cost and then wait for you to resolve it anyway."
---

Every large organisation eventually discovers it does not know how many customers
it has. Sales counts accounts, finance counts billable entities, support counts
contacts, and the three numbers disagree by a margin nobody can explain. The
standard response is to buy master data management software.

That response is usually premature, and understanding why is most of what is
worth knowing about MDM.

## What master data actually is

**Master data is the set of entities a business shares across systems** —
customer, product, supplier, location, employee. It is the nouns, as distinct
from transactions, which are the verbs. An order is a transaction; the customer
who placed it and the product they bought are master data.

The defining property is that master data is *referenced by many systems and
owned by none of them in practice*. Every system that touches a customer has
opinions about what a customer is, and each of those opinions is encoded in a
schema somebody shipped years ago.

**Master data management** is the practice of maintaining one agreed version of
those entities. It has three parts, and they are not equally hard.

## The mechanical part: matching, merging, survivorship

<figure style="margin:2rem auto;text-align:center;">
<svg class="dia-mob" viewBox="0 0 400 620" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="mdm-mt mdm-md">
  <title id="mdm-mt">Every mechanical step in MDM rests on a human decision</title>
  <desc id="mdm-md">A pipeline runs from source systems through matching, merging and survivorship to a golden record. Beside each mechanical step sits the decision it depends on: matching needs agreement on what counts as the same customer and what match confidence is good enough; merging needs someone empowered to approve or reverse a merge; survivorship needs a per-attribute ranking of which source is more trustworthy. The software performs the steps; it cannot make the decisions.</desc>
  <text x="200" y="22" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">What the software does</text>
  <rect x="30" y="36" width="340" height="40" rx="4" fill="#1c1a17"/>
  <text x="200" y="53" font-size="11" fill="#f6f3ec" text-anchor="middle">CRM · ERP · billing · support</text>
  <text x="200" y="69" font-size="10" fill="#cabfac" text-anchor="middle">each with its own idea of "customer"</text>
  <line x1="200" y1="76" x2="200" y2="98" stroke="#cabfac" stroke-width="2"/>
  <rect x="30" y="98" width="340" height="34" rx="4" fill="#c8472b"/>
  <text x="200" y="120" font-size="11" fill="#f6f3ec" text-anchor="middle">MATCH — are these the same thing?</text>
  <text x="200" y="150" font-size="10" fill="#a4391f" text-anchor="middle">needs: what counts as the same customer,</text>
  <text x="200" y="165" font-size="10" fill="#a4391f" text-anchor="middle">and what confidence is good enough</text>
  <line x1="200" y1="176" x2="200" y2="196" stroke="#cabfac" stroke-width="2"/>
  <rect x="30" y="196" width="340" height="34" rx="4" fill="#c8472b"/>
  <text x="200" y="218" font-size="11" fill="#f6f3ec" text-anchor="middle">MERGE — combine the matches</text>
  <text x="200" y="248" font-size="10" fill="#a4391f" text-anchor="middle">needs: someone empowered to approve,</text>
  <text x="200" y="263" font-size="10" fill="#a4391f" text-anchor="middle">reject and reverse a merge</text>
  <line x1="200" y1="274" x2="200" y2="294" stroke="#cabfac" stroke-width="2"/>
  <rect x="30" y="294" width="340" height="34" rx="4" fill="#c8472b"/>
  <text x="200" y="316" font-size="11" fill="#f6f3ec" text-anchor="middle">SURVIVORSHIP — which value wins?</text>
  <text x="200" y="346" font-size="10" fill="#a4391f" text-anchor="middle">needs: a per-attribute ranking of which</text>
  <text x="200" y="361" font-size="10" fill="#a4391f" text-anchor="middle">source is more trustworthy, field by field</text>
  <line x1="200" y1="372" x2="200" y2="392" stroke="#cabfac" stroke-width="2"/>
  <rect x="30" y="392" width="340" height="44" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="412" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">golden record</text>
  <text x="200" y="429" font-size="10" fill="#56514a" text-anchor="middle">assembled, not found</text>
  <line x1="20" y1="466" x2="380" y2="466" stroke="#ddd6c8" stroke-width="1"/>
  <text x="200" y="494" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">The software performs every step.</text>
  <text x="200" y="514" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">It cannot make a single decision.</text>
  <text x="200" y="546" font-size="10" fill="#8b857a" text-anchor="middle">Each decision needs a person with the</text>
  <text x="200" y="561" font-size="10" fill="#8b857a" text-anchor="middle">authority to overrule a department.</text>
  <text x="200" y="588" font-size="10" fill="#8b857a" text-anchor="middle">If that person does not exist, the project</text>
  <text x="200" y="603" font-size="10" fill="#8b857a" text-anchor="middle">stalls here — after the licence is signed.</text>
</svg>
<svg class="dia-desk" viewBox="0 0 800 330" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="mdm-t mdm-d">
  <title id="mdm-t">Every mechanical step in MDM rests on a human decision</title>
  <desc id="mdm-d">On the left, a pipeline runs from source systems through matching, merging and survivorship to a golden record. On the right, the decision each mechanical step depends on: matching needs agreement on what counts as the same customer and what match confidence is good enough; merging needs someone empowered to approve or reverse a merge; survivorship needs a per-attribute ranking of which source is more trustworthy. The software performs the steps; it cannot make the decisions.</desc>
  <text x="200" y="22" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">What the software does</text>
  <text x="600" y="22" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">What it cannot do</text>
  <rect x="40" y="36" width="320" height="40" rx="4" fill="#1c1a17"/>
  <text x="200" y="53" font-size="11" fill="#f6f3ec" text-anchor="middle">CRM · ERP · billing · support</text>
  <text x="200" y="69" font-size="10" fill="#cabfac" text-anchor="middle">each with its own idea of "customer"</text>
  <line x1="200" y1="76" x2="200" y2="96" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="96" width="320" height="34" rx="4" fill="#c8472b"/>
  <text x="200" y="118" font-size="11" fill="#f6f3ec" text-anchor="middle">MATCH — are these the same thing?</text>
  <text x="440" y="112" font-size="11" fill="#a4391f">what counts as the same customer,</text>
  <text x="440" y="128" font-size="11" fill="#a4391f">and what confidence is good enough</text>
  <line x1="200" y1="130" x2="200" y2="150" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="150" width="320" height="34" rx="4" fill="#c8472b"/>
  <text x="200" y="172" font-size="11" fill="#f6f3ec" text-anchor="middle">MERGE — combine the matches</text>
  <text x="440" y="166" font-size="11" fill="#a4391f">someone empowered to approve,</text>
  <text x="440" y="182" font-size="11" fill="#a4391f">reject and reverse a merge</text>
  <line x1="200" y1="184" x2="200" y2="204" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="204" width="320" height="34" rx="4" fill="#c8472b"/>
  <text x="200" y="226" font-size="11" fill="#f6f3ec" text-anchor="middle">SURVIVORSHIP — which value wins?</text>
  <text x="440" y="220" font-size="11" fill="#a4391f">a per-attribute ranking of which source</text>
  <text x="440" y="236" font-size="11" fill="#a4391f">is more trustworthy, field by field</text>
  <line x1="200" y1="238" x2="200" y2="258" stroke="#cabfac" stroke-width="2"/>
  <rect x="40" y="258" width="320" height="40" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="200" y="276" font-size="12" fill="#1c1a17" text-anchor="middle" font-weight="700">golden record</text>
  <text x="200" y="292" font-size="10" fill="#56514a" text-anchor="middle">assembled, not found</text>
  <line x1="420" y1="30" x2="420" y2="300" stroke="#ddd6c8" stroke-width="1.5" stroke-dasharray="4 4"/>
  <text x="600" y="268" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">Each needs authority to</text>
  <text x="600" y="286" font-size="11" fill="#1c1a17" text-anchor="middle" font-weight="700">overrule a department.</text>
  <text x="400" y="322" font-size="12" fill="#8b857a" text-anchor="middle">The software performs every step and cannot make a single decision.</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">The pipeline is the easy half. Every box on the left waits on an answer from the right.</figcaption>
</figure>

**Matching** asks whether two records refer to the same real-world thing.
*Deterministic* matching compares exact keys — a tax identifier, a registration
number, an email. *Fuzzy* or probabilistic matching scores similarity when no
shared key exists, which is the usual case for customers and suppliers whose
names and addresses are typed by humans in a hurry.

**Merging** combines matched records. Most implementations auto-merge above a
confidence threshold, queue the middle band for human review, and leave the rest
alone.

**Survivorship** decides, attribute by attribute, which value wins. The standard
approach ranks sources per field: ERP wins on legal name and tax data, CRM wins
on contact preferences, the billing system wins on the address that actually
receives invoices. A single blanket rule across every field is the classic
mistake, because it lets a source that is authoritative for one attribute
overwrite a better source for another.

The output is the **golden record** — and the word "record" oversells it. It is
not a row that existed somewhere waiting to be found. **It is assembled**, and it
reflects a set of decisions about trust. Change the survivorship ranking and you
get a different golden record from identical inputs.

## The four implementation styles

Most MDM writing organises implementations into four styles. They are a genuinely
useful ladder, and they are usually presented as a vendor-neutral industry
standard. A caveat on provenance: this taxonomy is widely attributed, and I could
not trace it to a single authoritative primary source — almost every citation
leads to a vendor glossary. Treat the names as common usage rather than a
specification.

| Style | Where master data lives | Writes back? | What it costs you |
|---|---|---|---|
| **Registry** | Sources keep it; hub holds IDs and match keys only | No | Least disruption, least benefit |
| **Consolidation** | Copied into a hub, cleansed, published | No | Good for analytics, fixes nothing operationally |
| **Coexistence** | Both hub and sources, synchronised | Yes | Sync complexity, and the hub is not the system of record |
| **Centralized / transaction hub** | The hub, authored directly | N/A — it *is* the source | Maximum benefit, maximum organisational commitment |

Read down that last column. **The ladder is not primarily technical.** Each rung
increases how much authority the hub has over systems other teams own, and that
is a political quantity, not an architectural one. Programmes that start at
registry or consolidation and earn their way upward tend to survive. Programmes
that begin at transaction hub because that is where the value is have skipped the
part where everyone agrees to be overruled.

## Why MDM projects fail

Not because the software is bad. Modern matching engines are genuinely good, and
the fuzzy-matching problem is largely solved for ordinary cases.

They fail because **every mechanical step above has a prerequisite that is a
decision, and the decision requires authority somebody has to actually hold.**

- Matching needs agreement on what counts as *the same customer*. Is a
  subsidiary the same customer as its parent? Is a person who moved house the
  same person? Finance and sales will answer differently, and both answers are
  defensible within their own department's purpose.
- Merging needs someone who can approve a merge over the objection of the team
  whose record loses.
- Survivorship needs a per-field ranking that says, in writing, that one
  department's data is less trustworthy than another's.

None of these is a configuration question. All of them are *whose definition
wins*, which is a question about org charts. A tool makes them unavoidable and
explicit, which is useful — but it surfaces them at the most expensive possible
moment, after a licence is signed and a delivery date is public.

This is the same shape as
[data quality problems being org-chart problems](/essays/data-quality-problems-are-org-chart-problems/),
and the same reason a [data contract](/glossary/data-contract/) is
[mostly a cultural artefact](/essays/data-contracts-are-a-cultural-problem/). The
pattern repeats because the underlying constraint repeats: software can enforce
an agreement and cannot manufacture one.

## What to do before buying anything

Two diagnostics, both cheap, both revealing.

**Count the claimants.** For your most contested entity, list every system that
believes it defines that entity. Not systems that *store* it — systems whose
owners would argue if you told them their version was wrong. The number is
usually higher than expected and is the real scope of the problem.

**Ask who can overrule.** Name the person who can tell finance that sales owns
the customer definition, and make them say it out loud. If no such person exists,
you do not have an MDM project; you have an escalation waiting to happen.

If the second question has a clear answer, a tool will accelerate you
considerably. If it does not, the useful first step is cheaper and less
political: a [data catalog](/essays/what-is-a-data-catalog/) to document how many
conflicting definitions exist, or a
[semantic layer](/essays/what-is-a-semantic-layer/) to make the disagreement
visible in reporting before you try to resolve it at source.

## Where it meets the warehouse

For analytics specifically, there is a narrower and much cheaper version of this
problem, and it is worth knowing you may only need that one.

If your goal is consistent reporting rather than consistent operations, you do
not need to fix the source systems. You need
[conformed dimensions](/essays/conformed-dimensions/): one shared customer
dimension that every fact table references, with the reconciliation done once on
the way in. That is MDM's analytical benefit without MDM's political cost, and it
is a well-trodden path.

MDM proper earns its keep when the *operational* systems need to agree — when a
shipment goes to the wrong address because billing and logistics disagree about
which one is current. That is a real problem and worth real money. It is just a
different problem from the one most MDM purchases are trying to solve.

**The summary worth keeping:** master data management is an organisational
agreement with software attached. Buy the software when you have the agreement,
or at minimum when you know who is empowered to make it. Buying it to *produce*
the agreement is the expensive way to discover you needed it first.
