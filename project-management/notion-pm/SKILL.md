---
name: notion-pm
description: >
  Notion expert for product management workflows. Use for database design
  for PRDs/OKRs/Roadmaps/Decisions, property and view design, page
  architecture, Notion REST API, and sync with Jira, Linear, and GitHub.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-integration
  updated: 2026-06-15
  tech-stack: [notion, rest-api, jira, linear, github]
  tags: [notion, databases, prd, okr, roadmap, decisions]
---
# Notion for Product Management

Master-level expertise in using Notion as the documentation and operational backbone for a product team: PRDs, OKRs, roadmaps, decision logs, sprint reviews, 1:1 notes, customer research, and sync patterns with Jira, Linear, and GitHub. Covers Notion's database model, view design, formula and rollup patterns, page architecture, and REST API.

## Overview

Notion's PM value comes from its database model: every meaningful PM artifact (a PRD, an OKR, a roadmap row, a decision) becomes a row in a typed database, with relations to other databases. This unlocks linked views (one source of truth, many surface presentations), rollups (aggregate child progress into a parent), and a queryable API. The job of a Notion PM expert is to design these databases up front, restrain ad-hoc page creation, and tie the workspace into Jira/Linear/GitHub so the artifacts stay current without manual maintenance.

## Core Capabilities

- **Database design** — typed schemas for PRDs, OKRs, Roadmap, Decisions, and Sprint/Cycle Reviews, with the right property types (relation, rollup, formula, status, unique_id).
- **View design** — Table, Board, Timeline, Calendar, Gallery, and List views with filters, sorts, and groups tuned per artifact.
- **Page & workspace architecture** — Teamspace setup, curated home dashboards, linking strategy (relations vs mentions vs sub-pages), governance and review cadence.
- **REST API authoring** — query/create/update/append calls, compound filters, pagination, and rate-limit handling.
- **Sync patterns** — one-way, two-way, roll-up, and embed integrations with Jira, Linear, and GitHub.

## When to Use

- Standing up a new product team's documentation workspace
- Designing a PRD, OKR, Roadmap, or Decisions database from scratch
- Refactoring an existing Notion workspace that has grown into a sprawl of unrelated pages
- Building roadmap or status views aggregated from underlying issue trackers
- Authoring Notion REST API calls (page creation, database queries, block updates)
- Setting up two-way sync between Notion and Jira/Linear/GitHub
- Establishing governance: ownership, review cadence, archive strategy

## Clarify First

Notion advice depends most on whether the user is designing a workspace or scripting against the API, and on what already exists. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **New workspace or existing sprawl:** A new workspace can start from the canonical schemas in `references/notion-database-design-for-pm.md`. A refactor needs an inventory first: which PRDs live outside the database, which cross-database references are plain text instead of Relations, and who owns each Teamspace.
- **Read-only, write or sync:** Querying a database is low risk but has to loop on `has_more`. Creating pages, updating properties or running a two-way sync with Jira, Linear or GitHub writes to shared content, and the limit of about 3 requests per second decides whether a sync needs batching and a queue.
- **Plan tier and API version:** Lower plan tiers cannot create Status options through the API, so those must be created by hand first. The API references target `Notion-Version: 2025-09-03`, where databases are queried as data sources; an integration pinned to an older version uses different endpoints and cannot chain rollups.
- **Access level:** Teamspace setup, database design and views are in scope for a Teamspace owner. SCIM, SAML and billing are workspace-admin tasks outside this skill, and Teamspace-level changes can override page permissions, so know who can change what before proposing a permission model.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Anti-Patterns

### Ignoring API pagination
**Mistake:** A script queries a database through `POST /v1/data_sources/{data_source_id}/query`, gets 100 results back and treats them as all results.
**Why it happens:** The first page looks complete, and small test databases never go past 100 rows.
**Instead:** Loop until `has_more` is false, passing `next_cursor` as `start_cursor` on each call. Any Notion API call that doesn't loop on `has_more` is broken, and decisions made on its output rest on a partial sample.

### Cross-database links stored as text
**Mistake:** The PRDs, OKRs and Roadmap databases exist, but each PRD names its OKR in plain text instead of linking to it.
**Why it happens:** Typing a name is quicker than setting up a Relation property, and it reads fine on the page.
**Instead:** Convert every cross-database reference to a Relation. Text references go stale when the OKR's wording changes, and they make basic queries like "all PRDs supporting this OKR" impossible.

### PRDs as free-form pages
**Mistake:** Each PRD is a hand-made page in a folder, some with a status and some without.
**Why it happens:** A new page is Notion's default, and a database feels like overhead for a few documents.
**Instead:** Make every PRD a row in the PRDs database with consistent properties (see `references/notion-database-design-for-pm.md`). Then you can query which PRDs are blocked or waiting on design review. Migrate PRD pages that live outside the database.

Seven more, each with a bad and a good example: `references/red-flags.md`.

## References

Pull the reference that matches the task; keep this file lean and load detail on demand.

- **[references/notion-pm-playbook.md](references/notion-pm-playbook.md)** — the full operational playbook: core concepts (hierarchy, property types, views, block types), the seven core workflows (workspace setup, PRD/OKR/Roadmap/Decisions/Review DB design, linking, sync), inline API/query examples, best practices, troubleshooting, and success criteria. Read when building or refactoring a workspace.
- **[references/notion-api-patterns.md](references/notion-api-patterns.md)** — full REST API call catalog with request/response examples, targeting `Notion-Version: 2025-09-03` (databases → data sources; as of September 2026). Read when authoring API integrations.
- **[references/notion-database-design-for-pm.md](references/notion-database-design-for-pm.md)** — canonical schemas for PRDs, OKRs, Roadmap, Decisions, Reviews. Read when designing the database relations.
- **[references/red-flags.md](references/red-flags.md)** — concrete examples of how Notion PM setups go wrong and how to fix them. Read when reviewing a workspace for quality.
- **assets/notion-prd-template.md** — PRD page template using Notion-native blocks.
- **assets/notion-roadmap-template.md** — Roadmap database schema and view definitions.
- **assets/notion-okr-template.md** — OKR database schema with Wodtke confidence model.
- Notion API docs: https://developers.notion.com/ — reference: https://developers.notion.com/reference/intro — changelog: https://developers.notion.com/page/changelog

## Scope & Limitations

**In Scope:** Notion workspace and Teamspace setup, database design for PRDs/OKRs/Roadmap/Decisions/Reviews/1:1s, view design, property and relation modeling, page architecture, Notion REST API authoring, sync pattern design with Jira/Linear/GitHub, governance and review cadences.

**Out of Scope:** Notion administration (SCIM, SAML, billing) at the workspace level beyond Teamspace setup. Jira space and project configuration (hand off to `jira-expert/` and `confluence-expert/`). Linear configuration (hand off to `linear-expert/`). Strategic OKR setting (hand off to `execution/brainstorm-okrs/`). Story splitting and backlog refinement (hand off to `execution/backlog-refinement/`, `execution/story-splitting/`).

**Limitations:** Notion's API rate limits (~3 req/s) make it unsuitable for very high-throughput sync; batch and queue. Status properties cannot have options created via the API in lower plan tiers; pre-create options manually. Rollups cannot reference rollups in older API versions; chain via formulas where needed. Page-level permissions can be overridden in unexpected ways by Teamspace-level changes. Notion is not a real-time collaboration substitute for chat; do not try to replace Slack with comments.

## Integration Points

| Integration | Direction | What Flows |
|---|---|---|
| `jira-expert/` | Notion ↔ Jira | PRD-to-Epic creation; Jira issue embeds in PRD pages |
| `confluence-expert/` | Migration | When moving from Confluence to Notion, structure and content mapping |
| `linear-expert/` | Notion ↔ Linear | PRD-to-Project creation; Linear progress rollups into Notion |
| `execution/create-prd/` | PRD → Notion | PRD scaffolder output rendered as Notion blocks via `--format notion` |
| `execution/brainstorm-okrs/` | OKR → Notion | OKR validator output written to the OKR DB |
| `execution/outcome-roadmap/` | Roadmap → Notion | Roadmap rows materialized in the Roadmap DB |
| `execution/daci-framework/` | Decision → Notion | DACI decisions logged in the Decisions DB |
| `execution/status-update-generator/` | Notion → Status | Weekly status pulls aggregates from PRDs/OKRs DBs |
| `execution/release-notes/` | Notion → Release | Shipped PRDs feed release notes input |
| `senior-pm/` | Notion → Portfolio | OKR and Roadmap DBs feed portfolio reports |
| `discovery/interview-synthesis/` | Research → Notion | Customer research database populated from interview synth output |
