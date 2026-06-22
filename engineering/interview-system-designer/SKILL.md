---
name: interview-system-designer
description: >
  Design calibrated interview loops, competency-based question banks, and hiring calibration.
  Use when designing interview processes, creating hiring pipelines, generating scoring
  rubrics, analyzing interviewer bias, or building question banks.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  updated: 2026-06-17
---
# Interview System Designer

Design role-specific interview loops, generate competency-based question banks with scoring rubrics, and detect interviewer bias through statistical calibration analysis.

## Core Capabilities

- **Interview loop design** — role/level/team-specific loops with rounds, time allocations, interviewer skill requirements, and scorecard templates.
- **Question bank generation** — competency-based questions with 1-4 scoring rubrics, follow-up probes, and poor/good/great calibration examples.
- **Hiring calibration** — statistical bias and drift detection across interviewers and time periods, with coaching recommendations.
- **Scoring & benchmarks** — 4-point rubric, target score distribution (20/40/30/10), interviewer-consistency and pass-rate benchmarks.
- **Loop templates** — junior/senior/staff+ engineering loops plus sample questions by level and STAR behavioral prompts.
- **Bias guardrails** — anti-pattern catalog (halo effect, similarity bias, unstandardized loops) and mitigation practices.

## When to Use

- Designing an interview process or end-to-end hiring pipeline for any seniority level.
- Building a competency-based question bank with scoring rubrics.
- Generating scorecards, debrief guides, or interviewer assignments.
- Analyzing interviewer bias or calibration drift across candidates and time.

## Clarify First

Before designing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — design an interview loop, generate a question bank, or calibrate hiring (selects `loop_designer.py` vs `question_bank_generator.py` vs `hiring_calibrator.py`)
- [ ] **Role & level** — the role and seniority (junior/senior/staff+) (drives loop rounds, time allocation, and rubric calibration via `--role`/`--level`)
- [ ] **Competencies** — which competencies the loop or questions must cover (sets `--competencies` and the question-bank scope)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

The Python tools live at the skill root (not in `scripts/`). All support `--help`, JSON/text output.

| Tool | Purpose | Command |
|------|---------|---------|
| `loop_designer.py` | Generate a calibrated interview loop (rounds, time, scorecards) | `python loop_designer.py --role "Senior Software Engineer" --level senior --team platform --output loops/` |
| `question_bank_generator.py` | Generate competency-based questions with rubrics + calibration examples | `python question_bank_generator.py --role "Frontend Engineer" --competencies react,typescript,system-design --num-questions 30` |
| `hiring_calibrator.py` | Detect bias/calibration drift across interviewers and periods | `python hiring_calibrator.py --input interview_data.json --analysis-type comprehensive --trend-analysis` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-templates.md](references/workflows-and-templates.md)** — quick start, the 3 core workflows (design loop / generate bank / calibrate bar) with validation checkpoints, engineering loop templates, sample questions, the scoring rubric + calibration benchmarks, and the anti-pattern list. Read when designing a loop or applying the rubric.
- **[references/tool-reference.md](references/tool-reference.md)** — full flag tables, examples, and output formats for all three tools, plus a troubleshooting table and the success-criteria bar. Read when invoking the tools or debugging output.
- **[references/competency_matrix_templates.md](references/competency_matrix_templates.md)** — competency matrix templates per role family and level. Read when defining the competencies a loop must cover.
- **[references/debrief_facilitation_guide.md](references/debrief_facilitation_guide.md)** — structured debrief facilitation guide. Read when running the post-loop debrief and consolidating scores.
- **[references/bias_mitigation_checklist.md](references/bias_mitigation_checklist.md)** — interview bias mitigation checklist. Read when reviewing a loop or panel for fairness.

## Scope & Limitations

**This skill covers:**
- Designing end-to-end interview loops for engineering, product, design, and data roles across all seniority levels (junior through principal)
- Generating competency-based question banks with structured scoring rubrics and calibration examples
- Detecting statistical bias and calibration drift across interviewers and time periods
- Producing scorecard templates, debrief guides, and interviewer assignment recommendations

**This skill does NOT cover:**
- Applicant tracking system (ATS) integration, job posting, or candidate sourcing pipeline management — see `hr-operations/talent-acquisition`
- Compensation benchmarking, offer negotiation strategy, or total rewards analysis — see `hr-operations/hr-business-partner`
- Workforce planning, headcount modeling, or organizational design — see `hr-operations/people-analytics`
- Post-hire onboarding program design or new-hire ramp-up tracking — see `engineering/codebase-onboarding`

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `hr-operations/talent-acquisition` | Feed designed interview loops and scorecards into the talent acquisition pipeline for end-to-end hiring execution | Loop JSON output → talent acquisition workflow input |
| `hr-operations/people-analytics` | Supply calibration reports and interviewer performance data for workforce-level hiring analytics | Calibrator JSON reports → people analytics dashboards |
| `engineering/codebase-onboarding` | Hand off hired candidate profiles and assessed competency gaps to onboarding plan generation | Scorecard results → onboarding skill-gap inputs |
| `hr-operations/hr-business-partner` | Provide interview quality metrics and pass-rate data to support hiring bar discussions with HR leadership | Calibration trend data → HRBP quarterly reviews |
| `product-team` | Align PM interview loop competencies with the product team's competency frameworks and role leveling guides | Competency matrix → PM loop designer `--competencies` input |
| `engineering/pr-review-expert` | Use coding round evaluation criteria to inform code review standards for new hires during their ramp period | Scoring rubric technical criteria → PR review checklist alignment |
