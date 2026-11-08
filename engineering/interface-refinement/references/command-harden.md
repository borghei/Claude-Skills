# harden — survive real content, real users and real failures

**Job:** make a surface hold up against long text, translation, errors, slow networks, keyboard
and assistive technology, and bad input.

**Run when:** the detector reports `focus-ring-removed` or `broken-image`; before launch; after `clarify` makes
strings longer; when a critique's stress-test persona breaks the page.

## Change

- **Focus:** every interactive element shows a `:focus-visible` ring at least 2px wide with 3:1
  contrast against its surroundings. `outline: none` survives only next to its replacement.
- **Text overflow:** headings and labels wrap or truncate deliberately (with the full text
  available on hover/focus); flex and grid children get `min-width: 0` where they hold text.
- **Localisation:** room for 30-40% longer strings; logical properties (`margin-inline-start`)
  for right-to-left; dates, numbers and currency formatted per locale; no text baked into images.
- **Errors:** every request has a visible failure path with a retry; form errors sit beside the
  field and are announced (`aria-live` or focus move).
- **Edge content:** zero items, one item, thousands of items, missing image, missing name,
  very long name, permission denied.
- **Input:** validation states before submit, `inputmode` and `autocomplete` set, paste allowed.
- **Slow paths:** skeletons or progress for waits over ~1 second; disable double-submit.

## Do not touch

- The visual language. Hardening fixes behaviour and resilience, not look.
- Copy meaning (route copy changes to `clarify`).
- Business logic, except where a missing failure path is the defect; then flag it to the owner.

## Steps

1. List the states and extremes this surface can meet; use the context file's Constraints
   (locales, devices, accessibility standard).
2. Feed each extreme in: a 60-character name, an empty list, a failed request, a 200% zoom, a
   German build, keyboard only, a screen reader pass on the primary flow.
3. Fix the failures, worst first: blocked task, data loss, invisible state, then cosmetics.

## Verify

- Detector `--rules focus-ring-removed,broken-image` exits 0.
- Keyboard-only walk of the primary flow; focus never lost, never trapped, always visible.
- Screenshots with the longest realistic strings at 360px.
- Every network call has a visible error and retry; double-click on submit sends once.
- Screen reader announces errors and state changes on the primary flow (state which reader and
  browser produced the evidence).

## Hand-off

`polish`.
