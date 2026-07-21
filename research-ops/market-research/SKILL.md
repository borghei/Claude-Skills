---
name: market-research
description: >
  Market sizing and market structure work — TAM/SAM/SOM built top-down and
  bottom-up then reconciled, segmentation, demand triangulation, and survey
  design. Use when sizing a market, writing a sizing memo, or fielding a survey.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: research-ops
  domain: market-sizing
  updated: 2026-07-21
  tags: [tam, sam, som, market-sizing, segmentation, survey-design, demand]
---

# Market Research

Applied market research for people who have to defend a number in a room. This
skill is about the operational craft: constructing a market size two independent
ways, reconciling the gap, cutting the market into segments that behave
differently, and fielding survey instruments that do not manufacture the answer
you hoped for.

## When to use this skill

- **Sizing a market for a board deck, investor memo, or funding request** where
  the number will be challenged line by line
- **Reconciling a TAM you inherited** — an analyst report says $12B, your
  bottom-up build says $700M, and you need to explain the gap
- **Segmenting a market** before a pricing, packaging, or GTM decision
- **Triangulating demand signals** (search volume, inbound, win rates, analyst
  data, competitor headcount) into one directional read
- **Designing a survey** to answer a market question — willingness to pay,
  category awareness, switching intent — without leading the respondent
- **Auditing someone else's sizing** before you sign off on it

## Inputs the skill expects

- The market definition in one sentence — including geography and buyer
- A top-down anchor (published market value) with its source and vintage
- Bottom-up unit economics — unit count, qualified share, annual value per unit
- The decision the number is feeding (investment size, hiring plan, pricing)
- Time horizon for SOM (1 year vs 3 years changes it by an order of magnitude)
- For surveys: population size, target margin of error, mode (panel, list, intercept)

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Market definition — what is in and what is out** — the single biggest driver of the number; "dental software" and "dental practice management software for multi-chair EU practices" differ by 20x
- [ ] **The decision this sizing supports** — a fundraise tolerates a wide TAM; a hiring plan needs a defensible SOM
- [ ] **Time horizon for SOM** — 12-month obtainable share and 3-year obtainable share are different artifacts
- [ ] **Whether a published anchor exists and its vintage** — a 2022 report in a 2026 memo needs an explicit growth bridge

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Build and reconcile TAM/SAM/SOM

1. Write the market definition sentence first. Everything downstream inherits it.
2. Build the top-down chain: published market value, then named filters that
   each cut it (geography, segment, buyer qualification), each with a retention
   fraction and a stated justification.
3. Build the bottom-up chain independently: unit count from a countable source,
   qualified share, annual value per unit, reachable share, expected win rate.
4. Run the builder. It computes both chains, reconciles them layer by layer, and
   flags implausible ratios and divergence.
5. Resolve every `fail` before the number leaves your machine. A `warn` needs a
   sentence in the memo, not a fix.

```bash
python3 research-ops/market-research/scripts/tam_sam_som_builder.py \
  --input research-ops/market-research/assets/sample_market_model.json \
  --format text
```

### Workflow 2 — Triangulate demand signals

1. Collect every observable demand signal you have — search volume, inbound
   lead velocity, win rate by segment, analyst growth rates, competitor hiring,
   category conference attendance.
2. Score each for source independence and directional strength.
3. Run the triangulator to get a weighted demand index and, more importantly,
   the list of signals that contradict each other.
4. Investigate contradictions before averaging them away. A conflicting signal
   is usually a segmentation boundary you have not drawn yet.

```bash
python3 research-ops/market-research/scripts/demand_signal_triangulator.py \
  --input research-ops/market-research/assets/sample_demand_signals.json \
  --format text
```

### Workflow 3 — Audit a survey instrument before fielding

1. Draft the instrument with the market question stated at the top.
2. Run the auditor. It checks each item for leading language, double-barrelled
   phrasing, absolutes, unbalanced or over-long scales, and missing escape
   options.
3. Check the sample-size verdict — it computes required n from population,
   target margin of error, and confidence level.
4. Fix every `fail`, then re-run. Field only on a clean run.

```bash
python3 research-ops/market-research/scripts/survey_instrument_auditor.py \
  --input research-ops/market-research/assets/sample_survey.json \
  --format text
```

## Decision frameworks

### Which sizing method for which situation

| Situation | Method | Why |
|-----------|--------|-----|
| Established category, published reports exist | **[PROVEN]** Top-down anchored, bottom-up as a check | The anchor is defensible; bottom-up catches definition drift |
| New category, no analyst coverage | **[PROVEN]** Bottom-up only, stated as such | A top-down number for a category that does not exist yet is fiction |
| Adjacent expansion from an existing product | **[RECOMMENDED]** Bottom-up from your own funnel conversion | Your observed win rates beat any external estimate |
| Regulated market with registries | **[PROVEN]** Bottom-up from the registry count | Counting licensed entities is the strongest unit base available |
| Consumer market, behaviour-driven | **[RECOMMENDED]** Top-down plus survey-derived incidence | Unit counts exist but qualification requires stated behaviour |

### Plausibility thresholds

These are the ratios the builder enforces. They are heuristics, not laws — but
crossing one without an explanation in the memo is how sizing loses credibility.

| Ratio | Healthy range | Flag when |
|-------|---------------|-----------|
| SAM / TAM | 5% – 40% | Above 60% — you are claiming almost the whole market is addressable |
| SOM / SAM (3-year) | 1% – 10% | Above 20% — implies category leadership inside the horizon |
| SOM / TAM | 0.1% – 5% | Above 5% for a pre-scale company |
| Bottom-up vs top-down TAM | Within 3x | Above 3x warn, above 10x fail — the two builds are answering different questions |

### Survey sample size at 95% confidence

Required n for a proportion estimate, finite population corrected. Use these as
a sanity check on the auditor's output.

| Population | ±10% MoE | ±5% MoE | ±3% MoE |
|-----------|----------|---------|---------|
| 500 | 81 | 218 | 341 |
| 5,000 | 95 | 357 | 880 |
| 100,000 | 96 | 383 | 1,056 |
| 1,000,000+ | 97 | 385 | 1,066 |

The jump from ±10% to ±5% quadruples cost for a band most market decisions do
not need. **[RECOMMENDED]** Field at ±10% for directional category questions and
reserve ±5% for pricing and packaging decisions where the band drives the choice.

## Anti-Patterns

### The Inherited TAM
**Mistake:** Copying a market size from an analyst report or a competitor's deck
into your own memo, adjusting the geography, and presenting it as your build.
**Why it happens:** The number is already large and already sourced, and building
bottom-up takes two days you do not think you have.
**Instead:** Use the published figure as the top-down anchor only, and always
build the bottom-up chain alongside it. The reconciliation gap is the most
informative artifact of the whole exercise — it tells you exactly which
definition the report used and yours does not.

### The Multiplication Fantasy
**Mistake:** SOM computed as "if we capture 1% of the TAM" with no mechanism
behind the 1%.
**Why it happens:** It sounds modest, so nobody challenges it, and it produces a
convenient number without requiring a channel model.
**Instead:** Build SOM from reachable units times expected win rate, where both
come from something observed — your funnel, a pilot, or a comparable. If you
cannot name the channel that reaches those units, you do not have a SOM.

### The Stale Anchor
**Mistake:** A four-year-old market report used at face value in a current memo.
**Why it happens:** It was the best available source when someone first built the
model, and nobody re-checks a number that has been in the deck for a year.
**Instead:** Record the vintage of every anchor. If it is more than 18 months
old, apply an explicit growth bridge with a stated CAGR and show both the raw
and bridged figures. An unbridged stale anchor invites the reviewer to discount
everything downstream of it.

### The Leading Instrument
**Mistake:** Asking "How valuable would an automated reporting feature be to
your team?" and reporting the enthusiasm as demand evidence.
**Why it happens:** The team already believes in the feature, and the question is
written by the person who wants it built.
**Instead:** Ask about the current behaviour and its cost — "How many hours last
month did your team spend building reports manually?" — and let the demand fall
out of the numbers. Run every instrument through the auditor before fielding;
leading items are cheap to fix pre-field and impossible to fix post-field.

### Segments That Do Not Behave Differently
**Mistake:** Cutting the market by company size or geography because that data is
available, then finding every segment has the same conversion and the same ACV.
**Why it happens:** Firmographic fields are in the CRM; behavioural ones are not.
**Instead:** Segment on the variable that changes the buying decision — trigger
event, existing tooling, regulatory obligation, or team structure. A segmentation
is only useful if the segments have measurably different win rates or values.

## Files

| File | Purpose |
|------|---------|
| `scripts/tam_sam_som_builder.py` | Builds top-down and bottom-up TAM/SAM/SOM, reconciles them, flags implausible ratios |
| `scripts/survey_instrument_auditor.py` | Checks survey items for leading language, scale problems, and computes required sample size |
| `scripts/demand_signal_triangulator.py` | Weights and triangulates demand signals; surfaces contradictions and source concentration |
| `references/market-sizing-methods.md` | Method selection, filter design, growth bridges, worked reconciliation examples |
| `references/survey-design-methodology.md` | Question construction, scale design, sampling frames, mode effects, field QA |
| `assets/market-sizing-memo-template.md` | The memo structure a sizing number ships in |
| `assets/sample_market_model.json` | Runnable input for the TAM/SAM/SOM builder |
| `assets/sample_survey.json` | Runnable input for the survey auditor |
| `assets/sample_demand_signals.json` | Runnable input for the demand triangulator |
