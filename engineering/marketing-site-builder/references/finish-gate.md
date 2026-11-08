# The Finish Gate

A page is not finished while a check it could pass still fails. The gate is six static scripts, run
together by `finish_gate.py`, plus a browser checklist for what source code cannot show. Run the gate
after every round of fixes; it counts the rounds and stops at three, so the build iterates for real
and still ends. Never game a check: a false finding is waived in writing.

## 1. The scripts

```bash
python3 scripts/finish_gate.py index.html --kind service --state .site-gate.json   # all six, one verdict
python3 scripts/copy_lint.py index.html          # words and phrases
python3 scripts/copy_devices.py index.html       # repeated devices and honesty tells
python3 scripts/consistency_check.py index.html  # distinct design values against a budget
python3 scripts/page_gate.py index.html          # head, structure, images, effects, motion
python3 scripts/access_links_check.py index.html # names, labels, forms, links, head tags, shell
python3 scripts/style_rules.py index.html        # rule-level CSS style checks
```

Every script takes `--format json`; the six checkers also take `--strict` (warnings fail too). Each
exits 0 when clean, 1 on findings, 2 on unusable input (missing file, an `.html` file with no markup,
bad JSON or a wrong shape in a budget, lexicon, waiver or state file, a page with no CSS at all for
`consistency_check.py` and `style_rules.py` run alone). Line numbers point at the source file.

Linked stylesheets, scripts and images are read from disk when they are local: relative paths
against the page's folder, root-relative paths (`/_next/static/css/a.css`, `/css/site.css`, the way a
static export links them) against the page's folder and up to four folders above it. Remote files
are never fetched.

### copy_lint.py

Reads visible text only: it skips `script`, `style`, `template`, `noscript` and inline SVG, and adds
the meta description. Each block element is one segment, so a phrase split by inline tags is still
seen whole. Link and button texts are checked separately as labels. A `.md` or `.txt` draft is
linted line by line, with `#` lines as headings and `[text](url)` as labels, so copy can be checked
before any markup exists.

| Severity | ids |
|---|---|
| FAIL (one hit) | `hype-word`, `stock-phrase`, `residue`, `vague-cta` |
| FAIL at twice the budget plus one, WARN above the budget | `virtue-word` (2), `contrast-frame` (2), `ing-rider` (1), `fragment-heading` (1), `em-dash` (2), `exclamation` (0), `emoji` (1) |
| WARN | `soft-cta`, `reveal`, `puffery`, `proof-figure`, `default-cast`, `footer-signoff`, `stale-year`, `question-heading`, `h1-length` |

`--allow harness` skips a word that is literal for the trade. `--lexicon` swaps in a client's own
word lists (copy `assets/copy_tells.json` and edit it).

### consistency_check.py

Collects CSS from `<style>` blocks, `style=""` attributes and local linked stylesheets (remote ones
are skipped), plus any `--css` files; or reads a `.css` file directly. It resolves `var(--token)`
references, including fallbacks, so tokens are counted by the values they hold. For each category it
prints distinct values, the budget, and when over budget each value with its count and first
location.

| Category | Read from | Budget key |
|---|---|---|
| Spacing | `margin*`, `padding*`, `gap`, `row-gap`, `column-gap` (rem and em as 16px) | `spacing_values` |
| Radius | `border-*radius` (999px and up counted as one "pill") | `radius_values` |
| Colour | `color`, `background*`, `border*`, `outline*`, `fill`, `stroke`, shadows | `colour_values` |
| Accent hues | Saturated colours grouped into 30-degree hue bands | `accent_hues` |
| Font families | First family of each `font-family` or `font` (generic names ignored) | `font_families` |
| Font sizes | Each distinct `font-size` value | `font_sizes` |
| Shadows | Each distinct `box-shadow` or `text-shadow` | `shadow_styles` |
| Durations | Every time in `transition*` and `animation*` | `durations` |
| Button variants | Distinct class sets on elements whose class names a btn, button or cta | `button_variants` |

Warnings (never exit 1 unless `--strict`): `off-grid` spacing not on the 4px grid, `pure-black` ink,
`slow-ui` transitions over the budget.

What it cannot see: values set by script, utility classes resolved by a framework at build time.
For a Tailwind or CSS-in-JS project, run it on the built CSS (`dist/assets/*.css`) with `--css`.
A page with no readable CSS is bad input here (exit 2); inside `finish_gate.py` it becomes one
`no-css` FAIL so every other check still runs.
Native CSS nesting is read with a brace-depth scan, so declarations beside a nested rule count. Lengths
inside `calc()` are not counted as spacing values; `clamp()`, `min()` and `max()` endpoints are.

### copy_devices.py

Counts the shapes copy_lint's word lists cannot: number-pair and colon headings, negation runs, a
strip of figures, step numbers, eyebrow labels, three or more quotes, a response-time promise in two
wordings, "since <year>" twice, a grey heading half that runs on, labels in capitals, sentences of
one length or a drumbeat of fragments, apology notes ("names are examples") and a default-cast name
as the page's own brand. Ids and budgets: `copy-voice-and-tells.md`, section 4. FAIL: `apology-note`,
`cast-brand`, and a device at twice its budget plus one. Pass several pages at once to see their first
headings side by side and the heading phrases they share (`shared-phrase`).

### access_links_check.py

| Severity | ids |
|---|---|
| FAIL | `a11y-name` (a control with no name), `field-label` (no visible label), `tabindex` (above 0), `form-action` (sends nowhere), `anchor-target` (an `#id` that does not exist), `carousel` (class, element or library), `checker-gaming` (code that tests for a headless or automated browser) |
| WARN | `menu-toggle`, `field-type`, `skip-link`, `share-meta`, `head-icon`, `button-verb`, `label-target`, `label-count`, `main-action`, `map-embed`, `popup`, `shell-widget` |

`skip-link` is satisfied by an in-page link before `<main>` that says "skip" or points at the id of
`<main>`, so it works in any language. `button-verb` uses an English verb list and runs only when
`<html lang>` is English or missing; on other pages read the labels yourself. `#top` counts as a
landing target without an id, as browsers treat it.

Elements marked `data-assumed` (a price or an hour the brief did not give) are listed as INFO for the
report. The rules behind each id: `sections-cards-forms.md`.

### style_rules.py

Reads the CSS rule by rule, with `var()` resolved. FAIL: `contrast-pair` under 3:1 (WARN under 4.5:1)
where one rule sets both the text colour and a solid ground. WARN: `violet` accents, `default-face`,
`heavy-weight` (700 and up), `tiny-text` (under 13px), `small-body` (reading text under 16px),
`tight-leading` (under 1.4), `tracked-caps` (more than one uppercase rule), `css-bg-photo`,
`font-display`. It cannot see colours set by script or contrast between rules; the screenshot pass
covers those.

### finish_gate.py

Runs all six in-process, then prints each script's counts, the open FAILs, the waived ones with their
reasons, notes on ignored waivers, and one verdict as its last line:

| Verdict | Meaning | Exit |
|---|---|---|
| `GATE: PASS` | no FAIL left | 0 |
| `GATE: FAIL n (round k of 3)` | fix and run again | 1 |
| `GATE: OPEN n (rounds used up)` | stop fixing; put the open FAILs in the report | 1 |
| `GATE: DONE (...)` | the user ended the build with `--done "<their words>"` | 0 |

With `--state .site-gate.json` a run counts as a round only when the page, any stylesheet it read
(linked or `--css`), the waiver file, the budget or the lexicon changed since the last run, so
rerunning an unchanged page costs nothing and raising a budget still costs a round. A state file
written for another page starts fresh. Use `--done` only when the user says to stop or ship as it
is, never on your own judgement; delete the state file to start a new build. `--max-rounds` must be
1 or more. A `.md` draft runs the two copy checks only. With no readable CSS (an unbuilt Tailwind
page, a remote stylesheet) the two CSS checkers are replaced by one `no-css` FAIL: pass the built
stylesheet with `--css` rather than waiving it.

### page_gate.py

| Group | Checks |
|---|---|
| Head | `lang`, `viewport`, `title` (FAIL); `description` missing or equal to the title (WARN); `kind-missing` when neither `<html data-kind>` nor `--kind` is given, so the page was checked as a product (WARN) |
| Structure | `one-h1` (FAIL); `heading-order`, `section-count`, `section-heading`, `section-words`, `page-words`, `hero-actions` (WARN) |
| Images | `img-alt` (FAIL from the first), `img-dims` and `img-lazy` (WARN 1-3, FAIL 4+), `hero-lazy`, `eager-images`, `data-uri`, `img-weight` and `img-total` (local file weight; FAIL past the fail budget), `caption` |
| Fonts and scripts | `font-families` (WARN at budget + 1, FAIL beyond), `font-files`, `blocking-script` |
| Effects by kind | `effects`: canvas, autoplay video, gradients, `backdrop-filter`, blur filters, blend modes, scroll and 3D libraries, and the same effects as utility classes (`bg-gradient-to-*`, `backdrop-blur-*`, `blur-*`, `mix-blend-*`, with any `md:` style prefix); FAIL on any for product, service and place, WARN past one on tech |
| Motion | `scroll-reveal` (WARN 1-2, FAIL 3+), `scroll-snap`, `reduced-motion` (FAIL when the page moves, through `@keyframes`, `animation`, `transition`, an `animate-*` class, canvas, autoplay video or a motion library, with no `prefers-reduced-motion` rule or `motion-reduce:`/`motion-safe:` variant; a static gradient does not count as movement), `layout-transition`, `transition-all`, `fixed-elements` |
| Links | `dead-link`: `href` empty, `#` alone or `javascript:` (FAIL) |

Line numbers for CSS findings point into the page; a finding from a linked stylesheet is printed
with line `-` and its location in brackets (`[style.css:52]`).

Sections are the direct `<section>` children of `<main>` (nested sections count with their parent);
the first one, or one with a `hero` class, is the hero.

## 2. The browser checklist (cannot be checked statically)

Take screenshots at 1440x900, 1024x768, 820x1180, 768x1024 and 390x844 and read them against this list.

- [ ] The hero fills the first screen alone; its main button is visible without scrolling at every width.
- [ ] Each later section is one or two screens tall; no screenshot shows the next section's heading peeking in.
- [ ] Left and right content edges line up across every section, the header and the footer.
- [ ] Nothing overlaps, nothing is cut by the fold, no horizontal scroll at 320px.
- [ ] Every visual draws: no empty frame, no half-loaded picture, no blank canvas.
- [ ] At 768x1024 and 820x1180 (a tablet held upright) each section still fits its one or two
      screens, and the first screen ends on a whole picture or a clear bleed, never a card cut by the fold.
- [ ] The h1 takes three lines at most at every width; the hero's picture ends inside the hero.
- [ ] Two picture-less sections are never neighbours; no layout appears more than twice.
- [ ] Hovering a button, a linked card and a linked photograph visibly changes each.
- [ ] Tab reaches a skip link first; the focus ring shows at once and never hides under the header.
- [ ] Text contrast holds on the real grounds, including text over photographs.
- [ ] Tap targets outside running text are at least 44px tall on a phone.
- [ ] With reduced motion on, nothing moves and nothing stays hidden.
- [ ] Lab timing (Lighthouse or WebPageTest): LCP under 2.5s, CLS under 0.1, INP under 200ms on a mid-range phone profile.

## 3. Waivers

A check that is wrong for this page is waived in writing, never silenced by editing the page to
dodge the pattern. Keep waivers beside the page as `site-waivers.json` (`finish_gate.py` reads it
from there, or from `--waivers`):

```json
[
  {"check": "hype-word", "target": "seamless",
   "reason": "Product is a seamless knit sock; the word is literal"}
]
```

- `check` is the finding id; `target` is text from the finding (its word, its line such as `L42`,
  or its message), 3 characters or more, matched without regard to case; `reason` is 12 characters
  or more. A line target goes stale when lines above it move; rerun and fix the waiver when the gate
  notes that it matches no FAIL.
- One waiver covers one finding. A target that matches several FAILs is ignored with a note saying
  so: name one. Each copy word is its own finding, so a new hit added later is never covered.
- `checker-gaming` cannot be waived. More than five waivers is itself a FAIL (`too-many-waivers`):
  the budget or the page is wrong, so fix that instead.
- Words from the client's own approved copy are waived hit by hit with the brief as the reason.

## 4. The handover report

End every build with:

1. The `GATE:` line first, then every open FAIL with the reason it stays.
2. Every waiver and its reason.
3. The kind and the effect and moments used (if any).
4. Every assumed fact (the `data-assumed` lines access_links_check lists), every stand-in photograph
   and client-asset slot, the form's stand-in address, and the canonical domain still to come.
5. The voice card in one line, and every copy WARN kept, with why.
6. What was not checked: the browser checklist items not yet run.
