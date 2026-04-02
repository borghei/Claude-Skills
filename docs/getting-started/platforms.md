---
title: Platform Setup
---

# Platform Setup

Claude Skills works with 10 AI coding assistants. Each platform has a different configuration file where you reference skills.

## Supported Platforms

| Platform | Config File | Status |
|---|---|---|
| Claude Code | `CLAUDE.md` | Full support (skills + agents + subagents) |
| OpenAI Codex | `AGENTS.md` | Full support (skills + agents) |
| Cursor | `.cursorrules` | Full support |
| GitHub Copilot | `.github/copilot-instructions.md` | Full support |
| Google Gemini | `GEMINI.md` | Full support |
| Windsurf | `.windsurfrules` | Full support |
| Cline | `.clinerules` | Full support |
| Aider | `.aider.conf.yml` | Full support |
| Goose | `.goosehints` | Full support |
| RooCode | `.roo/rules` | Full support |

## Platform-Specific Setup

=== "Claude Code"

    Claude Code has the deepest integration. It supports SKILL.md references, subagents, slash commands, and hooks.

    ```markdown
    <!-- CLAUDE.md -->
    ## Skills
    When reviewing code, load engineering/code-reviewer/SKILL.md
    When optimizing SEO, load marketing/seo-specialist/SKILL.md
    ```

    **Subagents** live in `.claude/agents/` and run autonomously:
    ```
    > /agents/code-reviewer Review the last 3 commits
    ```

    **Slash commands** live in `.claude/commands/`:
    ```
    > /review        # Run quality gate
    > /security-scan # Run security audit
    > /git:pr        # Create a pull request
    ```

=== "Cursor"

    Add skill references to `.cursorrules` at your project root:

    ```
    # .cursorrules
    When writing backend code, follow engineering/senior-backend/SKILL.md patterns.
    When creating tests, follow engineering/senior-qa/SKILL.md test strategy.
    For database design, apply engineering/database-designer/SKILL.md principles.
    ```

=== "GitHub Copilot"

    Reference skills in `.github/copilot-instructions.md`:

    ```markdown
    ## Code Standards
    Follow engineering/code-reviewer/SKILL.md for all code reviews.
    Apply engineering/senior-security/SKILL.md for security patterns.
    ```

=== "OpenAI Codex"

    Configure in `AGENTS.md` at your project root:

    ```markdown
    ## Skills
    - engineering/senior-fullstack/SKILL.md - Fullstack development
    - marketing/seo-specialist/SKILL.md - SEO optimization
    ```

    See `engineering/codex-cli-specialist/SKILL.md` for the full Codex integration guide.

=== "Windsurf"

    Add to `.windsurfrules`:

    ```
    Follow engineering/senior-frontend/SKILL.md for React/Next.js patterns.
    Apply product-team/product-manager-toolkit/SKILL.md for feature specs.
    ```

=== "Cline / Aider / Goose"

    Each tool has its own config file (`.clinerules`, `.aider.conf.yml`, `.goosehints`). The pattern is the same -- reference the SKILL.md path:

    ```
    Use engineering/senior-fullstack/SKILL.md for development guidelines.
    ```

## Cross-Platform Skills

Every SKILL.md file is platform-agnostic. The same skill works in Claude Code, Cursor, Copilot, and all other supported assistants. Only the configuration file differs.

!!! note "Python tools are universal"
    The `scripts/` folder in each skill contains standard Python CLI tools. They run identically regardless of which AI platform you use.
