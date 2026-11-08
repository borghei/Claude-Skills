# typeset — hierarchy, readability and a type decision

**Job:** make type carry hierarchy and voice inside the existing visual world: clear roles, a real
scale, comfortable reading, and faces chosen for a reason.

**Run when:** the detector reports `gradient-text`, `kicker-above-heading`, `italic-serif-display`,
`overused-face`, `default-font-stack`, `tiny-text`, `tight-body-leading`, `wide-body-tracking`,
`crushed-tracking`, `justified-text`, `everything-bold`, `all-caps-body`, `oversized-headline` or
`flat-type-hierarchy`; a critique says "flat" or "everything
looks the same".

## By mode

- **Persuade / Showcase:** display type may carry the voice; decisive size steps; responsive display
  sizes are welcome.
- **Operate / Read:** one well-tuned family is often right; fixed role scale; body at 16px (14px
  for dense data views); measure 60-75 characters for reading.

## Change

- **Roles first:** name the roles the surface needs (display, heading, body, label, figures,
  code). Each role is one size, weight, line height and tracking, used identically everywhere.
- **Scale:** adjacent roles differ by at least ~1.2x in size, or by size and weight together.
- **Emphasis:** solid colour plus weight or size. Gradient-filled text goes.
- **Eyebrows:** delete the label above the heading, or fold its information into the heading.
- **Weight:** body and secondary text return to regular; heavy weights stay on headings and the
  one figure per block that matters.
- **Reading:** body line height 1.45-1.7; tracking at the face's default for lowercase text;
  display tracking no tighter than -0.03em; `text-wrap: balance` on headings and `pretty` on body.
- **Numbers:** tabular numerals in tables and anywhere figures are compared.
- **Faces:** if the face is a reflex default, propose two alternatives with a reason each (voice,
  legibility at the sizes used, script coverage, licence). Changing the face is the owner's call;
  record it in the context file's Type roles.

## Do not touch

- A face the context file binds (brand commitment). Improve its use instead.
- Layout topology and colour roles.
- Zoom and user font settings: never lock font sizes in px on `html`.

## Steps

1. Inventory every font-size, weight, line-height and letter-spacing in the target's styles; map
   each to a role or mark it a one-off.
2. Write the role table before editing (role, size, line height, weight, tracking).
3. Apply through tokens or shared classes; delete one-offs.
4. Test the longest real heading at 360px and the body at 200% zoom.

## Verify

- Detector `--scope type` exits 0 on the target, or remaining hits carry waivers with reasons.
- Squint test: heading, body, label and metadata are distinguishable without reading.
- Body measure is 45-75 characters at desktop width.
- No invisible-text flash or large reflow when fonts load (`font-display: swap` plus a
  metric-compatible fallback).

## Hand-off

`polish`.
