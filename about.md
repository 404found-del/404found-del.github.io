---
layout: page
title: "About this studio"
kicker: "Colophon"
permalink: /about/
seo:
  type: "AboutPage"
description: "What dataarchitect.studio covers, who writes it, how the essays are made, and the editorial standards behind them."
---

This is a working notebook on **data architecture** — the discipline of deciding
how information is shaped, stored, moved, and trusted inside an organisation.

## Who writes this

A practicing data architect, writing here under the studio's name rather than a
personal one. The subjects covered are ones I work in: operational databases,
enterprise warehouses, dimensional models, and cloud and lakehouse migrations.

Publishing anonymously has an obvious cost, and it's worth naming rather than
glossing over: you can't check my record, so nothing here should be taken on
authority. Read it as an argument to be tested, not a credential to be trusted.
What I can offer instead is that the reasoning is shown rather than asserted, the
comparisons commit to a recommendation you can disagree with, and errors get
corrected in public. Judge the essays on whether they hold up.

## What you'll find here

Essays and field notes, roughly in three registers:

- **Manifestos** — opinionated arguments about how data work *should* be done.
- **Field notes** — practical, evergreen explainers on modeling, pipelines, and design patterns.
- **Reconsiderations** — second looks at popular architectures, including where they quietly fail.

Around the essays sit three reference sections:
[Start here](/start-here/) sequences the essays into reading paths, the
[patterns catalog](/patterns/) documents the major architectures with honest
trade-offs, and the [glossary](/glossary/) defines the vocabulary a paragraph at
a time.

I write for practitioners. The goal is not to be comprehensive but to be *useful*
— to leave you with a sharper mental model than you arrived with.

## How the essays are made

Worked SQL and configuration examples are written to run, not to illustrate —
if a snippet here would throw against a real engine, that's a bug and I want to
know about it. Where a claim depends on a specification or a release, the essay
links to the primary source rather than paraphrasing it. Comparison pieces state
a recommendation instead of hiding behind "it depends," and state the trade-offs
that would reverse it. When a subject changes materially — a spec version, a
market shift — the essay is updated in place and its modification date is set
honestly.

What you won't find here is a case study: these essays argue from how the
mechanisms work, not from a war story I can't corroborate under a pseudonym.
Where a piece walks through a scenario with numbers, it says plainly that the
scenario is constructed.

Spotted an error? Open an issue on
[GitHub](https://github.com/404found-del/404found-del.github.io/issues) — corrections are taken seriously and
made visibly.

## The premise

Most data problems are not technology problems. They are problems of **structure
and agreement**: someone defined "active user" three different ways, no one owns
the orders table, and the warehouse has quietly become a museum of every decision
nobody wanted to make. Good architecture is mostly the courage to make those
decisions explicit, and the discipline to keep them that way.

That's the thread running through everything here.

---

*Built with Jekyll, hosted on GitHub Pages, and set in Fraunces, Newsreader, and
IBM Plex Mono. The source lives on
[GitHub](https://github.com/404found-del/404found-del.github.io).*
