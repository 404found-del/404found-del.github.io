---
layout: page
title: "About this studio"
kicker: "Colophon"
permalink: /about/
description: "What dataarchitect.studio covers, who writes it, how the essays are made, and the editorial standards behind them."
---

This is a working notebook on **data architecture** — the discipline of deciding
how information is shaped, stored, moved, and trusted inside an organisation.

## Who writes this

A practicing data architect, writing here under the studio's name rather than a
personal one. The short version of the credentials: close to two decades of
hands-on work in data — operational databases, enterprise warehouses, dimensional
models that survived contact with real organisations, and the cloud and lakehouse
migrations that followed. The essays are written from the scar tissue of that
work, not from vendor decks.

The site publishes as *dataarchitect.studio* deliberately. Arguments should stand
on their reasoning and their accuracy, not on a byline — and the writing stays
more honest when it can describe failure modes candidly, including the author's
own.

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

Every technical claim is one the author has either implemented, broken, or
audited. Worked SQL examples are real patterns, not pseudocode. Comparison pieces
state a recommendation rather than hiding behind "it depends" — and state the
trade-offs that would reverse it. When an essay's subject changes materially (a
spec version, a market shift), the essay is updated in place and its modification
date is set honestly.

Spotted an error? Open an issue on
[GitHub](https://github.com/404found-del) — corrections are taken seriously and
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
IBM Plex Mono. The source lives on [GitHub](https://github.com/404found-del).*
