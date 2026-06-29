---
name: agent-workflow-designer
description: >
  Design multi-agent orchestration with workflow DAGs, routing, handoff protocols, and state
  management. Use when building pipelines of specialized agents, designing fan-out/fan-in
  patterns, or implementing fault-tolerant workflows.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: ai-orchestration
  tier: POWERFUL
  updated: 2026-06-29
  frameworks: langgraph, crewai, autogen, claude-agent-teams
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

Before designing the workflow, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Workflow topology** — linear, parallel, tree/delegation, reactive, or consensus (selects which of the five orchestration patterns)
- [ ] **Framework target** — LangGraph, CrewAI, AutoGen, or Claude agent teams (determines the implementation code emitted)
- [ ] **Reliability & cost constraints** — failure tolerance and budget (drives circuit breakers, retries, timeouts, and model-tier routing)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/orchestration-patterns.md](references/orchestration-patterns.md)** — full implementations of all five patterns (LangGraph sequential pipeline, async fan-out/fan-in, hierarchical orchestrator with dependency batching, event bus, consensus validation). Read after picking a topology from the decision tree.
- **[references/routing-and-cost.md](references/routing-and-cost.md)** — intent-based router, context window budgeting (`ContextBudget`), and the cost optimization matrix. Read when deciding how requests reach agents and how to control spend.
- **[references/reliability-and-troubleshooting.md](references/reliability-and-troubleshooting.md)** — circuit breaker, common pitfalls, best practices, troubleshooting table, and success criteria. Read when hardening for production or diagnosing failures.
- **[references/subagent-scoping-and-orchestration.md](references/subagent-scoping-and-orchestration.md)** — when to split work into scoped subagents vs one loop; scoping a subagent (minimal tool allow-list, focused instructions, isolated context, return contract); the lead→parallel-specialists→merge pattern on a shared workspace; failure isolation/retries; and multi-agent vs single-agent cost/latency tradeoffs. Read when designing a lead that delegates to specialist subagents.

## Tools Overview

Stdlib-only Python CLIs in `scripts/` (run with `python3`, support `--json` and human-readable output):

- **`cost_estimator.py`** — per-step token/cost estimate for a workflow DAG with model-tier what-ifs.
- **`multi_agent_cost_estimator.py`** — compares a **lead + scoped subagents** design (per-role price tier, call counts, token sizes, reasoning-effort multiplier) against a **single strong agent** baseline, with a per-role breakdown and total-cost projection. Prices are user-supplied with neutral placeholder defaults — pass `--price tier=input/output` or a JSON `price_tiers` block with your real rates.
- **`workflow_validator.py`** / **`workflow_visualizer.py`** — validate and render workflow DAGs.

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
- Training or fine-tuning the underlying LLMs used by agents (see `engineering/ml-pipeline-architect` for ML training workflows)
- Infrastructure provisioning, container orchestration, or deployment pipelines (see `engineering/cloud-infrastructure-designer` for cloud architecture)
- Human-in-the-loop approval workflows or UI design for agent dashboards (see `product-team/ux-researcher` for user-facing workflow design)
- Long-term agent memory, vector database setup, or RAG pipeline construction (see `engineering/rag-pipeline-architect` for retrieval-augmented generation)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/ml-pipeline-architect` | Agent workflows that include ML inference stages use ML Pipeline Architect for model serving and batch prediction design | Workflow DAG exports stage specs to ML pipeline; ML pipeline returns inference endpoints for agent consumption |
| `engineering/rag-pipeline-architect` | Research and retrieval agents within workflows rely on RAG pipelines for grounded knowledge access | Agent sends queries to RAG pipeline; RAG returns ranked document chunks with citations for agent context |
| `engineering/cloud-infrastructure-designer` | Production deployment of agent workflows requires infrastructure design for scaling, queuing, and monitoring | Workflow resource requirements feed into infrastructure specs; infra returns endpoint URLs, queue ARNs, and scaling policies |
| `engineering/api-design-architect` | Inter-agent communication contracts and external API boundaries follow API design standards | Agent handoff schemas are validated against API design specs; API architect provides OpenAPI definitions for external integrations |
| `engineering/system-design-architect` | Overall system architecture decisions (sync vs async, monolith vs distributed) shape workflow topology choices | System design constraints (latency budgets, availability targets) inform pattern selection; workflow requirements feed back into system capacity planning |
| `project-management/technical-project-planning` | Complex multi-agent projects require structured planning for phased rollout, risk management, and milestone tracking | Workflow complexity estimates feed into project plans; PM skill provides sprint boundaries and dependency timelines for staged deployment |
