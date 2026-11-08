# Scrum Master Workflow & Operations

Read this when running the end-to-end Scrum Master workflow (assess → health → forecast → capacity → retro → coach), wiring up the tools, or preparing the JSON input schema.

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

`velocity_analyzer.py`, `sprint_health_scorer.py` and `retrospective_analyzer.py` accept JSON following `assets/sample_sprint_data.json` (below). `sprint_capacity_calculator.py` takes a different shape, a team roster: see `assets/sample_team_data.json` (`sprint_length_days`, `historical_velocity`, `team_members[]`).

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
