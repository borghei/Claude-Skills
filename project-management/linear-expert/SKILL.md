---
name: linear-expert
description: >
  Linear expert for workspace/team admin, Cycles, Projects, Initiatives,
  Roadmaps, GraphQL API queries, triage workflows, GitHub integration, bulk
  operations, and Jira-to-Linear migration.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-integration
  updated: 2026-06-15
  tech-stack: [linear, graphql, github, slack]
  tags: [linear, graphql, cycles, initiatives, roadmaps, triage, migration]
---
# Linear Expert

Master-level expertise in Linear configuration, workflow design, GraphQL API mastery, Cycle and Project management, Initiative-level roadmaps, triage automation, GitHub integration, and migration from Jira. Covers everything from workspace setup to programmatic bulk operations against the Linear API.

## Overview

Linear is an opinionated, keyboard-driven issue tracker built around a strict data model (Team → Project → Issue → Sub-issue) and a GraphQL-only public API. Unlike Jira, Linear's strength is its lack of configurability: there is one workflow shape (Backlog → Unstarted → Started → Completed → Canceled), one priority scale (0-4), and a tight set of first-class concepts (Cycles, Projects, Initiatives, Labels, Milestones). The job of a Linear expert is to operate fluently inside those rails while extending the system through the API, automations, and integrations.

## Core Capabilities

- **Workspace & team configuration** — URL keys, SSO, team keys, cycle cadence, estimation scales, workflow states, label taxonomy
- **Planning hierarchy** — Cycles (sprints), Projects + Milestones, Initiatives, and Roadmap views
- **Triage automation** — inbound routing from Slack, support, GitHub Issues; daily triage SOP
- **GraphQL API mastery** — query/mutation authoring, pagination, batch mutations, webhooks, rate-limit hygiene
- **GitHub integration** — magic-word auto-link/auto-close, branch auto-linking, PR-state syncing
- **Bulk operations & migration** — API-driven bulk edits and Jira → Linear migration planning

## When to Use

- Setting up a new Linear workspace, team, or project from scratch
- Designing Cycle cadence, triage rules, and SLA workflows
- Writing GraphQL queries and mutations against the Linear API
- Configuring GitHub PR auto-link/auto-close and Slack notifications
- Building Initiative / Project / Milestone hierarchies for executive roadmaps
- Running bulk operations (relabel, retarget, reassign) across hundreds of issues
- Migrating an existing Jira instance to Linear without losing history
- Diagnosing why automations, sub-issues, or triage rules are not firing as expected

## Quick Start

Linear's API is GraphQL-only at `https://api.linear.app/graphql`; auth via personal API key (`Authorization: <key>`) or OAuth2.

```bash
linear_query() {
  curl -s -X POST https://api.linear.app/graphql \
    -H "Authorization: $LINEAR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$1\"}"
}
```

Cache team/label/state UUIDs locally, use nested selection to avoid N+1 calls, and prefer webhooks over polling. See the references below for the full query catalog and operating workflows.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/linear-concepts-and-workflows.md](references/linear-concepts-and-workflows.md)** — Linear data model, the 7 core workflows (setup, cycle/project planning, initiatives, triage, GitHub, bulk ops, Jira migration), best practices, and success criteria. Read when configuring a workspace or running any of the core operating workflows.
- **[references/linear-graphql-patterns.md](references/linear-graphql-patterns.md)** — canonical query and mutation catalog with variables, plus inline quick examples and CLI patterns. Read when authoring any GraphQL query/mutation or scripting against the API.
- **[references/linear-vs-jira.md](references/linear-vs-jira.md)** — concept-by-concept translation guide for teams migrating from Jira. Read before planning a Jira → Linear migration.
- **[references/red-flags.md](references/red-flags.md)** — common anti-patterns (cycle-as-sprint, project bloat, N+1, untriaged inbox, unsigned webhooks) plus the troubleshooting table. Read before applying config/queries to a team or when diagnosing failures.
- **[assets/linear-team-template.md](assets/linear-team-template.md)** — recommended new-team configuration. Read when standing up a new team.
- **[assets/linear-triage-workflow.md](assets/linear-triage-workflow.md)** — daily triage SOP and rotation template. Read when staffing or designing triage.
- Linear API docs: https://developers.linear.app/docs
- Linear GraphQL schema explorer: https://studio.apollographql.com/public/Linear-API/
- Linear method (workspace conventions): https://linear.app/method

## Scope & Limitations

**In Scope:** Linear workspace, team, and project configuration; cycle and project planning; Initiative and Roadmap hierarchy; triage workflow design; GitHub PR integration; GraphQL query and mutation authoring; bulk operations via API; webhook configuration; Jira → Linear migration planning and execution.

**Out of Scope:** Jira-side configuration and migration freeze (hand off to `jira-expert/`); Notion documentation pages for Linear roadmaps (hand off to `notion-pm/`); strategic prioritization and OKR setting (hand off to `senior-pm/`, `execution/brainstorm-okrs/`); sprint coaching and team health (hand off to `scrum-master/`); release notes generation from Linear issues (hand off to `execution/release-notes/`).

**Limitations:** Linear has no custom fields; all extension happens through labels, descriptions, or external systems. As of September 2026 the Free plan caps at 250 issues and 2 teams; Initiatives are on every plan, but sub-initiatives and SAML/SCIM are Enterprise-only and team initiatives need Business or Enterprise (verify on linear.app/pricing). API rate limits depend on auth type, not plan: API keys get 2,500 requests/hour per user, OAuth apps 5,000/hour, each with an hourly complexity budget; heavy automation may require coordination. Importers preserve most history but cannot recreate Jira's custom workflow states; mapping is many-to-five. GraphQL schema evolves continuously; pin client code to the deprecation calendar.

## Integration Points

| Integration | Direction | What Flows |
|---|---|---|
| `jira-expert/` | Jira → Linear | Migration mappings, custom-field translation, freeze coordination |
| `notion-pm/` | Linear → Notion | Roadmap embeds, Initiative pages, project status rollups |
| `execution/create-prd/` | PRD → Linear | PRD page becomes the Linear Project description; PRD sections become Milestones |
| `execution/brainstorm-okrs/` | OKR → Linear | Initiatives mapped to Objectives; Projects tagged with KR identifiers |
| `execution/outcome-roadmap/` | Roadmap → Linear | Outcome roadmap rows mapped to Linear Initiatives; outputs become Projects |
| `execution/release-notes/` | Linear → Release Notes | Closed issues in a cycle/project become release note line items |
| `execution/prioritization-frameworks/` | Scoring → Linear | RICE/WSJF scores written back to labels or description fields |
| `scrum-master/` | Linear → Analytics | Cycle data feeds velocity_analyzer.py and sprint_health_scorer.py |
| `senior-pm/` | Linear → Portfolio | Initiative-level rollups feed project_health_dashboard.py |
| `delivery-manager/` | Linear → Release | Project completion state and milestone dates feed release coordination |
