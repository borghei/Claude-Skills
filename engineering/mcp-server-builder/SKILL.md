---
name: mcp-server-builder
description: >
  Build MCP (Model Context Protocol) servers with tool definitions, resource providers, prompt
  templates, and transports. Use when exposing APIs to AI agents, building tool servers,
  converting OpenAPI to MCP, or creating MCP integrations.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: ai-integration
  tier: POWERFUL
  updated: 2026-06-29
  frameworks: mcp-sdk, typescript, python, openapi
---
# MCP Server Builder

**Tier:** POWERFUL
**Category:** Engineering / AI Integration
**Maintainer:** Claude Skills Team

## Overview

Design and ship production-ready MCP (Model Context Protocol) servers from API contracts. Covers tool definition best practices, resource providers, prompt templates, OpenAPI-to-MCP conversion, TypeScript and Python server implementations, transport selection (stdio, SSE, StreamableHTTP), authentication patterns, testing strategies, and deployment configurations. Treats schema quality and tool discoverability as first-class concerns.

## Keywords

MCP, Model Context Protocol, MCP server, tool definition, resource provider, prompt template, stdio transport, SSE transport, OpenAPI to MCP, AI tool server, Claude tools

## Core Capabilities

- **Tool design & schema quality** — verb-noun naming, description engineering, typed input schemas, LLM-friendly output formatting
- **Server implementation** — TypeScript (`@modelcontextprotocol/sdk`) and Python (`mcp[cli]`) servers; tool/resource/prompt registration; structured error handling; logging, auth, and rate-limit middleware
- **Transport & deployment** — stdio (local/CLI), SSE (web), StreamableHTTP (production), Docker containerization, health checks, graceful shutdown
- **Testing & validation** — schema validation, MCP Inspector integration tests, contract/snapshot tests, load testing for remote servers

## When to Use

- Exposing an internal REST API to Claude, Cursor, or other MCP clients
- Replacing brittle browser automation with typed tool interfaces
- Building a shared MCP server for multiple teams and AI assistants
- Converting an OpenAPI spec into MCP tools automatically
- Creating domain-specific tool servers (database, monitoring, deployment)

## Clarify First

Before building the server, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Source contract** — the OpenAPI spec or API to expose, or whether building tools from scratch (the input the tool definitions and conversion derive from)
- [ ] **Language** — TypeScript (`@modelcontextprotocol/sdk`) or Python (`mcp[cli]`) (sets the server implementation generated)
- [ ] **Transport** — stdio (local/CLI), SSE (web), or StreamableHTTP (production) (drives transport, auth, and deployment patterns)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tool-schema-design.md](references/tool-schema-design.md)** — naming conventions, description engineering template, and input schema best practices. Read first when defining any tool, since description quality drives LLM tool selection.
- **[references/server-implementation.md](references/server-implementation.md)** — complete TypeScript and Python server code (tools, resources, prompts) plus the OpenAPI-to-MCP conversion rules and script. Read when writing the server.
- **[references/transport-and-deployment.md](references/transport-and-deployment.md)** — client configuration (`claude_desktop_config.json` for stdio and remote) and the tool versioning strategy. Read when connecting clients or planning releases.
- **[references/testing-and-troubleshooting.md](references/testing-and-troubleshooting.md)** — schema validation function, MCP Inspector commands, common pitfalls, best practices, troubleshooting table, and success criteria. Read when validating, hardening for production, or diagnosing failures.
- **[references/streaming-batch-and-computer-use.md](references/streaming-batch-and-computer-use.md)** — progress/streaming and cancellation for long-running tools, wrapping computer-use/browser/desktop actions (granularity, returning state, safety gates), and batch-friendly tool design (arrays, idempotency, partial-failure results, pagination). Read when a tool runs long, drives a live surface, or processes many items.

## Common Patterns

- **Streaming long-running tools** — when a call routinely exceeds a few seconds (builds, crawls, automation), emit throttled progress updates with a stable correlation handle, stream semantically whole chunks ending in an explicit terminal signal, and honor cancellation by aborting the real work and cleaning up sessions. The final response must stand alone. See `references/streaming-batch-and-computer-use.md`.
- **Batch-friendly tools** — when an operation is naturally repeated, accept a bounded array instead of forcing one chatty call per item; make operations idempotent (or take an idempotency key) and return per-item success/failure results so the agent retries only what failed. List/read tools must paginate with a documented cap and a cursor. Run `scripts/tool_schema_linter.py` to flag chatty single-item tools and missing pagination.
- **Computer-use via MCP** — expose intent-level actions (`navigate`, `click`, `read_page`) rather than raw pixel primitives, return current observable state (text-first, screenshots only when layout matters), and gate destructive/irreversible actions behind a `confirm`/`dry_run` param scoped to an allowlist with secrets redacted. For the automation engine itself, see the `computer-use-automation` skill.

## Scope & Limitations

**This skill covers:**
- Designing tool schemas, resource providers, and prompt templates for MCP servers
- Implementing servers in TypeScript (`@modelcontextprotocol/sdk`) and Python (`mcp[cli]`)
- Transport selection and client configuration (stdio, SSE, StreamableHTTP)
- OpenAPI-to-MCP conversion patterns and testing strategies

**This skill does NOT cover:**
- Building MCP clients or custom LLM orchestration layers — see `engineering/agent-workflow-designer`
- Designing multi-agent systems that consume MCP tools — see `engineering/agent-designer`
- API design itself (REST conventions, endpoint naming, versioning) — see `engineering/api-design-reviewer`
- Infrastructure provisioning, container orchestration, or CI/CD pipelines for deploying MCP servers — see `engineering/ci-cd-pipeline-builder`

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/api-design-reviewer` | Review the underlying REST API before converting it to MCP tools | OpenAPI spec → API review findings → refined spec → MCP conversion |
| `engineering/api-test-suite-builder` | Generate integration tests for the HTTP endpoints that MCP tools wrap | MCP tool definitions → endpoint mapping → test suite generation |
| `engineering/agent-designer` | Design agents that consume the MCP tools this skill produces | MCP tool schemas → agent tool inventory → agent behavior design |
| `engineering/observability-designer` | Add structured logging, tracing, and metrics to MCP server handlers | MCP server code → instrumentation plan → logging/tracing middleware |
| `engineering/ci-cd-pipeline-builder` | Automate build, test, and deploy pipelines for MCP server releases | MCP server repo → pipeline config → automated deploy to staging/prod |
| `engineering/env-secrets-manager` | Manage API keys, database credentials, and tokens used in MCP server configs | MCP server env vars → secrets audit → secure injection patterns |
