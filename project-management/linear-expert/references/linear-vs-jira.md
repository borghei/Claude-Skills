# Linear vs Jira: Translation Guide for Migrating Teams

This guide is for teams moving an existing Jira instance to Linear. It maps Jira concepts to Linear concepts, calls out where the mapping is lossy, and recommends a migration sequence.

---

## Concept Map

| Jira | Linear | Notes |
|---|---|---|
| Site / Cloud Instance | Workspace (Organization) | One Linear workspace usually maps to one Jira site |
| Project | **Team** (most often) | A Jira Project's permission boundary and issue prefix are closest to Linear's Team |
| Project (when it's really a feature) | **Project** (Linear) | If a Jira project is one feature, map it to a Linear Project under an existing Team |
| Issue Type (Story, Bug, Task) | **Label** in a `type/*` group | Linear has no issue types; convention is `type/feature`, `type/bug`, `type/chore`, `type/spike` |
| Epic | **Project** | Linear Projects are the right "container of related issues with a target date" |
| Initiative (Premium/Enterprise Plans, formerly Advanced Roadmaps) | **Initiative** | Direct map |
| Sprint | **Cycle** | Direct map; cycles are per-team in Linear |
| Subtask | **Sub-issue** | Direct map |
| Component | **Label** in an `area/*` group | E.g. `area/api`, `area/web` |
| Fix Version / Release | **Project Milestone** or **Project target date** | Lossy: Jira releases span multiple projects; Linear milestones live inside one project |
| Custom Field (single-select) | **Label** in a custom label group | Use a label group per single-select field |
| Custom Field (free text) | Description text or a comment | No first-class home; structure as `Key: value` lines in description |
| Custom Field (number) | Description text | No first-class home; consider rounding into priority/estimate |
| Workflow (custom states) | **Workflow State** (constrained to 5 types) | Lossy: Jira workflows with 10+ states collapse to Linear's 5 type buckets (backlog/unstarted/started/completed/canceled) |
| Workflow Transition rules | Automations + GraphQL | Most rules become Linear automations or external webhook handlers |
| Resolution | Workflow state in `completed` or `canceled` type | Linear conveys resolution through the state's type |
| Priority (Highest/High/Medium/Low/Lowest) | Priority (Urgent/High/Medium/Low/No priority) | Map Highest+High → Urgent or High; Lowest → No priority or Low |
| Story Points | **Estimate** | Pick the team's estimation scale to match: Fibonacci (1, 2, 3, 5, 8) is closest |
| Labels | **Label** (no group) | Direct map |
| Watchers | **Subscribers** | Direct map |
| Comment | Comment | Direct map; Markdown is preserved by the importer |
| Attachment | Attachment | Direct map; importer downloads from Jira and re-uploads |
| Issue Link (blocks/is blocked by) | **Issue Relation** (blocks/blocked by/related to/duplicate of) | Direct map for the standard link types |
| Filter (JQL saved filter) | **View** (saved filter) | JQL → Linear's filter UI; the syntax differs |
| Dashboard / Gadget | **Views** + Insights | Linear has no gadget concept; Insights covers velocity, throughput, scope; custom dashboards live in Notion or BI tools |
| Permission Scheme | Team membership + workspace role | Linear has 3 workspace roles (Admin, Member, Guest) and team membership; no per-issue permissions |
| Service Desk / Jira Service Management | Not in Linear; use Triage + external helpdesk | Linear is not a helpdesk; integrate with Front, Intercom, Plain |
| Confluence link | Notion page link or attachment | If migrating docs too, see `notion-pm/` |

---

## Workflow State Mapping

Jira workflows are highly variable. Linear constrains every state to one of 5 types. Default mapping:

| Jira state (typical) | Linear type | Linear state name (typical) |
|---|---|---|
| Backlog, Open | `backlog` | Backlog |
| To Do, Selected for Development, Ready | `unstarted` | Todo |
| In Progress, In Development | `started` | In Progress |
| In Code Review, In QA, In Staging | `started` | In Review |
| Done, Closed, Resolved | `completed` | Done |
| Won't Do, Rejected, Duplicate | `canceled` | Canceled |
| Triage, Needs Triage | `triage` | Triage (enable on team) |

When a Jira project has unusual states like "Awaiting Customer Response," create a label (`status/awaiting-customer`) and keep the issue in `started`.

---

## Filter / JQL Translation Examples

| JQL | Linear filter equivalent |
|---|---|
| `project = ENG AND status = "In Progress"` | Team filter = ENG + State type = Started |
| `assignee = currentUser() AND sprint in openSprints()` | Assigned to me + Cycle = Current cycle |
| `priority in (Highest, High) AND status != Done` | Priority in (Urgent, High) + State type not in (Completed, Canceled) |
| `labels = "tech-debt"` | Label = tech-debt |
| `updated < -30d AND status != Done` | Updated date < 30 days ago + State type not in (Completed, Canceled) |
| `"Epic Link" = ENG-100` | Project = <linked Linear Project for that Jira Epic> |
| `type = Bug AND created >= -7d` | Label = type/bug + Created date < 7 days ago |

---

## Migration Plan (Recommended Sequence)

### Phase 0 — Inventory (1-2 days)
- Count: projects, issues per project, custom fields, workflows, users.
- Identify integrations: Slack, GitHub, CI, BI exports, scripts hitting the Jira REST API.
- Decide cutover strategy: big bang (one weekend) or phased (one Jira project per week).

### Phase 1 — Pilot (1 week)
- Pick the smallest, most active Jira project.
- Create the destination Linear team; configure labels, states, cycles.
- Run Linear's first-party Jira importer in dry-run mode.
- Validate: identifiers, comments, attachments, status mappings, custom fields → labels.
- Tweak the team configuration based on what broke.

### Phase 2 — Communication and Training (1 week, in parallel)
- Announce timeline to all users.
- Run 2-3 live demos showing the daily workflow in Linear.
- Publish a cheat sheet: keyboard shortcuts, magic words, triage SOP.
- Set the Jira instance to read-only on the cutover date.

### Phase 3 — Cutover (1 weekend per batch)
- Freeze writes on the source Jira projects.
- Run the importer for real.
- Spot-check 5% of issues for fidelity.
- Switch integrations: GitHub app, Slack, CI, scripts.
- Set up a 301-redirect or maintenance page on the Jira URL.

### Phase 4 — Decommission (after 30 days)
- Confirm no team is still writing to Jira.
- Export Jira as XML/JSON for compliance archive.
- Cancel the Jira subscription.

---

## What You Lose Going Jira → Linear

- **Per-issue permissions and security levels.** Linear permissions are at the team level.
- **Highly customized workflows.** Linear's 5 state types are a hard ceiling.
- **Custom field rigor.** Labels and structured description sections are the only extension points.
- **Service desk / SLA features.** Linear is not a helpdesk; pair with Front/Intercom/Plain for support workflows.
- **JQL.** Linear's filter UI is more visual but less expressive; very complex JQL becomes multiple saved views.
- **Time tracking.** Linear has no native time tracking; use an integration (Toggl, Harvest) if required.
- **Gadgets and pixel-perfect dashboards.** Use Linear Insights for velocity/throughput; push exported data to Notion or a BI tool for executive dashboards.

## What You Gain Going Jira → Linear

- A keyboard-first UI most engineers will adopt voluntarily.
- A GraphQL API that is consistent, documented, and pleasant to script against.
- GitHub integration that actually closes issues on merge without configuration ceremony.
- An opinionated Cycle / Project / Initiative hierarchy that resists the sprawl Jira invites.
- Triage as a first-class concept, not a workaround.
- Performance: Linear is fast even on workspaces with hundreds of thousands of issues.

---

## Common Pitfalls

1. **Mapping every Jira project to a Linear team.** Often the right move is many small Jira "feature projects" → one Linear team with multiple Linear Projects.
2. **Recreating Jira's 12-state workflow.** Resist; collapse to 5-6 states and use labels for nuance.
3. **Preserving every custom field.** Most are read by nobody; audit before mapping.
4. **Doing a big-bang migration on a large instance.** Phase by team or business unit; pilot first.
5. **Forgetting BI exports and ETL pipelines.** They will break the moment Jira goes read-only.
6. **Not training on keyboard shortcuts.** Linear's velocity advantage evaporates if users navigate by mouse.
