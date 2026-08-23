---
title: "What Are Conformed Dimensions, and Why Do They Matter?"
kicker: "Field Notes"
topic: "Modeling"
description: "A conformed dimension is one dimension shared identically across several fact tables, so different business processes can be compared on the same terms."
date: 2026-05-21
last_modified_at: 2026-08-23
faq:
  - q: "What is a conformed dimension?"
    a: "A conformed dimension is a dimension table used identically across multiple fact tables or data marts — the same surrogate keys, the same attribute names, the same attribute values. Because every process references the same customer or date dimension, metrics from different processes can be compared and combined consistently. Kimball's formal test is that conforming dimensions are either identical, or one is a strict subset of the other in both rows and columns."
  - q: "Why use a conformed dimension rather than duplicating the attribute in each dimension?"
    a: "Because duplication gives you consistency only for as long as nobody edits one copy. If sales and support each carry their own `segment` column, the two definitions drift the first time one team reclassifies an account, and nothing in the schema detects it — the queries keep running and quietly return different answers. A conformed dimension makes consistency structural: there is one row for that customer, one segment value, and no second copy that can disagree with it."
  - q: "Are conformed dimensions a way of joining two fact tables together?"
    a: "No, and this is the most common misunderstanding of the technique. You should not join two fact tables directly — the join fans out and multiplies rows, inflating both measures. What conformed dimensions enable is drilling across: query each fact table separately, aggregate each result to the same conformed dimension attributes, then sort-merge the two answer sets on those shared attributes. The dimension is the alignment key between two result sets, not a join path between two fact tables."
  - q: "Do conformed dimensions have to be completely identical?"
    a: "No. Kimball allows a second, weaker form: a shrunken rollup dimension, which is a strict subset of a base dimension's rows or columns at a coarser grain. A Month dimension conformed to Date, or Brand conformed to Product, lets a monthly forecast fact table conform with a daily sales fact table. The subset must be strict — the same values, just fewer of them. A dimension that adds or redefines an attribute is not conformed, it is a fork."
  - q: "What is a conformed fact?"
    a: "The measure-side counterpart to a conformed dimension. If the same measurement appears in more than one fact table, its technical definition must be identical for the two to be compared or added. Kimball's rule is that consistent facts should carry identical names, and incompatible facts should be deliberately given different names so that users and BI tools are alerted rather than silently combining them. Naming two differently-defined measures `revenue` is how drill-across produces confident nonsense."
  - q: "What is the difference between a conformed dimension and the bus matrix?"
    a: "A conformed dimension is the shared table itself. The bus matrix is the planning grid that maps which business processes (fact tables) use which conformed dimensions — a blueprint for building marts incrementally while keeping them integrated. The matrix is how you decide what to conform; the dimension is the thing you conform."
  - q: "How is a conformed dimension different from a role-playing or multi-valued dimension?"
    a: "They answer different questions and can all be true of one table. Conformance is about sharing across fact tables. Role-playing is about one dimension joined several times to a single fact table under different aliases, such as order date and ship date both pointing at `dim_date`. Multi-valued is about a dimension where one fact row legitimately has several dimension members, resolved with a bridge table. A conformed date dimension is very often also role-playing."
---

[Dimensional modeling](/essays/a-field-guide-to-dimensional-modeling/) is usually
taught one star at a time — a [fact table](/glossary/fact-table/), its dimensions, done. But real
organizations have *many* business processes, each with its own fact table: sales,
shipping, support tickets, web sessions. The question that decides whether those
separate stars add up to a coherent warehouse or a pile of disconnected silos is
this: do they **share their dimensions?** A dimension shared identically across many
fact tables is a *conformed dimension*, and conformity is the single most important
idea for making a multi-process warehouse hang together.

## The definition

A conformed dimension is a [dimension table](/glossary/dimension-table/) that is used **identically** across
multiple fact tables — the same [surrogate keys](/glossary/surrogate-key/), the same attributes, the same
meanings. There is one `dim_customer`, one `dim_product`, one
[`dim_date`](/essays/date-dimension-table/), and *every* fact table that needs
customer, product, or date points at that same shared table.

The opposite — each business process building its own private customer dimension, with
its own keys and its own slightly different definition of "segment" — is how you end up
with the [three-different-numbers problem](/essays/what-is-a-semantic-layer/) baked
into the warehouse's very structure.

Kimball's test for whether two dimensions actually conform is stricter than "they look
similar." Two dimensions conform when they are
[identical, or when one is a strict subset](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/conformed-dimension/)
of the other in both rows and columns: same column names, same domain of values. That
word *strict* is carrying weight. A dimension that keeps the shared attributes and drops
some rows still conforms. A dimension that keeps the shared attributes and adds a locally
redefined `segment` does not conform, no matter how much of it matches.

The surrogate key is part of that test and is the piece most often gotten wrong. If
`dim_customer` in the sales mart assigns customer 4471 a different surrogate key than
`dim_customer` in the support mart, the two dimensions are not conformed even if every
attribute is byte-identical, because nothing lines up when you try to use them together.
Conformity is a property of keys and values together, not of column lists.

### Why not just copy the attribute into each dimension?

This is the honest alternative, and it is worth saying why it fails rather than just
asserting that it does. Copying `segment` into every mart's private customer dimension
gives you identical values on day one. It gives you nothing at all on day two, because
the copies can now diverge and no mechanism exists to notice. The day someone reclassifies
a set of accounts from Mid-Market to Enterprise in the sales mart's dimension, every query
against the support mart keeps running, keeps returning numbers, and is now wrong in a way
that no test fails on.

A conformed dimension removes the possibility rather than managing it. There is one row
for that customer and one segment value, so there is no second copy available to disagree.
That is a structural guarantee rather than a process guarantee, and structural guarantees
are the only kind that survive staff turnover.

## Why conformity is the whole game

Here's what sharing a dimension actually buys you, and why Kimball treated it as the
cornerstone of enterprise dimensional modeling.

**You can compare processes on the same terms.** If sales and support both reference
the *same* `dim_customer`, you can ask "do customers in the Enterprise segment file
more support tickets?" — joining a sales fact and a support fact through the shared
customer dimension and trusting that "Enterprise" means the same thing on both sides.
The instant each process has its own customer dimension, that question becomes
unanswerable: you'd be comparing two different definitions of customer and segment.

> Conformed dimensions are what turn a collection of separate stars into a single
> warehouse. Without them you don't have a warehouse — you have several small ones
> that happen to share a database and can't be compared.

**Consistency by construction.** "Revenue by region" and "tickets by region" use the
*same* region attribute from the *same* dimension, so they're automatically
comparable and consistent. The conformity isn't enforced by a downstream tool; it's
built into the model.

**Drilling across becomes possible.** Querying multiple fact tables and lining their
results up by a shared dimension — "monthly sales *and* monthly support volume by
product" — is called drilling across, and it only works because the dimensions conform.
It is also the step people most often implement incorrectly, so it gets its own section.

## Drilling across is not a fact-to-fact join

A question that shows up constantly, phrased more or less this way: *are conformed
dimensions a way of joining two fact tables together?*

No. And the reason matters, because the wrong implementation does not fail loudly. It
returns numbers.

If you join `fact_sales` to `fact_support_tickets` on `customer_key`, you get a Cartesian
product within each customer. A customer with 8 orders and 5 tickets produces 40 rows.
Sum revenue across those rows and you get 5× the real figure; sum ticket counts and you
get 8× the real figure. Both totals are wrong, both are wrong by a *different* multiplier,
and the query completes in a second with no error. This fan-out trap is the same one that
makes [fact table grain](/essays/fact-table-grain/) worth being pedantic about.

[Drilling across](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/drilling-across/)
is a three-step operation instead:

1. Query each fact table **separately**, aggregating each to the same conformed dimension
   attributes as row headers — say `product_name` and `month`.
2. Each query now returns one row per attribute combination. The fan-out cannot happen,
   because each fact table has already been collapsed to the shared grain.
3. **Sort-merge** the two answer sets on those shared row headers, joining result to
   result rather than fact to fact.

```sql
-- Correct: aggregate first, then align. One row per product per month on each side.
with sales as (
  select p.product_name, d.month_key, sum(f.extended_amount) as revenue
  from fact_sales f
  join dim_product p on p.product_key = f.product_key
  join dim_date    d on d.date_key    = f.date_key
  group by 1, 2
),
tickets as (
  select p.product_name, d.month_key, count(*) as ticket_count
  from fact_support_tickets f
  join dim_product p on p.product_key = f.product_key   -- same conformed dimension
  join dim_date    d on d.date_key    = f.date_key      -- same conformed dimension
  group by 1, 2
)
select coalesce(s.product_name, t.product_name) as product_name,
       coalesce(s.month_key,    t.month_key)    as month_key,
       s.revenue, t.ticket_count
from sales s
full outer join tickets t
  on s.product_name = t.product_name and s.month_key = t.month_key;
```

The full outer join is deliberate: a product with tickets and no sales that month is a
real and interesting row, and an inner join would silently drop it.

The conformed dimension's job here is to guarantee that `product_name` and `month_key`
mean the same thing on both sides, so that the merge in the final step is meaningful. It
is the alignment key between two result sets. It is not a join path between two fact
tables, and treating it as one is how a warehouse produces its most confident wrong
answers.

<figure style="margin:2rem auto;text-align:center;">
<svg viewBox="0 0 800 330" xmlns="http://www.w3.org/2000/svg" style="max-width:100%;height:auto;font-family:'IBM Plex Mono',ui-monospace,monospace;" role="img" aria-labelledby="cd-t cd-d">
  <title id="cd-t">Fact-to-fact join versus drilling across a conformed dimension</title>
  <desc id="cd-d">Two panels. On the left, joining a sales fact table with eight order rows directly to a support fact table with five ticket rows on customer key produces forty rows, inflating revenue five times and ticket count eight times, with no error raised. On the right, each fact table is aggregated separately to the shared conformed attributes of product name and month, producing one row per combination on each side, and the two small result sets are then sort-merged on those shared attributes to give correct figures.</desc>
  <text x="20" y="22" font-size="12" fill="#1c1a17" font-weight="700">Wrong: join fact to fact</text>
  <rect x="20" y="38" width="150" height="46" rx="3" fill="none" stroke="#cabfac" stroke-width="1.5"/>
  <text x="95" y="58" font-size="11" fill="#1c1a17" text-anchor="middle">fact_sales</text>
  <text x="95" y="74" font-size="10" fill="#8b857a" text-anchor="middle">8 order rows</text>
  <rect x="200" y="38" width="150" height="46" rx="3" fill="none" stroke="#cabfac" stroke-width="1.5"/>
  <text x="275" y="58" font-size="11" fill="#1c1a17" text-anchor="middle">fact_tickets</text>
  <text x="275" y="74" font-size="10" fill="#8b857a" text-anchor="middle">5 ticket rows</text>
  <line x1="170" y1="61" x2="200" y2="61" stroke="#c8472b" stroke-width="1.5"/>
  <text x="185" y="105" font-size="10" fill="#8b857a" text-anchor="middle">join on customer_key</text>
  <rect x="20" y="120" width="330" height="44" rx="3" fill="#f2e4de" stroke="#c8472b" stroke-width="1.5"/>
  <text x="185" y="140" font-size="11" fill="#a4391f" text-anchor="middle" font-weight="700">40 rows (8 × 5)</text>
  <text x="185" y="156" font-size="10" fill="#a4391f" text-anchor="middle">revenue 5× too high, tickets 8× too high</text>
  <text x="185" y="186" font-size="10" fill="#8b857a" text-anchor="middle">no error is raised</text>
  <line x1="390" y1="20" x2="390" y2="310" stroke="#ddd6c8" stroke-width="1"/>
  <text x="430" y="22" font-size="12" fill="#1c1a17" font-weight="700">Right: drill across</text>
  <rect x="430" y="38" width="150" height="46" rx="3" fill="none" stroke="#cabfac" stroke-width="1.5"/>
  <text x="505" y="58" font-size="11" fill="#1c1a17" text-anchor="middle">fact_sales</text>
  <text x="505" y="74" font-size="10" fill="#8b857a" text-anchor="middle">group by product, month</text>
  <rect x="610" y="38" width="150" height="46" rx="3" fill="none" stroke="#cabfac" stroke-width="1.5"/>
  <text x="685" y="58" font-size="11" fill="#1c1a17" text-anchor="middle">fact_tickets</text>
  <text x="685" y="74" font-size="10" fill="#8b857a" text-anchor="middle">group by product, month</text>
  <text x="595" y="104" font-size="10" fill="#8b857a" text-anchor="middle">aggregate each side first, separately</text>
  <rect x="430" y="118" width="150" height="34" rx="3" fill="#eae3d5" stroke="#cabfac" stroke-width="1.5"/>
  <text x="505" y="139" font-size="10" fill="#1c1a17" text-anchor="middle">1 row per product/month</text>
  <rect x="610" y="118" width="150" height="34" rx="3" fill="#eae3d5" stroke="#cabfac" stroke-width="1.5"/>
  <text x="685" y="139" font-size="10" fill="#1c1a17" text-anchor="middle">1 row per product/month</text>
  <line x1="580" y1="135" x2="610" y2="135" stroke="#c8472b" stroke-width="1.5"/>
  <text x="595" y="176" font-size="10" fill="#8b857a" text-anchor="middle">sort-merge on the conformed attributes</text>
  <rect x="430" y="190" width="330" height="44" rx="3" fill="#e6efe6" stroke="#4a7a4a" stroke-width="1.5"/>
  <text x="595" y="210" font-size="11" fill="#2f5c2f" text-anchor="middle" font-weight="700">correct revenue and correct ticket count</text>
  <text x="595" y="226" font-size="10" fill="#2f5c2f" text-anchor="middle">result joined to result, not fact to fact</text>
  <line x1="20" y1="262" x2="780" y2="262" stroke="#ddd6c8" stroke-width="1"/>
  <text x="20" y="286" font-size="11" fill="#1c1a17" font-weight="700">The conformed dimension is the alignment key between two result sets.</text>
  <text x="20" y="306" font-size="11" fill="#8b857a">It is not a join path between two fact tables.</text>
</svg>
<figcaption style="font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8b857a;margin-top:0.6rem;">The fan-out on the left completes without error. That is what makes it dangerous.</figcaption>
</figure>

## Two degrees of conformity

"Identical" is the strong form, and it is not the only one Kimball permits. There is a
second, weaker form that exists because business processes genuinely operate at different
grains: a
[shrunken rollup dimension](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/shrunken-rollup-dimension/),
a strict subset of a base dimension's rows or columns at a coarser grain.

| | Identical conformance | Shrunken rollup conformance |
|---|---|---|
| **What it is** | The same dimension table, shared | A strict subset at a coarser grain |
| **Example** | `dim_customer` used by sales and support | `dim_month` rolled up from `dim_date` |
| **Why you need it** | Processes share the same grain | Forecast is monthly; sales is daily |
| **The rule** | Same keys, attributes, values | Same values, fewer of them |
| **Breaks when** | One mart adds a local attribute | The rollup redefines rather than restricts |

A monthly forecast fact table cannot join `dim_date` at day grain, so it joins `dim_month`
instead. That still conforms, because every month value in the rollup came from the base
date dimension and means exactly what it means there. Drill-across between forecast and
sales works, at month grain.

The failure mode is a rollup that quietly redefines something. If `dim_month` derives its
fiscal month using a different calendar than `dim_date` does, the two no longer conform,
the drill-across still runs, and forecast-versus-actual is wrong at every period boundary.
Restriction preserves conformity. Redefinition destroys it, and looks identical in the
schema diagram.

## The bus matrix: conformity as a plan

Because conformed dimensions are about *sharing across processes*, they come with a
planning tool: the **bus matrix**. It's a simple grid — business processes (future fact
tables) down the side, dimensions across the top — with a mark wherever a process uses
a dimension.

```
                  Date  Customer  Product  Store  Employee
Sales              ✓       ✓         ✓       ✓
Shipping           ✓       ✓         ✓       ✓
Support Tickets    ✓       ✓                         ✓
Web Sessions       ✓       ✓         ✓
```

The columns that recur — Date, Customer, Product — are your conformed dimensions, the
ones worth building once, carefully, and sharing. The matrix lets you build the
warehouse **incrementally, one process at a time**, while guaranteeing the pieces
integrate: each new fact table reuses the dimensions already built rather than
inventing its own. It's the architecture that lets you ship a sales mart now and a
support mart next quarter and have them work together on day one.

## Conformed facts: the half nobody mentions

Conforming the dimensions aligns the *rows* of a drill-across. It does nothing about the
*columns*, and that is where the second failure lives.

If `revenue` appears in both the sales fact table and the finance fact table, the
drill-across will happily place the two side by side under one heading. Whether that means
anything depends entirely on whether the two definitions match: does sales `revenue`
include tax, freight, returns, intercompany eliminations? Does finance `revenue`? If the
answers differ, you have produced a comparison of two different quantities and labelled it
as one.

Kimball's
[rule for conformed facts](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/conformed-fact/)
is a naming discipline, and it is unusually practical for a modeling rule:

- If two measures have **identical technical definitions**, give them the **same name**.
  They are the same fact and should be comparable everywhere.
- If they are **incompatible**, give them **deliberately different names** —
  `gross_revenue` and `net_recognized_revenue`, not `revenue` twice.

The second rule is the one that earns its keep. It converts a silent semantic error into a
visible naming difference, at the exact moment someone tries to put both columns in one
report. You cannot enforce definitional agreement through a foreign key, but you can make
disagreement impossible to ignore. This is the same instinct as a
[data contract](/glossary/data-contract/): make the disagreement surface early and loudly
rather than late and quietly.

## What conformance is not

Three concepts get filed under the same heading because they all involve dimensions
behaving in a non-obvious way. They are orthogonal, and one dimension can be all three at
once.

| Concept | The question it answers | Typical example |
|---|---|---|
| **Conformed** | Is this dimension shared *across fact tables* with the same meaning? | One `dim_customer` used by sales and support |
| **Role-playing** | Is this dimension joined *several times to one fact table* under different aliases? | `order_date` and `ship_date` both pointing at `dim_date` |
| **Multi-valued** | Does one fact row legitimately have *many* dimension members? | A patient visit with several diagnoses, resolved by a bridge table |

A date dimension in a well-built warehouse is usually conformed *and* role-playing at the
same time: every fact table in the enterprise points at the same `dim_date`, and several
of them point at it more than once. Those two facts about it are unrelated, and neither
implies the other.

Multi-valued is the one that is genuinely a different subject. It concerns the
[grain](/glossary/grain/) of the relationship between a fact and its dimension rather than
the sharing of the dimension, and it is resolved with a bridge table. A bridge table can
sit between a fact and a perfectly conformed dimension without affecting its conformity at
all.

## Getting conformity right

The practical discipline is to identify the dimensions used across many processes —
almost always date, customer, and product, plus whatever is central to your business —
and treat them as **shared assets owned deliberately**, not as something each team
rebuilds locally. This is as much an [ownership question](/essays/data-quality-problems-are-org-chart-problems/)
as a modeling one: a conformed dimension only stays conformed if someone is
responsible for keeping it the single, authoritative version.

Four things are worth checking on a warehouse that claims to have conformed dimensions,
because each can be absent while the schema diagram still looks correct:

- **Do the surrogate keys match** across marts, not just the attribute names?
- **Are the rollups strict subsets**, or has one of them quietly redefined a derived
  attribute such as fiscal period?
- **Do the drill-across queries aggregate before merging**, or is something joining fact
  to fact and returning inflated numbers nobody has audited?
- **Are incompatible measures differently named**, so that putting the wrong two columns
  side by side is visibly wrong rather than merely wrong?

Do that, and your separate stars become a genuine warehouse — one where any process
can be compared to any other because they all speak the same dimensional language.
Skip it, and you get the thing that looks like a warehouse on the schema diagram but
behaves like a dozen incompatible spreadsheets the moment someone asks a question that
crosses two processes. Conformed dimensions are the difference, and they're worth the
deliberate effort they take.
