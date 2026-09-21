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
