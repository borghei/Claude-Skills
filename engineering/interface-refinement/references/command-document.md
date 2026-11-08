# document — record the visual system that actually shipped

**Job:** write the `## Visual system` half of the context file from the code as it is, so later
commands extend the real system instead of inventing a parallel one.

**Run when:** code exists but the context file has no visual system; the recorded system has
drifted from the code; before a large refine pass, to capture the current state.

## What to record

| Subsection | Format | Source of truth |
|------------|--------|-----------------|
| Palette roles | `- role: <colour>` (surface, text, text-muted, action, action-text, danger ...) | CSS custom properties, theme file, most-used literals |
| Type roles | `- body: <family>, <size>px/<line-height>, <weight>` per role | computed styles of real elements |
| Spacing scale | `- steps: 4, 8, 12, 16, 24, 40` | padding / margin / gap values actually reused |
| Radius | `- control: 6px`, `- container: 8px` | border-radius values reused |
| Elevation | `- resting: ...`, `- raised: <shadow>` and where each is allowed | box-shadow and border values reused |
| Layout | content width, prose measure, grid and breakpoints | containers and media queries |
| Components | one line per shared control: shape, states, the rule it follows | the component library or the most-reused markup |
| Motion | durations, easing, reduced-motion behaviour | transitions and keyframes |
| Named rules | `- **The <Name> Rule.** <one-sentence doctrine>` | patterns the code applies consistently |
| Refusals | detector rule ids this product refuses | the owner's decisions and the craft floor |

## Change

Only the `## Visual system` section of `interface-context.md`.

## Do not touch

- Source code. Document records; it does not repair. Report drift instead of fixing it.
- An existing visual system section without asking: offer refresh, overwrite or merge.
- The product half.

## Rules for writing it

- Record only what is reused. A value used once is a one-off, not a token.
- Write roles by purpose (`text-muted`), not by value (`gray-500`).
- **Never canonise a defect.** A side stripe, an eyebrow label, gradient text or a glow found in
  the code goes in the report as drift, never into Named rules. Writing it down turns one
  violation into house style.
- Check each refusal against the product's own materials: do not refuse a device the brief
  actually chose (a print-heritage product may keep its cream paper).
- Prove every text/surface pair you record passes contrast; if one fails, record it and flag it.

## Steps

1. Collect tokens and literals: `ui_slop_detector.py <src> --format json` for the defect list,
   plus a search of style files for custom properties, colours, sizes and radii.
2. Group values into roles; drop one-offs.
3. Write the section; list drift and defects in the report, not in the file.
4. Lint, then scan with the new file so drift shows up as findings rather than memory:
   `ui_slop_detector.py <src> --context interface-context.md --scope color,type,surface`.
   Every `off-system-*` hit is either a value you missed (add it) or drift (report it; `extract`
   fixes it).

## Verify

```bash
python3 scripts/context_linter.py --input interface-context.md --strict
```

Exit 0, and every recorded value can be found in the code.

## Hand-off

The refine command the request needs, now reading a real system.
