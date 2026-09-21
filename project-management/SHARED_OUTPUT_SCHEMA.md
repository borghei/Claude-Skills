# PM Skills — Shared Output Format Schema

All Python tools in `project-management/` follow this shared output convention so artifacts move cleanly between Jira, Linear, Confluence, Notion and Markdown without rework.

---

## The `--format` flag

Every PM Python tool MUST support a `--format` flag with these values:

| Value | Purpose | Consumer |
|---|---|---|
| `json` | Machine-readable structured output | scripts, MCP servers, agents |
| `markdown` | GitHub-flavored markdown (default) | PRs, READMEs, GitHub Issues |
| `mermaid` | Mermaid diagrams (story maps, roadmaps, opportunity trees) | GitHub README, Notion, Confluence |
| `confluence` | Confluence storage format (XHTML-ish) | Confluence pages via Atlassian MCP |
| `notion` | Notion-compatible Markdown blocks | Notion pages via API |
| `linear` | Linear-flavored Markdown (mentions, issue refs) | Linear issues via API |

### Default

If `--format` is omitted, tools emit `markdown`.

### CLI signature

```bash
python tool.py --format <json|markdown|mermaid|confluence|notion|linear> [--output file.ext] [other flags]
```

If `--output` is omitted, write to stdout.

---

## Format-specific conventions

### `json`

```json
{
  "schema": "pm/<skill-name>/v1",
  "generated_at": "2026-05-21T00:00:00Z",
  "data": { ... }
}
```

- Always wrap payload under `data` so multiple tools can be chained
- Always include `schema` so consumers can version-check
- ISO-8601 UTC timestamps

### `markdown`

- GitHub-flavored Markdown
- H1 = artifact title, H2 = sections, H3 = sub-sections
- Tables use the GitHub pipe syntax
- Code blocks always tagged with language
- No HTML except `<details>`/`<summary>` for collapsibles

### `mermaid`

Wrap output in a single fenced code block:

````
```mermaid
<graph>
```
````

Supported diagram types per skill (each skill SKILL.md declares which it uses):
- `flowchart TD` — workflow, decision trees
- `graph LR` — dependency maps, opportunity solution trees
- `gantt` — roadmaps
- `journey` — user story maps
- `mindmap` — brainstorm outputs

### `confluence`

Confluence storage format. Use:

- `<h2>`, `<h3>` for headings
- `<table>` with `<tr>/<th>/<td>` for tables
- `<ac:structured-macro ac:name="info">` for callouts
- `<ac:structured-macro ac:name="code">` for code blocks
- `<ac:link><ri:page ri:content-title="..."/></ac:link>` for cross-page links

Tools should produce raw storage format suitable for a Confluence page body (REST API, or the Atlassian Rovo MCP Server `createConfluenceContent` tool -- check its `getContentFormatGuide` tool for the body formats it accepts).

### `notion`

Notion-compatible Markdown extensions:

- `[ ]` task checkboxes
- `> [!NOTE]` / `> [!WARNING]` / `> [!TIP]` callouts
- `---` for dividers
- `# / ## / ###` heading mapping (Notion treats H1 specially in DBs — default to H2 as the root in page bodies)
- Tables use simple pipe syntax (Notion converts)

### `linear`

Linear Markdown:

- `@mentions` rendered as `@username` (caller passes the mapping)
- Issue refs as `[ENG-123]` (do not invent IDs — caller passes)
- Priority labels as `~~Urgent~~ ~~High~~ ~~Medium~~ ~~Low~~ ~~No priority~~` matching Linear's label set
- Status names matching the team's workflow (caller passes)

---

## Schema versioning

When a tool's output schema changes in a breaking way, bump the `schema` field:

```
pm/status-update-generator/v1 → pm/status-update-generator/v2
```

Document the diff in `references/CHANGELOG.md` for that skill.

---

## Validation

Every PM tool ships with a `--demo` flag that produces a valid example output for each supported format. CI can grep for the `schema` field to confirm version consistency.

---

## Adoption checklist (new skills)

- [ ] `--format` flag implemented for all 6 values
- [ ] `--output` flag implemented
- [ ] `--demo` flag produces valid sample for each format
- [ ] `schema` field present in JSON output, versioned
- [ ] Mermaid diagram type documented in SKILL.md (if used)
- [ ] Confluence storage format passes round-trip through Atlassian MCP
- [ ] Notion output verified in a real Notion page
- [ ] Linear output verified in a real Linear issue

---

**Last Updated:** 2026-05-21
**Applies to:** All Python tools in `project-management/` (discovery, execution, career, role-based, integrations)
