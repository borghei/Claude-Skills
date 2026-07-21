---
name: knowledge-ops
description: >
  Audit and repair an internal knowledge base — staleness, ownership gaps, orphans,
  duplication, and findability. Use when the wiki is untrusted, docs are out of date,
  nobody owns pages, or search returns the wrong answer.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-operations
  domain: knowledge-management
  updated: 2026-07-21
  tags: [knowledge-base, documentation, information-architecture, doc-ownership, findability]
---

# Knowledge Operations

Knowledge bases do not fail by being incomplete. They fail by becoming untrustworthy: once a
reader has been burned twice by a confidently wrong page, they stop reading and start asking
in chat, and every subsequent doc you write is written into a void. This skill treats the KB
as an operational system with owners, freshness SLAs, and a measurable health score — not as
a writing backlog.

The core insight is that **deletion is the highest-value action available**. Most struggling
knowledge bases need 30% fewer pages, not more pages.

## When to use this skill

- The wiki is **large and distrusted** — people ask in chat rather than search, and are right to
- A **doc audit** is due before onboarding a cohort, an acquisition merge, or a compliance review
- **Search returns the wrong page** consistently, usually because three near-duplicates compete
- **Nobody owns** large parts of the KB and nobody can say what is current
- Planning a **documentation-debt sprint** and needing a ranked backlog rather than a wish list
- **Migrating** between wiki platforms and needing to decide what survives the move

## Inputs the skill expects

- A **doc inventory**: path, title, owner, last-updated date, and outbound links
- **Criticality tier** per doc, or enough signal (traffic, area) to infer it
- **Usage data** if available — 90-day views separate the load-bearing pages from the archive
- The **as-of date** for the audit, so results are reproducible
- Your **freshness SLA policy**, or acceptance of the default tiering below
- Whether **deletion is politically possible**, which changes the entire remediation plan

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which docs are load-bearing vs archival** — a stale onboarding runbook is an incident; a stale 2019 retro is fine, and treating them identically produces a backlog nobody works
- [ ] **Whether pages can be deleted or only archived** — deletion authority roughly halves the remediation effort, so the plan differs structurally
- [ ] **Who can be assigned as an owner** — ownership assigned to a team alias rather than a person is the same as no owner, and the audit will keep reporting it
- [ ] **The as-of date for the audit** — staleness is relative, and an undated audit cannot be compared against the next one

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Score KB health

1. Build a doc inventory as JSON, or point the auditor at a directory of markdown with
   YAML frontmatter (`owner`, `updated`, `tier`).
2. Run the auditor with an explicit `--as-of` date so the run is reproducible.
3. Read the health score as a trend, not an absolute. A first run below 60 is normal;
   what matters is the direction across quarterly runs.
4. Triage the `critical` findings first — a stale critical-tier doc is the class of failure
   that causes real incidents.

```bash
python3 business-operations/knowledge-ops/scripts/kb_health_auditor.py \
  --input business-operations/knowledge-ops/assets/sample_kb.json \
  --as-of 2026-07-21 --format text
```

To scan a real directory of markdown instead:

```bash
python3 business-operations/knowledge-ops/scripts/kb_health_auditor.py \
  --root ./docs --as-of 2026-07-21 --format json
```

### Workflow 2 — Find orphans, dead links, and duplicates

1. Run the orphan detector over the same inventory. It builds the link graph and reports
   pages nothing links to, links pointing at pages that do not exist, and hub pages.
2. Cross-reference orphans against traffic. **An orphan with traffic is a findability bug**
   (people reach it by search or bookmark but the IA does not connect it). **An orphan with
   no traffic is a deletion candidate.** These need opposite fixes.
3. Fix dead links before anything else — they are cheap and they are the most visible
   signal of an unmaintained KB.

```bash
python3 business-operations/knowledge-ops/scripts/orphan_detector.py \
  --input business-operations/knowledge-ops/assets/sample_kb.json \
  --format text
```

### Workflow 3 — Build a ranked documentation-debt backlog

1. Run the debt ranker over the inventory. It scores each issue on value (traffic ×
   criticality × severity) and effort, then sorts into do-now / schedule / batch / drop.
2. Take the top 10 into a debt sprint. Do not attempt the whole backlog — the backlog is a
   measurement instrument, not a plan.
3. Re-run the auditor after the sprint with the same `--as-of` convention to show movement.

```bash
python3 business-operations/knowledge-ops/scripts/doc_debt_ranker.py \
  --input business-operations/knowledge-ops/assets/sample_kb.json \
  --as-of 2026-07-21 --top 10 --format text
```

## Decision frameworks

### Freshness SLA by tier [PROVEN]

Uniform review cycles fail because they generate more review work than any team will do, so
nothing gets reviewed. Tier the SLA instead.

| Tier | Examples | Review SLA | Stale at | Action when stale |
|------|----------|-----------|----------|-------------------|
| **Critical** | On-call runbooks, incident procedures, security policy, payroll process | 90 days | 120 days | Page the owner; a stale runbook is an incident risk |
| **Core** | Onboarding, architecture overviews, team charters, release process | 180 days | 270 days | Owner review ticket in the next sprint |
| **Reference** | How-tos, tool guides, FAQs | 365 days | 540 days | Batch review annually |
| **Archive** | Retros, past project docs, historical decisions | Never | Never | Mark archived; exclude from search and from the score |

The single most valuable configuration change in most knowledge bases is moving 40% of pages
into Archive and excluding them from search. Search quality is a ratio, and the denominator is
usually the problem.

### Orphan triage [PROVEN]

| Inbound links | 90-day traffic | Diagnosis | Action |
|---------------|----------------|-----------|--------|
| 0 | 0 | Dead weight | Delete. Not archive — delete |
| 0 | Low (1-50) | Bookmark-only survivor | Link it from the right hub, or fold into a parent page |
| 0 | High (50+) | Findability bug | Link from a hub urgently; people are relying on a page the IA hides |
| 1-2 | Any | Weakly connected | Fine if the parent is the right one |
| 10+ | High | Hub page | Protect it; assign a named owner and the Critical SLA |

### Duplication resolution [RECOMMENDED]

When two or more pages cover the same topic, **merge into the one with the most inbound links**,
not the one that is best written. Inbound links represent accumulated navigation habit across
the org; rewriting the winner is cheap, rebuilding link equity is not. Redirect the losers,
never delete them silently — a 404 on a bookmarked page costs more trust than a stale page did.

Escape hatch: if the highest-linked version is factually wrong and the other is correct, merge
into the linked one and replace its content wholesale. The URL wins, the content does not.

### Health score bands

| Score | Reading | Response |
|-------|---------|----------|
| 80-100 | Healthy; maintenance mode | Quarterly audit, keep SLAs |
| 60-79 | Degrading; trust still intact | One debt sprint, focus on critical-tier staleness |
| 40-59 | Distrusted; people are asking in chat | Ownership assignment sprint first, then content |
| 0-39 | Failed; a rewrite is cheaper than a repair | Pick the top 20 pages by traffic, rebuild those, archive everything else |

## Anti-Patterns

### The Documentation Sprint With No Owners
**Mistake:** Running a week-long effort where everyone writes docs, then declaring the KB fixed.
**Why it happens:** Writing is visible, satisfying, and easy to organise. Ownership is neither.
**Instead:** Assign owners before writing anything. An unowned page is stale the day it is
written — it just has not been noticed yet. If you can only do one thing, do ownership
assignment; a KB with owners and old content recovers, and a KB with fresh content and no
owners degrades to the same state within two quarters.

### Team Aliases as Owners
**Mistake:** Setting the owner field to `@platform-team` or `docs@company.com`.
**Why it happens:** It survives staff turnover and feels more robust than naming a person.
**Instead:** Name a person, with the team as a fallback field. Review notifications sent to a
group alias are read by nobody — this is the most reliable finding in knowledge-base
operations. Rotate the named owner quarterly if you must, but keep it a person.

### Archiving Instead of Deleting
**Mistake:** Moving every obsolete page to an archive space rather than removing it.
**Why it happens:** Deletion feels risky and irreversible, and someone always says "we might
need it."
**Instead:** Delete pages with zero inbound links and zero traffic outright — version history
already preserves them. Archive is for documents with historical or compliance value, not for
things you are afraid to delete. An archive that grows without bound is a slower failure mode
than deletion, not a safer one.

### Optimising Search Instead of Fixing Content
**Mistake:** Responding to "search is broken" by tuning the search engine or buying a new one.
**Why it happens:** It is a procurement problem with a vendor solution, which is easier than a
content problem with an organisational solution.
**Instead:** Search almost always fails because three near-duplicate pages compete for the same
query and the engine cannot know which is current. Merge the duplicates and exclude archives
from the index. Do this before evaluating any search product — it is usually the whole fix.

### Auditing Without an As-Of Date
**Mistake:** Running the audit ad hoc and comparing results across runs.
**Why it happens:** The tooling defaults to "today" and nobody records what today was.
**Instead:** Always pass an explicit `--as-of` and store the output. KB health is only
meaningful as a trend; two undated audits cannot be compared, and a number with no trend
gets ignored by the people who fund the remediation.

## Files

| File | Purpose |
|------|---------|
| `scripts/kb_health_auditor.py` | Scores staleness against tiered SLAs, missing owners, duplicate titles, and thin pages |
| `scripts/orphan_detector.py` | Builds the link graph; reports orphans, dead links, hub pages, and traffic-weighted triage |
| `scripts/doc_debt_ranker.py` | Ranks remediation work by value and effort into do-now / schedule / batch / drop |
| `references/information-architecture-patterns.md` | IA models, hub-and-spoke structure, naming, and search-behaviour design |
| `references/freshness-sla-and-ownership.md` | SLA tiering, ownership models, review workflows, and health metrics |
| `assets/kb-audit-report-template.md` | Report template for presenting audit findings and a remediation plan |
| `assets/doc-ownership-charter.md` | Charter defining what a doc owner is accountable for |
| `assets/sample_kb.json` | Runnable inventory used by all three scripts |
