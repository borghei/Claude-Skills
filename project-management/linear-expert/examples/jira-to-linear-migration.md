# Example: Jira -> Linear Migration Playbook for a Series B SaaS

> Real-world scenario showing how to apply this skill end-to-end.

## Context

Northwind SaaS (fintech, Series C, 200 people) is migrating off Jira to Linear. The engineering org has been on Jira for six years; the product org has been quietly using Linear in pockets for two. The CTO (Hari) decided to unify on Linear after the Jira annual renewal landed at $94K and the team's productivity surveys showed Jira friction was a top-three complaint.

Migration scope: 12 Jira projects, 18,400 open + closed issues, 35 custom fields, 28 workflows, three years of historical sprint data. The PM running the migration (Ana) has six weeks. The constraint: no work stoppage, no lost history, and clean Linear hygiene at the end.

## Inputs

- 12 Jira projects, 5 of which are active (the other 7 are archived)
- 18,400 issues total (active projects: 6,200; archived: 12,200)
- 35 custom fields (most unused; will normalize during migration)
- 200 users; 22 admins
- Linear plan: Business ($16/user/month)
- Cutover: 2026-09-01 (six weeks out)

## Applying the skill

1. **Map Jira -> Linear concepts first.** Workflows are different shapes; force the mapping before exporting any data.
2. **Audit Jira state.** Half the fields and half the issues will not migrate. Decide what.
3. **Build Linear team structure** to match the future engineering org (not the past).
4. **Export with the Atlassian REST API.** Transform. Bulk-create in Linear via GraphQL.
5. **Run shadow week.** Both systems live; nightly diff. Cutover when diff is clean.
6. **Decommission Jira read-only.** Keep for audit; revoke writes.

## The artifact

### Phase 0: Concept mapping

| Jira concept | Linear equivalent | Notes |
|--------------|-------------------|-------|
| Project | Team | One-to-one for active projects; archived become Linear archives |
| Epic | Project (Linear) | Linear's "Project" = Jira's "Epic" |
| Story / Task / Bug | Issue | Use Linear labels for type (not separate object) |
| Sprint | Cycle | Linear cycles are 2-week by default |
| Sub-task | Sub-issue | Same concept; cleaner UI in Linear |
| Component | Label (or Sub-team) | Most components -> labels |
| Fix Version | Project (Linear) milestone | Linear "Milestone" inside Project |
| Custom field | Issue properties or labels | Most won't survive; see below |
| Workflow status | Workflow status | Linear has fewer states; collapse on the way over |

### Phase 1: Jira audit (week 1)

```python
# Audit script (excerpt) — uses Jira REST API
import requests

JIRA_BASE = "https://northwind.atlassian.net"
auth = (USERNAME, API_TOKEN)

# Count issues across the spaces being migrated.
# The enhanced search (/rest/api/3/search/jql) returns no `total`, so use the
# approximate-count endpoint for sizing (as of September 2026).
jql = "project in (TREAS, ACT, COMP, INF, SEARCH)"
res = requests.post(f"{JIRA_BASE}/rest/api/3/search/approximate-count",
                    auth=auth, json={"jql": jql})
print(res.json()["count"])  # ~6,200 (estimate)
```

> The legacy `/rest/api/3/search` and `/rest/api/2/search` endpoints are deprecated and being removed (Atlassian changelog CHANGE-2046). Use `GET`/`POST /rest/api/3/search/jql`: cursor pagination via `nextPageToken`, no `startAt`/`total`, and `fields` defaults to `id` only, so request the fields you need explicitly. See the [Issue search API reference](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/).

**Audit findings (full table at decision-time):**

| Project | Active issues | Closed issues | Will migrate? |
|---------|--------------|---------------|---------------|
| TREAS (Treasury) | 540 | 4,200 | Yes -- both |
| ACT (Activation) | 320 | 1,100 | Yes -- both |
| COMP (Compliance) | 180 | 600 | Yes -- both |
| INF (Infrastructure) | 420 | 1,800 | Yes -- both |
| SEARCH | 280 | 760 | Yes -- both |
| Legacy: ADMIN, OPS, etc. | 0 | 9,000 | No -- export to S3 archive only |

**Custom-field decisions:** 22 of 35 fields are dropped (none of: "Original ETA from 2022," etc.). Kept and mapped: Story Points, Customer Impact, RICE Score, Sprint, Fix Version, Linked PR, Acceptance Criteria, OKR Link, Risk Score, Post-Mortem Doc, Definition of Ready, Reporter Squad. The 12 we keep map to Linear issue properties + labels.

### Phase 2: Linear team structure (week 1-2)

Five teams (one per active project), each with its own cycle cadence:

```graphql
mutation CreateTeams {
  treasury: teamCreate(input: {
    name: "Treasury", key: "TREAS", cycleEnabled: true,
    cycleDuration: 14, defaultIssueEstimate: 3
  }) { team { id key } }
  activation: teamCreate(input: {
    name: "Activation", key: "ACT", cycleEnabled: true, cycleDuration: 14
  }) { team { id key } }
  compliance: teamCreate(input: {
    name: "Compliance", key: "COMP", cycleEnabled: false
  }) { team { id key } }
  infra: teamCreate(input: {
    name: "Infrastructure", key: "INF", cycleEnabled: true, cycleDuration: 14
  }) { team { id key } }
  search: teamCreate(input: {
    name: "Search", key: "SEARCH", cycleEnabled: true, cycleDuration: 14
  }) { team { id key } }
}
```

Compliance is async work; cycles disabled. Treasury, Activation, Infrastructure, Search run 2-week cycles synchronized.

### Phase 3: Workflow status mapping (week 2)

| Jira status | Linear status (in workflow) | Type |
|-------------|----------------------------|------|
| Backlog | Backlog | unstarted |
| Ready | Todo | unstarted |
| In Progress | In Progress | started |
| In Review | In Review | started |
| Verified | In Verification | started |
| Done | Done | completed |
| Won't Do | Cancelled | cancelled |

Collapsed from 7 to 6 states; "Won't Do" maps to Linear's native Cancelled.

### Phase 4: Bulk issue creation (week 3)

#### Pattern: pull from Jira, push to Linear

```python
import requests, time

# 1) Pull batch from Jira (enhanced JQL search, token pagination)
FIELDS = "summary,description,status,priority,components,customfield_10010"

def pull_jira_batch(project_key, next_page_token=None, page=100):
    jql = f'project = "{project_key}" ORDER BY created ASC'
    params = {"jql": jql, "fields": FIELDS, "maxResults": page}
    if next_page_token:
        params["nextPageToken"] = next_page_token
    res = requests.get(f"{JIRA_BASE}/rest/api/3/search/jql", auth=auth, params=params)
    body = res.json()
    # nextPageToken is absent on the last page
    return body["issues"], body.get("nextPageToken")

# 2) Transform a Jira issue to a Linear issueCreate input
def transform(jira_issue, linear_team_id):
    fields = jira_issue["fields"]
    return {
        "teamId": linear_team_id,
        "title": fields["summary"],
        "description": render_adf_to_markdown(fields.get("description")),
        "stateId": MAP_STATUS[fields["status"]["name"]],
        "priority": MAP_PRIORITY.get(fields["priority"]["name"], 0),
        "estimate": fields.get("customfield_10010"),  # Story Points
        "labelIds": [LABEL_MAP[c["name"]] for c in fields.get("components") or []],
    }

# 3) Linear GraphQL mutation
LINEAR_URL = "https://api.linear.app/graphql"
LINEAR_HEADERS = {"Authorization": LINEAR_API_KEY, "Content-Type": "application/json"}

ISSUE_CREATE = """
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue { id identifier }
  }
}
"""

def push_to_linear(input_obj):
    res = requests.post(LINEAR_URL, headers=LINEAR_HEADERS, json={
        "query": ISSUE_CREATE, "variables": {"input": input_obj}
    })
    return res.json()

# 4) Loop with rate-limit handling
for project in ACTIVE_PROJECTS:
    token = None
    while True:
        batch, token = pull_jira_batch(project["jira_key"], token)
        for issue in batch:
            input_obj = transform(issue, project["linear_team_id"])
            result = push_to_linear(input_obj)
            log_migration_mapping(issue["key"], result["data"]["issueCreate"]["issue"]["identifier"])
            time.sleep(0.15)  # ~6 req/s, well below Linear's limit
        if not token:
            break
```

#### Mapping table preserved during migration

| Jira key | Linear identifier | Migrated at |
|----------|-------------------|-------------|
| TREAS-1042 | TREAS-302 | 2026-08-22 11:02 UTC |
| TREAS-1043 | TREAS-303 | 2026-08-22 11:02 UTC |
| ACT-892 | ACT-201 | 2026-08-22 11:14 UTC |

The mapping table goes into S3 + linked Notion so historical Jira links keep working via a redirect proxy.

### Phase 5: Sub-issues, comments, and history (week 4)

#### Sub-issue linking

```graphql
mutation LinkSubIssue($parentId: String!, $childId: String!) {
  issueUpdate(id: $childId, input: { parentId: $parentId }) {
    success
  }
}
```

Run after all issues are created (sub-issue links require both parent and child to exist).

#### Comment migration

```graphql
mutation CommentCreate($issueId: String!, $body: String!, $createdAt: DateTime!) {
  commentCreate(input: { issueId: $issueId, body: $body, createdAt: $createdAt }) {
    success
  }
}
```

(Note: Linear allows setting `createdAt` on imports via the API to preserve history dates.)

### Phase 6: Shadow week (week 5)

Both Jira and Linear are live. Engineers work in Linear; PMO writes to both via a sync script. Nightly diff job:

```python
# nightly_diff.py — runs at 02:00 UTC
def diff_active_issues():
    jira_active = pull_all_active(JIRA_BASE)
    linear_active = pull_all_active(LINEAR_URL)
    missing_in_linear = set(jira_active) - set(linear_active)
    missing_in_jira = set(linear_active) - set(jira_active)
    if missing_in_linear or missing_in_jira:
        post_slack_alert(missing_in_linear, missing_in_jira)
```

Five days of clean diffs (zero new mismatches) -> cutover green light.

### Phase 7: Cutover (Sep 1)

- 09:00 PT: Freeze Jira writes for engineering org.
- 09:30 PT: Final sync run.
- 10:00 PT: Linear becomes single source of truth.
- 10:00 PT onwards: Jira read-only for 90 days for audit/history. Then archived to S3.

### Phase 8: First two cycles in Linear

| Cycle | Team | What we watched | Result |
|-------|------|-----------------|--------|
| Cycle 1 (Sep 1-15) | All 5 teams | Velocity, # bugs filed, support tickets about "where did X go?" | Velocity drop ~12% (expected). 18 "where is X" tickets, all answered with the redirect proxy. |
| Cycle 2 (Sep 15-29) | All 5 teams | Velocity recovery, label adoption, project structure | Velocity at 96% of pre-migration baseline. Label usage clean. |

### Cost / time outcomes

| Metric | Before | After |
|--------|--------|-------|
| Annual cost | $94K Jira | $38K Linear |
| Avg issue create time | 47 sec | 14 sec |
| Engineering survey "tool friction" rank | #3 | not in top 10 |
| Active custom fields | 35 | 12 (mapped to labels/properties) |

## Why this works

- Concept mapping happens before any export. The team did not try to ship Jira workflows verbatim into Linear; they translated.
- Custom-field hygiene happens during migration. The team killed 22 unused fields rather than re-implementing them.
- Linear team structure reflects the *future* engineering org, not the historical Jira project layout. Compliance gets no cycles because that work is not cycle-shaped.
- Shadow week with a nightly diff job catches every drift before cutover.
- The mapping table (Jira-key -> Linear-identifier) is preserved permanently so old Slack links and Confluence references resolve.
- 90-day Jira read-only window protects audit history without keeping write paths around.

## What's next

- Run `../execution/status-update-generator/` against Linear to confirm format parity.
- Use `../sprint-retrospective/` to inspect Cycle 1 retros and find adoption friction.
- Mirror the Notion docs via `../notion-pm/` for cross-tool reference.
- Roll the migration retro into the company's quarterly review per `../execution/quarterly-planning/`.
- Archive Jira to S3 after 90 days; document the archive location in the Tech Decisions DB.
