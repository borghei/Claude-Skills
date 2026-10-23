---
name: wwas
description: Why-What-Acceptance backlog format that connects every work item to strategic business objectives, with INVEST quality gates and observable acceptance criteria.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: backlog-management, invest-criteria, strategic-alignment
  tags:
    - backlog
    - acceptance-criteria
    - invest
    - strategic-alignment
---
# Why-What-Acceptance Backlog Expert

## Overview

Create backlog items using the Why-What-Acceptance (WWAS) format. This format ensures every piece of work connects to strategic context, includes a concise description that serves as a "reminder of the discussion" rather than a detailed specification, and defines high-level acceptance criteria focused on observable outcomes.

The format has three parts:

- **Why (1-2 sentences):** connects the item to a business objective, OKR, or theme; answers "why does this matter?" and "why now?" If you cannot write a compelling Why, the item should not be prioritized.
- **What (1-2 paragraphs):** a reminder of the refinement discussion, not a specification. Link the design if one exists.
- **Acceptance Criteria (4+):** observable outcomes that define done — not implementation steps or test scripts.

Before an item enters a sprint, it must pass the **INVEST** gates (Independent, Negotiable, Valuable, Estimable, Small, Testable).

### When to Use

- **Backlog creation** -- building a product backlog where strategic alignment is critical.
- **Sprint planning** -- refining items and the team needs to understand *why* each matters.
- **Stakeholder communication** -- executives need to see how work connects to business objectives.
- **Roadmap decomposition** -- breaking roadmap themes into actionable backlog items.

### When NOT to Use

- When you need situation-driven requirements -- use `job-stories/` instead.
- A pure technical task with no strategic context (use a simple task description).
- The team prefers traditional user stories and strategic context is well-understood.

## Clarify First

Before writing the item, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The strategic objective / OKR it connects to:** drives the **Why**; without it the Why is a forced exercise and the item should not be prioritized.
- **The refinement discussion or design link:** becomes the **What** (a reminder of the discussion, not a specification).
- **The observable done-state:** drives the **Acceptance Criteria** (outcomes a user or system can observe, not implementation steps or test scripts).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Anti-Patterns

### A Why that names the feature
**Mistake:** "Why: to launch bulk-edit." The reason given for the work is the work itself.
**Why it happens:** The team has already decided to build it, so the Why gets written after the fact.
**Instead:** End the Why in a customer outcome or business metric tied to an objective or OKR. If the Why mentions the feature itself, rewrite it. If you can't, the item isn't ready to prioritize.

### A Why with no hypothesis
**Mistake:** The Why states the impact as a certainty, with no sign it is a bet and no plan to check it.
**Why it happens:** A confident Why gets through prioritization more easily than one that admits doubt.
**Instead:** Frame the Why as a hypothesis: the outcome you expect and how you will measure it after launch. Then the team can tell whether the bet paid off, and can de-prioritize the work when evidence says no.

### Ignoring existing data and workflows
**Mistake:** The What and the Acceptance Criteria describe only the new behavior. Neither says what happens to existing records, deprecated flows or in-flight states.
**Why it happens:** The refinement discussion focuses on the new experience, and the migration tail is easy to miss.
**Instead:** State what happens to existing data and workflows in the What or the Acceptance Criteria. If the item says nothing about them, ask the engineering reviewer to check for a migration before approving.

Seven more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task; keep this file lean and pull detail on demand.

- **[references/wwas-format-and-examples.md](references/wwas-format-and-examples.md)** — full Why/What/Acceptance writing rules with good/bad examples, the INVEST gate table, the item template, a complete worked example, the objective-mapping table, troubleshooting, and success criteria. Read this when writing or reviewing actual WWAS items.
- **[references/backlog-management-guide.md](references/backlog-management-guide.md)** — format comparison (WWAS vs user stories vs job stories), INVEST deep dive, Definition of Ready, and refinement best practices. Read when choosing a format or running refinement.
- **[references/red-flags.md](references/red-flags.md)** — bad-vs-good quoted examples of WWAS items. Scan every item before it enters refinement.
- `assets/wwas_template.md` — ready-to-use WWAS templates.

## Integration with Other Skills

- Use `job-stories/` for situation-driven stories focused on user context rather than strategic alignment.
- Use `brainstorm-okrs/` to define the objectives that WWAS items connect to.
- Use `summarize-meeting/` to capture refinement discussions that inform the What.
- Feed WWAS items into `../jira-expert/` for ticket creation with structured fields.

## Scope & Limitations

**In Scope:** Writing items in WWAS format, applying INVEST gates, connecting work to strategic objectives, facilitating refinement, converting existing items to WWAS, integrating with Jira.

**Out of Scope:** Situation-driven requirements (`job-stories/`), ideation/discovery (`discovery/brainstorm-ideas/`), OKR definition (`execution/brainstorm-okrs/`), detailed technical specs, sprint planning/capacity (`../scrum-master/`).

**Limitations:** WWAS adds most value with clearly defined objectives (OKRs, North Star). Without strategic context the Why becomes a forced exercise. It fits product/feature work better than pure tech-debt/infra items. Teams transitioning from user stories may need 2-3 sprints to build fluency.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `job-stories/` | Complementary | Job stories add situational context (When); WWAS adds strategic context (Why). Use both for complete requirements |
| `summarize-meeting/` | Meetings -> WWAS | Refinement discussions produce the What; decisions produce acceptance criteria |
| `../jira-expert/` | WWAS -> Jira | WWAS items become Jira tickets with structured description fields |
| `execution/brainstorm-okrs/` | OKRs -> WWAS | Team OKRs provide the strategic objectives that Why statements reference |
| `execution/prioritization-frameworks/` | WWAS -> Prioritization | WWAS items scored via RICE or other frameworks for backlog ordering |
| `discovery/brainstorm-ideas/` | Ideas -> WWAS | Validated ideas decompose into WWAS backlog items with strategic traceability |
