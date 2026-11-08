---
name: marketing-site-builder
description: >
  Build company, product and landing sites that do not look generic: one system, plain copy,
  real imagery, restrained motion, a static finish gate. Use when building, restyling or
  reviewing a marketing site, or a page reads as templated.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: frontend
  updated: 2026-11-08
  tags: [frontend, web-design, landing-page, copywriting, design-system, performance, motion]
---

# Marketing Site Builder

Build the website a good company would ship: it says plainly what is sold, shows the real thing on
every screen, and looks made for this client rather than assembled from a template. The method is
fixed in order. Decide the kind of business first, because it decides what the page may show and how
much may move. Write the copy from facts before any layout. Plan the page as a list of screens. Build
on one system of tokens. Then run the finish gate (six static checkers behind one verdict line,
with written waivers and a three-round limit) and a short browser checklist, fix, and report what is
still open.

Most generic pages fail in the same three places: copy that would fit any business, a stylesheet with
a dozen ad-hoc spacings, radii and colours, and decoration (gradients, glass, scroll reveals) standing
where the product should be. The agent catches those from source with the gate, the rest on screenshots.

## When to Use

- **Building a marketing, company or product site** as static HTML/CSS or inside an existing
  React, Next.js, Vue, Svelte or Astro project
- **Restyling or reviewing a page** that someone says looks generic, templated or "AI-made"
- **Writing or cleaning up website copy** before it goes into markup
- **Adding a finish gate** to a site build so copy, consistency and weight are checked before handover
- **Deciding how much motion and effect** a page may carry for its kind of business

## Clarify First

What most shapes the page is the kind of business and the real material on hand. Settle the inputs
below before producing anything. When one is missing or vague and would change the result, ask about
it; when it wouldn't, use a sensible default and say which one you used.

- **The kind and what is sold:** tech, product, service or place decides the effect budget, the
  photograph count and the hero; a wrong kind puts a shader on a bakery.
- **The main action:** the one transaction (Book a room, Start a free trial) sets the button
  wording in the nav, hero and close; a page with three equal actions has none.
- **The real material:** client photographs, screenshots, prices, address and hours decide which
  sections can exist; nothing missing is invented.
- **The stack:** static files or an existing framework decides where tokens live and which built
  CSS the consistency check reads.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user
wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# One verdict over all six checkers: the sound sample ends on GATE: PASS (exit 0)
python3 engineering/marketing-site-builder/scripts/finish_gate.py engineering/marketing-site-builder/assets/sound_page.html

# The deliberately flawed sample fails every checker (exit 1); run one alone for its full list
python3 engineering/marketing-site-builder/scripts/finish_gate.py engineering/marketing-site-builder/assets/flawed_page.html
python3 engineering/marketing-site-builder/scripts/access_links_check.py engineering/marketing-site-builder/assets/flawed_page.html --format json
```

## Workflow

### Step 1 — Decide the kind [PROVEN]

Write the kind on the plan's first line and on the page as `<html data-kind="...">`.

| Kind | Examples | Leads with | Effects |
|---|---|---|---|
| `tech` | SaaS, AI and developer tools, fintech apps, games, hardware | The real interface as live HTML, or the device photographed | One per page |
| `product` | Furniture, bikes, food sold online, cosmetics | The product whole and large, a new view each section | None |
| `service` | Clinics, law firms, agencies, studios, trades | The people, the rooms, the finished work | None |
| `place` | Cafes, bakeries, guesthouses, shops, gyms | The room, the counter, the goods; two or more photographs per screen | None |

A maker that also opens its door is a place. When unsure between product and service, ask what the
buyer takes home: a thing is a product, an outcome is a service.

### Step 2 — Write the copy first, from facts [PROVEN]

1. Fill the fact sheet in `assets/site-plan-template.md` from the brief, word for word where possible.
   Empty fields stay empty; their sections shrink or go.
2. Pick one register for the voice card (`references/copy-voice-and-tells.md`, section 2). Never the
   default warm-wry-literary voice unless the client asks for it.
3. Write every line under the five rules: the h1 names the category and the buyer or place in 2 to 8
   words; one hard fact on the first screen; a noun in every heading; buttons as verb plus object;
   at most two hero actions, each with one wording everywhere.
4. Shape the page from the reader's questions; write the microcopy in the same register
   (`references/copy-voice-and-tells.md`, sections 2 and 5).
5. Lint the draft before any markup exists, words first, then devices:

```bash
python3 engineering/marketing-site-builder/scripts/copy_lint.py draft.md
python3 engineering/marketing-site-builder/scripts/copy_devices.py draft.md
```

Validation checkpoint: both exit 0, and the draft passes the outside reads (a rival's name in the
h1 and headings, read as the client, a fresh reader where a subagent is available;
`references/copy-voice-and-tells.md`, section 8).

### Step 3 — Plan the page as screens [RECOMMENDED]

One line per section in the plan: its id, its one idea, its picture and that picture's kind
(object, use, parts, people, place, interface, diagram, type, slot), its height (one screen or two
at 1440x900) and any motion with its purpose. A section with no picture and under half a screen of
content merges into the one above. Five to nine sections for a landing page; long copy goes to
sub-pages.

- The product or hero object leads the hero and at most two more sections; three object lines at most.
- No card layout more than twice, never the same layout in neighbouring sections; two picture-less
  sections never side by side.
- Every asset the brief names (trailer, screenshots, CAD) gets a finished-looking slot with a stand-in.

Rhythm rules: `references/one-system-and-rhythm.md`, section 3; content rules:
`references/sections-cards-forms.md`, section 1.

### Step 4 — Set one system [PROVEN]

Define tokens on `:root` before any rule: a spacing scale on a 4px grid, two to four radii, a
near-black ink, a muted text colour, two or three grounds, one hairline, one accent, two font
families, one button pair. Use `var(--token)` everywhere. Take the accent from the client's
material, set headlines by size and tracking rather than weight, keep everything at 13px or more and
reading text at 16px. Defaults and the reasons behind them: `references/one-system-and-rhythm.md`,
sections 1 and 2.

### Step 5 — Build [RECOMMENDED]

- Every section is a direct child of `main`, opens with its h2, and uses the one `.wrap` so all edges
  line up.
- Photographs: the client's first, stand-ins listed for replacement, library stock only in detail
  slots; alt, width and height on every image, the hero eager, the rest lazy
  (`references/imagery-motion-effects.md`, section 2).
- Motion in three layers only: the hero's entrance once, one or two moments in their own sections,
  the hover and press layer. No scroll reveals. A reduced-motion rule on every page that moves.
- Effects only on tech, one per page, with a still fallback.
- Cards two levels deep at most; labelled forms that really send; every control named, every link
  landing; no carousel or popup (`references/sections-cards-forms.md`).

### Step 6 — Run the finish gate [PROVEN]

```bash
python3 engineering/marketing-site-builder/scripts/finish_gate.py index.html --kind product \
  --css dist/assets/app.css --state .site-gate.json
```

Fix every FAIL; fix each WARN or keep it and say why. Waive a false FAIL in `site-waivers.json`
with its reason (five at most). Then read screenshots at 1440, 1024, 820x1180, 768x1024 and 390
against the browser checklist (`references/finish-gate.md`, section 2).

Validation checkpoint: the last line is `GATE: PASS`, `GATE: OPEN` after the third round (stop and
report), or `GATE: DONE` when the user said to stop (`--done "<their words>"`).

### Step 7 — Report

The `GATE:` line first, then every waiver and open FAIL, the kind and voice card, every assumed fact
(`data-assumed`), stand-in photograph and client-asset slot, the form's stand-in address, and the
browser checks not yet run (`references/finish-gate.md`, section 4).

## Decision Frameworks

### How much may move

| Layer | tech | product, service | place |
|---|---|---|---|
| Hero entrance on load | Yes | Yes | Yes |
| Moments in their own section | 1 or 2 | 1 or 2, led by photographs or type | 1 or 2, led by photographs or type |
| Hover and press layer | Yes | Yes | Yes |
| Card loops, counters, one timed loop | Yes | No | No |
| Shader, canvas, WebGL, gradient grounds, glass | One effect | No | No |
| Scroll reveals, parallax on text, scroll-jacking | Never | Never | Never |

### When a check fires

| Finding | First move |
|---|---|
| `hype-word`, `stock-phrase` | Replace with the fact from the fact sheet; if there is none, cut the line |
| `vague-cta` | Name the transaction: verb plus what the visitor gets |
| Spacing or radius over budget | Map every off-scale value to the nearest token; delete the leftovers |
| Colour or accent hues over budget | Collapse greys into ink, muted and hairline; keep one accent |
| `effects` on a non-tech page | Replace the effect with the photograph it was standing in for |
| `img-lazy`, `img-dims` | Add `loading="lazy"` below the hero and real dimensions everywhere |
| `reduced-motion` | Add the media query that rests every transition and animation |
| `stat-strip`, `testimonials`, `apology-note` | Each number in its sentence; only the brief's quotes; real material or no element |
| `a11y-name`, `field-label`, `form-action` | Name the control; a visible label; a real endpoint or a listed mailto stand-in |
| `anchor-target`, `label-target`, `main-action` | An id that exists; one wording per target; the hero's action repeated word for word |
| `violet`, `default-face`, `heavy-weight` | Accent from the client's material; a pairing with a reason; size and tracking, not bold |
| `contrast-pair`, `tiny-text`, `small-body` | 4.5:1; nothing under 13px; reading text 16px |
| `no-css`, `kind-missing` | Pass the built stylesheet with `--css`; write `<html data-kind>` or pass `--kind` |
| `checker-gaming` | Remove the headless test; the page behaves the same for every visitor |

## Anti-Patterns

### The Template Section Stack
**Mistake:** Every section built as eyebrow label, claim heading, short lede, three icon cards, with
a strip of three round figures under the hero.
**Why it happens:** It is the shape that fits any business, so it is what templates and generators
produce first, and it looks finished at a glance.
**Instead:** Shape sections from the reader's questions (what is it, what does it cost, where, how
does it work, why trust it) and the material on hand. A section with nothing true to say goes.

### Synonym Swapping
**Mistake:** Replacing "seamless" with "smooth" and "empower" with "help" to clear the linter.
**Why it happens:** The linter reports words, so the quickest fix looks like a word change.
**Instead:** Replace the claim with the fact it stood for: the number of setup steps, the failure
case handled, the figure from the brief. If there is no fact, delete the sentence.

### Decoration in Place of the Subject
**Mistake:** A gradient mesh, a glass panel or a particle field in the hero of a law firm or a cafe.
**Why it happens:** Effects make an empty page look busy, and the real photographs are not ready yet.
**Instead:** Effects are a tech-only budget of one. On every other kind, the hero is a photograph of
the work. Without client photographs, use listed stand-ins of the same subject and say so in the report.

### Raising the Budget to Pass
**Mistake:** Bumping `radius_values` to 8 in the budget file because the page uses eight radii.
**Why it happens:** The budget file is editable and the deadline is close.
**Instead:** Collapse the values to the system first. Change a budget only for a documented system
reason, in the project's own copy of the file, and say so in the report.

### Stock Scroll Reveals
**Mistake:** Every card fading up as it scrolls into view, from a reveal library.
**Why it happens:** It is a one-line install that makes a static page feel alive.
**Instead:** Content stands at rest. Spend motion on the hero entrance, one moment in its own
section and a hover layer that answers every pointer.

### Gaming the Checker
**Mistake:** Hiding content from a headless browser, splitting a banned word with a tag, or a vague
waiver to turn the gate green.
**Why it happens:** The gate counts rounds, and red on the third feels like failure.
**Instead:** Fix the page or waive one finding with a real reason. `GATE: OPEN` with an honest list is
a valid ending; `checker-gaming` cannot be waived.

### Invented Proof
**Mistake:** "Trusted by 10,000+ teams", three polished testimonials and a logo wall, none from the brief.
**Why it happens:** Social proof sections are in every template, and an empty one looks unfinished.
**Instead:** Only proof the client gives, quoted exactly. Without it, a line of plain facts (price,
hours, a count the brief states) or nothing.

## Files

### Tools Overview

| Script | Purpose | Exit codes |
|---|---|---|
| `scripts/copy_lint.py` | Copy tells with line numbers: hype words, stock lines, residue, vague CTAs, device tics over budget (virtue words, contrast frames, -ing riders, fragment headings), em dash, exclamation and emoji overuse, proof figures, default-cast names, footer sign-offs, stale year. HTML, Markdown or text | 0 clean, 1 FAIL (WARN with `--strict`), 2 bad input |
| `scripts/consistency_check.py` | Distinct spacing, radius, colour, accent hue, font family, font size, shadow, duration and button-variant counts against a budget, with `var()` resolved; off-grid, pure-black and slow-UI warnings | 0 within budget, 1 over, 2 bad input |
| `scripts/page_gate.py` | Head tags, declared kind, one h1, heading order, sections and words, hero actions, image alt/dims/lazy/weight, captions, fonts, blocking scripts, effects by kind (CSS or utility classes), scroll reveals, reduced motion, layout transitions, fixed elements, dead links | 0 pass, 1 FAIL, 2 bad input |
| `scripts/copy_devices.py` | Repeated devices (number-pair headings, negation runs, stat strips, eyebrows, quote walls, even rhythm) and honesty tells (apology notes, default-cast brand); phrases shared across pages | 0 clean, 1 FAIL, 2 bad input |
| `scripts/access_links_check.py` | Control names, labels, forms, tabindex, skip link, share tags, link targets, verb-first buttons, main-action wording, carousels, popups, headless-checker tests; lists `data-assumed` facts | 0 pass, 1 FAIL, 2 bad input |
| `scripts/style_rules.py` | Rule-level CSS: violet accents, default faces, heavy weights, small text, tracked caps, in-rule contrast, CSS-background photographs, font-display | 0 pass, 1 FAIL, 2 bad input |
| `scripts/finish_gate.py` | Runs all six, applies `site-waivers.json`, counts rounds with `--state`, ends on one `GATE:` line | 0 PASS or DONE, 1 FAIL or OPEN, 2 bad input |

All take `--format text|json`. Budgets: `--budget` (default `assets/site_budget.json`); word lists:
`--lexicon` (default `assets/copy_tells.json`).

### Reference Documentation

| File | Purpose |
|---|---|
| `references/one-system-and-rhythm.md` | Token budgets and why, colour and type rules, section rhythm, words per screen, equal edges, hero, shell |
| `references/copy-voice-and-tells.md` | Fact sheet, voice registers, the five copy rules, every tell with its fix, over-correction, what is not a tell, read-aloud check |
| `references/imagery-motion-effects.md` | The four kinds, photograph sourcing and rules, the three motion layers and house timings, effect budget by kind, weight budget |
| `references/sections-cards-forms.md` | What each section carries, the one-object rule, plans by kind, the card recipe, forms, access and head tags, links and actions, the shell and nav |
| `references/finish-gate.md` | What each script checks and misses, the gate's verdicts and rounds, the browser checklist, waiver format, handover report |
| `assets/site-plan-template.md` | Kind, fact sheet, voice card, system, screens and gate log to fill before building |
| `assets/copy_tells.json` | Editable lexicon for `copy_lint.py` |
| `assets/site_budget.json` | Editable budgets for `consistency_check.py` and `page_gate.py` |
| `assets/sample_budget_strict.json` | A tightened client budget (one accent, three radii, eight sections); pass with `--budget` |
| `assets/sound_page.html` | A place page built to the rules; every script exits 0 and the gate prints `GATE: PASS` |
| `assets/flawed_page.html` | A service page with every common fault; every script exits 1 |
| `assets/malformed_page.html` | Plain text with an `.html` name; every script exits 2 |
| `assets/sound_page_de.html` | A German place page with a root-relative stylesheet (`/sound_page_de.css`) and `#top` links; every script exits 0 |
| `assets/flawed_utility_page.html` | A utility-class service page with no built CSS: `page_gate.py` and `finish_gate.py` exit 1 (utility effects, no reduced motion, `no-css`); the two CSS checkers alone exit 2 |

## Scope & Limitations

**In Scope:**
- Planning, writing and building marketing, company, product and landing pages with a consistent system.
- Static checks of copy, design values, structure, imagery, effects, access, forms, links and style, behind one gate.
- Choosing motion and effect budgets by kind of business.

**Out of Scope:**
- Choosing a palette, type pairing or style direction from scratch for a product category; this skill
  assumes the system is set and checks that it is kept.
- Auditing an existing app interface for visual slop or against a token file, and refining it by
  named commands; that is interface-audit work, not site building.
- React or Next.js scaffolding, component generation and bundle analysis: see `engineering/senior-frontend`.
- Conversion strategy, copy frameworks and A/B testing: see `marketing/landing-page-generator`.
- Long-form article editing: see `marketing/copy-editing`.

**Important Caveats:**
- The scripts read source, not a rendered page. Section heights, edges, overlap, contrast on real
  grounds, hover response and timing need the browser checklist.
- Local and root-relative (`/css/site.css`) stylesheets, scripts and images are read from disk;
  remote ones never are. Without readable CSS the gate reports `no-css`: pass the built file with `--css`.
- `consistency_check.py` sees what is in the CSS it is given; utility classes and CSS-in-JS must be
  checked on the built stylesheet.
- The lexicon and the `button-verb` list are English; on a page in another language the copy lint
  finds little and `button-verb` is skipped, so read the copy aloud instead. A word literal for the
  trade is a false positive: `--allow` it and say why.
- Budgets are house defaults, not standards. Tighten them per client; loosen them only with a reason.
