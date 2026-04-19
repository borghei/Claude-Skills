# @borghei/claude-skills

Install any skill from the [Claude Skills library](https://github.com/borghei/Claude-Skills) into your AI assistant in one command.

```bash
npx @borghei/claude-skills add senior-fullstack
```

After a global install (`npm i -g @borghei/claude-skills`), the `claude-skills` binary is available directly.

Auto-detects Claude Code, Cursor, Codex, Gemini CLI, Copilot, Windsurf, Cline, Aider and Goose. Installs the skill into the right directory for whichever assistant you're using.

## Commands

```bash
claude-skills list                         # All skills, grouped by domain
claude-skills list --domain engineering    # Filter to one domain
claude-skills search "docker"              # Match name, tags or description
claude-skills info senior-fullstack        # Full detail for one skill

claude-skills add senior-fullstack         # Install into the detected assistant
claude-skills add senior-fullstack --to cursor   # Force target
claude-skills add senior-fullstack --dir ./my-skills  # Install into a specific dir
claude-skills add senior-fullstack --force # Overwrite if already installed

claude-skills update                       # Update every installed skill
claude-skills update senior-fullstack      # Update just one

claude-skills remove senior-fullstack      # Remove an installed skill

claude-skills create my-new-skill          # Scaffold a new skill from the template
```

## Target detection

The CLI detects your AI assistant by looking for marker files in the current directory:

| Marker | Target | Install path |
|---|---|---|
| `.claude/` | Claude Code | `.claude/skills/<name>/` |
| `.codex/` or `AGENTS.md` | Codex | `.codex/skills/<name>/` |
| `.gemini/` or `GEMINI.md` | Gemini CLI | `.gemini/skills/<name>/` |
| `.cursor/` or `.cursorrules` | Cursor | `.cursor/rules/<name>/` |
| `.github/copilot-instructions.md` | GitHub Copilot | `.github/skills/<name>/` |
| `.windsurfrules` | Windsurf | `.ai-skills/<name>/` |
| `.clinerules` | Cline | `.ai-skills/<name>/` |
| `.aider.conf.yml` | Aider | `.ai-skills/<name>/` |
| `.goosehints` | Goose | `.ai-skills/<name>/` |

If the CLI can't detect a target, pass `--to <name>` explicitly.

## Lockfile

Installed skills are tracked in `.claude-skills.json` in the current directory. This file records what's installed, which target, and version, so `update` and `remove` work cleanly.

## Requirements

Node.js 18 or later. No Python required for end users.

## License

MIT + Commons Clause. See [LICENSE](https://github.com/borghei/Claude-Skills/blob/main/LICENSE).
