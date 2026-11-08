# colorize — colour with a job

**Job:** use colour for hierarchy, meaning and atmosphere inside the established identity, and fix
contrast failures on the way.

**Run when:** the detector reports `low-contrast-pair`, `faint-gray-text`, `gray-on-color`,
`ai-hue-gradient` or `cream-ground`; a critique says "grey", "washed out", or "looks like every
other AI page".

## By mode

- **Persuade / Showcase:** colour may own large regions and carry the voice.
- **Operate / Read:** colour marks action, selection, status and wayfinding. Rarity gives the
  accent its force; a committed colour on the shell (rail, header) beats grey with one accent.

## Change

- **Roles, not swatches:** surface, raised surface, text, muted text, action, action text, focus,
  selection, border, success, warning, danger, info, and data series if needed. Every literal
  colour in source maps to a role or is removed.
- **Contrast:** body text 4.5:1, large text (24px, or 18.66px bold) 3:1, controls, icons and
  focus rings 3:1 against their surroundings. Utility greys at the 200-400 steps fail on white;
  muted text starts at the 500 step or a token proven with `ui_rules.py --contrast`.
- **Grey on colour:** secondary text on a coloured surface is a shade of that surface's hue, or
  white / near-black, never neutral grey.
- **Reflex palettes:** violet-to-blue/cyan/pink gradients and cream grounds chosen by habit are
  replaced by hues from the product's palette roles. Keep cream only when the brief chose it and
  the context file says why.
- **Meaning:** status colours never carry meaning alone; pair them with text, icon or position.
- **Themes:** design dark mode as its own composition (elevation by lighter surfaces, reduced
  chroma), not an inversion.
- **New palettes:** prefer OKLCH for derived ramps; lower chroma near white and black.

## Do not touch

- Confirmed brand colours in the context file. Adjust their use, not their values, unless the
  value fails contrast; then propose the nearest passing shade to the owner.
- Type, layout and copy.

## Steps

1. List every colour in the target (detector evidence plus a search for `#`, `rgb(`, `hsl(`,
   `oklch(`, utility colour classes). Map each to a role.
2. Prove each text/surface pair with `ui_rules.py --contrast`.
3. Write the role table into the context file if it is missing or stale.
4. Apply through tokens; theme switches remap roles, not components.

## Verify

- Detector `--scope color` exits 0 on the target.
- Every pair in the palette table passes, in both themes, including hover, disabled and
  text-on-image states.
- `context_linter.py` passes the Palette roles section.
- Grayscale screenshot: hierarchy and status still read without hue.

## Hand-off

`polish`.
