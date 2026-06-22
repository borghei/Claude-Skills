---
name: swot-analysis
description: >
  SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for
  strategic positioning. Use when assessing a new market entry, a
  strategic pivot, a competitive response, an org restructure, or as
  input to annual strategic planning.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: strategy-frameworks
  updated: 2026-05-27
  python-tools: swot_scorer.py
  tech-stack: swot-analysis, strategic-positioning, situation-analysis
---

# SWOT Analysis

A grounded, evidence-backed SWOT — not the bullet-point ceremony most
people perform at the start of a planning offsite.

## When to use this skill

- **Annual strategic planning** input
- **New market entry** assessment
- **Pivot conversations**
- **Competitive response** decisions
- **Org restructure** evaluation
- **Pre-board** strategic review
- **Pre-fundraise** investor narrative grounding

## The 2x2

|                | Helpful | Harmful |
|----------------|---------|---------|
| **Internal**   | Strengths | Weaknesses |
| **External**   | Opportunities | Threats |

Internal = within our control (people, IP, ops, brand, capital).
External = outside our control (market, competition, regulation, tech shifts).

The single most-common SWOT failure: confusing internal with external.

## Clarify First

Before building the SWOT, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Explicit scope/subject** — e.g. "entering market X" or "our position vs Competitor X" (a SWOT for "the company" produces four lists pointing in four directions)
- [ ] **Evidence per item** — the data/quote/benchmark behind each entry (strengths must be facts, not aspirations; a SWOT with no real weaknesses signals bias)
- [ ] **Competitor/market reference frame** — what you're comparing against (strengths and threats are relative, not absolute)
- [ ] **TOWS actions wanted** — whether to cross-cut into SO/ST/WO/WT moves (converts the static SWOT into strategy rather than a wall of bullets)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Define the scope
A SWOT must have an explicit subject:
- "Acme entering the European market"
- "Our enterprise sales motion vs SMB"
- "Our position vs Competitor X in vertical Y"

A SWOT without scope produces 4 lists of bullets that point in 4 directions.

### Step 2 — Strengths (with evidence)
For each strength:
- What is it specifically?
- What's the evidence (data, customer quote, benchmark)?
- How does it compare to competitors?
- Does the market actually care?

A strength no customer cares about isn't a strength.

### Step 3 — Weaknesses (with honesty)
For each weakness:
- What is it specifically?
- What's the evidence?
- Are we fixing it? Why or why not?
- What's the cost of leaving it?

A SWOT with no real weaknesses signals bias or low candor.

### Step 4 — Opportunities (with sizing)
For each opportunity:
- What's the trigger / shift creating this opportunity?
- What's the size (TAM/SAM/SOM if quantifiable)?
- What's the time window?
- What's our right to win?

"AI is hot" is not an opportunity. "Regulated industries replacing
manual GDPR processes — $8B SAM, 36-month window" is.

### Step 5 — Threats (with severity)
For each threat:
- What is it specifically?
- How likely (1-5)?
- How severe if realized (1-5)?
- What can we do to mitigate?

### Step 6 — TOWS matrix (cross-cuts)
The most-valuable post-SWOT step:

|              | Opportunities | Threats |
|--------------|---------------|---------|
| **Strengths** | SO: leverage strength to capture opportunity | ST: leverage strength to defend against threat |
| **Weaknesses** | WO: address weakness to capture opportunity | WT: minimize weakness to avoid threat |

This converts a static SWOT into strategic actions.

### Step 7 — Run `swot_scorer.py`
Audit for: generic items, missing evidence, internal/external misclassification,
no quantification, no TOWS actions, one-sided SWOT.

```bash
python3 project-management/strategy-frameworks/swot-analysis/scripts/swot_scorer.py \
  --input swot.json --format markdown
```

## Decision frameworks

### Internal vs external — the test

If the item depends on something we own (people, money, tech, brand,
process, IP) → internal.

If the item depends on something we don't own (market, customers,
competitors, regulators, technology trends) → external.

Common miscategorizations:
- "Strong brand recognition in segment X" — internal (we own it)
- "Customers love our brand" — external (customer behavior)
- "Strong eng team" — internal
- "Hard to recruit eng talent" — external
- "Our cloud bill is high" — internal
- "Cloud prices rising" — external

### When to do a SWOT vs other frameworks

| Use SWOT | Use other |
|----------|-----------|
| Broad strategic positioning | Industry analysis → Porter's Five Forces |
| Multi-stakeholder alignment | Macro environment → PESTLE |
| Annual planning input | Growth options → Ansoff Matrix |
| New market entry overview | Business model design → BMC / Lean Canvas |

SWOT is breadth. Other frameworks add depth on specific dimensions.

### From SWOT to strategy

A SWOT alone isn't a strategy. It's input. Strategy comes from:

1. SWOT → identifies positioning realities
2. TOWS → identifies strategic options
3. Prioritization → which 2-3 options to pursue
4. Resourcing → what we'll fund + give up
5. KPIs → how we'll know it worked

Skipping any step produces a wall of analysis without action.

## Common engagements

### "Run a SWOT for entering market X"
1. Scope: explicitly "entering market X."
2. List internal capabilities relevant to that market (Strengths, Weaknesses).
3. List external factors specific to market X (Opportunities, Threats).
4. Score evidence + materiality per item.
5. Run TOWS.
6. Recommend 2-3 strategic moves.

### "Audit our existing SWOT"
1. Pull current SWOT.
2. Run `swot_scorer.py` for generic/ungrounded/miscategorized items.
3. Surface bias: too many strengths, no real weaknesses, vague opportunities.
4. Add TOWS if missing.

## Anti-patterns to avoid

- **No explicit scope.** SWOT for "the company" = SWOT for nothing.
- **Generic items.** "Great team, great product, growing market, competitors."
- **Strengths = aspirations.** What you wish were true, not what is.
- **No weaknesses.** Either bias or low candor.
- **Opportunities = topics, not options.** "AI" isn't an opportunity.
- **Threats = abstract anxieties.** Quantify likelihood + severity.
- **No TOWS.** SWOT without TOWS is just a wall.
- **Internal/external confusion.** Common; check every item.
- **SWOT replaces strategy.** SWOT is input, not output.

## References

- `references/swot-framework.md` — categorization, evidence standards, TOWS
- `references/swot-anti-patterns.md` — common failures + worked fixes

## Related skills

- `project-management/strategy-frameworks/porters-five-forces` — competitive dynamics
- `project-management/strategy-frameworks/ansoff-matrix` — growth options
- `project-management/strategy-frameworks/business-model-canvas` — operational view
- `project-management/strategy-frameworks/lean-canvas` — startup view
- `c-level-advisor/ceo-advisor` — strategic context
