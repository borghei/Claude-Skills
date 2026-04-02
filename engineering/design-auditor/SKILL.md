---
name: design-auditor
description: >
  Use when auditing UI/UX designs for quality, detecting AI-generated slop
  patterns, validating WCAG accessibility compliance, checking design system
  token adherence, or reviewing responsive design across breakpoints. Produces
  three independent grades (Design, AI Slop, Accessibility) with prioritized
  fix recommendations.
license: MIT + Commons Clause
metadata:
  version: 2.1.0
  author: borghei
  category: engineering
  domain: design-engineering
  updated: 2026-04-02
  tags: [design-audit, ai-slop, color-contrast, accessibility]
  python-tools: design_scorer.py, ai_slop_detector.py, color_contrast_checker.py, design_system_validator.py
  tech-stack: python, css, accessibility, wcag, design-systems
---
# Design Auditor

The agent performs systematic 12-category UI/UX audits, detects AI-generated slop patterns, validates WCAG color contrast, and checks design system token compliance. Produces three independent grades: Design (A-F), AI Slop (A-F), and Accessibility (A-F).

---

## Quick Start

```bash
# Score a full design audit (12 categories -> 3 grades)
python scripts/design_scorer.py --input findings.json --output report.json --verbose

# Detect AI-generated slop in HTML/CSS
python scripts/ai_slop_detector.py --input page.html --css styles.css --threshold 0.6

# Check color contrast (single pair or batch)
python scripts/color_contrast_checker.py --fg "#333" --bg "#fff" --level AA
python scripts/color_contrast_checker.py --input color-pairs.json --level AAA --suggest-fixes

# Validate design system token compliance
python scripts/design_system_validator.py --tokens tokens.json --input src/styles/
```

## Tools Overview

| Tool | Input | Output |
|------|-------|--------|
| `design_scorer.py` | 12-category audit findings JSON | Three grades, category breakdown, prioritized recommendations |
| `ai_slop_detector.py` | HTML + optional CSS file | Findings with confidence scores (0.0-1.0), slop grade |
| `color_contrast_checker.py` | Color pairs (hex/rgb/hsl/named) | WCAG pass/fail, ratios, compliant color suggestions |
| `design_system_validator.py` | Design tokens JSON + CSS files | Compliance percentage, violations with token suggestions |

All tools support `--format json|text` and `--output` for file writing.

---

## Workflow 1: Full Design Audit

The agent evaluates 12 weighted categories in five passes:

1. **Visual Pass** -- Visual Hierarchy (10%), Typography (8%), Color & Contrast (8%), Spacing & Layout (8%)
2. **Interaction Pass** -- Interaction States (10%), Navigation & IA (8%)
3. **Platform Pass** -- Responsive Design (8%), Accessibility/WCAG (12%)
4. **Polish Pass** -- Motion & Animation (5%), Content & Microcopy (5%)
5. **Integrity Pass** -- AI Slop Indicators (8%), Performance as Design (5%), Coherence Bonus (5%)

```bash
python scripts/design_scorer.py --input audit_findings.json --baseline last_sprint.json --format text --verbose
```

**Three independent grades:**

| Grade | Design (weighted aggregate) | AI Slop (inverted) | Accessibility (WCAG) |
|-------|----|----|----|
| A+ | 95-100 | Highly original | AAA compliant |
| A | 90-94 | No detectable patterns | Full AA compliant |
| B | 80-89 | 1-2 minor patterns | Mostly AA, 1-3 minor violations |
| C | 70-79 | Several AI patterns | Partial AA |
| D | 60-69 | Heavily templated | Significant gaps |
| F | 0-59 | Pure AI-generated slop | Fundamental failures |

**Validation checkpoint:** Release gate requires minimum B Design grade and A Accessibility grade.

---

## Workflow 2: AI Slop Detection

```bash
python scripts/ai_slop_detector.py --input index.html --css styles.css --threshold 0.6 --format json
```

The agent detects patterns across three categories:

**Visual slop** (confidence 0.4-0.9):
- Generic hero section (full-width, centered text, gradient)
- Stock gradients (trending purple-blue, pink-orange)
- 3-column feature grid (icon + heading + paragraph x3)
- Shadow/blur overuse on >60% of containers

**Copy slop** (confidence 0.5-1.0):
- Vague CTAs: "Get Started", "Learn More" without context
- Buzzword clustering: "Seamless", "Powerful", "Revolutionary"
- Lorem ipsum residue or uniform paragraph lengths

**Structural slop** (confidence 0.4-0.8):
- Template ordering: Hero > Features > Social Proof > Pricing > CTA > Footer
- Cookie-cutter pricing (3 tiers, middle highlighted)

Each finding includes a remediation suggestion for making the element more intentional.

---

## Workflow 3: Accessibility & Design System Compliance

**Color contrast audit:**

```bash
python scripts/color_contrast_checker.py --input brand-colors.json --level AA --suggest-fixes --format text
```

Input format:
```json
[
  {"foreground": "#666666", "background": "#ffffff", "label": "body text"},
  {"foreground": "#999999", "background": "#f5f5f5", "label": "muted text"}
]
```

The agent checks against WCAG thresholds (4.5:1 normal text, 3:1 large text) and suggests the closest compliant alternative for failing pairs.

**Design system validation:**

```bash
python scripts/design_system_validator.py --tokens design-tokens.json --input src/styles/ --glob "*.scss"
```

Token file format:
```json
{
  "colors": {"primary": "#1a73e8", "secondary": "#5f6368", "error": "#d93025"},
  "spacing": [0, 4, 8, 12, 16, 24, 32, 48, 64],
  "typography": {"body": "16px", "h1": "32px", "h2": "24px"},
  "radii": [0, 4, 8, 16, 9999]
}
```

Detects hardcoded colors, spacing, fonts, radii, shadows, z-indices, and transitions that deviate from tokens. Reports compliance percentage and suggests nearest token for each violation.

**Validation checkpoint:** Token compliance >= 90%. Zero off-system colors in production CSS.

---

## Design Principles (Audit Operating System)

These 10 principles drive every finding evaluation:

1. **Specificity over vibes** -- "Clean UI" is banned. Name the font, spacing scale, color system.
2. **Empty states are features** -- "No items found" is a bug. Guide users to first action.
3. **Subtraction default** -- every element must earn its place. When in doubt, remove it.
4. **Edge cases are user experiences** -- 47-character names, zero results, slow networks, stale state.
5. **Four shadow paths** -- happy path, nil input, empty input, error upstream. Blank screen = Critical.
6. **Loading states earn trust** -- skeleton screens > spinners > blank pages.
7. **Consistency compounds** -- one off-system color erodes the entire design language. Tokens are contracts.
8. **Motion has meaning** -- decorative animation without purpose is noise.
9. **Accessibility is baseline** -- WCAG AA is the floor. Accessibility findings are never "Low" priority.
10. **Performance is perceived design** -- 3-second load feels broken regardless of visual quality.

---

## Fix Session Rules

- **One issue = one question** -- never batch multiple findings.
- **AUTO-FIX**: Cosmetic -- spacing token mismatches, off-system colors to nearest token.
- **ASK**: Structural -- layout changes, component swaps, navigation restructuring.
- **Max 30 fixes per session.** Hard stop, then generate report.
- **Risk accumulator**: component (+5), global style (+8), layout (+10), revert (+15). Stop at 20% of budget.
- **Revert on regression** -- if fix breaks visual tests or introduces Critical finding, `git revert` immediately.

---

## CI/CD Integration

```yaml
jobs:
  design-checks:
    steps:
      - run: python scripts/color_contrast_checker.py --input color-pairs.json --level AA
      - run: |
          python scripts/design_system_validator.py --tokens tokens.json --input src/styles/ --format json > compliance.json
          python -c "import json; exit(0 if json.load(open('compliance.json')).get('compliance_percentage',0)>=90 else 1)"
      - run: python scripts/ai_slop_detector.py --input dist/index.html --threshold 0.7 --format json
```

---

## Anti-Patterns

1. **Scoring categories too high relative to findings** -- if there are 4 accessibility findings, the score should not be 8/10.
2. **Ignoring interaction states** -- every interactive element needs: default, hover, focus, active, disabled, loading, error, empty, success.
3. **Color as sole information carrier** -- information must not be conveyed by color alone.
4. **Skipping edge cases** -- test with long names, empty data, error states, not just the happy path.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `design_scorer.py` exits "Missing category" | Input JSON missing required keys | Ensure all 12 keys present under `categories` |
| Color checker rejects value | Unsupported format | Use hex, `rgb()`, `hsl()`, or named colors |
| AI slop detector finds zero on templated page | Threshold too high | Lower `--threshold` to 0.3 |
| Validator reports "No CSS files found" | SCSS not matched | Pass `--glob "*.scss"` |
| Scores seem inflated | Author-provided scores too generous | Re-evaluate each 0-10 score against finding count and severity |

---

## References

| Guide | Path |
|-------|------|
| Audit Methodology | `references/design_audit_methodology.md` |
| AI Slop Patterns Catalog | `references/ai_slop_patterns.md` |
| WCAG 2.1 Checklist | `references/accessibility_checklist.md` |

---

## Integration Points

| Skill | Integration |
|-------|-------------|
| `senior-frontend` | Design audit on component library after build |
| `senior-qa` | Accessibility and design regression in QA pipelines |
| `code-reviewer` | Attach audit findings to frontend PR reviews |
| `senior-devops` | Gate deployments on minimum compliance scores |
| `product-team/ux-researcher` | Feed findings into usability research prioritization |

---

**Last Updated:** April 2026
**Version:** 2.1.0
