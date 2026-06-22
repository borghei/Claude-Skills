---
name: job-stories
description: Jobs-to-Be-Done story writing that focuses on user situations and motivations rather than personas. Use to write When/Want/So backlog items, run a JTBD discovery canvas, apply INVEST, and convert user stories to job stories.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: jtbd, jobs-to-be-done, invest-criteria
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

Before writing job stories, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Situation / trigger** — the "When" anchors the entire story; a vague situation produces a persona-style story in disguise
- [ ] **Underlying job & motivation** — the functional/social/emotional job behind the "I want to"; without it the story encodes a solution, not a need
- [ ] **Desired outcome / progress** — the "so I can" the user is trying to reach; drives the outcome-focused acceptance criteria
- [ ] **Source of user research** — interviews/observation/support data vs guesswork; without grounding, situations get invented and may not reflect reality

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```
When [situation], I want to [motivation], so I can [outcome].
```

1. Run the JTBD discovery canvas (or pull from research) to find job-pain-gain clusters.
2. Write one job story per cluster in the When/Want/So format.
3. Apply INVEST; split any story that fails the Small or Independent test.
4. Add 6-8 observable, outcome-focused acceptance criteria per story.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/job-stories-playbook.md](references/job-stories-playbook.md)** — the full procedure: JTBD discovery canvas template + canvas-to-story mapping, format details, writing-quality tables, INVEST table, story-card template, acceptance-criteria guidelines, worked example, troubleshooting, and success criteria. Read when writing or refining stories.
- **[references/jtbd-guide.md](references/jtbd-guide.md)** — JTBD theory, job-story vs user-story comparison, techniques for discovering situations, and story-splitting strategies. Read to understand the framework or decide which story format to use.
- **[references/red-flags.md](references/red-flags.md)** — common ways job stories go wrong, each with a bad/good example and how to catch it. Read before stories enter sprint planning.
- **[assets/job_story_template.md](assets/job_story_template.md)** — ready-to-use job story card template. Use when drafting a story.

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
