# layout — grouping, rhythm and reading order

**Job:** turn product priority into reading order, grouping and space. Diagnose the structural
problem before moving boxes.

**Run when:** the detector reports `identical-card-row`, `icon-tile-stack` or
`monotonous-spacing`; a critique says "everything has the same weight" or "I can't tell what
belongs together".

## By mode

- **Persuade / Showcase:** asymmetric and intentionally uneven compositions are allowed when one
  element must lead.
- **Operate / Read:** predictable structure and stable density are affordances; keep them.

## Change

- **Lead element:** decide what leads. In a row of equal cards, one item becomes larger, first,
  or richer in content; the rest become a list or a lighter form.
- **Proximity before containers:** related items move closer; unrelated groups separate. Remove a
  box when spacing alone can show the group.
- **Rhythm:** tight steps inside a group, a larger step between groups, the largest between
  sections; more space above a heading than below it.
- **Scale:** values come from the spacing scale (a 4-based scale gives useful 12 and 20 steps).
- **Icon tiles:** the rounded tinted square above each heading goes; the icon sits inline with the
  heading or is replaced by something only this product can show.
- **Responsive structure:** reorder, collapse or reveal by priority, not by shrinking. Container
  queries for components used in different widths.
- **Order:** DOM order and focus order match the visual order.

## Do not touch

- The visual identity (palette, type families, imagery).
- Copy, except where a layout needs a shorter label; then hand it to `clarify`.
- Navigation model on operate surfaces without the owner's agreement.

## Steps

1. Squint at a screenshot. Write down the first, second and third things you see and the groups.
   Compare with what the context file says the surface's job is.
2. Write the spatial plan: lead element, groups, rhythm steps, what changes at each width.
3. Apply with `gap` for sibling rhythm and the scale tokens for everything else.

## Verify

- Detector `--scope layout` exits 0 on the target.
- Squint test now matches the intended order.
- Screenshots at 360px, ~768px and 1280px; nothing overflows; DOM order equals visual order
  (tab through it).
- Long content and empty states do not break the structure.

## Hand-off

`polish`.
