---
name: job-stories
description: Jobs-to-Be-Done story writing that focuses on user situations and motivations rather than personas.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-03-04
  tech-stack: jtbd, jobs-to-be-done, invest-criteria
---
# Job Stories Expert

## Overview

Write job stories using the Jobs-to-Be-Done (JTBD) framework. Unlike traditional user stories that focus on roles ("As a user..."), job stories focus on the situation, motivation, and desired outcome. This shift produces requirements that are more grounded in real user context and less likely to encode assumptions about who the user is.

### When to Use

- **Feature definition** -- When you need to articulate what to build and why, grounded in user context.
- **Backlog creation** -- When populating a backlog with work items that stay focused on user outcomes.
- **Requirement workshops** -- When collaborating with stakeholders to define what "done" looks like.
- **Design briefs** -- When giving designers context about the situation and motivation behind a feature.

### When NOT to Use

- When you need strategic backlog items with business context -- use `wwas/` instead.
- When you need lightweight stories for a team already fluent in user story format.
- When the work is purely technical with no direct user-facing situation.

## The Job Story Format

```
When [situation], I want to [motivation], so I can [outcome].
```

| Component | Focus | Question It Answers |
|-----------|-------|-------------------|
| **When [situation]** | The context or trigger | What is happening when the user needs this? |
| **I want to [motivation]** | The action or capability desired | What does the user want to do in this moment? |
| **So I can [outcome]** | The expected result or benefit | What does success look like for the user? |

### Key Principle: Focus on the Job, Not the Role

User stories say "As a [role]..." which anchors the requirement to a persona. Job stories remove the role and instead describe the *situation* -- the real-world context that creates the need. This matters because:

- The same person may have different needs in different situations.
- Different people in the same situation often have the same need.
- Situations are observable and testable; roles are abstract labels.

**Example comparison:**

| User Story | Job Story |
|-----------|-----------|
| As a budget manager, I want to see a spending report so I can track expenses. | When I am preparing my weekly budget, I want to see spending so far this period, so I can adjust before overspending. |
| As an admin, I want to export user data so I can comply with data requests. | When I receive a data subject access request, I want to export all data associated with that person, so I can respond within the 30-day legal deadline. |

The job story version is more specific, more testable, and provides better design guidance.

## Writing Good Job Stories

### Situations (When...)

Good situations are:

- **Specific and observable** -- You could watch someone be in this situation.
- **Contextual** -- They describe what is happening, not who the person is.
- **Triggering** -- They explain what creates the need right now.

| Weak Situation | Strong Situation |
|---------------|-----------------|
| When I use the app | When I open the app for the first time after signing up |
| When I need data | When I am in a client meeting and need to reference last quarter's results |
| When I manage my team | When a team member submits a time-off request that overlaps with a project deadline |

### Motivations (I want to...)

Good motivations are:

- **Action-oriented** -- They describe doing something, not having something.
- **Solution-agnostic** -- They describe the capability, not the implementation.
- **Singular** -- One motivation per story.

| Weak Motivation | Strong Motivation |
|----------------|-------------------|
| I want a dashboard | I want to see my team's progress at a glance |
| I want better notifications | I want to be alerted only when something requires my action |
| I want to manage users and permissions | I want to grant a new team member access to the project (split into two if needed) |

### Outcomes (So I can...)

Good outcomes are:

- **Benefit-focused** -- They describe the end result, not the means.
- **Measurable or observable** -- You can tell if the outcome was achieved.
- **Meaningful** -- They connect to something the user genuinely cares about.

| Weak Outcome | Strong Outcome |
|-------------|----------------|
| So I can use the feature | So I can complete my weekly report in under 10 minutes |
| So I can be productive | So I can identify which tasks are blocked before standup |
| So I can do my job | So I can respond to the customer within our 4-hour SLA |

## INVEST Quality Criteria

Apply INVEST to every job story before it enters the backlog:

| Criterion | Question | Red Flag |
|-----------|----------|----------|
| **Independent** | Can this story be delivered without depending on another story? | "This only works after story X is done" |
| **Negotiable** | Is the implementation open to discussion, or is it prescribing a solution? | Motivation says "I want a dropdown menu" instead of "I want to select from available options" |
| **Valuable** | Does the outcome deliver clear value to the user? | Outcome is vague ("so I can use it") or internal ("so the database is normalized") |
| **Estimable** | Can the team estimate the effort? | Situation is too vague to understand scope |
| **Small** | Can this be completed in one sprint? | Story covers multiple distinct situations or motivations |
| **Testable** | Can you write acceptance criteria that verify the outcome? | Outcome is subjective ("so I feel confident") |

## Story Template

For each job story, produce a card with the following structure:

```markdown
### [Title]

**Job Story:**
When [situation], I want to [motivation], so I can [outcome].

**Design:** [Link to design file or "TBD"]

**Acceptance Criteria:**

1. [ ] [Observable outcome that verifies the story is complete]
2. [ ] [Observable outcome]
3. [ ] [Observable outcome]
4. [ ] [Observable outcome]
5. [ ] [Observable outcome]
6. [ ] [Observable outcome]
```

### Acceptance Criteria Guidelines

- Write 6-8 acceptance criteria per story.
- Focus on **outcomes**, not implementation steps.
- Each criterion should be independently verifiable.
- Use the pattern: "[Thing] [does/shows/enables] [expected behavior] [under condition]."
- Include edge cases and error states, not just the happy path.

**Good acceptance criteria examples:**

1. The spending summary shows all transactions from the current period, grouped by category.
2. Transactions from previous periods are excluded from the current period total.
3. The summary updates within 5 seconds of a new transaction being recorded.
4. If no transactions exist for the current period, a message explains that no spending has been recorded yet.
5. The summary is accessible on mobile screens without horizontal scrolling.
6. Category totals match the individual transaction amounts (no rounding discrepancies).

**Bad acceptance criteria examples (avoid):**

- The API returns a 200 status code (implementation detail)
- The React component renders correctly (implementation detail)
- It works (not testable)
- The user is happy (not observable)

## Worked Example

**Context:** A budgeting application for personal finance.

### Weekly Budget Check

**Job Story:**
When I am preparing my weekly budget on Sunday evening, I want to see how much I have spent so far this month by category, so I can decide where to cut back before the month ends.

**Design:** [Link to Figma mock]

**Acceptance Criteria:**

1. [ ] The spending view shows the current month's transactions grouped by category (e.g., groceries, dining, transport).
2. [ ] Each category displays the total spent and the remaining budget for that category.
3. [ ] Categories that have exceeded their budget are visually distinguished from those within budget.
4. [ ] Tapping a category shows the individual transactions within it.
5. [ ] The view loads within 2 seconds on a standard mobile connection.
6. [ ] If no budget has been set for a category, the category still appears with total spent but no remaining budget indicator.
7. [ ] The date range is fixed to the current calendar month and is clearly displayed.
8. [ ] A "last updated" timestamp shows when transaction data was last synced.

## Integration with Other Skills

- Use `summarize-meeting/` to capture the discovery conversations that inform job stories.
- Use `wwas/` when you need to add strategic business context (the "Why") to backlog items.
- Feed completed job stories into `../jira-expert/` for ticket creation.
- Use `brainstorm-okrs/` to connect job stories back to team objectives.

## References

- See `references/jtbd-guide.md` for Jobs-to-Be-Done theory, comparison with user stories, and story splitting techniques.
- See `assets/job_story_template.md` for ready-to-use templates.

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Team writes situations that are too vague ("When I use the app...") | Insufficient user research; situations invented at desk rather than observed | Require each situation to reference a specific interview quote, support ticket, or analytics event; use the "could you video this?" test |
| Motivations prescribe a specific solution ("I want a dropdown...") | Team conflates solution with capability; negotiability criterion failing | Rewrite using "I want to [verb] [object]" pattern without naming UI elements; apply the INVEST-N check before acceptance |
| Outcomes are not measurable ("So I can be productive") | Outcome too abstract; not grounded in observable behavior | Ask "How would you know the user achieved this?" -- if you cannot describe an observable signal, the outcome needs rewriting |
| Job stories are too large for a single sprint | Multiple situations or motivations packed into one story | Split by situation (different contexts become separate stories) or by outcome (different success criteria become separate stories) |
| Team defaults to user story format despite training | Habit and muscle memory; Jira templates still use "As a..." format | Update Jira issue templates to use JTBD format; run a conversion workshop with 5 real user stories rewritten as job stories |
| Acceptance criteria describe implementation steps instead of outcomes | Engineering team writing criteria from their perspective rather than the user's perspective | Apply the "would the user care about this?" filter; replace API/database criteria with observable behavior statements |
| Job stories lack connection to strategic objectives | JTBD format focuses on user context but does not inherently include business "why" | Pair each job story with a WWAS "Why" statement from `wwas/`; or add an optional "Supports:" field linking to an OKR |

## Success Criteria

- 100% of job stories in the backlog follow the "When / I want to / So I can" format correctly
- All situations reference observable, specific contexts (pass the "could you video this?" test)
- All motivations are solution-agnostic (no UI element names or implementation details)
- Each story has 6-8 acceptance criteria focused on observable outcomes, not implementation
- Every job story passes all 6 INVEST criteria before entering a sprint
- Defect rate on stories written in JTBD format is 20%+ lower than stories written in traditional format (measured over 3 months)
- Team members can articulate the difference between a job story and a user story and choose the appropriate format for the context

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
