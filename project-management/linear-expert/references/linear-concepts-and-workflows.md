# Linear Concepts & Workflows

> Read this when you need the Linear data model, the seven core operating workflows (setup, cycle/project planning, initiatives, triage, GitHub, bulk ops, Jira migration), best practices, or the success criteria for a healthy Linear workspace.

## Concepts

### Data Model

| Entity | Purpose | Key Fields |
|---|---|---|
| **Workspace** (Organization) | Top-level account, billing scope | `urlKey`, `name`, `samlEnabled` |
| **Team** | Permissions boundary, workflow owner, issue identifier prefix (e.g. `ENG`, `DESIGN`) | `key`, `cyclesEnabled`, `triageEnabled`, `defaultIssueState` |
| **Cycle** | Time-boxed iteration owned by one team (Linear's "sprint") | `number`, `startsAt`, `endsAt`, `progress`, `scopeHistory` |
| **Project** | Cross-functional body of work with a target date; spans one or more teams | `state` (planned/started/paused/completed/canceled), `targetDate`, `lead`, `teamIds` |
| **Initiative** | Strategic theme that groups Projects under a top-line outcome | `status`, `targetDate`, `owner`, `projects` |
| **Roadmap** | Saved view of Projects/Initiatives ordered by time | (UI construct, queried as filtered Project list) |
| **Issue** | The atomic unit of work | `identifier` (e.g. `ENG-123`), `state`, `priority`, `estimate`, `cycle`, `project`, `parent` |
| **Sub-issue** | Issue with `parent` set, rolls progress up | inherits team from parent |
| **Label** | Free-form tag; can be grouped into mutually-exclusive label groups | `color`, `parent` (for groups) |
| **Milestone** | Project-scoped checkpoint with a target date | `name`, `targetDate`, `sortOrder` |
| **Workflow State** | Per-team status; lives in one of 5 types | `type` (backlog/unstarted/started/completed/canceled/triage) |
| **Triage** | Special inbox state for unassigned/unscored incoming issues | enabled per-team via `triageEnabled` |

### Issue Identifier & Linear-Flavored Markdown

- Issues are referenced as `TEAMKEY-NUMBER` (e.g. `ENG-123`, `DSGN-47`). The number is workspace-unique within the team. Pasting an identifier in any Linear text field auto-resolves to a link with the issue title.
- **Mentions**: `@username` resolves against workspace members. `@team-name` mentions an entire team.
- **Priorities** map to numeric values: `0` No priority, `1` Urgent, `2` High, `3` Medium, `4` Low. Most UIs and the API accept the numeric value.
- **Markdown extensions**: standard CommonMark plus issue refs, mentions, task lists (`- [ ]`), and inline emoji shortcodes (`:rocket:`).
- **Code blocks** support fenced language tags; Linear renders syntax highlighting for ~30 languages.

## Core Workflows

### 1. Workspace and Team Setup

1. Create workspace; set URL key (immutable, used in all issue URLs).
2. Configure SSO/SAML if available on the plan tier.
3. Create the first Team with a meaningful 2-4 letter key (it appears in every issue ID forever).
4. Decide per-team:
   - **Cycles enabled?** Yes for shipping teams, no for triage-only/support teams.
   - **Cycle cadence**: typically 1-2 weeks, set the day-of-week start.
   - **Triage enabled?** Yes if external sources (Slack, support, GitHub Issues) create issues that need human routing.
   - **Estimation scale**: Exponential (0, 1, 2, 4, 8), Fibonacci, Linear (1-5), or T-shirt.
5. Customize workflow states (within the 5 allowed types). Common pattern: `Backlog → Todo → In Progress → In Review → Done → Canceled`.
6. Define core labels and label groups (e.g. group `area/*` with values `area/api`, `area/web`, `area/infra`).
7. **HANDOFF TO**: team leads for issue templates, automations, and GitHub install.

### 2. Cycle and Project Planning

**Cycle planning checklist** (run 1-2 days before cycle start):
1. Review the Cycle view: any issues without estimates, owners, or projects?
2. Pull issues from Backlog into Todo for the upcoming cycle.
3. Confirm cycle scope against the team's recent velocity (Linear shows median cycle velocity in Insights).
4. Set the cycle's auto-archive cadence (default: 6 completed cycles).

**Project planning**:
1. Create Project; assign Lead, target date, and member teams.
2. Add Milestones inside the project; order them.
3. Pull or create issues, assigning each to a milestone where useful.
4. Set Project status updates cadence (weekly is the default expectation).

### 3. Initiative and Roadmap Management

Initiatives are the top of Linear's hierarchy (Initiative → Project → Milestone → Issue).
1. Create an Initiative per strategic theme (e.g. "Self-Serve Onboarding Q3").
2. Attach 3-7 Projects per Initiative; more than 10 signals the Initiative is too broad.
3. Use the Roadmap view to visualize Initiatives and Projects on a quarterly timeline.
4. Owner posts an Initiative update at minimum monthly; the update appears in the Initiative feed and in any subscribed Slack channel.

### 4. Triage Workflow

Triage is Linear's inbox for issues that arrive without a workflow state. It's the right destination for Slack-created issues, customer support escalations, and inbound GitHub Issues.
1. Enable Triage on the receiving team.
2. Configure intake sources: GitHub Issues mirroring, Slack-to-Linear, customer request form, or API.
3. Establish a daily triage cadence (one person, ~15 minutes). For each triage item:
   - Confirm or reassign team.
   - Assign priority (Urgent/High/Medium/Low).
   - Assign owner or leave in `Todo` for cycle planning.
   - Attach project/milestone if it belongs to existing work.
   - Apply labels (`area/*`, `type/bug|feature|chore`).
4. **HANDOFF TO**: cycle planning for any items not closed during triage.

### 5. GitHub Integration

Linear's GitHub integration is bidirectional and the highest-leverage automation in the product.
1. Install the Linear GitHub app on the org; grant access to the relevant repos.
2. **Magic words in PR titles or descriptions** auto-link and auto-close:
   - `Fixes ENG-123`, `Closes ENG-123`, `Resolves ENG-123` move the issue to Done on PR merge.
   - `Part of ENG-123` or just `ENG-123` link without auto-close.
3. **Branch name auto-linking**: branches matching `<username>/eng-123-short-description` are auto-detected.
4. PR status changes update the issue state (Linear → In Review when PR opens; → Done when merged).
5. Configure per-team "GitHub repos" so only the relevant repos appear in the issue sidebar.

### 6. Bulk Operations

Bulk edits go through the API for anything beyond ~50 issues. Strategy:
1. Build a GraphQL query to fetch the issue IDs matching the criteria.
2. Loop in batches of 50; call `issueUpdate` mutation for each.
3. Rate limit (as of September 2026, per [Linear's rate-limiting docs](https://linear.app/developers/rate-limiting)): API keys get 2,500 requests / hour and 3,000,000 complexity points / hour per user; OAuth apps get 5,000 requests / hour and 2,000,000 complexity points / hour per user or app user; a single query may not exceed 10,000 complexity points. Limits are set by auth type, not by plan.
4. Always include an `--dry-run` mode in scripts; print the full list of issues that will change before mutating.
5. Use `issueBatchUpdate` mutation (where available) to update up to 100 issues per call.

### 7. Migration from Jira

Linear ships a first-party Jira importer that covers ~80% of cases. For the remaining 20%, plan a custom GraphQL-backed migration.
1. **Inventory Jira**: project count, custom fields, workflows, user count, issue count, attachment volume.
2. **Map concepts**:
   - Jira Project → Linear Team (often) or Linear Project (sometimes)
   - Jira Epic → Linear Project
   - Jira Initiative → Linear Initiative
   - Jira Sprint → Linear Cycle
   - Jira Subtask → Linear Sub-issue
   - Jira Components → Linear Labels (often in an `area/*` group)
3. **Decide on history**: Linear's importer preserves comments, attachments, status history, and assignees, but not custom field values verbatim (they map to labels or description text).
4. **Pilot with one Jira project** before mass migration. Validate identifiers, link integrity, and attachment downloads.
5. **Cut over**: freeze Jira writes, run final import, redirect all integrations (Slack, GitHub, CI) to Linear, archive Jira.
6. **HANDOFF TO**: `jira-expert/` for the Jira freeze and decommission plan.

## Best Practices

**Data quality**
- Enforce labels via team conventions (e.g. every issue must carry one `area/*` and one `type/*` label).
- Estimate every issue before it enters a cycle. Cycle velocity is meaningless if half the issues have null estimates.
- Use sub-issues for genuine parent-child decomposition; do not use them as a substitute for projects.

**Workflow discipline**
- Resist the urge to add a 7th or 8th workflow state. Linear's strength is the constrained model. If a team feels squeezed, the right move is usually a label, not a new state.
- Use the `Triage` state aggressively for any source that creates issues automatically; do not let bots write directly into `Todo`.

**Cycles and projects**
- Cycle scope set at planning time should drift no more than ~20% during the cycle; bigger drift is a signal of unclear acceptance criteria upstream.
- Projects without a target date are red flags; every project should have one even if approximate.

**API hygiene**
- Cache the team and label UUIDs your scripts use; never look them up by name on every call.
- Use webhooks instead of polling. Linear's webhook system covers nearly every entity.
- Respect rate limits; a rate-limited request returns HTTP 400 with a `RATELIMITED` error code in `errors[].extensions`. Back off until the time in `X-RateLimit-Requests-Reset` / `X-RateLimit-Complexity-Reset`.

**Governance**
- Restrict who can create teams (admins only on larger workspaces).
- Audit Initiatives quarterly; merge or close stale ones.
- Document the workspace's label taxonomy in a pinned issue or Notion page.

## Success Criteria

- All active teams have triage enabled (where applicable), a defined cycle cadence, and a standard label taxonomy
- 95%+ of issues entering a cycle carry an estimate, an owner, and a state-appropriate label
- Cycle velocity variance stays within 25% of the trailing 6-cycle median
- Every active Project has a Lead, a target date, and a status update within the last 14 days
- Initiatives have a clear owner and a monthly update; no Initiative carries more than 10 Projects
- GitHub PRs auto-close their linked Linear issues in 95%+ of merges
- API/automation scripts respect rate limits; no script triggers more than 5 `RATELIMITED` responses per day
- Jira-to-Linear migrations cut over with zero loss of comment history and 100% of identifiers redirected
