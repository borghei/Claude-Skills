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

Before generating the program artifact, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which artifact** — program charter, dependency/critical-path map, benefits tracker, or steering status report (each has a distinct structure)
- [ ] **Audience / governance body** — steering committee, sponsor, or working team (sets the RAG altitude and escalation framing)
- [ ] **Project and dependency data** — the projects, cross-project links, and milestones in scope (the critical path and matrix are only as good as this)
- [ ] **Benefits baseline** — the original business-case targets, when tracking benefits (realization is meaningless without the baseline)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python scripts/dependency_analyzer.py --projects projects.yaml      # critical path
python scripts/resource_forecast.py --program program.yaml --months 12
python scripts/benefits_tracker.py --plan benefits_plan.yaml
python scripts/program_dashboard.py --program "Name"                # RAG dashboard
```

Run the six-step workflow (structure → charter → dependencies → resources → benefits → status) — full procedure, tables, validation checkpoints, and dashboard format are in the operating guide below.

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
