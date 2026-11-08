# Testing and Troubleshooting

Read this when validating tool schemas, running integration tests, hardening for production, or diagnosing why a server or tool misbehaves.

## Testing MCP Servers

### Schema Validation

```typescript
function validateToolSchema(tool: { name: string; description: string; inputSchema: any }): string[] {
  const issues: string[] = [];

  // Name validation
  if (!/^[a-z][a-z0-9_]*$/.test(tool.name)) {
    issues.push(`Name '${tool.name}' must be snake_case`);
  }

  // Description validation
  if (tool.description.length < 30) {
    issues.push("Description too short for reliable LLM tool selection");
  }
  if (!tool.description.includes("Use when") && !tool.description.includes("Use for")) {
    issues.push("Description should include usage guidance ('Use when...')");
  }

  // Schema validation
  const schema = tool.inputSchema;
  if (schema.type !== "object") {
    issues.push("inputSchema.type must be 'object'");
  }
  for (const [prop, def] of Object.entries(schema.properties || {})) {
    if (!(def as any).description) {
      issues.push(`Property '${prop}' missing description`);
    }
  }

  return issues;
}
```

### Integration Testing with MCP Inspector

```bash
# Install MCP Inspector
npx @modelcontextprotocol/inspector

# Test stdio server
npx @modelcontextprotocol/inspector node dist/index.js

# Test a Streamable HTTP server (legacy SSE servers use their /sse URL)
npx @modelcontextprotocol/inspector --url http://localhost:3001/mcp
```

## Common Pitfalls

- **Vague tool descriptions** causing the LLM to select the wrong tool or skip yours entirely
- **Missing property descriptions** leaving the LLM to guess what a parameter means
- **No timeout on tool execution** allowing runaway processes to hang the server
- **Exposing destructive operations without confirmation** — add a `confirm: true` required parameter
- **Returning raw JSON instead of formatted text** — LLMs work better with readable text output
- **No error handling** causing the server to crash on unexpected input
- **Breaking changes without versioning** breaking all connected clients simultaneously

## Best Practices

1. **Description-first design** — write the tool description before implementing the handler
2. **One intent per tool** — a tool that does three things confuses LLM selection
3. **Validate inputs in the handler** — never trust that the LLM sent correct types
4. **Return human-readable text** — format output as tables or structured text, not raw JSON
5. **Set timeouts on all operations** — prevent runaway commands from blocking the server
6. **Test tool selection** — present your tools to an LLM and verify it picks the right one for various prompts
7. **Log every tool call** — capture name, inputs, outputs, duration, and errors for debugging
8. **Version your tools** — maintain backward compatibility for at least one release cycle

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| LLM never selects my tool | Tool description is too vague or missing usage guidance | Rewrite the description using the template: "[What it does]. [What it returns]. [When to use it]." Ensure at least 30 characters and include "Use when..." phrasing |
| Tool call returns empty or `null` | Handler returns raw `undefined` instead of a content array | Always return `{ content: [{ type: "text", text: "..." }] }` even for empty results — never return bare `null` or `undefined` |
| `ECONNREFUSED` when connecting to remote server | HTTP server not running or wrong port in client config | Verify the server process is listening (`curl -i http://localhost:<port>/mcp`), check `url` in the client config (`.mcp.json` or `claude_desktop_config.json`), and confirm no firewall rules block the port |
| `spawn ENOENT` on stdio server startup | The `command` path in client config points to a missing binary | Use absolute paths for `command` (e.g., `/usr/local/bin/node`) or ensure the binary is on the shell PATH that the MCP host process inherits |
| Client connects but lists zero tools | `list_tools` handler not registered or returns an empty array | Confirm `@server.list_tools()` (Python) or `server.tool()` (TypeScript) is called before `server.connect()`. Test with MCP Inspector to verify the handshake |
| Tool execution times out | No timeout set on subprocess or HTTP calls inside the handler | Add explicit `timeout` to every `subprocess.run()`, `execSync()`, and `fetch()` call. 10-30 seconds for queries, 120 seconds max for builds |
| Schema validation errors from the client | `inputSchema.type` is not `"object"` or required fields are misspelled | Validate your tool definitions with the `validateToolSchema` function from the Testing section. Every `inputSchema` must have `type: "object"` at the top level |

## Success Criteria

- **Tool selection accuracy ≥ 90%** — when presented with 10 natural-language prompts, the LLM picks the correct tool at least 9 times
- **Schema validation passes at 100%** — every tool clears the `validateToolSchema` checks with zero issues (snake_case name, ≥30-char description, usage guidance, property descriptions)
- **Median tool response time < 2 seconds** — measured end-to-end from tool call to content response for typical queries
- **Zero unhandled exceptions** — every tool handler catches errors and returns a structured `isError: true` response instead of crashing the server
- **MCP Inspector green path** — the server connects, lists tools, executes each tool, and returns valid content through MCP Inspector without manual fixes
- **Client configuration works first try** — a new developer can copy the provided `claude_desktop_config.json` snippet, start the server, and invoke a tool within 5 minutes
- **OpenAPI conversion coverage ≥ 80%** — for a standard OpenAPI 3.x spec, at least 80% of operations convert to usable MCP tools without manual edits
