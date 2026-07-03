---
title: "Why a New Data Source Still Takes Weeks When You Already Have a Connector"
kicker: "Field Notes"
topic: "Engineering"
description: "A connector copies data from source to destination — and that's one step out of eleven. Here's the other ten, and why 'just add a connector' quietly hides most of the actual work of onboarding a data source."
date: 2026-07-01
faq:
  - q: "If I have a connector, why does adding a data source still take so long?"
    a: "Because the connector only does one part of the job — copying data from source to destination. The time goes into everything around it: understanding the data, securing the path, wiring authentication, building change-data-capture logic, validating correctness, orchestrating pipelines, testing end to end, and surfacing the data to users. The copy is fast; certifying and delivering the data is the work."
  - q: "What does a data connector actually do?"
    a: "It copies data from a source system to a destination, and it does a one-time full load well. What it does not do is make that data correct, secure, in-sync, governed, or usable — those are separate engineering tasks the connector never touches."
  - q: "Why isn't the initial load the hard part?"
    a: "A one-time full load is a bounded, well-understood operation that connectors handle cleanly. The hard part is everything that has to keep being true afterward — ongoing sync, correctness, access control, and delivery to users — which is where most of the effort and risk actually live."
---

Someone reasonable looks at a modern data stack and asks a reasonable question: *we
already have connectors that plug into every source — so why does onboarding a new data
source still take weeks?* The connector demo took ninety seconds. Where does the time
go?

Here's the honest answer. A connector moves data from a source to a destination. That
is one step. It does not make the data trustworthy, secure, correct, in-sync, or usable
— and those are the other ten steps. "Just add a connector" quietly collapses an
eleven-step job into the one step that was never the hard part.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
  <!-- Step 1: the connector, lit -->
  <rect x="40" y="20" width="720" height="56" rx="6" fill="#c8472b"/>
  <text x="70" y="54" font-size="20" fill="#f6f3ec" font-weight="700">1</text>
  <text x="104" y="46" font-size="14" fill="#fdfcf9" font-weight="600">Move the data — the connector does this</text>
  <text x="104" y="64" font-size="10.5" fill="#f3d9d1">one-time full load · fast · solved</text>
  <text x="720" y="52" font-size="11" fill="#f3d9d1" text-anchor="end">✓ the click</text>
  <!-- subheading -->
  <text x="400" y="102" font-size="11" fill="#8b857a" text-anchor="middle" letter-spacing="0.5">The other ten steps — the connector touches none of them</text>
  <!-- 10 muted steps, 2 columns x 5 rows -->
  <g font-size="11.5">
    <!-- row1 -->
    <g><rect x="40" y="118" width="350" height="44" rx="5" fill="#f0ece2" stroke="#cabfac"/><circle cx="64" cy="140" r="13" fill="#e0d8c8"/><text x="64" y="144" text-anchor="middle" font-size="11" fill="#8b857a">2</text><text x="88" y="145" fill="#56514a">Understand the data</text></g>
    <g><rect x="410" y="118" width="350" height="44" rx="5" fill="#f0ece2" stroke="#cabfac"/><circle cx="434" cy="140" r="13" fill="#e0d8c8"/><text x="434" y="144" text-anchor="middle" font-size="11" fill="#8b857a">3</text><text x="458" y="145" fill="#56514a">Prepare the source system</text></g>
    <!-- row2 -->
    <g><rect x="40" y="172" width="350" height="44" rx="5" fill="#f0ece2" stroke="#cabfac"/><circle cx="64" cy="194" r="13" fill="#e0d8c8"/><text x="64" y="198" text-anchor="middle" font-size="11" fill="#8b857a">4</text><text x="88" y="199" fill="#56514a">Secure the path</text></g>
    <g><rect x="410" y="172" width="350" height="44" rx="5" fill="#f0ece2" stroke="#cabfac"/><circle cx="434" cy="194" r="13" fill="#e0d8c8"/><text x="434" y="198" text-anchor="middle" font-size="11" fill="#8b857a">5</text><text x="458" y="199" fill="#56514a">Authentication &amp; access</text></g>
    <!-- row3 -->
    <g><rect x="40" y="226" width="350" height="44" rx="5" fill="#f0ece2" stroke="#cabfac"/><circle cx="64" cy="248" r="13" fill="#e0d8c8"/><text x="64" y="252" text-anchor="middle" font-size="11" fill="#8b857a">6</text><text x="88" y="253" fill="#56514a">Keep in sync (CDC)</text></g>
    <g><rect x="410" y="226" width="350" height="44" rx="5" fill="#f0ece2" stroke="#cabfac"/><circle cx="434" cy="248" r="13" fill="#e0d8c8"/><text x="434" y="252" text-anchor="middle" font-size="11" fill="#8b857a">7</text><text x="458" y="253" fill="#56514a">Make it correct</text></g>
    <!-- row4 -->
    <g><rect x="40" y="280" width="350" height="44" rx="5" fill="#f0ece2" stroke="#cabfac"/><circle cx="64" cy="302" r="13" fill="#e0d8c8"/><text x="64" y="306" text-anchor="middle" font-size="11" fill="#8b857a">8</text><text x="88" y="307" fill="#56514a">Orchestrate pipelines</text></g>
    <g><rect x="410" y="280" width="350" height="44" rx="5" fill="#f0ece2" stroke="#cabfac"/><circle cx="434" cy="302" r="13" fill="#e0d8c8"/><text x="434" y="306" text-anchor="middle" font-size="11" fill="#8b857a">9</text><text x="458" y="307" fill="#56514a">Test end to end</text></g>
    <!-- row5 -->
    <g><rect x="40" y="334" width="350" height="44" rx="5" fill="#f0ece2" stroke="#cabfac"/><circle cx="64" cy="356" r="13" fill="#e0d8c8"/><text x="60" y="360" text-anchor="middle" font-size="10" fill="#8b857a">10</text><text x="88" y="361" fill="#56514a">Update the viewing app</text></g>
    <g><rect x="410" y="334" width="350" height="44" rx="5" fill="#f0ece2" stroke="#cabfac"/><circle cx="434" cy="356" r="13" fill="#e0d8c8"/><text x="430" y="360" text-anchor="middle" font-size="10" fill="#8b857a">11</text><text x="458" y="361" fill="#56514a">Document &amp; tune (GenAI)</text></g>
  </g>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#8b857a;margin-top:0.5rem;">The connector is step 1. Steps 2–11 are the actual work of onboarding a data source — and the connector does none of them.</figcaption>
</figure>

## What the connector actually does

Give the connector its due: it copies data from source to destination, and a one-time
full load genuinely works well. Point it at a table, and the rows arrive. That part is
fast, bounded, and mostly solved.

That's it. That's the whole job description. The connector is a very good pump — and a
pump moves water, it doesn't make the water safe to drink.

> Moving the data is the click. Certifying it, securing it, and surfacing it to users
> is the job.

## The other ten steps — the part nobody demos

Everything below is work the connector cannot touch, and it's where the weeks actually
go:

1. **Understand the data.** Which tables matter, and what does each field *mean*? Only
   the source team knows, and getting that knowledge out of their heads is its own
   project. This is the [data-context problem](/essays/what-is-a-data-catalog/) — a copy
   of a table you don't understand is not an asset.
2. **Prepare the source system.** Their production database has to be configured for
   replication in the first place — which means involving the team that owns it, on
   their timeline, with their risk tolerance.
3. **Secure the path.** Network access, credentials, firewalls, approvals. None of it
   is glamorous; all of it is required before a single byte is allowed to move.
4. **Wire authentication and authorization.** Identity and access have to be threaded
   end to end, from the source application all the way to the warehouse — deciding who
   sees what, often *per client*. Get this wrong and you have a breach, not a bug.
5. **Keep the data in sync.** The one-time load was the easy part; staying current is
   [change data capture](/essays/what-is-change-data-capture/), and CDC is where it gets
   hard. If your warehouse has no native upsert, you're building merge logic,
   transaction ordering, and delete handling *per table*, by hand.
6. **Make it correct.** Quality rules, validation, reconciliation. In a client-facing
   system, a wrong number isn't a nuisance — it's an incident. As I've
   [argued elsewhere](/essays/data-quality-problems-are-org-chart-problems/), correctness
   is mostly an ownership problem, and the connector owns none of it.
7. **Plumb and schedule every pipeline.** Orchestration, dependencies, retries,
   alerting — wired end to end so the thing runs unattended and tells you when it
   breaks. And it has to break safely, which means the pipeline has to be
   [idempotent](/essays/how-to-make-a-data-pipeline-idempotent/).
8. **Test end to end.** Data accuracy, failure scenarios, reconciliation, performance —
   all validated *before* any client sees it. Testing data systems is harder than
   testing code, because the data itself is a moving input.
9. **Change the viewing application.** The self-service portal or BI layer has to be
   updated so users can actually *see* the new data. Data nobody can reach delivers no
   value, however clean it is.
10. **Document and tune for how it's consumed.** Data dictionaries so fields are
    understood, and — increasingly — prompt engineering for GenAI interfaces, tuned per
    domain, because a direct-tax query and an indirect-tax query are not the same
    question. This is the [semantic and meaning layer](/essays/what-is-a-semantic-layer/)
    that turns raw columns into answers.

## Why the misconception is so sticky

The connector is the *visible* step. It has a UI, a progress bar, a satisfying "done."
The other ten are invisible until they fail — you don't see access control until
someone sees data they shouldn't, you don't see reconciliation until a client's number
is wrong. So the mental model forms around the one step you can watch, and the ten you
can't get compressed into "and then some engineering stuff."

This is the same illusion behind "[the modern data stack will fix
it](/essays/is-the-modern-data-stack-dead/)" — buying the tool that does the easy,
visible 10% and assuming the hard, invisible 90% comes along for free. It doesn't. The
tools got very good at the part that was already tractable, and left the genuinely hard
parts exactly where they were: with the engineers who have to understand the data,
secure it, keep it correct, and deliver it.

<figure style="margin:2.5rem auto;text-align:center;">
<img src="/assets/connectors-11-steps.png" alt="Slide breaking down data source onboarding into 11 steps: one step (moving data) done by the connector, and ten steps — understanding, securing, authenticating, syncing, validating, orchestrating, testing, updating the app, and documenting — done by engineers." style="max-width:100%;height:auto;border:1px solid #ddd6c8;border-radius:6px;"/>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#8b857a;margin-top:0.5rem;">The original slide this essay grew out of — the connector lit up as one step against the ten it can't do.</figcaption>
</figure>

## What to do with this

Two things follow, and they're worth saying plainly to whoever is asking why it takes so
long.

First, **scope onboarding as the eleven-step job it is, not the one-step job the demo
implied.** When someone requests a new source, the estimate should account for
understanding, securing, syncing, validating, and surfacing it — not just connecting it.
Setting that expectation up front is the difference between "why is this taking weeks?"
and "of course this takes weeks."

Second, **value the pump for what it is and no more.** Connectors are genuinely useful;
they removed a real chunk of undifferentiated work. But they moved the bottleneck, they
didn't remove it. The work that remains — trust, security, correctness, delivery — is
the work that was always the point. The connector clicks. The engineering is the job.
