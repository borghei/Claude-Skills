# Business Operations Skills - Claude Code Guidance

This domain covers the internal operating machinery of a company: how work
capacity is planned, how processes run, how vendors and spend are managed, and
how information and announcements move through the organisation.

Distinct from `c-level-advisor/` (strategic counsel at the executive altitude)
and `project-management/` (delivery of specific initiatives). This domain is the
recurring operational layer underneath both.

## Business Operations Skills Overview (6 skills)

- **capacity-planner/** — headcount and team-capacity planning: converting gross
  headcount into committable hours, modelling hire/contract/defer scenarios
  across quarters, and reporting capacity-vs-commitment gaps. Use when planning
  a quarter, justifying a hire, or explaining why a roadmap does not fit.

- **process-mapper/** — mapping and improving business processes: SIPOC and
  swimlane capture, cycle-time and wait-time analysis, handoff and bottleneck
  identification, and a prioritised improvement backlog. Use when a process is
  slow, ownership is unclear, or work stalls between teams.

- **vendor-management/** — vendor lifecycle: weighted selection scorecards, risk
  tiering, SLA performance review, renewal tracking, and consolidation analysis.
  Use when selecting a vendor, preparing a renewal, or reviewing a portfolio.

- **internal-comms/** — internal communication strategy: announcement planning by
  audience and blast radius, change-communication sequencing, all-hands and
  exec-update structure, and message testing before send. Use when announcing a
  change, planning a reorg communication, or auditing a draft.

- **knowledge-ops/** — internal knowledge base health: information architecture,
  doc ownership and freshness SLAs, duplication and orphan detection, and a
  documentation-debt backlog. Use when the wiki has decayed, docs are stale, or
  nobody can find anything.

- **procurement-optimizer/** — software and services spend optimisation: spend
  categorisation, license utilisation, redundant-tool detection, renewal timing
  leverage, and savings-opportunity ranking. Use when cutting SaaS spend or
  preparing a negotiation.

**Total Tools:** 18 Python automation tools (stdlib only)

## Common Patterns

```
business-operations/<skill>/
├── SKILL.md
├── references/
│   └── *.md (frameworks, benchmarks, decision thresholds)
├── scripts/
│   └── *.py (analysis, scoring, modelling — stdlib only)
└── assets/
    └── *.md templates + sample_*.json inputs
```

Every script accepts `--input <sample>.json --format {text,json}`. Several expose
a gate flag (`--fail-on`, `--min-*`) that exits non-zero so the tool can run in
CI or a scheduled review.

## Related Skills

- `project-management/` — delivery of specific initiatives (this domain is the
  recurring operational layer)
- `c-level-advisor/coo-advisor` — strategic operations counsel
- `hr-operations/` — people processes specifically
- `finance/` — financial planning (procurement-optimizer covers spend, not FP&A)
- `business-growth/` — external commercial motion

## Quality Standard

Each skill must:
- Use stdlib-only Python (no external dependencies)
- Support both JSON and human-readable output (`--format` flag)
- Carry real benchmark numbers and thresholds, not generic advice
- State an opinionated default with the escape hatch named
- Ship runnable sample data for every documented workflow

---

**Last Updated:** July 2026
**Skills Deployed:** 6/6 business operations skills
