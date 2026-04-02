# Sub-Skill: Agent Board

**Parent:** agenthub
**Trigger:** "show board", "agent dashboard", "workflow progress"

## Purpose

Display a real-time dashboard of agent status within a running workflow. Shows which agents are pending, running, completed, or failed, along with timing and dependency information.

## Workflow

### Step 1: Load Session State

Read the current session from `session_manager.py`:
```bash
python scripts/board_manager.py --session <session-id> --view board
```

### Step 2: Render Board

Display a visual board organized by execution stage:

```
AgentHub Board - Session: abc123
Workflow: market-analysis
Started: 2026-04-02 10:30:00 | Elapsed: 2m 15s

COMPLETED (2)           RUNNING (1)            PENDING (1)
───────────────         ───────────────        ───────────────
[x] researcher          [>] data_collector     [ ] analyst
    1m 30s                  0m 45s...              waiting on:
    2 outputs                                      data_collector

QUEUE: analyst (ready when data_collector completes)
CRITICAL PATH: researcher -> data_collector -> analyst -> writer (est. 8m)
```

### Step 3: Show Details (Optional)

Drill into a specific agent:
```bash
python scripts/board_manager.py --session <session-id> --agent researcher --detail
```

Shows:
- Agent task description
- Input data received
- Output data produced
- Execution log/timeline
- Retries (if any)

### Step 4: Refresh

Board auto-updates as agents change state. In non-interactive mode, produces a snapshot.

## Display Modes

| Mode | Description |
|------|-------------|
| `board` | Kanban-style columns by state |
| `timeline` | Gantt-style timeline view |
| `graph` | DAG visualization with state colors |
| `summary` | One-line-per-agent compact view |

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Session ID | Yes | Active orchestration session |
| View mode | No | board, timeline, graph, or summary (default: board) |
| Agent ID | No | Specific agent to detail |

## Outputs

- Visual board display
- Per-agent status details
- Timing estimates for remaining work
