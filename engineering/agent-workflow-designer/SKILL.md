---
name: agent-workflow-designer
description: >
  Designs multi-agent workflow DAGs (routing, hand-offs, state, retries) and validates and costs
  them before build. Use when planning a pipeline of specialised agents, fan-out/fan-in, or a
  lead with subagents.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: ai-orchestration
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: langgraph, crewai, autogen, claude-agent-teams
  tags:
    - multi-agent
    - orchestration
    - workflow-dag
    - routing
    - handoffs
    - state-management
---
# Agent Workflow Designer

The agent designs multi-agent orchestration systems using five core patterns: sequential pipeline, parallel fan-out/fan-in, hierarchical delegation, event-driven reactor, and consensus validation. It implements agent routing strategies, circuit breaker reliability patterns, context window budgeting, and cost optimization across LangGraph, CrewAI, AutoGen, and Claude Code agent teams.

## Core Capabilities

- **Pattern selection & design** — sequential pipelines, parallel fan-out/fan-in, hierarchical delegation, event-driven reactors, consensus validation
- **Agent routing** — intent-based, skill-based, cost-aware, load-balanced, and fallback-chain routing
- **State & context management** — persistent workflow state, context budgeting, checkpoint/resume, conflict resolution
- **Reliability engineering** — circuit breakers, retry with backoff, dead letter queues, timeout enforcement, idempotency

## When to Use

- Building multi-step AI pipelines that exceed one agent's capability
- Parallelizing research, analysis, or generation tasks
- Creating specialist agent teams with defined roles and contracts
- Designing fault-tolerant AI workflows for production deployment
- Optimizing cost across workflows with mixed model tiers

## Clarify First

Before designing the workflow, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Workflow topology:** linear, parallel, tree/delegation, reactive, or consensus (selects which of the five orchestration patterns).
- **Framework target:** LangGraph, CrewAI, AutoGen, or Claude agent teams (determines the implementation code emitted).
- **Reliability & cost constraints:** failure tolerance and budget (drives circuit breakers, retries, timeouts, and model-tier routing).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Pattern Selection Decision Tree

```
What does the workflow look like?
│
├─ Linear: step A feeds step B feeds step C
│  └─ SEQUENTIAL PIPELINE
│     Best for: content pipelines, code review chains, data transformation
│
├─ Parallel: N independent tasks, then combine
│  └─ FAN-OUT / FAN-IN
│     Best for: competitive research, multi-source analysis, parallel code gen
│
├─ Tree: orchestrator breaks work into subtasks dynamically
│  └─ HIERARCHICAL DELEGATION
│     Best for: complex projects, open-ended research, code generation with planning
│
├─ Reactive: agents respond to events/triggers
│  └─ EVENT-DRIVEN REACTOR
│     Best for: monitoring, alerting, continuous integration, chat workflows
│
└─ Verification: multiple agents must agree on output
   └─ CONSENSUS VALIDATION
      Best for: high-stakes decisions, code review, fact checking, safety-critical output
```

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/orchestration-patterns.md](references/orchestration-patterns.md)** — full implementations of all five patterns (LangGraph sequential pipeline, async fan-out/fan-in, hierarchical orchestrator with dependency batching, event bus, consensus validation). Read after picking a topology from the decision tree.
- **[references/routing-and-cost.md](references/routing-and-cost.md)** — intent-based router, context window budgeting (`ContextBudget`), and the cost optimization matrix. Read when deciding how requests reach agents and how to control spend.
- **[references/reliability-and-troubleshooting.md](references/reliability-and-troubleshooting.md)** — circuit breaker, common pitfalls, best practices, troubleshooting table, and success criteria. Read when hardening for production or diagnosing failures.
- **[references/subagent-scoping-and-orchestration.md](references/subagent-scoping-and-orchestration.md)** — when to split work into scoped subagents vs one loop; scoping a subagent (minimal tool allow-list, focused instructions, isolated context, return contract); the lead→parallel-specialists→merge pattern on a shared workspace; failure isolation/retries; and multi-agent vs single-agent cost/latency tradeoffs. Read when designing a lead that delegates to specialist subagents.

## Quick Start Workflow

Design time only: these tools check and price a workflow file; they run no agents. To track a
live multi-agent run (spawned agents, a board, ranked results) use `engineering/agenthub`, which
reads its own `agents`/`dependencies` format rather than the `steps`/`depends_on` format below.

```bash
# 1. Validate the DAG: cycles, missing dependencies, unreachable steps, dead ends, duplicate ids
python3 scripts/workflow_validator.py assets/sample_workflow.json            # exit 0, VALID
python3 scripts/workflow_validator.py assets/sample_workflow_flawed.json     # exit 1, 4 errors

# 2. Draw it (Mermaid) with detected patterns; --annotate-models / --annotate-cost add labels
python3 scripts/workflow_visualizer.py assets/sample_workflow.json --annotate-models

# 3a. Price the step DAG per run and over N runs, with what-if model swaps
python3 scripts/cost_estimator.py assets/sample_workflow.json --runs 1000 --prices assets/sample_prices.json
python3 scripts/cost_estimator.py assets/sample_workflow.json --override-model claude-haiku-5-5

# 3b. Or compare a lead + scoped subagents topology against one strong agent
python3 scripts/multi_agent_cost_estimator.py --file assets/sample_multi_agent_design.json
```

**Tools overview: which estimator.** Use `cost_estimator.py` when you have the step DAG and per-step token
estimates (`estimated_input_tokens`, `estimated_output_tokens`, optional `cached_input_tokens`,
`parallel_branches`, `retry_probability`). Use `multi_agent_cost_estimator.py` earlier, when the
question is whether to split into subagents at all; it works on roles, call counts and price tiers.

**Prices.** Neither tool ships a provider price list, because prices change faster than the skill.
`cost_estimator.py` prices each model at your `--prices` rate (JSON `{"model-id": {"input", "output",
"cached_input"}}` per 1M tokens; `assets/sample_prices.json` holds illustrative numbers only) and
otherwise at a placeholder rate for the tier its name suggests, and says so in the output.
`multi_agent_cost_estimator.py` takes `--price tier=input/output`. Copy current rates from the
provider's pricing page before quoting a dollar figure.

**Exit codes.** `workflow_validator.py`: `0` valid, `1` structural errors, `2` unreadable or
malformed input. The other three: `0` report printed, `2` unreadable or malformed input. All
accept `--json` and `--stdin`.

**Done when** this checklist holds:
1. `workflow_validator.py` exits 0 on the final workflow file.
2. Every step has an owner agent, a timeout and a retry or fallback rule.
3. The hand-off contract between steps (fields, types, done condition) is written down.
4. The cost for the expected run volume, at real rates, is within budget.

## Anti-Patterns

### Agents for every verb
**Mistake:** A pipeline of seven agents where three would do, each hand-off losing context.
**Why it happens:** Splitting by verb ("research", "outline", "draft", "edit") feels like good design.
**Instead:** Split only where tools, permissions or parallelism differ. Run `multi_agent_cost_estimator.py`; keep the single loop if the split is not clearly cheaper or faster.

### Hand-offs as free text
**Mistake:** Each agent passes the next one a paragraph of prose and hopes it contains what is needed.
**Why it happens:** Free text works in the demo.
**Instead:** Define a small return contract per step (fields, types, what "done" means) and validate it before the next step runs.

### No failure path
**Mistake:** A fan-out with no timeout, so one hung branch stalls the whole run, and no rule for partial results.
**Why it happens:** Happy-path demos never hang.
**Instead:** Give every step a timeout, a bounded retry and a fallback; decide up front whether fan-in proceeds with N-1 results.

## Files

- `scripts/workflow_validator.py`, `scripts/workflow_visualizer.py`, `scripts/cost_estimator.py`, `scripts/multi_agent_cost_estimator.py` — the four CLIs above.
- `assets/sample_workflow.json` (valid), `assets/sample_workflow_flawed.json` (cycle + missing dependency), `assets/sample_multi_agent_design.json`, `assets/sample_prices.json`.
- `references/` — pattern implementations, routing and cost, reliability, subagent scoping.

## Common Patterns

- **Scoped subagents** — split a job into specialists only where responsibilities are genuinely independent; give each a minimal tool allow-list, one-job instructions, an isolated context, and a small return contract, then merge their contracts in the lead on a shared workspace (see `references/subagent-scoping-and-orchestration.md`).
- **Multi-model routing** — run the orchestrator on a stronger tier and narrow subagents on cheaper tiers, matching reasoning effort to each role; estimate both topologies with `scripts/multi_agent_cost_estimator.py` before committing, and keep the single loop if the multi-agent design isn't meaningfully cheaper or faster.

## Scope & Limitations

**This skill covers:**
- Design and implementation of five core multi-agent orchestration patterns (sequential, parallel, hierarchical, event-driven, consensus)
- Agent routing strategies including intent-based, skill-based, and cost-aware routing
- Reliability engineering patterns: circuit breakers, retries, timeouts, and dead letter queues
- Context window budgeting, cost optimization, and framework-specific implementations (LangGraph, CrewAI, AutoGen)

**This skill does NOT cover:**
- Running or tracking live agent sessions (see `engineering/agenthub`)
- Choosing agent roles, architecture pattern and tool schemas from requirements (see `engineering/agent-designer`)
- Training or fine-tuning the underlying models (see `engineering/senior-ml-engineer`)
- Retrieval pipelines and vector stores for research agents (see `engineering/rag-architect`)
- Infrastructure for hosting the workflow (see `engineering/senior-cloud-architect`)

## See Also

- `engineering/agent-designer` — architecture pattern and roles that feed this DAG.
- `engineering/agenthub` — run-time board and result ranking for the agents designed here.
- `engineering/agent-protocol` — message and tool schema formats for the hand-offs.
- `engineering/batch-api-orchestrator` — when a step is a large offline batch rather than a live call.
