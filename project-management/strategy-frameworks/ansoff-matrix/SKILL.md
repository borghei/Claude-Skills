---
name: ansoff-matrix
description: >
  Classifies growth bets into the four Ansoff quadrants and checks the
  investment mix against the company's stage. Use when prioritising growth
  bets, allocating a growth budget or testing a pitched "adjacent" move.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: strategy-frameworks
  updated: 2026-11-08
  python-tools: ansoff_growth_scorer.py
  tech-stack: ansoff-matrix, growth-strategy, product-market-expansion
  tags:
    - ansoff-matrix
    - growth-strategy
    - diversification
    - market-development
---

# Ansoff Matrix

The agent uses the product/market matrix to force an explicit choice between four growth bets of increasing risk. Market penetration (existing product, existing market) carries the least risk, diversification (new product, new market) the most; market and product development sit between. Quadrant tactics, the risk ladder and misclassification patterns are in `references/ansoff-matrix-deep.md`.

**Done looks like:** "existing market" and "existing product" defined in a sentence each; every initiative in one quadrant with investment, expected return, a 1-5 risk score, an owner and a rationale; the mix compared with the stage target and every drift over 20 points explained; `ansoff_growth_scorer.py` exits 0.

## When to Use

- Annual or quarterly growth planning, or deploying a new funding round
- Board discussions of where growth money goes
- Checking whether an "adjacent" bet or an acquisition is really diversification

## Clarify First

Before scoring the growth options, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Precise "existing" boundaries:** which segment/geography/buyer is "existing market" and which SKU/capabilities are "existing product" (vague boundaries cause the #1 error: misclassifying a Q4 bet as Q2/Q3).
- **The growth initiatives to classify:** the actual list of bets (the raw input to quadrant assignment; no list, no matrix).
- **Company stage:** early / growth / mature (sets the stage-appropriate target investment mix across quadrants).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Balanced growth-stage portfolio: exit 0
python3 project-management/strategy-frameworks/ansoff-matrix/scripts/ansoff_growth_scorer.py \
  --input project-management/strategy-frameworks/ansoff-matrix/assets/sample_initiatives.json --format markdown
```

```bash
# Invalid quadrant, low-risk diversification, return below investment: exit 1
python3 project-management/strategy-frameworks/ansoff-matrix/scripts/ansoff_growth_scorer.py \
  --input project-management/strategy-frameworks/ansoff-matrix/assets/sample_initiatives_flawed.json --format markdown
```

```bash
# Input schema and flags
python3 project-management/strategy-frameworks/ansoff-matrix/scripts/ansoff_growth_scorer.py --help
```

## Tools Overview

`ansoff_growth_scorer.py` is the quality gate for this skill. **What the scorer checks:** a valid quadrant per initiative (fail otherwise); missing investment, return, rationale or owner; risk scores that contradict the quadrant (low-risk diversification, maximum-risk product development); expected return below investment; drift over 20 points from the target mix; diversification above 25%; penetration above 85% past the early stage. It classifies nothing itself: you assign the quadrant.

**Exit codes:** `0` no fail findings · `1` at least one fail (no initiatives, an invalid quadrant, a `target_mix` that does not sum to 100) · `2` unreadable file, invalid JSON or a top level that is not an object. JSON by default, `--format markdown`, `--output FILE`.

## Workflow

1. **Define "existing".** Which segment, geography and buyer is the existing market; which SKU and capabilities are the existing product. Vague boundaries are the most common error.
2. **Classify each initiative.** A different geography, vertical, size band or buyer persona is a new market; if it needs a different sales motion or channel, treat it as new. A new SKU, module, value proposition or underlying technology is a new product; a feature or pricing tier of the same product is not. "Adjacent" often hides diversification.
3. **Size each bet:** investment, expected return, risk (1-5), time to revenue, owner, rationale.
4. **Compare the mix with the stage target.** The defaults are a heuristic starting point, not a standard: early 75/10/15/0, growth 50/25/20/5, mature 35/27/28/10, declining 25/25/35/15 (penetration / market dev / product dev / diversification, % of investment). Put your own split in `target_mix` when leadership has one.
5. **Audit.** Write the bets as JSON (schema in `--help`; `assets/sample_initiatives.json` is a complete example) and run the scorer. It must pass with no fail findings; then verify that each drift is either fixed or explained in the plan.

## Anti-Patterns

### Diversification dressed as product development
**Mistake:** A new product for a new buyer is labelled "adjacent product development" and skips the scrutiny a diversification bet would get.
**Why it happens:** The lower-risk label gets budget approved faster.
**Instead:** Apply the new-market and new-product tests in step 2. If both answers are "new", call it diversification and justify it as one.

### No allocation, only a list
**Mistake:** The matrix shows initiatives in boxes but no investment numbers.
**Why it happens:** Classification feels like the analysis.
**Instead:** Put a budget on every bet so the mix can be compared with the stage target.

### Ignoring penetration
**Mistake:** Every new bet is market or product development while the core still has headroom.
**Why it happens:** Penetration work looks unglamorous.
**Instead:** Size the penetration opportunity first; it is usually the highest return for the risk.

## Scope & Limitations

**In Scope:**
- Classifying growth initiatives into the four Ansoff quadrants: market penetration, market development, product development and diversification
- Tests for what counts as a new market and a new product
- Per-initiative scoring on investment, expected return, risk and time to revenue
- Stage-based default investment mixes (heuristic, overridable with `target_mix`)
- A scorer that surfaces the investment mix and flags concentration and likely misclassification (`ansoff_growth_scorer.py`)

**Out of Scope:**
- Industry structure and competitive pressure analysis (see `project-management/strategy-frameworks/porters-five-forces/`)
- Internal strengths and weaknesses (see `project-management/strategy-frameworks/swot-analysis/`)
- Financial modelling and valuation of each bet (see `finance/financial-analyst/`)
- Running an acquisition beyond classifying it (see `c-level-advisor/ma-playbook/`)

**Important Caveats:**
- The user assigns each quadrant. The scorer only flags mismatches from the risk score, such as a Q1 bet with high risk or a Q4 bet with low risk.
- Investment, expected return and risk scores are estimates entered by hand. The output is only as good as those numbers.
- Stage mixes and per-quadrant investment ranges are rules of thumb, not targets every company should hit.
- Where the line between existing and new sits, and which bets to fund, stay leadership decisions.

## Files

| File | Purpose |
|------|---------|
| `scripts/ansoff_growth_scorer.py` | Quadrant mix audit and misclassification flags |
| `assets/sample_initiatives.json` | Five growth-stage bets; exits 0 |
| `assets/sample_initiatives_flawed.json` | Misclassified and invalid bets; exits 1 |
| `assets/ansoff_template.md` | Fill-in template |

## Reference Documentation

- [references/ansoff-matrix-deep.md](references/ansoff-matrix-deep.md): Quadrant tactics, examples, risk patterns, misclassification
- [references/growth-strategy-patterns.md](references/growth-strategy-patterns.md): Stage-based patterns and pitfalls

## Related skills

- `project-management/strategy-frameworks/business-model-canvas` — operational view of each quadrant
- `project-management/strategy-frameworks/swot-analysis` — strategic context
- `project-management/strategy-frameworks/porters-five-forces` — industry analysis
- `c-level-advisor/ceo-advisor` — strategic context
- `c-level-advisor/cmo-advisor` — Q1/Q2 marketing context
- `c-level-advisor/cpo-advisor` — Q3 product development context
