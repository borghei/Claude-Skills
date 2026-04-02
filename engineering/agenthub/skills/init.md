# Sub-Skill: Initialize Workflow

**Parent:** agenthub
**Trigger:** "create multi-agent workflow", "design agent DAG", "initialize orchestration"

## Purpose

Create a new multi-agent workflow definition. Guides the user through decomposing a complex task into agent nodes, defining dependencies, and validating the resulting DAG.

## Workflow

### Step 1: Decompose the Task

Break the overall objective into discrete sub-tasks:
- Each sub-task should be completable by a single agent in one session
- Sub-tasks should have clear inputs and outputs
- Identify which sub-tasks can run in parallel vs must be sequential

### Step 2: Define Agents

For each sub-task, define an agent node:
```json
{
  "id": "agent-name",
  "task": "Clear description of what this agent does",
  "inputs": ["list of required inputs"],
  "outputs": ["list of produced outputs"],
  "dependencies": ["ids of agents that must complete first"],
  "config": {
    "timeout": 300,
    "retries": 1,
    "quality_threshold": 0.7
  }
}
```

### Step 3: Build Dependency Graph

Map the edges:
- Root nodes: agents with no dependencies (start first)
- Terminal nodes: agents with no dependents (feed into merge)
- Ensure every output needed by a downstream agent is produced by an upstream agent

### Step 4: Validate

Run `dag_analyzer.py` on the definition:
```bash
python scripts/dag_analyzer.py --workflow workflow.json --validate
```

Checks:
- No cycles in the graph
- All input references resolve to upstream outputs
- No orphaned nodes (unreachable from root or terminal)
- Critical path length is reasonable

### Step 5: Save Definition

Write the validated workflow definition to a JSON file for execution.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Task description | Yes | The overall objective to decompose |
| Max parallel | No | Maximum concurrent agents (default: 3) |
| Timeout | No | Per-agent timeout in seconds (default: 300) |

## Outputs

- Validated workflow definition (JSON)
- DAG visualization (text-based)
- Critical path analysis
- Estimated execution time
