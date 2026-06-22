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
  updated: 2026-06-15
  frameworks: mcp, a2a, openai-functions, langchain-tools
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

Before designing the protocol, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Protocol target** — MCP, A2A, OpenAI Function Calling, or LangChain Tools (drives the entire schema and transport design via the Decision Framework below)
- [ ] **Transport & client** — which client consumes it (stdio/SSE/WebSocket for MCP, HTTP+JSON-RPC for A2A)
- [ ] **Auth & trust boundary** — in-process vs cross-organization (determines OAuth 2.1 vs API key vs none, plus rate limiting and signing)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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

## References

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
