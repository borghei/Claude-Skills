# Sub-Skill: Execute Workflow

**Parent:** agenthub
**Trigger:** "run workflow", "execute the agents", "start orchestration"

## Purpose

Execute a validated workflow definition end-to-end. Manages the execution lifecycle including agent spawning, dependency resolution, output passing, and final merge.

## Workflow

### Step 1: Load and Validate

Load the workflow definition and run a final validation pass. Ensure all dependencies are satisfiable and configurations are complete.

### Step 2: Initialize Session

Create an orchestration session using `session_manager.py`:
```bash
python scripts/session_manager.py create --workflow workflow.json
```

This creates a session record tracking:
- Session ID and start time
- Agent states (all start as PENDING)
- Output storage locations
- Execution log

### Step 3: Execute Topological Order

Process agents in dependency order:
1. Identify all READY agents (dependencies met)
2. Spawn up to `max_parallel` agents simultaneously
3. Monitor running agents for completion or timeout
4. On completion: store output, update state, check dependents
5. On failure: retry if configured, or mark FAILED and SKIP dependents

### Step 4: Pass Outputs

When an agent completes:
- Validate output format matches the declared schema
- Store output in session state
- Check if any PENDING agents now have all dependencies met
- Transition those agents to READY

### Step 5: Final Merge

When all terminal agents complete:
- Collect their outputs
- Invoke the merge sub-skill (or merge agent if defined)
- Produce the final combined result

### Step 6: Report

Generate an execution report:
- Total wall-clock time
- Per-agent execution times
- Parallelization efficiency
- Quality scores if eval was run
- Any failures or retries

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Workflow file | Yes | Path to validated workflow JSON |
| Input data | Yes | Initial inputs for root agents |
| Dry run | No | Simulate without actually executing |

## Outputs

- Final merged result
- Per-agent outputs
- Execution report with timing and quality metrics
- Session record for audit trail
