---
name: wwas
description: >
  Writes and grades Why-What-Acceptance backlog items so each one traces to an OKR
  and passes INVEST before a sprint. Use when writing backlog items, checking sprint
  readiness, or finding work that serves no objective.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: invest_gate_checker.py, wwas_quality_scorer.py, backlog_alignment_checker.py
  tech-stack: backlog-management, invest-criteria, strategic-alignment
  tags:
    - backlog
    - acceptance-criteria
    - invest
    - strategic-alignment
---
# Why-What-Acceptance Backlog Expert

## Overview

Create backlog items using the Why-What-Acceptance (WWAS) format. This format ensures every piece of work connects to strategic context, includes a concise description that serves as a "reminder of the discussion" rather than a detailed specification, and defines high-level acceptance criteria focused on observable outcomes.

The format has three parts:

- **Why (1-2 sentences):** connects the item to a business objective, OKR, or theme; answers "why does this matter?" and "why now?" If you cannot write a compelling Why, the item should not be prioritized.
- **What (1-2 paragraphs):** a reminder of the refinement discussion, not a specification. Link the design if one exists.
- **Acceptance Criteria (4+):** observable outcomes that define done — not implementation steps or test scripts.

Before an item enters a sprint, it must pass the **INVEST** gates (Independent, Negotiable, Valuable, Estimable, Small, Testable).

### When to Use

- **Backlog creation** -- building a product backlog where strategic alignment is critical.
- **Sprint planning** -- refining items and the team needs to understand *why* each matters.
- **Stakeholder communication** -- executives need to see how work connects to business objectives.
- **Roadmap decomposition** -- breaking roadmap themes into actionable backlog items.

### When NOT to Use

- When you need situation-driven requirements -- use `job-stories/` instead.
- A pure technical task with no strategic context (use a simple task description).
- The team prefers traditional user stories and strategic context is well-understood.

## Clarify First

Before writing the item, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The strategic objective / OKR it connects to:** drives the **Why**; without it the Why is a forced exercise and the item should not be prioritized.
- **The refinement discussion or design link:** becomes the **What** (a reminder of the discussion, not a specification).
- **The observable done-state:** drives the **Acceptance Criteria** (outcomes a user or system can observe, not implementation steps or test scripts).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

All three read a backlog JSON (`items[]` with `title`, `why`, `what`, `acceptance_criteria`, optional `design_link`, `okr_ref`; the alignment checker also reads `okrs[]` with `id`, `name`, `keywords`). Each prints text or `--format json` (`--json` is the same), and `--example` prints a valid input.

| Tool | Flag | Checks |
|------|------|--------|
| `invest_gate_checker.py` | `--items FILE` | Six INVEST gates per item. Testable needs at least half the criteria to name an observable behaviour or threshold; Estimable needs 4+ criteria. **Gate:** exits 1 if any item is FAIL or CONDITIONAL. |
| `wwas_quality_scorer.py` | `--items FILE` | 0-100 per item for Why (metric, objective), What (length, design link) and criteria (count, edge cases). |
| `backlog_alignment_checker.py` | `--backlog FILE` | Which items map to which OKR (by `okr_ref` or keywords), unaligned items, OKRs with no items. |

```bash
# Sprint-ready backlog: all tools report clean, the gate exits 0
python3 project-management/execution/wwas/scripts/invest_gate_checker.py \
  --items project-management/execution/wwas/assets/sample_backlog_ready.json
# Mixed backlog: two items with a feature-as-Why and vague criteria; the gate exits 1
python3 project-management/execution/wwas/scripts/invest_gate_checker.py \
  --items project-management/execution/wwas/assets/sample_backlog.json
python3 project-management/execution/wwas/scripts/backlog_alignment_checker.py \
  --backlog project-management/execution/wwas/assets/sample_backlog.json
```

**Exit codes:** `0` report produced (for the INVEST checker: every item sprint-ready) · `1` INVEST checker only: at least one item not ready · `2` missing or unreadable file, invalid JSON, or the wrong shape.

The checks are keyword heuristics. A pass means the item has the right parts, not that the Why is true or the criteria are the right ones; read the items too.

## Anti-Patterns

### A Why that names the feature
**Mistake:** "Why: to launch bulk-edit." The reason given for the work is the work itself.
**Why it happens:** The team has already decided to build it, so the Why gets written after the fact.
**Instead:** End the Why in a customer outcome or business metric tied to an objective or OKR. If the Why mentions the feature itself, rewrite it. If you can't, the item isn't ready to prioritize.

### A Why with no hypothesis
**Mistake:** The Why states the impact as a certainty, with no sign it is a bet and no plan to check it.
**Why it happens:** A confident Why gets through prioritization more easily than one that admits doubt.
**Instead:** Frame the Why as a hypothesis: the outcome you expect and how you will measure it after launch. Then the team can tell whether the bet paid off, and can de-prioritize the work when evidence says no.

### Ignoring existing data and workflows
**Mistake:** The What and the Acceptance Criteria describe only the new behavior. Neither says what happens to existing records, deprecated flows or in-flight states.
**Why it happens:** The refinement discussion focuses on the new experience, and the migration tail is easy to miss.
**Instead:** State what happens to existing data and workflows in the What or the Acceptance Criteria. If the item says nothing about them, ask the engineering reviewer to check for a migration before approving.

Seven more, each with a bad and a good example: `references/red-flags.md`.

## Reference Documentation

Load the reference that matches the task; keep this file lean and pull detail on demand.

- **[references/wwas-format-and-examples.md](references/wwas-format-and-examples.md)** — full Why/What/Acceptance writing rules with good/bad examples, the INVEST gate table, the item template, a complete worked example, the objective-mapping table, troubleshooting, and success criteria. Read this when writing or reviewing actual WWAS items.
- **[references/backlog-management-guide.md](references/backlog-management-guide.md)** — format comparison (WWAS vs user stories vs job stories), INVEST deep dive, Definition of Ready, and refinement best practices. Read when choosing a format or running refinement.
- **[references/red-flags.md](references/red-flags.md)** — bad-vs-good quoted examples of WWAS items. Scan every item before it enters refinement.
- `assets/wwas_template.md` — ready-to-use WWAS templates.

## Scope & Limitations

**In Scope:** Writing items in WWAS format, applying INVEST gates, connecting work to strategic objectives, facilitating refinement, converting existing items to WWAS, integrating with Jira.

**Out of Scope:** Situation-driven requirements (`job-stories/`), ideation/discovery (`discovery/brainstorm-ideas/`), OKR definition (`execution/brainstorm-okrs/`), detailed technical specs, sprint planning/capacity (`../scrum-master/`).

**Limitations:** WWAS adds most value with clearly defined objectives (OKRs, North Star). Without strategic context the Why becomes a forced exercise. It fits product/feature work better than pure tech-debt/infra items. Teams transitioning from user stories may need 2-3 sprints to build fluency.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `job-stories/` | Complementary | Job stories add situational context (When); WWAS adds strategic context (Why). Use both for complete requirements |
| `summarize-meeting/` | Meetings -> WWAS | Refinement discussions produce the What; decisions produce acceptance criteria |
| `../jira-expert/` | WWAS -> Jira | WWAS items become Jira tickets with structured description fields |
| `execution/brainstorm-okrs/` | OKRs -> WWAS | Team OKRs provide the strategic objectives that Why statements reference |
| `execution/prioritization-frameworks/` | WWAS -> Prioritization | WWAS items scored via RICE or other frameworks for backlog ordering |
| `discovery/brainstorm-ideas/` | Ideas -> WWAS | Validated ideas decompose into WWAS backlog items with strategic traceability |

## Files

| File | Purpose |
|------|---------|
| `scripts/invest_gate_checker.py` | INVEST gate (exit 1 when not sprint-ready) |
| `scripts/wwas_quality_scorer.py` | Per-item WWAS quality score |
| `scripts/backlog_alignment_checker.py` | Item-to-OKR alignment and coverage |
| `assets/sample_backlog_ready.json` | Two sprint-ready items; gate exits 0 |
| `assets/sample_backlog.json` | Four items, two not ready; gate exits 1 |
| `assets/wwas_template.md` | Item templates |
| `examples/northwind-backlog-rewritten.md` | Worked rewrite of a weak backlog |
