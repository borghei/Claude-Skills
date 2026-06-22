---
name: design-auditor
description: >
  Audit UI/UX designs for quality, AI-generated slop, and accessibility. Use when reviewing
  designs, detecting slop patterns, validating WCAG compliance, checking design-token
  adherence, or reviewing responsive design across breakpoints.
license: MIT + Commons Clause
metadata:
  version: 2.2.0
  author: borghei
  category: engineering
  domain: design-engineering
  updated: 2026-06-17
  tags: [design-audit, ai-slop, color-contrast, accessibility]
  python-tools: design_scorer.py, ai_slop_detector.py, color_contrast_checker.py, design_system_validator.py
  tech-stack: python, css, accessibility, wcag, design-systems
---
# Design Auditor

Performs systematic 12-category UI/UX audits, detects AI-generated slop patterns, validates WCAG color contrast, and checks design system token compliance. Produces three independent grades: Design (A-F), AI Slop (A-F), and Accessibility (A-F).

## Core Capabilities

- **Full design audit** — score 12 weighted categories in five passes into a Design grade with prioritized recommendations and baseline comparison.
- **AI slop detection** — flag visual, copy, and structural slop in HTML/CSS with confidence scores and per-finding remediation.
- **Accessibility audit** — WCAG color-contrast checking (AA/AAA) with closest-compliant-color suggestions.
- **Design-system compliance** — detect hardcoded colors, spacing, fonts, radii, shadows, z-indices, and transitions that deviate from tokens; report compliance percentage.
- **Three independent grades** — Design (weighted aggregate), AI Slop (inverted), Accessibility (WCAG), each A–F.
- **Operating system** — 10 design principles, fix-session rules with a risk accumulator, and CI/CD gating.

## When to Use

- Reviewing a UI/UX design for quality, originality, and accessibility.
- Detecting AI-generated slop patterns in HTML/CSS.
- Validating WCAG color contrast or design-token adherence.
- Gating deployments or PRs on minimum compliance scores.

## Clarify First

Before running the audit, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Audit type** — full design score, AI-slop detection, contrast check, or token compliance (selects `design_scorer.py` vs `ai_slop_detector.py` vs `color_contrast_checker.py` vs `design_system_validator.py`)
- [ ] **Input artifacts** — the findings JSON, HTML/CSS, color pairs, or design-token file (the input each tool requires)
- [ ] **Conformance level / threshold** — WCAG AA vs AAA, slop confidence threshold, and the minimum passing grade (sets `--level`, `--threshold`, and the gate)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `design_scorer.py` | Score 12-category audit findings into three grades | `python scripts/design_scorer.py --input findings.json --output report.json --verbose` |
| `ai_slop_detector.py` | Detect AI-generated slop in HTML/CSS | `python scripts/ai_slop_detector.py --input page.html --css styles.css --threshold 0.6` |
| `color_contrast_checker.py` | Check WCAG color contrast (single/batch) | `python scripts/color_contrast_checker.py --input color-pairs.json --level AA --suggest-fixes` |
| `design_system_validator.py` | Validate CSS against design tokens | `python scripts/design_system_validator.py --tokens tokens.json --input src/styles/` |

All tools support `--format json|text` and `--output` for file writing.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/audit-workflows-and-operations.md](references/audit-workflows-and-operations.md)** — quick-start commands, tools-overview table, the three workflows (full audit, slop detection, accessibility/token compliance), grade tables, the 10 design principles, fix-session rules, CI/CD integration, anti-patterns, and troubleshooting. Read when running an audit end to end.
- **[references/design_audit_methodology.md](references/design_audit_methodology.md)** — systematic audit approach, heuristic evaluation, Gestalt principles, critique frameworks, and anti-patterns. Read when designing the evaluation pass.
- **[references/ai_slop_patterns.md](references/ai_slop_patterns.md)** — comprehensive catalog of AI-generated UI patterns and remediation guidance. Read when judging originality.
- **[references/accessibility_checklist.md](references/accessibility_checklist.md)** — full WCAG 2.1 Level A/AA/AAA checklist organized by POUR with testing methodology and fixes. Read when auditing accessibility.

## Scope & Limitations

Covers static design quality, AI-slop, WCAG contrast, and design-token compliance auditing for web UI (HTML/CSS). Does not run live browsers, render-test layouts, or replace manual usability research. Accessibility findings are never "Low" priority; WCAG AA is the floor.

## Integration Points

| Skill | Integration |
|-------|-------------|
| `senior-frontend` | Design audit on component library after build |
| `senior-qa` | Accessibility and design regression in QA pipelines |
| `code-reviewer` | Attach audit findings to frontend PR reviews |
| `senior-devops` | Gate deployments on minimum compliance scores |
| `product-team/ux-researcher` | Feed findings into usability research prioritization |

---

**Last Updated:** June 2026
**Version:** 2.2.0
