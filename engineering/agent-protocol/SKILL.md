---
name: agent-protocol
description: Design and implement AI agent communication protocols including MCP tool schemas, Google A2A protocol, OpenAI function calling, structured inter-agent messaging, and protocol negotiation. Use when building multi-agent systems, defining tool interfaces, implementing agent-to-agent communication, or standardizing LLM tool calling patterns across platforms.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: ai-agent-systems
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: mcp, a2a, openai-functions, langchain-tools
---

# Agent Protocol

**Tier:** POWERFUL
**Category:** Engineering / AI Systems
**Maintainer:** Claude Skills Team

## Overview

The Agent Protocol skill provides production-grade patterns for AI agent communication across every major protocol: Model Context Protocol (MCP), Google Agent-to-Agent (A2A), OpenAI Function Calling, and custom inter-agent messaging. Covers tool schema design, transport negotiation, capability discovery, authentication, error handling, and protocol bridging for heterogeneous agent ecosystems.

## Keywords

agent protocol, MCP, model context protocol, A2A, agent-to-agent, function calling, tool schema, agent communication, inter-agent messaging, tool definition, capability discovery, protocol bridge, agent orchestration, LLM tools

## Core Capabilities

### 1. Protocol Selection and Comparison
- **MCP (Model Context Protocol)**: Anthropic's standard for tool/resource/prompt serving
- **Google A2A (Agent-to-Agent)**: Agent card discovery, task lifecycle, streaming
- **OpenAI Function Calling**: JSON Schema tool definitions, parallel calls, strict mode
- **LangChain/LangGraph Tools**: Python-native tool wrappers with callback integration
- **Custom Protocols**: WebSocket, gRPC, and event-driven agent messaging

### 2. Tool Schema Design
- JSON Schema validation for inputs and outputs
- Semantic naming conventions that improve agent tool selection
- Description engineering for maximum LLM comprehension
- Required vs optional parameter design
- Enum constraints and default value strategies

### 3. Transport and Discovery
- stdio, SSE, and WebSocket transport for MCP
- HTTP+JSON-RPC for A2A task management
- Agent card and capability advertisement
- Health checking and graceful degradation
- Protocol version negotiation

### 4. Security and Authentication
- OAuth 2.1 flows for MCP remote servers
- API key rotation and scoping
- Request signing and verification
- Rate limiting per agent identity
- Audit logging for all inter-agent calls

## When to Use

- Designing tool interfaces for LLM-powered agents
- Building MCP servers that expose APIs to Claude, Cursor, or other clients
- Implementing agent-to-agent communication in multi-agent systems
- Bridging between different agent protocols (MCP to A2A, etc.)
- Standardizing tool calling patterns across a team or organization
- Debugging agent tool selection failures

## Protocol Comparison Matrix

| Feature | MCP | A2A | OpenAI Functions | LangChain Tools |
|---------|-----|-----|-----------------|-----------------|
| Transport | stdio/SSE/WebSocket | HTTP+JSON-RPC | HTTP REST | In-process |
| Discovery | Server capabilities | Agent cards | API spec | Registry |
| Streaming | SSE notifications | SSE streaming | Streaming deltas | Callbacks |
| Auth | OAuth 2.1 | Agent auth | API key | N/A |
| State | Resources + context | Task lifecycle | Conversation | Memory |
| Multi-turn | Sampling | Task updates | Thread context | Chain state |
| File handling | Resource URIs | Artifact parts | File search | Document loaders |
| Best for | Tool serving | Agent networks | Single-model tools | Python pipelines |

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

## MCP Tool Schema Design

### Anatomy of a Well-Designed Tool

```json
{
  "name": "search_documents",
  "description": "Search the knowledge base for documents matching a query. Returns ranked results with titles, snippets, and relevance scores. Use this when the user asks a question that requires looking up information from stored documents.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Natural language search query. Be specific — 'Q4 2025 revenue projections' works better than 'revenue'."
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of results to return.",
        "default": 10,
        "minimum": 1,
        "maximum": 50
      },
      "filters": {
        "type": "object",
        "description": "Optional filters to narrow results.",
        "properties": {
          "date_after": {
            "type": "string",
            "format": "date",
            "description": "Only return documents created after this date (YYYY-MM-DD)."
          },
          "document_type": {
            "type": "string",
            "enum": ["report", "memo", "presentation", "spreadsheet"],
            "description": "Filter by document type."
          }
        }
      }
    },
    "required": ["query"]
  }
}
```

### Tool Naming Rules

```
GOOD tool names (verb_noun, specific):
  search_documents      — clear action + target
  create_github_issue   — includes the service for disambiguation
  get_user_profile      — standard CRUD verb
  analyze_pr_diff       — describes the analysis action
  send_slack_message    — action + channel type

BAD tool names (vague, ambiguous, or too generic):
  search                — search what?
  do_thing              — meaningless
  handler               — not a verb_noun
  processData           — camelCase breaks conventions
  get_stuff             — too vague for LLM selection
```

### Description Engineering

The description is the single most important field for agent tool selection. An LLM reads the description to decide whether to call this tool.

```
EFFECTIVE description pattern:
"[What it does]. [What it returns]. [When to use it]."

Example:
"Search the knowledge base for documents matching a query. Returns ranked
results with titles, snippets, and relevance scores. Use this when the
user asks a question that requires looking up stored documents."

INEFFECTIVE descriptions:
"Searches documents."           — too short, no usage guidance
"This tool is used for..."      — wastes tokens on filler
"A powerful search engine..."   — marketing copy, not instructions
```

## MCP Server Implementation (TypeScript)

### Minimal Server with Tool and Resource

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "project-tools",
  version: "1.0.0",
  capabilities: {
    tools: {},
    resources: {},
  },
});

// Tool: search codebase
server.tool(
  "search_codebase",
  "Search the project codebase for files matching a pattern. Returns file paths and line numbers with matching content. Use when looking for implementations, definitions, or usage of specific code patterns.",
  {
    pattern: z.string().describe("Regex or glob pattern to search for"),
    file_type: z.enum(["ts", "py", "go", "rs", "all"]).default("all")
      .describe("Filter by file extension"),
    max_results: z.number().int().min(1).max(100).default(20)
      .describe("Maximum results to return"),
  },
  async ({ pattern, file_type, max_results }) => {
    // Implementation: run ripgrep or similar
    const results = await searchFiles(pattern, file_type, max_results);
    return {
      content: [{
        type: "text",
        text: JSON.stringify(results, null, 2),
      }],
    };
  }
);

// Resource: project structure
server.resource(
  "project://structure",
  "project://structure",
  async (uri) => ({
    contents: [{
      uri: uri.href,
      mimeType: "application/json",
      text: JSON.stringify(await getProjectStructure()),
    }],
  })
);

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

### MCP Server with Authentication (SSE Transport)

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import express from "express";

const app = express();

// Authentication middleware
function authenticateAgent(req, res, next) {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token || !verifyAgentToken(token)) {
    return res.status(401).json({ error: "Invalid agent credentials" });
  }
  req.agentId = extractAgentId(token);
  next();
}

// Rate limiting per agent
const rateLimiter = new Map<string, { count: number; resetAt: number }>();
function rateLimit(agentId: string, maxPerMinute = 60): boolean {
  const now = Date.now();
  const entry = rateLimiter.get(agentId) || { count: 0, resetAt: now + 60000 };
  if (now > entry.resetAt) {
    entry.count = 0;
    entry.resetAt = now + 60000;
  }
  entry.count++;
  rateLimiter.set(agentId, entry);
  return entry.count <= maxPerMinute;
}

app.use("/mcp", authenticateAgent);

app.get("/mcp/sse", (req, res) => {
  if (!rateLimit(req.agentId)) {
    return res.status(429).json({ error: "Rate limit exceeded" });
  }
  const transport = new SSEServerTransport("/mcp/messages", res);
  server.connect(transport);
});

app.listen(3001, () => console.log("MCP server on :3001"));
```

## Google A2A Protocol Implementation

### Agent Card (Discovery)

```json
{
  "name": "Research Agent",
  "description": "Performs web research and synthesizes findings into structured reports.",
  "url": "https://research-agent.example.com",
  "provider": {
    "organization": "Acme Corp",
    "url": "https://acme.example.com"
  },
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": true
  },
  "authentication": {
    "schemes": ["Bearer"],
    "credentials": "oauth2"
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain", "application/json"],
  "skills": [
    {
      "id": "web-research",
      "name": "Web Research",
      "description": "Search the web and synthesize findings into a structured report with citations.",
      "tags": ["research", "web", "synthesis"],
      "examples": [
        "Research the latest trends in AI agent frameworks",
        "Find competitive pricing data for SaaS products in the CRM space"
      ]
    }
  ]
}
```

### A2A Task Lifecycle

```
Client                           Agent
  │                                │
  ├─ POST /tasks/send ────────────►│ Create task
  │◄──────── task (submitted) ─────┤
  │                                │
  ├─ GET /tasks/{id} ─────────────►│ Poll status
  │◄──────── task (working) ───────┤
  │                                │
  │  (agent processes...)          │
  │                                │
  ├─ GET /tasks/{id} ─────────────►│ Poll status
  │◄──────── task (completed) ─────┤
  │         + artifacts            │
```

### A2A Client Implementation

```python
import httpx
import json
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class TaskState(Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

@dataclass
class A2AClient:
    base_url: str
    auth_token: str
    timeout: float = 30.0

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }

    def discover(self) -> dict:
        """Fetch the agent card for capability discovery."""
        resp = httpx.get(
            f"{self.base_url}/.well-known/agent.json",
            headers=self._headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def send_task(self, message: str, task_id: Optional[str] = None) -> dict:
        """Send a task to the agent. Returns task object with status."""
        payload = {
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": message}],
                },
            },
            "id": task_id or self._generate_id(),
        }
        resp = httpx.post(
            f"{self.base_url}/a2a",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["result"]

    def get_task(self, task_id: str) -> dict:
        """Poll task status."""
        payload = {
            "jsonrpc": "2.0",
            "method": "tasks/get",
            "params": {"id": task_id},
            "id": self._generate_id(),
        }
        resp = httpx.post(
            f"{self.base_url}/a2a",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["result"]

    def wait_for_completion(self, task_id: str, poll_interval: float = 2.0, max_polls: int = 60) -> dict:
        """Poll until task reaches a terminal state."""
        import time
        terminal_states = {TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELED}
        for _ in range(max_polls):
            task = self.get_task(task_id)
            if TaskState(task["status"]["state"]) in terminal_states:
                return task
            time.sleep(poll_interval)
        raise TimeoutError(f"Task {task_id} did not complete within {max_polls * poll_interval}s")

    @staticmethod
    def _generate_id() -> str:
        import uuid
        return str(uuid.uuid4())
```

## Protocol Bridge Pattern

When your system uses multiple protocols, implement a bridge that translates between them.

```python
class ProtocolBridge:
    """Translates between MCP tool calls and A2A task delegation."""

    def __init__(self, a2a_agents: dict[str, A2AClient]):
        self.agents = a2a_agents  # skill_id -> A2AClient

    def mcp_tool_to_a2a_task(self, tool_name: str, arguments: dict) -> dict:
        """Convert an MCP tool call into an A2A task send."""
        agent_id, skill = self._resolve_agent(tool_name)
        client = self.agents[agent_id]

        message = self._format_task_message(tool_name, arguments)
        task = client.send_task(message)
        result = client.wait_for_completion(task["id"])

        return self._a2a_result_to_mcp_response(result)

    def _resolve_agent(self, tool_name: str) -> tuple[str, str]:
        """Map MCP tool name to A2A agent + skill."""
        routing = {
            "search_web": ("research-agent", "web-research"),
            "analyze_data": ("analytics-agent", "data-analysis"),
            "generate_code": ("code-agent", "code-generation"),
        }
        if tool_name not in routing:
            raise ValueError(f"No A2A agent registered for tool: {tool_name}")
        return routing[tool_name]

    def _format_task_message(self, tool_name: str, arguments: dict) -> str:
        return json.dumps({"tool": tool_name, "arguments": arguments})

    def _a2a_result_to_mcp_response(self, task: dict) -> dict:
        """Convert A2A task result to MCP tool response format."""
        if task["status"]["state"] == "completed":
            artifacts = task.get("artifacts", [])
            text_parts = []
            for artifact in artifacts:
                for part in artifact.get("parts", []):
                    if part["type"] == "text":
                        text_parts.append(part["text"])
            return {"content": [{"type": "text", "text": "\n".join(text_parts)}]}
        else:
            error_msg = task["status"].get("message", "Task failed")
            return {"content": [{"type": "text", "text": f"Error: {error_msg}"}], "isError": True}
```

## Error Handling Standards

### Structured Error Responses

Every protocol should return errors in a consistent format that agents can parse and recover from.

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests. Retry after 30 seconds.",
    "retryable": true,
    "retry_after_seconds": 30,
    "details": {
      "limit": 60,
      "window": "1m",
      "current": 62
    }
  }
}
```

### Error Code Taxonomy

| Code | Meaning | Agent Action |
|------|---------|-------------|
| `INVALID_INPUT` | Bad parameters | Fix input and retry |
| `NOT_FOUND` | Resource missing | Try alternative or report |
| `AUTH_FAILED` | Credentials invalid | Refresh token and retry |
| `AUTH_EXPIRED` | Token expired | Refresh and retry once |
| `RATE_LIMITED` | Too many requests | Wait `retry_after` then retry |
| `UPSTREAM_ERROR` | External service failed | Retry with backoff |
| `INTERNAL_ERROR` | Server bug | Report, do not retry |
| `CAPABILITY_UNAVAILABLE` | Tool/skill disabled | Use alternative tool |

## Testing Agent Protocols

### Tool Schema Validation

```python
import jsonschema

def validate_mcp_tool(tool_def: dict) -> list[str]:
    """Validate an MCP tool definition for common issues."""
    issues = []

    if not tool_def.get("name"):
        issues.append("Missing tool name")
    elif not tool_def["name"].replace("_", "").isalnum():
        issues.append(f"Tool name '{tool_def['name']}' should use snake_case with alphanumeric chars")

    desc = tool_def.get("description", "")
    if len(desc) < 20:
        issues.append("Description too short — LLMs need clear usage guidance")
    if not any(word in desc.lower() for word in ["use when", "returns", "use this"]):
        issues.append("Description should explain when to use the tool and what it returns")

    schema = tool_def.get("inputSchema", {})
    if schema.get("type") != "object":
        issues.append("inputSchema must be type: object")

    for prop_name, prop_def in schema.get("properties", {}).items():
        if not prop_def.get("description"):
            issues.append(f"Property '{prop_name}' missing description")
        if prop_def.get("type") == "string" and not prop_def.get("description"):
            issues.append(f"String property '{prop_name}' needs description for LLM context")

    return issues
```

### Integration Testing Pattern

```python
import subprocess
import json

def test_mcp_server_tools():
    """Verify MCP server starts and lists expected tools."""
    proc = subprocess.Popen(
        ["node", "dist/index.js"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Send initialize request
    init_msg = json.dumps({
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "test"}},
        "id": 1,
    }) + "\n"
    proc.stdin.write(init_msg.encode())
    proc.stdin.flush()

    # Send tools/list
    list_msg = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2,
    }) + "\n"
    proc.stdin.write(list_msg.encode())
    proc.stdin.flush()

    # Read and validate response
    # (In production, use proper JSON-RPC response parsing)
    proc.terminate()
```

## Common Pitfalls

- **Vague tool descriptions** that cause the LLM to select the wrong tool or skip it entirely
- **Missing required field declarations** leading to agents sending incomplete parameters
- **No error codes** in responses, forcing agents to parse error messages with heuristics
- **Exposing internal implementation details** in tool schemas instead of user-intent abstractions
- **No rate limiting** on MCP servers, allowing runaway agent loops to exhaust resources
- **Mixing transport concerns with protocol logic** instead of keeping them separate
- **No capability versioning** making it impossible to evolve tools without breaking clients
- **Synchronous-only design** that blocks on long-running operations instead of using task lifecycle

## Best Practices

1. **Description-first design** — write the tool description before the implementation
2. **One intent per tool** — a tool that does three things gets selected for the wrong reason
3. **Validate inputs on the server** — never trust that the LLM sent correct types
4. **Return structured errors** with codes, not string messages
5. **Version your protocol** — use capability negotiation at connection time
6. **Log every tool call** with agent ID, inputs, outputs, and latency for debugging
7. **Test tool selection** — present your tool list to an LLM and verify it picks the right one
8. **Use protocol bridges** at boundaries rather than forcing all agents onto one protocol
