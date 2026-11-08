---
name: interface-refinement
description: >
  Refine an existing interface with named commands (critique, polish, distill, typeset, colorize ...),
  a product and design context file, and a static detector of generic UI patterns. Use when UI looks
  generic, cluttered or unfinished.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: design-engineering
  updated: 2026-11-08
  tags: [ui-refinement, design-critique, design-review, generic-ui, typography, color, motion, accessibility]
---

# Interface Refinement

A shared vocabulary for improving interfaces that already exist. Each command names one kind of
change (`distill` removes, `typeset` fixes type, `colorize` gives colour a job, `harden` survives
real content), says what it may change and what it must leave alone, and ends with a check that
produces evidence. A context file records the product and its visual system so commands decide
from facts. A static detector finds the patterns that make an interface look assembled from
defaults: side stripes on rounded cards, gradient text, violet-to-cyan gradients, cream page
grounds, eyebrow labels over headings, cards inside cards, chip soup, rows of identical cards,
emoji icons, radial hazes, clip-path blobs, faint grey text, removed focus rings, broken images,
template headlines and vague button labels. Given the context file, it also reports every literal
colour, face, size and radius that has drifted outside the recorded system.

The agent reads the context file and the craft floor before any edit, keeps every change inside
the named target, and never calls a refinement done without the evidence its command reference
asks for: a rerun scan, a contrast ratio, a keyboard pass, screenshots at real widths.

Two rules hold across every command:

- **Refinement preserves.** Identity, behaviour, copy and everything outside the named target stay
  as they are. If the concept itself is wrong, say so and recommend a redesign; do not smuggle one
  into a polish pass.
- **Scope is the contract.** Every edit step lists what changes, what must not be touched, and how
  the result is verified. `command_router.py --plan` refuses plans that skip any of the three.

## When to use this skill

- **"This looks generic / AI-made / like every other SaaS page"** on an existing page or app
- **Critique or audit** a surface before release, with scores and a prioritised fix list
- **A focused pass:** typography, colour and contrast, spacing and hierarchy, motion, UX copy,
  edge cases and focus, responsive adaptation, first-run and empty states
- **"Tone it down" / "make it bolder"** on a named section without restyling the rest
- **Gate a pull request** that touches markup or styles on generic-pattern and quality findings
- **Write or check the project context file** (product brief + design brief) that steers later work
- **Native screens:** platform conformance review for iOS and Android

Use `engineering/design-auditor` for letter grades and landing-page template detection,
`engineering/a11y-audit` for a WCAG scan of alt text, labels and landmarks. To choose a visual
direction or build a new site from nothing, use a design-direction or frontend-build skill; this
one refines what exists.

## Clarify First

The target and its mode change every recommendation. Settle these before editing. When one is
missing or vague and would change the result, ask; when it would not, use a sensible default and
say which one you used.

- **Target:** the file, component or route, and what is out of scope. Refinement edits only the
  named target.
- **Surface mode:** persuade, operate, read or showcase (see `references/surface-modes.md`).
  "Quieter" on a dashboard and on a landing page are different jobs.
- **Context file:** does `interface-context.md` exist and pass the linter? If not, offer `init`
  for anything bigger than a one-line fix; do not block a narrow fix on it.
- **Binding brand decisions:** faces, colours or devices the owner chose on purpose. They override
  detector findings (waive with a reason).
- **Platform:** web, iOS, Android or cross-platform; the web detector does not read native code.

Ask about the two or three inputs that matter most for this request, not the whole list. If the
user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# 1. Scan for generic and quality patterns (exit 1 on findings at or above medium)
python3 engineering/interface-refinement/scripts/ui_slop_detector.py \
  engineering/interface-refinement/assets/sample_ui_flawed.* --format text

# 2. Route the findings to the next commands (exit 1 when access-blocking work exists)
python3 engineering/interface-refinement/scripts/ui_slop_detector.py src/ --format json > detector.json
python3 engineering/interface-refinement/scripts/command_router.py --report detector.json --mode operate

# 3. Validate the refinement plan before editing
python3 engineering/interface-refinement/scripts/command_router.py \
  --plan engineering/interface-refinement/assets/sample_refinement_plan.json

# 4. Check shipped values against the recorded visual system (off-system-* rules, refusals fail)
python3 engineering/interface-refinement/scripts/ui_slop_detector.py src/ \
  --context engineering/interface-refinement/assets/sample_context.md --format text

# 5. Lint the project context file
python3 engineering/interface-refinement/scripts/context_linter.py \
  --input engineering/interface-refinement/assets/sample_context.md
```

## Tools Overview

| Tool | Input | Output | Exit codes |
|------|-------|--------|------------|
| `ui_slop_detector.py` | files or directories (HTML, JSX, TSX, Vue, Svelte, Astro, CSS, SCSS, LESS); optional `--context` | findings with file:line, rule, severity, evidence, fix, owning command; summary by command | 0 clean at `--fail-on`, 1 findings, 2 bad input |
| `command_router.py --report` | detector JSON + mode + platform | 2-3 next commands in triage order, then polish; a plan skeleton | 0 routed, 1 access-blocking work found, 2 bad input |
| `command_router.py --plan` | refinement plan JSON | errors and warnings per step | 0 valid, 1 errors (warnings with `--strict`), 2 malformed |
| `context_linter.py` | `interface-context.md` | errors and warnings by section | 0 pass, 1 errors (warnings with `--strict`), 2 not a context file |
| `ui_rules.py` | `--list [--scope S]` or `--contrast FG BG` | rule catalog, or a WCAG ratio (translucent colours composited over white; pass the opaque ground for dark UIs) | 0 ok / ratio passes, 1 ratio fails, 2 bad colour, scope or catalog |
| `system_checks.py` | `--context` file + files | off-system values only (drift report for `document` and `extract`) | 0 / 1 / 2 |
| `css_checks.py`, `markup_checks.py`, `class_checks.py`, `extra_checks.py` | stylesheets, markup, or one class list | the detector's layers run alone, for debugging a rule | 0 / 1 / 2 |
| `css_parse.py` | one file | the CSS blocks and declarations the detector reads, for debugging a parse | 0 parsed, 2 bad input |

All tools are stdlib-only, offline, deterministic, and support `--format text|json`. Waive a
finding inline with `ui-refine-ignore <rule> -- <reason>`; waivers without a reason are rejected.

## Commands

| Group | Command | Job | Detector rules routed here | Reference |
|-------|---------|-----|----------------------------|-----------|
| Evaluate | `critique` | design review, heuristic scores, 3-5 priority issues | none (judgment) | `references/command-critique.md` |
| Evaluate | `audit` | five-dimension technical score out of 20 | all, as evidence | `references/command-audit.md` |
| Context | `init` | write the product half of the context file | none | `references/command-init.md` |
| Context | `document` | record the shipped visual system | none | `references/command-document.md` |
| Context | `extract` | turn drift into tokens and shared components | off-system-color, off-system-font, off-system-radius, off-system-font-size | `references/command-extract.md` |
| Refine | `polish` | closing pass: states, alignment, browser surfaces | emoji-icon, skipped-heading, buried-raster | `references/command-polish.md` |
| Refine | `distill` | remove what does not earn its place | nested-cards, chip-soup, numbered-section-labels, shape-assembled-illustration | `references/command-distill.md` |
| Refine | `quieter` | lower the volume, keep the point of view | side-stripe-border, glow-shadow, radial-glow, organic-clip-path, hairline-wide-shadow, hard-offset-shadow, repeating-stripes, grid-line-background | `references/command-quieter.md` |
| Refine | `bolder` | raise one flat section with the system's own moves; "all-out" requests too | none (critique only) | `references/command-bolder.md` |
| Refine | `harden` | focus, overflow, i18n, errors, edge content | focus-ring-removed, broken-image | `references/command-harden.md` |
| Refine | `clarify` | labels, headlines, errors, empty states | vague-control-label, vague-headline | `references/command-clarify.md` |
| Enhance | `typeset` | roles, scale, reading comfort, a type decision | gradient-text, kicker-above-heading, italic-serif-display, overused-face, default-font-stack, tiny-text, all-caps-body, oversized-headline, flat-type-hierarchy, tight-body-leading, wide-body-tracking, crushed-tracking, justified-text, everything-bold | `references/command-typeset.md` |
| Enhance | `colorize` | colour roles, contrast, reflex palettes | low-contrast-pair, faint-gray-text, gray-on-color, ai-hue-gradient, cream-ground | `references/command-colorize.md` |
| Enhance | `layout` | lead element, grouping, rhythm, order | identical-card-row, icon-tile-stack, monotonous-spacing | `references/command-layout.md` |
| Enhance | `animate` | motion that explains, reduced-motion paths | missing-reduced-motion, transition-all, layout-property-motion, bounce-easing, decorative-pulse, marquee-scroll, blinking-cursor | `references/command-animate.md` |
| Enhance | `optimize` | no layout jumps, readable before fonts load, smooth motion | image-missing-dimensions, font-display-missing (and the motion rules it shares with animate) | `references/command-optimize.md` |
| Enhance | `adapt` | restructure for phone, tablet, print, email, other platforms | none (audit, critique) | `references/command-adapt.md` |
| Enhance | `onboard` | first run, empty states, time to first value | none (critique) | `references/command-onboard.md` |
| Enhance | `delight` | one considered, product-specific moment | none (owner request) | `references/command-delight.md` |

### Routing

- **No command named:** run the detector, then `command_router.py --report` and offer its two or
  three picks with one-line reasons. Never auto-run; the user confirms the pick.
- **A command named or clearly implied** ("fix the type", "it's too loud"): load that command's
  reference and follow it. If two fit, ask once.
- **A clean scan:** recommend `critique`. The detector proves the floor, not the design.
- **Missing context file:** a narrow fix proceeds on the existing code; offer `init` afterwards.
  Anything wider (a redesign, a new surface, more than a few files) starts with `init`.
- **Native platform:** `critique` and `audit` against `references/native-platforms.md`; skip the
  web detector.

## Workflows

### Workflow 1 — Refine a surface

1. Settle target, mode and scope (Clarify First). Read `interface-context.md` if it exists.
2. Scan the target and the global styles together, so project-level rules (focus-visible,
   reduced motion) see everything:
   ```bash
   python3 engineering/interface-refinement/scripts/ui_slop_detector.py src/pages/invoices.tsx src/styles --format json > detector.json
   ```
3. Route: `command_router.py --report detector.json --mode operate`. Access-blocking work
   (contrast, tiny text, focus, reduced motion) comes first.
4. Write the plan JSON: one step per command with `changes`, `must_not_touch`, `verify`; evaluate
   steps first, `polish` last. Validate it:
   ```bash
   python3 engineering/interface-refinement/scripts/command_router.py --plan plan.json --strict
   ```
5. Read `references/craft-floor.md`, then execute each step from its command reference.
6. Verify each step as its reference says, then rerun the detector on the target:
   ```bash
   python3 engineering/interface-refinement/scripts/ui_slop_detector.py src/pages/invoices.tsx src/styles \
     --context interface-context.md --fail-on advisory
   ```
7. Hand the diff and before/after screenshots to a fresh reviewer for the finish disposition
   (`ship`, `fix`, `rework`, `re-evidence`; see `references/review-protocol.md`).

### Workflow 2 — Critique with isolated assessments

1. Resolve the target to a source path; read the context file; note the mode.
2. Run Assessment A (design review) **before** looking at any detector output. With subagents,
   run A and B in parallel as two subagents using the briefs in `references/review-protocol.md`.
3. Run Assessment B: the detector, with every hit checked against its source line.
4. Synthesize: agreements are strong findings; name detector false positives; keep A's
   judgments that B cannot see.
5. Fill `assets/refinement-report-template.md`. The first line states the method. End with the
   question to the owner; nothing follows it.

### Workflow 3 — Write and lint the context file

1. `init`: interview for the product half (three questions per round at most); write
   `interface-context.md` from `assets/interface-context-template.md`.
2. `document`: extract the visual system from shipped code; record reused values only; never
   canonise a detector finding as a rule. Rescan with `--context interface-context.md`: each
   `off-system-*` hit is a value you missed or drift that `extract` will fold back in.
3. Lint until it passes:
   ```bash
   python3 engineering/interface-refinement/scripts/context_linter.py --input interface-context.md --strict
   ```
4. Put the refusals you agreed on (rule ids) in `### Refusals`. With `--context`, the detector
   raises any refused advisory rule to medium, so it fails the default gate.

### Validation checkpoint before calling a refinement done

- [ ] Plan validated by `command_router.py --plan` with no errors
- [ ] Detector on the target with `--context interface-context.md` exits 0 at `--fail-on medium`; every remaining hit has a waiver with a reason
- [ ] Every contrast pair you touched proven with `ui_rules.py --contrast`
- [ ] Keyboard walk of the primary task with a visible focus ring throughout
- [ ] Screenshots at 360px and 1280px (or each native device class), before and after
- [ ] Diff contains only the named target; no new colours, faces or radii unless approved
- [ ] Context file still passes `context_linter.py`

## Decision frameworks

### Which command first

| Symptom | Command | Confidence |
|---------|---------|------------|
| Contrast, tiny text, focus or reduced-motion findings | the owning command, before anything else | **[PROVEN]** access defects block people; style does not |
| Many findings across five or more commands | `audit`, then plan | **[RECOMMENDED]** a score keeps the pass from fixing corners |
| "Cluttered", nested containers, chip soup | `distill` before `layout` | **[RECOMMENDED]** decide what stays before arranging it |
| "Generic" with a clean scan | `critique` | **[PROVEN]** specificity is a judgment, not a pattern match |
| "Flat" on a persuade page | `bolder` on one named section | **[RECOMMENDED]** amplify, never add primitives |
| Any edit plan | ends with `polish` | **[PROVEN]** the closing pass catches the drift the other passes create |

### When a detector finding is not a defect

**[RECOMMENDED]** Waive, do not fix, when the context file or the owner chose the pattern on
purpose (a print-heritage cream ground, a literal bouncing ball, a brutalist offset shadow, a
bound typeface). Waive one line and one rule, with the evidence in the reason. **[EXPERIMENTAL]**
For a project that refuses a pattern outright, list the rule id under `### Refusals` and gate CI
with `--fail-on advisory --rules <ids>`.

## Anti-Patterns

### Polish as Disguised Redesign
**Mistake:** A "polish" or "quieter" pass that swaps the palette, the face and the layout.
**Why it happens:** The refiner dislikes the current look and the command name feels like permission.
**Instead:** Refinement keeps the identity. If the concept is wrong, say so in a critique and let
the owner decide on a redesign.

### Fixing the Detector Instead of the Design
**Mistake:** Renaming a `card` class or splitting a gradient until the rule stops firing.
**Why it happens:** A green gate is the visible goal; the pattern is still on screen.
**Instead:** Fix what the person sees, or waive with a named reason. Rerun the scan as
verification, never as the objective.

### Anchored Critique
**Mistake:** Reading the detector report first and writing a critique that restates it.
**Why it happens:** Deterministic output feels authoritative and saves effort.
**Instead:** Finish the design review blind, then merge. Hierarchy, specificity and copy tone are
invisible to a static scan.

### Everything Gets Louder
**Mistake:** A `bolder` pass that adds glows, gradients and a new accent colour.
**Why it happens:** Effects are the fastest way to make a section look different.
**Instead:** One decisive move in the system's own vocabulary, then quiet its surroundings. The
plan validator warns on new primitives without approval.

### Canonising the Defect
**Mistake:** Writing the eyebrow label or side stripe found in the code into the context file's
named rules.
**Why it happens:** `document` records what ships, and the defect ships everywhere.
**Instead:** Report it as drift. Named rules describe decisions, not accidents.

## Reference Documentation

- `references/command-*.md` — one file per command: job, mode notes, change, do not touch, steps, verify, hand-off
- `references/surface-modes.md` — persuade, operate, read, showcase; what each mode allows
- `references/craft-floor.md` — checks every edit meets and patterns refused by default
- `references/detector-rules.md` — every rule's signal, precision notes and blind spots
- `references/detector-rules.json` — the catalog data the tools read
- `references/review-protocol.md` — isolated assessments, subagent briefs, heuristics, personas, finish dispositions, waivers
- `references/native-platforms.md` — iOS and Android checks, native audit, idiom translation, evidence capture

## Files

| File | Purpose |
|------|---------|
| `scripts/ui_slop_detector.py` | Entry point: scans paths, runs all layers, waivers, project-level rules, exit gate |
| `scripts/css_parse.py` | Linear CSS reader: comments, SCSS nesting, JSX style objects, styled/css templates (nested ones too) |
| `scripts/css_checks.py` | Declaration rules over the blocks `css_parse.py` reads from stylesheets, style blocks, inline styles and templates |
| `scripts/class_checks.py` | Utility-class rules and the shape predicates (card, chip, icon tile, kicker, bold) |
| `scripts/markup_checks.py` | Structural rules over the element tree |
| `scripts/extra_checks.py` | Effects, image, type-scale and font-loading rules (declaration hook, raw markup, project-level hierarchy) |
| `scripts/system_checks.py` | Reads the context file's visual system; off-system drift; refusal escalation |
| `scripts/ui_rules.py` | Rule catalog loader, colour parsing (hex/rgb/hsl/oklch), WCAG contrast |
| `scripts/command_router.py` | Route findings to commands; validate refinement plans |
| `scripts/context_linter.py` | Lint `interface-context.md` |
| `assets/sample_ui_sound.{html,css,tsx}` | Sound invoice screen: detector exits 0 at `--fail-on advisory`, with or without `--context` |
| `assets/sample_ui_flawed.{html,css,tsx}` | Deliberately generic landing page: all 54 rules fire with `--context assets/sample_context.md` (50 without), exit 1 |
| `assets/sample_detector_report.json` / `_flawed.json` | Detector JSON for the two samples, router input |
| `assets/sample_context.md` / `_flawed.md` | Context file that passes `--strict` / one with 13 errors |
| `assets/sample_refinement_plan.json` / `_flawed.json` | Valid plan / plan breaking every ordering and scope rule |
| `assets/interface-context-template.md` | Blank context file |
| `assets/refinement-report-template.md` | Critique and plan report |

## Integration Points

| Skill | Integration |
|-------|-------------|
| `engineering/design-auditor` | Letter grades and landing-page template slop; run its detector alongside this one |
| `engineering/a11y-audit` | WCAG HTML scan (alt, labels, landmarks) feeding `harden` and `audit` |
| `engineering/senior-frontend` | Implements the plan's steps in the component library |
| `engineering/code-reviewer` | Attach detector JSON and the plan verdict to UI pull requests |

## Scope & Limitations

**In Scope:**
- Refining existing web interfaces through 19 named commands with scope and verification rules
- Static detection of 54 generic-pattern and quality rules in HTML, JSX/TSX, Vue, Svelte, Astro and CSS,
  four of them checking shipped values against the context file's visual system
- Routing findings to commands and validating refinement plans before any edit
- Writing and linting the product + design context file
- Native iOS/Android review guidance (checks, audit dimensions, idiom translation)

**Out of Scope:**
- Choosing a new visual direction or building a site from nothing
- Rendering pages, measuring layout or driving a browser; static source only
- Native code scanning (Swift, Kotlin, Dart)
- Performance measurement (paint timings, bundle size) beyond the static signals `optimize` reads,
  and marketing copy analysis

**Important Caveats:**
- The detector cannot see inherited colours, runtime class names or rendered overflow; a clean
  scan is the floor, not a verdict. Critique covers the rest.
- Generic-family rules are judgments about defaults; the owner's brief can earn any of them back.
- Rows rendered with `.map()` appear once in source, so `identical-card-row` misses them.
- Class names held in variables are invisible; string literals inside `cn()`, `clsx()`, Vue
  `:class` and Svelte `class={...}` are read. Scan the layout or global stylesheet with a page so
  the page ground (light or dark) is known.
- Drift rules read literals only: values behind `var()`, `calc()`, em or named utility classes
  cannot drift as far as the scan knows, so keep tokens as the single source.
