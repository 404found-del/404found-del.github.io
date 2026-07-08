---
title: "Data Observability vs Data Quality: What Each One Actually Catches"
kicker: "Field Notes"
topic: "Governance"
description: "Data quality checks the rules you wrote; data observability watches for the failures you didn't anticipate. Neither replaces the other — here's the honest split."
date: 2026-07-08 20:00:00 +0530
faq:
  - q: "What's the difference between data observability and data quality?"
    a: "Data quality is explicit rules you write about the data itself — this column is never null, amounts are positive, keys are unique. Data observability is automated monitoring of data health signals — freshness, volume, schema, distribution — that learns baselines from history and alerts on anomalies. Quality catches violations you anticipated; observability catches the incidents you didn't."
  - q: "Do I need both data quality checks and observability?"
    a: "At any real scale, yes — they fail differently. Quality rules are precise but only cover what someone thought to write. Observability covers everything but only notices deviation from history, so it misses data that has always been quietly wrong. One is a spec, the other is a smoke detector."
  - q: "Which should a small team start with?"
    a: "Quality checks first — a handful of tests on your most-consumed tables (nulls, uniqueness, freshness) is an afternoon's work in dbt and catches the majority of embarrassing incidents. Add observability when your table count outgrows what anyone can write rules for, which is when unanticipated failures start dominating."
  - q: "Is data observability just monitoring rebranded?"
    a: "It borrows the idea from software observability, but the signals differ: instead of latency and error rates, it watches freshness, row volume, schema changes, and value distributions — and uses lineage to trace an anomaly to its upstream cause and downstream blast radius. The rebrand is real, but so is the discipline."
---

The confusion is understandable, because every vendor selling one now claims to
do both. The clean split: **data quality** is the rules you write about the
data — *this column is never null, revenue is never negative, one row per order
line*. **Data observability** is machinery that watches the data's vital signs —
freshness, volume, schema, distribution — learns what normal looks like from
history, and alerts when something drifts. Quality is a spec: it catches
violations you anticipated. Observability is a smoke detector: it catches the
fires you didn't. Neither replaces the other, because they fail in opposite
ways.

## The comparison, honestly

| | Data quality | Data observability |
|---|---|---|
| **What it is** | Explicit assertions about data | Anomaly detection on health signals |
| **Written by** | Humans who know the business rule | Learned baselines from history |
| **Catches** | Known failure modes, precisely | Unknown failure modes, approximately |
| **Misses** | Everything nobody wrote a rule for | Data that was always quietly wrong |
| **Coverage** | Deep on chosen tables | Broad across the whole warehouse |
| **When it runs** | In the pipeline, blocking or flagging | Continuously, after the fact |
| **Typical tools** | dbt tests, Great Expectations | Monte Carlo, Bigeye, Elementary |
| **Failure smell** | "The test passed but the number's wrong" | "Alert fatigue — everything drifts a little" |

## What each looks like in practice

A quality check is an assertion, and the best ones read like business rules:

```sql
-- Quality: explicit rules — fail the pipeline if violated
SELECT order_id
FROM fact_order_line
GROUP BY order_id, product_key
HAVING count(*) > 1;              -- grain violation: dupes at declared grain

SELECT count(*) AS bad_rows
FROM fact_order_line
WHERE line_amount < 0
   OR customer_key IS NULL;       -- rule violations someone wrote down
```

Observability asks a different question — not "is this rule true?" but "does
today look like history?":

```sql
-- Observability signal: is today's volume anomalous vs the last 28 days?
SELECT
  count(*) AS rows_today,
  avg(count(*)) OVER w AS baseline,
  count(*) / nullif(avg(count(*)) OVER w, 0) AS ratio  -- alert if far from 1.0
FROM fact_order_line
WHERE order_ts >= current_date
WINDOW w AS (ORDER BY 1 ROWS BETWEEN 28 PRECEDING AND 1 PRECEDING);
```

Real observability platforms automate thousands of these across every table —
freshness, volume, schema, distributions — and use
[lineage](/essays/what-is-data-lineage/) to do the two things a lone alert
can't: trace the anomaly upstream to its cause, and enumerate the dashboards
and models downstream in its blast radius.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;">
  <rect x="60" y="40" width="320" height="200" rx="8" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="220" y="72" font-size="14" fill="#1c1a17" text-anchor="middle" font-weight="700">Data quality</text>
  <text x="220" y="100" font-size="12" fill="#56514a" text-anchor="middle">rules you wrote</text>
  <rect x="90" y="120" width="260" height="34" rx="4" fill="#1c1a17"/>
  <text x="220" y="142" font-size="11" fill="#f6f3ec" text-anchor="middle">catches: anticipated failures</text>
  <rect x="90" y="164" width="260" height="34" rx="4" fill="#f6f3ec" stroke="#c8472b" stroke-width="1.5"/>
  <text x="220" y="186" font-size="11" fill="#a4391f" text-anchor="middle">misses: what nobody thought of</text>
  <rect x="420" y="40" width="320" height="200" rx="8" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="580" y="72" font-size="14" fill="#1c1a17" text-anchor="middle" font-weight="700">Data observability</text>
  <text x="580" y="100" font-size="12" fill="#56514a" text-anchor="middle">baselines learned from history</text>
  <rect x="450" y="120" width="260" height="34" rx="4" fill="#1c1a17"/>
  <text x="580" y="142" font-size="11" fill="#f6f3ec" text-anchor="middle">catches: unanticipated drift</text>
  <rect x="450" y="164" width="260" height="34" rx="4" fill="#f6f3ec" stroke="#c8472b" stroke-width="1.5"/>
  <text x="580" y="186" font-size="11" fill="#a4391f" text-anchor="middle">misses: always-been-wrong data</text>
  <text x="400" y="275" font-size="12" fill="#8b857a" text-anchor="middle">each one's blind spot is the other one's job — that's why "vs" is the wrong word</text>
</svg>
</figure>

## The part the vendors won't say

Neither discipline fixes the thing that actually produces bad data. A failed
test and a fired alert both end at a human question: *who owns this table, and
who's accountable for the fix?* If the answer is "nobody," quality checks
become warnings everyone ignores and observability becomes alert fatigue with a
dashboard. Detection is a tooling problem;
[data quality is an org-chart problem](/essays/data-quality-problems-are-org-chart-problems/),
and the durable fix is ownership — usually formalised as
[data contracts](/essays/data-contracts-are-a-cultural-problem/), with checks
and monitors as the enforcement layer.

So: start with a dozen quality rules on the tables people actually consume. Add
observability when your estate outgrows what anyone can write rules for. And
spend the money you saved on tooling on the unglamorous part — making ownership
real.
