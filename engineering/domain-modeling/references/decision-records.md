# Decision Records

Lightweight architecture decision records (ADRs) for the decisions that shape a
domain model and the code around it. The goal is a short paper trail that stops
the team from relitigating settled questions and stops newcomers from "fixing"
things that were deliberate — without turning every choice into paperwork.

## Contents

- [When a decision earns a record](#when-a-decision-earns-a-record)
- [What usually qualifies](#what-usually-qualifies)
- [Layout and numbering](#layout-and-numbering)
- [Writing the record](#writing-the-record)
- [Lifecycle](#lifecycle)
- [Recording decisions during design work](#recording-decisions-during-design-work)
- [Worked examples](#worked-examples)

## When a decision earns a record

Write one only when all three hold:

| Test | Question | If no |
|------|----------|-------|
| Costly to reverse | Would undoing this take days of work, a migration, or a contract change? | Skip — you will just change it |
| Surprising later | Would someone reading the code in a year ask "why on earth is it like this?" | Skip — the code explains itself |
| Real trade-off | Was there a credible alternative, rejected for a reason? | Skip — there is nothing to record beyond "we did the obvious thing" |

`adr_lint.py` warns when an accepted record lists no alternatives, because that
usually means the third test failed.

## What usually qualifies

- **The shape of a domain concept**: "A Subscription has exactly one Plan at a time; Plan changes create a new period, not a new Subscription."
- **Ownership between contexts**: "Billing owns Invoice; other contexts refer to it by id only."
- **How contexts talk**: "Ordering and Billing communicate through published events, not synchronous calls."
- **Naming decisions that were contested**: "We use Subscription, not membership, everywhere."
- **Deliberate departures from the obvious**: "Totals are rounded once, after summing, even though line items are displayed rounded."
- **Constraints the code cannot show**: legal, contractual, regulatory or partner limits.
- **Rejections that will come back**: "We considered invoicing in advance and rejected it because refunds would become routine."

Not records: library picks that take an afternoon to swap, style choices, bug
fixes, and anything a code comment can explain in one line.

## Layout and numbering

```
docs/adr/
├── 0001-invoice-each-subscription-in-arrears.md
├── 0002-retry-failed-charges-nightly.md
└── 0003-grace-period-before-suspension.md
```

- Four-digit, zero-padded, sequential numbers. Never reuse a number and never delete a record.
- Slug in kebab-case, built from the title's meaningful words.
- First heading `# NNNN. Title`, matching the file number.
- Create `docs/adr/` when the first record is needed, not before.
- For a system with several contexts, keep system-wide records at the root and context-specific ones next to the context's code, each with its own sequence.

Get the next name with:

```bash
python3 scripts/adr_lint.py --dir docs/adr --next-title "Seven-day grace period before suspension"
```

## Writing the record

Required: **Status**, **Date** (ISO), **Context**, **Decision**. Optional, when
they add something: **Deciders**, **Alternatives considered**, **Consequences**,
**Supersedes**.

- **Title states the decision**, not the topic: "Invoice each Subscription in arrears", not "Invoicing approach".
- **Context** gives the forces: the problem, the constraint, what made it a choice. Use glossary terms; if you need a new term, add it to the glossary in the same change.
- **Decision** is decisive: "We will…", "We do not…". Hedged language ("we might consider") means the decision has not been made — keep the status `proposed`.
- **Alternatives** name each credible option and the reason it lost, in one line each.
- **Consequences** list what gets easier, what gets harder, and any follow-up work.

A record can be ten lines. Length is not quality; the reason is.

## Lifecycle

| Status | Meaning | Transition |
|--------|---------|------------|
| `proposed` | Written, under discussion | → accepted or rejected |
| `accepted` | In force | → deprecated or superseded |
| `rejected` | Considered and declined; kept so it is not proposed again unchanged | terminal |
| `deprecated` | No longer applies, nothing replaces it | terminal |
| `superseded by NNNN` | Replaced by a newer record | terminal |

Supersession runs both ways: the old record's status names the new one, and the
new one carries `**Supersedes:** NNNN`. `adr_lint.py` flags a supersession that
points at a missing record, a new record that claims to supersede an old one that
is not marked, and two records that disagree about which replaced which.

## Recording decisions during design work

Decisions crystallise mid-conversation. Capture them then:

1. When a choice passes the three tests, say so and offer to write the record. Do not write records nobody agreed to.
2. Draft from `assets/adr-template.md` with status `proposed`; ask the deciders to confirm, then set `accepted`.
3. When a proposal is rejected for a lasting reason, offer a `rejected` record so the next review does not suggest it again. Skip it for passing reasons ("not this quarter").
4. Before suggesting a change, check existing records in the area. If a suggestion contradicts one, raise it only when the new pain justifies reopening it — and then write a superseding record, not an edit to the old one.
5. Run `adr_lint.py` before merging.

## Worked examples

### Qualifies

```markdown
# 0007. Ordering and Billing exchange events, not synchronous calls

**Status:** accepted
**Date:** 2026-08-14
**Deciders:** Commerce lead, Billing lead

## Context
Placing an Order called Billing synchronously to create the first Invoice. Billing
outages blocked checkout twice this quarter.

## Decision
We will publish an OrderPlaced event; Billing creates the Invoice when it consumes
it. Ordering never calls Billing directly.

## Alternatives considered
- Retry the synchronous call with a circuit breaker: rejected, checkout still waits on Billing.

## Consequences
Invoices appear seconds after the Order rather than instantly. Billing must handle
duplicate events.
```

### Does not qualify

"We will use the standard JSON library instead of a faster third-party one." —
easy to reverse, unsurprising, no meaningful trade-off. A one-line code comment
is enough.
