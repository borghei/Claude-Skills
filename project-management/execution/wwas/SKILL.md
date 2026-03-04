---
name: wwas
description: Why-What-Acceptance backlog format that connects every work item to strategic business objectives.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-03-04
  tech-stack: backlog-management, invest-criteria, strategic-alignment
---

# Why-What-Acceptance Backlog Expert

## Overview

Create backlog items using the Why-What-Acceptance (WWAS) format. This format ensures every piece of work connects to strategic context, includes a concise description that serves as a "reminder of the discussion" rather than a detailed specification, and defines high-level acceptance criteria focused on observable outcomes.

### When to Use

- **Backlog creation** -- When building a product backlog where strategic alignment is critical.
- **Sprint planning** -- When refining items for upcoming sprints and the team needs to understand *why* each item matters.
- **Stakeholder communication** -- When executives or cross-functional partners need to see how individual work items connect to business objectives.
- **Roadmap decomposition** -- When breaking down roadmap themes into actionable backlog items.

### When NOT to Use

- When you need situation-driven requirements -- use `job-stories/` instead.
- When the work is a pure technical task with no strategic context (use a simple task description).
- When the team prefers traditional user story format and the strategic context is well-understood.

## The WWAS Format

Every backlog item has three parts:

### 1. Why (Strategic Context)

1-2 sentences that connect this work item to the team's objectives and business strategy. The Why answers:

- **What business objective does this support?** (e.g., "Reduce churn by 10% in Q2")
- **Why now?** What makes this item timely or important relative to other work?

**The Why is the most important part.** It prevents the team from building features disconnected from strategy. If you cannot articulate the Why, the item should not be in the backlog.

**Good Why examples:**

- "Our Q2 objective is to reduce time-to-value for new users from 14 days to 3 days. Onboarding is the biggest lever -- 60% of churned users never completed setup."
- "Enterprise customers have cited lack of SSO as the top reason for not upgrading. This directly supports our revenue expansion target of $2M ARR growth in H1."
- "Support ticket volume for billing issues increased 40% last quarter. Resolving this frees up 2 support FTEs to focus on onboarding assistance, which supports our activation goal."

**Bad Why examples (avoid):**

- "Because the customer asked for it." (No strategic context)
- "It's a best practice." (No connection to team objectives)
- "We need this for the release." (Circular reasoning)

### 2. What (Description)

A short description of what needs to be built or changed. This section is a **reminder of the discussion, not a detailed specification.**

**Guidelines:**

- 1-2 paragraphs maximum.
- Describe the change at a level that reminds the team of what was discussed during refinement.
- Include a link to the design file if one exists.
- Do not write implementation details, technical specifications, or step-by-step instructions.
- The team should be able to read the What and say "Yes, I remember what we agreed to build."

**Good What examples:**

- "Add a guided setup wizard that walks new users through connecting their data source, inviting a teammate, and creating their first dashboard. The wizard should be skippable and resumable. [Design: Figma link]"
- "Replace the current billing FAQ page with an interactive troubleshooter that guides users through common billing issues (failed payments, plan changes, invoice requests) and resolves 80% of cases without a support ticket."

**Bad What examples (avoid):**

- A multi-page specification with wireframes, API contracts, and database schemas (too detailed -- that belongs in a design doc).
- "Build SSO." (Too vague -- the team cannot recall what was discussed).

### 3. Acceptance Criteria

High-level, observable outcomes that define when the item is done. These are not detailed test cases -- they are the minimum set of conditions that must be true for the item to be accepted.

**Guidelines:**

- 4 or more acceptance criteria per item.
- Each criterion describes an **observable outcome**, not an implementation step.
- Focus on what the user or system should do, not how it is built.
- Include the most important edge cases, but save exhaustive test cases for QA.

**Good acceptance criteria examples:**

1. New users who complete the setup wizard activate within 3 days (measured by creating their first dashboard).
2. The wizard is accessible on mobile and desktop browsers.
3. Users can skip the wizard at any step and resume later from where they left off.
4. Users who skip the wizard can access it again from the help menu.

**Bad acceptance criteria examples (avoid):**

- The API returns a 200 status code with a JSON payload containing... (implementation detail)
- The React component passes all unit tests (internal quality, not user outcome)
- It works on Chrome (too vague; specify what "works" means)

## INVEST Quality Gates

Before a WWAS item enters a sprint, it must pass the INVEST criteria:

| Criterion | Question | Action If Failing |
|-----------|----------|-------------------|
| **Independent** | Can this item be delivered without waiting for another item? | Reorder the backlog or combine dependent items. |
| **Negotiable** | Is the What open to discussion on implementation approach? | Remove implementation prescriptions from the What. |
| **Valuable** | Does the Why connect to a real business objective? | Rewrite the Why or deprioritize the item. |
| **Estimable** | Can the team estimate effort with reasonable confidence? | Add more context to the What or conduct a spike. |
| **Small** | Can this be completed within one sprint? | Split the item (by outcome, by scope, or by user segment). |
| **Testable** | Can the acceptance criteria be verified? | Rewrite criteria to be observable and specific. |

## Item Template

```markdown
### [Title]

**Why:**
[1-2 sentences connecting to strategic objective and explaining why this matters now.]

**What:**
[1-2 paragraphs describing the change. Reminder of the discussion, not a specification.]

[Design: link or "TBD"]

**Acceptance Criteria:**

1. [ ] [Observable outcome]
2. [ ] [Observable outcome]
3. [ ] [Observable outcome]
4. [ ] [Observable outcome]
```

## Worked Example

### Guided Onboarding Wizard

**Why:**
Our Q2 North Star is reducing time-to-value from 14 days to 3 days. User research shows that 60% of churned users never completed the initial setup, and the top reason cited is "I did not know what to do next." A guided onboarding flow directly addresses this by walking users through the critical first steps.

**What:**
Add a step-by-step setup wizard that appears on first login and guides new users through three milestones: connecting a data source, inviting a teammate, and creating their first dashboard. The wizard should be skippable at any point (some users prefer to explore on their own) and resumable if the user leaves before finishing. Each step includes a brief explanation of why it matters and a direct action button.

[Design: figma.com/file/abc123]

**Acceptance Criteria:**

1. [ ] The wizard appears automatically on first login for new users.
2. [ ] Users can skip the wizard at any step and return to it later from the help menu.
3. [ ] Each milestone (data source, teammate, dashboard) can be completed independently and in any order.
4. [ ] Users who complete all three milestones see a completion confirmation with suggested next steps.
5. [ ] The wizard does not appear for existing users who have already completed setup.
6. [ ] The wizard is functional on both desktop and mobile browsers.

## Connecting Why to Business Objectives

The strength of WWAS is the explicit strategic connection. Use this mapping to write strong Why statements:

| Objective Level | Example Objective | Why Framing |
|----------------|-------------------|-------------|
| **Company OKR** | Grow ARR to $10M | "This supports our $10M ARR target by..." |
| **Team OKR** | Reduce churn to <5% monthly | "Our team's Q2 churn target requires..." |
| **Product theme** | Self-serve onboarding | "As part of the self-serve onboarding theme..." |
| **Customer feedback** | Top 3 requested feature | "This is the #1 requested feature from enterprise customers, blocking $500K in pipeline..." |
| **Operational** | Reduce support load | "Support ticket volume for this issue is X/month, costing Y hours..." |

## Integration with Other Skills

- Use `job-stories/` when you need situation-driven stories focused on user context rather than strategic alignment.
- Use `brainstorm-okrs/` to define the objectives that WWAS items connect to.
- Use `summarize-meeting/` to capture refinement session discussions that inform the What.
- Feed WWAS items into `../jira-expert/` for ticket creation with structured fields.

## References

- See `references/backlog-management-guide.md` for format comparison, INVEST deep dive, and refinement best practices.
- See `assets/wwas_template.md` for ready-to-use templates.
