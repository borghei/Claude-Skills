# optimize — make the interface load and move without stutter

**Job:** remove the front-end causes of slow first paint, layout jumps and janky motion on the
named target, without changing how it looks.

**Run when:** the detector reports `image-missing-dimensions`, `font-display-missing`,
`layout-property-motion` or `transition-all`; someone says "slow", "laggy", "jumps when it loads";
field data shows poor loading, interaction or layout-stability numbers.

## By mode

- **Persuade:** the first screen is the budget. The largest image or headline must paint fast, and
  nothing above the fold may move after it appears.
- **Operate:** interaction speed matters more than first paint. Long lists, heavy re-renders and
  input lag are the usual causes.
- **Read:** fonts and images. Text must be readable before the web font arrives.

## Diagnose first (static signals this skill can read)

| Symptom | Static cause to look for | Fix |
|---------|-------------------------|-----|
| Content jumps while loading | `<img>` / `<video>` / embeds without width and height or aspect-ratio | add intrinsic dimensions; reserve space for late banners and ads |
| Blank text on slow networks | `@font-face` without `font-display`; four or more font files on the first screen | `font-display: swap`; subset; preload the one or two faces above the fold |
| Janky transitions | transitions or keyframes on width, height, top, left, margin, padding; `transition: all` | animate `transform` and `opacity`; name the properties |
| Slow largest paint | hero image lazy-loaded, unsized or served at full camera resolution | eager-load and size the hero; serve responsive `srcset` and a modern format |
| Sluggish scroll | `background-attachment: fixed`, large `filter: blur()` or `backdrop-filter` on scrolling layers, `will-change` on many elements | drop or confine the effect; set `will-change` only during the animation |
| Long lists stall | hundreds of rows rendered at once in source | paginate or window the list; keep row markup flat |

What needs a browser or field data (actual paint times, interaction delay, bundle size) is out of
reach of a static scan: measure it with the project's own tooling and record the numbers.

## Change

- Markup attributes (dimensions, `loading`, `decoding`, `fetchpriority`, `srcset`), font loading,
  animated properties, and list rendering inside the target.

## Do not touch

- The look. Every optimisation must be invisible in a side-by-side screenshot, except that things
  stop moving.
- Content and copy.
- Build tooling and dependencies, unless the owner asks; propose the change instead.

## Steps

1. Record a baseline: the detector's `--scope layout,motion,type` findings on the target, plus any
   field or lab numbers the team already has.
2. Fix layout shift first (dimensions, reserved space), then font loading, then motion, then list
   rendering. Shift is the defect people feel most.
3. Recheck after each family; stop when the remaining cost is not on the first screen or the
   primary task.

## Verify

- Detector on the target: no `image-missing-dimensions`, `font-display-missing`,
  `layout-property-motion` or `transition-all` findings left unwaived.
- Before/after screenshots at 360px and 1280px are identical.
- The same measurement as the baseline, rerun, with both numbers in the report.
- Reduced-motion still honoured after any motion change.

## Hand-off

`polish`.
