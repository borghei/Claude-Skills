---
name: ui-design-system
description: >
  Generates a design-token system from a brand colour, checks its contrast, and specs
  component variants. Use when turning a chosen colour into tokens, exporting CSS, SCSS or
  JSON, or extending a token set for components.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: product
  domain: design-systems
  updated: 2026-11-08
  tags: [design-system, design-tokens, components, wcag, css-variables, scss, handoff]
---
# UI Design System

The direction is already chosen: there is a brand colour and a style. This skill turns that
into a token system people can build with: a 10-step primary and complementary secondary
scale (50-200 are near-white tints for backgrounds and hover), fixed neutral, semantic and surface colours, a 1.25 modular type scale, an 8pt
spacing grid, component sizes, radius, shadows, motion, breakpoints and z-index. It exports
them as JSON, CSS custom properties or SCSS variables. A checker then computes WCAG contrast
for every pair that carries text and, when the brand hex fails, names the primary shade that
passes. The rest of the skill specs components on top of those tokens and hands them off.

The deliverable states contrast ratios only as the checker printed them. Ratios guessed by
eye are wrong often enough that a pasted number is the only one worth trusting.

## When to use this skill

- **A brand colour is fixed and the team needs tokens** for a new product or a rebrand
- **Exporting tokens** for a stack: CSS variables, Tailwind 4 `@theme`, SCSS, a JS theme
- **Checking whether a brand colour works as button fill and link colour**, and which
  shade to use if it does not
- **Extending an existing generated token set** with component variants, states and sizes
- **Writing the handoff** that maps tokens to components and frameworks

If there is no direction yet (no brand colour, no style, only a product brief), start with
`product-team/design-direction`, which picks the direction. This skill turns that
direction into a working token system.

## Inputs the skill expects

- A brand colour as hex (`#RRGGBB` or `#RGB`) and a style preset: `modern`, `classic` or
  `playful` (fonts, radius and shadow set).
- The target stack, so the export and the integration snippet match it.
- For an existing system: the tokens JSON this generator produced (the checker reads that
  shape; other token files go through `product-team/design-direction`'s checker).

## Clarify First

Settle the inputs below before generating. When one is missing and would change the
result, ask; when it would not, use the default and say so.

- **Brand colour, and whether it is negotiable:** a fixed logo colour that fails contrast
  is kept for decorative use and a darker step carries text. Ask whether the team will
  accept that before presenting it as a fix.
- **Style preset:** decides fonts, radius and shadows. Default `modern`.
- **Stack:** CSS, Tailwind 4, Sass or a JS theme. This decides the export and the snippet.
- **AA or AAA:** AAA fails the brand, muted text and three of the four semantic labels on
  the bundled sample. Agree it before any
  palette work, so nobody reworks the palette after the build.
- **Light only or dark too:** the generator emits a light palette only. Dark mode is a
  separate, checked palette, so it changes the scope of the work.

Ask the two or three that matter for this request. If the user wants tokens straight away,
generate with defaults and put the assumptions at the top.

## Quick Start

Run from the skill folder:

```bash
# Generate tokens (JSON), then check contrast on them
python3 scripts/design_token_generator.py "#0066CC" modern json > /tmp/tokens.json
python3 scripts/token_contrast_checker.py --tokens /tmp/tokens.json

# Bundled samples: sound (exit 0) and flawed (exit 1)
python3 scripts/token_contrast_checker.py --tokens assets/sample_tokens.json
python3 scripts/token_contrast_checker.py --tokens assets/sample_tokens_flawed.json

# Extra pairs a component adds: hover fill with a white label, focus ring at 3:1 (non-text)
python3 scripts/token_contrast_checker.py --tokens assets/sample_tokens.json \
  --pair surface.background:primary.600 --pair primary.DEFAULT:surface.background:3

# Other exports and a summary
python3 scripts/design_token_generator.py "#0066CC" modern css > /tmp/design-tokens.css
python3 scripts/design_token_generator.py "#8B4513" classic scss > /tmp/_design-tokens.scss
python3 scripts/design_token_generator.py "#FF6B6B" playful --format text
```

## Tools Overview

| Script | Input | Output | Exit codes |
|--------|-------|--------|------------|
| `design_token_generator.py` | `brand_color [style] [output]` or `--format text\|json\|css\|scss` | Token system as JSON, CSS, SCSS or a summary | 0 written, 2 bad colour, unknown style or unreadable presets |
| `token_contrast_checker.py` | `--tokens file.json\|-`, `--target AA\|AAA`, `--pair FG:BG[:MIN]` (repeatable), `--format text\|json` | Ratio per text pair, failed pairs, suggested primary shade, verdict | 0 all pass, 1 a pair fails, 2 unreadable or incomplete input |

The checker tests five kinds of pair: body text (foreground on background), muted text
(neutral-500), link text (brand on background), button label (background colour on a brand
fill), and each semantic label (`contrast` on `base`). All use the normal-text threshold
(4.5:1 AA, 7:1 AAA), because button labels and links are normal-size text. `--pair` adds
any other pair, as `#RRGGBB` or a token path such as `primary.600`. The optional third
field sets its own minimum, for example 3 for a focus ring or large text.

## Workflows

### 1. Brand colour to checked tokens

1. Generate JSON for the brand colour and style, and keep that file as the source of truth.
   Regenerate CSS and SCSS from it, never by hand, because the next run overwrites edits.
2. Run the checker at the agreed target and paste its output into the deliverable.
3. If `link text` or `button label` fails, use the shade the checker names for links and
   button fills, and keep the brand hex for large or decorative use. If a semantic or
   surface pair fails in a file someone edited, restore the generated value or pick a
   darker one and re-run.
4. Export the format the stack needs (see `references/developer-handoff.md`).

**Done when:** the checker's verdict is PASS at the agreed target, or each remaining
failure is listed with the reason it was accepted.

### 2. Component specs on the tokens

Define each component's sizes, variants and states only in terms of tokens. A raw hex or
px value in a component is a second source of truth that drifts from the first.

- **Sizes:** `sizing.components.button|input.sm|md|lg` (32/40/48px heights). Keep one
  height scale for every control that sits in the same row.
- **Variants:** primary fills with `primary.DEFAULT`, or the checker's shade. Hover goes
  one step darker. Secondary uses `neutral-100` with `neutral-900` text, and ghost is
  transparent with `neutral-700` text. Do not use `primary.500` as the fill: it is a lighter
  tone than the brand (3.86:1 with white for `#0066CC`).
- **States:** hover, active, `focus-visible` (a 2px outline in a colour at 3:1 against
  the page, never `outline: none`), disabled and loading. List the tokens each state uses.
- **Accessibility per component:** role, keyboard behaviour, accessible name, and a touch
  target of at least 44×44px (pad small controls instead of growing their visuals).

Templates and the token-to-component map are in `references/component-architecture.md`.

**Done when:** every variant and state names its tokens, and every colour pair a component
adds (hover and active fills with their labels, the focus ring, outline and ghost text)
passes the checker via `--pair`.

### 3. Responsive and fluid type

The generator's breakpoints are 480/640/768/1024/1280/1536px (`xs` to `2xl`), and its
type scale is fixed in px. For fluid headings, derive `clamp()` values from the scale's
min and max sizes using the formula in `references/responsive-calculations.md`. Test at
each breakpoint, and at 200% zoom with no horizontal scroll.

### 4. Developer handoff

Ship the JSON plus the stack's export, the checker output, the component specs, and the
integration snippet for the stack (Tailwind 4 `@theme inline`, plain CSS, Sass, JS theme)
from `references/developer-handoff.md`. That file uses the exact names the generator
emits (`--colors-primary-DEFAULT`, `--typography-fontSize-base`, and so on).

## Decision frameworks

| Situation | Do | Why |
|-----------|----|-----|
| Brand hex fails as link or fill | **[PROVEN]** Use the checker's shade for text and fills, and keep the brand hex for decoration | Contrast is arithmetic. A brand guideline cannot make 2.8:1 readable |
| Brand hex passes | **[RECOMMENDED]** Fill with `primary.DEFAULT`, hover with the next darker step | Step 500 is lighter than the brand, so it often fails where the brand passes |
| Team wants AAA | **[RECOMMENDED]** Agree it per surface (body text first), not for every pair | The fixed error and info bases cannot reach 7:1 with any label (error 5.58:1 and info 5.71:1, both on black), so blanket AAA means a new semantic palette |
| Dark mode needed | **[PROVEN]** Build and check a separate palette | Inverted light tokens give wrong elevation and fail contrast unpredictably |
| Style preset does not fit | **[EXPERIMENTAL]** Edit `references/token-presets.json` (fonts, radius, shadows) and re-run | Keeps one source of values. Record the change in the handoff |

## Anti-Patterns

### Primary-500 as the Brand
**Mistake:** Filling buttons with `primary.500` because it is "the middle of the scale".
**Why it happens:** Tailwind-style scales put the brand at 500. This generator puts it in
`DEFAULT` and makes 500 a lighter, less saturated tone.
**Instead:** Fill with `primary.DEFAULT` when the checker passes it, otherwise with the
shade it names.

### Contrast by Eye
**Mistake:** Approving a palette because it looks readable on a good monitor.
**Why it happens:** Designers review on calibrated screens in good light.
**Instead:** Run the checker and paste the ratios. Do not paraphrase them as "accessible".

### Hand-Edited Exports
**Mistake:** Tweaking values in `design-tokens.css` to fix one screen.
**Why it happens:** It is faster than re-running the generator.
**Instead:** Change the brand colour, the style or `references/token-presets.json`, then
regenerate, so JSON, CSS and SCSS stay identical.

### Raw Values in Components
**Mistake:** A component with `#2563EB` or `13px` in its styles.
**Why it happens:** The token did not exist yet, so a raw value went in.
**Instead:** Add the token, then use it. Search component styles for raw hex and px
before handoff.

### Removing the Focus Ring
**Mistake:** `outline: none` with a pale `box-shadow` (or nothing) in its place.
**Why it happens:** The default ring looks unstyled.
**Instead:** A 2px `focus-visible` outline in a colour at 3:1 against the page.
Keyboard users have no other way to see where they are.

## Reference Documentation

- `references/token-generation.md`: how each scale is computed, what the colour steps
  are, type and spacing scales, contrast formula, export shapes
- `references/component-architecture.md`: component hierarchy, naming, props, variant and
  state templates, token-to-component map
- `references/responsive-calculations.md`: breakpoints, fluid type with `clamp()`, grids
- `references/developer-handoff.md`: exports, Tailwind 4, CSS, Sass, JS themes, Style
  Dictionary, Figma, checklist, versioning
- `references/token-presets.json`: every fixed value the generator uses

## Files

| File | Purpose |
|------|---------|
| `scripts/design_token_generator.py` | Brand colour and style to token JSON, CSS, SCSS or summary |
| `scripts/token_contrast_checker.py` | WCAG contrast for text pairs in a tokens JSON, with a suggested primary shade |
| `references/token-presets.json` | Fixed presets: semantic, surface, neutral, fonts, type, spacing, sizing, radius, shadows, motion, breakpoints, z-index |
| `references/*.md` | Knowledge base listed above |
| `assets/sample_tokens.json` | Sound tokens for `#0066CC` modern (checker exit 0) |
| `assets/sample_tokens_flawed.json` | `#FF6B6B` playful with the foreground lightened to `#9CA3AF` (checker exit 1: body text, link text, button label) |

## Scope & Limitations

**In scope:** token generation from a chosen brand colour and style, JSON/CSS/SCSS export,
WCAG 2.x contrast for the text-bearing pairs, component variant and state specs on those
tokens, responsive and handoff guidance.

**Out of scope:** choosing the direction, dark-mode palettes, icons and imagery, Figma
plugin work, rendering or screenshot checks.

**Caveats:** contrast uses the WCAG 2.x formula, and APCA can differ for thin type and dark
surfaces. The checker covers the generator's own pairs, not every pair a component
creates. Font names are suggestions, so confirm licences before shipping.

**Related skills, one job each:**
- `product-team/design-direction` chooses the design system from a brief: style, palette,
  type pairing and tokens. Use it before this skill when there is no brand colour or style yet.
- `product-team/product-designer` handles design critique, journey maps and usability scoring.
- `engineering/marketing-site-builder` builds a marketing site and runs its finish gate.
- `engineering/interface-refinement` refines an existing UI with a detector and commands.
- `engineering/design-auditor` grades a built UI.
- `engineering/a11y-audit` runs the WCAG audit on a running interface, beyond token contrast.
- `engineering/senior-frontend` implements components and state in the frontend codebase.
