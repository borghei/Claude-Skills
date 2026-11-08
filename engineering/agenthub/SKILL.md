---
name: agenthub
description: >
  Runs a multi-agent job as a dependency graph: validates the DAG, tracks each agent's state on
  a board, then ranks and merges their outputs. Use when spawning parallel agents, monitoring a
  run, or merging results.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: ai-agents
  updated: 2026-11-08
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

Before designing the workflow, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task decomposition:** how the work splits into agent sub-tasks and their dependencies (defines the DAG nodes and edges in Init).
- **Parallelism budget:** how many agents may run concurrently (sets `max_parallel` scheduling).
- **Merge strategy:** synthesize, rank-select, or chain (determines how the Merge stage combines outputs).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

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

**Who does what.** The scripts never start an agent or call a model. You spawn agents with your platform's own mechanism (subagents, background tasks, separate sessions) and record each state change with `session_manager.py update`; the scripts validate the plan, keep the session file, draw the board and rank what came back. For design-time work (choosing a topology, pricing it) use `engineering/agent-workflow-designer`, whose `steps`/`depends_on` files this skill does not read.

## Quick Start Workflow

```bash
# 1. Validate the DAG: unknown dependencies, cycles, roots/terminals, inputs not covered by a dependency
python scripts/dag_analyzer.py --workflow assets/sample_workflow.json --validate --critical-path

# 2. Open a session file for the run (the global --json flag goes before the subcommand)
python scripts/session_manager.py create --workflow assets/sample_workflow.json --output /tmp/session.json

# 3. As each agent you spawned starts, finishes or fails, record it
python scripts/session_manager.py update --session /tmp/session.json --agent researcher --state RUNNING
python scripts/session_manager.py update --session /tmp/session.json --agent researcher --state COMPLETED \
    --eval-score 0.8 --output-data '{"competitor_list": "..."}'

# 4. Watch progress, then rank and merge the outputs
python scripts/board_manager.py --session assets/sample_session.json --view board
python scripts/result_ranker.py --session assets/sample_session.json --rank
python scripts/result_ranker.py --session assets/sample_session.json --merge rank-select
```

`assets/sample_session.json` is a run caught mid-way: three agents completed, `analyst` failed on a timeout and `writer` waits on it, so the board shows a blocked run and the ranker has three outputs to score. On the sample workflow the analyzer passes with one real warning: `analyst` reads `market_size` without depending on `researcher` directly.

**Tools overview.** `dag_analyzer.py` validates and reports parallel groups and the critical path (from per-agent `config.timeout`). `session_manager.py` has `create`, `status`, `update`, `history` and `list`. `board_manager.py` views are `board`, `timeline` and `summary`. `result_ranker.py` scores each output on completeness, depth, structure and any `eval_score`, then merges with `synthesize`, `rank-select` or `chain`. The ranker's score is a structural heuristic; read the top outputs before trusting the order.

**Exit codes.** `dag_analyzer.py`: `0` valid, `1` validation errors, `2` missing file, bad JSON or no `agents` object. The other three: `0` done, `2` missing or malformed session or workflow file.

**Done when:** the analyzer passes with no unexplained warnings, every agent in the session reached COMPLETED (or FAILED with a recorded reason and a decision on retry), and the merged output was read and checked against the workflow's terminal outputs.

## Anti-Patterns

### Parallel agents with overlapping scopes
**Mistake:** Two agents both "research the market", then the merge step has to reconcile contradictory duplicates.
**Why it happens:** Splitting by topic is easier than splitting by output.
**Instead:** Give each agent a distinct output contract (`outputs` in the workflow). If two agents would write the same field, merge them into one.

### Hidden data dependencies
**Mistake:** An agent reads an output from an agent it does not list as a dependency, so it can start before that output exists.
**Why it happens:** The dependency is indirect and looks implied.
**Instead:** Declare every producer you read from. `dag_analyzer.py` warns on exactly this case.

### Trusting the ranker blindly
**Mistake:** Shipping the top-ranked output without reading it.
**Why it happens:** A numeric score looks authoritative.
**Instead:** Use the rank to decide what to read first. Record a real `--eval-score` from your own check so the ranker weighs it.

## Files

- `scripts/dag_analyzer.py`, `scripts/session_manager.py`, `scripts/board_manager.py`, `scripts/result_ranker.py` — the four CLIs above.
- `assets/sample_workflow.json` — five-agent workflow (fan-out, fan-in); `assets/sample_session.json` — a partially failed run of it.
- `skills/*.md` — lifecycle sub-skills; `references/` — DAG format, patterns, operations.

## Reference Documentation

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

## See Also

- `engineering/agent-workflow-designer` — design-time topology, validation and cost before you run anything.
- `engineering/agent-designer` — roles and tool schemas for the agents that become DAG nodes.
- `engineering/observability-designer` — tracing and alerting for long-running agent jobs.
