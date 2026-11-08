# Usability Test Plan: <flow name>

## Decision this test informs
<One sentence: what we will change, ship or drop depending on the result.>

## Objectives
- <Can users complete <task> in under <time>?>
- <Where in <step> do users hesitate or make errors?>

## Participants
- <N> participants (5-8 per distinct user group), screened for <persona criteria>
- Mix: <new vs returning, device split, assistive-technology users if the flow is public>

## Tasks
Write each task as a goal in the participant's words, never naming the UI control.

| # | Task prompt | Success means | Completion target | Time target |
|---|-------------|---------------|-------------------|-------------|
| 1 | "<goal>" | <observable end state> | 90%+ | < <n>s |
| 2 | "<goal>" | <observable end state> | 90%+ | < <n>s |
| 3 | "<goal>" | <observable end state> | 80%+ | < <n>s |

## Measures
- Completion, time on task (completed attempts only) and errors per task: `task_data.csv`
  with columns `participant,task,completed,time_seconds,errors`
- SUS after the session: `sus.csv` with columns `participant,q1..q10` (each 1-5)
- Observed issues, each with a heuristic id and a severity 0-3 (critique checklist)

## Pass line
- SUS mean 68 or above, and no task under 75% completion (`usability_scorer.py` exits 0)
- No Critical issue open in the critique (`design_critique.py` exits 0)

## Logistics
- Moderator / note-taker:
- Prototype or build version:
- Dates and recruitment source:
