# Research to Design: Scales, Thresholds and Input Formats

Reference for the three `product-designer` tools. SKILL.md carries the workflow; this file
carries the numbers and file formats behind it.

## Severity scale (design_critique.py)

| Value | Label | Use it when | Action |
|-------|-------|-------------|--------|
| 0 | Cosmetic | Noticed, no effect on task success or time | Fix when possible |
| 1 | Minor | Slows some users; they recover alone | Low priority fix |
| 2 | Major | Many users slowed or confused; some give up | Fix before next release |
| 3 | Critical | Data loss, blocked task, or an accessibility barrier that excludes users | Fix immediately |

Rate severity on three questions: how many users hit it, whether they can recover, and
whether it repeats every visit. A failed checkpoint with a blank severity counts as Minor.

Grade from the compliance score (passed / answered checkpoints):
A >= 90 and no Critical, B >= 80 and no Critical, C >= 65, D >= 50, F below. Unanswered
checkpoints (`"pass": null`) are left out of the score and reported as a count, so a partial
review is not graded as a failure. Gate: exit 1 on any Critical issue or grade D/F.

The checklist wording (10 Nielsen heuristics x 4 checkpoints, 3 accessibility groups x 4)
lives in `heuristics.json`. The accessibility group is a screen-level prompt, not a WCAG
audit; run `engineering/a11y-audit` for that.

## SUS (usability_scorer.py)

- Ten items, 1-5 each. Odd items contribute `score - 1`, even items `5 - score`; the sum
  times 2.5 gives 0-100. Item wording is in `sus-questions.json`.
- 68 is the commonly cited mean across published studies; the tool treats it as the gate.
- Bands used by the tool: A >= 80.3, B >= 68, C >= 51, D >= 35, F below. These are
  coarser than the Sauro-Lewis curved grading scale; quote the score, not only the letter.
- Acceptability: >= 70 acceptable, 50-69 marginal, < 50 not acceptable.
- With 5-8 participants the standard deviation is often 10-20 points. A mean of 66 vs 70
  is not a real difference; report the range alongside the mean.
- Standard deviation is the sample form (n-1, labelled `Std Dev (n-1)`; 0 for a single
  participant); median is the true median (mean of the two middle values for an even count).

## Task metrics (usability_scorer.py)

| Completion rate | Severity | Gate |
|-----------------|----------|------|
| >= 90% | None | pass |
| 75-89% | Minor | pass |
| 50-74% | Major | fail |
| < 50% | Critical | fail |

Time on task is averaged over completed attempts only; failed attempts still count toward
errors. Compare time against the target in the test plan, not against other tasks.

## Journey maps (journey_mapper.py)

JSON object with `name`, `persona`, `goal`, optional `evidence` (strongly recommended) and
`stages`. Each stage: `name`, `emotions: {score: 1-5, label}`, and lists `actions`,
`touchpoints`, `pain_points`, `opportunities`.

Findings:
- `unaddressed-low-point` (fail, exit 1): a stage scored 2 or lower with no opportunity.
- `unexplained-low-point` (warn): a stage scored 2 or lower with no pain point saying why.
- `no-evidence` (warn, custom maps only): nothing names the research behind the map.

Emotion scores are the team's synthesis of research, not a measurement. Anchor them:
1 = abandons or complains, 3 = neutral, 5 = would recommend unprompted. The three
templates in `journey-templates.json` are starting shapes for a workshop, not findings.

## Participant numbers

5 participants per distinct user group usually surface the most frequent problems in one
flow; they do not give a stable SUS or completion rate. For a benchmark number, use 12 or
more per group, or report the result as directional.
