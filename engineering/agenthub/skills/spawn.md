# Sub-Skill: Spawn Agent

**Parent:** agenthub
**Trigger:** "spawn agent", "create agent instance", "start sub-agent"

## Purpose

Spawn an individual agent within a workflow. Prepares the agent's context, passes inputs from upstream agents, monitors execution, and captures outputs.

## Workflow

### Step 1: Prepare Context

Assemble the agent's execution context:
- Task description from the workflow definition
- Input data from upstream agent outputs
- Constraints: timeout, output format, quality expectations
- Relevant reference material (if specified)

### Step 2: Configure Agent

Set agent parameters:
```
Agent ID:       researcher-001
Task:           Research competitor landscape
Inputs:         { product_description: "..." }
Expected output: { competitor_list: [], market_size: {} }
Timeout:        300s
Retries:        1
```

### Step 3: Execute

Launch the agent and monitor:
- Start the agent with prepared context
- Track execution time
- Capture stdout/output as it streams
- Watch for timeout

### Step 4: Capture Output

On completion:
- Parse agent output into structured format
- Validate output matches expected schema
- Store in session state keyed by agent ID
- Transition state to COMPLETED

On failure:
- Capture error message and stack trace
- If retries remain, re-spawn with error context
- If no retries, transition to FAILED

### Step 5: Notify Orchestrator

Report back to the workflow engine:
- Agent state transition
- Output availability
- Duration and resource usage
- Quality signals (if evaluatable)

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Agent definition | Yes | From workflow definition |
| Upstream outputs | Yes | Data from completed dependencies |
| Session ID | Yes | Orchestration session reference |

## Outputs

- Agent output in structured format
- Execution metadata (duration, retries, state)
- Error details (if failed)
