# Notion PM Playbook

> Read this when standing up or refactoring a Notion PM workspace: core concepts (hierarchy, property types, views, blocks), the seven core workflows (workspace setup, PRD/OKR/Roadmap/Decisions/Review DB design, linking, sync), inline API/query patterns, best practices, troubleshooting, and success criteria.

## Concepts

### Workspace Hierarchy

| Level | Purpose | Example |
|---|---|---|
| **Workspace** | Top-level account, billing scope, SCIM/SAML | "Acme Inc" |
| **Teamspace** | Permission boundary for a team or function | "Product", "Engineering" |
| **Page** | A document or container | "Onboarding wiki" |
| **Database** | Typed collection of pages (rows = pages with properties) | "PRDs DB", "OKRs DB" |
| **Database row** | A page whose parent is a database | "PRD: Self-Serve Signup" |
| **Linked Database** | A view of another database, embedded in a page | A "This Quarter" view of the PRDs DB |
| **Block** | A unit of content inside a page (paragraph, heading, callout, toggle, image, embed) | "Heading 2", "Callout", "Synced Block" |

### Property Types (the heart of database design)

| Type | Use | Notes |
|---|---|---|
| `title` | The row's name; every database has exactly one | Renders as the page title |
| `rich_text` | Long-form text | Supports markdown formatting |
| `select` | Single-value tag from a closed list | E.g. PRD status: Draft / Review / Approved / Shipped |
| `multi_select` | Multi-value tags | E.g. PRD area: API, Web, Mobile |
| `status` | Special select with three groups: To-do, In progress, Complete | First-class in views |
| `date` | Date or date range | Supports reminders |
| `people` | Reference to workspace member(s) | Owner, reviewer |
| `files` | Attached files or URLs | Specs, mocks |
| `checkbox` | Boolean | Approved? |
| `url`, `email`, `phone` | Typed contact data | Customer DB |
| `number` | Numeric with optional format (percent, currency) | Confidence, RICE score |
| `formula` | Computed from other properties | E.g. RICE = (R*I*C)/E |
| `relation` | Link to row(s) in another database | PRD → OKR, PRD → Roadmap Item |
| `rollup` | Aggregate property of related rows | "Sum of estimates from linked Linear issues" |
| `created_time`, `last_edited_time` | System | Always present |
| `created_by`, `last_edited_by` | System | Always present |
| `unique_id` | Auto-incremented short ID with prefix | E.g. PRD-001, DEC-042 |

### Views

Every database can present multiple views, each with its own filter, sort, group, and property visibility:

- **Table** — spreadsheet-like; default editing view
- **Board** — Kanban grouped by a select/status property; great for PRD status, OKR confidence
- **Timeline** — Gantt-like; great for Roadmaps when there is a date-range property
- **Calendar** — month view; great for launches, reviews, sprint ceremonies
- **Gallery** — card view with the cover image; great for customer research notes or design reviews
- **List** — minimal, dense; great for backlog-style browsing

### Notion-Compatible Markdown / Block Types

Notion is not strictly Markdown, but Markdown extensions are recognized in many contexts. Key blocks used in PM artifacts:

- Headings: `#`, `##`, `###`
- Callouts: `> [!NOTE]`, `> [!WARNING]`, `> [!TIP]` (in Markdown imports; native block in UI)
- Toggle blocks: collapse-expand sections (great for "Open questions", "Out of scope")
- Synced blocks: a single block reused across pages (Definition of Done, glossary)
- Code blocks: fenced with language for syntax highlighting
- Linked databases: a view of another DB embedded inline
- Mentions: `@person`, `@page`, `@date`
- Bookmarks: a URL becomes a rich preview card
- Embeds: Figma, Loom, GitHub Gist, YouTube
- Math: `$equation$` inline; `$$equation$$` block

## Core Workflows

### 1. Workspace Setup for a Product Team

1. Create a Teamspace named `Product`.
2. Create the foundational databases as direct children of the Teamspace:
   - PRDs
   - OKRs (with quarter as a property)
   - Roadmap
   - Decisions
   - Customer Research
   - Sprint Reviews (or Cycle Reviews if on Linear)
   - 1:1s
3. Define the relations between them (see `references/notion-database-design-for-pm.md`).
4. Create a Teamspace home page with a curated set of linked database views.
5. Establish naming conventions; pin them in a "Team conventions" page.
6. Set permissions: full access for product team, edit for engineering, view for everyone else.
7. **HANDOFF TO**: PMs to start populating PRDs and OKRs.

### 2. PRD Database Design

A PRD is a row in the PRDs database. Properties:

| Property | Type | Purpose |
|---|---|---|
| `Title` | title | PRD name |
| `Status` | status | Draft / In Review / Approved / In Build / Shipped / Killed |
| `Owner` | people | Driving PM |
| `Author` | people | Original drafter |
| `Reviewers` | people | DRI, Eng lead, Design lead |
| `Target Date` | date | Aspirational launch |
| `Priority` | select | P0 / P1 / P2 / P3 |
| `OKR` | relation → OKRs | Which OKR(s) this serves |
| `Roadmap Item` | relation → Roadmap | Which roadmap item this delivers |
| `Linear Project` | url | Link to the Linear Project tracking the work |
| `Jira Epic` | url | If using Jira |
| `Tech Lead` | people | Engineering DRI |
| `Design Lead` | people | Design DRI |
| `Approved On` | date | Set when status → Approved |
| `Shipped On` | date | Set when status → Shipped |
| `Document` | (page body) | The PRD itself, with the template from `assets/notion-prd-template.md` |

Build views:
- **My PRDs** (filter: Owner is me)
- **In Review** (filter: Status = In Review; sort by Target Date)
- **This Quarter** (filter: Target Date in this quarter, group by Status)
- **All by Owner** (group by Owner, hide killed)

### 3. OKR Database Design

| Property | Type | Purpose |
|---|---|---|
| `Title` | title | KR or Objective name |
| `Type` | select | Objective / Key Result |
| `Parent Objective` | relation (self) | For KRs, link to parent Objective |
| `Quarter` | select | Q1 2026, Q2 2026, ... |
| `Owner` | people | Single accountable owner |
| `Status` | status | Not started / On track / At risk / Off track / Hit / Missed |
| `Confidence` | select | 10 / 7 / 5 / 3 (Wodtke scale) |
| `Target` | rich_text | The measurable target |
| `Current` | rich_text | Current value (updated weekly) |
| `Progress` | number (percent) | Manual or formula |
| `PRDs` | relation → PRDs | PRDs that contribute to this KR |
| `Notes` | rich_text | Context, blockers |

Views:
- **This Quarter by Objective** (group by Parent Objective)
- **My OKRs** (filter: Owner is me)
- **At Risk / Off Track** (filter on Status)

### 4. Roadmap Database Design

| Property | Type | Purpose |
|---|---|---|
| `Title` | title | Initiative name |
| `Horizon` | select | Now / Next / Later (or Q1 / Q2 / Q3 / Q4) |
| `Status` | status | Discovery / Defining / Building / Shipped / Killed |
| `Owner` | people | Driving PM |
| `Customer Outcome` | rich_text | Outcome statement |
| `OKR` | relation → OKRs | What this rolls up to |
| `PRDs` | relation → PRDs | Underlying PRDs |
| `Start` | date | Range start |
| `End` | date | Range end |
| `Confidence` | select | High / Medium / Low |
| `Audience` | multi_select | Internal / Customer / Exec |

Views:
- **Timeline** (grouped by Horizon, dates from Start/End)
- **Now/Next/Later Board** (grouped by Horizon)
- **Customer-Facing** (filter: Audience contains Customer)

### 5. Decisions (ADR-style) Database

| Property | Type | Purpose |
|---|---|---|
| `Title` | title | Decision name |
| `ID` | unique_id (prefix DEC) | Auto-numbered |
| `Status` | select | Proposed / Approved / Superseded / Reversed |
| `Date` | date | Decision date |
| `DACI Driver` | people | The Driver |
| `Approver` | people | The Approver |
| `Contributors` | people | Contributors |
| `Informed` | people | Informed parties |
| `Context` | rich_text | What forced the decision |
| `Options` | (page body) | Options considered with pros/cons |
| `Decision` | rich_text | Chosen path |
| `Supersedes` | relation (self) | If this overrides a prior decision |

### 6. Sprint / Cycle Review Database

| Property | Type | Purpose |
|---|---|---|
| `Title` | title | "Sprint 23 Review" or "Cycle 47 Review" |
| `Cycle Number` | number | For sorting |
| `Date` | date | Review date |
| `Team` | select | Engineering, Design, Data, ... |
| `Velocity` | number | Story points or issue count |
| `Health` | select | Green / Yellow / Red |
| `Demos` | rich_text | What was shown |
| `Outcomes` | rich_text | What changed for users |
| `Retro` | (page body) | Liked / Learned / Lacked / Longed-for |

### 7. Linking Strategy

Three layers of linking:

1. **Relations** for many-to-many DB joins (PRD ↔ OKR, PRD ↔ Roadmap).
2. **Mentions** for one-off references inside page bodies (`@PRD: Self-Serve Signup`).
3. **Sub-pages** only for hierarchical content that does not warrant a database (e.g. PRD has a child page "Open Questions").

Avoid: linking with raw markdown links to other Notion pages (loses bidirectionality and search relevance).

### 8. Sync Patterns

**Notion ↔ Jira**
- One-way: build a Zapier/Make/n8n job that, on PRD status change, creates the linked Jira Epic.
- Two-way (advanced): periodically diff PRD status and Jira Epic status; reconcile.
- Embed: paste a Jira issue URL; Notion renders a rich preview (read-only).

**Notion ↔ Linear**
- One-way: on PRD approval, create a Linear Project; store its URL in `Linear Project` property.
- Roll-up: a scheduled job queries Linear's GraphQL API for project progress and writes back to a Notion number property.
- Embed: paste a Linear issue/project URL for a rich preview.

**Notion ↔ GitHub**
- Embed: PR and Issue URLs render as rich previews.
- Custom: a webhook handler creates Decisions DB rows when an ADR is added to a repo.

See `references/notion-api-patterns.md` for the API calls these patterns use.

## API / Query Patterns

The Notion API is REST, served at `https://api.notion.com/v1/`. Auth is via integration tokens (`Authorization: Bearer secret_...`). Every request must include a `Notion-Version` header; these examples use `2025-09-03`, which splits each database into one or more **data sources** (as of September 2026; `2026-03-11` is the newest version). Rows are queried and created against the data source, so first resolve it: `GET /v1/databases/<db_id>` returns `data_sources[].id`. See `references/notion-api-patterns.md` for the full library and the version-change table.

**Query a database** (find all PRDs in review — via its data source):
```bash
curl -X POST https://api.notion.com/v1/data_sources/<data_source_id>/query \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2025-09-03" \
  -d '{
    "filter": {
      "property": "Status",
      "status": { "equals": "In Review" }
    },
    "sorts": [{ "property": "Target Date", "direction": "ascending" }]
  }'
```

**Create a page in a database** (new PRD):
```bash
curl -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2025-09-03" \
  -d '{
    "parent": { "type": "data_source_id", "data_source_id": "<prd_data_source_id>" },
    "properties": {
      "Title":   { "title":  [{ "text": { "content": "PRD: Self-Serve Signup" } }] },
      "Status":  { "status": { "name": "Draft" } },
      "Owner":   { "people": [{ "id": "<user_id>" }] },
      "Target Date": { "date": { "start": "2026-09-30" } }
    },
    "children": [
      { "object": "block", "type": "heading_2",
        "heading_2": { "rich_text": [{ "text": { "content": "Problem" } }] } },
      { "object": "block", "type": "paragraph",
        "paragraph": { "rich_text": [{ "text": { "content": "..." } }] } }
    ]
  }'
```

**Update a page property** (mark PRD approved):
```bash
curl -X PATCH https://api.notion.com/v1/pages/<page_id> \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2025-09-03" \
  -d '{
    "properties": {
      "Status":      { "status": { "name": "Approved" } },
      "Approved On": { "date":   { "start": "2026-05-21" } }
    }
  }'
```

**Append blocks to a page** (add a section):
```bash
curl -X PATCH https://api.notion.com/v1/blocks/<page_id>/children \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2025-09-03" \
  -d '{
    "children": [
      { "object": "block", "type": "callout",
        "callout": {
          "icon":     { "type": "emoji", "emoji": "ℹ" },
          "rich_text": [{ "text": { "content": "Approved by Product Council on 2026-05-21." } }]
        }
      }
    ]
  }'
```

**Paginate through a large database** (handle `has_more`):
```bash
# Pass `start_cursor` from the previous response on each subsequent call
curl -X POST https://api.notion.com/v1/data_sources/<data_source_id>/query \
  -d '{ "page_size": 100, "start_cursor": "<cursor>" }'
```

**Compound filter** (PRDs owned by me and in review):
```json
{
  "filter": {
    "and": [
      { "property": "Owner",  "people": { "contains": "<user_id>" } },
      { "property": "Status", "status": { "equals": "In Review" } }
    ]
  }
}
```

### Rate Limits

Notion rate-limits at ~3 requests/second per integration with bursts permitted. On `429`, honor the `Retry-After` header. For bulk operations, batch and add 300-500ms sleep between writes.

## Best Practices

**Database design**
- Decide property types up front; changing a property type later can be lossy.
- Prefer `select` and `status` over free-text where values are constrained; this enables filters and Boards.
- Use `relation` for any many-to-many link between artifact types; do not paste page URLs into rich_text.
- Use `unique_id` for any artifact you want to reference externally (PRD-042, DEC-017).

**Views over duplication**
- Never copy a database row to display it elsewhere; embed a Linked Database View instead.
- Each page should have at most one source-of-truth database; everything else is a view.

**Page architecture**
- Teamspace home page = a curated dashboard of linked views; not a content dumping ground.
- Use synced blocks for content reused across many pages (e.g. Definition of Done).
- Cap page nesting at 3 levels for navigability.

**Governance**
- Every active page in a database must have an Owner and a `Last Reviewed` date.
- Quarterly review: archive Shipped/Killed PRDs older than 12 months.
- Permissions at the Teamspace level whenever possible; avoid per-page overrides.

**API hygiene**
- Cache database IDs, data source IDs, property IDs, and user IDs.
- Always set `Notion-Version` header explicitly to avoid silent breaks.
- Use webhooks (via Notion's official webhooks where available, or Zapier/Make as fallback) instead of polling.

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---|---|---|
| API returns 404 for a database the integration "should" see | Integration has not been explicitly shared on the database (or its parent page) | Open the database in Notion, click "..." → "Add connections" → select the integration |
| Rollup property shows nothing | The relation property is empty, or the rolled-up property is filtered out | Confirm the relation has linked rows; check the rollup's source property; rebuild the rollup if added recently |
| Status property cannot be set via API | The status name does not exactly match an existing option (case-sensitive) | Read the database schema first; use the exact option name; status options cannot be created via the API in some plan tiers |
| Linked database view loses its filter after edit | The view was edited in a destination page rather than at the source | Edit views at the database's source location; saved views from the source propagate everywhere |
| Page becomes very slow to load | Too many embedded videos, too many rollup calculations, or a deeply nested toggle structure | Move heavy content to a child page; replace rollups with formula caches where possible; flatten toggles |
| Workspace search returns irrelevant results | Pages share generic titles ("Notes"), or are missing tags | Use descriptive titles with a prefix (PRD:, DEC:, OKR:); add multi_select tags |
| Bulk import of Markdown loses callouts and toggles | Notion's Markdown import does not preserve all custom block types | Use the API to create blocks programmatically (block-by-block) for high-fidelity migration |

## Success Criteria

- Every PM artifact (PRD, OKR, Decision, Roadmap item) lives in a database, not as an ad-hoc page
- 90%+ of database rows have an Owner and a Last Reviewed date within the past 6 months
- The Teamspace home page is the single launching point for the team's daily work
- New team members can find an active PRD in under 3 clicks from the home page
- API integrations (Linear sync, Jira sync, GitHub webhooks) run nightly with zero manual reconciliation
- No more than 5% of database rows reference deleted or archived counterparts (relation hygiene)
- Quarterly OKR check-ins are recorded in the OKR database with updated Confidence and Progress
- Decision log captures 100% of architecture-level decisions across the team
