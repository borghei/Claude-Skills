# Productboard Operations Playbook

> Read this when setting up a workspace, running the daily Insight triage, configuring Drivers/scoring, planning Releases/Roadmaps, scripting the REST API, or diagnosing workflow failures. Concepts, the 9 core workflows, inline API call catalog, best practices, troubleshooting, and success criteria.

## Concepts

### Data Model

| Entity | Purpose | Key fields |
|---|---|---|
| **Workspace** | Top-level account; one company has one workspace | `name`, `plan_tier`, `members[]` |
| **Product** (legacy) / **Workspace** | Top-level container in some plans | varies |
| **Component** | Hierarchical grouping for Features (e.g. `Reporting > Dashboards > Filters`) | `id`, `name`, `parent_id` |
| **Feature** | The atomic prioritization unit; can have parent and child Features | `id`, `name`, `description`, `status`, `component_id`, `parent_id`, `tags[]`, `custom_fields` |
| **Insight** (also called "Note") | An inbound customer evidence item; lives in the Insights inbox until linked to Features | `id`, `title`, `content`, `source`, `customer{}`, `tags[]`, `feature_links[]` |
| **Customer** | A profile that can be associated with Insights and Companies | `id`, `email`, `external_id`, `company` |
| **Company** | An account-level grouping of Customers (typically pulled from CRM) | `id`, `name`, `mrr`, `segment` |
| **Driver** | A weighted prioritization criterion (e.g. "Revenue Impact", "Strategic Fit", "Customer Demand") | `id`, `name`, `weight`, `scoring_scale` |
| **Objective** | A strategic theme; Features can be linked to Objectives | `id`, `name`, `time_horizon` |
| **Release** | A time-boxed grouping of Features for delivery planning | `id`, `name`, `start_date`, `end_date`, `feature_ids[]` |
| **Release Group** | A category of Releases (e.g. "Q3 2026") | `id`, `name`, `release_ids[]` |
| **Roadmap view** | A saved configuration of Features filtered and grouped for presentation | UI construct |
| **Custom field** | User-defined Feature attribute (single select, multi-select, number, text, date) | `id`, `name`, `type`, `options[]` |

### Insights vs Features vs Drivers — the three layers

The mental model that makes Productboard click:

```
INSIGHTS (evidence)          FEATURES (candidates)         DRIVERS (criteria)
─────────────────            ──────────────────            ──────────────────
Slack message    ──┐
Salesforce note  ──┼──link──> Feature: "Shareable read-only link"  ──score──>  Revenue impact: 8/10
Intercom thread  ──┤                                                            Strategic fit:   7/10
NPS verbatim     ──┘                                                            Cust demand:     9/10
                                                                                ─────────
                                                                                composite: 8.1
```

Insights are evidence; Features are decisions; Drivers are the scoring system. The Insight-to-Feature link is the system's most important relationship: it lets the team answer "how many real customers asked for this and who are they?" with a click.

### Importance × Evidence

Productboard's Driver scoring is a 2D model: each Feature gets a score (Importance) per Driver, and each Driver has a weight. The composite Feature score is the weighted average.

Evidence (linked Insights) is the supporting data; it does not directly compute the score but is visible alongside the score for context. A high score without supporting Insights is a flag — the team is prioritizing based on opinion rather than evidence.

## Core Workflows

### 1. Workspace and Hierarchy Setup

1. Create the workspace. Set timezone, locale, currency.
2. Invite members; assign roles (Admin, Maker, Contributor, Viewer). Roles in Productboard are global; team-level restrictions come via Features access controls (paid tiers).
3. Define the **Component hierarchy** before adding Features. Common patterns:
   - By product area: `Reporting`, `Onboarding`, `Integrations`, `Billing`, `Platform`
   - By customer journey: `Acquisition`, `Activation`, `Retention`, `Expansion`
   - By team ownership: maps Component to engineering team — useful if engineering teams are stable, fragile if reorgs are frequent.
4. Decide on **Feature naming convention**. Avoid embedding solutions in names. Prefer "Shareable read-only dashboard view" to "PDF export button".
5. Create **Tags** for orthogonal attributes (e.g. `customer-segment/enterprise`, `effort/L`, `theme/AI`).
6. Create **Custom fields** for anything that doesn't fit Tags. Common custom fields: T-shirt size, Engineering owner, Design owner, External ticket ID.
7. **HANDOFF TO**: team leads to start populating Features and linking Insights.

### 2. Insight Inbox Triage (daily ritual)

Productboard's Insight inbox is the central inbound surface. Untriaged Insights pile up quickly if there's no daily ritual.

**Daily inbox triage** (one PM, ~15 minutes):

1. Filter the inbox to "Not yet processed" Insights.
2. For each Insight:
   - **Read the verbatim**. Resist paraphrasing.
   - **Link to one or more Features**. If a matching Feature doesn't exist, create one.
   - **Tag with relevant attributes** (customer segment, theme, source).
   - **Mark "processed"**.
3. If an Insight doesn't map to a Feature within 60 seconds, park it in the "Needs discussion" view and come back to it in the weekly review.

Anti-pattern: creating one Feature per Insight. This explodes Feature count and dilutes scoring. Multiple Insights should commonly map to the same Feature.

See `assets/productboard-insight-triage-workflow.md` for a full SOP.

### 3. Driver Configuration

Drivers are how the team's strategy becomes scoring weight. Configuration steps:

1. Decide on 3-5 Drivers. More than 5 Drivers becomes noise; fewer than 3 gives insufficient resolution.
2. Common Driver sets:
   - **General SaaS**: Revenue Impact, Strategic Fit, Customer Demand, Effort, Risk
   - **Enterprise-led**: Top Account Demand, Renewal Risk, New Logo Acquisition, Strategic Fit, Effort
   - **Growth-led**: Activation Lift, Retention Lift, ARPU Lift, Effort, Risk
3. Assign weights. Weights should sum to 100% (Productboard normalizes if they don't). Higher-weight Drivers move scores more.
4. Define the scoring scale per Driver (typically 0-10). Document what each level means — a "9" on Customer Demand should have a concrete definition (e.g. "≥ 20 customer requests in the last 90 days").
5. Review Driver weights quarterly. If strategy shifts (growth-focused → enterprise-focused), the weights need to shift correspondingly.

See `assets/productboard-driver-template.md` for a Driver definition template.

### 4. Feature Scoring

For each Feature in the candidate pool:

1. Score against each Driver on the defined scale (0-10).
2. Productboard computes the composite weighted score.
3. The Features table can be sorted by score; the top N candidates feed Roadmap planning.

**Discipline**: do not score every Feature in the workspace. Score only Features that are realistic candidates for the next 1-2 release horizons. Scoring 500 Features is a productivity trap.

### 5. Release and Roadmap Planning

1. Define **Releases** as time-boxed delivery containers (e.g. "Q3 2026", "September 2026 Launch").
2. Drag high-scoring Features into the appropriate Release. Productboard's "Plan" view supports this.
3. Set Feature status as Features move through their lifecycle: Idea → Discovery → Planned → In Progress → Done.
4. Create **Roadmap views** filtered for audiences:
   - Executive Roadmap: Releases grouped by Quarter, top Features per Release, status badges
   - Customer-Facing Roadmap (uses Productboard Portal): Features in "Planned" or later, with descriptions sanitized for external sharing
   - Internal Engineering Roadmap: full detail, integration with Jira/Linear status
5. **HANDOFF TO**: Eng for execution via Jira/Linear integration.

### 6. Two-Way Integration with Jira / Linear / Azure DevOps

Productboard's Jira/Linear/ADO integration is bidirectional:

- **Productboard → Jira/Linear**: When a Feature reaches "Planned", push it as an Epic to Jira/Linear. Sync description, owner, target Release date.
- **Jira/Linear → Productboard**: Status updates on the Epic flow back to Productboard. A merged PR closing the Epic marks the Feature as Done.
- **Child issues** (Stories, Tasks, Subtasks) live in Jira/Linear, not Productboard. Productboard tracks the Feature; the engineering tracker tracks the implementation breakdown.

Setup steps:

1. Install the integration in Productboard settings.
2. Map Productboard statuses to engineering-tracker statuses.
3. Map Productboard Releases to Jira Versions or Linear Cycles/Projects.
4. Decide on the push trigger (auto on status change, or manual).
5. Decide on field-mapping (custom fields, owners, dates).

### 7. Customer & Company Sync (Salesforce / HubSpot)

Productboard's value scales with customer-data fidelity. Sync from your CRM:

1. Install the Salesforce / HubSpot integration.
2. Sync Companies (with MRR/ARR, segment, renewal date) and Customers (with email, role, account).
3. Use Company segment and MRR to enrich Insight context. When a feature is requested by "Acme Corp (Enterprise, $480k ARR)", the Insight inherits that context.
4. Use Company MRR as a Driver input for "Customer Demand" or as a separate "Revenue at Risk" Driver.

### 8. Inbound Insight Capture

Productboard captures Insights from multiple channels:

| Channel | Method |
|---|---|
| Email | Forward to `pbinbox-{workspace}@productboard.com` |
| Slack | Productboard Slack app — react with a Productboard emoji to convert a message to an Insight |
| Intercom | Native integration — convert Intercom conversations to Insights |
| Salesforce | Native integration — push Salesforce opportunity notes as Insights |
| Zendesk | Native integration |
| Productboard Portal | Customers submit ideas directly (if enabled) |
| Browser extension | Capture from any web page |
| REST API | Programmatic creation — see API patterns below |

Configure intake from at least 2-3 channels at launch. Single-channel capture undercounts demand.

### 9. Bulk Operations via API

Productboard offers a REST API for operations the UI doesn't cover well. Common bulk operations:

- Bulk-create Insights from a CSV / data dump (e.g. importing 2 years of support tickets at onboarding)
- Bulk-update Feature custom fields based on engineering-tracker data
- Reconcile Features with Jira / Linear if integration drift occurs
- Snapshot Feature scores weekly for trend analysis
- Export the prioritization-ranked Feature list for use in another system

API patterns are detailed in `references/productboard-api-patterns.md`.

## API Patterns

Productboard's REST API is **Public API v2** at `https://api.productboard.com/v2` (as of September 2026). v2 became generally available on 2026-04-09 and v1 — the un-prefixed paths called with an `X-Version: 1` header — was scheduled to sunset on 2026-07-08 ([changelog](https://developer.productboard.com/changelog/2026-04-09)). v2 needs no `X-Version` header. Authentication is via Bearer token (`Authorization: Bearer <token>`) plus `Accept: application/json`. API tokens are available on the Pro plan and higher.

Full reference: https://developer.productboard.com/ — migration guide: https://developer.productboard.com/reference/migration-guide

### Authentication

```bash
export PB_TOKEN="<personal-access-token>"
curl -s -H "Authorization: Bearer $PB_TOKEN" -H "Accept: application/json" \
  "https://api.productboard.com/v2/entities?type[]=feature"
```

### List Features

Features, components, products, releases, objectives, initiatives, companies and users all live under one endpoint, `/v2/entities`, filtered by `type[]`:

```bash
curl -s -H "Authorization: Bearer $PB_TOKEN" -H "Accept: application/json" \
  "https://api.productboard.com/v2/entities?type[]=feature&fields[]=name&fields[]=status&fields[]=owner"
```

Response shape:

```json
{
  "data": [
    {
      "id": "3f1c2a9e-6b1d-4d0e-9a51-1b2c3d4e5f60",
      "type": "feature",
      "fields": {
        "name": "Shareable read-only dashboard view",
        "status": { "id": "447eb060-...", "name": "Planned" },
        "owner": { "id": "56caede9-...", "email": "pm@company.com" }
      },
      "relationships": [ { "type": "parent", "target": { "id": "9b8c7d6e-...", "type": "component" } } ],
      "links": { "self": "https://api.productboard.com/v2/entities/3f1c2a9e-...", "html": "https://..." },
      "createdAt": "2026-04-01T12:00:00Z",
      "updatedAt": "2026-05-20T15:30:00Z"
    }
  ],
  "links": { "next": "https://api.productboard.com/v2/entities?pageCursor=..." }
}
```

Paginate by following `links.next` until it is `null`. Page size cannot be set in v2 (v1's `pageLimit` is gone).

### Create a Feature

```bash
curl -s -X POST -H "Authorization: Bearer $PB_TOKEN" -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "feature",
      "fields": {
        "name": "Shareable read-only dashboard view",
        "description": "<p>Customers want to share dashboards with stakeholders who do not have an account, especially CFO/board readers.</p>",
        "status": { "name": "New idea" }
      },
      "relationships": [ { "type": "parent", "target": { "id": "<component-uuid>" } } ]
    }
  }' \
  https://api.productboard.com/v2/entities
```

Creates and updates return only `id`, `type` and `links.self`; GET `links.self` for the full record.

### Create an Insight (note)

```bash
curl -s -X POST -H "Authorization: Bearer $PB_TOKEN" -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "textNote",
      "fields": {
        "name": "Acme Corp wants PDF export for board pack",
        "content": "On QBR call, CFO at Acme Corp asked for a way to share dashboards with their board. PDF export was mentioned as a workaround they would accept.",
        "tags": [ { "name": "enterprise" }, { "name": "reporting" }, { "name": "quarterly-business-review" } ]
      },
      "metadata": { "source": { "system": "Salesforce", "recordId": "opp-12345" } },
      "relationships": [ { "type": "customer", "target": { "type": "user", "email": "cfo@acme.com" } } ]
    }
  }' \
  https://api.productboard.com/v2/notes
```

v2 does **not** auto-create the user or company (v1 did): an unknown email returns 404. Create the user first (`POST /v2/entities` with `type: "user"`), then retry.

### Link an Insight to a Feature

```bash
curl -s -X POST -H "Authorization: Bearer $PB_TOKEN" -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{ "data": { "type": "link", "target": { "id": "<feature-uuid>", "type": "link" } } }' \
  https://api.productboard.com/v2/notes/<note-uuid>/relationships
```

### List Releases

```bash
curl -s -H "Authorization: Bearer $PB_TOKEN" -H "Accept: application/json" \
  "https://api.productboard.com/v2/entities?type[]=release"
```

### Add a Feature to a Release

v1's `/release-assignments` is replaced by a `link` relationship from the feature to the release:

```bash
curl -s -X POST -H "Authorization: Bearer $PB_TOKEN" -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{ "data": { "type": "link", "target": { "id": "<release-uuid>" } } }' \
  https://api.productboard.com/v2/entities/<feature-uuid>/relationships
```

### Update a Custom Field on a Feature

Custom fields are ordinary entity fields keyed by their UUID (discover them with `GET /v2/entities/configurations/feature`):

```bash
curl -s -X PATCH -H "Authorization: Bearer $PB_TOKEN" -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{ "data": { "fields": { "<tshirt-field-uuid>": { "name": "Large" } } } }' \
  https://api.productboard.com/v2/entities/<feature-uuid>
```

### Webhook subscription

Subscribe to events for outbound automation:

```bash
curl -s -X POST -H "Authorization: Bearer $PB_TOKEN" -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "fields": {
        "name": "PM automation",
        "events": [
          { "eventType": "feature.created" },
          { "eventType": "feature.updated" },
          { "eventType": "note.created" }
        ],
        "notification": {
          "url": "https://your-app.example.com/webhooks/productboard",
          "version": 1,
          "headers": { "authorization": "Bearer <shared-secret>" }
        }
      }
    }
  }' \
  https://api.productboard.com/v2/webhooks
```

Productboard sends the configured `headers.authorization` value with every notification; reject requests that do not carry it.

### Not available in v2 (as of September 2026)

Note followers and feedback-form endpoints were removed permanently; company custom-field *definition* management and tag filters on notes search are listed as future work; Driver scores are not exposed. See the "Not carried over to v2" section of `references/productboard-api-patterns.md`.

### Rate limits

The documented default is 50 requests per second per access token (as of September 2026). `X-RateLimit-Limit` / `X-RateLimit-Remaining` headers are returned, and `Retry-After` (seconds) on 429; back off accordingly.

### Pagination

List endpoints use cursor-based pagination: follow `links.next` (which carries a `pageCursor`) until it is `null`. Always paginate; do not assume a single page returns everything.

## Best Practices

### Hierarchy and naming

- Define the Component hierarchy before bulk-creating Features. Reshuffling Components after the fact is painful.
- Feature names describe the customer outcome, not the implementation. Good: "Share a dashboard with non-account users". Bad: "PDF export button".
- Use parent/child Features sparingly. Two levels of Feature hierarchy is the practical maximum.

### Insight discipline

- Every Insight must have a `customer` field populated. Insights without customer attribution lose their value (you can't filter by segment or by company).
- The verbatim of the Insight is the most important field. Resist summarizing at intake.
- Re-link Insights when a Feature is split or merged. Orphan Insights degrade prioritization signal.

### Driver and scoring discipline

- Drivers should map to the company's current strategic themes. Re-weight at least quarterly.
- Score discipline: only score Features that are realistic candidates for the next 1-2 release horizons. Don't score the long tail.
- The composite score is a sorting aid, not a decision. Drivers + Insights together inform the call.

### Releases

- One Release = one time-boxed delivery window (a quarter, a sprint, a launch month). Avoid open-ended Releases ("Future").
- A Release with > 15 Features is probably too large. Split.
- Tie Releases to engineering Cycles/Versions via integration so status flows automatically.

### Roadmap views

- Build dedicated views for each audience (Exec, Customer, Engineering, Sales). Do not show engineering details to customers, or customer-facing names to engineering.
- Public-facing Roadmap (Portal): only Features in "Planned" or later; sanitized descriptions; no internal commitments.
- Refresh exec views before every monthly business review.

### API hygiene

- Cache Workspace-level IDs (Component IDs, Custom Field UUIDs from `/v2/entities/configurations`, Status IDs). Looking them up by name on every call wastes rate-limit budget.
- Use webhooks for event-driven workflows. Polling is expensive and slow.
- Call the `/v2/...` paths only; v1 (`X-Version: 1`) was scheduled to sunset on 2026-07-08. Watch the developer changelog for additive v2 changes.
- Implement idempotency for bulk-create operations (use external IDs to prevent duplicates on retry).

### Governance

- Restrict workspace admin to 2-3 people. Component restructuring and Driver re-weighting are high-stakes operations.
- Audit Features quarterly: archive everything with status "Idea" that hasn't been touched in 6 months and has zero linked Insights.
- Audit Customers/Companies quarterly: sync drift with CRM is the most common Productboard data-quality issue.

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---|---|---|
| Insights from Slack/Intercom not appearing | Source integration not configured for the workspace, or the user submitting lacks permission | Check Productboard Settings → Integrations; confirm the connected accounts; check user permissions in the source app |
| Feature score not updating after linking new Insights | Score is driven by Drivers (manual scoring), not by Insight count; linking does not auto-recompute | Open the Feature, manually update the relevant Driver score (e.g. Customer Demand) to reflect the new evidence |
| Jira/Linear integration shows stale status | Webhook delivery failure, or the integration's user lost access to the project | Check Productboard integration logs; reconnect; verify the integration user is a member of the Jira/Linear project |
| Customer / Company data out of sync with CRM | Salesforce/HubSpot integration is one-way (CRM → Productboard) and runs on a schedule; recent CRM changes won't appear immediately | Trigger manual sync from Settings → Integrations; for real-time needs, use the Productboard API to push customer data on demand |
| API returns 429 (rate limit) | Workspace rate limit exceeded; common during bulk imports | Respect `Retry-After` header; spread bulk operations over time; consider Enterprise plan for higher limits |
| Insights inbox grows faster than triage capacity | Intake is wider than the daily ritual; multiple channels feeding without filtering | Reduce intake channels OR raise the triage cadence (twice daily); add automated rules to pre-tag Insights by source |
| Productboard Portal shows internal feature names externally | Roadmap view filter not applied; or Features marked public without renaming | Audit Portal-visible Features; ensure customer-facing Feature name is sanitized; use a separate Custom Field for internal-only naming |
| Drivers don't match how the team prioritizes | Weights stale from a previous strategy phase | Run the quarterly Driver review; collect input from PM/Eng/Sales/CS; recalibrate weights to current strategy |
| Cannot find a Feature in search | Feature is archived, or in a Component the user lacks access to | Toggle "Include archived" in search; check Component-level permissions; confirm workspace role |
| Insights are linked to too many Features (signal dilution) | PM links generously without judgment | Restrict linking to the 1-3 Features the Insight most directly supports; train the team that an Insight linked to 10 Features is informationally worthless |

## Success Criteria

- Component hierarchy is stable for 2+ quarters without restructuring
- Insight inbox is triaged daily; "Not yet processed" queue depth stays under 50 items
- 90%+ of Insights have a customer/company association
- All Features in the next 2 Release horizons are scored against current Drivers
- Drivers are re-weighted at least quarterly to match current strategy
- Jira/Linear integration delivers status updates within 5 minutes of the source event 95%+ of the time
- Customer-facing Roadmap (Portal) is refreshed monthly; no leaked internal commitments
- API rate-limit 429 responses stay under 1% of total API calls
- Exec Roadmap is reviewed monthly at the business review; presentation requires no Productboard-specific explanation
- New PM onboarding includes a Productboard walkthrough and a triage shadow within first 30 days
