# Sub-Skill: Workflow Status

**Parent:** agenthub
**Trigger:** "workflow status", "orchestration health", "how is the run going"

## Purpose

Report the overall status and health of a workflow execution. Provides a compact summary of progress, timing, failures, and estimated completion.

## Workflow

### Step 1: Load Session

```bash
python scripts/session_manager.py status --session <session-id>
```

### Step 2: Compute Metrics

| Metric | Calculation |
|--------|-------------|
| Progress | completed_agents / total_agents * 100% |
| Elapsed time | now - session_start |
| Est. remaining | critical_path_remaining * avg_agent_duration |
| Parallelization | time_agents_ran_parallel / total_agent_time |
| Failure rate | failed_agents / attempted_agents |
| Quality avg | mean(eval_scores) for completed agents |

### Step 3: Determine Health

| Condition | Health Status |
|-----------|--------------|
| All agents on track, no failures | HEALTHY |
| Minor delays but progressing | DEGRADED |
| Agent failed, retrying | AT_RISK |
| Multiple failures, blocked | CRITICAL |
| All agents complete | COMPLETE |

### Step 4: Display Status

```
Workflow Status: market-analysis
Session: abc123
Health: HEALTHY

Progress: ████████░░░░░░░░ 50% (2/4 agents)
Elapsed:  3m 15s
Est. remaining: 4m 00s

Agents:
  researcher      COMPLETED  1m 30s
  data_collector  COMPLETED  1m 45s
  analyst         RUNNING    0m 30s...
  writer          PENDING    (waiting: analyst)

Quality: 0.85 avg (2 evaluated)
Failures: 0
Retries: 0
```

### Step 5: Recommendations

If health is not HEALTHY:
- Suggest timeout adjustments
- Identify bottleneck agents
- Recommend retry or skip strategies

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Session ID | Yes | Active orchestration session |
| Verbose | No | Show per-agent details (default: summary) |

## Outputs

- Health status with color indicator
- Progress percentage and agent counts
- Timing breakdown (elapsed, estimated remaining)
- Quality metrics
- Actionable recommendations (if issues detected)
