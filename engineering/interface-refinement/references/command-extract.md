# extract — bring drift back into the system

**Job:** turn repeated literals and near-duplicate components into tokens and shared components,
then move existing uses onto them, so the next edit changes one place instead of twelve.

**Run when:** the detector, run with `--context interface-context.md`, reports `off-system-color`,
`off-system-font`, `off-system-radius` or `off-system-font-size`; a critique finds the same
control built three different ways; a team asks why two screens of one product look unrelated.

## By mode

- **Operate / Read:** extraction pays most here. Tables, fields, toolbars, empty states and status
  labels repeat on every screen; consistency is the brand.
- **Persuade / Showcase:** extract the shell (buttons, links, type roles, section spacing). Leave
  one-off section art alone: a hero composition is allowed to be unique.

## What to extract

| Signal | Becomes | Threshold |
|--------|---------|-----------|
| The same literal colour, size, radius or duration in three or more places with one job | a token named by purpose (`--text-muted`, `--radius-control`) | 3 uses, same intent |
| Three or more hand-built versions of one control | one component with variants | same job, not just same look |
| Repeated font-size + weight + line-height combination | a type role | 3 uses |
| Repeated easing + duration pair | a motion token | 2 uses |
| A value one step off an existing token (13px next to a 12px/14px scale, `#1c2531` next to `#1b2430`) | the existing token | always: snap, do not mint |

Two things that look alike but do different jobs stay separate (a destructive button and a primary
button may share a shape and nothing else).

## Change

- Token definitions in the project's existing token location (custom properties, theme file, or
  the utility-class config). If none exists, ask where they should live before creating one.
- Call sites in the named target, moved onto the new tokens and components.
- The context file's `## Visual system` entries for every token you add.

## Do not touch

- Visual output. Extraction is a refactor: before and after screenshots must match, except where
  a near-duplicate value snapped to its token (list each one).
- Code outside the target. Report other call sites; migrate them in a separate step.
- Values with no repeat. A one-off stays a literal; a token per value is noise.
- Naming conventions the project already uses.

## Steps

1. Run the detector with the context file and list off-system values by count:
   `ui_slop_detector.py <target> --context interface-context.md --rules off-system-color,off-system-font,off-system-radius,off-system-font-size --format json`.
2. Group by intent. For each group decide: snap to an existing token, mint a new token, or leave as
   a recorded exception (waive with a reason).
3. Write the tokens and components first, then migrate call sites one family at a time.
4. Delete the dead code paths the migration leaves behind.
5. Add each new token to `interface-context.md` and lint it.

## Verify

- Detector with `--context` on the target: no remaining `off-system-*` findings, or each one waived
  with a reason.
- Screenshots before/after at 360px and 1280px match, apart from the listed snaps.
- `context_linter.py --input interface-context.md --strict` exits 0.
- Search the diff for the old literals: each remaining hit is an intended exception.

## Hand-off

`polish`, or the refine command the request needs, now working on one system.
