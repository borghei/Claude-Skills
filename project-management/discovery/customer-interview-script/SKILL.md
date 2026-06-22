---
name: customer-interview-script
description: >
  Run high-signal customer discovery interviews using a scripted question
  hierarchy, behavior-over-opinion probes, and rapport techniques drawn from
  Portigal, Torres, Fitzpatrick (Mom Test), and Lewis Lin.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-discovery
  updated: 2026-06-15
  tech-stack: customer-interviews, discovery, jobs-to-be-done, mom-test
---
# Customer Interview Script Expert

## Overview

Running a customer interview is harder than it looks. The difference between a 60-minute conversation that produces three actionable insights and one that produces zero is almost entirely method: what you ask, when you ask it, and what you do *not* ask. This skill is the live-interview companion to `discovery/interview-synthesis/` (post-interview analysis) and `discovery/identify-assumptions/` (which produces the questions you go in to test).

The script structure draws from four canonical sources: Steve Portigal's *Interviewing Users* (rapport, listening, "tell me about the last time"), Teresa Torres' *Continuous Discovery Habits* (story-based probing, weekly cadence), Rob Fitzpatrick's *The Mom Test* (avoiding compliments, opinions, and futures), and Lewis Lin's behavioral interviewing patterns (concrete-recent-relevant). The goal is to leave each interview with at least one story, one contradiction, and one surprise.

## Core Capabilities

- **5-phase script** -- opening/consent, context, story collection (the meat), probing/synthesis, closing -- timed for 45/60/90-minute slots.
- **Story-based probing** -- the story funnel and 5-Whys turn opinions into concrete-recent-relevant evidence.
- **Mom Test discipline** -- bad-question to good-question conversions that strip out compliments, fluff, and feature pitches.
- **Question banks by type** -- problem discovery, solution validation, journey mapping, churn/win-loss.
- **Interview craft** -- rapport rules, silence handling, pacing, pair-interviewing roles, recording/consent/storage.

## When to Use

- **Problem discovery** -- test whether a customer pain is real, who has it, and how acute it is.
- **Solution validation** -- get feedback on a wireframe/prototype grounded in past behavior, not hypotheticals.
- **Journey research** -- understand the end-to-end flow of how a customer does a job today (tools, workarounds, handoffs).
- **Churn or win/loss** -- understand why customers left, stayed, or chose a competitor.
- **Continuous discovery cadence** -- weekly customer touchpoints to keep the team grounded in evidence.

## Clarify First

Before building the interview script, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Interview type** — problem discovery / solution validation / journey / churn-win-loss (selects the question bank and phase emphasis)
- [ ] **Must-answer questions** — the 2-3 assumptions you go in to test (drives the custom story-collection prompts)
- [ ] **Time slot** — 45 / 60 / 90 minutes (sets the per-phase timing)
- [ ] **Participant recency** — how recently they did the job (story-based probing degrades past ~90 days, which weakens the script's core)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

1. Pull top assumptions from `discovery/identify-assumptions/`; write 2-3 must-answer questions and pick the interview type.
2. Customize `assets/interview_script_template.md` and pull type-specific prompts from `assets/question_bank.md`.
3. Run the 5-phase script (rapport first, stories in the middle, contradictions at the end); debrief within 30 minutes; hand the transcript to `discovery/interview-synthesis/`.

See `references/interview-execution-playbook.md` for the full method, scripts, question banks, pacing, and troubleshooting.

## References

- `references/interview-execution-playbook.md` -- read this before running an interview: the four-source frameworks, the verbatim 5-phase script, question banks by type, what-not-to-ask table, pacing, pair-interviewing roles, recording/consent, silence handling, workflow, troubleshooting, and success criteria.
- `references/interviewing-methodology-guide.md` -- read this for the deep method with worked examples (Portigal, Torres, Fitzpatrick, Lin).
- `references/red-flags.md` -- read this when auditing a transcript or technique for biasing anti-patterns before trusting the findings.
- `assets/interview_script_template.md` -- ready-to-customize 5-phase interview script.
- `assets/question_bank.md` -- question bank organized by interview type (problem / solution / journey / churn).

## Scope & Limitations

**In scope:** live discovery interview script structure and pacing; question banks (problem / solution / journey / churn); rapport, listening, and silence techniques; recording consent and retention policy; pair-interviewing role definitions.

**Out of scope:** interview synthesis and theme clustering (`discovery/interview-synthesis/`); assumption mapping before interviews (`discovery/identify-assumptions/`); survey design and quantitative research; usability testing protocols (task-based, not story-based); recruiting operations (panel sourcing, screening, incentives).

**Caveats:** this skill produces interview *technique*, not research operations. Story-based interviewing is bounded by participant memory -- events older than 90 days are reconstructions. B2B enterprise interviews often need procurement-style approval; build 2-4 weeks into recruiting. Continuous discovery assumes weekly touchpoints; one-off rounds produce shallower evidence -- weight findings accordingly.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `discovery/identify-assumptions/` | Receives from | Top assumptions become the must-answer questions for each interview |
| `discovery/interview-synthesis/` | Feeds into | Transcripts and debrief notes are the input for theme clustering |
| `discovery/brainstorm-ideas/` | Bidirectional | Pre-interview hypotheses; post-interview ideas seeded by themes |
| `discovery/brainstorm-experiments/` | Feeds into | Validated pains become experiment hypotheses |
| `discovery/jtbd-workshop/` | Complementary | Switch interviews use this script structure as their foundation |
| `discovery/value-proposition-canvas/` | Feeds into | Jobs, pains, and gains captured in stories populate the Customer Profile |
| `execution/create-prd/` | Feeds into | Direct quotes strengthen PRD Background and Market Segments |
