# animate — motion that explains

**Job:** use motion for feedback, state change and continuity, plus at most one authored moment
the surface has earned. Remove motion that does none of those.

**Run when:** the detector reports `missing-reduced-motion`, `transition-all`,
`layout-property-motion`, `bounce-easing`, `decorative-pulse`, `marquee-scroll` or
`blinking-cursor`; a critique
calls the page "jittery", "slow" or "static where state changes".

## By mode

- **Persuade / Showcase:** one rehearsed focal sequence beats a fade-and-rise on every section.
- **Operate / Read:** fast feedback, continuity on navigation and layout change; no load
  choreography that makes people wait.

## Change

- **Reduced motion:** every animation gets a `prefers-reduced-motion: reduce` path (or
  `motion-safe:` utilities) that removes movement but keeps meaningful opacity and colour changes.
- **Properties:** name them. `transition: all` and bare-duration shorthands become explicit
  lists (`opacity, transform, background-color`).
- **Layout work:** animations of width, height, top, left, margin or padding become transform /
  opacity, a grid-rows technique, or a FLIP transition.
- **Easing:** decelerating curves for arrivals (for example `cubic-bezier(0.2, 0.8, 0.2, 1)`);
  exits faster than entrances; no bounce or overshoot unless the subject literally bounces.
- **Durations:** 100-150ms feedback, 150-300ms state change, 300-500ms overlays and view changes,
  up to 800ms for one authored entrance.
- **Idle loops:** pulsing dots, marquees and endless shimmer stop unless they track live data;
  any loop stops when off-screen and offers pause.
- **Visible by default:** content is visible without JavaScript; reveal animations start from an
  already-readable state.

## Do not touch

- The surface's visual design and copy.
- Motion that carries real meaning (progress, live data); refine its timing instead of removing it.

## Steps

1. List every animation and transition in the target. For each, write its job: feedback, state,
   continuity, attention, or none.
2. Remove the "none" items. Fix properties, easing and duration on the rest.
3. Add the reduced-motion path in the same change.
4. Choose the focal moment, if any, and make it specific to this product.

## Verify

- Detector `--scope motion` exits 0 on the target.
- With the OS reduced-motion setting on, nothing slides or scales; state changes are still visible.
- A performance recording of the main interaction shows no layout work during animation.
- Interrupting an animation (clicking twice, navigating away) leaves no broken state.

## Hand-off

`polish`.
