# Transformation Playbook

> Read this when designing or running a transformation: the 4-phase roadmap with phase gates, the four metric categories to track, a worked kickoff-assessment example, the troubleshooting table, and success criteria.

## Design Transformation Roadmap

The agent structures transformation in 4 phases:

1. **Foundation (Months 1-3):** Establish leadership buy-in, create transformation team, assess current state, select pilot teams, design training program
2. **Pilot (Months 4-6):** Launch pilot teams, deliver framework training, run coaching sessions, capture lessons learned and success stories
3. **Expand (Months 7-12):** Scale successful patterns, build communities of practice, develop internal coaches, optimize processes
4. **Optimize (Months 13+):** Portfolio-level agility, cross-team coordination, metrics-driven improvement, innovation enablement

**Validation checkpoint:** Each phase has explicit success criteria. Do not advance to the next phase until criteria are met.

## Track Metrics

The agent monitors four metric categories:

| Category | Metrics | Purpose |
|----------|---------|---------|
| Outcome | Customer satisfaction, time to market, revenue delivered | Business value |
| Process | Lead time, cycle time, throughput, WIP | Flow efficiency |
| Quality | Defect rate, tech debt, test coverage, deploy frequency | Technical health |
| Team | Happiness, psychological safety, engagement, sustainability | Team health |

```bash
python scripts/velocity_analyzer.py --sprints sprints.json      # Process: throughput trend and forecast
python scripts/team_health_checker.py --survey survey.json      # Team: health across 10 dimensions
```

Outcome and Quality metrics come from your product analytics and CI data; the skill has no tool that collects them.

**Validation checkpoint:** Review metrics monthly. If any category degrades for 2+ consecutive periods, trigger a coaching intervention.

## Example: Transformation Kickoff Assessment

`assessment.json` (`python scripts/agile_maturity_scorer.py --example` prints this template):

```json
{
  "organization": "Acme Corp",
  "teams_assessed": 5,
  "dimensions": {
    "values_and_mindset": 2,
    "team_practices": 3,
    "technical_excellence": 2,
    "product_ownership": 2,
    "leadership_support": 3,
    "continuous_improvement": 2
  }
}
```

```bash
$ python scripts/agile_maturity_scorer.py --assessment assessment.json


Agile Maturity Assessment: Acme Corp
Teams Assessed: 5
============================================================
Overall Score: 2.3 / 5.0 (Level 2: Repeatable)
  Basic Scrum/Kanban in place, team-level practices established, some metrics tracked.

Dimension Scores:
  Values & Mindset          2/5  [########------------]  Level 2: Repeatable
  Team Practices            3/5  [############--------]  Level 3: Defined
  Technical Excellence      2/5  [########------------]  Level 2: Repeatable
  Product Ownership         2/5  [########------------]  Level 2: Repeatable
  Leadership Support        3/5  [############--------]  Level 3: Defined
  Continuous Improvement    2/5  [########------------]  Level 2: Repeatable

Gap Analysis (target: Level 3):
  [Medium] Values & Mindset: 2 -> 3 (gap: 1.0)
  [Medium] Technical Excellence: 2 -> 3 (gap: 1.0)
  [Medium] Product Ownership: 2 -> 3 (gap: 1.0)
  [Medium] Continuous Improvement: 2 -> 3 (gap: 1.0)

...
```

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
