# Market Sizing Memo — [Market Name]

**Author:** [name] | **Date:** [YYYY-MM-DD] | **Decision this supports:** [the specific decision]

> Replace every bracketed field. Delete any section you genuinely do not need,
> but never delete the Reconciliation or Sensitivity sections — those are the
> two a reviewer will look for first.

---

## Market definition

[One sentence. Must include the problem, the buyer, and the geography.
Example: "Cloud practice-management software sold to EU-27 dental clinics
operating three or more chairs."]

**Explicitly out of scope:** [what a reader might assume is included but is not]

---

## Headline

| Layer | Value | Basis |
|-------|-------|-------|
| **TAM** | [currency + amount] / year | [one clause] |
| **SAM** | [currency + amount] / year | [one clause] |
| **SOM ([N]-year)** | [low]–[high], base case [amount] | [one clause] |

**In one sentence:** [The takeaway a reader would repeat in a meeting.]

---

## Top-down build

**Anchor:** [source name, publication date] — [value]
**Vintage:** [N] years. [If over 18 months: growth bridge applied at [X]% CAGR
sourced from [source]; raw [value] → bridged [value].]

| Step | Retention | Surviving value | Surviving units | Basis |
|------|-----------|-----------------|-----------------|-------|
| Anchor | — | [value] | [units] | [source] |
| [filter 1] | [x.xx] | [value] | [units] | [evidence] |
| [filter 2] | [x.xx] | [value] | [units] | [evidence] |
| **= SAM** | | **[value]** | **[units]** | |
| [reach filter] | [x.xx] | [value] | [units] | [evidence] |
| [win-rate filter] | [x.xx] | [value] | [units] | [evidence] |
| **= SOM** | | **[value]** | **[units]** | |

---

## Bottom-up build

| Input | Value | Source |
|-------|-------|--------|
| Unit base ([unit name]) | [count] | [countable source] |
| Qualified share | [x.xx] | [evidence] |
| Annual value per unit | [amount] | [observed / budget-derived — say which] |
| Reachable share | [x.xx] | [named channel and its capacity] |
| Expected win rate | [x.xx] | [observed rate or stated comparable] |

**TAM** [value] · **SAM** [value] · **SOM** [value]

---

## Reconciliation

| Layer | Top-down | Bottom-up | Divergence | Explanation |
|-------|----------|-----------|------------|-------------|
| TAM | [value] | [value] | [N]x | [what definitional difference accounts for it] |
| SAM | [value] | [value] | [N]x | [—] |
| SOM | [value] | [value] | [N]x | [—] |

**Which build we lead with and why:** [state one, with the reason]

---

## Sensitivity

The three assumptions the number is most sensitive to, ranked by their swing in SOM:

| Assumption | Base case | Plausible range | SOM at low | SOM at high |
|------------|-----------|-----------------|-----------|------------|
| [assumption 1] | [value] | [low]–[high] | [value] | [value] |
| [assumption 2] | [value] | [low]–[high] | [value] | [value] |
| [assumption 3] | [value] | [low]–[high] | [value] | [value] |

---

## Segmentation

| Segment | Units | Value per unit | Expected win rate | SOM contribution |
|---------|-------|----------------|-------------------|------------------|
| [segment] | [count] | [amount] | [x.xx] | [value] |
| [segment] | [count] | [amount] | [x.xx] | [value] |

**Segmentation variable used:** [variable] — chosen because [the segments differ
measurably on [metric], and membership is identifiable before the sale].

---

## What would change this answer

- [Specific observation 1 — and which direction it would move the number]
- [Specific observation 2]
- [Specific observation 3]

## Known weaknesses

- [The weakest link in the build, stated plainly before a reviewer finds it]
- [Any layer resting on a single unverified source]

## Assumptions made without confirmation

[If this memo was drafted without confirming the Clarify First inputs, list every
assumption here. Delete this section once the inputs are confirmed.]
