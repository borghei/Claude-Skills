---
name: codex-cli-specialist
description: >
  OpenAI Codex CLI and cross-platform skill authoring. Use when setting up Codex CLI,
  converting or syncing skills between Claude Code and Codex, configuring agents/openai.yaml,
  or validating cross-platform skill compatibility.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: development-tools
  updated: 2026-06-17
  tags: [openai-codex, cross-platform, skill-conversion, cli]
---
# Codex CLI Specialist

The agent converts Claude Code skills to Codex-compatible format, validates cross-platform compatibility, and builds skill registry manifests. It generates `agents/openai.yaml` configurations from SKILL.md frontmatter, runs 17 compatibility checks across both platforms, and produces `skills-index.json` for discovery systems.

## Core Capabilities

- **Skill conversion** — turn a Claude Code SKILL.md into a Codex-compatible skill by generating `agents/openai.yaml` and copying scripts/references/assets.
- **Cross-platform validation** — run 17 checks across Claude Code, Codex CLI, and shared categories (frontmatter, openai.yaml, encoding, naming, size).
- **Index building** — scan skill directories and emit a `skills-index.json` manifest for registries, discovery, and version pinning.
- **Codex CLI setup & operation** — install, configure API access, and run with the right approval mode (suggest / auto-edit / full-auto).
- **Dual-target authoring** — write skills that work on both platforms from one shared `scripts/`, `references/`, `assets/` tree.
- **Distribution & sync** — keep Claude Code and Codex in sync via shared repo, CI/CD conversion, or git hooks; publish via GitHub releases.

## When to Use

- Setting up or operating OpenAI Codex CLI.
- Converting or syncing skills between Claude Code and Codex.
- Configuring or reviewing `agents/openai.yaml`.
- Validating a skill for dual-platform compatibility.
- Building a `skills-index.json` for a skill library.

## Clarify First

Before converting or building, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — convert a skill, validate cross-platform compatibility, or build a skills index (selects `codex_skill_converter.py` vs `cross_platform_validator.py` vs `skills_index_builder.py`)
- [ ] **Source path** — the SKILL.md or skill directory to operate on (the input the scripts read)
- [ ] **Strictness** — strict validation mode and whether to fail on warnings (sets `--strict` and the pass/fail gate)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `codex_skill_converter.py` | Convert a Claude Code SKILL.md into Codex format (`agents/openai.yaml`) | `python scripts/codex_skill_converter.py <skill_md> [--output-dir DIR] [--json]` |
| `cross_platform_validator.py` | Run 17 Claude Code + Codex + cross-platform compatibility checks on a skill dir | `python scripts/cross_platform_validator.py <skill_dir> [--strict] [--json]` |
| `skills_index_builder.py` | Build a `skills-index.json` manifest from a directory of skills | `python scripts/skills_index_builder.py <skills_dir> [--output FILE] [--format json\|human] [--category CAT]` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows.md](references/workflows.md)** — Quick Start, Tools Overview, the 5 core workflows (install, author, convert, validate, build index), Common Patterns, and deep per-tool parameter/output reference. Read when running a workflow or needing exact tool arguments.
- **[references/configuration-and-distribution.md](references/configuration-and-distribution.md)** — `agents/openai.yaml` structure, discovery/locations, invocation patterns, cross-platform patterns, frontmatter compatibility, install/versioning, and sync/CI/CD/GitHub distribution. Read when configuring openai.yaml or distributing a library.
- **[references/best-practices-and-troubleshooting.md](references/best-practices-and-troubleshooting.md)** — best practices (authoring, Codex usage, cross-platform, performance), anti-patterns, troubleshooting table, and success criteria. Read before shipping or when a tool misbehaves.
- **[references/codex-cli-guide.md](references/codex-cli-guide.md)** — full Codex CLI reference: installation, configuration, approval modes, skill system, invocation, built-in features, environment variables.
- **[references/cross-platform-skills.md](references/cross-platform-skills.md)** — writing skills for multiple agents (Claude Code, Codex, Cursor, Copilot, Goose): platform comparison, universal structure, per-platform config files, template.
- **[assets/openai-yaml-template.yaml](assets/openai-yaml-template.yaml)** — production-grade Codex config template (instructions, tools, model selection, versioning).

## Scope & Limitations

**This skill covers:**
- Installing, configuring, and operating OpenAI Codex CLI
- Converting Claude Code SKILL.md files into Codex-compatible format with `agents/openai.yaml`
- Validating skill directories for dual-platform (Claude Code + Codex CLI) compatibility
- Building skill registry manifests (`skills-index.json`) for discovery and distribution

**This skill does NOT cover:**
- Writing the actual domain logic inside Python tool scripts (see [senior-fullstack](../senior-fullstack/SKILL.md), [code-reviewer](../code-reviewer/SKILL.md), or the relevant domain skill)
- Cursor, Windsurf, Cline, or Aider platform-specific configuration (see [standards/](../../standards/) and root-level dotfiles like `.cursorrules`, `.windsurfrules`)
- OpenAI API key management, billing, or rate-limit troubleshooting (out of scope -- refer to OpenAI documentation)
- Automated testing or CI/CD pipeline authoring beyond skill validation (see [senior-devops](../senior-devops/SKILL.md) and [templates/](../../templates/))

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| [code-reviewer](../code-reviewer/SKILL.md) | Convert code-reviewer's SKILL.md to Codex format so it can run in Codex CLI | `codex_skill_converter.py` reads code-reviewer's SKILL.md and generates `agents/openai.yaml` |
| [senior-fullstack](../senior-fullstack/SKILL.md) | Validate fullstack skill's cross-platform compatibility after adding Codex support | `cross_platform_validator.py` checks both SKILL.md frontmatter and openai.yaml structure |
| [senior-devops](../senior-devops/SKILL.md) | Embed skill validation and index building into CI/CD pipelines | DevOps workflows call `cross_platform_validator.py --strict --json` and `skills_index_builder.py` as pipeline steps |
| [tech-stack-evaluator](../tech-stack-evaluator/SKILL.md) | Evaluate whether Codex CLI fits a project's AI tooling stack | Tech stack evaluator references Codex CLI capabilities and configuration patterns from this skill |
| [senior-architect](../senior-architect/SKILL.md) | Architect multi-agent skill systems that span Claude Code and Codex CLI | Architect uses cross-platform skill patterns and index manifests to plan skill distribution |
