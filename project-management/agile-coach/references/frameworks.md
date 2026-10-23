# Agile Framework Comparison and Selection

> Read this when assessing organizational maturity or selecting a framework: the 5-level maturity model and its 6 dimensions, the size × complexity selection grid, and the Scrum/Kanban/SAFe/LeSS comparison table.

## Assess Current State

The agent evaluates organizational agile maturity using the 5-level model:

```bash
python scripts/agile_maturity_scorer.py --assessment assessment.json
```

**Maturity Levels:**

| Level | Name | Indicators |
|-------|------|-----------|
| 1 | Initial | Ad-hoc processes, hero-dependent delivery, limited visibility |
| 2 | Repeatable | Basic Scrum/Kanban in place, team-level practices, some metrics |
| 3 | Defined | Consistent practices across teams, cross-team coordination, CI culture |
| 4 | Managed | Quantitative management, predictable outcomes, business alignment |
| 5 | Optimizing | Innovation culture, market responsiveness, organizational learning |

**Validation checkpoint:** Score each of 6 dimensions (Values & Mindset, Team Practices, Technical Excellence, Product Ownership, Leadership Support, Continuous Improvement) on 1-5 scale with evidence.

## Select Framework

The agent recommends a framework based on team size and complexity:

```
                    Simple          Complex
Small (1-2 teams)   Kanban          Scrum
                    XP              Scrumban

Medium (3-8 teams)  Scrum@Scale     SAFe Essential
                    Nexus           LeSS

Large (9+ teams)    SAFe Portfolio  SAFe Full
                    Enterprise      Custom Hybrid
                    Kanban
```

| Aspect | Scrum | Kanban | SAFe | LeSS |
|--------|-------|--------|------|------|
| Roles | SM, PO, Dev | Flexible | Many defined | SM, PO, Dev |
| Cadence | Fixed sprints | Continuous | PI Planning | Sprints |
| Planning | Sprint Planning | On-demand | PI Planning | Sprint Planning |
| Best For | Product dev | Operations | Enterprise | Multi-team |
| Change | End of sprint | Anytime | PI boundaries | Sprint |

**Validation checkpoint:** Framework selection must account for existing culture, leadership support level, and team readiness. Never recommend SAFe for teams below maturity level 2.
