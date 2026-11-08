---
name: jtbd-workshop
description: >
  Plans and runs a 2, 4 or 8-hour Jobs-To-Be-Done workshop: switch interviews, forces of
  progress, scored outcome statements. Use when you need to know why customers switch,
  or to ground strategy in jobs before writing PRDs.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-discovery
  updated: 2026-11-08
  tech-stack: jobs-to-be-done, switch-interviews, forces-of-progress, odi
  tags:
    - jobs-to-be-done
    - switch-interviews
    - odi
    - workshop
    - discovery
---
# JTBD Workshop Expert

## Overview

Run a Jobs-To-Be-Done (JTBD) workshop end-to-end. This skill is the workshop facilitation companion to the `execution/job-stories/` skill (the *writing format* for backlog stories). Where `job-stories/` produces When/Want/So statements for individual backlog items, this skill produces the *upstream discovery output* -- the job hierarchy, the forces driving switching behavior, and the desired-outcome statements that anchor product strategy.

It combines switch interviews (four forces: push, pull, anxiety, habit) with importance/satisfaction outcome scoring; the theory is in `references/jtbd-method-guide.md`. A well-run workshop produces three artifacts: a ranked job hierarchy with measurable outcome statements, a forces-of-progress map, and a prioritized opportunity list ready to feed PRDs, OKRs, or roadmap themes.

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

Before planning the workshop, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Format:** 2h validation / 4h half-day / 8h full-day (sets the agenda depth; 2h is validation, not primary discovery).
- **Target segment:** JTBD is segment-by-job, not persona-by-demographic (defines who you study and which job hierarchy you build).
- **Switch-interview access:** can you recruit recent (90-day) switchers (without customer voice the forces canvas and ODI scores become team-aligned fiction).
- **Trigger/purpose:** new product / pivot / stalled adoption (shapes which of the four forces to emphasize).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

The workflow, start to finish:

1. Pick a format (2h validation / 4h half-day / 8h full-day) by stakes and availability; define the segment.
2. Recruit 6-12 recent (90-day) switchers and run pre-work switch interviews.
3. Facilitate the agenda; build the job hierarchy, score outcomes (Importance x Satisfaction), fill the forces canvas.
4. Convert top-scored outcomes into opportunity statements (`<verb> <object> <context>`) with named owners.
5. Hand off to `identify-assumptions/`, `brainstorm-experiments/`, or `create-prd/`. Revisit quarterly.
6. Verify that every top outcome statement is scored by real switchers, each force on the canvas cites an interview, and each opportunity has an owner before calling it done.

## Anti-Patterns

### Jobs written as product usage
**Mistake:** The job list reads "use our analytics dashboard" or "open the AI assistant".
**Why it happens:** The team knows its own product best, so it describes the customer's work in feature terms.
**Instead:** Check every job statement for a tool, feature or interface name and rewrite any that has one. Use Klement's situation-motivation-outcome form ("When..., I want to..., so I can...") so the job stays solution-agnostic.

### Outcome statements you cannot score
**Mistake:** Desired outcomes such as "make customers feel valued" or "improve the experience".
**Why it happens:** Fuzzy outcomes are easy to agree on in the room.
**Instead:** Write each outcome so it can be measured with a stopwatch, a count, a percentage or a dollar value, for example "minimize the time it takes to identify which deal is at risk this week". Only then score Importance x Satisfaction.

### Loudest voice sets the jobs
**Mistake:** The workshop runs as open discussion, a senior PM does most of the talking, and the output matches that person's view from before the session.
**Why it happens:** Open discussion feels faster than structured exercises, and few people contradict a senior leader.
**Instead:** Start each block with 5 minutes of silent individual writing, then share round-robin and cluster with sticky-note voting. Check that everyone added at least 3 notes, and invite support and engineering voices directly.

Nine more, each with a bad and a good example: `references/red-flags.md`.

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

## Files

| File | Purpose |
|------|---------|
| `assets/workshop_agenda_2hr.md`, `assets/workshop_agenda_4hr.md`, `assets/workshop_agenda_8hr.md` | Agendas by format |
| `assets/pre_work_email.md`, `assets/switch_interview_script.md`, `assets/forces_of_progress_canvas.md` | Pre-work, interview script, forces canvas |
| `references/facilitation-playbook.md`, `references/jtbd-method-guide.md`, `references/red-flags.md` | Facilitation, method, failure modes |
| `examples/calendar-tool-4hr-workshop-output.md` | Worked 4-hour workshop output |

Use `value-proposition-canvas` once the jobs are known and you are designing the offer against them.
