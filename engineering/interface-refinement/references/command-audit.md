# audit — technical quality score

**Job:** measure what can be measured in the implementation and score it on five dimensions so
the team knows where the surface stands. Audit reports; it does not fix.

**Run when:** before a release; when the detector reports a wide spread of findings (the router
says so); when a team wants a number to track across refine passes.

## Dimensions (score each 0-4)

| # | Dimension | What to check | 0 means | 4 means |
|---|-----------|---------------|---------|---------|
| 1 | Accessibility | contrast pairs, focus visibility, keyboard order, labels, headings outline, reduced motion | fails WCAG A | AA met everywhere, AAA in places |
| 2 | Performance | layout-property animation, `transition: all`, unbounded blur/shadow, unsized images, heavy fonts | visible jank on mid-range devices | lean, no layout work in motion |
| 3 | Theming | literal colours vs tokens, dark theme composed (not inverted), state colours stable | everything hard-coded | every colour a role token, both themes tested |
| 4 | Responsive | fixed widths, overflow at 360px, touch targets (24px minimum, 44px comfortable), text at 200% zoom | desktop only | fluid from 360px up, targets sized, zoom safe |
| 5 | Specificity | detector generic-family findings, repeated templates, interchangeable copy | template throughout | coherent, product-specific system |

Bands for the total out of 20: 18-20 ship with minor polish; 14-17 good, fix the weak dimension;
10-13 needs a planned pass; 6-9 major rework; 0-5 not shippable.

## Change

Nothing.

## Do not touch

Source and tokens. Record exceptions the team already decided (a waiver with a reason) as
"accepted", not as findings.

## Steps

1. Run `ui_slop_detector.py <target> --context interface-context.md --format json --fail-on advisory`
   and keep the JSON (drop `--context` when no context file exists yet, and say so).
2. The `off-system-*` findings are the theming evidence: literal colours, faces, sizes and radii
   that bypass the recorded system. Read the token files for anything the scan cannot see
   (values behind utility classes, runtime themes).
3. Check each dimension against source evidence. Use `ui_rules.py --contrast FG BG` for any colour
   pair you need to prove.
4. Tag each issue P0 (blocks a task), P1 (WCAG AA failure or major difficulty), P2 (annoyance with
   a workaround), P3 (polish). Keep P3s few; a long tail buries the P1s.
5. Name the patterns that repeat across files ("hard-coded greys in 14 components") separately
   from one-off defects.
6. Map every issue to one command. Order the detector's share with `command_router.py --report` on the
   JSON from step 1, then slot the issues only you found into the same triage order: access first,
   then structure, then expression and copy.

## Verify

- Every issue has a location (file:line or selector), an impact, and a command.
- No issue is reported from the detector without checking the source line.
- Positive findings are listed; they tell the next pass what to keep.

## Native surfaces

For iOS and Android, swap the dimensions for: accessibility (VoiceOver/TalkBack labels, Dynamic
Type / sp scaling), performance (dropped frames, main-thread work), appearance (dark mode,
increased contrast), platform conformance (navigation, back gesture, native controls, targets of
44pt / 48dp), adaptivity (size classes, orientation). See `native-platforms.md`. The web detector
does not read native code; do not report its empty result as clean.

## Hand-off

The ordered command list. End it with `polish`.
