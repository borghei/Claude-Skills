---
name: offer-design
description: >
  Build an offer from the buyer's obstacles: component stack, value drivers,
  an affordable guarantee and honest urgency, scored before launch. Use when
  buyers say no, packaging bonuses, choosing a guarantee, or naming an offer.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-growth
  domain: offer-design
  updated: 2026-11-08
  tags: [offer, value-proposition, guarantee, bonuses, conversion, packaging]
---

# Offer Design

An offer is everything a buyer gets for the price, framed around the result
they want. When good products do not sell, the usual cause is that buyers
cannot see how the offer gets them past the obstacles they already expect. This
skill builds the offer from those obstacles, scores its perceived value,
checks that every component earns its cost, prices the guarantee into the
contribution, and refuses fake urgency.

The agent works from the buyer's words: obstacles, objections and the result
they want come from interviews, reviews or panel answers, not from the seller's
feature list.

## When to use this skill

- **Buyers say no** and the product is not obviously the problem
- **Packaging a launch offer** with bonuses, onboarding help or included extras
- **Choosing a guarantee** and checking the business can afford it
- **Adding urgency** without inventing scarcity
- **Naming the offer** by the outcome it delivers
- **Comparing two offer versions** before testing them with buyers

For setting the price point, tiers and value metric, use a pricing skill; this
one designs what the price buys.

## Inputs the skill expects

- Price and core delivery cost per sale
- The result the buyer wants, in their words
- The obstacles the buyer expects on the way to that result
- Candidate components, each with a buyer value and a delivery cost
- Proof available today (results, demonstrations, credentials)
- Refund history or a reasoned claim-rate estimate for any guarantee
- Any real constraint that could justify urgency (cohort dates, capacity)

## Clarify First

The obstacle list shapes this output more than anything else: the offer is
built to remove them. Settle the inputs below before producing anything. When
one is missing or vague and would change the result, ask about it; when it
wouldn't, use a sensible default and say which one you used.

- **The obstacles, in the buyer's words:** each one becomes a component; an
  obstacle invented by the seller produces a component nobody values.
- **Delivery cost per component:** decides what gets trimmed and whether the
  guarantee is affordable.
- **What proof exists today:** belief is the driver most new offers fail on,
  and the score must not credit proof that does not exist.
- **Any real deadline or capacity limit:** urgency is only added when a buyer
  could verify it.

Ask about the two or three inputs that matter most for this request, not the
whole list. If the user wants a result straight away, produce it and state your
assumptions at the top, marking estimated values and costs.

## Quick Start

```bash
python3 business-growth/offer-design/scripts/offer_scorer.py \
  --input business-growth/offer-design/assets/sample_offer.json

python3 business-growth/offer-design/scripts/offer_scorer.py \
  --input business-growth/offer-design/assets/sample_offer_flawed.json --format json
```

## Tools Overview

| Tool | Input | Output | Exit codes |
|------|-------|--------|------------|
| `offer_scorer.py` | Offer JSON | Value score 0-100, best lever, stack ratio, obstacle coverage, component efficiency, contribution after guarantee, findings | 0 no fail, 1 fail finding, 2 bad input |

Stdlib-only and deterministic, with `--format text|json`. The scoring formula is
printed in `--help` so every number can be checked by hand.

## Workflows

### Workflow 1 — Build the offer from obstacles

1. Check the market first: pain, budget, reach and momentum
   (`references/offer-construction.md`, section 1). If two are weak, rework who
   the offer is for before designing anything.
2. Write the result the buyer wants in one sentence, in their words.
3. List every obstacle between paying and getting that result: before, during
   and after. Pull them from interviews, reviews of alternatives or panel
   objections.
4. For each obstacle, write the component that removes it, its buyer value and
   its delivery cost.
5. Score the four value drivers from the buyer's point of view: outcome, belief,
   days to first result, effort.

### Workflow 2 — Score, trim and strengthen

1. Run the scorer. Every FAIL must be fixed before the offer is shown to buyers.

```bash
python3 business-growth/offer-design/scripts/offer_scorer.py --input offer.json
```

2. Trim components that return under 3x their cost or answer no obstacle.
3. Add components for unanswered obstacles, cheapest effective fix first.
4. Follow the best lever the scorer names: raise belief with proof, or cut
   effort and time to the first result.
5. Re-run until the stack is 3x price or more and coverage is complete.

### Workflow 3 — Guarantee, urgency and name

1. Pick the strongest guarantee type the contribution can afford, write exact
   terms, and enter an honest claim rate. The scorer subtracts expected claims
   from contribution and fails a guarantee that makes sales lose money.
2. Add urgency only from a real constraint (cohort date, capacity cap, published
   deadline) and mark it verifiable. The scorer fails unverifiable urgency.
3. Name the offer by outcome and timeframe, under twelve words.
4. Fill `assets/offer-sheet-template.md`.

### Workflow 4 — Test with buyers

1. Show the offer to buyers: a simulated panel to surface objections quickly,
   then a real priced test.
2. Find the objection that still blocks the most buyers, change the one
   component that answers it, re-score and re-test.
3. Change one thing per round so the result can be attributed.

### Validation checkpoint before launch

Use this checklist; each item must pass:

- [ ] Scorer exits 0 (no FAIL findings)
- [ ] Every obstacle came from buyers, and each is answered
- [ ] Belief score is backed by at least two proof items
- [ ] Guarantee terms written, claim rate sourced
- [ ] Urgency, if any, is verifiable by a buyer

## Decision frameworks

### Which guarantee

| Situation | Guarantee | Confidence |
|-----------|-----------|------------|
| Results depend on the buyer's participation | Conditional (did the work, no result, refund) | **[PROVEN]** |
| Low delivery cost, strong onboarding | Unconditional within a window | **[RECOMMENDED]** |
| Measurable result with a delivery track record | Outcome guarantee | **[RECOMMENDED]** |
| Heavy front-loaded delivery cost, high belief already | None, with proof instead | **[RECOMMENDED]** |

### Which lever first

| Weakest signal | Lever | Why |
|----------------|-------|-----|
| Belief under 6 | **[PROVEN]** Proof and a guarantee | New businesses lose most buyers on "will this work for me" |
| Effort 7+ or first result over 90 days | **[RECOMMENDED]** Done-for-you parts, a week-one win | Cheaper to fix than outcome size |
| Stack under 3x price | **[RECOMMENDED]** Add obstacle-removing bonuses before cutting price | Price cuts invite matching; stack changes do not |
| Coverage under 100% | Add a component per unanswered obstacle | An unanswered obstacle is a standing reason to say no |

### Thresholds the scorer enforces

| Check | Warn | Fail |
|-------|------|------|
| Stack value / price | Under 3x | Under 1x |
| Obstacle coverage | Any obstacle unanswered | Under 60% |
| Component value / cost | Under 3x | — |
| Contribution after guarantee | Under 20% of price | Zero or below |
| Urgency | — | No reason, or not verifiable |
| Belief without proof | 8+ with fewer than 2 proof items | — |

## Anti-Patterns

### The Feature Stack
**Mistake:** Listing everything the product does as bonuses, regardless of what the buyer worries about.
**Why it happens:** The seller knows the features and assumes more equals better.
**Instead:** Start from obstacles. A component that answers no obstacle reads as
padding and lowers perceived value; the scorer flags it.

### The Unaffordable Guarantee
**Mistake:** Offering a no-questions refund on a product with high delivery cost and weak onboarding.
**Why it happens:** Strong guarantees lift conversion in case studies, and the claim rate is never estimated.
**Instead:** Price the guarantee in: expected claims times price comes out of
contribution. Pick a conditional guarantee when results depend on participation.

### The Resetting Countdown
**Mistake:** Adding a deadline or "only a few left" that is not true.
**Why it happens:** Urgency lifts short-term conversion, and the cost lands later.
**Instead:** Use only constraints a buyer could check: cohort dates, capacity
caps, published price changes. Fake scarcity breaks trust and can breach
consumer-protection rules.

### Competing on Price Alone
**Mistake:** Responding to "too expensive" by cutting the price.
**Why it happens:** It is the fastest change and the objection names price.
**Instead:** First raise belief, cut effort and add obstacle-removing components;
re-test at the same or a higher price. "Too expensive" often means "not sure it
will work for me".

### Belief Scored on Hope
**Mistake:** Rating belief 8-9 because the founder is confident.
**Why it happens:** The seller scores from their own view rather than the buyer's.
**Instead:** Score belief from the buyer's side and back anything above 7 with
proof. The scorer warns when the score is not earned.

## Reference Documentation

- `references/offer-construction.md` — market check, the four value drivers,
  building from obstacles, guarantee types and affordability, honest urgency,
  naming, testing, and offer versus price

## Files

| File | Purpose |
|------|---------|
| `scripts/offer_scorer.py` | Scores value, stack, coverage, efficiency, guarantee cost and urgency |
| `references/offer-construction.md` | The method behind the scorer |
| `assets/sample_offer.json` | Sound example: beginner bouldering course (exit 0) |
| `assets/sample_offer_flawed.json` | Deliberately flawed example: online course with fake urgency (exit 1) |
| `assets/offer-sheet-template.md` | One-page offer sheet to fill after scoring |

## Scope & Limitations

**In Scope:**
- Building an offer from buyer obstacles and scoring it with `offer_scorer.py`
- Value-driver scoring, component trimming, stack ratio and obstacle coverage
- Guarantee choice with expected claim cost priced into contribution
- Honest urgency and outcome-led naming

**Out of Scope:**
- Setting the price point, tiers or value metric
- Writing ad copy, landing pages or sales emails
- Running the buyer tests themselves
- Legal review of guarantee or refund terms

**Important Caveats:**
- Buyer values and driver scores are judgements. The tool makes them explicit and
  consistent; it does not make them true. Validate with real buyers.
- The value score is a comparison aid between versions of one offer, not a
  benchmark across businesses.
- Refund and urgency rules vary by market. Have guarantee terms and any
  deadline or scarcity claims checked against local consumer-protection law.
