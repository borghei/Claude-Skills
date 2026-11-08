# Design Audit Workflows & Operations

Read this when running an audit end to end: quick-start commands, the three workflows, the design-principles operating system, the fix hand-off, CI/CD wiring, anti-patterns, and troubleshooting.

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

All tools support `--format json|text` and `--output` for file writing. Each entry point has
single-layer helpers for debugging (`score_model.py`, `slop_visual_checks.py`,
`slop_content_checks.py`, `contrast_pairs.py`, `color_parse.py`, `css_declarations.py`); the
weights, patterns, WCAG minimums and token categories are JSON files in `references/`.

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

| Grade | Design (weighted 0-100) | AI Slop (`ai_slop` score 0-10) | Accessibility (`accessibility` score 0-10) |
|-------|----|----|----|
| A+ | >= 95 | n/a | >= 9.5 (AAA-level care) |
| A | 90-94 | >= 9 (no detectable patterns) | 8.5-9.4 (full AA) |
| B+ / B | 85-89 / 80-84 | 7-8.9 (1-2 minor patterns) | 7-8.4 (mostly AA) |
| C+ / C | 75-79 / 70-74 | 5-6.9 (several patterns) | 5-6.9 (partial AA) |
| D | 60-69 | 3-4.9 (heavily templated) | 3-4.9 (significant gaps) |
| F | < 60 | < 3 | < 3 |

The bands live in `references/scoring-model.json`. The Slop and Accessibility grades come from
the scores you enter for those two categories, so set them from the measured results: the
detector's findings and the contrast checker's failures.

**Validation checkpoint:** Release gate requires minimum B Design grade and A Accessibility grade.

## Workflow 2: AI Slop Detection

```bash
python scripts/ai_slop_detector.py --input index.html --css styles.css --threshold 0.6 --format json
```

The detector reports patterns in three categories (patterns in `references/slop-patterns.json`):

**Visual** (`slop_visual_checks.py`):
- Stock gradients (trending purple-blue, pink-orange, stacked gradients), 0.6
- `box-shadow` on more than 40% of rules; more than 3 `backdrop-filter: blur`
- More than 60% of 4+ `border-radius` values at 16px or more
- Mixed icon libraries, or outlined and filled SVGs together

**Structural** (`slop_content_checks.py`):
- Generic hero (hero/banner class plus 2 of: centered text, auto margins, h1 > p > button), 0.8-0.9
- 3-column grid with exactly three icon + heading + paragraph blocks, 0.75
- Cookie-cutter pricing (3 price points, "most popular" badge), 0.5-0.85
- Avatar + quote testimonials, 0.6
- Template order: hero > feature > testimonial > pricing > cta > footer (4+ present, in order), 0.6

**Copy** (`slop_content_checks.py`):
- 3+ stock CTAs ("Get started", "Learn more", "Book a demo" ...)
- Buzzword density above 2% of words on pages over 50 words
- Lorem ipsum, "placeholder", TODO/FIXME/XXX, 0.95

Each finding carries a one-line remediation hint. Treat it as a pointer, not the fix: the fix
step belongs to `engineering/interface-refinement` (see the hand-off table in SKILL.md).

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

Token file format (keys must match the categories in `references/token-categories.json`;
values are compared as CSS strings, so write `"16px"`, not `16`):
```json
{
  "colors": {"primary": "#1a73e8", "secondary": "#5f6368", "error": "#d93025"},
  "spacing": ["4px", "8px", "12px", "16px", "24px", "32px", "48px", "64px"],
  "font_sizes": {"body": "16px", "h1": "32px", "h2": "24px"},
  "border_radii": ["4px", "8px", "16px", "9999px"]
}
```

A category missing from the token file is not checked. When an off-system value sits exactly
between two tokens, the smaller token is suggested.

Detects hardcoded colors, spacing, fonts, radii, shadows, z-indices, and transitions that deviate from tokens. Reports compliance percentage and suggests nearest token for each violation.

**Validation checkpoint:** Token compliance >= 90%. Zero off-system colors in production CSS.

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

## Handing Off the Fix

This skill grades and gates; it does not edit the interface. When the owner wants the findings
fixed:

- Pass the report (top findings, measured failures, the grade you are trying to move) to
  `engineering/interface-refinement`, which runs the named refinement commands with a scoped plan
  and its own detector.
- Off-system token values are the exception that needs no design judgment: replace each with the
  suggested token, then rerun the validator.
- Re-grade only after the fixes land: rerun the measured checks, then rescore with `--baseline`
  set to this audit so the trend shows what moved.

## CI/CD Integration

```yaml
jobs:
  design-checks:
    steps:
      - run: python scripts/color_contrast_checker.py --input color-pairs.json --level AA
      - run: python scripts/design_system_validator.py --tokens tokens.json --input src/styles/ --min-compliance 90
      - run: python scripts/ai_slop_detector.py --input dist/index.html --threshold 0.7 --format json
```

## Anti-Patterns

1. **Scoring categories too high relative to findings** -- if there are 4 accessibility findings, the score should not be 8/10.
2. **Ignoring interaction states** -- every interactive element needs: default, hover, focus, active, disabled, loading, error, empty, success.
3. **Color as sole information carrier** -- information must not be conveyed by color alone.
4. **Skipping edge cases** -- test with long names, empty data, error states, not just the happy path.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `design_scorer.py` exits "Missing category" | Input JSON missing required keys | Ensure all 12 keys present under `categories` |
| Color checker exits 2 on one pair | Unparseable colour | Use hex, `rgb()`, `hsl()`, or named colors; check how it reads with `color_parse.py --color` |
| AI slop detector finds zero on templated page | Threshold too high | Lower `--threshold` to 0.3 |
| Validator reports "No CSS files found" | SCSS not matched | Pass `--glob "*.scss"` |
| Scores seem inflated | Author-provided scores too generous | Re-evaluate each 0-10 score against finding count and severity |
