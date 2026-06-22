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
  updated: 2026-06-17
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

Before designing the system, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **System goal & scale** — the task the agents perform and expected load (drives which architecture pattern: single, supervisor, swarm, hierarchical, or pipeline)
- [ ] **Tool protocol target** — OpenAI function calling vs Anthropic tool use (sets the schema format `tool_schema_generator.py` emits)
- [ ] **Optimization priority** — cost, latency, or quality (determines agent roles, model tiers, and which metrics the evaluator weights)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `agent_planner.py` | Design architecture from requirements (pattern, roles, topology, Mermaid diagram, roadmap) | `python agent_planner.py requirements.json -o my_system --format both` |
| `agent_evaluator.py` | Evaluate performance from execution logs (success, cost, latency, bottlenecks) | `python agent_evaluator.py execution_logs.json -o perf_report --format both --detailed` |
| `tool_schema_generator.py` | Generate OpenAI/Anthropic tool schemas with validation | `python tool_schema_generator.py tools.json -o my_tools --format both --validate` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/core-capabilities.md](references/core-capabilities.md)** — the full Core Capabilities catalog (architecture patterns, role definition, tool design, communication, guardrails, evaluation, orchestration, memory, scaling, failure handling) plus Implementation Guidelines. Read when designing any part of a system.
- **[references/agent_architecture_patterns.md](references/agent_architecture_patterns.md)** — deep catalog of architecture patterns with structure diagrams, characteristics, use cases, and implementation considerations. Read when selecting or comparing patterns.
- **[references/tool_design_best_practices.md](references/tool_design_best_practices.md)** — best practices for designing tools in multi-agent systems (single responsibility, idempotency, composability, schemas, error handling). Read when designing tools or schemas.
- **[references/evaluation_methodology.md](references/evaluation_methodology.md)** — full evaluation methodology across performance, reliability, cost, and satisfaction dimensions. Read when planning evaluation or interpreting reports.
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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/agent-workflow-designer` | Workflow definitions consume architecture designs from Agent Designer | Agent roles and communication topology feed into workflow step definitions |
| `engineering/prompt-engineer-toolkit` | System prompts are crafted per agent role defined by Agent Designer | Agent role specifications and responsibilities inform prompt structure and constraints |
| `engineering/mcp-server-builder` | Tool schemas generated here map to MCP server tool implementations | `tool_schema_generator.py` output provides the schema contract that MCP servers implement |
| `engineering/self-improving-agent` | Evaluation reports feed into self-improvement loops | `agent_evaluator.py` bottleneck analysis drives autonomous optimization decisions |
| `engineering/observability-designer` | Monitoring architecture aligns with agent topology and communication links | Agent definitions and communication patterns define what to instrument and alert on |
| `engineering/agent-protocol` | Protocol standards govern inter-agent message formats designed here | Communication topology patterns must comply with agent protocol specifications |
