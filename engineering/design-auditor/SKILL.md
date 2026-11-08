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
  python-tools: design_scorer.py, ai_slop_detector.py, color_contrast_checker.py, design_system_validator.py
  tech-stack: python, css, accessibility, wcag, design-systems
---
# Design Auditor

The agent audits a web UI and reports three independent letter grades (Design, AI Slop, Accessibility) with prioritised findings, and turns the measurable parts (contrast, token compliance, slop patterns) into CI gates. This skill measures and reports; to change the interface, hand the findings to `engineering/interface-refinement`, which has the refinement commands.

## When to Use

- "Audit this design", "score our UI", "is this accessible?", "does this look AI-generated?"
- Checking a palette or a set of color pairs against WCAG AA/AAA.
- Checking CSS against a design-token file, or gating a PR on compliance.
- Tracking a design's grade against a previous audit (baseline).

## Clarify First

Before running the audit, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Audit type:** full design score, AI-slop detection, contrast check, or token compliance (selects `design_scorer.py` vs `ai_slop_detector.py` vs `color_contrast_checker.py` vs `design_system_validator.py`).
- **Input artifacts:** the findings JSON, HTML/CSS, color pairs, or design-token file (the input each tool requires).
- **Conformance level / threshold:** WCAG AA vs AAA, slop confidence threshold, and the minimum passing grade (sets `--level`, `--threshold`, and the gate).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Measure what tools can measure.** Run the contrast checker on the color pairs, the token validator on the CSS, and the slop detector on the HTML/CSS. These are objective and repeatable.
2. **Judge the rest.** Walk the 12 categories in [references/design_audit_methodology.md](references/design_audit_methodology.md) (hierarchy, typography, layout, interaction, copy ...) and write each finding with a priority, an impact and a fix. These judgments are yours: `design_scorer.py` only aggregates the scores and findings you enter, so the Design grade is as good as that input. Say so in the report.
3. **Score** with `design_scorer.py` (optionally `--baseline` from the last audit).
4. **Report** the three grades, the top findings by impact, and the measured results. Accessibility failures are never low priority; WCAG AA is the floor.
5. **Verify** fixes by rerunning the measured checks; they must pass before the grade changes.

The contrast checker implements the WCAG 2.x contrast ratio (1.4.3 text, 1.4.11 non-text UI). It does not check other WCAG 2.2 criteria such as focus appearance, target size or keyboard access, and APCA (the WCAG 3 draft method) gives different results for some pairs; check those by hand or in a browser.

## Quick Start

```bash
python3 scripts/color_contrast_checker.py --input assets/sample_color_pairs.json --level AA --suggest-fixes --format text  # 2 of 4 fail (exit 1)
python3 scripts/design_system_validator.py --tokens assets/sample_tokens.json --input assets/sample_page.css --format text --min-compliance 80   # 10% (exit 1)
python3 scripts/design_system_validator.py --tokens assets/sample_tokens.json --input assets/sample_page_sound.css --min-compliance 80         # 100% (exit 0)
python3 scripts/ai_slop_detector.py --input assets/sample_page.html --css assets/sample_page.css --format text                              # gradient, 3-card grid, stock copy (exit 1)
python3 scripts/design_scorer.py --input assets/sample_audit_data.json --format text --verbose
```

## Tools Overview

| Tool | What it does | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `color_contrast_checker.py` | WCAG contrast ratio per pair (hex, rgb, hsl), AA/AAA, closest passing color | `--fg/--bg` or `--input pairs.json` (`{"pairs": [{label, foreground, background, text_size}]}`), `--level`, `--size normal|large|ui`, `--suggest-fixes` | 0 all pass, 1 a pair fails, 2 bad input |
| `design_system_validator.py` | Hard-coded colors, spacing, font sizes, radii, shadows, z-index, transitions vs tokens; compliance % | `--tokens`, `--input <css|dir>`, `--glob`, `--min-compliance` | 0, 1 below `--min-compliance`, 2 bad input |
| `ai_slop_detector.py` | Visual, copy and structural patterns typical of generated UIs, with confidence and fix | `--input page.html`, `--css`, `--threshold 0-1` | 0 nothing at/above threshold, 1 patterns found, 2 bad input |
| `design_scorer.py` | Aggregate the agent's 12-category scores and findings into the three grades | `--input findings.json`, `--baseline`, `--verbose` | 0, 2 invalid findings file |

All tools take `--format json|text` and `--output <file>`.

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

## Files

- `scripts/` — the four tools above.
- `assets/sample_color_pairs.json`, `assets/sample_tokens.json`, `assets/sample_page.html` + `assets/sample_page.css` (flawed), `assets/sample_page_sound.html` + `assets/sample_page_sound.css` (pass), `assets/sample_audit_data.json` (scorer input), `assets/design_audit_template.md` (report template).

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/audit-workflows-and-operations.md](references/audit-workflows-and-operations.md)** — quick-start commands, tools-overview table, the three workflows (full audit, slop detection, accessibility/token compliance), grade tables, the 10 design principles, fix-session rules, CI/CD integration, anti-patterns, and troubleshooting. Read when running an audit end to end.
- **[references/design_audit_methodology.md](references/design_audit_methodology.md)** — systematic audit approach, heuristic evaluation, Gestalt principles, critique frameworks, and anti-patterns. Read when designing the evaluation pass.
- **[references/ai_slop_patterns.md](references/ai_slop_patterns.md)** — comprehensive catalog of AI-generated UI patterns and remediation guidance. Read when judging originality.
- **[references/accessibility_checklist.md](references/accessibility_checklist.md)** — full WCAG 2.1 Level A/AA/AAA checklist organized by POUR with testing methodology and fixes. Read when auditing accessibility.

## Scope & Limitations

Static audit of web UI (HTML/CSS) and design tokens. It does not render pages in a browser, test layouts at breakpoints, or replace usability research; check responsive behaviour and keyboard flows in a real browser.

Related skills: `engineering/interface-refinement` (apply fixes), `engineering/senior-frontend` (component implementation).
