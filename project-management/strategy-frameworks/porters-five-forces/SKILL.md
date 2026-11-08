---
name: porters-five-forces
description: >
  Rates the five competitive forces of one precisely defined industry with
  evidence and turns the dominant forces into moves. Use when weighing market
  entry, diagnosing margin pressure or auditing industry positioning.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: strategy-frameworks
  updated: 2026-11-08
  python-tools: five_forces_scorer.py
  tech-stack: porters-five-forces, industry-analysis, competitive-strategy
  tags:
    - porters-five-forces
    - industry-analysis
    - competition
    - market-entry
---

# Porter's Five Forces

Michael Porter's framework for analyzing the structural attractiveness
of an industry. Reveals where profit pools form, why some markets are
chronically unprofitable, and where strategic positioning has leverage.

**Done looks like:** an industry named by segment and geography; each force rated low, medium or high with at least two factors and cited evidence; the one or two dominant forces named; 2-3 high-priority moves that counter them; `five_forces_scorer.py` exits 0.

## When to Use

- A market-entry or M&A decision that turns on industry attractiveness
- Margins keep falling and nobody can say which force moved
- Planning a defensive strategy or competitive response

Firm-level strengths and weaknesses belong in `swot-analysis`; the forces, their sub-factors and examples are in `references/five-forces-deep.md` (the complementors "sixth force" is optional).

## Clarify First

Before scoring the forces, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Precise industry definition:** narrow enough to be specific, broad enough to catch substitutes (too broad/narrow is the #1 error and sets the entire analysis scope).
- **Evidence per force:** the data/facts behind each low/medium/high rating (a score without evidence is just opinion).
- **Purpose:** market entry / margin-pressure diagnosis / positioning audit (frames which dominant force matters and the strategy translation; margin diagnosis also needs a then-vs-now comparison).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Sound analysis: two dominant forces, three moves, exit 0
python3 project-management/strategy-frameworks/porters-five-forces/scripts/five_forces_scorer.py \
  --input project-management/strategy-frameworks/porters-five-forces/assets/sample_forces.json --format markdown
```

```bash
# "Software", a missing force and an invalid rating: exit 1
python3 project-management/strategy-frameworks/porters-five-forces/scripts/five_forces_scorer.py \
  --input project-management/strategy-frameworks/porters-five-forces/assets/sample_forces_flawed.json --format markdown
```

```bash
# Input schema and flags
python3 project-management/strategy-frameworks/porters-five-forces/scripts/five_forces_scorer.py --help
```

## Tools Overview

`five_forces_scorer.py` is the quality gate for this skill. **What the scorer checks:** an industry definition of useful length; all five forces rated with a valid intensity (fail otherwise); at least two factors and some evidence per force; all-medium ratings; strategy implications present with 1-5 high-priority moves. It sums intensities (low 1, medium 2, high 3) into an attractiveness band and reports "Not rated" while any force is missing. It does not judge whether the factors or evidence are right.

**Exit codes:** `0` no fail findings · `1` at least one fail (missing industry, an unscored force, an invalid intensity) · `2` unreadable file, invalid JSON or a top level that is not an object. JSON by default, `--format markdown`, `--output FILE`.

## Workflow

1. **Define the industry** by segment, buyer and geography. "Software" and "B2B SaaS" are too broad; "mid-market HR analytics SaaS in North America" works. Too narrow misses substitutes.
2. **Rate each force** low, medium or high using the sub-factors in `references/five-forces-deep.md`, with at least two factors and the evidence behind them. Rating everything medium usually means the factors were not weighed.
3. **Name the dominant forces** (usually one or two): they set the profit pool.
4. **Translate to moves.** For each high force, pick the counter from `references/five-forces-and-strategy.md` (barriers, diversifying supply or buyers, defending the value proposition, niching or consolidating) and mark 2-3 as high priority. For margin diagnosis, rate the industry then and now and name the force that shifted.
5. **Audit.** Write the analysis as JSON (schema in `--help`; `assets/sample_forces.json` is a complete example) and run the scorer.

## Anti-Patterns

### The industry is "software"
**Mistake:** The industry is defined so broadly that every force is "it depends".
**Why it happens:** A broad label feels safe and avoids choosing a segment.
**Instead:** Name segment, buyer and geography; check that the substitutes you care about still fall inside.

### Ratings without evidence
**Mistake:** Each force gets a colour and no factors or data.
**Why it happens:** The ratings feel obvious to people inside the industry.
**Instead:** Two factors and one piece of evidence per force; the scorer warns when either is missing.

### Scores with no moves
**Mistake:** The analysis ends at "unattractive, 12/15".
**Why it happens:** The scoring feels like the work.
**Instead:** Turn each dominant force into a move with an owner, and refresh the analysis every 12-18 months.

## Scope & Limitations

**In Scope:**
- Industry analysis across Porter's five forces: new entrants, supplier power, buyer power, substitutes and competitive rivalry, plus complementors as an optional sixth force
- A low, medium or high rating per force from a factor rubric, with evidence
- Identifying the one or two dominant forces and translating each high force into strategic moves
- A scorer that flags unscored forces, thin factors, missing evidence, all-medium ratings and absent strategy implications (`five_forces_scorer.py`)
- Market entry, margin pressure and strategic position engagements

**Out of Scope:**
- Firm-level strengths and weaknesses (see `project-management/strategy-frameworks/swot-analysis/`)
- Choosing among growth bets (see `project-management/strategy-frameworks/ansoff-matrix/`)
- Teardowns of individual competitors (see `business-growth/competitive-teardown/`)
- Market sizing and primary market research (see `research-ops/market-research/`)

**Important Caveats:**
- `five_forces_scorer.py` reads a hand-written JSON file. Intensity ratings, factors and evidence come from the user, and the tool pulls in no market data.
- The analysis is only as sound as the industry definition. Too broad gives generic results, and too narrow misses substitutes.
- Ratings are judgments. Without cited evidence they are opinion.
- Industries change. The skill recommends a refresh every 12-18 months.

## Files

| File | Purpose |
|------|---------|
| `scripts/five_forces_scorer.py` | Five Forces audit and attractiveness band |
| `assets/sample_forces.json` | HR analytics SaaS analysis; exits 0 |
| `assets/sample_forces_flawed.json` | Broad industry, missing force, invalid rating; exits 1 |
| `assets/five_forces_template.md` | Fill-in template |

## Reference Documentation

- [references/five-forces-deep.md](references/five-forces-deep.md): Each force, sub-factors, examples
- [references/five-forces-and-strategy.md](references/five-forces-and-strategy.md): Translating forces into strategic moves

## Related skills

- `project-management/strategy-frameworks/swot-analysis` — firm-level positioning
- `project-management/strategy-frameworks/ansoff-matrix` — growth options
- `project-management/strategy-frameworks/business-model-canvas` — operational view
- `business-growth/competitive-teardown` — competitor-specific analysis
- `c-level-advisor/ceo-advisor` — strategic context
