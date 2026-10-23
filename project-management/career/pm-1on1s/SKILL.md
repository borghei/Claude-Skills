---
name: pm-1on1s
description: >
  Structured PM 1:1 templates by partner type — manager, engineering-manager
  partner, designer, IC reports, cross-functional — grounded in Radical Candor,
  the GROW coaching model, and the Manager Tools 1:1 framework.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-career
  updated: 2026-06-15
  tech-stack: 1on1s, manager-cadence, grow-model, radical-candor
  tags:
    - one-on-ones
    - coaching
    - radical-candor
    - grow-model
    - pm-career
---
# PM 1:1 Expert

## Overview

PMs run more 1:1s than almost any other role: with their manager, their engineering manager partner, their design lead, cross-functional partners (sales, support, data), and -- once they have reports -- with their direct PMs. Each 1:1 type has a different purpose, cadence, and ideal structure.

This skill provides templates and question banks for the most common 1:1 types a PM runs, calibrated to the PM context. It draws on Kim Scott's Radical Candor (caring personally + challenging directly), the GROW coaching model (Whitmore), the Manager Tools 1:1 framework (Auzenne & Horstman), and PM-specific 1:1 patterns popularized by senior product leaders.

### Five core principles

1. **The 1:1 belongs to the other person** — their agenda first.
2. **Status updates do not need a 1:1** — write them async; reserve live time for trust, growth, judgment, feedback.
3. **Care personally, challenge directly** — avoid ruinous empathy and obnoxious aggression.
4. **Cadence matters** — weekly for direct partners, monthly for tier-3; don't skip, reschedule.
5. **Document agreements, not transcripts** — capture decisions and next steps.

### When to Use

- **Starting a new 1:1 relationship** -- use the kickoff template to set expectations.
- **Existing 1:1s feel transactional** -- adopt the structured partner-type template.
- **You manage other PMs** -- use the direct-report template for growth and feedback.
- **You partner with an EM, designer, or cross-functional lead** -- use the partner-type template.

### When NOT to Use

- Ad-hoc problem-solving meetings (treat as project meetings, not 1:1s).
- Performance management conversations (use a separate, manager-led structure).
- Initial intro meetings during onboarding -- use `pm-onboarding/` for those.

## Clarify First

Before drafting the 1:1 agenda, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Partner type:** your manager, EM partner, designer, direct report, or cross-functional lead (selects the agenda template and question bank).
- **Relationship stage:** brand-new vs steady-state (decides whether you run the kickoff script or the recurring agenda).
- **Purpose this session:** growth/feedback, alignment, or status-clearing (sets which sections matter and whether the Radical Candor frame applies).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Anti-Patterns

### Jumping to the solution
**Mistake:** The other person raises an issue and you answer with "you should..." within the first few minutes.
**Why it happens:** Giving the answer is faster and feels helpful.
**Instead:** Run GROW in order: Goal, Reality, Options, then Will. Ask first whether they want coaching questions or just want to be heard. Offering the fix up front builds dependency.

### No notes, no follow-through
**Mistake:** Nobody writes anything down, so agreed actions vanish and the same topics come back two weeks later.
**Why it happens:** The conversation felt clear at the time, so notes seem unnecessary.
**Instead:** Record agreements and next steps after every 1:1. Skip the transcript. Check: can you show four months of agreed actions for each 1:1 relationship? If not, your follow-through only exists in memory.

### Feedback that only flows down
**Mistake:** Your manager gives you feedback and you never give any back. Or you give feedback to your reports and never ask for theirs.
**Why it happens:** Upward feedback feels risky, and nobody puts it on the agenda.
**Instead:** Put upward feedback on the agenda on purpose. Over your last four 1:1s, aim for at least one piece of upward feedback. Use the Radical Candor frame: care personally, challenge directly.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task; keep this file lean and pull detail on demand.

- **[references/one-on-one-templates.md](references/one-on-one-templates.md)** — the five core principles in full, per-partner agenda templates (manager, EM partner, designer, direct report, cross-functional), the kickoff conversation script, the Radical Candor feedback frame, the run-the-system workflow, troubleshooting table, and success criteria. Read this when designing or fixing any specific 1:1.
- **[references/1on1-playbook.md](references/1on1-playbook.md)** — deep dive on cadence by partner type, the three failure modes, and structuring manager / direct-report / EM / design / async 1:1s. Read when you want the underlying theory and quarterly-review discipline.
- **[references/red-flags.md](references/red-flags.md)** — bad-vs-good examples of agendas, notes, and question banks. Scan after drafting a 1:1 agenda or notes, before your next 1:1.
- `assets/kickoff_template.md` — script for kicking off a new 1:1 relationship.
- `assets/1on1_notes_template.md` — recurring 1:1 notes template.
- `assets/manager_1on1_agenda.md` — ready-to-use agenda for your manager 1:1.

External: Scott, K. *Radical Candor* (2017); Whitmore, J. *Coaching for Performance* (GROW); Auzenne & Horstman, *The Effective Manager* (Manager Tools 1:1).

## Scope & Limitations

**In Scope:** 1:1 templates for the 5 common PM partner types; the GROW coaching framework for direct reports; Radical Candor feedback; kickoff conversation script; notes/agenda templates.

**Out of Scope:** Formal performance management (PIP, terminations, reviews — requires HR); compensation conversations; skip-level design from the senior-leader perspective; career conversations beyond growth-plan refresh (use `pm-career-ladder/`).

**Caveats:** 1:1 patterns are culturally inflected — calibrate directness to the room. Templates are starting points that should evolve as the relationship deepens. Re-establish the kickoff conversation when you join a new team.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `pm-career-ladder/` | Bidirectional | Quarterly growth 1:1s use the ladder rubric as the calibration tool |
| `pm-onboarding/` | Receives from | Onboarding 1:1s evolve into steady-state 1:1s after day 90 |
| `pm-interview-prep/` | Reuses | Behavioral story prep often surfaces from 1:1 reflections |
| `senior-pm/stakeholder-mapper/` | Reuses | Tier-1 stakeholders should be your weekly 1:1s |
| `personal-productivity/weekly-review/` | Feeds into | Weekly review captures 1:1 actions and growth-plan progress |
