---
name: job-stories
description: >
  Write When/Want/So backlog stories from observed user situations, gated on
  INVEST and outcome-focused acceptance criteria. Use when writing backlog items from
  research or converting "As a..." user stories to job stories.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: story_quality_checker.py, invest_validator.py, story_converter.py
  tech-stack: jtbd, jobs-to-be-done, invest-criteria
  tags:
    - job-stories
    - jobs-to-be-done
    - backlog
    - user-stories
---
# Job Stories Expert

## Overview

Write job stories using the Jobs-to-Be-Done (JTBD) framework. Unlike traditional user stories that focus on roles ("As a user..."), job stories focus on the situation, motivation, and desired outcome. This shift produces requirements that are more grounded in real user context and less likely to encode assumptions about who the user is.

The format is `When [situation], I want to [motivation], so I can [outcome].` Removing the role and describing the *situation* matters because the same person has different needs in different situations, different people in the same situation share needs, and situations are observable and testable while roles are abstract labels.

## Core Capabilities

- **JTBD discovery canvas** — surface functional/social/emotional jobs, pains, and gains, then map each to a job-story component.
- **Story writing** — author situations, motivations, and outcomes that are specific, solution-agnostic, and benefit-focused.
- **Quality gating** — apply the six INVEST criteria and write 6-8 outcome-focused acceptance criteria per story.
- **Conversion & facilitation** — convert traditional user stories to job stories and run story-writing workshops.

## When to Use

- **Feature definition** -- When you need to articulate what to build and why, grounded in user context.
- **Backlog creation** -- When populating a backlog with work items that stay focused on user outcomes.
- **Requirement workshops** -- When collaborating with stakeholders to define what "done" looks like.
- **Design briefs** -- When giving designers context about the situation and motivation behind a feature.

### When NOT to Use

- When you need strategic backlog items with business context -- use `wwas/` instead.
- When you need lightweight stories for a team already fluent in user story format.
- When the work is purely technical with no direct user-facing situation.

## Clarify First

Before writing job stories, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Situation / trigger:** the "When" anchors the entire story; a vague situation produces a persona-style story in disguise.
- **Underlying job & motivation:** the functional/social/emotional job behind the "I want to"; without it the story encodes a solution, not a need.
- **Desired outcome / progress:** the "so I can" the user is trying to reach; drives the outcome-focused acceptance criteria.
- **Source of user research:** interviews/observation/support data vs guesswork; without grounding, situations get invented and may not reflect reality.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

```
When [situation], I want to [motivation], so I can [outcome].
```

1. Run the JTBD discovery canvas (or pull from research) to find job-pain-gain clusters. The situation must come from something observed; no tool can supply it.
2. Write one job story per cluster in the When/Want/So format.
3. Apply INVEST; split any story that fails the Small or Independent test.
4. Add 6-8 observable, outcome-focused acceptance criteria per story.
5. **Verify** [RECOMMENDED]: run the two gates below and fix every flagged story before it enters sprint planning. Done means both exit 0.

```bash
# Format, vague situation/outcome, solution words, AC count and AC wording
python3 project-management/execution/job-stories/scripts/story_quality_checker.py \
  --stories project-management/execution/job-stories/assets/sample_job_stories_clean.json

# INVEST on backlog items (print the input shape with --example)
python3 project-management/execution/job-stories/scripts/invest_validator.py \
  --items project-management/execution/job-stories/assets/sample_invest_items.json
```

The second command exits 1 by design: its sample includes a 40-point "platform redesign" that fails all six criteria.

## Tools

| Tool | Input | What it does |
|---|---|---|
| `story_quality_checker.py --stories F` | `{"stories": [{title, situation, motivation, outcome, acceptance_criteria}]}` | Scores each story 0-100: all three clauses present, situation not generic ("I use the app"), no UI/solution words in the motivation, outcome not vague ("be productive"), at least 4 ACs, no ACs naming APIs, status codes or components. Ready at 85+ |
| `invest_validator.py --items F` | `{"items": [{title, description, outcome, acceptance_criteria, dependencies, story_points}]}` | The six INVEST criteria as heuristics: dependencies, prescriptive wording, stated value, enough detail, ≤8 points, testable ACs. Sprint Ready only at 6/6 |
| `story_converter.py --stories F` | `{"stories": [{title, role, want, so_that}]}` | Drafts a job story from an "As a..." story: keeps motivation and outcome, leaves a marked `[SITUATION: ...]` placeholder with a hint, warns on generic roles, UI words and system-state outcomes. Never gates |

All three take `--format text|json` and `--example` (prints a valid input file). The checks are keyword heuristics: they catch common failures, not a wrong situation.

**Exit codes:** 0 every story or item ready (converter: converted), 1 at least one not ready, 2 missing file, invalid JSON or wrong shape.

## Anti-Patterns

### A feature request in JTBD wording
**Mistake:** "When I want to use saved searches, I want a saved-search button, so I can save searches." The situation names the feature and the outcome repeats it.
**Why it happens:** The team already has a solution in mind, and the When/Want/So format is easy to fill around it.
**Instead:** Strip the Want clause. If the remaining "When ... so I can ..." does not describe a real moment you could film, rewrite it from the user's situation. Run the JTBD discovery canvas first if you can't.

### Acceptance criteria that describe implementation
**Mistake:** ACs read "POST /saved-searches returns 201" or "React component renders".
**Why it happens:** Engineers write the ACs, and the implementation is what they can see clearly.
**Instead:** Write each AC as behavior a user or QA can observe: "after clicking Save, the search appears in the Saved list within 1 second". If an AC mentions an endpoint, status code, table or UI framework, rewrite it.

### Acceptance criteria that cover only the happy path
**Mistake:** All 6 ACs describe the main flow. None covers empty states, errors, limits or accessibility.
**Why it happens:** The happy path is what the story describes, so it is what comes to mind first.
**Instead:** Sort the 6-8 ACs by category. If fewer than 30% cover edge cases, empty states, errors or a11y, add them before the story enters sprint planning.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## Files

| File | Purpose |
|---|---|
| `scripts/*.py` | The three tools above |
| `assets/sample_job_stories.json`, `sample_job_stories_clean.json` | Mixed (exit 1) and clean (exit 0) input for the quality checker |
| `assets/sample_invest_items.json`, `sample_invest_items_clean.json` | Mixed (exit 1) and clean (exit 0) input for the INVEST validator |
| `assets/sample_user_stories.json` | User stories for the converter |
| `assets/job_story_template.md` | Story card template |
| `examples/wayfinder-onboarding-job-stories.md` | Worked set of job stories |

## References

- **[references/job-stories-playbook.md](references/job-stories-playbook.md)** — JTBD discovery canvas and canvas-to-story mapping, writing-quality tables, INVEST table, AC guidelines, worked example, troubleshooting. Read when writing or refining stories.
- **[references/jtbd-guide.md](references/jtbd-guide.md)** — JTBD theory, job story vs user story, finding situations, splitting. Read to decide which story format to use.
- **[references/red-flags.md](references/red-flags.md)** — common failures with bad/good examples. Read before stories enter sprint planning.

## Scope & Limitations

**In Scope:** Writing job stories using JTBD "When/Want/So" format, applying INVEST quality criteria, writing outcome-focused acceptance criteria, converting existing user stories to job stories, facilitating story-writing workshops, integrating job stories with Jira backlog items.

**Out of Scope:** Strategic backlog items with business context (hand off to `wwas/`), product ideation and opportunity discovery (hand off to `discovery/brainstorm-ideas/`), detailed technical specifications, UX research and user interviewing methodology.

**Limitations:** Job stories work best when the team has access to real user research (interviews, observation, support data). Without user context, teams will invent situations that may not reflect reality. The format is less natural for purely technical or infrastructure work where there is no direct user situation. Job stories and user stories are complementary -- some teams use both formats for different types of work.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `wwas/` | Complementary | WWAS adds strategic "Why" context; job stories add situational "When" context. Use both when needed |
| `summarize-meeting/` | Meetings -> Stories | Discovery conversations and refinement sessions produce the situations that inform job stories |
| `../jira-expert/` | Stories -> Jira | Completed job stories become Jira tickets with structured descriptions |
| `discovery/brainstorm-ideas/` | Ideas -> Stories | Validated product ideas decompose into job stories for the backlog |
| `execution/brainstorm-okrs/` | OKRs -> Stories | Team objectives define the outcomes that job stories should connect to |
| `execution/prioritization-frameworks/` | Stories -> Prioritization | Job stories scored via RICE or other frameworks for sprint planning |
