# Worked Example: Feature End-to-End

**Scenario:** You're a PM at a B2B SaaS company. The sales team has been requesting a "shared dashboards" feature for quarterly business reviews. You need to validate the idea, scope it, and ship it.

This example shows how to take a vague request from idea → release notes in **6 commands** using the PM skills library.

---

## The Feature

> "Customers want to share dashboards with their clients during QBRs."
> — Sales team, repeated in 4 deal-review meetings

You have:
- ~3 sales anecdotes (no quant)
- A roadmap slot in next quarter
- Engineering capacity: 1 squad, 6 weeks

---

## Step 1 — Brainstorm ideas (Product Trio)

**Skill:** `discovery/brainstorm-ideas/`

Generate ideas from PM, Designer, and Engineer perspectives on *how* sharing could work.

```bash
# Open the brainstorm-ideas skill, fill the Product Trio canvas
# Result: 15 distinct solution shapes (link-share, embed, PDF export, live collab, ...)
```

**Output:** `dashboard-sharing-ideas.md` — 15 ideas grouped by solution shape.

---

## Step 2 — Identify assumptions

**Skill:** `discovery/identify-assumptions/`

For the top 3 solution shapes, surface what we're assuming about value, usability, viability, and feasibility.

```bash
python discovery/identify-assumptions/scripts/assumption_tracker.py \
  --solution "Public read-only share link" \
  --format markdown \
  --output assumptions-public-link.md
```

**Key assumptions surfaced:**
- Value: Customers will share with >3 clients per quarter (untested)
- Usability: Recipients won't need an account (untested)
- Viability: We can price it at $20/mo per seat (untested)
- Feasibility: Our data layer supports row-level sharing (false — needs work)

**Output:** Prioritized assumption matrix, top 3 marked "Test Now".

---

## Step 3 — Design a lean experiment

**Skill:** `discovery/brainstorm-experiments/`

Test the riskiest assumption (Value: will they share with >3 clients?) before building.

```bash
python discovery/brainstorm-experiments/scripts/experiment_designer.py \
  --assumption "Customers share with >3 clients per quarter" \
  --format markdown \
  --output experiment-share-frequency.md
```

**Experiment:** Concierge MVP. Manually generate share links for 10 customers; track usage over 4 weeks.

**Hypothesis (XYZ format):** "We believe at least 60% of the 10 customers will generate ≥3 share links within 4 weeks. We'll know we're right if usage exceeds that threshold."

**Decision rule:** ≥60% → build. <40% → kill. 40–60% → run a second experiment.

**Output:** Experiment plan with success criteria, kill criteria, and timeline.

---

## Step 4 — Pre-mortem

**Skill:** `discovery/pre-mortem/`

Before scoping the PRD, run a pre-mortem on "what could go wrong if we ship this?".

```bash
python discovery/pre-mortem/scripts/risk_categorizer.py \
  --feature "Shared dashboards v1" \
  --format mermaid \
  --output risks-shared-dashboards.mmd
```

**Risks identified:**
- 🐅 Tiger: Security incident — share links leak sensitive data → mitigation: signed URLs + expiry
- 🐅 Tiger: Data residency violation in EU → mitigation: regional share link domains
- 📄 Paper Tiger: Performance under load (false alarm — we cache reads)
- 🐘 Elephant: Long-term — analytics on shared views (not v1, but plan for v2)

**Output:** Tiger/Paper Tiger/Elephant matrix, mitigation plan for Tigers.

---

## Step 5 — Write the PRD

**Skill:** `execution/create-prd/`

Now you have validated value (assumption confirmed), known risks (mitigated), and a feasible scope. Write the PRD.

```bash
python execution/create-prd/scripts/prd_scaffolder.py \
  --product-name "Shared Dashboards" \
  --objective "Let customers share read-only dashboards with external stakeholders during QBRs" \
  --segments "Sales-led B2B customers, Customer success teams" \
  --format markdown \
  --output PRD-shared-dashboards.md
```

**Output:** 8-section PRD skeleton. You fill in:
- Section 4 (Objective): "Increase QBR engagement by 30% via shareable artifacts; KR1: 40% of mid-market customers use share links by Q3"
- Section 7 (Solution): P0 = signed URLs + expiry + audit log; P1 = revoke from UI; P2 = analytics on shared views
- Section 8 (Release): v1 = link-share. v2 (deferred) = embed, PDF export, live collab

---

## Step 6 — Define OKRs

**Skill:** `execution/brainstorm-okrs/`

Connect the feature to a measurable outcome.

```bash
python execution/brainstorm-okrs/scripts/okr_validator.py \
  --objective "Customers complete higher-impact QBRs with their clients" \
  --format markdown \
  --output okrs-q3-shared-dashboards.md
```

**Output (validated against SMART criteria):**

> **Objective:** Customers complete higher-impact QBRs with their clients.
>
> - **KR1:** Increase QBR satisfaction score from 7.2 → 8.5 by end of Q3
> - **KR2:** 40% of mid-market customers generate ≥1 share link in Q3
> - **KR3:** Reduce QBR prep time from 4 hr → 1 hr (customer-reported)

---

## Step 7 — Prioritize the backlog

**Skill:** `execution/prioritization-frameworks/`

Rank the 12 stories spawned from the PRD using RICE.

```bash
python execution/prioritization-frameworks/scripts/prioritization_scorer.py \
  backlog-shared-dashboards.json \
  --framework rice \
  --format markdown \
  --output ranked-backlog.md
```

**Output:** RICE-scored backlog. Top 3:
1. Signed share URLs with expiry (RICE: 480)
2. Revoke-from-UI (RICE: 360)
3. Audit log of shared views (RICE: 240)

---

## Step 8 — Write release notes

**Skill:** `execution/release-notes/`

After v1 ships, generate user-facing release notes from the closed tickets.

```bash
python execution/release-notes/scripts/release_notes_generator.py \
  shipped-tickets.json \
  --product-name "Shared Dashboards" \
  --version "1.0" \
  --format markdown \
  --output release-notes-v1.md
```

**Output:** Category-grouped release notes ready to publish.

---

## What you produced

| Artifact | Skill | Purpose |
|---|---|---|
| `dashboard-sharing-ideas.md` | brainstorm-ideas | Solution space |
| `assumptions-public-link.md` | identify-assumptions | Risk surface |
| `experiment-share-frequency.md` | brainstorm-experiments | Validation plan |
| `risks-shared-dashboards.mmd` | pre-mortem | Mitigation plan |
| `PRD-shared-dashboards.md` | create-prd | Build spec |
| `okrs-q3-shared-dashboards.md` | brainstorm-okrs | Success metric |
| `ranked-backlog.md` | prioritization-frameworks | Build order |
| `release-notes-v1.md` | release-notes | Launch comms |

**Total commands:** 6 Python invocations + 2 manual canvas fills.

**Total time (typical PM):** ~6 hours instead of ~3 weeks of meetings.

---

## Push to your tools

Every artifact above can be pushed to Jira/Linear/Notion/Confluence directly:

```bash
# Push PRD to Confluence -- ask your agent to call the Atlassian Rovo MCP Server
# tool createConfluenceContent (space PROD, title "PRD: Shared Dashboards",
# body from PRD-shared-dashboards.md)

# Push backlog to Linear
python execution/prioritization-frameworks/scripts/prioritization_scorer.py \
  backlog-shared-dashboards.json --framework rice --format linear \
  | linear-cli issues create-batch --team PROD

# Push roadmap to Notion
python execution/outcome-roadmap/scripts/roadmap_transformer.py \
  --format notion --output - | notion-cli pages create --parent <db-id>
```

---

## Next examples

- [`sprint-planning.md`](sprint-planning.md) — data-driven sprint planning from velocity + backlog
- [`exec-status-update.md`](exec-status-update.md) — weekly exec update from Jira/Linear data

---

**Last Updated:** 2026-05-21
