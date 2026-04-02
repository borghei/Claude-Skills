---
title: Architecture
---

# Repository Architecture

## Directory Layout

```
Claude-Skills/
├── .claude/                  # Claude Code configuration
│   ├── agents/               # 6 subagents (code-reviewer, qa, docs, etc.)
│   └── commands/             # 26 slash commands
├── agents/                   # 19 role-based agents + 7 personas
│   ├── engineering/          # Tech lead, director, code auditor, etc.
│   ├── c-level/              # CEO, CTO, CFO advisors
│   ├── compliance/           # Compliance auditor, CISO advisor
│   ├── marketing/            # Content creator, demand gen, SEO
│   ├── product/              # Product manager
│   └── personas/             # 7 cross-functional personas
├── engineering/              # 76 engineering skills + 224 tools
├── marketing/                # 38 marketing skills + 115 tools
├── c-level-advisor/          # 26 C-level skills + 73 tools
├── product-team/             # 8 product skills + 15 tools
├── project-management/       # 22 PM skills + 53 tools
│   ├── discovery/            # Brainstorming, assumption mapping
│   └── execution/            # PRDs, OKRs, roadmaps, release notes
├── ra-qm-team/              # 21 compliance skills + 38 tools
├── business-growth/          # 16 growth skills + 48 tools
├── finance/                  # 3 finance skills + 10 tools
├── data-analytics/           # 5 analytics skills + 16 tools
├── sales-success/            # 5 sales skills + 15 tools
├── hr-operations/            # 4 HR skills + 12 tools
├── standards/                # Best practices library
├── templates/                # Templates + 12 sample GitHub workflows
├── scripts/                  # Skill installer + utilities
├── docs/                     # MkDocs documentation site
├── skills.json               # Machine-readable skill catalog
├── CLAUDE.md                 # Claude Code config
├── AGENTS.md                 # Codex/Jules config
├── .cursorrules              # Cursor config
├── .windsurfrules            # Windsurf config
├── .clinerules               # Cline config
├── .goosehints               # Goose config
└── GEMINI.md                 # Gemini config
```

## Skill Package Pattern

Each skill is a self-contained folder:

```
skill-name/
├── SKILL.md              # Master documentation
├── scripts/              # Python CLI tools (no ML/LLM calls)
├── references/           # Expert knowledge bases
└── assets/               # User templates
```

**Knowledge flow:** `references/` (expert knowledge) feeds into `SKILL.md` (workflows), which are executed via `scripts/` (automation), and applied using `assets/` (templates).

## Agent Architecture

### Subagents (.claude/agents/)

Subagents run autonomously within Claude Code. They have full tool access and can read/write files, run commands, and interact with git.

### Task Agents (agents/)

Task agents are markdown files that define a role, its skill dependencies, and structured workflows. They are loaded into the AI assistant's context on demand.

### Personas (agents/personas/)

Personas combine skills from multiple domains. They define a professional identity with decision frameworks and communication style.

## Data Files

| File | Purpose |
|---|---|
| `skills.json` | Machine-readable catalog of all 224 skills with metadata |
| `CHANGELOG.md` | Version history and release notes |
| `CONTRIBUTING.md` | Contribution guidelines |
| `LICENSE` | MIT + Commons Clause license |

## Configuration Files

Each AI platform reads a different config file at the project root:

| File | Platform |
|---|---|
| `CLAUDE.md` | Claude Code |
| `AGENTS.md` | OpenAI Codex, Jules |
| `.cursorrules` | Cursor |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `GEMINI.md` | Google Gemini |
| `.windsurfrules` | Windsurf |
| `.clinerules` | Cline |
| `.goosehints` | Goose |

## Design Principles

1. **Skills are products** -- Each skill is deployable as a standalone package
2. **Algorithm over AI** -- Deterministic analysis (Python scripts) over LLM calls
3. **Standard library only** -- No pip dependencies for maximum portability
4. **Self-contained** -- No inter-skill dependencies
5. **Template-heavy** -- Ready-to-use templates that users customize
