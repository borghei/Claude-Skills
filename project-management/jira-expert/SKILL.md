---
name: jira-expert
description: >
  Jira expert for project setup, workflow design, JQL queries, custom fields,
  automation rules, dashboards, and reporting. Use for Jira configuration,
  advanced search, board and dashboard creation, and technical Jira operations.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: atlassian
  updated: 2026-06-15
  tags: [jira, jql, workflows, automation, dashboards]
---
# Atlassian Jira Expert

Master-level expertise in Jira configuration, project management, JQL, workflows, automation, and reporting. Handles all technical and operational aspects of Jira.

> **Terminology (Jira Cloud, as of September 2026):** Jira "projects" are now called **spaces** and "issues" **work items** in the UI -- a naming change only ([announcement](https://jirareleases.atlassian.com/announcements/jira-spaces-a-new-name-that-matches-how-you-really-work)). Existing JQL keeps working, and if a new term is not yet accepted in JQL, use the old one (`project`, `issuetype`) ([JQL fields](https://support.atlassian.com/jira-software-cloud/docs/jql-fields/)); REST paths are unchanged (`/rest/api/3/project`). Advanced Roadmaps is now **Plans** (Jira Premium and Enterprise, [docs](https://support.atlassian.com/jira-software-cloud/docs/what-is-advanced-roadmaps/)). This skill uses "project" and "space" interchangeably.

## Core Capabilities

- **Project configuration** — create Scrum/Kanban/custom projects, design custom workflows, configure issue types/fields/screens, set permission and security schemes
- **JQL mastery** — author advanced queries, build complex filters, optimize query performance, create saved filters for teams
- **Automation & integration** — design automation rules, configure webhooks and notifications, integrate Confluence/Slack/external tools
- **Reporting & dashboards** — custom dashboards with gadgets, sprint/velocity/burndown reports, portfolio-level and executive reporting

## When to Use

- Setting up a new project and its workflow, fields, and board
- Writing or debugging JQL for filters, reports, or dashboards
- Designing automation rules and avoiding trigger loops
- Building dashboards and configuring gadgets for a team or exec
- Managing custom fields, issue links, security levels, or bulk operations

## Clarify First

Jira advice depends most on which Jira the user runs, what they are allowed to change, and whether the work only reads data or changes it. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Cloud or Data Center, and plan:** Plans (formerly Advanced Roadmaps) needs Premium or Enterprise. Cloud automation is metered in usage-based steps pooled across the organization, which limits how many rules a design can afford. Data Center reaches end of life on 28 Mar 2029, so long-lived configuration work there should assume a Cloud move.
- **Querying or configuring:** JQL, saved filters and dashboards need little more than browse access and affect nobody else. Workflow schemes, permission schemes, custom fields and org-wide automation need project or Jira admin rights, and some go to `atlassian-admin/`. A workflow change on an active project needs a migration plan, because in-flight issues are not changed retroactively.
- **Read-only or writing through the API or MCP:** A JQL search is safe to run. Creating, editing, transitioning or bulk-changing work items alters shared data and notifies people, so confirm the scope before any write. Workflow schemes, automation rules, permission schemes and custom-field configuration are not exposed as MCP tools and have to be done in Jira admin or the REST API.
- **Instance size and current setup:** JQL on instances above about 100K issues can hit performance ceilings, and more than five active workflows across the org is a signal to consolidate rather than add another. `workflow_analyzer.py`, `board_optimizer.py` and `issue_quality_checker.py` need an export of issues or the board config to say anything specific.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Anti-Patterns

### A custom workflow for every project
**Mistake:** Each project gets its own workflow with 12+ states, until the org runs dozens of distinct workflows.
**Why it happens:** Every team asks for statuses that match its own process exactly, and saying yes is easy.
**Instead:** Start new projects from a shared workflow and push back on per-project states. Count the active workflows across the org: more than 5 means consolidate. Cross-project reporting and reusable automation depend on shared statuses.

### Unreadable JQL
**Mistake:** Filters and dashboards run on 200-character JQL with nested AND / OR / NOT chains nobody can read.
**Why it happens:** Each new condition gets bolted onto a query that already works, and nobody goes back to restructure it.
**Instead:** Break any JQL longer than 120 characters or deeper than 2 levels of parentheses into named saved filters with comments. A misplaced OR or missing parenthesis silently drops tickets, and small named filters are easier to check.

### Story points per person
**Mistake:** A dashboard or filter groups completed story points by assignee, and the numbers end up in performance reviews.
**Why it happens:** The data is already in Jira, and it looks like an objective productivity measure.
**Instead:** Report story points at team level only, and remove any filter or gadget that groups them by assignee. Points are a team's relative sizing tool. Judging people by them leads to inflated estimates and avoided hard work.

Eight more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/jira-playbook.md](references/jira-playbook.md)** — full detail behind this map: competencies, workflows (project creation, workflow design, dashboards, automation), JQL operators/functions, advanced features (custom fields, linking, security, bulk ops), reporting templates, decision/handoff protocols, best practices, troubleshooting table, and success criteria. Read when executing any Jira task.
- **[references/jql-examples.md](references/jql-examples.md)** — extended library of ready-to-run JQL queries grouped by use case (sprints, and more). Read when you need a specific query pattern fast.
- **[references/automation-examples.md](references/automation-examples.md)** — concrete Jira automation rule recipes (auto-assignment, and more) with triggers/conditions/actions. Read when building or troubleshooting automation rules.
- **[references/red-flags.md](references/red-flags.md)** — common ways a Jira configuration, JQL query, automation rule, or dashboard goes wrong, with bad/good examples. Read before shipping any change to a team.

## Scope & Limitations

**In Scope:** Jira project creation and configuration, workflow design and implementation, JQL query authoring and optimization, automation rule design, dashboard and reporting setup, custom field management, board configuration, bulk operations, issue linking strategies.

**Out of Scope:** Org-wide Atlassian administration (hand off to `atlassian-admin/`), Confluence space management (hand off to `confluence-expert/`), sprint execution and team coaching (hand off to `scrum-master/`), strategic project prioritization (hand off to `senior-pm/`).

**Limitations:** Jira Cloud automation is metered as usage-based automation steps, with per-plan allowances pooled at the organization level ([usage](https://support.atlassian.com/cloud-automation/docs/how-is-my-usage-calculated/), as of September 2026). Jira Data Center reaches end of life on 28 Mar 2029 (no new/expanded DC licenses after 30 Mar 2028) -- see `atlassian-admin/` and Atlassian's [DC end-of-life page](https://www.atlassian.com/licensing/data-center-end-of-life). Complex JQL on large instances (>100K issues) may hit performance ceilings. Workflow changes to active projects require careful migration planning -- retroactive changes do not apply to in-flight issues.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `atlassian-admin/` | Admin -> Jira | Global schemes, permission templates, user provisioning |
| `scrum-master/` | SM -> Jira | Sprint board configuration requests, velocity report needs |
| `senior-pm/` | PM -> Jira | Portfolio-level reporting requirements, cross-project dashboards |
| `confluence-expert/` | Bidirectional | Jira macros embedded in Confluence pages; documentation links in issue descriptions |
| `atlassian-templates/` | Templates -> Jira | Issue description templates, workflow documentation |
| `delivery-manager/` | DM -> Jira | Release version management, deployment tracking fields |
