# Design Decision Guide

How the recommender turns a brief into a spec, what each decision rests on, and when
to override it. Read this before arguing with a default.

## The decision chain

A spec is a chain of nine decisions. Each one constrains the next, so make them in
order and do not reopen an earlier one without re-running the tool.

1. **Product type.** The brief's product sentence, audience and mood words are scored
   against the keyword lists in `product-types.json` (whole phrase +3, shared word +1).
   Ties go to the candidate with more keyword hits (as opposed to name hits). The top
   three candidates are reported. A top score of 0 is a `no-match` failure (the spec is
   built on the first product type and means nothing); a top score of 1, or a tie, warns
   `weak-match`. Either way set `product_type` explicitly rather than accepting a guess.
   Matching is English-only: a brief in another language always needs `product_type`.
   US and UK spellings (color/colour, gray/grey) match each other.
2. **Brief modifiers.** Cue phrases in the product, audience and mood
   (matched as whole words, so "documentation site" does not trigger "on site";
   `brief-modifiers.json`: pre-launch, enterprise, app-first, high-end, live data,
   outdoor glare, night use, young audience, first-time users, safety-critical) adjust
   the landing pattern, density, motion, mode or preferred direction, and add items to
   the avoid list. A modifier never overrides a field the brief sets itself, and each
   one is reported as an `info` finding so the reader can see why a default moved.
3. **Mode.** `light`, `dark`, `both`, or `auto` (take a modifier's mode, else the product type's default).
   `both` means both palettes are generated *and* contrast-checked; nothing is inverted.
4. **Direction.** Order of preference: the brief's `direction`, then a modifier's
   preferred direction, then the product's primary and alternate. Mood words are scored
   against both of the product's directions; when the alternate fits them better the two
   swap (`direction-mood`). Any candidate in `must_avoid` or unable to render the
   requested mode (Dark Immersive has no light mode) is skipped. A preferred direction
   with high accessibility risk (Translucent Layered, Soft Depth) is used but warned
   (`direction-risk`). If both are blocked the tool fails with `direction-conflict`: the
   brief asks for something the product type has no sound answer for. Resolve by
   loosening `must_avoid`, changing the mode, or choosing a different product type.
5. **Palette.** The first palette in the product's list whose required modes pass the
   contrast target. With `contrast_target: "AAA"` the high-contrast palette is added as a
   last resort, with a `palette-fallback` warning. With a `brand_color`, the brand takes
   the primary role and is adjusted per mode until it reaches 4.5:1 on that background.
6. **Typography.** The brief's `pairing` when set. Otherwise the product's first
   pairing while the product's own direction is used, or the direction's own `pairing`
   when a forced, modifier or mood direction replaces it (so a premium direction does not
   ship with a dashboard sans). Overridden when the brief mentions or is written in a
   non-Latin or RTL script (global superfamily), or mentions low-vision or older readers
   (hyperlegible family, 18px base). The ratio comes from the direction; compact density
   forces 1.2 so headings do not eat dense screens.
7. **Tokens.** Spacing by density, radius and elevation by direction, durations by
   motion tier, touch target by platform (44 web, 48 when mobile is in scope, 48 on any
   platform when the outdoor-glare modifier applies), focus
   ring 2px with 2px offset, icon sizes 16/20/24 with a 1.5 stroke for flat and soft
   directions and 2 for raised and layered ones.
8. **Page patterns.** The product type names a landing pattern (or none, for internal
   tools) and two or three in-product screens from `page-patterns.json`. A modifier can
   replace the landing pattern (a pre-launch brief gets `waitlist`). Each pattern lists
   sections in order, where the primary action sits, the evidence the page must carry,
   and when the pattern misleads.
9. **Motion by interaction.** The motion tier selects one duration per interaction from
   `motion.json` (press, state change, overlay entry and exit, toast, page transition,
   list stagger, scroll reveal, loading, data update, celebration, drag). Interactions
   with no duration in a tier are dropped: calm products get no stagger, scroll reveal,
   number animation or celebration.

## Why these defaults

**Contrast is computed, never asserted.** Every palette mode is checked on eleven pairs:
text on background and on surface, muted text on both, text on each coloured fill,
primary and focus against background (3:1, non-text contrast), and danger and success
as text. Border, disabled and scrim colours are not checked by the tool (CLR-06, CLR-07
are manual). A
palette that fails one pair is not offered. Run
`design_spec_checker.py --palettes` to re-verify the bundled set after editing it.

**Brand colour adjustment.** Most brand colours were picked for a logo, not for text. A
mid-saturation brand blue is typically 3-4:1 on white: fine for a large logo, not for a
link or a button label. The tool darkens it (light mode) or lightens it (dark mode) in
2% steps toward black or white until it reaches 4.5:1, and reports both values. Keep the
original for large decorative use only.

**Density.** Comfortable is the default for most products. Compact belongs to
operational tools where people scan many rows; it shrinks gaps, never hit areas. Spacious
belongs to reading, luxury and calm products. The tool warns when spacious density meets
four or more data views (expect scrolling) and when compact density meets touch.

**Motion tiers.**

| Tier | Durations (ms) | Use for |
|------|----------------|---------|
| calm | 120 / 180 / 240 | Operational, clinical, financial and reading products |
| standard | 150 / 220 / 320 | Consumer apps where spatial continuity helps orientation |
| expressive | 180 / 280 / 420 | Games, kids, launches, celebration moments |

Expressive motion for an audience described as motion-sensitive, vestibular, older or
migraine-prone is a hard conflict (`motion-audience`). Every tier ships with
`reduced_motion: true`: reduced motion removes movement and keeps short opacity changes.

**Radius and elevation** follow the direction because they are the most visible
signature of a style. Do not mix: a Swiss Functional product with 20px pill cards reads
as two products.

## Overriding a default

Override when you have evidence the default does not fit, and record the reason in the
spec. Good reasons: the brand book fixes a typeface; user research shows the audience
works on phones in sunlight; the product sells to both consumers and enterprises and the
enterprise buyer decides. Weak reasons: "it looks dated", "competitor X uses it".

To override, set the field in the brief (`density`, `motion`, `mode`, `product_type`,
`direction`, `pairing`, `must_avoid`) and re-run. Do not hand-edit the generated tokens: the checker will not know
which values were deliberate.

## File formats

### Brief (input to `design_recommender.py`)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `product` | string | yes | One sentence: what it is and for whom |
| `audience` | string | no | Who uses it, where, with what constraints |
| `product_type` | string | no | Force an id from `product-types.json` |
| `platform` | `web` / `mobile` / `both` | no | Default `web` |
| `mode` | `light` / `dark` / `both` / `auto` | no | Default `auto` |
| `density` | `compact` / `comfortable` / `spacious` | no | Overrides the product default |
| `motion` | `calm` / `standard` / `expressive` | no | Overrides the product default |
| `contrast_target` | `AA` / `AAA` | no | Default `AA` |
| `brand_color` | hex | no | Placed in the primary role and adjusted per mode |
| `stack` | string | no | Stack id or keyword from `stacks.json` |
| `mood` | list of strings | no | Extra words for matching; also decides between the product's two directions |
| `direction` | string | no | Force a direction id from `directions.json` (still subject to `must_avoid` and mode) |
| `pairing` | string | no | Force a type pairing id from `type-pairings.json`; overrides the script and low-vision switches, so choose a legible one |
| `data_questions` | list of strings | no | Plain-language questions the charts must answer |
| `must_avoid` | list of strings | no | Direction ids or names to exclude |

A field set to `null` counts as not given. A key not in this table (a typo such as
`brand_colour`) is ignored and reported as an `unknown-field` warning.

### Tokens (input to `design_spec_checker.py`)

The recommender's JSON output carries a `tokens` block in exactly this shape, and the
checker reads it directly. A hand-written file uses the same keys:

```json
{
  "contrast_target": "AA",
  "modes": ["light", "dark"],
  "color": {"light": {"bg": "#FFFFFF", "fg": "#111827", "primary": "#1F4FD1", "on_primary": "#FFFFFF"},
            "dark":  {"bg": "#0E1422", "fg": "#E8ECF4", "primary": "#7AA2FF", "on_primary": "#0E1422"}},
  "font": {"families": ["Inter", "JetBrains Mono"], "base_size": 16, "line_height": 1.5, "scale": [13, 16, 20, 25, 31]},
  "space": [4, 8, 12, 16, 24, 32, 48, 64],
  "radius": {"sm": 2, "md": 4, "lg": 6},
  "motion": {"durations_ms": [120, 180, 240], "reduced_motion": true},
  "touch_target": 44,
  "focus": {"width": 2},
  "icon": {"sizes": [16, 20, 24], "stroke": 1.5}
}
```

Colour roles: `bg`, `surface`, `fg`, `muted_fg`, `primary`, `on_primary`, `accent`,
`on_accent`, `border`, `focus`, `danger`, `on_danger`, `success`. `bg`, `fg` and
`primary` are required per mode; pairs whose roles are absent are skipped, not failed.
`modes` (optional) lists the modes the product ships; `["light"]` marks a deliberate
light-only product, so the missing dark block is not reported (CLR-02). A missing
`touch_target` or `focus.width` is reported at `medium` ("check by hand"); a value that
is present and below the threshold takes the rule's own severity (touch targets: under
24px critical, 24-43px high).

### CSS

`css_token_extractor.py` turns the custom properties of one or more `.css` files (read in
the order given, later files overriding) into the tokens shape above, for the checker to
audit. `spec_renderer.py --format css` writes a theme in the same naming, so a generated
theme round-trips.

- **Modes.** Light values come from blocks outside any dark context; dark values from
  blocks whose selector or at-rule prelude mentions `dark` (`@media (prefers-color-scheme:
  dark)`, `[data-theme=dark]`, `.dark`, `.dark &`), with anything inside `:not(...)`
  ignored. Dark values are layered over the light ones, as the cascade does, so a dark
  block that only overrides what changes is complete. `color-scheme: light` alone marks a
  light-only theme; `color-scheme: dark` alone moves undecorated `:root` blocks to dark
  mode (or pass `--root-mode dark`).
- **Structure.** Comments are stripped; `@layer`, `@media`, `@theme` and nested rules are
  followed, and declarations before and after a nested rule stay with their block.
  Values inside `prefers-reduced-motion` are not theme values; the block's presence counts
  as reduced-motion handling.
- **Colours.** Hex (3, 4, 6, 8 digits), `rgb()`/`rgba()` and `hsl()`/`hsla()` in comma or
  space syntax, bare `H S% L%` channels, `oklch()`, `oklab()`, `white`/`black`, and
  `color-mix(in srgb, ...)`. `var()` chains and fallbacks are resolved. A translucent role
  is composited over the mode's background and noted. Anything else (named colours,
  `color-mix` in other spaces, `light-dark()`) is listed under `extraction.unresolved` and
  is a gap: the role is skipped, never guessed.
- **Names.** Matched after stripping a `color-` prefix, with common aliases (`background`,
  `foreground`, `card`, `muted-foreground`, `ring`, `destructive`, `primary-foreground`);
  the more specific alias wins, so `muted-foreground` beats `muted`. Spacing comes from
  `--space-*` or a single `--spacing` base, radius from `--radius*`, durations from
  `--duration-*`, base size from `--font-size-base` or `--text-base`, line height from
  `--line-height-body` or `--leading-normal`, families from
  `--font-display|heading|body|sans|serif|mono|ui`. rem and em count as 16px.
