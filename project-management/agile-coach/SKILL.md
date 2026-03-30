---
name: agile-coach
description: >
  Expert agile coaching for team transformation, framework selection, maturity
  assessment, and organizational change management. Use when selecting an agile
  framework for a team, coaching through Tuckman development stages,
  facilitating retrospectives, assessing organizational agile maturity, or
  designing a transformation roadmap.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-ops
  domain: agile
  updated: 2026-03-31
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

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Teams revert to waterfall habits after initial training | Coaching stance too directive; team never internalized agile values | Shift to facilitative coaching; run a "why agile" workshop focused on outcomes, not ceremonies |
| Velocity fluctuates wildly sprint to sprint | Inconsistent story pointing, scope changes mid-sprint, or unplanned work not tracked | Calibrate estimation with reference stories; track unplanned work separately; protect sprint scope |
| Retrospective action items never get implemented | Actions too vague, no owners, or no capacity reserved for improvements | Apply SMART criteria to retro actions; reserve 10-15% sprint capacity for improvement items |
| Leadership loses patience with transformation timeline | Unrealistic expectations set during Phase 1; no visible quick wins | Identify and publicize early wins within first 60 days; show leading indicators (cycle time, team satisfaction) before lagging indicators (revenue, quality) |
| Teams resist framework adoption | Change fatigue, lack of psychological safety, or imposed top-down mandate | Start with volunteer pilot teams; let success stories create pull rather than push; address fears openly |
| Agile maturity score plateaus at Level 2-3 | Focus on ceremonies over outcomes; technical practices neglected | Invest in engineering excellence (CI/CD, TDD, pair programming); shift metrics from output to outcomes |
| Cross-team coordination breaks down at scale | No explicit coordination mechanisms beyond team-level Scrum | Introduce Scrum-of-Scrums, communities of practice, or consider a lightweight scaling framework (LeSS, Nexus) |

## Success Criteria

- Team velocity stabilizes within +/-15% variance after 4 sprints of coaching engagement
- Agile maturity score improves by at least 1 full level within 6 months of sustained coaching
- Retrospective action item completion rate exceeds 70% per sprint
- Team NPS or satisfaction score (measured quarterly) trends upward over 3 consecutive periods
- Cycle time for standard work items decreases by 20%+ within the first quarter
- At least 80% of team members can articulate the purpose behind each ceremony they practice
- Leadership stakeholders rate transformation progress as "on track" or better in quarterly reviews

## Scope & Limitations

**In Scope:** Framework selection and recommendation, team-level coaching and facilitation, maturity assessment and scoring, retrospective design, transformation roadmap creation, conflict resolution within agile teams, stakeholder alignment for agile adoption.

**Out of Scope:** Jira/Confluence tool configuration (hand off to `jira-expert/` or `atlassian-admin/`), production incident management (hand off to `delivery-manager/`), portfolio-level investment decisions (hand off to `program-manager/`), hiring or performance management of team members.

**Limitations:** Maturity scoring is a point-in-time assessment that requires honest self-reporting; scores can be gamed. Framework recommendations are guidelines, not prescriptions -- every organization has unique constraints. Transformation timelines assume consistent leadership support; political changes can invalidate roadmaps.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `scrum-master/` | Bidirectional | Agile coach sets framework; Scrum Master executes sprint-level practices |
| `delivery-manager/` | Coach -> DM | Transformation roadmap milestones feed into delivery planning |
| `program-manager/` | Coach -> PgM | Scaling framework selection informs program governance structure |
| `jira-expert/` | Coach -> Jira | Board and workflow requirements derived from framework selection |
| `senior-pm/` | PM -> Coach | Portfolio priorities shape which teams get coaching focus first |
| `confluence-expert/` | Coach -> Confluence | Coaching artifacts (maturity reports, retro outcomes) documented in Confluence |
