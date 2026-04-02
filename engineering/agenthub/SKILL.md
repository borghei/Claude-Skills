---
name: agenthub
description: >
  Multi-agent DAG orchestration framework. Design, execute, and manage workflows
  where multiple AI agents collaborate on complex tasks with dependency graphs.
  Covers agent spawning, output merging, quality evaluation, and real-time status
  boards. Use when a task requires multiple specialized agents working in concert,
  or when you need to parallelize AI work across sub-tasks.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-agents
  updated: 2026-04-02
  tags: [multi-agent, orchestration, dag, workflow, parallel, agent-hub]
---
# AgentHub - Multi-Agent DAG Orchestration

**Category:** Engineering / AI Agents
**Maintainer:** Claude Skills Team

## Overview

AgentHub provides patterns and tools for orchestrating multiple AI agents as a directed acyclic graph (DAG). Instead of one agent doing everything sequentially, AgentHub lets you decompose complex tasks into sub-tasks, assign each to a specialized agent, define dependencies between them, and merge their outputs into a coherent result.

The core insight: complex tasks decompose better than they scale. A 10-step sequential task run by one agent hits context limits and quality degradation. Five parallel agents with clear scopes and a merge step produce better results faster.

## Sub-Skills

This skill uses compound sub-skill architecture. Each sub-skill in `skills/` handles a stage of the orchestration lifecycle:

| Sub-Skill | File | Purpose |
|-----------|------|---------|
| **Init** | `skills/init.md` | Initialize a multi-agent workflow definition |
| **Run** | `skills/run.md` | Execute a defined workflow end-to-end |
| **Spawn** | `skills/spawn.md` | Spawn individual agents within a workflow |
| **Board** | `skills/board.md` | Dashboard showing agent status and progress |
| **Eval** | `skills/eval.md` | Evaluate agent outputs for quality and consistency |
| **Merge** | `skills/merge.md` | Merge outputs from multiple agents into final result |
| **Status** | `skills/status.md` | Show workflow execution status and health |

### Sub-Skill Flow

```
Init ──> Run ──> Spawn (parallel) ──> Eval ──> Merge
                      │                            │
                    Board ◄──── Status ◄───────────┘
```

**Lifecycle:** Init defines the workflow DAG, Run orchestrates execution, Spawn creates individual agents, Board provides real-time visibility, Eval checks output quality, Merge combines results, and Status reports overall health.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/dag_analyzer.py` | Analyze DAG definitions for cycles, unreachable nodes, and bottlenecks |
| `scripts/board_manager.py` | Manage agent task boards with status tracking |
| `scripts/result_ranker.py` | Rank and merge outputs from multiple agents |
| `scripts/session_manager.py` | Manage orchestration sessions and state |

## Core Concepts

### Workflow DAG

A workflow is a directed acyclic graph where:
- **Nodes** are agent tasks with a defined scope, inputs, and expected outputs
- **Edges** are dependencies: agent B cannot start until agent A completes
- **Root nodes** have no dependencies and start immediately
- **Terminal nodes** have no dependents and feed into the merge step

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Research  │────>│ Analysis │────>│  Merge   │
│  Agent    │     │  Agent   │     │  Agent   │
└──────────┘     └──────────┘     └──────────┘
                       ▲
┌──────────┐           │
│ Data      │──────────┘
│ Agent     │
└──────────┘
```

### Workflow Definition Format

```json
{
  "name": "market-analysis",
  "description": "Comprehensive market analysis for product launch",
  "agents": {
    "researcher": {
      "task": "Research competitor landscape and market size",
      "inputs": ["product_description"],
      "outputs": ["competitor_list", "market_size"],
      "dependencies": []
    },
    "data_collector": {
      "task": "Collect pricing and feature data from competitors",
      "inputs": ["competitor_list"],
      "outputs": ["pricing_data", "feature_matrix"],
      "dependencies": ["researcher"]
    },
    "analyst": {
      "task": "Analyze positioning opportunities and pricing strategy",
      "inputs": ["pricing_data", "feature_matrix", "market_size"],
      "outputs": ["positioning_report", "pricing_recommendation"],
      "dependencies": ["data_collector", "researcher"]
    },
    "writer": {
      "task": "Write executive summary combining all findings",
      "inputs": ["positioning_report", "pricing_recommendation"],
      "outputs": ["executive_summary"],
      "dependencies": ["analyst"]
    }
  },
  "config": {
    "max_parallel": 3,
    "timeout_per_agent": 300,
    "retry_on_failure": true,
    "quality_threshold": 0.7
  }
}
```

### Agent States

| State | Description |
|-------|-------------|
| `PENDING` | Waiting for dependencies to complete |
| `READY` | All dependencies met, queued for execution |
| `RUNNING` | Currently executing |
| `COMPLETED` | Finished successfully |
| `FAILED` | Failed after all retries |
| `SKIPPED` | Skipped due to upstream failure |
| `EVALUATING` | Output being evaluated for quality |

### Execution Strategy

1. **Topological sort** the DAG to determine execution order
2. **Identify parallel groups**: nodes with no inter-dependencies run simultaneously
3. **Execute root nodes** first (no dependencies)
4. **Chain results**: completed node outputs become inputs for dependents
5. **Evaluate outputs** at quality gates
6. **Merge terminal outputs** into final result

## Workflows

### Workflow 1: Define and Validate

```
1. Define agents with tasks, inputs, outputs, dependencies
2. Run dag_analyzer.py to validate:
   - No cycles in the dependency graph
   - All referenced inputs are produced by upstream agents
   - No unreachable nodes
   - Critical path length is acceptable
3. Estimate execution time based on agent count and dependencies
```

### Workflow 2: Execute Orchestration

```
1. Load workflow definition
2. Initialize session (session_manager.py)
3. Topological sort to determine execution order
4. For each parallel group:
   a. Spawn agents (up to max_parallel)
   b. Monitor progress on board
   c. Collect outputs on completion
   d. Evaluate outputs against quality threshold
5. Pass outputs to downstream agents as inputs
6. Merge final outputs
7. Generate execution report
```

### Workflow 3: Evaluate and Iterate

```
1. Collect all agent outputs
2. Run quality evaluation (eval sub-skill)
3. Rank outputs by quality score (result_ranker.py)
4. If any output below threshold:
   a. Retry the agent with adjusted instructions
   b. Or flag for human review
5. Merge passing outputs into final result
```

## Common Patterns

### Fan-Out / Fan-In

Multiple independent agents work in parallel, then a single agent merges results:
```
Task A ──┐
Task B ──┼──> Merge
Task C ──┘
```

### Pipeline

Sequential agents where each transforms the previous output:
```
Extract ──> Transform ──> Load ──> Validate
```

### Reducer

Multiple agents produce competing outputs, ranked and best one selected:
```
Agent 1 ──┐
Agent 2 ──┼──> Rank ──> Best Output
Agent 3 ──┘
```

### Validator Chain

Each agent validates the previous agent's work:
```
Generate ──> Review ──> Fix ──> Approve
```

## Best Practices

1. **Small, focused agent scopes** -- each agent should have a single clear objective
2. **Explicit inputs/outputs** -- never rely on implicit shared state between agents
3. **Quality gates between stages** -- evaluate before passing outputs downstream
4. **Timeout per agent** -- prevent runaway agents from blocking the workflow
5. **Retry with context** -- when retrying a failed agent, include the failure reason
6. **Merge strategy documented** -- how competing or complementary outputs combine
7. **Critical path awareness** -- optimize the longest dependency chain first
8. **Idempotent agents** -- agents should produce the same output given the same input

## Common Pitfalls

| Pitfall | Why It Happens | Fix |
|---------|---------------|-----|
| Cycle in DAG | Agent A depends on B which depends on A | Run dag_analyzer.py before execution |
| Output format mismatch | Agent B expects JSON, Agent A produces markdown | Define explicit output schemas per agent |
| Single bottleneck agent | One agent depends on everything | Restructure DAG to parallelize dependencies |
| Lost context between agents | Outputs too terse for downstream use | Require structured output with context preservation |
| Quality degradation in merge | Naive concatenation loses coherence | Use a dedicated merge agent with synthesis instructions |
| Runaway execution time | No timeouts, retry loops | Set timeout_per_agent and max retries |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Workflow hangs at agent N | Dependency not met or agent timeout | Check board for PENDING agents; verify upstream completed; check timeout config |
| Merged output is incoherent | No merge strategy defined | Use the merge sub-skill with explicit synthesis instructions |
| Agent produces wrong format | Input/output contract unclear | Define JSON schemas for agent inputs and outputs |
| DAG validation fails with cycle | Circular dependency in definition | Use dag_analyzer.py to identify the cycle; restructure the dependency chain |
| Quality eval fails everything | Threshold too strict for task complexity | Lower threshold or add a revision step before eval |

## Success Criteria

- **DAG validation passes** on every workflow definition before execution
- **Parallel execution utilization above 60%** -- agents running in parallel most of the time
- **Quality gate pass rate above 80%** -- agent outputs meet threshold on first attempt
- **End-to-end execution time within 2x critical path** -- parallelization delivers real speedup
- **Zero lost outputs** -- every agent's output is captured and available for merge/review
- **Merge coherence score above 0.7** -- final merged output reads as a unified deliverable

## Scope and Limitations

**This skill covers:**
- Multi-agent workflow design with DAG dependency graphs
- Agent spawning, monitoring, and lifecycle management
- Output quality evaluation and ranking
- Result merging strategies for coherent final deliverables

**This skill does NOT cover:**
- Individual agent design or prompt engineering (see `agent-designer`)
- Agent memory and self-improvement (see `self-improving-agent`)
- Infrastructure for running agents (compute, scheduling, deployment)
- Real-time streaming communication between agents

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `agent-designer` | Defines individual agent capabilities that become DAG nodes | Agent specs flow in; execution results flow back for agent tuning |
| `self-improving-agent` | Each agent can use self-improvement patterns to get better | Session feedback from orchestration feeds into agent learning loops |
| `prompt-engineer-toolkit` | Agent task prompts benefit from prompt engineering | Optimized prompts improve individual agent quality within the DAG |
| `context-engine` | Manages what context each agent sees | Context retrieval provides relevant inputs to each spawned agent |
| `observability-designer` | Monitors workflow execution and agent health | Agent state transitions and timing metrics feed into dashboards |
