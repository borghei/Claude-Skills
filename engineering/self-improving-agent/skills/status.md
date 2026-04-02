# Sub-Skill: Status

**Parent:** self-improving-agent
**Trigger:** "memory status", "learning progress", "how am I improving", "show improvement metrics"

## Purpose

Display the current state of the self-improvement system: memory size, rule counts, learning velocity, and improvement trends. Provides a dashboard view of agent learning progress.

## Workflow

### Step 1: Gather Metrics

Collect data from all improvement system components:

**Memory metrics:**
- Total entries in MEMORY.md
- Entries per topic file
- Line counts vs limits
- Oldest and newest entries

**Rule metrics:**
- Total promoted rules
- Rules by category
- Rules by age (fresh / aging / stale)
- Rules with/without "why" annotations

**Learning velocity:**
- Entries added in last 7 days
- Entries promoted in last 30 days
- Entries pruned in last 30 days
- Net growth rate

### Step 2: Compute Improvement Score

```
Improvement Score = (
  promoted_rules_30d * 0.3 +
  (1 - stale_entry_ratio) * 0.2 +
  first_attempt_success_delta * 0.3 +
  memory_health_score * 0.2
)
```

Where:
- `promoted_rules_30d`: Rules promoted in last 30 days (normalized 0-1)
- `stale_entry_ratio`: Fraction of entries classified as stale
- `first_attempt_success_delta`: Change in first-attempt success rate
- `memory_health_score`: 1.0 if under limits, decreasing with violations

### Step 3: Determine Maturity Level

Map to the improvement maturity model:
| Level | Name | Indicator |
|-------|------|-----------|
| 0 | Stateless | No MEMORY.md or empty |
| 1 | Recording | Entries exist, no promotions |
| 2 | Curating | Regular reviews, entries classified |
| 3 | Promoting | Active rule promotion pipeline |
| 4 | Extracting | Skills being extracted from patterns |
| 5 | Meta-Learning | Capture strategy adapting based on value |

### Step 4: Display Dashboard

```
Self-Improvement Status
========================
Maturity Level: 3 (Promoting)
Improvement Score: 0.72

Memory:    47 entries (187/200 lines)
Rules:     12 promoted (3 this month)
Velocity:  +8 entries, -3 pruned, +3 promoted (30d)

Health:    GOOD (no constraint violations)
Trend:     IMPROVING (first-attempt success +5% over 30d)
```

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Memory path | No | Defaults to ./MEMORY.md |
| Feedback log | No | Path to feedback data for trend analysis |

## Outputs

- Dashboard with current metrics
- Maturity level classification
- Improvement score with breakdown
- Trend direction (improving / stable / degrading)
- Recommended next actions
