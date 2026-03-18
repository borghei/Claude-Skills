# AI Skills Library — Agent Instructions

## What This Repository Is

This is the **universal AI skills library** — 204 production-ready skill packages across 13 professional domains with 230+ Python automation tools and 12 sample CI/CD workflows. It works with every major AI coding assistant: Claude Code, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose, and more.

**This is NOT a traditional application.** It's a library of self-contained skill packages meant to be extracted and deployed by users into their own workflows.

## Supported Platforms

| Platform | Config File | Status |
|----------|------------|--------|
| Claude Code | `CLAUDE.md` | Primary |
| OpenAI Codex | `AGENTS.md` | Full |
| Cursor | `.cursorrules` | Full |
| GitHub Copilot | `.github/copilot-instructions.md` | Full |
| Windsurf | `.windsurfrules` | Full |
| Cline | `.clinerules` | Full |
| Goose | `.goosehints` | Full |
| Aider | `AGENTS.md` | Full |
| Jules | `AGENTS.md` | Full |
| RooCode / Kilo Code | `AGENTS.md` | Full |

## Repository Structure

```
├── engineering-team/     # 28 core engineering skills + 66 Python tools
├── engineering/          # 33 advanced architecture skills + 33 Python tools
├── marketing-skill/      # 35 marketing skills + 6 Python tools
├── product-team/         # 8 product skills + 6 Python tools
├── project-management/   # 23 PM skills + 14 Python tools
├── c-level-advisor/      # 26 C-level advisory skills + 4 Python tools
├── ra-qm-team/           # 21 regulatory/quality/compliance skills + 35 Python tools
├── business-growth/      # 16 business & growth skills + 9 Python tools
├── data-analytics/       # 5 data analytics skills
├── hr-operations/        # 4 HR operations skills
├── sales-success/        # 5 sales success skills
├── finance/              # 1 finance skill + 4 Python tools
├── agents/               # 7 production skill agents
├── scripts/              # Skill installer + utility scripts
├── standards/            # Best practices library
└── templates/            # Reusable templates + 12 sample workflows
```

## Skill Package Pattern

Every skill follows the same structure:

```
skill-name/
├── SKILL.md       # Master documentation with workflows
├── scripts/       # Python CLI tools (standard library, no ML/LLM calls)
├── references/    # Expert knowledge bases
└── assets/        # User-facing templates
```

Knowledge flows: `references/` → `SKILL.md` workflows → `scripts/` execution → `assets/` templates.

## Quick Install

```bash
# Browse available skills
python scripts/skill-installer.py list

# Install a skill
python scripts/skill-installer.py install senior-fullstack --agent claude
python scripts/skill-installer.py install content-creator --agent cursor
python scripts/skill-installer.py install ceo-advisor --agent vscode

# Keep skills up to date
python scripts/skill-installer.py update
```

## Code Style

- **Python scripts:** Standard library only, CLI-first with argparse, JSON + human-readable output
- **Markdown:** YAML frontmatter on all SKILL.md files, consistent formatting
- **Commits:** Conventional commits — `feat(domain):`, `fix(tool):`, `docs(skill):`

## Key Principles

1. **Skills are products** — Each skill is deployable as a standalone package
2. **Documentation-driven** — Clear, actionable docs over generic advice
3. **Algorithm over AI** — Deterministic analysis (Python scripts) over LLM calls
4. **Template-heavy** — Ready-to-use templates users customize
5. **Self-contained** — No dependencies between skills

## Anti-Patterns

- Creating dependencies between skills
- Adding complex build systems or test frameworks
- Generic advice instead of specific, actionable frameworks
- LLM/ML calls in scripts (defeats portability)
- Over-documenting file structure
