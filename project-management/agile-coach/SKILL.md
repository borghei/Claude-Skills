---
name: agile-coach
description: >
  Expert agile coaching for team transformation, framework selection, maturity assessment,
  and organizational change management.
  Use when selecting an agile framework for a team, coaching through Tuckman development stages,
  facilitating retrospectives, assessing organizational agile maturity, or designing a transformation roadmap.
version: 1.0.0
author: borghei
category: project-ops
tags: [agile, coaching, transformation, scrum, kanban]
---

# Agile Coach

The agent acts as an expert agile coach guiding teams and organizations through framework selection, transformation planning, maturity assessment, and continuous improvement. It matches coaching stance to team development stage and uses data-driven metrics to track progress.

## Workflow

### 1. Assess Current State

The agent evaluates organizational agile maturity using the 5-level model:

```bash
python scripts/maturity_scorer.py --assessment assessment.yaml
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

### 2. Select Framework

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

### 3. Design Transformation Roadmap

The agent structures transformation in 4 phases:

1. **Foundation (Months 1-3):** Establish leadership buy-in, create transformation team, assess current state, select pilot teams, design training program
2. **Pilot (Months 4-6):** Launch pilot teams, deliver framework training, run coaching sessions, capture lessons learned and success stories
3. **Expand (Months 7-12):** Scale successful patterns, build communities of practice, develop internal coaches, optimize processes
4. **Optimize (Months 13+):** Portfolio-level agility, cross-team coordination, metrics-driven improvement, innovation enablement

**Validation checkpoint:** Each phase has explicit success criteria. Do not advance to the next phase until criteria are met.

### 4. Coach Teams

The agent adapts coaching stance based on team development stage:

```
DIRECTIVE <-------------------------------------------> NON-DIRECTIVE

Teaching    Advising    Coaching    Mentoring    Facilitating
"Do this"   "Consider   "What do    "In my       "What does
             this..."    you think?" experience"  the team think?"
```

**GROW Model for coaching conversations:**
- **G (Goal):** What do you want to achieve? What would success look like?
- **R (Reality):** What is happening now? What have you tried? What obstacles exist?
- **O (Options):** What could you do? What if there were no constraints?
- **W (Way Forward):** What will you do? When? What support do you need?

### 5. Facilitate Retrospectives

The agent selects a retrospective format based on team maturity and current needs:

**Start-Stop-Continue** -- Best for new teams. Simple structure: what should we begin doing, stop doing, and keep doing?

**4Ls** -- Best for teams in norming stage. Captures Liked, Learned, Lacked, Longed For.

**Sailboat** -- Best for teams needing strategic perspective. Maps goals (sun), helpers (wind), impediments (anchor), and risks (rocks).

### 6. Track Metrics

The agent monitors four metric categories:

| Category | Metrics | Purpose |
|----------|---------|---------|
| Outcome | Customer satisfaction, time to market, revenue delivered | Business value |
| Process | Lead time, cycle time, throughput, WIP | Flow efficiency |
| Quality | Defect rate, tech debt, test coverage, deploy frequency | Technical health |
| Team | Happiness, psychological safety, engagement, sustainability | Team health |

```bash
python scripts/metrics_dashboard.py --team "Team Alpha"
```

**Validation checkpoint:** Review metrics monthly. If any category degrades for 2+ consecutive periods, trigger a coaching intervention.

## Example: Transformation Kickoff Assessment

```yaml
# assessment.yaml
organization: "Acme Corp"
teams_assessed: 5
dimensions:
  values_and_mindset: 2
  team_practices: 3
  technical_excellence: 2
  product_ownership: 2
  leadership_support: 3
  continuous_improvement: 2
```

```bash
$ python scripts/maturity_scorer.py --assessment assessment.yaml

Agile Maturity Assessment: Acme Corp
=====================================
Overall Score: 2.3 / 5.0 (Level 2: Repeatable)

Dimension Scores:
  Values & Mindset:       2/5 - Teams follow process but lack agile mindset
  Team Practices:         3/5 - Consistent Scrum ceremonies across teams
  Technical Excellence:   2/5 - Limited automation, manual testing prevalent
  Product Ownership:      2/5 - Feature-driven, not outcome-driven
  Leadership Support:     3/5 - Middle management supportive, exec sponsorship partial
  Continuous Improvement: 2/5 - Retrospectives happen but action items stall

Recommendation: Start with Scrum pilot on 2 willing teams.
Focus first on Technical Excellence and Product Ownership.
Target Level 3 within 6 months.
```

## Conflict Resolution Process

1. **Acknowledge** -- Recognize the conflict, create safe space, set ground rules
2. **Understand** -- Hear all perspectives, identify underlying needs, separate positions from interests
3. **Explore** -- Generate options, find common ground, build on shared interests
4. **Agree** -- Define acceptable solution, document agreements, set follow-up plan

## Stakeholder Management

| Stakeholder | Influence | Interest | Strategy |
|-------------|-----------|----------|----------|
| Executives | High | Variable | Align to business goals, show ROI |
| Middle Mgmt | High | Medium | Address concerns, show career path |
| Teams | Medium | High | Enable success, remove impediments |
| Customers | Medium | High | Show value delivery improvement |

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `maturity_scorer.py` | Score organizational agile maturity | `python scripts/maturity_scorer.py --assessment assessment.yaml` |
| `metrics_dashboard.py` | Generate team metrics dashboard | `python scripts/metrics_dashboard.py --team "Team Alpha"` |
| `retro_format.py` | Generate retrospective facilitation guide | `python scripts/retro_format.py --format sailboat` |
| `transformation_tracker.py` | Track transformation phase progress | `python scripts/transformation_tracker.py --phase pilot` |

## References

- `references/frameworks.md` -- Agile framework comparison and selection criteria
- `references/coaching_techniques.md` -- GROW model, coaching stances, intervention patterns
- `references/facilitation.md` -- Retrospective formats, workshop structures, conflict resolution
- `references/transformation.md` -- Transformation playbook with phase gates and success criteria
