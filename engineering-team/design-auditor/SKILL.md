---
name: design-auditor
description: Comprehensive UI/UX design audit with 12-category scoring, AI slop detection, WCAG accessibility validation, design system compliance, and automated fix recommendations
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: engineering-team
  domain: design-engineering
  updated: 2026-03-18
  python-tools: design_scorer.py, ai_slop_detector.py, color_contrast_checker.py, design_system_validator.py
  tech-stack: python, css, accessibility, wcag, design-systems
---

# Design Auditor

The most comprehensive design audit skill available for AI coding assistants. Combines systematic 12-category UI/UX evaluation, AI slop detection, WCAG accessibility validation, design system compliance checking, and responsive design auditing into a single unified workflow with three independent grades and prioritized fix recommendations.

## Keywords

design audit, UI review, UX evaluation, accessibility, WCAG, design system, AI slop detection, color contrast, responsive design, usability heuristics, interaction states, visual hierarchy, typography, spacing, motion design, information architecture, design tokens, cross-device testing

## Quick Start

```bash
# 1. Run a full design audit (produces 3 grades)
# Prepare audit findings as JSON, then score:
python scripts/design_scorer.py --input findings.json --output report.json

# 2. Detect AI-generated slop in HTML/CSS
python scripts/ai_slop_detector.py --input page.html --css styles.css

# 3. Check color contrast against WCAG
python scripts/color_contrast_checker.py --foreground "#333333" --background "#ffffff"
python scripts/color_contrast_checker.py --input colors.json --level AAA

# 4. Validate design system compliance
python scripts/design_system_validator.py --tokens tokens.json --input styles.css
```

## Core Workflows

### Workflow 1: Full Design Audit (12-Category Systematic Review)

Execute a top-to-bottom audit across all 12 categories plus overall coherence. Each category is scored 0-10, weighted, and aggregated into a Design Grade (A-F).

**Steps:**

1. **Preparation** — Gather all screens, components, and interaction flows. Identify the design system (if any) and target platforms.
2. **Visual Pass** — Evaluate categories 1-4: Visual Hierarchy, Typography, Color & Contrast, Spacing & Layout Grid.
3. **Interaction Pass** — Evaluate categories 5-6: Interaction States, Navigation & Information Architecture.
4. **Platform Pass** — Evaluate categories 7-8: Responsive Design, Accessibility (WCAG).
5. **Polish Pass** — Evaluate categories 9-10: Motion & Animation, Content & Microcopy.
6. **Integrity Pass** — Evaluate categories 11-12: AI Slop Indicators, Performance as Design.
7. **Coherence Assessment** — Rate overall design coherence across all categories.
8. **Scoring** — Run `design_scorer.py` to compute weighted grades.
9. **Remediation Plan** — Prioritize fixes by severity (Critical > High > Medium > Low > Cosmetic).

```bash
python scripts/design_scorer.py --input audit_findings.json --output full_report.json --verbose
```

### Workflow 2: AI Slop Detection

Identify generic, template-driven, or AI-generated UI patterns that lack intentionality and reduce design quality.

**Steps:**

1. **HTML Analysis** — Scan markup for structural slop patterns (generic hero sections, 3-column grids, cookie-cutter pricing tables).
2. **CSS Analysis** — Detect visual slop (stock gradients, excessive box-shadows, blur overuse, inconsistent spacing values).
3. **Copy Analysis** — Flag generic microcopy, vague CTAs, buzzword density, lorem ipsum residue.
4. **Confidence Scoring** — Each finding gets a confidence score (0.0-1.0) indicating how likely it is AI-generated vs intentional design.
5. **Remediation** — Provide specific suggestions for making each flagged element more intentional.

```bash
python scripts/ai_slop_detector.py --input index.html --css styles.css --threshold 0.6
```

### Workflow 3: Accessibility Compliance Check (WCAG 2.1 AA/AAA)

Systematic validation against WCAG 2.1 success criteria with automated color contrast checking.

**Steps:**

1. **Color Contrast Audit** — Run `color_contrast_checker.py` against all foreground/background combinations.
2. **Semantic Structure** — Verify heading hierarchy, landmark regions, ARIA labels.
3. **Keyboard Navigation** — Validate focus order, skip links, focus indicators.
4. **Screen Reader Compatibility** — Check alt text, form labels, live regions, error announcements.
5. **Motor Accessibility** — Verify touch target sizes (minimum 44x44px), gesture alternatives.
6. **Cognitive Accessibility** — Evaluate reading level, consistent navigation, error prevention.

```bash
python scripts/color_contrast_checker.py --input color_pairs.json --level AA --suggest-fixes
```

### Workflow 4: Design System Compliance

Validate that implementation matches the project's design token definitions.

**Steps:**

1. **Token Extraction** — Load design tokens (colors, spacing, typography, shadows, radii).
2. **CSS Scanning** — Parse stylesheets for hardcoded values that should use tokens.
3. **Deviation Detection** — Flag any value not in the token set.
4. **Compliance Scoring** — Calculate percentage of values using tokens vs hardcoded.
5. **Migration Plan** — Generate token replacement suggestions for each violation.

```bash
python scripts/design_system_validator.py --tokens design-tokens.json --input styles.css --output compliance.json
```

### Workflow 5: Responsive & Cross-Device Audit

Validate design across breakpoints and device categories.

**Steps:**

1. **Breakpoint Analysis** — Verify media query coverage (mobile: 320-480, tablet: 481-1024, desktop: 1025+).
2. **Touch Target Validation** — Ensure interactive elements meet 44x44px minimum on touch devices.
3. **Content Reflow** — Check that content reflows properly without horizontal scrolling at 320px.
4. **Image Responsiveness** — Verify srcset usage, art direction, lazy loading.
5. **Typography Scaling** — Check fluid typography or appropriate size adjustments per breakpoint.
6. **Navigation Patterns** — Validate mobile navigation patterns (hamburger, bottom nav, etc.).

## Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `design_scorer.py` | Score audit findings across 12 categories, generate 3 grades | Audit JSON | Scored report JSON |
| `ai_slop_detector.py` | Detect AI-generated UI patterns in HTML/CSS | HTML + CSS files | Findings JSON |
| `color_contrast_checker.py` | WCAG color contrast validation | Color pairs | Pass/fail + suggestions |
| `design_system_validator.py` | Design token compliance checking | Tokens + CSS | Compliance report |

## 12 Audit Categories

### 1. Visual Hierarchy & Composition (Weight: 10%)

Evaluate how effectively the design guides the user's eye through content.

- **Primary focal point** — Is there a clear visual entry point on each screen?
- **Z-pattern / F-pattern** — Does content flow match established reading patterns?
- **Size contrast** — Do important elements have sufficient size differentiation?
- **Whitespace usage** — Is negative space used intentionally to create groupings?
- **Visual weight balance** — Is the composition balanced or intentionally asymmetric?

### 2. Typography System (Weight: 8%)

Assess typographic consistency, hierarchy, and readability.

- **Type scale** — Is there a consistent modular scale (e.g., 1.25, 1.333, 1.5)?
- **Heading hierarchy** — H1 > H2 > H3 clearly differentiated in size and weight?
- **Body readability** — Line height 1.4-1.6, line length 45-75 characters?
- **Font pairing** — Maximum 2-3 font families with clear roles?
- **Responsive typography** — Font sizes adapt appropriately across breakpoints?

### 3. Color & Contrast (Weight: 8%)

Validate color system integrity and accessibility compliance.

- **Color palette** — Defined primary, secondary, neutral, semantic (error/warning/success/info)?
- **Contrast ratios** — All text meets WCAG AA minimum (4.5:1 normal, 3:1 large)?
- **Color independence** — Information not conveyed by color alone?
- **Dark mode** — If applicable, proper color inversion with maintained contrast?
- **Color consistency** — Same semantic meaning for same colors throughout?

### 4. Spacing & Layout Grid (Weight: 8%)

Assess spatial consistency and grid system usage.

- **Spacing scale** — Consistent spacing values (4px/8px base or similar)?
- **Grid system** — Defined column grid with consistent gutters?
- **Component spacing** — Consistent internal padding and external margins?
- **Alignment** — Elements aligned to grid or intentionally offset?
- **Density balance** — Appropriate information density for the context?

### 5. Interaction States (Weight: 10%)

Validate completeness of interactive element states.

- **Default** — Clear affordance that element is interactive
- **Hover** — Visual feedback on cursor hover (desktop)
- **Focus** — Visible focus indicator for keyboard navigation
- **Active/Pressed** — Feedback during click/tap
- **Disabled** — Clearly non-interactive appearance with reduced opacity
- **Loading** — Skeleton screens, spinners, or progress indicators
- **Error** — Clear error state with actionable messaging
- **Empty** — Meaningful empty states with guidance
- **Success** — Confirmation feedback after successful actions

### 6. Navigation & Information Architecture (Weight: 8%)

Evaluate wayfinding and content organization.

- **Navigation clarity** — User always knows where they are and can get where they need
- **Breadcrumbs/indicators** — Current location visible in navigation hierarchy
- **Menu organization** — Logical grouping with 7-plus-or-minus-2 items per level
- **Search** — Available and functional when content volume warrants it
- **Deep linking** — Key content reachable within 3 clicks/taps

### 7. Responsive Design (Weight: 8%)

Validate cross-device adaptation quality.

- **Breakpoint coverage** — Smooth transitions at mobile/tablet/desktop breakpoints
- **Content priority** — Most important content visible without scrolling on mobile
- **Touch targets** — Minimum 44x44px on touch devices with 8px gaps
- **Orientation** — Layouts work in both portrait and landscape
- **No horizontal scroll** — Content contained at 320px minimum width

### 8. Accessibility — WCAG (Weight: 12%)

Comprehensive accessibility validation (highest weight category).

- **Perceivable** — Alt text, captions, sufficient contrast, text resizing
- **Operable** — Keyboard accessible, sufficient time, no seizure triggers, navigable
- **Understandable** — Readable, predictable, input assistance
- **Robust** — Compatible with assistive technologies, valid markup
- **ARIA usage** — Correct roles, states, and properties when needed
- **Focus management** — Logical focus order, focus trapping in modals

### 9. Motion & Animation (Weight: 5%)

Assess animation quality and appropriateness.

- **Purpose** — Animations serve functional purpose (feedback, orientation, guidance)
- **Performance** — Animations use GPU-accelerated properties (transform, opacity)
- **Duration** — Appropriate timing (100-300ms for micro-interactions, 300-500ms for transitions)
- **Easing** — Natural easing curves, no linear animations for UI elements
- **Reduced motion** — Respects prefers-reduced-motion media query

### 10. Content & Microcopy (Weight: 5%)

Evaluate written content quality within the UI.

- **Button labels** — Action-oriented, specific (not "Submit" or "Click Here")
- **Error messages** — Explain what happened and how to fix it
- **Empty states** — Guide users toward productive action
- **Tooltips/help** — Contextual without overwhelming
- **Consistency** — Same terminology throughout (not "delete" in one place, "remove" in another)

### 11. AI Slop Indicators (Weight: 8%)

Detect patterns suggesting generic AI-generated design without human refinement.

- **Generic hero sections** — Full-width hero with centered text over stock gradient
- **Stock gradient backgrounds** — Linear gradients with trending color combinations (purple-to-blue, etc.)
- **3-column feature grids** — Icon + heading + paragraph repeated exactly 3 times
- **Meaningless illustrations** — Abstract SVG decorations with no semantic connection
- **Cookie-cutter pricing tables** — 3-tier layout with highlighted "recommended" plan
- **Generic testimonial layouts** — Circular avatar + quote + name/title in a carousel
- **Over-use of shadows/blur** — Excessive drop shadows and backdrop blur on every element
- **Inconsistent icon styles** — Mixed icon sets (some outlined, some filled, different weights)
- **Lorem ipsum residue** — Placeholder text or suspiciously generic content
- **Template section ordering** — Hero > Features > Testimonials > Pricing > CTA > Footer

### 12. Performance as Design (Weight: 5%)

Evaluate how performance impacts the design experience.

- **Perceived performance** — Skeleton screens, optimistic UI, progressive loading
- **Image optimization** — Proper formats (WebP/AVIF), sizing, lazy loading
- **Font loading** — FOUT/FOIT strategy, font-display property
- **Layout stability** — No Cumulative Layout Shift (CLS) from late-loading elements
- **Interaction responsiveness** — UI responds within 100ms of user action

### Overall Coherence Bonus (Weight: 5%)

- **Design unity** — All elements feel like they belong to the same design system
- **Brand alignment** — Design reflects brand personality and values
- **Consistency** — Patterns learned in one area apply throughout
- **Polish level** — Attention to detail in edge cases and transitions

## Scoring System

### Three Independent Grades

Unlike single-grade systems, the Design Auditor produces **three separate grades** for comprehensive evaluation:

#### 1. Design Grade (A-F)

Weighted aggregate of all 12 categories plus coherence bonus.

| Grade | Score Range | Meaning |
|-------|------------|---------|
| A+ | 95-100 | Exceptional — production-ready, sets new standards |
| A | 90-94 | Excellent — minor polish items only |
| B+ | 85-89 | Very Good — few notable issues |
| B | 80-84 | Good — solid foundation with improvement areas |
| C+ | 75-79 | Adequate — functional but needs refinement |
| C | 70-74 | Below Average — multiple issues need attention |
| D | 60-69 | Poor — significant problems across categories |
| F | 0-59 | Failing — fundamental redesign needed |

#### 2. AI Slop Grade (A-F)

Based on AI Slop Indicators category (inverted — fewer slop patterns = higher grade).

| Grade | Meaning |
|-------|---------|
| A | Highly original — no detectable AI patterns |
| B | Mostly original — 1-2 minor patterns detected |
| C | Mixed — several AI patterns present but customized |
| D | Heavily templated — many generic AI patterns |
| F | Pure slop — design appears entirely AI-generated without refinement |

#### 3. Accessibility Grade (A-F)

Based on WCAG compliance level achieved.

| Grade | Meaning |
|-------|---------|
| A+ | AAA compliant — exceeds all requirements |
| A | AA compliant — meets all standard requirements |
| B | Mostly AA — 1-3 minor violations |
| C | Partial AA — several violations, core content accessible |
| D | Significant gaps — multiple barriers to access |
| F | Inaccessible — fundamental accessibility failures |

## AI Slop Detection Patterns

### Visual Slop

| Pattern | Description | Confidence |
|---------|-------------|------------|
| Generic hero section | Full-width hero, centered heading, subtitle, CTA over gradient/image | 0.7-0.9 |
| Stock gradient | Linear gradient with trending colors (purple-blue, pink-orange) | 0.5-0.8 |
| 3-column feature grid | Exactly 3 columns: icon + heading + paragraph | 0.6-0.8 |
| Shadow overuse | box-shadow on > 60% of card/container elements | 0.5-0.7 |
| Blur overuse | backdrop-filter: blur on multiple overlapping elements | 0.5-0.7 |
| Rounded everything | border-radius > 12px on most elements | 0.4-0.6 |

### Copy Slop

| Pattern | Description | Confidence |
|---------|-------------|------------|
| Vague CTAs | "Get Started", "Learn More", "Try It Free" without context | 0.5-0.7 |
| Buzzword density | "Seamless", "Powerful", "Revolutionary", "Next-gen" clustering | 0.6-0.8 |
| Generic testimonials | Vague praise without specific product/feature references | 0.6-0.8 |
| Lorem ipsum residue | Placeholder text fragments or suspiciously uniform paragraph lengths | 0.8-1.0 |

### Structural Slop

| Pattern | Description | Confidence |
|---------|-------------|------------|
| Template ordering | Hero > Features > Social Proof > Pricing > CTA > Footer | 0.5-0.7 |
| Cookie-cutter pricing | 3 tiers, middle highlighted, feature checkmark lists | 0.6-0.8 |
| Predictable footer | 4-column footer with Newsletter, Social, Links, Legal | 0.4-0.6 |

## Design Philosophy & Taste Anchors

These 10 principles are not optional guidelines — they are the audit's operating system. Every finding is evaluated against them.

1. **Specificity over vibes** — "Clean UI" is banned. Name the font, the spacing scale, the color system. If you cannot name it, it is not a design decision.
2. **Empty states are features** — "No items found" is a bug. Empty states guide users to their first action, explain what will appear, and build confidence.
3. **Subtraction default** — As little design as possible, but not less. Every element must earn its place. When in doubt, remove it. (Dieter Rams)
4. **Edge cases are user experiences** — 47-character names, zero search results, slow networks, stale state. These are not exceptions — they are the product for some users, every time.
5. **Four shadow paths** — For every interaction, test: happy path, nil input, empty input, error upstream. If any path produces a blank screen or unhandled state, that is a Critical finding.
6. **Loading states earn trust** — Skeleton screens > spinners > blank pages. Progressive disclosure of content signals responsiveness even before data arrives.
7. **Consistency compounds** — One off-system color erodes the entire design language. Design tokens are contracts, not suggestions. Every deviation is a finding.
8. **Motion has meaning** — Every animation must communicate state change (enter, exit, reorder, feedback). Decorative motion without purpose is noise — and noise is a finding.
9. **Accessibility is not a feature** — It is a baseline. WCAG AA is the floor, not the ceiling. Accessibility findings are never "Low" priority.
10. **Performance is perceived design** — A 3-second load feels broken regardless of visual quality. LCP, CLS, and INP are design metrics.

---

## Interaction Model & Safety Controls

### Fix Session Rules
- **One issue = one question** — never batch multiple design issues into a single prompt. Each finding is evaluated and addressed independently.
- **AUTO-FIX (no confirmation):** Cosmetic issues — spacing token mismatches, off-system colors swapped to nearest token, minor border-radius corrections
- **ASK (requires confirmation):** Structural issues — layout changes, component swaps, new patterns, navigation restructuring
- **Maximum 30 fixes per session** — hard stop. After 30 fixes, generate report and exit.
- **Risk accumulator** — component file changes (+5 risk), global style changes (+8), layout changes (+10), reverts (+15). **Stop if cumulative risk exceeds 20%** of budget (100).
- **Revert on regression** — if a fix breaks existing visual tests or introduces a new Critical finding, immediately `git revert` and flag for manual review.

---

## Tool Input/Output Documentation

### design_scorer.py — Expected Input Format

```json
{
  "categories": {
    "visual_hierarchy": {
      "score": 7.5,
      "findings": [
        {
          "description": "Homepage lacks clear visual entry point",
          "priority": "high",
          "fix": "Establish single primary focal point using size contrast",
          "impact": 7
        }
      ]
    },
    "typography": { "score": 8.0, "findings": [...] },
    "color_contrast": { "score": 6.5, "findings": [...] },
    "spacing_layout": { "score": 7.0, "findings": [...] },
    "interaction_states": { "score": 5.0, "findings": [...] },
    "navigation_ia": { "score": 7.5, "findings": [...] },
    "responsive": { "score": 6.0, "findings": [...] },
    "accessibility": { "score": 5.0, "findings": [...] },
    "motion_animation": { "score": 8.0, "findings": [...] },
    "content_microcopy": { "score": 7.0, "findings": [...] },
    "ai_slop": { "score": 6.0, "findings": [...] },
    "performance_design": { "score": 7.5, "findings": [...] }
  }
}
```

### design_scorer.py — Output

```
Design Grade:         D (67.2/100)
AI Slop Grade:        C (6.0/10)
Accessibility Grade:  C (5.0/10)

Category Breakdown:
  Visual Hierarchy      10%   7.5/10   1 finding
  Typography             8%   8.0/10   1 finding
  Color & Contrast       8%   6.5/10   2 findings
  Spacing & Layout       8%   7.0/10   1 finding
  Interaction States    10%   5.0/10   3 findings  ← attention
  Navigation & IA        8%   7.5/10   0 findings
  Responsive             8%   6.0/10   2 findings
  Accessibility         12%   5.0/10   4 findings  ← attention
  Motion & Animation     5%   8.0/10   0 findings
  Content & Microcopy    5%   7.0/10   1 finding
  AI Slop Indicators     8%   6.0/10   2 findings
  Performance            5%   7.5/10   1 finding

Recommendations (by impact):
  1. [Critical] Add missing form labels — accessibility
  2. [High] Implement hover/focus/disabled states for all buttons
  3. [High] Fix contrast ratio on secondary text (3.2:1 → 4.5:1)
```

### color_contrast_checker.py — Input/Output

```bash
# Single pair
python scripts/color_contrast_checker.py --fg "#333" --bg "#fff" --level AA

# Batch mode from JSON
python scripts/color_contrast_checker.py --input color-pairs.json --suggest-fixes
```

```json
// color-pairs.json input format
[
  {"foreground": "#666666", "background": "#ffffff", "label": "body text"},
  {"foreground": "#999999", "background": "#f5f5f5", "label": "muted text"}
]
```

### design_system_validator.py — Input

```bash
python scripts/design_system_validator.py --tokens design-tokens.json --input src/styles/
```

```json
// design-tokens.json format
{
  "colors": {"primary": "#1a73e8", "secondary": "#5f6368", "error": "#d93025"},
  "spacing": [0, 4, 8, 12, 16, 24, 32, 48, 64],
  "typography": {"body": "16px", "h1": "32px", "h2": "24px", "h3": "20px"},
  "radii": [0, 4, 8, 16, 9999]
}
```

---

## CI/CD Integration

```yaml
# .github/workflows/design-audit.yml
name: Design Audit Gate
on:
  pull_request:
    paths:
      - '**/*.css'
      - '**/*.scss'
      - '**/*.html'
      - '**/*.tsx'
      - '**/*.vue'
jobs:
  design-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Color Contrast Check
        run: python scripts/color_contrast_checker.py --input color-pairs.json --level AA
      - name: Design System Compliance
        run: |
          python scripts/design_system_validator.py \
            --tokens design-tokens.json \
            --input src/styles/ \
            --format json > compliance.json
          # Fail if compliance below 90%
          python -c "import json; c=json.load(open('compliance.json')); exit(0 if c.get('compliance_percentage',0)>=90 else 1)"
      - name: AI Slop Detection
        run: |
          python scripts/ai_slop_detector.py --input dist/index.html --threshold 0.7 --format json > slop.json
```

---

## Fix Priority System

| Priority | Definition | Response Time | Examples |
|----------|-----------|--------------|---------|
| **Critical** | Breaks core UX, blocks user tasks, accessibility barrier | Immediate | Missing form labels, contrast below 2:1, broken navigation |
| **High** | Degrades experience significantly, affects many users | Before launch | Inconsistent interaction states, poor mobile layout, missing error states |
| **Medium** | Creates inconsistency, affects some users | Next sprint | Off-system colors, spacing violations, minor responsive issues |
| **Low** | Polish and refinement, minor impact | Backlog | Animation timing, icon consistency, microcopy improvements |
| **Cosmetic** | Nice-to-have, no functional impact | Optional | Pixel alignment, hover animation easing, shadow refinement |

## Integration Points

- **Code Review** — Run design auditor alongside code review for frontend PRs
- **CI/CD** — Integrate `color_contrast_checker.py` and `design_system_validator.py` into pipelines
- **Design Handoff** — Use full audit before developer handoff to catch issues early
- **Sprint Review** — Run abbreviated audit (categories 1-8) for sprint demo review
- **Release Gate** — Require minimum B grade for Design and A for Accessibility before release
- **Design System Updates** — Re-run `design_system_validator.py` after token updates

## References

- `references/design_audit_methodology.md` — Systematic audit approach, heuristics, Gestalt principles
- `references/ai_slop_patterns.md` — Comprehensive AI pattern catalog with remediation strategies
- `references/accessibility_checklist.md` — Complete WCAG 2.1 A/AA/AAA checklist

## Assets

- `assets/design_audit_template.md` — Ready-to-use audit report template
- `assets/sample_audit_data.json` — Sample JSON input for Python tools
