---
name: interview-system-designer
description: >
  Design interview loops, competency rubrics and question banks, and check interviewer
  calibration. Use when designing an interview process, writing scorecards or questions,
  or reviewing hiring-bar drift and interviewer bias.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: hiring
  updated: 2026-11-08
  tags:
    - interviews
    - hiring
    - question-bank
    - calibration
    - competencies
---
# Interview System Designer

Design a structured interview loop for a role and level, write the questions and the rubric each interviewer scores against, and check afterwards whether interviewers are calibrated. The agent writes the questions; the scripts supply loop structure, rubric scaffolds and calibration statistics.

## When to Use

- Designing an interview process or loop for a role and seniority level.
- Writing competency-based questions, scorecards and 1-4 scoring anchors.
- Reviewing interview outcomes for calibration drift or interviewer bias.

Not for sourcing, ATS setup or offers (`hr-operations/talent-acquisition`), compensation (`hr-operations/hr-business-partner`), or onboarding (`engineering/codebase-onboarding`).

## Clarify First

Before designing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Role, level and team:** they set the rounds, time per round and what "meets the bar" means.
- **The three to five competencies that matter most** for this role, ideally from the team's leveling guide.
- **For calibration:** where the interview data comes from, how many records there are, and whether demographic fields may be used at all (legal and works-council rules differ by country).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Loop.** Run `loop_designer.py` for the role and level to get rounds, durations and scorecards; adjust rounds to the competencies the user named. Each competency should be assessed in at least one round, and no round should assess more than two.
2. **Questions.** Generate a first draft with `question_bank_generator.py`: it builds scenario questions from the role, competency and level (a senior engineer is asked about "the service you own", a staff engineer about "a system several teams depend on"), plus rubrics, follow-up probes and poor/good/great anchors. Then make each question specific to the team's real product and stack; a question about their actual scaling problem beats any stock scenario. Only competencies with no bundled scenarios fall back to templated questions, marked `"generic": true`; replace those.
3. **Rubric.** For each question, write what a 1, 2, 3 and 4 answer looks like at this level, in observable behaviour. Validate that two interviewers reading the anchors would score the same answer the same way.
4. **Calibrate** (after real interviews). Run `hiring_calibrator.py` on the results. Treat its bias figures as prompts for review, not findings: below about 50 records overall, or 30 per group, differences are noise, and the tool warns. Never use protected characteristics to score or rank candidates; analysing them for adverse impact may itself need legal sign-off.
5. **Verify** the loop before it goes live: checklist of every competency covered, every question has anchors, interviewers are trained on the rubric, and the debrief follows [references/debrief_facilitation_guide.md](references/debrief_facilitation_guide.md).

## Quick Start

```bash
python3 scripts/loop_designer.py --role "Senior Software Engineer" --level senior --team platform
python3 scripts/question_bank_generator.py --role "Frontend Engineer" --competencies react,typescript,system-design --num-questions 9 --format json
python3 scripts/scenario_stems.py --competency k8s --level staff     # preview the scenarios for one competency
python3 scripts/hiring_calibrator.py --input assets/sample_interview_results.json --analysis-type comprehensive --trend-analysis
```

## Tools Overview

| Tool | What it produces | Key flags |
|------|------------------|-----------|
| `scripts/loop_designer.py` | Rounds, durations, interviewer requirements, scorecards, calibration notes | `--role`, `--level`, `--team`, `--competencies`, `--input <role.json>` (a list uses its first entry) |
| `scripts/question_bank_generator.py` | Questions per competency with rubrics, probes and anchors; `--competencies` replaces the role defaults, duplicates and repeated questions are dropped; scenario questions come from `scripts/scenario_stems.py` (about 40 competencies plus aliases such as `ts`, `k8s`, `system_architecture`), and only competencies without stems get templated questions marked `"generic": true` | `--role`, `--level`, `--competencies`, `--question-types technical,behavioral,situational`, `--num-questions` |
| `scripts/hiring_calibrator.py` | Interviewer consistency, score distribution vs target, pass-rate drift, group disparity, recommendations | `--input <results.json>` (array), `--analysis-type comprehensive|bias|calibration|interviewer|scoring`, `--trend-analysis`, `--period` |

All three print to stdout by default and write files only with `--output <dir-or-file>`; `--format json|text|both`. Exit codes: 0 success, 2 bad input (missing file, invalid JSON, missing `--role`). The calibrator also warns on stderr when there are fewer than 50 records.

## Anti-Patterns

**Mistake:** Shipping the generated question bank as is.
**Why it happens:** It looks complete and has rubrics attached.
**Instead:** Replace every `"generic": true` question with one grounded in the team's real work, and keep the tool's anchors only where they fit.

**Mistake:** Reading a disparity figure from 20 interviews as proof of bias.
**Why it happens:** The report prints precise-looking percentages.
**Instead:** Collect enough data first, look at the individual debriefs, and involve HR or legal before acting on group-level numbers.

**Mistake:** Different questions for each candidate in the same loop.
**Why it happens:** Interviewers improvise to "get a feel" for the person.
**Instead:** Same core questions and anchors for every candidate at a level; follow-ups can vary. Unstructured interviews are where halo and similarity bias come from.

## Files

- `scripts/loop_designer.py`, `scripts/question_bank_generator.py`, `scripts/hiring_calibrator.py` — the tools above; `scripts/scenario_stems.py` — the scenario stems and level context the question bank fills in (add a competency there to stop it falling back to templated questions).
- `assets/sample_role_definitions.json` (8 roles), `assets/sample_interview_results.json` (20 interview records).
- `expected_outputs/` — reference outputs; `README.md` — longer tool walkthrough.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-templates.md](references/workflows-and-templates.md)** — quick start, the 3 core workflows (design loop / generate bank / calibrate bar) with validation checkpoints, engineering loop templates, sample questions, the scoring rubric + calibration benchmarks, and the anti-pattern list. Read when designing a loop or applying the rubric.
- **[references/tool-reference.md](references/tool-reference.md)** — full flag tables, examples, and output formats for all three tools, plus a troubleshooting table and the success-criteria bar. Read when invoking the tools or debugging output.
- **[references/competency_matrix_templates.md](references/competency_matrix_templates.md)** — competency matrix templates per role family and level. Read when defining the competencies a loop must cover.
- **[references/debrief_facilitation_guide.md](references/debrief_facilitation_guide.md)** — structured debrief facilitation guide. Read when running the post-loop debrief and consolidating scores.
- **[references/bias_mitigation_checklist.md](references/bias_mitigation_checklist.md)** — interview bias mitigation checklist. Read when reviewing a loop or panel for fairness.

## Scope & Limitations

Covers interview loop design for engineering, product, design and data roles from junior to principal, question and rubric design, and calibration analysis on exported interview results. It does not integrate with an ATS, and its statistics are descriptive: they do not establish legal compliance or prove bias.
