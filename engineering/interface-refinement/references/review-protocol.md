# Review protocol: isolated assessments, finish review, waivers

## Why two assessments

Deterministic findings anchor judgment. A reviewer who has seen "14 findings, 3 nested cards"
reviews the 14 findings and stops looking at hierarchy, specificity and fit. So a critique runs
two assessments that never see each other until synthesis:

- **A — design review:** source and rendered page, judged as a design lead would.
- **B — detector:** `ui_slop_detector.py` output, each hit checked against the source line.

When subagents are available, run A and B as two separate subagents in parallel (for a desktop app
with one window, run A, wait, then B, so they do not fight over the window). Without subagents,
finish and write down A before running B, and say `single context: <reason>` in the report's
first line. A degraded run that does not say so is a failed run.

### Brief for subagent A (paste and fill)

```
Review <target path> as a design lead. Product context: <path to interface-context.md>.
Surface mode: <mode>. Do not run any detector or linter and do not read detector output.
Return: specificity verdict (could another product ship this unchanged? why), heuristic scores
0-4 with one-line evidence each (n/a allowed with reason), 2-3 things that work, 3-5 priority
issues tagged P0-P3 with file:line or rendered evidence, persona red flags for 2-3 personas,
and 2 provocative questions. Edit nothing.
```

### Brief for subagent B

```
Run: python3 <skill>/scripts/ui_slop_detector.py <target> [--context <interface-context.md>] --format json --fail-on advisory
Then open every finding's file:line and mark it confirmed or false positive with one line of
reasoning. Return counts by rule and severity, the confirmed list, the false positives, and any
file the detector could not read. Edit nothing.
```

## Heuristics scoring guide (0-4)

| # | Heuristic | 4 looks like | 0-1 looks like |
|---|-----------|--------------|----------------|
| 1 | Visibility of state | every action acknowledged within 100ms; progress shown for waits | silent saves, spinners with no context |
| 2 | Match with the real world | the user's words, real-world order | internal codes and jargon |
| 3 | Control and freedom | undo, cancel, back everywhere | destructive actions with no way out |
| 4 | Consistency | same words and controls for the same things | three button styles for one action |
| 5 | Error prevention | constraints and defaults stop mistakes | free text where a picker belongs |
| 6 | Recognition over recall | options visible, recent items offered | users must remember codes between screens |
| 7 | Flexibility | shortcuts and bulk actions for experts | eight clicks for the daily task |
| 8 | Minimal design | every element earns its place | equal-weight clutter, decoration |
| 9 | Error recovery | errors say what, why, what now | "Something went wrong" |
| 10 | Help | contextual help where questions arise | none, or a PDF |

Heuristics 7 and 10 may be `n/a` on persuade and showcase surfaces. The total's maximum is 4 x the
number scored. Most real interfaces land between 55% and 80% of their maximum; a 4 means
genuinely excellent.

## Personas for red flags

Pick two or three by surface: a **power user** (keyboard, bulk work, impatience), a **first-timer**
(no product vocabulary, low confidence), a **keyboard and screen-reader user**, a **stress tester**
(long names, empty data, slow network, double clicks), a **one-handed phone user** (outdoors,
interrupted). Add one from the context file's Users section. For each, walk the primary task and
list what broke, by element. No generic persona prose.

## Severity

- **P0 blocking:** a task cannot be completed, data can be lost, state is misleading.
- **P1 major:** WCAG AA failure or significant difficulty.
- **P2 minor:** an annoyance with a workaround.
- **P3 polish:** no real user impact. Keep these few.

## Finish review (after a refine plan)

A fresh reviewer, outside the thread that did the work, reads the before/after screenshots, the
diff, the context file and the craft floor, and returns one word first:

| Disposition | When |
|-------------|------|
| `re-evidence` | screenshots are missing, blank, the wrong surface or the wrong width |
| `rework` | the change replaced the identity, or broke scope (edits outside the target) |
| `fix` | one or more material fixes remain; list them, most material first, at most eight |
| `ship` | no material fixes and no floor refusal visible |

The word is derived from the checks, never felt. A refused element from the craft floor is a
material fix even if the owner's mock-up contained it.

## Waivers (inline ignores)

The detector honours `ui-refine-ignore <rule> -- <reason>` (this line and the next) and
`ui-refine-ignore-file <rule|*> -- <reason>`. A waiver without a reason is rejected and reported.

1. **Real problem:** fix it. Never waive to get a gate green.
2. **Confident false positive or confirmed exception:** waive the narrowest scope (one line, one
   rule) and name the evidence in the reason: `-- owner confirmed: literal ball-bounce animation`.
   Write "owner confirmed" only when the owner did.
3. **Unsure:** leave the finding standing and say why in one line.

File-wide waivers are for fixtures, generated files and deliberate before/after demos. Never use
`*` on a real product surface.
