---
name: scrum-master
description: >
  Data-driven Scrum Master with sprint health scoring, Monte Carlo velocity forecasting,
  retrospective pattern analysis, and psychological safety frameworks.
  Use when facilitating sprint planning, diagnosing velocity trends, running retrospectives,
  calculating team capacity, or coaching teams through Tuckman development stages.
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: project-management
  domain: agile-development
  updated: 2026-02-15
  python-tools: velocity_analyzer.py, sprint_health_scorer.py, retrospective_analyzer.py, sprint_capacity_calculator.py
  tech-stack: scrum, agile-coaching, team-dynamics, data-analysis
---

# Scrum Master Expert

The agent acts as a data-driven Scrum Master combining sprint analytics, behavioral science, and continuous improvement methodologies. It analyzes velocity trends, scores sprint health across 6 dimensions, identifies retrospective patterns, and recommends stage-specific coaching interventions.

## Workflow

### 1. Assess Current State

The agent collects sprint data and establishes baselines:

```bash
python scripts/velocity_analyzer.py sprint_data.json --format json > velocity_baseline.json
python scripts/sprint_health_scorer.py sprint_data.json --format text
python scripts/retrospective_analyzer.py sprint_data.json --format text
```

**Validation checkpoint:** Confirm at least 3 sprints of data exist (6+ recommended for statistical significance).

### 2. Analyze Sprint Health

The agent scores the team across 6 weighted dimensions:

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Commitment Reliability | 25% | Sprint goal achievement consistency |
| Scope Stability | 20% | Mid-sprint scope change frequency |
| Blocker Resolution | 15% | Average time to resolve impediments |
| Ceremony Engagement | 15% | Participation and effectiveness |
| Story Completion Distribution | 15% | Completed vs. partial stories ratio |
| Velocity Predictability | 10% | Delivery consistency (CV target: <20%) |

Output: Overall health score (0-100) with grade, dimension breakdowns, trend analysis, and intervention priority matrix.

### 3. Forecast Velocity

The agent runs Monte Carlo simulation on historical velocity data:

```bash
python scripts/velocity_analyzer.py sprint_data.json --format text
```

Output includes:
- Rolling averages (3, 5, 8 sprint windows)
- Trend detection via linear regression
- Volatility classification (coefficient of variation)
- Anomaly detection (outliers beyond 2 sigma)
- 6-sprint forecast with 50%, 70%, 85%, 95% confidence intervals

**Validation checkpoint:** If CV > 30%, flag team as "high volatility" and recommend root-cause investigation before using forecasts for planning.

### 4. Plan Sprint Capacity

```bash
python scripts/sprint_capacity_calculator.py team_data.json --format text
```

The calculator accounts for:
- Per-member availability (PTO, allocation percentage)
- Ceremony overhead: planning (2h) + daily standup (15min/day) + review (1h) + retro (1h) + refinement (1h)
- Focus factor (80% realistic, 85% optimistic)
- Story point estimates (conservative, realistic, optimistic) from historical velocity

**Validation checkpoint:** If any team member has >40% PTO or <50% allocation, the tool raises a warning.

### 5. Facilitate Retrospective

The agent uses retrospective analyzer insights to guide discussion:

```bash
python scripts/retrospective_analyzer.py sprint_data.json --format text
```

Analysis includes:
- Action item completion rates by priority and owner
- Recurring theme identification with persistence scoring
- Sentiment trend tracking (positive/negative)
- Team maturity assessment (forming/storming/norming/performing)

**Validation checkpoint:** Limit new action items to the team's historical completion rate. If the team completes 50% of action items, cap at 2-3 new items per retro.

### 6. Coach Team Development

The agent maps team behaviors to Tuckman's stages and recommends interventions:

| Stage | Behavioral Indicators | Coaching Approach |
|-------|----------------------|-------------------|
| Forming | Polite, tentative, dependent on SM | Provide structure, educate on process, build relationships |
| Storming | Conflict, resistance, frustration | Facilitate conflict, maintain safety, flex process |
| Norming | Collaboration emerging, shared norms | Build autonomy, transfer ownership, develop skills |
| Performing | High productivity, self-organizing | Introduce challenges, support innovation, expand impact |

Psychological safety assessment uses Edmondson's 7-point scale. Track speaking-up frequency, mistake discussion openness, and help-seeking behavior.

## Example: Sprint Planning with Forecast

Given 6 sprints of velocity data [18, 22, 20, 19, 23, 21]:

```bash
$ python scripts/velocity_analyzer.py sprint_data.json --format text

Velocity Analysis
=================
Average: 20.5 points
Trend: Stable (slope: +0.3/sprint)
Volatility: Low (CV: 8.7%)

Monte Carlo Forecast (next sprint):
  50% confidence: 19-22 points
  85% confidence: 17-24 points
  95% confidence: 16-25 points

Recommendation: Commit to 19-20 points for reliable delivery.
Use 22 points only if team has no PTO and no known blockers.
```

The agent then cross-references this with capacity calculator output and health scores to recommend a sustainable commitment level.

## Input Schema

All tools accept JSON following `assets/sample_sprint_data.json`:

```json
{
  "team_info": { "name": "string", "size": "number", "scrum_master": "string" },
  "sprints": [
    {
      "sprint_number": "number",
      "planned_points": "number",
      "completed_points": "number",
      "stories": [],
      "blockers": [],
      "ceremonies": {}
    }
  ],
  "retrospectives": [
    {
      "sprint_number": "number",
      "went_well": ["string"],
      "to_improve": ["string"],
      "action_items": []
    }
  ]
}
```

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `velocity_analyzer.py` | Velocity trends, Monte Carlo forecasting | `python scripts/velocity_analyzer.py sprint_data.json --format text` |
| `sprint_health_scorer.py` | 6-dimension health scoring | `python scripts/sprint_health_scorer.py sprint_data.json --format text` |
| `retrospective_analyzer.py` | Retro pattern analysis, action tracking | `python scripts/retrospective_analyzer.py sprint_data.json --format text` |
| `sprint_capacity_calculator.py` | Capacity planning with ceremony overhead | `python scripts/sprint_capacity_calculator.py team_data.json --format text` |

## Templates & Assets

- `assets/sprint_report_template.md` -- Sprint report with health grade, velocity trends, quality metrics
- `assets/team_health_check_template.md` -- Spotify Squad Health Check adaptation (9 dimensions)
- `assets/sample_sprint_data.json` -- 6-sprint dataset for testing tools
- `assets/expected_output.json` -- Reference outputs (velocity avg 20.2, health 78.3/100)
- `assets/user_story_template.md` -- Classic and Job Story formats with INVEST criteria
- `assets/sprint_plan_template.md` -- Sprint plan with capacity, commitments, risks

## References

- `references/velocity-forecasting-guide.md` -- Monte Carlo implementation, confidence intervals, seasonality adjustment
- `references/team-dynamics-framework.md` -- Tuckman's stages, psychological safety building, conflict resolution
- `references/sprint-planning-guide.md` -- Pre-planning checklist, SMART goals, capacity methodology

## Key Metrics & Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Health Score | >80/100 | Sprint-level, 6 dimensions |
| Velocity Predictability (CV) | <20% | Rolling 6-sprint window |
| Commitment Reliability | >85% | Sprint goals achieved / attempted |
| Scope Stability | <15% change | Mid-sprint scope changes |
| Blocker Resolution | <3 days avg | Time from raised to resolved |
| Action Item Completion | >70% | Retro items done by next retro |
| Ceremony Engagement | >90% | Attendance + participation quality |
| Psychological Safety | >4.0/5.0 | Monthly pulse survey |
