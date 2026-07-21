---
title: Storage Tiering Decision
author: Platform Engineering
date: 2026-07-21
---

[layout: title]

# Storage Tiering Decision

Platform Engineering — July 2026

???
Thirty seconds. Name the decision we are here to make, not the background.
Everyone in the room already knows storage costs are up.

---

[layout: section]

# The problem

---

## Cold data is paying hot prices

- 41% of the platform bill is object storage
- 72% of stored bytes unread in 90 days
- All of it sits on the standard tier

???
The 72% number is the one that lands. Pause after it.
If asked how we measured: 12 months of access logs, not sampling.

---

[layout: two-column]

## What tiering costs us

Moving cold objects to infrequent access saves real money every month.

:::

But retrieval gets slower, and a small set of compliance exports are read
rarely and under a hard deadline.

???
This is the whole tradeoff. Do not rush it.

---

## Three policies, modelled

| Policy | Trigger | Saving | Latency |
|--------|---------|--------|---------|
| A | 180 days | $8,400 | 15-40 ms |
| B | 90 days | $19,100 | 15-40 ms |
| C | 30 days | $27,600 | 3-5 hours |

???
Let them read it. Do not narrate the table.
Policy C's latency is hours because it moves to archive class.

---

[layout: quote]

> A multi-hour restore against a regulator deadline is not a tradeoff
> worth $8,500 a month.

---

## Recommendation: Policy B

- Captures 69% of the theoretical saving
- Latency stays inside what the gateway already tolerates
- No caller changes required
- Compliance prefix stays on standard via tag

???
Expect pushback on why not C. The answer is the compliance tail, not the money.

---

[layout: section]

# Next steps

---

## What happens now

1. Lifecycle rule to staging this week
2. Compliance prefix tagged and verified
3. Production rollout after one full billing cycle

???
Ask for the go/no-go here. Do not end on a slide with no ask.
