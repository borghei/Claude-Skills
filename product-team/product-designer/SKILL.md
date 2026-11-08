---
name: product-designer
description: >
  Turns user research into design decisions: journey maps with gap checks, SUS and task
  scoring, and heuristic design critique. Use when mapping a journey, scoring a usability
  test, or critiquing a flow before it ships.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: product-design
  domain: product-design
  updated: 2026-11-08
  tags: [ux, journey-mapping, usability-testing, sus, heuristic-evaluation, design-critique]
---

# Product Designer

The work between research and pixels: deciding which moment in a journey hurts most, whether a
flow is usable enough to ship, and which problems to fix first. Three tools do the arithmetic so
the conclusions rest on the input rather than on impressions. The journey mapper builds the map
from stages and flags low points nobody has an answer for. The usability scorer turns SUS
responses and task logs into scores, severities and a pass line. The critique tool grades a flow
against Nielsen's ten heuristics and a short accessibility pass, and orders the fixes by severity.

Report the tools' numbers and verdicts as printed. A score worked out by hand, or a grade that
does not match the exit code, is the failure this skill exists to prevent.

## When to use this skill

- **Mapping a journey** from interviews, tickets or analytics, and choosing the stage to fix first
- **Scoring a usability test**: SUS, completion rate, time on task, errors per task
- **Critiquing a flow or screen** before release, with severities a team can triage
- **Planning a usability test** with tasks, targets and a pass line agreed up front
- **Deciding whether a redesign worked**: the same tasks and SUS before and after

Choosing the visual system (palette, type, tokens) belongs to `product-team/design-direction`;
fixing an existing UI screen by screen belongs to `engineering/interface-refinement`. This skill
says *what* is wrong for users and how badly; those skills decide how it looks and apply the fix.

## Clarify First

Settle these before running anything. Ask about the two or three that would change the result;
default the rest and state the defaults at the top of the deliverable. If the user wants a result
straight away, run the tools on what they gave you and list your assumptions at the top.

- **Which decision this informs:** ship or hold a release, pick the stage to redesign, or compare
  two versions. It decides which tool leads and what counts as done.
- **What evidence exists:** interview notes, recordings, ticket counts, analytics. A journey map
  without evidence is a hypothesis; label it so (the mapper warns `no-evidence`).
- **Who the users are and how many were tested:** one group or several. Five people per group
  find frequent problems but give a directional SUS, not a benchmark.
- **The pass line:** the default is SUS 68 and no task under 75% completion. A regulated or
  high-stakes flow may need higher; agree it before the data comes in, not after.
- **Prototype or live build:** a prototype critique skips performance and real-data checkpoints;
  mark them unanswered rather than passing them.

## Quick Start

```bash
# Journey map from your own stages (exit 1 if a low point has no opportunity)
python3 product-team/product-designer/scripts/journey_mapper.py \
  --stages product-team/product-designer/assets/sample_journey.json

# Score a usability test (exit 1 if SUS < 68 or a task is under 75% completion)
python3 product-team/product-designer/scripts/usability_scorer.py \
  --sus-responses product-team/product-designer/assets/sample_sus.csv \
  --task-data product-team/product-designer/assets/sample_tasks.csv

# Heuristic critique: print the checklist, fill it in, score it (exit 1 on Critical or grade D/F)
python3 product-team/product-designer/scripts/design_critique.py --checklist --format json > checklist.json
python3 product-team/product-designer/scripts/design_critique.py \
  --answers product-team/product-designer/assets/sample_critique_answers.json
```

## Tools Overview

| Tool | Input | Output | Exit codes |
|------|-------|--------|------------|
| `journey_mapper.py` | `--template saas\|ecommerce\|mobile_app` or `--stages file.json` | Emotion curve, stage details, health metrics (average, lowest stage, biggest drops), findings | 0 mapped, 1 a stage at emotion <= 2 has no opportunity, 2 bad input |
| `usability_scorer.py` | `--sus-responses` CSV (participant, q1-q10) and/or `--task-data` CSV (participant, task, completed, time_seconds, errors); `sample [--out-dir DIR] [--force]` copies a borderline sample there (refuses to overwrite without `--force`) | Per-participant and aggregate SUS with grade, acceptability, spread and per-item averages; per-task completion, mean and median time, errors, severity | 0 SUS >= 68 and no task under 75%, 1 otherwise, 2 bad input |
| `design_critique.py` | `--checklist` or `--answers file.json` | Empty checklist (52 checkpoints), or compliance score, grade, severity distribution, top five priorities, strengths, all issues | 0 checklist or pass, 1 any Critical or grade D/F, 2 bad input |

All three are stdlib-only, offline and deterministic, and take `--format text|json` (`--json`
still works). Missing or out-of-range values exit 2 instead of being filled in: a neutral 3
silently substituted for a missing SUS answer would move the score. Scales, thresholds and file
formats are in `references/research-to-design-guide.md`.

## Workflows

### Journey map: find the stage to fix first

1. Write the stages as JSON (copy `assets/sample_journey.json`). Put the research behind it in
   `evidence`; each pain point should trace to something a user said or did.
2. Run the mapper. Read the lowest stage and the biggest drop first; those are the candidates.
3. Resolve every `unaddressed-low-point` by adding at least one opportunity, or state that the
   team accepts the low point and why. Exit 0 means every low point has an answer.
4. Hand the chosen stage and its opportunities to the next step: a test plan to confirm the
   problem, or a design brief.

**Done when:** the map names its evidence, exits 0, and one stage is chosen with a reason.

### Usability test: decide ship or hold

1. Fill `assets/usability-test-plan-template.md`, including the pass line, before testing.
2. Run the sessions; log one row per participant per task, and the SUS form after each session.
3. Score both files together. Report the mean with its range, not the letter grade alone; at
   six participants a 4-point difference is noise.
4. For each Major or Critical task, find the moment of failure in the recordings and log it in
   the critique as a failed checkpoint with notes.

**Done when:** the scorer's exit code and the decision agree, or the report says why they differ.

### Design critique: order the fixes

1. Print the checklist as JSON. Walk the real flow (or prototype) end to end, then mark each
   checkpoint `true`, `false` or leave it `null` if it does not apply at this fidelity.
2. Give every failure a numeric `severity` from 0 to 3 and a note that names the screen and what
   happens. 0 Cosmetic (no effect on success or time), 1 Minor (slows some users, they recover
   alone; also the value used when severity is left blank), 2 Major (many users slowed, some give
   up), 3 Critical (data loss, blocked task, or users excluded). Anything else exits 2. A failure
   without a note cannot be fixed by someone who was not there.
3. Score it. Fix all Critical issues before anything else; a Critical caps the grade at C.
4. Hand the ordered list on: visual or interaction fixes to `engineering/interface-refinement`,
   WCAG failures to `engineering/a11y-audit` for a full check.

**Done when:** the critique exits 0, or every Critical issue has an owner and a date.

### Before and after a redesign

Run the same tasks and SUS with the same participant profile on both versions, score each, and
compare per-task completion first. **[RECOMMENDED]** Treat a SUS change under about 10 points at
small samples as inconclusive unless completion or errors moved too.

## Decision frameworks

| Question | Tool to lead with | Why |
|----------|-------------------|-----|
| Where in the experience do users struggle? | Journey mapper | Shows the stage and transition, across touchpoints |
| Can users complete this flow? | Usability scorer (tasks) | Completion and errors are behaviour, not opinion |
| How do users rate the whole product? | Usability scorer (SUS) | Standard ten items, comparable across releases |
| What is wrong with this screen and how bad? | Design critique | Severity-ranked list a team can triage |

- **[PROVEN]** Behaviour over opinion: when task completion and SUS disagree, trust completion.
- **[PROVEN]** Severity is frequency x impact x persistence; a rare, recoverable issue is Minor
  even if it annoys the reviewer.
- **[RECOMMENDED]** Critique before testing, so participant time is spent on problems a review
  could not find.

## Anti-Patterns

### The Persona-Free Journey
**Mistake:** A journey map written in a workshop from memory, presented as research.
**Why it happens:** Workshops feel collaborative and finish in an afternoon.
**Instead:** Fill `evidence` and trace each pain point to a source; the mapper warns when it is
missing. Label an unsourced map a hypothesis.

### Grading by the Letter
**Mistake:** "We got a B" with no score, range or participant count.
**Why it happens:** Letters are easy to repeat in a status update.
**Instead:** Report mean, range and n. At small samples the letter can flip on one participant.

### Moving the Pass Line After the Data
**Mistake:** Lowering the SUS target or completion threshold once results come in.
**Why it happens:** A release date is close and the result is near the line.
**Instead:** Agree the pass line in the test plan. If the team ships below it, write that down
as an accepted risk.

### Passing What You Did Not Check
**Mistake:** Marking checkpoints `true` because the prototype cannot show them.
**Why it happens:** A blank looks like an unfinished review.
**Instead:** Leave them `null`. The tool reports them as unanswered and scores only what was
reviewed.

### Severity by Annoyance
**Mistake:** Rating issues by how much they bothered the reviewer.
**Why it happens:** The reviewer is the only user in the room.
**Instead:** Rate on how many users hit it, whether they recover, and whether it repeats.

## Files

| File | Purpose |
|------|---------|
| `scripts/journey_mapper.py` | Journey map, health metrics, low-point findings |
| `scripts/usability_scorer.py` | SUS and task metrics with a pass line |
| `scripts/design_critique.py` | Heuristic checklist and severity-ranked critique |
| `references/research-to-design-guide.md` | Severity scale, SUS bands, task thresholds, input formats, sample sizes |
| `references/heuristics.json` | Checklist wording: 10 heuristics, 3 accessibility groups, severity scale |
| `references/journey-templates.json` | SaaS, e-commerce and mobile app journey templates |
| `references/sus-questions.json` | The ten SUS items |
| `assets/sample_journey.json` | Sound journey with evidence (exit 0) |
| `assets/sample_journey_flawed.json` | Journey with unaddressed low points (exit 1) |
| `assets/sample_sus.csv`, `assets/sample_tasks.csv` | Sound test: SUS 80.4, all tasks 100% (exit 0) |
| `assets/sample_sus_flawed.csv`, `assets/sample_tasks_flawed.csv` | Failing test: SUS 44.6, checkout 40% (exit 1) |
| `assets/sample_sus_borderline.csv`, `assets/sample_tasks_borderline.csv` | Source for `sample`, which copies them to `--out-dir` (default: current directory) as `sample_sus.csv` / `sample_tasks.csv`, refusing to overwrite unless `--force`: SUS 67.5, just under the line (exit 1) |
| `assets/sample_critique_answers.json` | Sound critique: 94.2%, grade A (exit 0) |
| `assets/sample_critique_answers_flawed.json` | Failing critique: 61.5%, five Critical issues (exit 1) |
| `assets/usability-test-plan-template.md` | Test plan with tasks, targets and pass line |

## Integration Points

| Skill | Its job, distinct from this one |
|-------|---------------------------------|
| `product-team/design-direction` | Chooses the design system (style, palette, type, tokens) from a brief |
| `engineering/interface-refinement` | Refines an existing UI with a detector and named commands |
| `engineering/design-auditor` | Grades a built UI's visual quality |
| `engineering/a11y-audit` | Full WCAG scan of built pages |
| `engineering/marketing-site-builder` | Builds marketing sites, with a finish gate |
| `product-team/ui-design-system` | Generates token files and component documentation |
| `engineering/senior-frontend` | Implements the fixes in the component library |
| `product-team/ux-researcher-designer` | Personas and research planning that feed the journey map |

## Scope & Limitations

**In Scope:**
- Journey maps from research, with low-point and evidence checks
- SUS scoring and task metrics from usability sessions, with a pass line
- Heuristic critique with severity ranking and a short accessibility pass
- Usability test planning

**Out of Scope:**
- Visual direction, palettes, type and tokens (`product-team/design-direction`)
- Applying UI fixes or scanning source code (`engineering/interface-refinement`)
- WCAG conformance testing (`engineering/a11y-audit`)
- Running sessions, recruiting, analytics collection, A/B test analysis
  (`product-team/ab-test-setup`)

**Important Caveats:**
- Emotion scores in a journey map are the team's synthesis, not a measurement.
- SUS bands are simplified; quote the number. Small samples give wide ranges.
- The critique scores what a reviewer marked. It finds nothing on its own; its value is a
  consistent checklist and an honest severity order.
