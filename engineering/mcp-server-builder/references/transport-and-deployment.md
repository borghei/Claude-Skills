# Transport and Deployment

Read this when choosing a transport, wiring a server into a client, and managing tool versions across releases.

## Choosing a Transport

| Transport | Use for | Notes |
|-----------|---------|-------|
| stdio | Local tools launched by the client (CLI, desktop) | Simplest; no network, no auth; one client per process |
| Streamable HTTP | Remote and shared servers | The current spec's HTTP transport: one endpoint (conventionally `/mcp`) for POST requests, with optional streamed responses; put auth in front of it |
| HTTP+SSE | Legacy clients only | Replaced by Streamable HTTP in the 2025 spec revisions; keep only for backward compatibility |

Default to stdio for local tools and Streamable HTTP for anything remote. Check the SDK version you install for the exact transport class names.

## Client Configuration

### Claude Code (project `.mcp.json`)

```json
{
  "mcpServers": {
    "project-tools": {
      "command": "node",
      "args": ["dist/index.js"],
      "env": {
        "PROJECT_ROOT": "/path/to/project",
        "DATABASE_URL": "${DATABASE_URL}"
      }
    },
    "remote-api-tools": {
      "type": "http",
      "url": "https://mcp.mycompany.com/mcp",
      "headers": {
        "Authorization": "Bearer ${MCP_API_TOKEN}"
      }
    }
  }
}
```

Claude Desktop reads the same `mcpServers` shape from `claude_desktop_config.json`. Keep secrets in environment variables, never inline.

## Versioning Strategy

- **Additive changes** (new tools, new optional parameters): non-breaking, bump minor version
- **Tool removal or rename**: breaking, requires deprecation period + major version bump
- **Required parameter addition**: breaking, consider making it optional with a default instead
- **Response format changes**: potentially breaking, document in changelog
