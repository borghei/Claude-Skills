# Detector rules: what fires, how, and how far to trust it

`ui_slop_detector.py` reads source text. It sees declarations, utility classes and element
structure; it does not render. The catalog data lives in `detector-rules.json` (id, severity,
scope, owning command, why, fix); `ui_rules.py --list` prints it. Two families:

- **generic:** patterns that mark an interface as assembled from defaults (the "looks generated"
  tells). These are design judgments; a brief can earn any of them back with a waiver and reason.
- **quality:** defects that hurt people regardless of taste (contrast, tiny text, focus, motion).

Severity: **high** fails at the default `--fail-on medium` and at `high`; **medium** fails at the
default; **advisory** reports but never fails unless `--fail-on advisory`.

## Rules and their signals

| Rule | Severity | Signal the tool reads | Precision notes |
|------|----------|----------------------|-----------------|
| side-stripe-border | high | `border-left/right/inline-*` 2px+ in a non-neutral colour; `border-l-4 border-<hue>-N` | High only on a rounded box (radius 4px+ or a `rounded*` class); a square callout or quote rule drops to advisory |
| gradient-text | high | `background-clip: text`; `bg-clip-text` with `text-transparent` | Reliable |
| ai-hue-gradient | medium | every gradient stop's hue: a violet stop (235-320 degrees) plus another chromatic stop 20+ degrees away; `from-/via-/to-` utility families | Works on hex, rgb, hsl, oklch and named colours, not a fixed hex list |
| glow-shadow | medium | box/text-shadow layer with zero x/y offset, blur > 0, chromatic colour; `shadow-<hue>-N` | Neutral glows (focus halos in grey) do not fire |
| hard-offset-shadow | advisory | shadow offset 3px+ with zero blur, not inset | Advisory because a brutalist brief chooses it |
| cream-ground | medium | warm (25-60 degrees), very light (88-97.5%), faintly tinted background on `html/body/:root/main` or a `--bg/--surface/--paper` token; `bg-amber-50` and friends on the page element | Only page-level grounds, never cards |
| overused-face | medium | first family in `font-family`, `font-['...']`, or a font-service link, in a list of 14 over-used faces | Waive when the brief binds the face; with `--context`, a face a type role names does not fire |
| default-font-stack | advisory | first family a system face on `html/body/:root/h1/h2/.hero` | Correct for many operate surfaces; record the decision. With `--context`, a type role naming a system face silences it |
| italic-serif-display | medium | `font-style: italic` plus a serif family on h1/h2/.hero/.display; `italic font-serif` on h1/h2 | |
| tiny-text | high | font-size below 12px on running-text selectors (p, li, body, td, .prose ...), below 11px anywhere else (labels, controls, fine print); px, rem, em, first argument of `clamp` | Skips `.sr-only` / `.visually-hidden` and `calc()` / `max()` values. 11px badges and table meta are allowed; 10px is not |
| tight-body-leading | medium | line-height below 1.3 on p, li, body, article, td, .prose | Headings are not checked |
| wide-body-tracking | medium | letter-spacing 0.05em+ on running-text selectors without uppercase | |
| crushed-tracking | medium | letter-spacing below -0.04em anywhere | |
| justified-text | advisory | `text-align: justify` without `hyphens: auto` | |
| low-contrast-pair | high | `color` and `background(-color)` declared in one block, both opaque, ratio under 4.5 (3.0 for large text) | Only pairs declared together; inherited colours are invisible to a static scan |
| faint-gray-text | high | `text-<neutral>-200/300/400` on an element whose own or inherited ground is light or unknown | Skipped when the nearest declared ground is dark. The page ground is also read across the scan (a `body`/`html` background or `@apply bg-*`, `<html class="dark">`, `<body class>`), so scan the layout or global styles with the page; pages that disagree count as unknown |
| gray-on-color | medium | neutral grey text on a saturated ground that still passes contrast | |
| bounce-easing | advisory | cubic-bezier with a y value outside 0-1; names with bounce/elastic/wobble; `animate-bounce` | |
| transition-all | medium | `transition: all`, `transition-property: all`, a shorthand that starts with a duration, `transition-all` | |
| layout-property-motion | medium | transitions naming width/height/top/left/margin/padding; keyframe steps that set them | |
| missing-reduced-motion | high | any keyframes, `animation` or `animate-*` in the scan, and no `prefers-reduced-motion`, `motion-safe:` or `motion-reduce:` anywhere in the scan | Project-level: scan the whole source tree to avoid false hits |
| decorative-pulse | medium | infinite pulse/ping/blink animation on a dot/status/live selector; `animate-ping/pulse` on a small `rounded-full` | |
| marquee-scroll | medium | `<marquee>`; infinite animation named marquee/ticker/scroll-x; marquee classes with `animate-*` | |
| focus-ring-removed | high | `outline: none/0` when the scan contains no `:focus-visible` rule; `outline-none` without a `focus-visible:` or `focus:ring` class | Project-level focus-visible search, so scan global styles too. `:focus:not(:focus-visible) { outline: none }` is the correct pattern and does not fire |
| repeating-stripes | advisory | `repeating-*-gradient` on a background | |
| grid-line-background | advisory | two or more linear-gradient layers with 1px lines plus a px `background-size` | |
| monotonous-spacing | advisory | 12+ padding/margin/gap values in a file, one value is 60%+ of them, and fewer than 3 distinct values | A dense 8px grid with 4px and 16px steps still has rhythm and stays silent |
| everything-bold | medium | 8+ text elements in a file and half or more carry semibold or heavier | |
| nested-cards | high | a card-shaped element (card class, `<Card>`, or rounded + border/shadow + padding) inside another | Parts such as `card-body` and `card-header` are not cards; nor are buttons, inputs, spans, `<dialog>` or `role=dialog` surfaces. Padding must be all-round 3+ (`p-3`) or vertical 4+ (`py-4`), so a `px-6 py-3` button is not a card |
| kicker-above-heading | high | the element right before an h1-h3 is short (48 chars or less) uppercase tracked text, or has an eyebrow/kicker/overline class | |
| icon-tile-stack | medium | the element right before a heading is a small square tinted rounded tile (or an icon-wrapper class) holding an svg, img, icon component or emoji | |
| chip-soup | medium | 4+ chips (badge/chip/pill/tag/status classes, or rounded-full + px + small text) inside one card, or 12+ in a file | Chips in table cells (a status column) are not counted |
| identical-card-row | medium | 3+ consecutive siblings with the same tag and class list, each containing a heading and each card-shaped or iconed | Rows rendered by `.map()` appear once in source and are not caught. A row where every card holds a photo (a raster `<img>`, not an svg or icon) is a product or media grid and does not fire |
| emoji-icon | medium | emoji in buttons, links, list items, nav, labels, headings, icon-classed elements, an emoji-only element, or starting a paragraph | |
| vague-control-label | medium | button, button-classed element, link or submit input whose whole label is Submit, OK, Yes, No, Click here, Here, Go ... | |
| vague-headline | medium | h1/h2 text matching template openers (Welcome to, The future of, all-in-one, Supercharge your, Everything you need ...) | Marketing CTA phrases and buzzword density are left to design-auditor |
| skipped-heading | medium | a heading more than one level below the previous one in the same file | Component files that start at h2 are fine |
| numbered-section-labels | advisory | 3+ elements whose whole text is 01, 02, (03), 04/10 ... | |
| radial-glow | medium | a `radial-gradient` on a background with a chromatic stop (saturation 0.25+, alpha over 0.15) that fades to `transparent` or alpha 0.05 or less | Neutral vignettes (black or grey to transparent) do not fire |
| organic-clip-path | medium | `clip-path: polygon()` with 10+ points, 5+ distinct x and y values, not a staircase of right angles; `path()` with 3+ curve commands | Hexagons, cut corners and diagonals have too few points to fire |
| hairline-wide-shadow | advisory | a card-like selector (card, tile, feature, plan, pricing, item) with a 1px `border` and a box-shadow blur of 24px or more | Popovers, menus and dialogs are not card-like selectors, so they keep both |
| blinking-cursor | advisory | an animation with `steps()` / `step-end` whose name or selector says blink, caret, cursor or typing | Smooth blinking (no steps) is left to decorative-pulse |
| shape-assembled-illustration | advisory | inline `<svg>` at least 200x200 (attributes or viewBox) with 12+ circle/ellipse/rect/polygon/line shapes in 3+ fills | `<path>`-drawn artwork, icons and bar series (all rects, one width) are skipped |
| oversized-headline | medium | an `<h1>` of 8+ words with a `text-6xl`-or-larger class, an arbitrary text size of 64px+, or an inline font-size of 64px+ | Headlines rendered from `{variables}` count as zero words and never fire |
| flat-type-hierarchy | medium | project-level: font sizes declared on plain `h1`, `h2`, `h3` and `body`/`p` selectors; fires when every step between them is under 1.25x | Needs body and two heading levels; sizes in `clamp()`, `var()`, em or vw are not read |
| broken-image | high | `<img>` with no `src`/`srcset`/`data-src`, an empty `src`, `#`, or a placeholder-service URL | Spread props (`{...props}`) and bound sources (`:src`, `[src]`, `src={x}`) are trusted |
| buried-raster | medium | a background `url()` under a gradient listed before it whose stops are all 0.9 alpha or more; a background image on a block with opacity under 0.1 | A blend mode in the same block keeps the image visible and does not fire |
| all-caps-body | medium | `text-transform: uppercase` on a running-text stylesheet selector (`.legal p`), excluding label, badge, button, nav and caption selectors; a `<p>` with an `uppercase` class and 80+ characters | Short uppercase labels, eyebrows and buttons are a convention and stay silent |
| image-missing-dimensions | medium | `<img>` without both `width` and `height`, no `fill`, no `aspect-*` / `size-*` class and not both `w-*` and `h-*` classes | Framework image components (`<Image>`) are not read |
| font-display-missing | advisory | an `@font-face` block with no `font-display` | |
| off-system-font | medium | with `--context`: a first `font-family` face (or `font-['...']`) that no type role names | System and generic families are allowed as first face |
| off-system-color | advisory | with `--context`: a literal colour in color, background, border, fill, stroke or a custom property that is not within 3/255 per channel of a palette role | Shadows are not read; alpha variants of a palette colour count as on-palette |
| off-system-radius | advisory | with `--context`: a border-radius literal not on the radius scale | Zero, 9999px pills and percentages are allowed |
| off-system-font-size | advisory | with `--context`: a px or rem font-size not within 0.5px of a type role size | em, %, vw, `clamp()` and named utility sizes are not read |

## Reading the context file (`--context`)

Pass `--context interface-context.md` and the detector reads the visual system the `document`
command wrote: palette roles, type roles (face and px size) and the radius scale. Literal values
outside them become `off-system-*` findings, one per distinct value per file, at its first use,
with the use count. Every rule id listed under `### Refusals` is escalated: an advisory hit becomes
medium, so a refused pattern always fails the default gate, and its evidence is marked
`[refused in context file]`. A context file without palette and type roles is a bad input (exit 2).

## How source is read

- SCSS/LESS nesting: nested rule blocks are read on their own and blanked out of the parent, so
  the parent's own declarations are still checked. Selectors are not combined (`&:hover` is read
  as `&:hover`).
- `var()`, `url()` and `env()` values are opaque: a token named `--gray-700` is not a colour.
- styled-components / `css` templates: `${...}` interpolations are skipped and the rest is read as
  CSS under the element tag (`styled.p` is checked as `p`); a `css` template nested inside an
  interpolation is read on its own.
- JS style objects (`style={{...}}`, emotion `css({...})`, `sx`): camelCase keys become properties
  and bare numbers become px; only a quoted nested key (`'& h1': {...}`) is read as a selector.
- Class expressions: every string literal inside `className={cn(...)}`, `clsx(...)`, a template
  literal, Svelte `class={...}` or Vue `:class` counts as a class, conditional ones included.
  Classes held in variables are not read.
- Markup is parsed tolerantly: an unclosed `<p>` or `<li>` closes at the next block or item, as
  browsers do. `<script>` bodies and HTML comments are ignored by the image, svg, h1 and
  paragraph rules.
- Stylesheets are read in one linear pass; multi-megabyte and minified files scan in about a
  second. Minified files report every finding on line 1.
- A file that is not valid UTF-8 is skipped and listed in the report; the scan continues.

## What the static scan cannot see

Rendered contrast through inheritance and images, text that overflows its box at a given width,
elements covering text, content hidden until a script runs, heading spacing as rendered, real
touch-target sizes, class names built at runtime (classes held in variables or theme objects),
values behind SCSS variables and mixins (`border-left: 3px solid $brand` has no colour to read),
translucent glass panels (`backdrop-blur` over `bg-white/5`), and anything in native code. Those belong to the critique's Assessment A and the audit. A clean scan is the floor, not a
verdict.

## Running it well

```bash
# whole source tree, so project-level rules see global styles
python3 scripts/ui_slop_detector.py src/ --format json > detector.json
# one surface while refining, stricter
python3 scripts/ui_slop_detector.py src/pages/invoices.tsx src/styles/ --fail-on advisory
# one family at a time
python3 scripts/ui_slop_detector.py src/ --scope motion
# against the recorded visual system; refusals fail the gate
python3 scripts/ui_slop_detector.py src/ --context interface-context.md
```

Pair it with `engineering/design-auditor`'s `ai_slop_detector.py` for landing-page template
patterns (stock hero, three-column grid, pricing and testimonial layouts, buzzword density) and
with `engineering/a11y-audit` for alt text, labels and landmarks. The three rule sets do not
overlap. Copy tells (buzzwords, em-dash density, aphorism cadence) belong to the copy lint in the
site-building and design-auditor skills; this detector reads only headlines and control labels.
