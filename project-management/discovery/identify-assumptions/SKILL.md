---
name: identify-assumptions
description: >
  Surfaces the assumptions behind a product bet, scores impact against confidence and
  picks the few to test first. Use when an idea feels right but is unproven, the team
  disagrees on risk, or before designing experiments.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-11-08
  python-tools: assumption_tracker.py
  tech-stack: assumption-mapping, risk-matrix, teresa-torres, continuous-discovery
  tags:
    - assumption-mapping
    - risk
    - devils-advocate
    - discovery
---
# Assumption Mapping Expert

## Overview

Systematically identify, categorize, and prioritize the assumptions underlying your product decisions. This skill extends Teresa Torres' four risk categories with four additional categories for new products, and uses a devil's advocate approach from PM, Designer, and Engineer perspectives to surface hidden assumptions.

## Core Capabilities

- **4-8 category risk model** — Value, Usability, Viability, Feasibility (Torres core) plus Ethics, Go-to-Market, Strategy, Team for new products.
- **Devil's advocate surfacing** — adversarial PM, Designer, and Engineer perspectives expose hidden assumptions.
- **Impact x Risk scoring** — `Risk Score = Impact x (1 - Confidence)` ranks what to test first.
- **Quadrant classification** — Test Now / Proceed / Investigate / Defer with category-matched validation methods.
- **Automated tracking** — `assumption_tracker.py` sorts by priority and suggests next actions.

## When to Use

- After ideation, before committing to build.
- When a product decision "feels right" but has not been validated.
- When the team disagrees on risk or priority -- assumptions make disagreements explicit.
- Before designing experiments -- test the riskiest assumptions first.

## Clarify First

Before mapping assumptions, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The decision or idea being mapped:** the specific product bet whose assumptions you surface (without it the map has no subject).
- **Product type:** new vs existing (determines whether to use the 4 core categories or the full 8-category model).
- **Impact and confidence basis:** what evidence sets each `impact` (1-10) and `confidence` (high/med/low) (drives `Risk Score = Impact × (1 − Confidence)` and quadrant placement).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. Settle the Clarify First inputs, then surface assumptions from PM, design and engineering angles (prompts in `references/methodology-and-tools.md`).
2. Rate each with `impact` (1-10) and `confidence`, citing the evidence behind every `high`.
3. Run `assumption_tracker.py`; it ranks by `Risk Score = Impact x (1 - Confidence)` and places each in a quadrant.
4. Done when Test Now holds about 20% of the map, each Test Now item has an owner, a date and a test, and the tool exits 0.

```bash
python3 project-management/discovery/identify-assumptions/scripts/assumption_tracker.py project-management/discovery/identify-assumptions/assets/sample_assumptions.json             # exit 0
python3 project-management/discovery/identify-assumptions/scripts/assumption_tracker.py project-management/discovery/identify-assumptions/assets/sample_assumptions_overloaded.json  # exit 1
python3 project-management/discovery/identify-assumptions/scripts/assumption_tracker.py --demo --format json
```

Each assumption needs `description`, `category` (`value`/`usability`/`viability`/`feasibility`/`ethics`/`gtm`/`strategy`/`team`), `confidence` (`high`/`medium`/`low`), and `impact` (1-10). Confidence maps to fixed values (high 0.8, medium 0.5, low 0.2) and drives every ranking; impact 7+ counts as high. Quadrants: Test Now (high impact, low or medium confidence), Proceed (high impact, high confidence), Investigate (lower impact, low confidence), Defer (the rest). Exit codes: 0 sound map, 1 Test Now holds more than about 20% (round(0.2 x n), minimum 1), 2 bad input. Document with `assets/assumption_map_template.md`.

## Anti-Patterns

### Everything rated risky
**Mistake:** The map lists dozens of assumptions, nearly all high impact and low confidence, so nothing can be tested in order.
**Why it happens:** Rating an assumption low-risk feels like tempting fate.
**Instead:** Keep no more than about 20% of assumptions in the Test Now quadrant. If more land there, re-score `impact` and `confidence` against real evidence until the load-bearing ones stand out.

### Beliefs marked as facts
**Mistake:** "Users want a faster checkout" is rated `high` confidence because "we know this," with no evidence cited.
**Why it happens:** The most dangerous assumptions feel obviously true.
**Instead:** Cite the evidence for every `high` confidence rating. "We know this" is not evidence. Without a source, rate it `low` and let `assumption_tracker.py` rank it.

### Testing the easiest assumption first
**Mistake:** The team tests the assumption with the easiest experiment, not the one the idea depends on most.
**Why it happens:** Hard experiments are uncomfortable, and easy ones give quick wins.
**Instead:** Rank by `Risk Score = Impact x (1 - Confidence)` and test the top three first, even when the experiment is hard. Give each one an owner and a date.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/methodology-and-tools.md](references/methodology-and-tools.md)** — the full 4-8 category tables with examples, the devil's advocate prompts, the 5-phase scoring/quadrant process, `assumption_tracker.py` usage and flags, output formats, troubleshooting, success criteria, and bibliography. Read when mapping or scripting assumptions.
- **[references/assumption-mapping-guide.md](references/assumption-mapping-guide.md)** — deep theory: Torres' four risks and the extended 8-category model with red flags per category, confidence calibration techniques (evidence-based, Five Whys, pre-mortem check), the prioritization matrix with tripwires, and assumption-to-experiment mapping. Read for the underlying framework.
- **[references/red-flags.md](references/red-flags.md)** — anti-patterns (assumption inflation, miscategorization, confidence without evidence) with bad/good examples anchored in Torres' categories. Read before sharing an assumption map.

## Scope & Limitations

**In Scope:** systematic assumption identification using PM/Designer/Engineer devil's advocate perspectives; 8-category risk classification; quantitative scoring with Impact x (1 - Confidence); quadrant classification with suggested validation methods; assumption registry with priority sorting and action plans.

**Out of Scope:** running validation experiments (`brainstorm-experiments/`); product strategy or roadmap decisions (`execution/outcome-roadmap/`); technical feasibility deep-dives (`engineering/` skills); financial modeling for viability (`finance/` skills).

**Important Caveats:** confidence levels map to fixed numeric values (0.8/0.5/0.2) — a simplification of continuous confidence; the "high impact" threshold is 7/10, adjustable for your risk tolerance; assumption mapping works best collaboratively (Product Trio), not solo.

## Files

| File | Purpose |
|------|---------|
| `scripts/assumption_tracker.py` | Risk score, quadrant, suggested test per assumption; Test Now overload gate |
| `assets/sample_assumptions.json`, `assets/sample_assumptions_overloaded.json` | Runnable inputs: balanced map (exit 0) and overloaded map (exit 1) |
| `assets/assumption_map_template.md` | Assumption map to fill in |
| `examples/shared-dashboards-assumption-mapping.md` | Worked example |
| `references/*.md` | See References |
