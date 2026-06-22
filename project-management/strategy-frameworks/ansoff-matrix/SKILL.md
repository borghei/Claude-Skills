---
name: ansoff-matrix
description: >
  Ansoff Matrix — 4-quadrant framework for growth options: market
  penetration, market/product development, and diversification. Use
  when evaluating growth bets, prioritizing investment across quadrants,
  or weighing the risk ladder of each move.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: strategy-frameworks
  updated: 2026-05-27
  python-tools: ansoff_growth_scorer.py
  tech-stack: ansoff-matrix, growth-strategy, product-market-expansion
---

# Ansoff Matrix

Igor Ansoff's product/market matrix for evaluating growth options.
Forces explicit choice between four growth bets of increasing risk.

## The 2x2

|                 | **Existing Products** | **New Products**       |
|-----------------|------------------------|------------------------|
| **Existing Markets** | Market Penetration (lowest risk) | Product Development |
| **New Markets**       | Market Development | Diversification (highest risk) |

## When to use this skill

- **Annual / quarterly growth planning**
- **Investment allocation** across growth bets
- **Post-funding deployment** planning
- **Board strategy discussions**
- **Strategic-pivot decisions** (which quadrant are we really in?)
- **Acquisition rationale** assessment

## The 4 quadrants in depth

### Q1 — Market Penetration (existing product × existing market)
Sell more of what we have to people we know.

**Tactics:**
- Increase usage / frequency
- Take share from competitors
- Improve conversion rates
- Pricing optimization
- Loyalty / retention programs

**Risk profile:** Lowest. You know the product + market.

**Investment:** ~30-50% of growth investment for most companies.

**When dominant:** Early-stage; high-growth market with share to take.

### Q2 — Market Development (existing product × new market)
Take what works to a new market.

**Tactics:**
- New geography
- New industry vertical
- New customer segment (SMB → mid-market)
- New use case
- New channel (direct → channel; SMB → enterprise sales)

**Risk profile:** Medium. Product known; market unknown.

**Investment:** ~20-30%.

**When dominant:** Product-market fit established in initial segment;
proven by reference customers; ready to scale.

### Q3 — Product Development (new product × existing market)
Build something new for people we know.

**Tactics:**
- New SKU / module / add-on
- Adjacent product line
- Platform extension
- Feature line that becomes its own product

**Risk profile:** Medium. Market known; product unknown.

**Investment:** ~15-25%.

**When dominant:** Captive audience with related JTBDs;
distribution advantage; brand permission to extend.

### Q4 — Diversification (new product × new market)
New thing for new people.

**Tactics:**
- Adjacent diversification (related to current)
- Conglomerate diversification (unrelated)
- Acquisition-driven new categories

**Risk profile:** Highest. Both axes unknown.

**Investment:** ~5-15% (or 0% — most companies should not diversify).

**When dominant:** Few situations justify high diversification. Usually:
mature core business with cash, declining core business needing pivot,
or genuine adjacent opportunity with shared capability.

## Clarify First

Before scoring the growth options, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Precise "existing" boundaries** — which segment/geography/buyer is "existing market" and which SKU/capabilities are "existing product" (vague boundaries cause the #1 error: misclassifying a Q4 bet as Q2/Q3)
- [ ] **The growth initiatives to classify** — the actual list of bets (the raw input to quadrant assignment; no list, no matrix)
- [ ] **Company stage** — early / growth / mature (sets the stage-appropriate target investment mix across quadrants)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Define "existing" precisely
Most Ansoff confusion comes from vague boundaries.
- "Existing market" = which segment, which geography, which buyer
- "Existing product" = which SKU, which capabilities
- "New" = anything outside those boundaries

### Step 2 — List current growth initiatives
For each initiative, classify into a quadrant. Be honest:
- "Adjacent vertical for our SaaS" = Market Development (usually)
- "New module for existing customers" = Product Development
- "Same product in EU" = Market Development (regulatory, cultural,
  linguistic differences = market difference)

### Step 3 — Score by risk-adjusted return
Per initiative:
- Investment size
- Expected return
- Risk of failure
- Time to revenue
- Risk-adjusted ROI

### Step 4 — Allocate across quadrants
Most companies cluster in Q1 + one other. Pure diversification (Q4) is
rare; usually disguised market or product development.

### Step 5 — Validate the mix
Target mix depends on stage:
- **Early:** 70% Q1 + 30% Q2/Q3 (split)
- **Growth:** 50% Q1 + 25% Q2 + 25% Q3
- **Mature:** 30% Q1 + 30% Q2 + 30% Q3 + 10% Q4

If you're 90% Q1, you're not growing strategically. If you're 40% Q4,
you're betting the company.

### Step 6 — Run `ansoff_growth_scorer.py`
Score each initiative; surface mix; flag risky concentration.

```bash
python3 project-management/strategy-frameworks/ansoff-matrix/scripts/ansoff_growth_scorer.py \
  --input initiatives.json --format markdown
```

## Decision frameworks

### What counts as "new market"?

| Different... | New market? |
|--------------|-------------|
| Geography | Yes (regulation, culture, language, channel) |
| Industry vertical | Yes |
| Company size band (SMB → ENT) | Usually yes |
| Use case (same persona) | Usually no |
| Buyer persona | Yes |
| Pricing tier (free vs paid) | Usually no |

If you'd need a different sales motion or different channels, it's a new market.

### What counts as "new product"?

| Different... | New product? |
|--------------|--------------|
| New SKU / module | Yes |
| New pricing tier of same product | No |
| New feature in existing product | No |
| Significantly different value prop | Yes |
| Different underlying tech | Yes |

If you'd need a different roadmap and different success metrics, it's a new product.

### When diversification (Q4) makes sense

- **Adjacent diversification:** shared capability or audience
  - Amazon → AWS: shared capability (infra)
  - Disney → theme parks: shared capability (IP)
- **Acquisition-led:** buying expertise + product + market together
- **Declining core:** need new business model

When diversification fails:
- "Synergies" overclaimed
- Acquired company managed by incumbent culture
- No shared capability or audience
- Justified by spreadsheet only

## Common engagements

### "Help us prioritize growth bets"
1. List all growth initiatives.
2. Classify into quadrants.
3. Score risk-adjusted return.
4. Reconcile against stage-appropriate target mix.
5. Recommend top 5 with allocation.

### "We're considering acquiring company X"
1. Classify the acquisition by quadrant.
2. Q1 (existing × existing) = bolt-on; lower risk
3. Q2 (existing × new) = market expansion via M&A
4. Q3 (new × existing) = product line extension
5. Q4 (new × new) = highest risk; question hard

### "Should we enter market X?"
1. Confirm it's truly Q2 (new market for existing product).
2. Test: same value prop? same buyer? same channel? if all yes, it's
   really Q1 (different segment).
3. If true Q2, scope cost + time to validate vs Q1 alternatives.

## Anti-patterns to avoid

- **Misclassifying initiatives.** Q4 dressed as Q3 or Q2 — gets approved that wouldn't pass Q4 scrutiny.
- **All-Q1 portfolio.** Not strategic growth.
- **All-Q4 portfolio.** Bet-the-company every quarter.
- **"Adjacent" labelling.** Often hides Q4 as Q3.
- **No investment percentages.** Just lists; no allocation.
- **Static mix.** Should change with stage.
- **Ignoring the boring Q1.** Penetration is unglamorous but highest-ROI.

## References

- `references/ansoff-matrix-deep.md` — quadrant tactics, examples, risk patterns
- `references/growth-strategy-patterns.md` — stage-based mixes, common pitfalls

## Related skills

- `project-management/strategy-frameworks/business-model-canvas` — operational view of each quadrant
- `project-management/strategy-frameworks/swot-analysis` — strategic context
- `project-management/strategy-frameworks/porters-five-forces` — industry analysis
- `c-level-advisor/ceo-advisor` — strategic context
- `c-level-advisor/cmo-advisor` — Q1/Q2 marketing context
- `c-level-advisor/cpo-advisor` — Q3 product development context
