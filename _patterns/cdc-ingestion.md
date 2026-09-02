---
last_modified_at: 2026-07-18
title: "Change Data Capture Ingestion"
intent: "Replicate operational data by streaming the database's own change log, instead of repeatedly querying tables for what's new."
description: "The CDC ingestion pattern: log-based capture, ordered change streams, merging into analytical tables, trade-offs against batch extracts, and when polling is fine."
essays:
  - what-is-change-data-capture
  - batch-vs-streaming
  - how-to-make-a-data-pipeline-idempotent
terms:
  - change-data-capture
  - idempotent-pipeline
  - etl
  - elt
faq:
  - q: "What is change data capture in simple terms?"
    a: "Instead of repeatedly querying a database for what changed, CDC reads the transaction log the database already writes. Every insert, update, and delete comes out complete, in order, including deletes — with almost no load on the source system."
  - q: "What is log-based CDC?"
    a: "The standard modern implementation: a reader (such as Debezium) tails the database's write-ahead log and emits each change as an event into a durable stream, which a sink job then merges into the analytical copy. It contrasts with query-based CDC, which polls tables and misses deletes."
  - q: "When is CDC overkill?"
    a: "Small tables, daily-batch freshness needs, soft-delete-only sources, or databases you can't get log access to. A scheduled incremental extract is simpler to run and honestly sufficient there. CDC earns its operational machinery when deletes, freshness, or source load genuinely matter."
---

## Intent

Get every insert, update, and delete out of an operational database — reliably,
in order, with low latency and near-zero load on the source — by reading the
transaction log the database already writes, rather than querying tables with
`WHERE updated_at > ?`.

## Context

Analytical systems need fresh copies of operational tables. Query-based extracts
miss hard deletes, hammer the source, lose intermediate states, and depend on
trustworthy timestamp columns. The database's write-ahead log has none of these
problems — it *is* the ground truth of what changed.

## Structure

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 220" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="cdc-ingestion-t cdc-ingestion-d">
  <title id="cdc-ingestion-t">Change data capture ingestion pattern</title>
  <desc id="cdc-ingestion-d">An OLTP database's transaction log is read by a CDC reader such as Debezium, producing an ordered, replayable change stream, which is merged into a lakehouse table. The log is ground truth: every change, in order, including deletes.</desc>
  <rect x="30" y="70" width="160" height="80" rx="6" fill="#1c1a17"/>
  <text x="110" y="105" font-size="13" fill="#f6f3ec" text-anchor="middle">OLTP database</text>
  <text x="110" y="126" font-size="11" fill="#f6f3ec" text-anchor="middle">transaction log</text>
  <line x1="190" y1="110" x2="240" y2="110" stroke="#cabfac" stroke-width="2"/>
  <rect x="240" y="70" width="160" height="80" rx="6" fill="#c8472b"/>
  <text x="320" y="105" font-size="13" fill="#f6f3ec" text-anchor="middle" font-weight="700">CDC reader</text>
  <text x="320" y="126" font-size="11" fill="#f6f3ec" text-anchor="middle">e.g. Debezium</text>
  <line x1="400" y1="110" x2="450" y2="110" stroke="#cabfac" stroke-width="2"/>
  <rect x="450" y="70" width="160" height="80" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="530" y="105" font-size="13" fill="#1c1a17" text-anchor="middle">change stream</text>
  <text x="530" y="126" font-size="11" fill="#56514a" text-anchor="middle">ordered, replayable</text>
  <line x1="610" y1="110" x2="660" y2="110" stroke="#cabfac" stroke-width="2"/>
  <rect x="660" y="70" width="120" height="80" rx="6" fill="#f6f3ec" stroke="#1c1a17" stroke-width="1.5"/>
  <text x="720" y="105" font-size="13" fill="#1c1a17" text-anchor="middle">MERGE into</text>
  <text x="720" y="126" font-size="11" fill="#56514a" text-anchor="middle">lakehouse table</text>
  <text x="400" y="196" font-size="12" fill="#8b857a" text-anchor="middle">the log is ground truth: every change, in order, including deletes</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">The transaction log is ground truth: every change, in order, including the deletes a polling query would miss.</figcaption>
</figure>

A log reader emits each change as an ordered event into a durable stream; a sink
job applies them to the analytical copy with an idempotent `MERGE`. Replaying
the stream rebuilds the target —
[idempotency](/essays/how-to-make-a-data-pipeline-idempotent/) is what makes the
pattern safe to operate.

## Trade-offs

**Gains:** deletes and every intermediate state captured; minutes-level
freshness; negligible source load; one mechanism for both
[streaming and batch consumers](/essays/batch-vs-streaming/).

**Costs:** operational machinery (connectors, offsets, schema-change handling,
snapshot bootstrapping) that must be monitored; database-specific quirks; and
initial-load complexity. The capture is the easy half —
[the other ten steps](/essays/what-is-change-data-capture/) of making the data
trustworthy still apply.

## When not to use it

Small tables, daily-batch freshness requirements, soft-delete-only sources, or
sources you can't get log access to: a scheduled full or incremental extract is
simpler and honestly sufficient. CDC earns its machinery when deletes matter,
freshness matters, or source load matters.
