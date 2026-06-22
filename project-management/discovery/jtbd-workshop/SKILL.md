---
name: jtbd-workshop
description: >
  Run a full Jobs-To-Be-Done discovery workshop with switch interviews,
  forces-of-progress mapping, ODI outcome scoring, and opportunity statements
  across 2hr, 4hr, and 8hr formats.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-discovery
  updated: 2026-06-15
  tech-stack: jobs-to-be-done, switch-interviews, forces-of-progress, odi
---
# JTBD Workshop Expert

## Overview

Run a Jobs-To-Be-Done (JTBD) workshop end-to-end. This skill is the workshop facilitation companion to the `execution/job-stories/` skill (the *writing format* for backlog stories). Where `job-stories/` produces When/Want/So statements for individual backlog items, this skill produces the *upstream discovery output* -- the job hierarchy, the forces driving switching behavior, and the desired-outcome statements that anchor product strategy.

The workshop synthesizes four JTBD schools: Christensen's *milkshake* hiring frame, Ulwick's Outcome-Driven Innovation (ODI) with importance/satisfaction scoring, Klement's situation-motivation-outcome canvas (the *job story* format), and Moesta's switch interview method surfacing the four forces of progress (push, pull, anxiety, habit). A well-run workshop produces three artifacts: a ranked job hierarchy with measurable outcome statements, a forces-of-progress map, and a prioritized opportunity list ready to feed PRDs, OKRs, or roadmap themes.

## Core Capabilities

- **Workshop facilitation** -- 2hr / 4hr / 8hr agendas with time-blocked outcomes
- **Switch interviews** -- four-anchor timeline script (First Thought -> Passive -> Active -> Deciding -> First Use)
- **Forces-of-progress mapping** -- push, pull, anxiety, habit canvas and the switch equation
- **ODI outcome scoring** -- Ulwick outcome statements with Importance x Satisfaction opportunity scores
- **Handoff** -- opportunity statements into assumptions, experiments, PRDs, and roadmap themes

## When to Use

- **New product or new segment.** Understand the underlying progress customers are trying to make before building.
- **Pivot or strategy reset.** Team is stuck debating features; re-ground in the customer's job.
- **Pre-roadmap.** Define the job hierarchy before committing to a quarterly or annual roadmap.
- **Stalled adoption.** Customers signed up but did not retain; switch interviews reveal which forces went wrong.
- **Onboarding a new product team.** Create a shared mental model of what the customer is hiring the product to do.

## Clarify First

Before planning the workshop, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Format** — 2h validation / 4h half-day / 8h full-day (sets the agenda depth; 2h is validation, not primary discovery)
- [ ] **Target segment** — JTBD is segment-by-job, not persona-by-demographic (defines who you study and which job hierarchy you build)
- [ ] **Switch-interview access** — can you recruit recent (90-day) switchers (without customer voice the forces canvas and ODI scores become team-aligned fiction)
- [ ] **Trigger/purpose** — new product / pivot / stalled adoption (shapes which of the four forces to emphasize)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

1. Pick a format (2h validation / 4h half-day / 8h full-day) by stakes and availability; define the segment.
2. Recruit 6-12 recent (90-day) switchers and run pre-work switch interviews.
3. Facilitate the agenda; build the job hierarchy, score outcomes (Importance x Satisfaction), fill the forces canvas.
4. Convert top-scored outcomes into opportunity statements (`<verb> <object> <context>`) with named owners.
5. Hand off to `identify-assumptions/`, `brainstorm-experiments/`, or `create-prd/`. Revisit quarterly.

## References

Load the reference that matches the task -- keep this file lean and pull detail on demand:

- **[references/facilitation-playbook.md](references/facilitation-playbook.md)** -- the full operational playbook: 2h/4h/8h agendas, switch interview script, forces canvas, ODI outcome format, common traps, the 10-step workflow, troubleshooting, and success criteria. Read this when planning or running a workshop.
- **[references/jtbd-method-guide.md](references/jtbd-method-guide.md)** -- full JTBD methodology (Christensen, Ulwick, Klement, Moesta) with worked examples. Read this when you need the theory behind the workshop activities.
- **[references/red-flags.md](references/red-flags.md)** -- 12 JTBD anti-patterns (solution-coded jobs, missing forces, speculation without switch interviews) with symptoms and fixes. Read this when reviewing or QA-ing workshop output.

Workshop templates live in `assets/`: `workshop_agenda_2hr.md`, `workshop_agenda_4hr.md`, `workshop_agenda_8hr.md`, `pre_work_email.md`, `switch_interview_script.md`, `forces_of_progress_canvas.md`.

## Scope & Limitations

**In scope:** 2h/4h/8h formats; switch interview script and four-anchor timeline; forces-of-progress mapping; Ulwick outcome statements with Importance x Satisfaction scoring; Klement situation-motivation-outcome decomposition (bridge to `execution/job-stories/`); pre-work email and participant brief.

**Out of scope:** writing individual backlog stories (`execution/job-stories/`); quantitative ODI surveying at scale; recording/transcription tooling; recruiting operations; personas (JTBD is segment-by-job, not persona-by-demographic).

**Caveats:** switch interviews require *recent* (90-day) switchers; the 2-hour format is for validation, not primary discovery; ODI scoring is sensitive to who is in the room (internal scores are hypotheses, customer-derived scores are truth); a workshop without customer voice produces team-aligned fiction.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `discovery/customer-interview-script/` | Receives from | Switch interviews use the base interview script structure |
| `discovery/interview-synthesis/` | Receives from | Synthesized themes seed the snippet wall on workshop day |
| `discovery/identify-assumptions/` | Feeds into | Top outcomes become assumptions to test |
| `discovery/brainstorm-experiments/` | Feeds into | Forces-of-progress weaknesses become experiment hypotheses |
| `discovery/value-proposition-canvas/` | Feeds into | Jobs, pains, gains populate the Customer Profile |
| `execution/job-stories/` | Feeds into | Job + outcome decomposition becomes When/Want/So backlog stories |
| `execution/create-prd/` | Feeds into | Job hierarchy populates PRD Section 5; outcomes populate Section 6 |
| `execution/outcome-roadmap/` | Feeds into | Top desired outcomes become roadmap themes |
| `execution/north-star-metric/` | Feeds into | The highest-priority outcome often becomes the input metric tree root |
