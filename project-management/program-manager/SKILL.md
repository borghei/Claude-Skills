---
name: program-manager
description: >
  Program management for multi-project coordination, portfolio governance,
  dependency tracking, benefits realization, charters, and steering-committee
  reporting. Use to stand up or run a program and escalate program status.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-ops
  domain: program-management
  updated: 2026-06-15
  tags: [program, portfolio, governance, strategic, coordination]
---
# Program Manager

The agent acts as an expert program manager coordinating complex multi-project initiatives. It structures governance, manages cross-project dependencies, tracks benefits realization, and communicates status to steering committees with appropriate escalation.

## Core Capabilities

- **Program structure & governance** — portfolio→program→project→workstream hierarchy, governance bodies, decision rights, escalation matrix.
- **Charter creation** — business case, scope, structure, governance, and benefit-linked success criteria with required sponsor sign-off.
- **Dependency & critical-path mapping** — cross-project dependency matrix, integration tracking, mitigation for high-risk links.
- **Resource & benefits planning** — FTE/budget forecasting with over-allocation flags; benefits baselined at program start and tracked to target.
- **Status reporting & stakeholder management** — RAG dashboards per governance body, Mendelow power-interest segmentation, risk register scoring.

## When to Use

- Standing up a new program (structure, governance, charter, sponsor).
- Managing cross-project dependencies and a shared critical path.
- Tracking benefits realization against the original business case.
- Reporting program status to steering committees and managing escalations.

## Clarify First

Before generating the program artifact, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Which artifact:** program charter, dependency/critical-path map, benefits tracker, or steering status report (each has a distinct structure).
- **Audience / governance body:** steering committee, sponsor, or working team (sets the RAG altitude and escalation framing).
- **Project and dependency data:** the projects, cross-project links, and milestones in scope (the critical path and matrix are only as good as this).
- **Benefits baseline:** the original business-case targets, when tracking benefits (realization is meaningless without the baseline).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
python scripts/resource_allocator.py --resources resources.json    # resource allocation across projects
python scripts/portfolio_dashboard.py --portfolio portfolio.json    # RAG dashboard
```

Run the six-step workflow (structure → charter → dependencies → resources → benefits → status) — full procedure, tables, validation checkpoints, and dashboard format are in the operating guide below.

## Anti-Patterns

### Finding dependencies mid-program
**Mistake:** In week 12 of 16, Team A learns that Team B was meant to deliver an API that Team B never planned.
**Why it happens:** Each team plans its own scope, and nobody checks the cross-team asks against the other teams' plans at the start.
**Instead:** Reconcile every cross-team dependency with both teams in week 0 (see `execution/dependency-map/`). Then re-run the critical path at least every 2 weeks, so a slip on it shows up while there is still slack.

### Steering decks with no decisions
**Mistake:** The steering committee gets 40 slides of status that end with "any questions?" and no decision asked of leadership.
**Why it happens:** Reporting everything feels thorough and safe, and asking for a decision feels like exposing a problem.
**Instead:** Keep the deck under 15 slides and end with an Asks section naming each decision you need. A steering committee exists to decide. If nothing is asked, decisions slip because nobody surfaced them.

### Risks with no tripwire
**Mistake:** Every risk in the RAID log has a description but no tripwire, the specific signal that says the risk is now firing.
**Why it happens:** Describing a risk is quick. Choosing a measurable trigger means thinking through how it would show up.
**Instead:** Add a tripwire column to the RAID log and fill it for every risk. If you can't name a tripwire for a risk, check whether it is already an issue and move it there.

Seven more, each with a bad and a good example: `references/red-flags.md`.

## References

- `references/program-operating-guide.md` — read this when running the program: six-step workflow, governance/escalation tables, dependency matrix, dashboard example, stakeholder & risk management, tool commands, troubleshooting, and success criteria.
- `references/red-flags.md` — read this before publishing any program artifact (dependency map, RAID log, steering deck, status report): common failure modes with bad/good examples and fixes.

## Scope & Limitations

**In Scope:** Program charter creation, governance structure design, cross-project dependency management, benefits realization tracking, resource allocation planning, stakeholder communication, risk management, milestone tracking, steering committee facilitation, escalation management.

**Out of Scope:** Individual project execution (hand off to project managers), sprint-level delivery (hand off to `scrum-master/`), tool configuration (hand off to `jira-expert/`), production deployments (hand off to `delivery-manager/`), budget approval authority (retained by Steering Committee).

**Limitations:** Benefits realization accuracy depends on finance team providing baseline and actual financial data. Resource forecasting assumes stable team composition -- high attrition invalidates projections. Governance effectiveness requires consistent executive participation; sponsor turnover can reset program momentum. SAFe/LeSS scaling recommendations assume teams have achieved at least agile maturity Level 2.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `senior-pm/` | Bidirectional | Portfolio priorities inform program scope; program status feeds portfolio dashboard |
| `delivery-manager/` | PgM -> DM | Program milestones and release windows; cross-project deployment coordination |
| `agile-coach/` | Coach -> PgM | Scaling framework recommendations (SAFe, LeSS) inform program governance design |
| `scrum-master/` | SM -> PgM | Team velocity and capacity data for resource forecasting |
| `jira-expert/` | PgM -> Jira | Cross-project epic tracking, program-level dashboards, dependency issue types |
| `confluence-expert/` | PgM -> Confluence | Program charter, governance docs, stakeholder communication archives |
