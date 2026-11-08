---
name: mcp-server-builder
description: >
  Builds MCP servers: OpenAPI-to-tool conversion, tool and schema linting, TypeScript or
  Python scaffolds, transports. Use when exposing an API to AI agents, building a tool
  server, or reviewing MCP tool definitions.
license: MIT + Commons Clause
metadata:
  version: 1.3.0
  author: borghei
  category: engineering
  domain: ai-integration
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: mcp-sdk, typescript, python, openapi
  tags:
    - mcp
    - ai-integration
    - tool-definitions
    - api
    - ai-agents
---
# MCP Server Builder

The agent designs and ships MCP (Model Context Protocol) servers whose tools an agent picks correctly and calls safely: verb_noun names, descriptions that say when to use the tool and what it returns, typed inputs, paginated lists and gated destructive actions. Schema quality is the main lever: the model chooses tools from names and descriptions alone.

## When to Use

- Exposing an internal REST API to Claude, Cursor or another MCP client.
- Converting an OpenAPI spec into MCP tools, then fixing what the conversion gets wrong.
- Replacing brittle browser automation with typed tool interfaces.
- Reviewing an existing server's tool definitions before release.

## Clarify First

Before building the server, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Source contract:** an OpenAPI spec, an existing API, or tools designed from scratch.
- **Language:** TypeScript (`@modelcontextprotocol/sdk`) or Python (`mcp`).
- **Transport:** stdio for local tools, Streamable HTTP for remote or shared servers (HTTP+SSE only for legacy clients).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Get tool definitions.** From a spec: `openapi_converter.py spec.json -o tools.json` (add `--filter GET,POST`, `--exclude '/internal/*'`, `--prefix`). From scratch: write `{"tools": [...]}` by hand using [references/tool-schema-design.md](references/tool-schema-design.md).
2. **Lint naming, descriptions and schemas** with `tool_linter.py tools.json`. Fix every error; rewrite descriptions to say when to use the tool and what it returns.
3. **Lint interaction design** with `tool_schema_linter.py tools.json`: add pagination to list tools, a `confirm` or `dry_run` gate to destructive ones, arrays where calls are naturally repeated.
4. **Scaffold** the server with `server_scaffolder.py tools.json --lang typescript|python --output <dir>`, then implement each handler from [references/server-implementation.md](references/server-implementation.md).
5. **Test** with MCP Inspector and the checks in [references/testing-and-troubleshooting.md](references/testing-and-troubleshooting.md).
6. Done when both linters exit 0 with `--strict`, every handler returns structured errors instead of throwing, and the Inspector lists and calls every tool.

## Quick Start

```bash
# from engineering/mcp-server-builder/; write output outside the repo
OUT=$(mktemp -d)
python3 scripts/openapi_converter.py assets/sample_openapi.json --prefix tasks -o "$OUT/tools.json"
python3 scripts/tool_linter.py "$OUT/tools.json"                # exit 0: no errors, 2 usage-guidance warnings
python3 scripts/tool_schema_linter.py "$OUT/tools.json"         # exit 1: delete has no confirm gate
python3 scripts/server_scaffolder.py "$OUT/tools.json" --lang python --output "$OUT/server" --dry-run
```

```bash
python3 scripts/tool_linter.py assets/flawed_tools.json         # exit 1: camelCase name, 1-char description, untyped property
python3 scripts/tool_schema_linter.py assets/flawed_tools.json  # exit 1: unpaginated list, ungated delete
```

## Tools Overview

| Tool | Purpose | Key flags | Exit codes |
|------|---------|-----------|------------|
| `scripts/openapi_converter.py` | OpenAPI 3.x / Swagger 2.0 JSON to MCP tool definitions (`{"tools": [...]}`), operationId to snake_case | `spec`, `-o`, `--prefix`, `--filter GET,POST`, `--exclude GLOB`, `--no-source`, `--json` | 0 converted; 2 missing or invalid spec |
| `scripts/tool_linter.py` | Naming (snake_case, verb_noun), description length and guidance, property types and descriptions | `file`, `--path`, `--strict`, `--json` | 0 no errors (or no warnings with `--strict`); 1 issues; 2 unreadable input |
| `scripts/tool_schema_linter.py` | Interaction smells: list tools without pagination, destructive tools without a gate, chatty single-item tools, unconstrained inputs | `file`, `--path`, `--strict`, `--json` | 0 no warnings; 1 smells found; 2 unreadable input |
| `scripts/server_scaffolder.py` | TypeScript or Python server skeleton with one handler stub per tool | `config`, `--lang`, `--output`, `--dry-run`, `--json` | 0 generated; 2 invalid config |

The linters accept a bare tool, a tool array, or a `{"tools": [...]}` wrapper (converter output); use `--path` for other nesting. The scaffolder takes the converter output directly and derives the server name from the spec title when `name` is absent. Run both linters: they check different things.

## Anti-Patterns

**Mistake:** Shipping the converter output as is.
**Why it matters:** OpenAPI summaries describe endpoints, not when an agent should call them, so the model picks the wrong tool or none.
**Instead:** Rewrite each description with a "Use when ..." clause and what it returns, then re-lint.

**Mistake:** A list tool that returns everything.
**Why it matters:** Unbounded results flood the context window and get truncated mid-record.
**Instead:** Cap the page size, return a cursor, and document both in the description.

**Mistake:** Destructive tools that act on the first call.
**Why it matters:** The agent calls tools speculatively; an ungated delete turns a misunderstanding into data loss.
**Instead:** Add `confirm` or `dry_run` defaulting to the safe path, and say in the description that the action cannot be undone.

## Common Patterns

- **Long-running tools:** emit throttled progress with a stable handle, honor cancellation, and make the final response stand alone. See [references/streaming-batch-and-computer-use.md](references/streaming-batch-and-computer-use.md).
- **Batch-friendly tools:** accept bounded arrays, take an idempotency key, return per-item results so the agent retries only failures.
- **Computer use via MCP:** expose intent-level actions (`navigate`, `click`, `read_page`), return observable state as text first, and gate irreversible actions. For the automation engine see `engineering/computer-use-automation`.

## Reference Documentation

- **[references/tool-schema-design.md](references/tool-schema-design.md)**: naming, the description template and input-schema rules. Read first when defining any tool.
- **[references/server-implementation.md](references/server-implementation.md)**: TypeScript and Python servers (tools, resources, prompts) and the OpenAPI conversion rules. Read when writing handlers.
- **[references/transport-and-deployment.md](references/transport-and-deployment.md)**: transport choice, client configuration and tool versioning. Read when connecting clients or planning releases.
- **[references/testing-and-troubleshooting.md](references/testing-and-troubleshooting.md)**: schema validation, MCP Inspector, pitfalls, troubleshooting and success criteria. Read when validating or diagnosing.
- **[references/streaming-batch-and-computer-use.md](references/streaming-batch-and-computer-use.md)**: streaming and cancellation, computer-use wrappers, batch design and pagination.

## Files

| File | Purpose |
|------|---------|
| `scripts/openapi_converter.py` | OpenAPI to MCP tool definitions |
| `scripts/tool_linter.py` | Naming, description and schema linter |
| `scripts/tool_schema_linter.py` | Interaction-design linter |
| `scripts/server_scaffolder.py` | Server skeleton generator |
| `assets/sample_openapi.json` | Three-operation Tasks API (list, create, delete) |
| `assets/flawed_tools.json` | Deliberately weak tool definitions; both linters exit 1 |

## Scope & Limitations

**Covers:** tool, resource and prompt design; TypeScript and Python servers; transport choice and client configuration; OpenAPI conversion; schema and interaction linting.

**Does not cover:**
- MCP clients or orchestration layers (see `engineering/agent-workflow-designer`).
- Multi-agent systems that consume the tools (see `engineering/agent-designer`).
- REST API design itself (see `engineering/api-design-reviewer`).
- Deployment pipelines (see `engineering/ci-cd-pipeline-builder`).
