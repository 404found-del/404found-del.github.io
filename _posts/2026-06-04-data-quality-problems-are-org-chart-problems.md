---
title: "Most Data Quality Problems Are Org-Chart Problems"
kicker: "Essay"
topic: "Governance"
description: "When data is wrong, teams buy a data-quality tool. But the durable causes are organizational — unclear ownership, misaligned incentives, no accountability — and no tool can fix an org-chart problem."
date: 2026-06-04
---

Here is the usual sequence. A dashboard shows a wrong number. It happens again. After
enough fire drills, someone proposes buying a data-quality or observability tool. The
tool gets bought, dashboards of freshness checks and anomaly alerts appear, everyone
feels better for a quarter — and then the data is mysteriously still wrong. The reason
this keeps happening is that most data-quality problems aren't technical problems with
technical fixes. They're organizational problems wearing a technical costume, and you
cannot buy your way out of an org chart.

## The tool detects symptoms, not causes

A monitoring tool is genuinely useful at one thing: telling you *that* a number
broke, and when. What it cannot tell you is *whose job it was to prevent it*, or give
that person any reason to care. It surfaces the symptom and hands it back to an
organization that has no clear answer for who should respond.

> An observability tool without an owner is just a louder alarm that nobody is
> responsible for silencing. The alert fires, lands in a shared channel, and dies
> there — because "everyone's problem" has always meant "no one's problem."

So before reaching for tooling, it's worth looking at the three organizational causes
underneath nearly every persistent data-quality failure. None of them are fixed by
software.

## Cause one: nobody owns the data

The single most common root cause. A dataset is produced by a team that considers it
exhaust — a byproduct of running their service — and consumed by people they've never
met. No one is accountable for its shape or correctness. It becomes one of the
[orphaned tables that turn a warehouse into a museum](/essays/the-shape-of-data/): a
fossil everyone queries and no one maintains.

You can monitor an unowned table forever. The monitor will dutifully report that it's
broken, and it will stay broken, because detection was never the missing piece —
*ownership* was. A dataset with a name attached to it, a team genuinely responsible
for it, gets fixed. One without doesn't, no matter how good your alerting is.

## Cause two: incentives point the wrong way

Even where ownership nominally exists, quality dies when incentives are misaligned —
and they usually are. The team that *produces* the data is measured on shipping
features, not on the quality of the data their service emits. The team that *suffers*
from bad data has every incentive to fix it but no authority to, because they don't
control the source.

This is the same fault line that runs under [why data contracts are a cultural
problem](/essays/data-contracts-are-a-cultural-problem/): a promise with no
consequence for breaking it is just a suggestion, and a producer who feels no cost
when they break downstream data will, predictably, keep breaking it. Quality follows
incentives. If no one upstream is rewarded for it or feels the pain of neglecting it,
no tool will conjure it into being.

## Cause three: meaning is nobody's job

The third cause is quieter. "Active user" gets defined three different ways because
defining it *once, authoritatively* was never anyone's explicit responsibility. The
result isn't data that's broken so much as data that's ambiguous — technically
correct numbers that disagree because they answer subtly different questions no one
ever reconciled. This is the gap a [semantic layer](/essays/what-is-a-semantic-layer/)
fills, but the layer only works if someone is accountable for the definitions in it.
Unowned meaning drifts exactly the way unowned data rots.

## What actually fixes it

The fixes are organizational, and they're unglamorous precisely because they're about
people and accountability rather than purchases:

- **Assign real ownership.** Every important dataset gets a team whose name is on it,
  with the authority and the responsibility to keep it right.
- **Align the incentives.** Make producers accountable for the data they emit —
  contracts with actual teeth, quality tied to objectives the producing team cares
  about, breakage that costs *them*, not just the downstream consumer.
- **Make meaning someone's job.** One governed place for definitions, and one owner
  responsible for it.

Do these, and a data-quality tool becomes genuinely valuable — because now its alerts
land on a named owner who is accountable and incentivized to act. Skip these, and the
tool is theatre: an expensive way to watch your data break in real time.

## The amplifier makes it urgent

This was always true, but it used to fail slowly enough to ignore. Now that AI systems
consume data directly, ungoverned quality fails *fluently and at scale* — [a model
reports bad data with total confidence](/essays/your-ai-is-only-as-good-as-your-data-architecture/),
with none of the human skepticism that used to catch it. The org-chart problems you
could once paper over are about to be amplified into confident, automated wrongness.

So the next time the data is wrong and someone reaches for a tool, ask the harder
question first: *who owns this, what are they measured on, and who decides what it
means?* If you don't have clean answers, the tool won't save you — and if you do, you
may find you needed far less tooling than you thought. Data quality isn't a product
you buy. It's an outcome of how you're organized.
