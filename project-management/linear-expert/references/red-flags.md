# Red Flags: Linear Expert

> Common ways this skill's output goes wrong -- concrete examples, why they're bad, and how to fix them.

## How to use this document

Scan every Linear configuration, GraphQL query, automation, or migration artifact before applying to a team. Each red flag has bad and good quoted examples.

---

## Red Flag 1: Cycle-as-Sprint Misuse

**Symptom.** Team treats Linear cycles as 2-week scrum sprints: cycle planning meeting, cycle goal, cycle review, velocity tracking.
**Why it's bad.** Linear cycles are designed for continuous flow, not commit-and-deliver ceremonies. Cycles auto-roll, do not enforce commitments, and have soft boundaries. Forcing scrum semantics on top creates friction -- the team works around Linear's defaults instead of leveraging them.
**Bad example:**
> "Cycle 23 (Apr 1 - Apr 14): team committed to 18 issues; carried 9 over to Cycle 24; treated this as a failed sprint and started over."
**Good example:**
> "Cycles 23 + 24 used as flow windows: team aims for ~12 issues per cycle but does not 'commit' in the scrum sense. Carry-over is expected and tracked as a flow metric (cycle-time, throughput) rather than as a failure mode. Sprint-style ceremonies (commit + review) replaced by continuous review per Linear's design."
**How to catch it.** Team is doing 'cycle planning' meetings with explicit commitments and carrying over = either re-adopt Linear's flow defaults or switch to Jira for scrum semantics.

---

## Red Flag 2: Project Bloat

**Symptom.** 200+ active Linear Projects, half with 1-3 issues; new initiatives spawn a Project by default.
**Why it's bad.** Projects are heavy-weight in Linear -- they have their own update cadence, members, lead, and visibility. Bloat dilutes the signal; nobody knows which Projects are truly active, and the org-wide Projects view becomes useless.
**Bad example:**
> "Active Projects: 247. Of those, 132 have < 5 issues, 78 have not been updated in 90 days. Project list is 14 screens long."
**Good example:**
> "Project hygiene: Projects are reserved for *initiatives that need a status update + a sponsor + a target date*. Smaller themed work uses Labels + Cycles instead. Quarterly review archives stale Projects. Today: 38 active Projects, all with a documented update cadence."
**How to catch it.** Project count > 50 = audit. Any Project with no Update in 30 days = candidate for archive.

---

## Red Flag 3: GraphQL N+1

**Symptom.** Script fetches 200 issues, then for each issue makes a separate query for its assignee and labels.
**Why it's bad.** Linear's GraphQL API supports nested selection; making N+1 queries hits rate limits fast (as of September 2026 Linear allows 2,500 requests/hour per user for API keys and 5,000 for OAuth apps, plus an hourly complexity budget), is 100x slower, and is the most common anti-pattern in Linear integrations.
**Bad example:**
> "for issue in issues:
>   assignee = client.query('{ user(id: ...) { name } }')
>   labels = client.query('{ issueLabels(filter: { issueId: ... }) { ... } }')"
**Good example:**
> "Single query with nested selection:
> ```graphql
> query {
>   issues(first: 200, filter: { ... }) {
>     nodes {
>       id identifier title state { name }
>       assignee { id name email }
>       labels { nodes { id name color } }
>     }
>   }
> }
> ```"
**How to catch it.** Any script that loops over issues making per-issue queries = rewrite with nested selection. Watch for `RATELIMITED` errors (returned with HTTP 400) in logs.

---

## Red Flag 4: Initiatives Used as Folders

**Symptom.** Linear Initiatives are created to group Projects by team or department, not by strategic outcome.
**Why it's bad.** Initiatives in Linear are designed for cross-team strategic bets. Misusing them as folders breaks Linear's outcome-tracking features and clutters the strategic view.
**Bad example:**
> "Initiative 'Engineering Q2 Work' contains 47 Projects. (It is a folder, not a strategy.)"
**Good example:**
> "Initiatives align with strategic outcomes (e.g. 'Activation: time-to-second-action < 3 min by Q4'). Each Initiative contains 3-8 Projects, each contributing to the outcome. Organizational grouping uses Teams + Labels, not Initiatives."
**How to catch it.** Initiative name contains a team / department / quarter / 'work' / 'engineering' = reclassify.

---

## Red Flag 5: Workflow States Modified Per-Team Without Org Alignment

**Symptom.** Team A's workflow: Backlog -> Triage -> Todo -> In Progress -> In Review -> Done. Team B added 4 custom states.
**Why it's bad.** Custom states break Linear's cross-team views (no shared mapping), confuse engineers who work across teams, and inflate the org-wide complexity. Linear's defaults are battle-tested; custom states should be rare and justified.
**Bad example:**
> "Team B added: 'Spec Review', 'Awaiting Design', 'In QA', 'Blocked External'. None match Team A's; cross-team reports broken."
**Good example:**
> "Org-wide default workflow used by all teams. Any custom state requires a documented exception in `linear-conventions.md` and an explicit mapping back to org-wide types (started / completed / canceled)."
**How to catch it.** Count distinct workflow states across all teams. > 8 in any team = audit; > 12 across the org = consolidate.

---

## Red Flag 6: Sub-Issue Hierarchy Inversion

**Symptom.** Issues with 15 sub-issues, sub-issues that are larger than the parent, deeply nested sub-issue trees (4+ levels).
**Why it's bad.** Linear's sub-issue model is intended for shallow within-task decomposition, not as a substitute for the Project layer. Deep nesting breaks burn-down, makes the issue view a tree of clutter, and slows the UI noticeably.
**Bad example:**
> "Issue 'Build Bulk Edit' has 4 sub-issues, each with 6-8 sub-sub-issues, totaling 31 nested issues."
**Good example:**
> "Issue 'Build Bulk Edit' is a Project (not an issue) -- because it spans > 2 weeks and crosses multiple components. The Project contains 6-8 top-level issues, each with 0-3 sub-issues for within-sprint tasks only. Max depth: 2."
**How to catch it.** Any issue with > 5 sub-issues or > 2 levels of nesting = re-model as a Project.

---

## Red Flag 7: Triage Inbox Untriaged

**Symptom.** Linear's Triage queue has 380 issues, going back 6 months.
**Why it's bad.** Triage is the gate between intake and the team's commitment. An overflowing Triage means new bugs / feature requests are not being acknowledged, customers wait, and the team loses visibility into what is incoming.
**Bad example:**
> "Triage queue: 380 issues, oldest 184 days. Nobody owns Triage."
**Good example:**
> "Triage SLA: each issue routed to a team within 2 business days. Rotating Triage owner per team (1-week rotation). Weekly Triage cleanup ritual: any issue > 14 days in Triage is either accepted, declined with reason, or escalated."
**How to catch it.** Triage queue > 30 issues or oldest > 14 days = staff Triage.

---

## Red Flag 8: API Webhooks With No Signature Verification

**Symptom.** Linear webhook posts to an internal service; service trusts the payload and acts on it.
**Why it's bad.** Without signature verification, attackers can replay or forge webhook events, triggering automation (deletions, status changes, notifications). This is a real security risk, not theoretical.
**Bad example:**
> "@app.route('/linear-webhook', methods=['POST'])
> def handle():
>     data = request.json
>     do_thing(data)  # no verification"
**Good example:**
> "Every webhook handler verifies the `Linear-Signature` header against the configured webhook secret using constant-time HMAC comparison. Failed verifications return 401 and log to the security channel. Documented in `references/webhook-security.md`."
**How to catch it.** Any webhook handler that does not validate `Linear-Signature` = security review now.

---

## Red Flag 9: Jira -> Linear Migration Without Workflow Mapping

**Symptom.** Bulk import 8000 Jira issues into Linear; statuses default to 'Backlog'.
**Why it's bad.** A statuses-collapsed migration loses the team's most valuable signal (which work is in flight, which is blocked, which is done). The team has to manually re-classify thousands of issues or the new Linear instance is unusable.
**Bad example:**
> "Bulk migrate: all 8000 Jira issues created in Linear; all set to Backlog. Sprint history dropped."
**Good example:**
> "Migration plan with explicit mappings:
> - Jira `In Progress`, `In Review`, `In QA` -> Linear `In Progress` (with a label preserving the precise Jira state)
> - Jira `Done` -> Linear `Done`
> - Closed-resolved Jira issues map to canceled state
> Sprint history is preserved in a custom field `legacy_sprint`. Migration script in `references/jira-to-linear-migration.md`."
**How to catch it.** Any migration plan that does not have a status-mapping table = stop and write one.

---

## Red Flag 10: Cycle Goals That Are Output Lists

**Symptom.** Cycle goal: "Ship features A, B, C." (Not an outcome.)
**Why it's bad.** A cycle goal that lists outputs collapses to a status checklist, not a coordination signal. The team ships and feels successful even if nothing improved. Linear's update cadence is built on outcomes, not output lists.
**Bad example:**
> "Cycle 23 goal: 'Ship bulk-edit, dark mode, and SCIM v1.'"
**Good example:**
> "Cycle 23 goal: 'Enterprise admins spend < 2 min on candidate edits' (measured via the candidate-edit-event log). Bets in flight this cycle: bulk-edit (primary), in-product templates (secondary). Reviewing the goal at cycle close means looking at the metric, not the ship-list."
**How to catch it.** Cycle goal is a list of features = rewrite as an outcome with bets underneath.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | Cycle-as-sprint | Team commits + carries over? Wrong tool. |
| 2 | Project bloat | > 50 active Projects = audit |
| 3 | GraphQL N+1 | Loops doing per-issue queries = nested selection |
| 4 | Initiatives as folders | Initiative named after a team / department |
| 5 | Custom workflow states | > 8 states per team = consolidate |
| 6 | Sub-issue hierarchy inversion | > 5 sub-issues or > 2 levels = use a Project |
| 7 | Triage untriaged | Queue > 30 or oldest > 14 days = staff |
| 8 | Webhooks unsigned | All handlers verify HMAC |
| 9 | Migration without mapping | Explicit status-mapping table |
| 10 | Output-list cycle goals | Cycle goal is an outcome, not a ship-list |

## Related Reading

- `SKILL.md` -- Linear admin + GraphQL patterns
- `references/linear-graphql-patterns.md` -- canonical queries
- `references/jira-to-linear-migration.md` -- migration playbook
- `references/webhook-security.md` -- signature verification
- Sibling skill: `jira-expert/` -- Jira's equivalent patterns
- Sibling skill: `scrum-master/` -- ceremony patterns that fit Linear cycles
- Sibling skill: `execution/cycle-time-analyzer/` -- flow metrics that Linear emphasizes

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---|---|---|
| Issue did not auto-close on PR merge | PR description used wrong magic word, repo not connected to the team, or PR was merged via squash without the magic word in the commit message | Verify the GitHub integration is enabled for the team; ensure the magic word (`Fixes`, `Closes`, `Resolves`) appears in PR title or description; if squash-merging, include the magic word in the commit message |
| GraphQL query returns null for a field that should exist | Field is gated behind a permission your API key lacks, or the field is on a different type (e.g. `Issue.project` vs `Issue.projectMilestone`) | Re-check the schema via Linear's GraphQL Playground; ensure the API key belongs to a workspace member with access to the relevant team |
| Triage rules not firing for inbound items | Team does not have triage enabled, or the source integration is configured to write directly to a workflow state | Enable triage in team settings; reconfigure the source (e.g. Slack-to-Linear) to create issues without a state so they land in triage |
| Bulk update script gets `RATELIMITED` errors | Exceeded the request or complexity budget for its auth type (API key: 2,500 req/hr and 3M points/hr per user; OAuth app: 5,000 req/hr and 2M points/hr; as of September 2026) | Add exponential backoff until the `X-RateLimit-*-Reset` time; use `issueBatchUpdate` instead of per-issue calls; trim nested selections to cut complexity; spread work over time or move the integration to an OAuth app |
| Cycle issues show the wrong velocity | Issues without estimates are excluded from velocity; canceled work is excluded; scope changes during cycle distort the chart | Require estimates at planning time; review the cycle's scope history in Insights to spot mid-cycle additions |
| Custom field values from Jira are missing after import | Linear has no custom fields; the Jira importer maps them to labels or appends to description, which can lose semantics | Pre-map critical Jira custom fields to label groups before import; for fields that cannot be expressed as labels, append structured key:value lines to the description |
| Webhook deliveries are missing or duplicated | Receiver is too slow (>10s response), or the webhook secret is rotated and signatures fail validation | Respond with 2xx within 5 seconds; queue work asynchronously; verify the signature on every payload using the current secret |
