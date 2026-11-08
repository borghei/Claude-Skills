# critique — design review of one surface

**Job:** judge whether a surface is clear, specific to this product and well made, and name
the 3-5 problems that matter most. Critique edits nothing.

**Run when:** a surface has never been reviewed; the detector is clean but the page still feels
generic; before a large refine pass; after a redesign lands.

## By mode

- **Persuade / Showcase:** weight specificity, the first viewport, the path to the one action, and
  whether anything on the page could only belong to this product.
- **Operate / Read:** weight task completion, scan order, state coverage, wayfinding and density.
  Expression is judged as precision, not as volume.

## Change

Nothing. The output is a report.

## Do not touch

Source files, the context file, tokens. If you notice a one-line fix, list it; do not apply it.

## Steps

1. **Resolve the target** to a file path or route. A source path beats a dev-server URL because
   ports change and paths do not.
2. **Read the context file** (`interface-context.md`). Note the surface's mode and job. If there is
   no context file, say so in the report header and review against the product's own copy.
3. **Assessment A — design review, blind.** Read the source and, when a browser is available, look
   at the rendered page at a phone width and a desktop width. Do this before any detector output
   is in view; deterministic findings anchor judgment. Cover:
   - Specificity: could a competitor ship this layout, copy and palette unchanged?
   - Hierarchy: squint at it. Is there one obvious first thing, a second, then groups?
   - Task path: can the visitor do the surface's job without hunting? Count decision points with
     more than four visible options.
   - States: loading, empty, error, success, disabled, long content, permission-limited.
   - Copy: does every control name its outcome? Do errors say what failed and what to do?
   - Heuristics: score the ten usability heuristics 0-4 (see the scoring guide in
     `review-protocol.md`), marking any that cannot apply to this mode `n/a`.
4. **Assessment B — detector.** Run `ui_slop_detector.py <target> --context interface-context.md --format json`
   (without `--context` when there is no context file). Keep the output
   out of Assessment A. When subagents are available, run A and B as two separate subagents and
   merge only at synthesis (brief templates in `review-protocol.md`).
5. **Synthesize.** Where A and B agree, the finding is strong. Where B fired and A disagrees,
   check the source: name false positives explicitly. Where A found something B cannot see
   (hierarchy, specificity, copy tone), it stands on A's evidence.
6. **Write the report** from `assets/refinement-report-template.md`: method line, heuristic table,
   specificity verdict, what works (2-3), priority issues (3-5, P0-P3, each with the command that
   fixes it), persona red flags, then questions for the owner.
7. **End with the question.** Ask which issue to fix first. Nothing follows the question.

## Verify

- The report's first line states the method: `two assessments (A, B)` or
  `single context: <reason>` when the assessments could not be isolated.
- Every priority issue cites a file:line, a selector, or a rendered observation.
- Totals use the applicable maximum (4 x heuristics scored), never /40 over a partial set.
- Detector false positives are named, not silently dropped.

## Hand-off

The priority list becomes the plan: route each issue to its command, validate the plan with
`command_router.py --plan`, and finish with `polish`.
