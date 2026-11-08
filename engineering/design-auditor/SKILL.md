---
name: design-auditor
description: >
  Grade a UI (Design, AI-slop and Accessibility, A-F) and gate it in CI: batch WCAG
  contrast, token compliance, slop detection. Use when asked to audit, score or gate a UI;
  to fix one, use interface-refinement.
license: MIT + Commons Clause
metadata:
  version: 2.2.0
  author: borghei
  category: engineering
  domain: design-engineering
  updated: 2026-11-08
  tags: [design-audit, ai-slop, color-contrast, accessibility]
  python-tools: design_scorer.py, ai_slop_detector.py, color_contrast_checker.py, design_system_validator.py, score_model.py, slop_visual_checks.py, slop_content_checks.py, contrast_pairs.py, color_parse.py, css_declarations.py
  tech-stack: python, css, accessibility, wcag, design-systems
---
# Design Auditor

The agent audits a web UI and reports three independent letter grades (Design, AI Slop, Accessibility) with prioritised findings, and turns the measurable parts (contrast, token compliance, slop patterns) into CI gates. This skill measures and reports. It does not edit the interface: to fix what it finds, hand the findings to `engineering/interface-refinement`, which owns the refinement commands and its own pattern detector.

## When to Use

- "Audit this design", "score our UI", "is this accessible?", "does this look AI-generated?"
- Checking a palette or a set of color pairs against WCAG AA/AAA.
- Checking CSS against a design-token file, or gating a PR on compliance.
- Tracking a design's grade against a previous audit (baseline).

Not for: fixing the UI (`engineering/interface-refinement`), choosing a design system from a brief (`product-team/design-direction`), or a full WCAG scan of markup (`engineering/a11y-audit`).

## Clarify First

Before running the audit, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Audit type:** full design score, AI-slop detection, contrast check, or token compliance (selects `design_scorer.py` vs `ai_slop_detector.py` vs `color_contrast_checker.py` vs `design_system_validator.py`).
- **Input artifacts:** the findings JSON, HTML/CSS, color pairs, or design-token file (the input each tool requires).
- **Conformance level / threshold:** WCAG AA vs AAA, slop confidence threshold, and the minimum passing grade (sets `--level`, `--threshold`, and the gate).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Measure what tools can measure.** Run the contrast checker on the color pairs, the token validator on the CSS, and the slop detector on the HTML/CSS. These are objective and repeatable.
2. **Judge the rest.** Walk the 12 categories in [references/design_audit_methodology.md](references/design_audit_methodology.md) (hierarchy, typography, layout, interaction, copy ...) and write each finding with a priority, an impact and a fix. These judgments are yours: `design_scorer.py` only aggregates the scores and findings you enter, so the Design grade is as good as that input. Say so in the report.
3. **Score** with `design_scorer.py` (optionally `--baseline` from the last audit). Check a hand-written findings file first with `score_model.py`.
4. **Report** the three grades, the top findings by impact, and the measured results. **[PROVEN]** Accessibility failures are never low priority; WCAG AA is the floor.
5. **Hand off the fix** to `engineering/interface-refinement` (table below). Token violations are the one mechanical fix: swap in the suggested token.
6. **Verify** by rerunning the measured checks after the fixes land; they must pass before the grade changes. Rescore with `--baseline` set to this audit.

**[PROVEN]** The contrast checker implements the WCAG 2.x contrast ratio (1.4.3 text, 1.4.11 non-text UI). Every other WCAG 2.2 criterion, including the 2.2 additions (focus not obscured, target size, dragging alternatives, accessible authentication), is a by-hand check: run them from [references/accessibility_checklist.md](references/accessibility_checklist.md) (criteria tables plus the manual and assistive-technology passes in its Testing Methodology section) in a real browser, and enter what fails as `accessibility` findings for the scorer. APCA (the WCAG 3 draft method) gives different results for some pairs.

### Hand-off to interface-refinement

The slop detector here grades landing-page templates; it carries no fix rules of its own beyond a one-line hint. Route each finding type to the interface-refinement command that owns the change, and let that skill's detector (`ui_slop_detector.py`) confirm the fix:

| `pattern_type` | interface-refinement command |
|----------------|------------------------------|
| `visual_gradient` | `colorize` |
| `visual_shadow`, `visual_blur` | `quieter` |
| `visual_radius` | `extract` (radius scale as tokens) |
| `visual_icons` | `polish` |
| `structural_hero`, `structural_grid`, `structural_ordering`, `structural_pricing` | `layout` |
| `structural_testimonial` | `clarify` (real names, sources, specifics) |
| `copy_cta`, `copy_buzzwords`, `copy_placeholder` | `clarify` |

**[RECOMMENDED]** When several findings share a cause (a stock template), say so and recommend `critique` first rather than a list of per-property fixes.

## Quick Start

Run from the skill folder (`engineering/design-auditor`):

```bash
python3 scripts/color_contrast_checker.py --input assets/sample_color_pairs.json --level AA --suggest-fixes --format text  # 2 of 4 fail (exit 1)
python3 scripts/color_contrast_checker.py --input assets/sample_color_pairs_sound.json --level AA --format text            # 5 of 5 pass (exit 0)
python3 scripts/design_system_validator.py --tokens assets/sample_tokens.json --input assets/sample_page.css --format text --min-compliance 80   # 10% (exit 1)
python3 scripts/design_system_validator.py --tokens assets/sample_tokens.json --input assets/sample_page_sound.css --min-compliance 80         # 100% (exit 0)
python3 scripts/ai_slop_detector.py --input assets/sample_page.html --css assets/sample_page.css --format text                              # gradient, 3-card grid, stock copy (exit 1)
python3 scripts/ai_slop_detector.py --input assets/sample_page_sound.html --css assets/sample_page_sound.css --format text                  # grade A (exit 0)
python3 scripts/score_model.py --input assets/sample_audit_data.json                                                                       # valid, 67.15/100 (exit 0)
python3 scripts/design_scorer.py --input assets/sample_audit_data.json --format text --verbose                                             # D / C / C (exit 0)
```

## Tools Overview

| Tool | What it does | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `color_contrast_checker.py` | WCAG contrast ratio per pair (hex, rgb, hsl), AA/AAA, closest passing color, grade | `--fg/--bg` or `--input pairs.json` (`{"pairs": [{label, foreground, background, text_size}]}`), `--level`, `--size normal|large|ui`, `--suggest-fixes` | 0 all pass, 1 a pair fails, 2 bad input |
| `design_system_validator.py` | Hard-coded colors, spacing, font sizes, radii, shadows, z-index, transitions vs tokens; compliance % | `--tokens`, `--input <css|dir>`, `--glob`, `--min-compliance` | 0, 1 below `--min-compliance`, 2 bad input |
| `ai_slop_detector.py` | Visual, copy and structural patterns typical of generated landing pages, with confidence; A-F grade | `--input page.html`, `--css`, `--threshold 0-1` | 0 nothing at/above threshold, 1 patterns found, 2 bad input |
| `design_scorer.py` | Aggregate the agent's 12-category scores and findings into the three grades, with trend | `--input findings.json`, `--baseline`, `--verbose` | 0, 2 invalid findings file |
| `score_model.py` | Validate a findings file and show its weighted score | `--input findings.json` | 0 valid, 2 invalid |
| `slop_visual_checks.py`, `slop_content_checks.py` | One layer of the slop detector alone (CSS side; markup and copy side) | `--input`, `--css` | 0 none, 1 findings, 2 bad input |
| `contrast_pairs.py` | One pair with the closest passing foreground and background | `--fg`, `--bg`, `--level`, `--size` | 0 pass, 1 fail, 2 bad colour |
| `color_parse.py` | How a colour string is read; luminance; ratio with `--against` | `--color`, `--against` | 0, 2 bad colour |
| `css_declarations.py` | The declarations and token values the validator reads from one CSS file | `--input`, `--category` | 0, 2 unreadable file |

All tools take `--format json|text`; the four entry points also take `--output <file>`. All are stdlib-only and offline.

## Anti-Patterns

**Mistake:** Presenting the Design grade as an objective measurement.
**Why it happens:** It comes out of a script with a letter on it.
**Instead:** Say which parts were measured (contrast, tokens, slop patterns) and which were judged, and show the evidence for each judged finding.

**Mistake:** Passing contrast on body text and forgetting UI parts.
**Why it happens:** Text pairs are the obvious ones to list.
**Instead:** Include focus rings, borders of inputs, icons and disabled states with `text_size: ui` (3:1).

**Mistake:** Fixing slop findings one property at a time.
**Why it happens:** Each finding has its own fix line.
**Instead:** Slop is usually a missing point of view. Hand the findings to interface-refinement and fix the direction, then rerun the detector.

**Mistake:** Reading a clean slop scan as "the design is good".
**Why it happens:** Grade A looks like a pass.
**Instead:** The detector knows a fixed list of landing-page templates; an app screen or a novel layout can be poor and still score A. Keep the judged categories in the report.

## Files

| File | Purpose |
|------|---------|
| `scripts/color_contrast_checker.py` | Entry point: contrast report and gate |
| `scripts/contrast_pairs.py` | Pair check and closest-passing-colour search |
| `scripts/color_parse.py` | Colour parsing, luminance, ratio |
| `scripts/design_system_validator.py` | Entry point: token compliance report and gate |
| `scripts/css_declarations.py` | CSS declaration parsing, token loading, closest token |
| `scripts/ai_slop_detector.py` | Entry point: slop grade and report |
| `scripts/slop_visual_checks.py` | Gradient, shadow, blur, radius and icon checks; shared finding type |
| `scripts/slop_content_checks.py` | Hero, grid, pricing, testimonial, order and copy checks |
| `scripts/design_scorer.py` | Entry point: three grades, trend, recommendations |
| `scripts/score_model.py` | Findings validation, weighting, grade bands |
| `references/scoring-model.json` | 12 category weights, coherence weight, priorities, grade bands |
| `references/slop-patterns.json` | Slop detector patterns and word lists |
| `references/wcag-contrast.json` | WCAG minimums per level and size; named colours |
| `references/token-categories.json` | CSS properties and extraction regexes per token category |
| `assets/sample_color_pairs.json` | Flawed pairs: muted caption and pale focus ring fail AA (exit 1) |
| `assets/sample_color_pairs_sound.json` | Sound pairs, text and UI parts (exit 0) |
| `assets/sample_tokens.json` | Token file for both CSS samples |
| `assets/sample_page.html`, `assets/sample_page.css` | Flawed page: stock gradient, 3-card grid, buzzwords (slop exit 1, tokens 10%) |
| `assets/sample_page_sound.html`, `assets/sample_page_sound.css` | Sound page (slop exit 0, tokens 100%) |
| `assets/sample_audit_data.json` | Scorer input: 12 categories with findings |
| `assets/design_audit_template.md` | Report template |

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/audit-workflows-and-operations.md](references/audit-workflows-and-operations.md)** — the three workflows (full audit, slop detection, accessibility/token compliance), grade bands, what each slop check looks for, the 10 design principles, the fix hand-off, CI/CD integration, and troubleshooting. Read when running an audit end to end.
- **[references/design_audit_methodology.md](references/design_audit_methodology.md)** — systematic audit approach, heuristic evaluation, Gestalt principles, critique frameworks, and anti-patterns. Read when designing the evaluation pass.
- **[references/ai_slop_patterns.md](references/ai_slop_patterns.md)** — catalog of generated-UI patterns with the signals for each. Read when judging originality.
- **[references/accessibility_checklist.md](references/accessibility_checklist.md)** — WCAG 2.2 Level A/AA/AAA checklist organized by POUR, with the 2.2 additions marked and the by-hand testing passes. Read when auditing accessibility.

## Scope & Limitations

**In Scope:**
- Three letter grades from the agent's 12-category judgment plus measured checks
- WCAG 2.x contrast for text and UI pairs, with the closest passing colour
- Token compliance of CSS/SCSS against a token file
- Landing-page template and stock-copy detection, as a grade and a CI gate

**Out of Scope:**
- Editing the interface or prescribing redesigns; that is interface-refinement's job
- Rendering pages, breakpoints, keyboard and screen-reader passes; do those in a real browser
- Usability research

**Important Caveats:**
- The slop detector is regex-based and tuned to marketing pages; it reads HTML and CSS, not JSX, Vue or Svelte.
- Token compliance proves values match the token file, not that the token file is good.

**Related skills (one job each):**
- `engineering/interface-refinement` — refines an existing UI with named commands; its detector confirms the fix.
- `product-team/design-direction` — chooses the design system (palette, type, tokens) from a brief.
- `engineering/marketing-site-builder` — builds a marketing site and runs its finish gate.
- `engineering/a11y-audit` — scans markup for WCAG issues beyond contrast (alt text, labels, landmarks).
- `product-team/ui-design-system` — designs and documents a component and token system.
- `product-team/product-designer` — UX research, flows and design process.
- `engineering/senior-frontend` — implements components and pages.
