---
name: agent-designer
description: >
  Designs multi-agent system architectures with orchestration patterns, tool
  schemas, and performance evaluation. Use when building AI agent systems,
  designing agent workflows, creating tool schemas, or evaluating agent
  performance.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: ai-agents
  tier: POWERFUL
  updated: 2026-11-08
  tags:
    - ai-agents
    - multi-agent
    - orchestration
    - tool-schemas
    - agent-evaluation
---
# Agent Designer - Multi-Agent System Architecture

A toolkit for designing, architecting, and evaluating multi-agent systems. It provides structured approaches to agent architecture patterns, tool design principles, communication strategies, and performance evaluation frameworks for building robust, scalable AI agent systems.

## Core Capabilities

- **Architecture pattern selection** — single agent, supervisor, swarm, hierarchical, and pipeline patterns with use-case fit and trade-offs.
- **Agent role definition** — identity, responsibilities, capabilities, interfaces, and constraints; common archetypes (coordinator, specialist, interface, monitor).
- **Tool design** — schema design, error handling, idempotency requirements, and validation rules.
- **Communication & orchestration** — message passing, shared state, event-driven architecture; centralized, decentralized, and hybrid orchestration.
- **Guardrails & safety** — input validation, output filtering, and human-in-the-loop checkpoints.
- **Evaluation frameworks** — task completion, quality, cost, and latency metrics with bottleneck analysis.
- **Memory, scaling & failure handling** — short/long/shared memory, horizontal/vertical scaling, retries, fallbacks, and circuit breakers.

## When to Use

- Building AI agent systems or designing multi-agent workflows.
- Creating tool schemas for OpenAI function calling or Anthropic tool use.
- Selecting an architecture pattern for a new system.
- Evaluating agent performance from execution logs.

## Clarify First

Before designing the system, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **System goal & scale:** the task the agents perform and expected load (drives which architecture pattern: single, supervisor, swarm, hierarchical, or pipeline).
- **Tool protocol target:** OpenAI function calling vs Anthropic tool use (sets the schema format `tool_schema_generator.py` emits).
- **Optimization priority:** cost, latency, or quality (determines agent roles, model tiers, and which metrics the evaluator weights).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

Run from the skill folder. Without `-o` nothing is written to disk: each tool prints its summary (and `--validate` results) to stdout, or with `--format json` the full JSON report. `-o PREFIX` additionally writes `PREFIX.json` (and, with `--format both`, the extra files listed below), so point the prefix at a scratch directory. Progress lines go to stderr.

```bash
# 1. Pick a pattern, roles and topology from requirements (writes <prefix>.json, _diagram.mmd, _roadmap.json)
python scripts/agent_planner.py assets/sample_system_requirements.json -o /tmp/arch --format both

# 2. Generate OpenAI and Anthropic tool schemas and check each one has properties and validation rules
python scripts/tool_schema_generator.py assets/sample_tool_descriptions.json -o /tmp/tools --format both --validate

# 3. Evaluate a run from execution logs: success rate, latency, cost, error patterns, bottlenecks
python scripts/agent_evaluator.py assets/sample_execution_logs.json -o /tmp/perf --format both --detailed
```

| Tool | Input | What it gives you |
|------|-------|-------------------|
| `agent_planner.py` | requirements JSON (goal, tasks, constraints, team) | pattern choice with rationale, agent roles, communication links, Mermaid diagram, phased roadmap |
| `tool_schema_generator.py` | `{"tools": [...]}` descriptions | `_openai.json` (function objects: wrap each as `{"type": "function", "function": ...}`), `_anthropic.json`, examples, validation notes |
| `agent_evaluator.py` | `{"execution_logs": [...]}` with per-task `cost_usd`, `duration_ms`, status, errors | health verdict, per-agent metrics, error patterns, bottlenecks, ranked recommendations |

Costs come only from the `cost_usd` field in the logs; the evaluator carries no model price list, so its numbers never go stale.

**Exit codes (all three):** `0` output written; `2` the input file is missing, is not valid JSON, is not a JSON object, or holds no usable records. These are generators, not gates: a POOR health verdict still exits 0, so read the report.

**Done when:** the chosen pattern is justified against the requirements (not just the planner's default), every tool schema has typed, described parameters and passes `--validate`, and the evaluator run on real logs has no unexplained critical bottleneck. Review the planner's topology by hand: a swarm of up to four agents is a full mesh; larger swarms get a ring of neighbour links (12 links for the six-agent sample, not 30).

## Anti-Patterns

### Multi-agent by default
**Mistake:** Splitting a task across a supervisor and five specialists when one agent with good tools would do.
**Why it happens:** Agent diagrams look like architecture; a single loop looks too simple.
**Instead:** Start with one agent and add a second only when context, permissions or parallelism demand it. Every hand-off costs tokens, latency and a new failure mode.

### Vague tool contracts
**Mistake:** Tools with one free-text `input` parameter and a description such as "does stuff with data".
**Why it happens:** Schemas get written after the code, as an afterthought.
**Instead:** Name and type every parameter, state units and limits, and describe when to call the tool and when not to. The model picks tools from these descriptions alone.

### Judging the system on success rate alone
**Mistake:** Shipping because 90% of tasks completed, without looking at cost per task, latency or which agent caused the failures.
**Why it happens:** Success rate is the only number that is easy to read off.
**Instead:** Run `agent_evaluator.py` on real logs and act on the bottleneck list; a high success rate with a 2-minute median latency is still a failed design.

## Files

- `scripts/agent_planner.py`, `scripts/tool_schema_generator.py`, `scripts/agent_evaluator.py` — the three CLIs above.
- `assets/sample_*.json` — runnable inputs for each tool; `expected_outputs/` — reference outputs for those samples.
- `references/usage-guide.md` — longer walkthrough with input formats and SDK examples.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/core-capabilities.md](references/core-capabilities.md)** — the full Core Capabilities catalog (architecture patterns, role definition, tool design, communication, guardrails, evaluation, orchestration, memory, scaling, failure handling) plus Implementation Guidelines. Read when designing any part of a system.
- **[references/agent_architecture_patterns.md](references/agent_architecture_patterns.md)** — deep catalog of architecture patterns with structure diagrams, characteristics, use cases, and implementation considerations. Read when selecting or comparing patterns.
- **[references/tool_design_best_practices.md](references/tool_design_best_practices.md)** — best practices for designing tools in multi-agent systems (single responsibility, idempotency, composability, schemas, error handling). Read when designing tools or schemas.
- **[references/evaluation_methodology.md](references/evaluation_methodology.md)** — full evaluation methodology across performance, reliability, cost, and satisfaction dimensions. Read when planning evaluation or interpreting reports.
- **[references/usage-guide.md](references/usage-guide.md)** — step-by-step walkthrough, input formats and SDK examples for the generated schemas.
- **[references/troubleshooting-and-tool-reference.md](references/troubleshooting-and-tool-reference.md)** — troubleshooting table, success criteria, and the complete CLI parameter reference for all three scripts. Read when a tool misbehaves or you need full command options.

## Scope & Limitations

**Covers:**
- Multi-agent architecture pattern selection (single agent, supervisor, swarm, hierarchical, pipeline)
- Agent role definition with responsibilities, capabilities, tools, and communication interfaces
- Tool schema generation in OpenAI and Anthropic formats with validation rules and error handling
- Performance evaluation from execution logs including bottleneck analysis and optimization recommendations

**Does NOT cover:**
- Runtime agent orchestration or execution engines (see `engineering/agent-workflow-designer` for workflow execution)
- LLM prompt engineering or system prompt design (see `engineering/prompt-engineer-toolkit`)
- MCP server implementation or protocol details (see `engineering/mcp-server-builder`)
- Self-improving agent feedback loops or autonomous learning (see `engineering/self-improving-agent`)

## See Also

- `engineering/agent-workflow-designer` — turn the chosen topology into a validated workflow DAG with cost estimates.
- `engineering/agent-protocol` — message and tool schema formats across MCP, OpenAI and A2A.
- `engineering/mcp-server-builder` — implement the tools whose schemas you generated here.
- `engineering/observability-designer` — decide what to trace and alert on for the agents you defined.
