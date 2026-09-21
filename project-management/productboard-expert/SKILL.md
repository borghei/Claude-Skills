---
name: productboard-expert
description: >
  Productboard expert for workspace setup, Insight-to-Feature triage,
  Driver scoring, Releases, Roadmap views, and REST API automation. Use
  for Productboard administration, prioritization workflows, and
  programmatic API operations.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-integration
  updated: 2026-06-15
  tech-stack: [productboard, rest-api, insights, drivers, features, releases]
  tags: [productboard, prioritization, insights, drivers, roadmap, salesforce, intercom, slack]
---
# Productboard Expert

Master-level expertise in Productboard workspace configuration, Insight inbox triage, Driver-based prioritization, Feature hierarchy management, Releases and Roadmap views, REST API operations, and two-way integration with Jira, Linear, Azure DevOps, Salesforce, Intercom, and Slack. Productboard sits between customer-feedback intake (Slack/Intercom/Salesforce/email) and the engineering tracker (Jira/Linear), with an opinionated three-layer model that differs meaningfully from generic issue trackers.

## Overview

Productboard separates three layers: **Insights** (inbound customer evidence), **Features** (candidate product changes organized in Components and parent/child hierarchy), and **Drivers + Releases** (the prioritization framework — Drivers = weighted criteria, Releases = time-boxed delivery groupings). Insights link to Features (many-to-many); Features score against Drivers; high-scoring Features get added to Releases; Releases push down to Jira/Linear epics. The flow is **inbox → triage → prioritize → ship**.

The job of a Productboard expert is to operate fluently inside this model: configure the workspace cleanly, run the Insight inbox without backlog, design Driver weightings that match company strategy, and write API automations for what the UI does not cover.

## Core Capabilities

- **Workspace & hierarchy setup** — Components, Feature taxonomy, Tags, custom fields, roles
- **Insight inbox triage** — the highest-leverage daily ritual; verbatim discipline, multi-Feature linking
- **Driver configuration & Feature scoring** — 3-5 weighted Drivers, composite scoring, quarterly re-weighting
- **Releases & Roadmap views** — time-boxed delivery, audience-specific views, Portal for customers
- **REST API automation** — bulk Insight/Feature operations, webhooks, custom-field updates, pagination
- **Two-way integration** — Jira/Linear/Azure DevOps (Features↔Epics) and Salesforce/HubSpot/Intercom/Zendesk (Insight capture)

## When to Use

- Setting up a new Productboard workspace, Component hierarchy, or Feature taxonomy
- Configuring Drivers and weighting them against strategic objectives
- Running the Insight inbox triage workflow (the highest-leverage daily ritual)
- Configuring two-way Jira/Linear/Azure DevOps integration or CRM customer sync
- Building Roadmap views for executives, customers, and internal teams
- Writing API calls to bulk-create Insights, update Features, or read prioritization data
- Migrating from spreadsheet-based prioritization, or troubleshooting "Insights aren't flowing", "scores aren't updating", and similar workflow failures

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/operations-playbook.md](references/operations-playbook.md)** — concepts (data model, three layers, Importance×Evidence), all 9 core workflows (setup, triage, Drivers, scoring, Releases, integrations, capture, bulk ops), inline API call catalog, best practices, troubleshooting table, and success criteria. Read this for any setup, triage, scoring, or API task.
- **[references/productboard-api-patterns.md](references/productboard-api-patterns.md)** — full REST API call catalog with curl examples and JSON shapes. Read when scripting against the API.
- **[references/productboard-vs-jira-vs-linear.md](references/productboard-vs-jira-vs-linear.md)** — when to use Productboard alongside (or instead of) Jira/Linear; concept translation. Read when positioning the tool in an existing stack.
- **[references/red-flags.md](references/red-flags.md)** — common ways this skill's output goes wrong, with fixes. Read before finalizing a workspace design or prioritization recommendation.
- Assets: `assets/productboard-feature-template.md` (Feature structure), `assets/productboard-insight-triage-workflow.md` (daily triage SOP), `assets/productboard-driver-template.md` (Driver definitions). Official docs: https://developer.productboard.com/ · https://help.productboard.com/

## Scope & Limitations

**In Scope:** Workspace and Component hierarchy setup, Insight inbox triage, Driver configuration and Feature scoring, Releases and Roadmap views (internal and customer-facing), Productboard REST API operations (Features, Insights, Releases, custom fields, webhooks), two-way integration setup with Jira/Linear/Azure DevOps, customer-data sync from Salesforce/HubSpot, bulk operations via API, Portal configuration.

**Out of Scope:** Engineering-side Jira/Linear configuration (see `jira-expert/`, `linear-expert/`). Strategic prioritization framework selection (see `execution/prioritization-frameworks/`). PRD authoring (see `execution/create-prd/`). Customer interview synthesis (see `discovery/interview-synthesis/`).

**Limitations:** API recipes target Public API v2 (`/v2/...`); v1 (`X-Version: 1`) was scheduled to sunset on 2026-07-08, and a few v1 capabilities (note followers, feedback forms, company field-definition management) have no v2 equivalent as of September 2026. API rate limits apply per access token (documented default 50 requests/second); aggressive scripts still compete with integrations sharing that token. The Salesforce/HubSpot integration is one-way (CRM → Productboard) on a schedule, not real time. Drivers max out at 10 per workspace on most plans. Roadmap views are good for time-bound delivery (Releases) but weaker for outcome-based roadmaps (Now/Next/Later) — augment with `execution/outcome-roadmap/`. Per-Component access control is an Enterprise feature.

## Integration Points

| Integration | Direction | What flows |
|---|---|---|
| `jira-expert/` | Productboard ↔ Jira | Features push as Epics; status flows back; Sprint plan derived from prioritization |
| `linear-expert/` | Productboard ↔ Linear | Features push as Projects/Issues; Cycle assignment from Release dates |
| `execution/prioritization-frameworks/` | Bidirectional | Drivers operationalize RICE/ICE/WSJF; external scores import as custom fields |
| `execution/create-prd/` | Productboard → PRD | High-priority Features become PRDs; PRD link returns as custom field |
| `execution/outcome-roadmap/` | Bidirectional | Outcome themes map to Objectives; Releases give the delivery side |
| `execution/roadmap-communication/` | Productboard → Comms | Customer-facing Roadmap variants pull from Portal |
| `execution/customer-feedback-triage/` | Bidirectional | Triaged feedback clusters become Insights; inbox is the triage entry point |
| `execution/release-notes/` | Productboard → Release Notes | Completed Features in a Release become release-note line items |
| `senior-pm/` | Productboard → Portfolio | Driver scores and Feature distribution feed portfolio health |
| `notion-pm/` | Productboard ↔ Notion | Roadmap embeds into Notion; deep PRDs live in Notion linked from Features |
| `discovery/interview-synthesis/` | Bidirectional | Interview insights become Notes; high-evidence Features motivate interviews |
| `business-growth/customer-success/` | CS → Productboard | CS is a primary Insight source via Salesforce / Intercom integration |
