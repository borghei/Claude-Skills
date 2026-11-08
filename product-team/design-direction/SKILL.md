---
name: design-direction
description: >
  Turns a product brief into a design-system spec: style direction, contrast-checked
  palette, type pairing, tokens, UX rules and chart choices. Use when starting a new
  product's UI, picking a palette or fonts, or auditing a token file.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: product-team
  domain: design-systems
  updated: 2026-11-08
  tags: [design-system, ui-direction, color-palette, typography, wcag, design-tokens, ux-rules, chart-selection]
---

# Design Direction

Most interface problems are decided before anyone draws a screen: the wrong style for the
audience, a brand colour that fails contrast on every button, three webfonts, a spacing
scale nobody chose. This skill makes those decisions from a written brief, in order, and
shows its working. A recommender maps the product to one of 50 product types, adjusts
for cues in the brief (pre-launch, enterprise buyer, outdoor use, beginners), and from
there picks a style direction, a palette whose contrast is computed in both modes, a type
pairing with roles, spacing/radius/icon/motion tokens, a landing pattern and the core
screens with their section order, a duration per interaction, the UX rules to review
first, and the right chart for each data question. A checker then audits any token file
or CSS theme against the same rules, and a pre-delivery checklist covers what tokens
cannot prove.

The agent never states a contrast ratio it has not computed and never calls a spec
consistent by hand: the tool's verdict and findings go into the deliverable as printed.

## When to use this skill

- **Starting a new product or redesign** and the team needs one agreed direction
  before building screens
- **Choosing a palette or typefaces** for a product type, with the reasoning written down
- **Fitting a brand colour into UI** without it failing contrast on buttons and links
- **Auditing an inherited theme** (CSS custom properties or tokens JSON) before a release
- **Picking a chart** for a dashboard from the question it must answer
- **Structuring a landing page or core screen**: section order, where the primary action
  sits, what evidence the page must carry
- **Setting motion per interaction** (dialogs, toasts, lists, page changes) with the
  reduced-motion replacement for each
- **Final check before handing back built UI** against the pre-delivery checklist
- **Setting the review order** for a design critique: which rules matter most for this product

This skill decides *what* system to use. For building a finished marketing site from the
spec, or for refining an existing interface screen by screen, use a frontend build or
interface-refinement skill; for component APIs and governance, use a design-system
programme skill.

## Inputs the skill expects

- A brief: one sentence on the product and who it is for (required); platform, mode,
  contrast target, brand colour, stack, mood words, a forced direction or type pairing, data questions,
  and directions to avoid (optional). Field list in `references/design-decision-guide.md`.
- For an audit: a tokens JSON file, the recommender's JSON output, or the `.css` files
  that define the theme's custom properties.

## Clarify First

The product type and the audience shape every downstream choice. Settle the inputs below
before producing a spec. When one is missing and would change the result, ask; when it
would not, use the default and say so at the top of the spec.

- **Who uses it, where, and on what device:** decides platform, touch target, density
  and whether low-vision or motion-sensitive defaults apply.
- **Light, dark or both:** `both` doubles the palette work and the contrast checks;
  agree it now, not after the build.
- **Fixed brand inputs:** a brand colour or typeface that cannot change. The tool
  adjusts colours for contrast and reports the shade it used.
- **AA or AAA:** AAA narrows the palette set sharply (5 of 22 bundled palettes pass in
  both modes).
- **What the public page must do:** sell now, collect a waitlist, book a demo, or get an
  app installed. Say it in the brief ("pre-launch", "enterprise", "mobile app"); it
  changes the landing pattern.
- **What the data must answer:** dashboards need questions in plain words ("revenue
  trend over 12 months"), not chart names.

Ask about the two or three that matter most for this request. If the user wants a result
straight away, run quick mode (`--product "..."`) and list the assumed defaults.

## Quick Start

```bash
# 1. Brief -> spec (exit 1 if the brief contradicts itself)
python3 product-team/design-direction/scripts/design_recommender.py \
  --brief product-team/design-direction/assets/sample_brief.json

# 2. Save the spec, then render it as a design-system document and a CSS theme
python3 product-team/design-direction/scripts/design_recommender.py \
  --brief product-team/design-direction/assets/sample_brief.json --format json > spec.json
python3 product-team/design-direction/scripts/spec_renderer.py --spec spec.json --format markdown > DESIGN-SPEC.md
python3 product-team/design-direction/scripts/spec_renderer.py --spec spec.json --format css > theme.css

# 3. Audit a CSS theme: extract its tokens, then check them (exit 1 on critical/high)
python3 product-team/design-direction/scripts/css_token_extractor.py \
  --css product-team/design-direction/assets/sample_theme_flawed.css --format json > tokens.json
python3 product-team/design-direction/scripts/design_spec_checker.py --tokens tokens.json

# 4. Look up rules, charts, palettes, pairings or stack notes
python3 product-team/design-direction/scripts/ux_rules_search.py --query "form errors"
```

## Tools Overview

| Tool | Input | Output | Exit codes |
|------|-------|--------|------------|
| `design_recommender.py` | Brief JSON or `--product` sentence | Spec: product match, applied modifiers, direction, palette with computed contrast per mode, type pairing and scale, spacing/radius/elevation/motion/touch/focus/icon tokens, landing and screen patterns, motion per interaction, prioritised UX rules, charts, stack notes, avoid list, findings, verdict | 0 consistent, 1 conflicts, 2 bad input |
| `spec_renderer.py` | Spec JSON | Markdown design-system document (with page patterns, motion table and delivery blockers), CSS theme (light, dark, reduced motion, focus ring, icon sizes), bare tokens JSON, or text summary | 0 consistent spec, 1 spec carries conflicts (rendered with a banner), 2 not a spec |
| `css_token_extractor.py` | One or more `.css` files (hex, `rgb()`, `hsl()`, bare `H S% L%`, `oklch()`, `color-mix(in srgb)`, `var()` chains, nested `@layer`/`@media`) | Tokens JSON from custom properties: colour roles per mode, declared `color-scheme` modes, type, spacing, radius, motion, touch, focus, plus an `extraction` block of unresolved values | 0 complete, 1 gaps (missing roles, no dark block and no light-only declaration, a colour it cannot read, no spacing/radius/base size), 2 unreadable or no custom properties |
| `design_spec_checker.py` | Tokens JSON or spec JSON (`-` for stdin); or `--palettes` | Findings tied to rule ids with severity, counts per severity; a token that is absent (touch target, focus width) is a `medium` "check by hand", a token that is present and wrong takes the rule's severity | 0 no critical/high, 1 critical/high (any with `--strict`), 2 bad input |
| `ux_rules_search.py` | Query and filters | Ranked rules, charts, stack notes, directions, palettes, pairings, product types, page patterns, motion | 0 results, 1 none, 2 bad arguments |

All five are standalone, stdlib-only, deterministic, offline, and support `--format`
(`text|json`; the renderer `markdown|css|json|text`). Bundled data lives in
`references/*.json`: 50 product types, 10 brief modifiers, 18 directions, 22 palettes
(light and dark), 21 type pairings, 91 UX rules, 22 chart rules, 23 page patterns
(13 landing, 10 screen), 12 motion interactions, 14 stacks, plus token presets.

## Workflows

### Workflow 1 — Brief to spec

1. Write the brief. Copy `assets/sample_brief.json` and replace every field; delete the
   optional fields you have no evidence for rather than guessing.
2. Run the recommender in text mode and read the product match. If the top candidate is
   wrong, or the tool reports `no-match` or `weak-match`, set `product_type` explicitly
   and re-run (always for a brief not written in English). Read
   each `info` finding: it names a modifier the brief triggered and what it changed.
3. Resolve every `fail` finding by changing the brief, not the output:

| Finding | Meaning | Fix in the brief |
|---------|---------|------------------|
| `no-match` | Nothing in the brief matched any product type (vague, or not in English) | Set `product_type`; keyword matching is English-only |
| `direction-conflict` | Both directions excluded or cannot render the mode | Loosen `must_avoid`, change `mode`, or pick another `product_type` |
| `palette-contrast` | No candidate palette reaches the target | Drop to AA, or supply a darker `brand_color` |
| `motion-audience` | Expressive motion for a motion-sensitive audience | Set `motion` to `calm` |
| `stack-platform` | Stack cannot run on the platform | Fix `platform` or `stack` |

Warnings worth a sentence each: `weak-match` (product type is a guess), `unknown-field`
(a misspelt brief key, such as `brand_colour`, that was ignored),
`direction-risk` (a forced direction with high accessibility risk), `brand-adjusted`,
`palette-fallback`, `chart-unmatched`.

4. Each `warn` needs one sentence in the spec: accepted and why, or fixed.
5. Make it the product's own (see "Defaults are a floor" below), by changing the brief
   and re-running, never by editing the output.
6. Render the markdown document and the CSS theme from the saved spec, then fill
   `assets/design-spec-template.md` with the decisions, findings and owners.

```bash
python3 product-team/design-direction/scripts/design_recommender.py --brief brief.json --format json > spec.json
python3 product-team/design-direction/scripts/spec_renderer.py --spec spec.json --format markdown > DESIGN-SPEC.md
python3 product-team/design-direction/scripts/spec_renderer.py --spec spec.json --format css > theme.css
```

The CSS theme declares `color-scheme` for the modes it covers, puts light roles on `:root`
(dark roles there for a dark-only product), dark roles under
`prefers-color-scheme: dark` and `[data-theme="dark"]`, zeroes durations under
`prefers-reduced-motion`, and sets a `:focus-visible` ring from the focus tokens.

### Workflow 2 — Audit a token file or theme

1. Take the theme as it ships. For CSS, extract its tokens first; the extractor exits 1
   and lists each gap (no dark block, missing roles, a colour value it cannot read) that
   would leave the audit partial. Pass every file that defines the theme in cascade order
   (`--css tokens.css theme.css`). A deliberately light-only theme declares
   `color-scheme: light` on `:root`; without it the missing dark block is a gap.
2. Run the checker. Fix every `critical` and `high` finding. Each names the rule, the
   measured value and the threshold; the fix is usually the token, not the component.
3. Re-run until it exits 0, then run with `--strict` and decide on each remaining medium
   or low finding.
4. Review the manual rules (those with `auto: null`) with the product open; a clean token
   audit says nothing about whether components use the tokens.

```bash
python3 product-team/design-direction/scripts/css_token_extractor.py --css theme.css --format json > tokens.json
python3 product-team/design-direction/scripts/design_spec_checker.py --tokens tokens.json --target AA
python3 product-team/design-direction/scripts/design_spec_checker.py --tokens spec.json --strict --format json
```

### Workflow 3 — Structure pages and motion

1. Read `page_patterns` in the spec: one landing pattern (none for internal tools) and two
   or three core screens, each with sections in order, the primary action, the evidence
   it needs, and when not to use it. If the landing is wrong for the stage of the
   product, add the cue to the brief ("pre-launch", "enterprise") rather than swapping
   it by hand.
2. Look up an alternative when a page does not fit:

```bash
python3 product-team/design-direction/scripts/ux_rules_search.py --domain patterns --query "pricing page"
python3 product-team/design-direction/scripts/ux_rules_search.py --domain motion --query "modal"
```

3. Copy the motion table into the build ticket. Each row has one duration for the
   spec's tier, the only properties allowed to animate, and the reduced-motion
   replacement. Calm products have no stagger, scroll reveal or celebration rows on
   purpose.
4. Every section the page needs evidence for (customer quotes, ratings, licences) needs
   a real source before build starts; a placeholder becomes a fake in production.

### Workflow 4 — Pick charts and review order for a dashboard

1. Write each view as a question in plain words.
2. Add them to the brief's `data_questions`, or look each up directly:

```bash
python3 product-team/design-direction/scripts/ux_rules_search.py --domain charts --query "share of revenue by plan"
python3 product-team/design-direction/scripts/ux_rules_search.py --domain rules --category data --min-severity medium
```

3. For each chart, copy its accessible fallback into the dashboard spec.
4. Review in the order in `references/review-and-charts.md`: critical rules first, then
   the product type's priority categories.

### Workflow 5 — Before handing back built UI

1. Re-extract and re-check the shipped theme (Workflow 2); it must exit 0.
2. Walk `references/pre-delivery-checklist.md` on the running build: process, colour,
   type, icons, interaction, motion, layout and states, product-specific items.
3. Mark each line pass, fail or not applicable with a reason. Any failing critical line
   blocks delivery; the rendered spec lists those blockers under "Before delivery".

### Workflow 6 — Extend the bundled data

1. Add the entry to the right `references/*.json` file with original wording; ids are
   lower-case and hyphenated.
2. For palettes, run `design_spec_checker.py --palettes`; every palette must pass AA in
   both modes before it is offered.
3. Page patterns, screens and modifier ids are cross-referenced from `product-types.json`
   and `brief-modifiers.json`; keep `kind` right (`landing` vs `screen`).
4. Run the tools on the sample assets; exit codes must stay 0 / 1 / 2.

### Validation checkpoint before the spec is shared

- [ ] Verdict pasted from the tool, with every finding and its resolution
- [ ] Contrast tables come from the tool output, both modes when mode is `both`
- [ ] Brand colour adjustments shown to the brand owner, original kept for decoration only
- [ ] No more than two webfont families plus a mono
- [ ] Each chart traces to a written data question
- [ ] Token audit exits 0 on the shipped theme
- [ ] Every `info` modifier finding read and accepted, or the brief changed
- [ ] Each landing section that needs evidence has a real source named

## Decision frameworks

### Which direction for which product

| Product family | Default direction | Why |
|----------------|-------------------|-----|
| B2B SaaS, docs, internal tools | **[RECOMMENDED]** Swiss Functional | Type and grid carry hierarchy; nothing competes with the work |
| Admin, analytics, monitoring, logistics | **[PROVEN]** Dense Operational | Many rows, tabular figures, meaningful status colour |
| Banking, insurance, government | **[PROVEN]** Trust Institutional | Predictability reads as safety; flourish reads as risk |
| Patient apps, clinical tools | **[PROVEN]** Clinical Clear | Every state labelled; nothing decorative near critical values |
| Publishing, law, research | **[RECOMMENDED]** Editorial | Reading comfort is the product |
| Luxury, beauty, property | **[RECOMMENDED]** Premium Restraint | Space and imagery signal quality; watch thin-text contrast |
| Retail, marketplaces, delivery | **[PROVEN]** Retail Merchandising | Product image as hero, price near the action |
| Streaming, gaming | **[RECOMMENDED]** Dark Immersive | Artwork carries colour; chrome stays out of the way |
| Kids, habit and language apps | **[RECOMMENDED]** Playful Tactile | Big targets and visible feedback; strict limits on looping motion |
| Developer and security tools | **[RECOMMENDED]** Technical Mono | Keyboard-first, code-adjacent, dark-capable |
| Clinics, trades, local services, dating | **[RECOMMENDED]** Warm Humanist | Real people and plain words; the booking or safety action is never more than one tap away |
| Mobility, utilities, weather | **[RECOMMENDED]** Calm Utility | Used in motion or at a glance: big targets, one job per screen |
| Smart home and device companions | **[RECOMMENDED]** Soft Depth | Tactile controls, but device state is always confirmed in text, never colour alone |

Mood words choose between the product's two directions; `direction` in the brief forces
one. Translucent Layered and Bento Modular are never defaults: they are offered when
asked for, with their risks reported.

The escape hatch: when the audience contradicts the category (a bank for teenagers, a
clinical tool used in the field), choose by audience and record the reason.

### Contrast targets

| Pair | AA minimum | AAA minimum |
|------|-----------|-------------|
| Body and muted text on background or surface | 4.5:1 | 7:1 |
| Text on coloured fills (buttons, badges) | 4.5:1 | 4.5:1 (tool default) |
| Controls, focus ring against background | 3:1 | 3:1 |
| Error and success text on background | 4.5:1 | 4.5:1 |

**[PROVEN]** Check both modes separately. Dark mode is where muted text and brand
colours most often fail.

### Defaults are a floor, not an identity

A spec with no `brand_color`, no `mood` and no `direction` is the product type's safest
answer, and for software that means a neutral sans and a stock blue: correct, accessible
and indistinguishable from its competitors. Before sharing the spec, pull at least two
of these levers and record which:

- **Brand colour.** Pass it as `brand_color`; without it the palette's stock primary ships.
- **Mood words.** Two or three words (`"warm"`, `"precise"`, `"editorial"`) decide between
  the product type's two directions and the pairing that follows.
- **One signature.** Pick one item from the direction's `signatures` list and make it the
  thing people remember (a numbered grid, a display serif on headings only, tabular
  figures as a visual motif). One, used consistently, not three.
- **The type pairing.** When the pairing uses one family for display and body, a pairing
  with a distinctive display face (`ux_rules_search.py --domain pairings`) is the cheapest
  identity there is; set its id as `pairing` in the brief and re-run.

A lever that would break a rule (a thin display face on a low-vision product, a second
accent colour) is not identity, it is a defect; the checker and the checklist still apply.

### Density

**[RECOMMENDED]** Comfortable unless the product is operational (compact) or
reading/luxury/calm (spacious). Compact changes gaps, never hit areas: touch targets stay
at 44px web, 48dp Android.

## Anti-Patterns

### The Mood-Board Spec
**Mistake:** Choosing a style because it looked good on a showcase site, then fitting the
product to it.
**Why it happens:** Showcase images are vivid; briefs are words.
**Instead:** Start from the product type and audience, run the recommender, and only
deviate with a written reason.

### Contrast by Eye
**Mistake:** Approving a palette because it "looks readable" on a calibrated monitor.
**Why it happens:** Designers work on good screens in good light.
**Instead:** Compute every pair in both modes. The tool prints ratios; paste them, do
not paraphrase them.

### The Logo Colour as Button Colour
**Mistake:** Using the brand hex for links and button fills unchanged.
**Why it happens:** Brand guidelines list one primary colour and nothing about UI use.
**Instead:** Pass it as `brand_color`; use the adjusted shade the tool reports for text
and controls and keep the original for large decorative use.

### Dark Mode by Inversion
**Mistake:** Flipping the light palette and calling it dark mode.
**Why it happens:** It is one line of CSS.
**Instead:** Use a palette's own dark roles and check them; the checker flags a theme
with no dark roles unless it declares itself light-only (`modes` or `color-scheme`).

### Font Collecting
**Mistake:** A display face, a body face, a UI face and a mono, each in four weights.
**Why it happens:** Each was added for one screen.
**Instead:** One pairing with roles, two families plus a mono at most. The checker flags
more than three.

### The Borrowed Landing Page
**Mistake:** Reusing a launch-page layout (waitlist, countdown, logo wall) for a product
that is live, or a sales-led page for a product people can just sign up to.
**Why it happens:** The last page that converted becomes the template.
**Instead:** State the page's job in the brief and use the pattern the tool returns; the
pattern's "not when" line says when it misleads.

### One Duration for Everything
**Mistake:** Every transition at 300ms with the same easing, exits as slow as entries.
**Why it happens:** A single `transition: all .3s` is quick to write.
**Instead:** Use the motion table: one duration per interaction, exits faster than
entries, only transform and opacity, and the listed reduced-motion replacement.

### Fixing Output Instead of Brief
**Mistake:** Hand-editing generated tokens to silence a finding.
**Why it happens:** It is faster than re-running.
**Instead:** Change the brief and re-run, so the spec and its reasoning stay in step.

## Reference Documentation

- `references/design-decision-guide.md` — the decision chain, why each default, when to
  override, brief/tokens/CSS formats
- `references/review-and-charts.md` — review order by severity and product priority,
  writing findings, chart choice and chart colour rules
- `references/pre-delivery-checklist.md` — the final pass on built UI, with the
  critical lines that block delivery
- `references/*.json` — the bundled decision data (product types, directions, palettes,
  type pairings, UX rules, charts, stacks)

## Files

| File | Purpose |
|------|---------|
| `scripts/design_recommender.py` | Brief to spec, with findings and verdict |
| `scripts/spec_renderer.py` | Spec to markdown document, CSS theme, tokens JSON or text |
| `scripts/css_token_extractor.py` | CSS custom properties to tokens JSON |
| `scripts/design_spec_checker.py` | Token audit against the rules; bundled palette self-check |
| `scripts/ux_rules_search.py` | Search all bundled data |
| `references/token-presets.json` | Spacing, motion and elevation presets; audience cues |
| `references/product-types.json` | 50 product types with defaults, priorities, risks, landing and screens |
| `references/brief-modifiers.json` | 10 cue-driven adjustments to landing, density, motion, mode, direction |
| `references/page-patterns.json` | 13 landing and 10 screen patterns: sections, primary action, evidence, when not |
| `references/motion.json` | 12 interactions with duration per tier, properties, reduced-motion replacement |
| `references/pre-delivery-checklist.md` | Final pass on built UI |
| `references/directions.json` | 18 style directions with tokens and pitfalls |
| `references/palettes.json` | 22 palettes with light and dark roles |
| `references/type-pairings.json` | 21 pairings with display/body/mono roles |
| `references/ux-rules.json` | 91 rules with severity, platform, check method |
| `references/charts.json` | 22 data questions mapped to charts |
| `references/stacks.json` | 14 stacks with implementation notes |
| `assets/sample_brief.json` | Sound brief: freelancer invoicing SaaS (exit 0) |
| `assets/sample_brief_flawed.json` | Contradictory brief: meditation app (exit 1) |
| `assets/sample_tokens.json` | Sound token file rendered from the sound brief (checker exit 0) |
| `assets/sample_theme.css` | Sound CSS theme rendered from the sound brief (extractor and checker exit 0) |
| `assets/sample_theme_flawed.css` | Flawed inherited theme (extractor exit 1, checker exit 1) |
| `assets/sample_theme_framework.css` | Sound theme in component-library style: bare HSL channels, `oklch`, `color-mix`, `var()` chains, `@layer`, nested `.dark &` (extractor and checker exit 0) |
| `assets/design-spec-template.md` | Decision record and sign-off sheet |

## Scope & Limitations

**In Scope:**
- Product-type matching and a full design-system spec from a brief
- Computed WCAG 2.x contrast for the eleven role pairs that carry text, controls or status, both modes
- Brand colour adjustment to reach contrast
- Static audit of tokens JSON and CSS custom properties
- Landing and screen structure, and motion per interaction
- UX rule, chart, pattern and stack-note lookup
- A manual pre-delivery checklist for built UI

**Out of Scope:**
- Rendering, screenshots or browser-based checks; the checker reads files, it does not
  load pages
- Logos, illustrations, imagery and any generated artwork
- Component APIs, variants and design-system governance
- Brand voice and messaging

**Important Caveats:**
- Contrast uses the WCAG 2.x formula. APCA or WCAG 3 results can differ, especially for
  dark mode and thin type.
- Token checks prove the tokens are sound, not that components use them.
- Type pairings name typefaces; confirm each licence before shipping.
- Product types are defaults, not rules: an unusual audience is a reason to override,
  recorded in the spec.
