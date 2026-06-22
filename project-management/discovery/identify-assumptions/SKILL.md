---
name: identify-assumptions
description: >
  Assumption mapping expert that identifies, categorizes, and prioritizes
  product assumptions across 4-8 risk categories using devil's advocate
  analysis.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-06-15
  python-tools: assumption_tracker.py
  tech-stack: assumption-mapping, risk-matrix, teresa-torres, continuous-discovery
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

Before mapping assumptions, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The decision or idea being mapped** — the specific product bet whose assumptions you surface (without it the map has no subject)
- [ ] **Product type** — new vs existing (determines whether to use the 4 core categories or the full 8-category model)
- [ ] **Impact and confidence basis** — what evidence sets each `impact` (1-10) and `confidence` (high/med/low) (drives `Risk Score = Impact × (1 − Confidence)` and quadrant placement)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python3 scripts/assumption_tracker.py --demo            # built-in sample (8 assumptions)
python3 scripts/assumption_tracker.py input.json        # score & prioritize your assumptions
python3 scripts/assumption_tracker.py input.json --format json
```

Each assumption needs `description`, `category` (`value`/`usability`/`viability`/`feasibility`/`ethics`/`gtm`/`strategy`/`team`), `confidence` (`high`/`medium`/`low`), and `impact` (1-10). Document with `assets/assumption_map_template.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/methodology-and-tools.md](references/methodology-and-tools.md)** — the full 4-8 category tables with examples, the devil's advocate prompts, the 5-phase scoring/quadrant process, `assumption_tracker.py` usage and flags, output formats, troubleshooting, success criteria, and bibliography. Read when mapping or scripting assumptions.
- **[references/assumption-mapping-guide.md](references/assumption-mapping-guide.md)** — deep theory: Torres' four risks and the extended 8-category model with red flags per category, confidence calibration techniques (evidence-based, Five Whys, pre-mortem check), the prioritization matrix with tripwires, and assumption-to-experiment mapping. Read for the underlying framework.
- **[references/red-flags.md](references/red-flags.md)** — anti-patterns (assumption inflation, miscategorization, confidence without evidence) with bad/good examples anchored in Torres' categories. Read before sharing an assumption map.

## Scope & Limitations

**In Scope:** systematic assumption identification using PM/Designer/Engineer devil's advocate perspectives; 8-category risk classification; quantitative scoring with Impact x (1 - Confidence); quadrant classification with suggested validation methods; assumption registry with priority sorting and action plans.

**Out of Scope:** running validation experiments (`brainstorm-experiments/`); product strategy or roadmap decisions (`execution/outcome-roadmap/`); technical feasibility deep-dives (`engineering/` skills); financial modeling for viability (`finance/` skills).

**Important Caveats:** confidence levels map to fixed numeric values (0.8/0.5/0.2) — a simplification of continuous confidence; the "high impact" threshold is 7/10, adjustable for your risk tolerance; assumption mapping works best collaboratively (Product Trio), not solo.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `brainstorm-ideas/` | Receives from | Ideas generated become the subjects whose assumptions are mapped |
| `brainstorm-experiments/` | Feeds into | "Test Now" assumptions become hypotheses for experiment design |
| `pre-mortem/` | Complements | Pre-mortem catches risks that assumption mapping may miss (especially elephants) |
| `execution/create-prd/` | Feeds into | Validated assumptions populate the PRD Assumptions section (Section 7) |
| `execution/brainstorm-okrs/` | Feeds into | Viability assumptions inform OKR key result selection and confidence levels |
| `senior-pm/` | Feeds into | High-impact assumptions feed into portfolio risk registers |
