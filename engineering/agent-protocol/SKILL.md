---
name: agent-protocol
description: >
  Design AI agent communication protocols: MCP tool schemas, A2A, function calling, and inter-
  agent messaging. Use when building multi-agent systems, defining tool interfaces, or
  implementing agent-to-agent communication.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: ai-agent-systems
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: mcp, a2a, openai-functions, langchain-tools
  tags:
    - mcp
    - a2a
    - function-calling
    - tool-schemas
    - multi-agent
---
# Agent Protocol

The agent designs tool schemas for MCP, Google A2A, and OpenAI Function Calling protocols. It implements transport selection, capability discovery, authentication flows (OAuth 2.1, API keys), structured error handling, rate limiting, and protocol bridges for heterogeneous agent ecosystems.

## Core Capabilities

- **Protocol selection & comparison** — MCP (tool/resource/prompt serving), Google A2A (agent cards, task lifecycle, streaming), OpenAI Function Calling (JSON Schema, parallel calls, strict mode), LangChain/LangGraph tools, and custom WebSocket/gRPC messaging
- **Tool schema design** — JSON Schema input/output validation, semantic naming conventions, description engineering for LLM comprehension, required vs optional parameters, enum and default strategies
- **Transport & discovery** — stdio/SSE/WebSocket for MCP, HTTP+JSON-RPC for A2A, agent card capability advertisement, health checking, and protocol version negotiation
- **Security & authentication** — OAuth 2.1 flows, API key rotation and scoping, request signing, per-identity rate limiting, and audit logging for inter-agent calls

## When to Use

- Designing tool interfaces for LLM-powered agents
- Building MCP servers that expose APIs to Claude, Cursor, or other clients
- Implementing agent-to-agent communication in multi-agent systems
- Bridging between different agent protocols (MCP to A2A, etc.)
- Standardizing tool calling patterns across a team or organization
- Debugging agent tool selection failures

## Clarify First

Before designing the protocol, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Protocol target:** MCP, A2A, OpenAI Function Calling, or LangChain Tools (drives the entire schema and transport design via the Decision Framework below).
- **Transport & client:** which client consumes it (stdio/SSE/WebSocket for MCP, HTTP+JSON-RPC for A2A).
- **Auth & trust boundary:** in-process vs cross-organization (determines OAuth 2.1 vs API key vs none, plus rate limiting and signing).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Decision Framework

```
What are you building?
│
├─ Tools for a single LLM client (Claude, Cursor, Copilot)
│  └─ Use MCP — it's the native protocol for tool serving
│
├─ Agent-to-agent communication across organizations
│  └─ Use A2A — designed for cross-boundary agent discovery and delegation
│
├─ Tools for OpenAI models specifically
│  └─ Use OpenAI Function Calling — tightest integration
│
├─ Python pipeline with multiple chained tools
│  └─ Use LangChain Tools — simplest for in-process orchestration
│
└─ Heterogeneous agent ecosystem (multiple protocols)
   └─ Use Protocol Bridge pattern — translate between protocols at boundaries
```

## Quick Start Workflow

```bash
# 1. Generate a schema from flags (or --from-python FILE --function NAME, or --from-config FILE)
python scripts/schema_generator.py --name search_docs \
    --desc "Search internal docs by keyword and return the top matches" \
    --param "query:string:required:Search terms" --param "limit:integer:optional:Max results" \
    --protocol openai --strict --output /tmp/search_docs.json

# 2. Validate it (auto-detects MCP, A2A agent card, OpenAI single tool / tools list / functions list)
python scripts/protocol_validator.py assets/sample_mcp_tool.json assets/sample_openai_tool.json --strict  # PASS, exit 0
python scripts/protocol_validator.py assets/sample_mcp_tool_flawed.json --strict                         # 2 errors, exit 1

# 3. Map capabilities across files: inventory, duplicate names, compatibility matrix, quality gaps
python scripts/capability_mapper.py assets/sample_mcp_tool.json assets/sample_openai_tool.json
```

## Tools Overview

| Tool | Purpose | Key flags |
|------|---------|-----------|
| `schema_generator.py` | MCP tool, OpenAI tool (`{"type": "function", ...}`) or A2A agent card from flags, a Python signature or a config file | `--param name:type[:required\|optional][:desc]`, `--protocol`, `--strict` (OpenAI strict mode: all params required, no extra properties), `--output` |
| `protocol_validator.py` | Naming, description quality, types, required-vs-properties consistency, strict-mode rules | `--protocol auto\|mcp\|a2a\|openai`, `--strict`, `--json` |
| `capability_mapper.py` | Inventory and duplicate detection across protocols; reads everything the generator writes | `--detect-conflicts`, `--compatibility-matrix`, `--gap-analysis`, `--scan-dir`, `--json` |

**Exit codes.** `protocol_validator.py`: `0` no errors, `1` validation errors, `2` missing file or
invalid JSON. `capability_mapper.py`: `0` clean, `1` an unreadable protocol file or a likely
duplicate tool (same name and description in two places, as in step 3), `2` missing file or
directory. `schema_generator.py`: `0` written, `2` bad arguments.

**Done when:** every schema passes `protocol_validator.py --strict`, each tool description says
what it does, when to use it and what it returns, and the mapper shows no unintended duplicates
across the protocols you serve.

## Anti-Patterns

### Descriptions written for humans skimming a list
**Mistake:** "Search tool" as the whole description.
**Why it happens:** The name feels self-explanatory to the author.
**Instead:** The model chooses tools from descriptions alone. Say what it does, when to use it instead of its neighbours, and what comes back.

### One schema per protocol, maintained by hand
**Mistake:** Copy-editing the MCP schema into an OpenAI schema and letting them drift.
**Why it happens:** Each integration was added by a different person.
**Instead:** Keep one source (a config file or the Python signature) and generate each protocol's schema from it with `schema_generator.py`.

### Free-form parameters
**Mistake:** A single `input: string` parameter that the tool parses itself.
**Why it happens:** It avoids designing the interface.
**Instead:** Typed, described parameters with enums and limits. Validation then happens before the call, and the model makes fewer malformed calls.

## Files

- `scripts/schema_generator.py`, `scripts/protocol_validator.py`, `scripts/capability_mapper.py` — the three CLIs above.
- `assets/sample_mcp_tool.json`, `assets/sample_openai_tool.json` (valid, generated by step 1), `assets/sample_mcp_tool_flawed.json` (bad name, missing types, required field not in properties).
- `references/` — protocol selection, MCP implementation, A2A and bridges, errors and testing.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/protocol-selection.md](references/protocol-selection.md)** — full MCP vs A2A vs OpenAI Functions vs LangChain Tools comparison matrix. Read when comparing protocols before committing to one.
- **[references/mcp-implementation.md](references/mcp-implementation.md)** — tool schema anatomy, naming/description rules, and TypeScript MCP server code (stdio + authenticated SSE). Read when building an MCP server or designing tool schemas.
- **[references/a2a-and-bridges.md](references/a2a-and-bridges.md)** — A2A agent card, task lifecycle, full Python A2A client, and the Protocol Bridge pattern. Read when building agent-to-agent communication or bridging protocols.
- **[references/errors-testing-and-quality.md](references/errors-testing-and-quality.md)** — structured error format, error code taxonomy, schema/integration testing, pitfalls, best practices, troubleshooting, and success criteria. Read when hardening for production or diagnosing failures.

## Scope & Limitations

**This skill covers:**
- Designing tool schemas for MCP, A2A, OpenAI Function Calling, and LangChain Tools
- Transport selection, capability discovery, and protocol version negotiation
- Authentication, rate limiting, and structured error handling for agent communication
- Protocol bridging between heterogeneous agent ecosystems

**This skill does NOT cover:**
- Building complete MCP server applications with business logic — see `engineering/mcp-server-builder`
- Agent orchestration patterns, planning loops, or multi-step reasoning — see `engineering/agent-workflow-designer`
- Designing agent personas, memory systems, or behavioral profiles — see `engineering/agent-designer`
- Infrastructure deployment, CI/CD pipelines, or container orchestration for agent services — see `engineering/senior-devops`

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/mcp-server-builder` | Protocol schemas defined here feed directly into MCP server scaffolding | Tool definitions and inputSchema objects flow into server code generation |
| `engineering/agent-workflow-designer` | Workflow orchestrators consume protocol interfaces to dispatch tasks | Agent-protocol defines the transport contract; workflow-designer defines execution order and branching |
| `engineering/agent-designer` | Agent identity and capability profiles reference protocol-level skill declarations | Agent cards and capability metadata from protocol design inform agent persona configuration |
| `engineering/senior-security` | Security review of auth flows, token scoping, and rate limiting configurations | OAuth 2.1 flows, API key rotation policies, and audit logging patterns flow into security assessments |
| `engineering/api-design-reviewer` | REST and JSON-RPC endpoint design review for A2A and MCP HTTP transports | API schema and endpoint contracts feed into design review checklists |
| `engineering/observability-designer` | Monitoring and tracing for inter-agent calls, latency tracking, and error budgets | Tool call logs with agent ID, latency, and error codes flow into observability dashboards |
