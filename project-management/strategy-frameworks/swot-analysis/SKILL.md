---
name: swot-analysis
description: >
  Builds and audits an evidence-backed SWOT with TOWS actions for one explicit
  strategic question. Use when assessing a market entry, pivot, competitive
  response or restructure, or as input to annual planning.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: strategy-frameworks
  updated: 2026-11-08
  python-tools: swot_scorer.py
  tech-stack: swot-analysis, strategic-positioning, situation-analysis
  tags:
    - swot
    - strategic-positioning
    - competitive-analysis
    - strategy
---

# SWOT Analysis

A grounded SWOT answers one strategic question with evidence, then turns the four lists into a few prioritised TOWS moves. The four quadrants are familiar; the value is in the discipline: scope, evidence per item, honest weaknesses, sized opportunities, scored threats and actions.

**Done looks like:** a one-sentence scope; 3-6 items per quadrant, each with its evidence; opportunities with a trigger, window and size; threats with likelihood, severity and mitigation; 2-3 high-priority TOWS actions; `swot_scorer.py` exits 0 and its warnings have been read and either fixed or answered.

## When to Use

- Annual strategic planning input, or a pre-board or pre-fundraise review
- A new market entry, pivot, competitive response or org restructure
- Auditing an existing SWOT that produced no decisions

Use `porters-five-forces` for industry structure, `ansoff-matrix` for growth options, and `business-model-canvas` / `lean-canvas` for the business model itself.

## Clarify First

Before building the SWOT, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Explicit scope/subject:** e.g. "entering market X" or "our position vs Competitor X" (a SWOT for "the company" produces four lists pointing in four directions).
- **Evidence per item:** the data, quote or benchmark behind each entry (strengths must be facts, not aspirations).
- **Reference frame:** who you compare against (strengths and threats are relative).
- **TOWS wanted:** whether to cross-cut into SO/ST/WO/WT moves (it turns the SWOT into options).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Sound SWOT: no findings, exit 0
python3 project-management/strategy-frameworks/swot-analysis/scripts/swot_scorer.py \
  --input project-management/strategy-frameworks/swot-analysis/assets/sample_swot.json --format markdown
```

```bash
# Generic, one-sided SWOT: exit 1 (no weaknesses) plus generic-term and missing-evidence warnings
python3 project-management/strategy-frameworks/swot-analysis/scripts/swot_scorer.py \
  --input project-management/strategy-frameworks/swot-analysis/assets/sample_swot_flawed.json --format markdown
```

```bash
# Input schema and flags
python3 project-management/strategy-frameworks/swot-analysis/scripts/swot_scorer.py --help
```

## Tools Overview

`swot_scorer.py` is the quality gate for this skill. **What the scorer checks:** scope present and specific; an empty quadrant (fail); generic phrases ("great team", "AI", "growing market"); items without evidence; strengths-to-weaknesses asymmetry; opportunities without trigger, window or size; threats without likelihood, severity or mitigation; TOWS present, cells covered and 1-5 high-priority actions. It cannot tell whether an item is internal or external, or whether the evidence is true; you check those.

**Exit codes:** `0` no fail findings (warnings may remain) · `1` at least one fail (an empty quadrant or no scope) · `2` unreadable file, invalid JSON or a top level that is not an object. Output is JSON by default, `--format markdown` for a table, `--output FILE` to write a file.

## Workflow

1. **Scope.** One sentence naming the decision, for example "Acme entering the German mid-market in 2027".
2. **Strengths and weaknesses (internal).** Only what we control. Each needs evidence and a comparison to the alternative the buyer has; a strength no customer cares about is not one. Expect at least three real weaknesses; fewer usually means low candour.
3. **Opportunities and threats (external).** Only what we do not control. Opportunities name the trigger that created them, the window and the size; threats get likelihood and severity (1-5) and a mitigation. Use the internal/external test in `references/swot-framework.md` when an item could sit either side.
4. **TOWS.** Cross the quadrants into SO, ST, WO and WT actions and mark 2-3 as high priority.
5. **Audit.** Write the SWOT as JSON (schema in `--help`; `assets/sample_swot.json` is a complete example) and run the scorer. Fix fails, then read every warning.
6. **Hand off.** The SWOT is input: the high-priority TOWS actions go to prioritisation, resourcing and KPIs.

## Anti-Patterns

### A SWOT for the whole company
**Mistake:** The SWOT has no scope, so each list points somewhere different and nothing follows from it.
**Why it happens:** "Do a SWOT" arrives without a decision attached.
**Instead:** Name the decision first. If nobody can, the SWOT is premature.

### Topics instead of opportunities
**Mistake:** Opportunities read "AI", "globalisation", "market growing".
**Why it happens:** Trends are easy to list and hard to argue with.
**Instead:** Each opportunity names what shifted, the window, the size and why we can win it. If you cannot fill those, it is a trend, not an opportunity.

### A SWOT with no TOWS
**Mistake:** Four tidy lists, no actions; the planning meeting ends where it started.
**Why it happens:** The SWOT is treated as the deliverable.
**Instead:** Cross-cut into TOWS and leave the session with 2-3 high-priority moves and owners.

More failure modes with worked fixes: `references/swot-anti-patterns.md`.

## Files

| File | Purpose |
|------|---------|
| `scripts/swot_scorer.py` | SWOT audit (completeness, evidence, TOWS) |
| `assets/sample_swot.json` | Complete market-entry SWOT; exits 0 |
| `assets/sample_swot_flawed.json` | Generic, one-sided SWOT; exits 1 |
| `assets/swot_template.md` | Fill-in template |

## Reference Documentation

- [references/swot-framework.md](references/swot-framework.md): Categorisation, evidence standards, TOWS, internal/external test, SWOT to strategy
- [references/swot-anti-patterns.md](references/swot-anti-patterns.md): Ten common failures with fixes

## Related skills

- `project-management/strategy-frameworks/porters-five-forces`: competitive dynamics
- `project-management/strategy-frameworks/ansoff-matrix`: growth options
- `project-management/strategy-frameworks/business-model-canvas`: operating model
- `project-management/strategy-frameworks/lean-canvas`: startup view
- `c-level-advisor/ceo-advisor`: strategic context
