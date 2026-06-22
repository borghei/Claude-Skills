---
name: agenthub
description: >
  Multi-agent DAG orchestration for workflows where AI agents collaborate via dependency
  graphs, covering agent spawning, output merging, and quality evaluation. Use when a task
  needs multiple specialized agents or to parallelize AI work.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: ai-agents
  updated: 2026-06-17
  tags: [multi-agent, orchestration, dag, workflow, parallel, agent-hub]
---
# AgentHub - Multi-Agent DAG Orchestration

AgentHub provides patterns and tools for orchestrating multiple AI agents as a directed acyclic graph (DAG). Instead of one agent doing everything sequentially, AgentHub lets you decompose complex tasks into sub-tasks, assign each to a specialized agent, define dependencies between them, and merge their outputs into a coherent result.

The core insight: complex tasks decompose better than they scale. A 10-step sequential task run by one agent hits context limits and quality degradation. Five parallel agents with clear scopes and a merge step produce better results faster.

## Core Capabilities

- **DAG workflow design** — model tasks as nodes with explicit input/output contracts and dependency edges.
- **Parallel execution** — topological sort, parallel groups, and `max_parallel` scheduling for real speedup.
- **Agent lifecycle** — spawn, monitor (board), and track states from PENDING through COMPLETED/FAILED.
- **Quality gates** — evaluate outputs against thresholds and rank competing results.
- **Output merging** — synthesize, rank-select, or chain terminal outputs into a coherent deliverable.

## When to Use

- A task needs multiple specialized agents with distinct scopes.
- You want to parallelize AI work that would otherwise run sequentially.
- A single agent hits context limits or quality degradation on a long task.
- You need quality gates and merge strategies across agent outputs.

## Clarify First

Before designing the workflow, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task decomposition** — how the work splits into agent sub-tasks and their dependencies (defines the DAG nodes and edges in Init)
- [ ] **Parallelism budget** — how many agents may run concurrently (sets `max_parallel` scheduling)
- [ ] **Merge strategy** — synthesize, rank-select, or chain (determines how the Merge stage combines outputs)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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

**Lifecycle:** Init defines the workflow DAG, Run orchestrates execution, Spawn creates individual agents, Board provides real-time visibility, Eval checks output quality, Merge combines results, and Status reports overall health (`Init → Run → Spawn (parallel) → Eval → Merge`, with `Board`/`Status` reading state throughout).

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `dag_analyzer.py` | Validate DAG definitions (cycles, unreachable nodes, critical path) | `python scripts/dag_analyzer.py --workflow workflow.json --validate --critical-path` |
| `session_manager.py` | Manage orchestration sessions and state | `python scripts/session_manager.py create --json` |
| `board_manager.py` | Manage agent task boards with status tracking | `python scripts/board_manager.py --session session.json --view board` |
| `result_ranker.py` | Rank and merge outputs from multiple agents | `python scripts/result_ranker.py --session session.json --rank --merge synthesize` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/orchestration-core.md](references/orchestration-core.md)** — workflow DAG concepts, the full workflow-definition JSON format, agent states, execution strategy, the define/execute/evaluate workflows, and the common DAG patterns (fan-out/fan-in, pipeline, reducer, validator chain). Read when designing or running a workflow.
- **[references/multi-agent-patterns.md](references/multi-agent-patterns.md)** — the deep pattern catalog (fan-out/fan-in, pipeline, reducer, validator chain, map-reduce, diamond dependency), agent design principles, quality-gate patterns, failure handling, scaling table, and metrics targets. Read when choosing a pattern or designing quality gates and failure handling.
- **[references/operations-and-quality.md](references/operations-and-quality.md)** — best practices, common pitfalls, troubleshooting table, and success criteria. Read when debugging a workflow or validating it against the quality bar.

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
