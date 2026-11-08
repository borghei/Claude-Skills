# polish — the closing pass

**Job:** bring a functionally complete surface up to one consistent finish without changing what
it is. Polish is refinement, never a disguised redesign.

**Run when:** last in every refine plan; before a release; when the detector reports
`emoji-icon`, `skipped-heading` or `buried-raster`; when a critique snapshot lists P2/P3 issues.

## By mode

- **Persuade / Showcase:** the first viewport, the primary action and the imagery get the closest
  look; one authored motion moment at most.
- **Operate / Read:** alignment, state coverage, keyboard path and density consistency across
  neighbouring screens.

## Change

- Drift from the system: classify each one first. A **missing token** (the system needs a value)
  gets a token; a **one-off** gets the shared component; a **local defect** gets fixed in place; a
  **concept mismatch** (flow differs from neighbouring screens) is reported, not patched.
- Alignment and spacing to the scale; optical alignment of icons and numerals.
- Every interactive state: default, hover, focus-visible, active, disabled, loading, error, success.
- The parts the browser draws by default: text selection colour, caret, focus ring, scrollbar on
  scroll regions, link underline offset, tabular numerals in tables.
- Icons: one family, one stroke, one size scale; replace emoji used as icons.
- Heading outline: no skipped levels (restyle a lower level instead).
- Clean-up the pass itself created: dead styles, duplicate values, debug output.

## Do not touch

- The visual identity: palette, type families, layout topology, imagery direction.
- Copy that states facts or claims. Ask before changing it.
- Anything outside the named target. If the concept is wrong, say so and recommend `critique` or
  a redesign instead of smuggling one in.

## Steps

1. Read the context file and the tokens. Find two neighbouring screens for comparison.
2. Use the surface yourself at 360px, ~768px and 1280px (or the platform's device classes).
3. Triage in this order: broken or blocked tasks; missing states; flow and hierarchy drift;
   visual and motion inconsistencies; code clean-up. Do not perfect one corner while the rest stays
   below the bar.
4. Fix at the narrowest correct level (token, shared component, or local).
5. Rerun the detector on the target.

## Verify

- `ui_slop_detector.py <target> --context interface-context.md --fail-on advisory` exits 0 (drop
  `--context` when there is none), or every remaining finding carries a waiver with a reason.
- A keyboard pass reaches every control in visual order with a visible ring.
- Screenshots at each width show no overflow, clipped text or orphaned controls.
- The source diff contains only scoped changes; no accidental churn.

## Hand-off

None; polish closes the plan. If a critique report fed this pass, mark which of its issues are
now closed.
