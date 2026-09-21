# Red Flags: Notion PM

> Common ways this skill's output goes wrong -- concrete examples, why they're bad, and how to fix them.

## How to use this document

Scan every Notion database design, relation, or API integration before adopting it for PM workflows. Each red flag has bad and good quoted examples.

---

## Red Flag 1: Page Sprawl

**Symptom.** PM workspace has 2,400 top-level pages, no consistent hierarchy. New PMs create pages in their personal space; nobody can find anything.
**Why it's bad.** Page sprawl makes Notion functionally a graveyard. Search returns 20 versions of the same PRD. The "shared knowledge" promise of Notion is broken because there is no shared structure.
**Bad example:**
> "Top-level workspace: 2400 pages, no folder structure. PRD-2026-Q1, PRD-2026-Q1-v2, PRD-2026-Q1-final, PRD-2026-Q1-final-v2 all exist."
**Good example:**
> "Workspace hierarchy:
> - PRDs database (one entry per PRD; versions tracked as a property + history)
> - OKRs database
> - Roadmap database
> - Decisions database
> - Meeting notes database
> Pages outside databases require a documented exception. Personal pages live in `/personal`."
**How to catch it.** Workspace has > 100 top-level pages without database membership = enforce DB-driven structure.

---

## Red Flag 2: Missing Relations

**Symptom.** PRDs database, OKRs database, and Roadmap database all exist -- but no relations between them. Each PRD lists its OKR as plain text.
**Why it's bad.** Plain-text references break. A PRD references "Q2 OKR: Activation" but the OKR's wording shifted; the PRD is now misleading. Worse, you cannot generate "all PRDs supporting this OKR" -- a basic PM query.
**Bad example:**
> "PRD page property `OKR`: text = 'Q2 Activation OKR'. (No link.)"
**Good example:**
> "PRD database has a Relation property `OKR` -> OKRs database. Two-way relation: each OKR shows its supporting PRDs. Rollup: OKR shows count of in-progress vs done PRDs."
**How to catch it.** Any cross-database reference stored as text = convert to a Relation.

---

## Red Flag 3: Rollup-of-Rollup Performance Collapse

**Symptom.** OKR DB has a rollup of Project DB (which has a rollup of Task DB). Page load > 10 seconds.
**Why it's bad.** Notion rollups across multiple databases recompute on every page render. Deep rollup chains (3+ levels) make the page sluggish; teams stop using the dashboards because they hang.
**Bad example:**
> "OKRs DB rollup: 'completed task count' = rollup of Projects.rollup of Tasks.is-done. Page takes 12s to render."
**Good example:**
> "Rollups are 1-deep. For aggregations needing more depth, a scheduled script (running daily via cron) updates an explicit 'aggregate-stats' property using the Notion API. Page renders in < 1s."
**How to catch it.** Notion page > 3s render time + uses rollups = re-architect to flat aggregations or scripted updates.

---

## Red Flag 4: Inline Databases Everywhere

**Symptom.** Every PM has their own inline database in their meeting notes, all duplicating fields with slight variations.
**Why it's bad.** Inline databases are isolated copies. Search does not aggregate them. Reporting is impossible. Renaming a property in one does not propagate. It is the worst of both worlds: database overhead with none of the benefits.
**Bad example:**
> "Each PM's weekly meeting notes contain an inline 'Action Items' DB. The org cannot generate 'all action items assigned to <name> across teams'."
**Good example:**
> "Single workspace-wide 'Action Items' DB. PM meeting notes embed a *filtered view* of this DB (filter: 'meeting = this page'). All action items live in one place; cross-team queries work."
**How to catch it.** Count databases named the same thing (e.g. 'Action Items' x 14) = consolidate.

---

## Red Flag 5: Notion Used as a Wiki Without Owners

**Symptom.** Pages exist with no owner, no last-reviewed date, no expiry. Half are 18 months stale.
**Why it's bad.** Stale pages mislead. New joiners trust the page; the team has long since changed practice. Documentation drift is a real cost; the right antidote is page-level ownership + review cadence.
**Bad example:**
> "Onboarding page 'How to deploy to staging': last edited 2024-08. Says to use AWS CodeBuild; team migrated to GitHub Actions in 2025."
**Good example:**
> "Every long-lived page has: `Owner` property (user), `Last Reviewed` (date), `Review Cadence` (every N months), `Expires` (date). A weekly script lists pages overdue for review; owners review or archive."
**How to catch it.** Workspace has pages with no Last Reviewed property or with Last Reviewed > 1 year ago = run the review script.

---

## Red Flag 6: API Tokens in Pages

**Symptom.** A page titled 'Notion API credentials' contains `secret_xxxxxxxx`.
**Why it's bad.** Notion pages are not secret stores. Anyone with workspace access (often a wide group) can read the secret. Worse, Notion's audit log of page views is limited, so leaks may go undetected.
**Bad example:**
> "Page 'Engineering / Tools / Notion API' contains the workspace integration secret in plain text."
**Good example:**
> "Secrets live in a secrets manager (1Password, AWS Secrets Manager, Vault). The Notion page references *how to retrieve* the secret (with the right permissions) but never contains the secret itself."
**How to catch it.** Search Notion for strings starting with `secret_`, `sk_`, `xoxb-`, `ghp_`, `xoxp-` = remove and rotate.

---

## Red Flag 7: Notion API Pagination Ignored

**Symptom.** Script fetches database entries via `POST /v1/data_sources/{data_source_id}/query` (or the pre-`2025-09-03` `POST /v1/databases/{id}/query`); returns 100 results; treats it as 'all results'.
**Why it's bad.** Notion API paginates at 100 items by default. Without honoring `has_more` + `next_cursor`, scripts silently miss data. The org thinks it has 100 PRDs; in reality there are 340 -- and decisions get made on a 30% sample.
**Bad example:**
> "response = requests.post(url, json={...}).json()
> all_results = response['results']  # treats 100 as all"
**Good example:**
> "all_results = []
> next_cursor = None
> while True:
>     body = {'page_size': 100}
>     if next_cursor:
>         body['start_cursor'] = next_cursor
>     r = requests.post(url, json=body).json()
>     all_results.extend(r['results'])
>     if not r.get('has_more'):
>         break
>     next_cursor = r['next_cursor']"
**How to catch it.** Any Notion API call that does not loop on `has_more` = broken.

---

## Red Flag 8: Synced Blocks Used as a Sharing Mechanism

**Symptom.** A team uses Synced Blocks to share a "current OKR" across 14 team-pages; updating the OKR requires editing the block in 14 places.
**Why it's bad.** Synced Blocks are tracking blocks across pages, but they do not survive page restructuring well and break in unpredictable ways. They are a workaround for missing database views, not a sharing mechanism.
**Bad example:**
> "Synced block 'Q2 OKRs' embedded in 14 team-pages. Editing the OKR requires opening each page to confirm sync."
**Good example:**
> "Q2 OKRs live in the OKRs database. Each team page embeds a *filtered view* of the OKRs DB (filter: 'team = this team'). Editing the OKR updates everywhere automatically."
**How to catch it.** > 3 instances of the same Synced Block = replace with a DB view.

---

## Red Flag 9: Permissions Set Per-Page Manually

**Symptom.** Each PRD page has hand-edited permissions. The CTO has access to 12 of 18 PRDs; nobody knows why the other 6 are different.
**Why it's bad.** Per-page permission editing does not scale and creates security drift. Someone leaves; their access is forgotten. New joiners get inconsistent visibility.
**Bad example:**
> "PRD pages with hand-edited permissions. Engineering Director has visibility into ~70% of PRDs; the rest 'must have been missed at setup'."
**Good example:**
> "Permissions inherit from the PRDs database. Database access groups are defined per role (PM full edit; Engineering read; Sales-Leadership read-only on customer-facing PRDs only). New pages inherit; per-page overrides require a documented exception."
**How to catch it.** Any page with permissions different from its parent DB = audit; standardize via inheritance.

---

## Red Flag 10: PRDs as Free-Form Pages, Not DB Entries

**Symptom.** Each PRD is a Notion page in a hand-crafted folder; some have status; some do not; no consistent properties.
**Why it's bad.** Without DB structure, you cannot query "which PRDs are blocked", "which are awaiting design review", "average days from draft to approved". The PRDs database is the org's pipeline; free-form pages destroy it.
**Bad example:**
> "PRD folder contains 47 pages, each with its own ad-hoc top section. Some have Status, some have Owner, some neither."
**Good example:**
> "PRDs database with required properties: Status (Draft / In Review / Approved / Shipped / Archived), Owner (user), Squad (relation), Target Quarter (select), OKR (relation), Last Updated (auto), Pre-mortem complete (checkbox). Page body uses a Template with the 8-section PRD structure. New PRDs must use the Template; the body sections cannot be skipped."
**How to catch it.** PRD pages outside the PRDs DB = migrate.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | Page sprawl | > 100 top-level pages outside DBs = restructure |
| 2 | Missing relations | Cross-DB references stored as text = convert |
| 3 | Rollup-of-rollup performance | Render time > 3s = re-architect |
| 4 | Inline databases everywhere | Duplicate-named DBs > 5 = consolidate |
| 5 | No page owners / cadence | Pages without Last Reviewed = run audit |
| 6 | API tokens in pages | Search for `secret_*` = remove & rotate |
| 7 | Pagination ignored | API calls loop on `has_more`? |
| 8 | Synced Blocks as sharing | > 3 copies of same block = replace with DB view |
| 9 | Per-page permissions | Page perms differ from parent DB = audit |
| 10 | PRDs as free-form pages | PRDs outside PRDs DB = migrate |

## Related Reading

- `SKILL.md` -- Notion DB-driven PM patterns
- `references/notion-api-patterns.md` -- the API recipes
- `references/db-schemas.md` -- canonical PRD / OKR / Roadmap / Decision schemas
- Sibling skill: `confluence-expert/` -- the Atlassian-side equivalent
- Sibling skill: `jira-expert/` -- ticket data that feeds Notion dashboards
- Sibling skill: `execution/create-prd/` -- the PRD content that lives in the DB
- Sibling skill: `senior-pm/` -- portfolio + stakeholder dashboards in Notion
