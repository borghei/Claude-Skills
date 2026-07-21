---
name: design-system
description: >
  Design tokens, light/dark theming, and WCAG contrast validation for HTML
  documents and decks, compiled into one inlinable CSS bundle. Use when theming
  a report or deck, auditing contrast, or fixing dark-mode color drift.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: markdown-html
  domain: document-theming
  updated: 2026-07-21
  tags: [design-tokens, wcag, contrast, dark-mode, css, typography]
---

# Document Design System

The visual layer for HTML documents and slide decks: a token file in, a single
self-contained CSS bundle out, with every color pairing checked against WCAG
before it ships. This is the theming layer for **documents** — type scales,
reading measure, print roles, light/dark surfaces. It is not a product UI
component library; there are no buttons, form states, or component variants here.

## When to use this skill

- **Theming a report or whitepaper** that must render as one self-contained HTML file
- **Building a deck theme** where type must stay legible at projection distance
- **Auditing an existing palette** before a public or regulated publication
- **Diagnosing dark-mode drift** — text that reads fine in light mode and fails in dark
- **Standardizing across documents** so a series of reports looks like one series
- **Answering "does this pass AA?"** with a number instead of an opinion

## Inputs the skill expects

- A design-token JSON file (or the intent to generate one from `assets/sample_tokens.json`)
- Brand colors, if any exist — a hex value and where it came from
- Typeface choices plus their fallback stacks (self-contained HTML cannot fetch web fonts)
- The conformance target: AA (default) or AAA
- Which artifacts consume the theme: document, deck, or both
- Whether the output will be printed or exported to PDF

## Clarify First

Before generating a theme, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Conformance target (AA vs AAA)** — why it changes the output: AAA at 7:1 rules out most saturated mid-tones, so the accent and warning colors must be picked differently from the start
- [ ] **Print / PDF export required** — why it changes the output: print needs a forced light role set and page-break rules; retrofitting them means re-deriving every dark value
- [ ] **Document or deck** — why it changes the output: the type ratio differs (1.25 vs 1.333) and decks need larger minimum sizes for projection
- [ ] **Existing brand colors** — why it changes the output: a fixed brand hex constrains the accent ramp and may force the underline-links decision

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Generate a themed CSS bundle from tokens

1. Copy `assets/sample_tokens.json` and edit the palette, roles, and scales.
2. Lint the token file first — a malformed ramp produces a valid-looking bundle
   with inverted colors.
3. Compile the bundle and inline the result into the target HTML document.

```bash
python3 markdown-html/design-system/scripts/token_linter.py \
  --input markdown-html/design-system/assets/sample_tokens.json --format text

python3 markdown-html/design-system/scripts/theme_builder.py \
  --input markdown-html/design-system/assets/sample_tokens.json \
  --out build/theme.css --format text
```

### Workflow 2 — Gate a palette on WCAG contrast

1. Declare every real foreground/background combination in the `pairings` block,
   each with its usage class.
2. Run the AA gate; it exits non-zero on any failure, so it drops into CI directly.
3. Run `--all-pairs` to find combinations nobody declared but a stylesheet will
   eventually produce, and `--level AAA --no-gate` as an aspirational report.

```bash
python3 markdown-html/design-system/scripts/contrast_validator.py \
  --input markdown-html/design-system/assets/sample_tokens.json \
  --level AA --format text

python3 markdown-html/design-system/scripts/contrast_validator.py \
  --input markdown-html/design-system/assets/sample_tokens.json \
  --level AAA --no-gate --format json
```

### Workflow 3 — Audit and repair an inherited theme

1. Run the linter to surface structural rot: non-monotonic ramps, roles present
   in one mode only, literal hex values that will not respond to theming.
2. Run the validator with `--all-pairs` to get the full contrast matrix.
3. Fix in this order — ramp order first, then mode parity, then contrast. Ramp
   and parity errors invalidate the contrast numbers, so fixing contrast first
   wastes the work.

`assets/sample_tokens_legacy.json` is a deliberately damaged theme carrying all
four failure classes, so this workflow demonstrates real repair rather than a
clean run. Expect findings from both commands: the linter reports 4 errors and
5 warnings and **exits 2**; the validator is pinned to report-only with
`--no-gate` and finds 13 failing pairings.

```bash
python3 markdown-html/design-system/scripts/token_linter.py \
  --input markdown-html/design-system/assets/sample_tokens_legacy.json \
  --max-severity warning --format json

python3 markdown-html/design-system/scripts/contrast_validator.py \
  --input markdown-html/design-system/assets/sample_tokens_legacy.json \
  --all-pairs --no-gate --format text
```

## Decision frameworks

### Type ratio selection

| Ratio | Name | Use for | Top step of an 8-step scale |
|-------|------|---------|------------------------------|
| 1.125 | Major second | Dense reference docs | 1.8x base |
| 1.200 | Minor third | Technical documentation | 2.5x base |
| **1.250** | **Major third** | **Reports, whitepapers [PROVEN]** | **3.1x base** |
| 1.333 | Perfect fourth | Slide decks [PROVEN] | 4.2x base |
| 1.500 | Perfect fifth | Title treatments only | 8.5x base — unusable in a document |

**Use 1.25 for documents and 1.333 for decks.** A document needs 7-8 usable steps
from caption to H1; at 1.5 the top of that range is 8.5x the base, which no
report can place on a page. Escape hatch: a single-page poster or title card can
use 1.5 because it has one heading and no hierarchy to preserve.

### Contrast usage classes

| Class | Threshold (AA) | Applies to | WCAG criterion |
|-------|----------------|------------|----------------|
| `body` | 4.5:1 | Body copy, captions, footnotes, inline links | 1.4.3 |
| `large` | 3:1 | Text >= 18.66px bold or >= 24px regular | 1.4.3 |
| `ui` | 3:1 | Component boundaries, meaningful graphics | 1.4.11 |
| `decor` | 1.5:1 | Table rules, dividers — losslessly removable | none (practical floor) |

Classify honestly. A border that is the only thing separating two data regions is
`ui`, not `decor`. The 1.5:1 `decor` floor is not a WCAG number — it is the point
below which a rule stops being visible on a mid-quality screen, so it fails at its
decorative job too.

### Contrast targets beyond the minimum

| Element | Gate | Target | Why the target exceeds the gate |
|---------|------|--------|----------------------------------|
| Body text | 4.5:1 | **10-16:1** | Below ~8:1 tires sustained reading; above ~17:1 causes halation on OLED |
| Captions | 4.5:1 | 5.5-8:1 | Must stay subordinate to body yet readable |
| Code text | 4.5:1 | 9-14:1 | Measured against its own tinted surface |
| Focus ring | 3:1 | 3-6:1 | Against both the element and the adjacent background |

**[RECOMMENDED] Do not use pure black on pure white.** 21:1 is the maximum and it
is worse than ~16:1 for extended reading — glyph edges bleed on bright displays,
and readers with astigmatism report the most discomfort at that pairing.

### Dark-mode role derivation

| Light role points at | Dark role points at | Reason |
|----------------------|---------------------|--------|
| neutral 900 (text) | neutral 100 | Read the same ramp from the other end |
| neutral 0 (surface) | neutral 1000 | Not pure black — 1000 leaves room for raised surfaces |
| accent 600 | accent **300** | [PROVEN] Move accents 2-3 steps, not 1 |

Moving an accent only one step is the most common dark-mode bug in this domain:
`accent.600` scores 5.9:1 on white and 3.4:1 on near-black, so it passes the light
gate and fails the dark one.

## Anti-Patterns

### The mode-in-the-name role
**Mistake:** Defining `light-text` and `dark-text` as two separate roles instead of one `text` role with two mode values.
**Why it happens:** It mirrors how the designer thinks — two comps, two palettes — and each role reads unambiguously in isolation.
**Instead:** Keep one semantic role and let `roles.light` and `roles.dark` supply the values. The mode belongs in the mode map, not the name. The linter's parity check enforces this by failing any role defined in only one mode.

### The literal hex escape hatch
**Mistake:** Hard-coding one color directly in a component rule because no existing role quite fits.
**Why it happens:** Adding a role feels like ceremony for a one-off, and the deadline is real.
**Instead:** Add the role or reuse the nearest one. That hard-coded value will not respond to theming and surfaces months later as the single element that stays dark in light mode. The linter flags it as `ROLE_LITERAL` specifically because it is always cheaper to fix on the day it is written.

### Untested dark mode
**Mistake:** Authoring the light theme carefully, mechanically inverting for dark, and never rendering the result.
**Why it happens:** Dark mode looks like a mechanical transform, and the CSS compiles either way.
**Instead:** Run the contrast validator across both modes — it checks every mode in the roles map for exactly this reason — and then actually open the document in dark mode. The failures cluster in the mode nobody looked at, especially in saturated accent and warning colors.

### Trusting a green contrast run
**Mistake:** Treating a passing validator as proof the theme is accessible.
**Why it happens:** The tool gives a number and the number is above the threshold, which feels conclusive.
**Instead:** Read the list of what pairing math cannot see: text over images, semi-transparent overlays, hover and focus states nobody declared, two chart series that both pass against the background but not against each other, and red/green pairs at equal luminance that pass every ratio test and vanish for a deuteranopic reader. Contrast ratio is a luminance metric and is hue-blind by construction.

### The 40-role sprawl
**Mistake:** Adding a role per component — `table-header-bg`, `figure-caption-color`, `toc-link-hover`.
**Why it happens:** Each addition is locally reasonable; no single one looks like a mistake.
**Instead:** Treat roles as a vocabulary, not a mapping table. Eleven roles cover a document; twenty is a smell; forty means the semantic and component layers have merged and the theme can no longer be re-skinned.

## Files

| File | Purpose |
|------|---------|
| `scripts/theme_builder.py` | Compile a token JSON file into one inlinable CSS bundle with light/dark blocks |
| `scripts/contrast_validator.py` | Score every declared pairing against WCAG AA/AAA in both modes; CI gate |
| `scripts/token_linter.py` | Structural audit — scale sanity, ramp monotonicity, mode parity, orphan stops |
| `references/token-architecture.md` | Three-layer token model, role vocabulary, type and spacing scales, dark-mode delivery |
| `references/wcag-contrast-reference.md` | Luminance math, thresholds, exemptions, remediation recipes, blind spots |
| `assets/sample_tokens.json` | Working token file — passes the linter and the AA gate as shipped |
| `assets/sample_tokens_legacy.json` | Deliberately damaged theme for Workflow 3: non-monotonic ramp, mode-parity gap, literal hex, un-re-anchored dark accent |
| `assets/theme_brief_template.md` | Pre-work brief: decisions to settle before writing hex values |

All scripts share one exit-code contract: **0** clean, **2** gate failed (findings at or above the threshold), **1** the tool itself errored. A CI job can therefore tell a real defect from a broken invocation.
