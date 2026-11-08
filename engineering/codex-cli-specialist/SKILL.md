---
name: codex-cli-specialist
description: >
  Converts Claude Code skills to OpenAI Codex format (agents/openai.yaml), checks dual-platform
  compatibility and builds a skills index. Use when porting or syncing skills to Codex, or setting
  up Codex CLI for a skill library.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: development-tools
  updated: 2026-11-08
  tags: [openai-codex, cross-platform, skill-conversion, cli]
---
# Codex CLI Specialist

The agent converts Claude Code skills to Codex-compatible format, validates cross-platform compatibility, and builds skill registry manifests. It generates `agents/openai.yaml` configurations from SKILL.md frontmatter, runs up to 21 compatibility checks across both platforms, and produces `skills-index.json` for discovery systems.

## Core Capabilities

- **Skill conversion** — turn a Claude Code SKILL.md into a Codex-compatible skill by generating `agents/openai.yaml` and copying scripts/references/assets.
- **Cross-platform validation** — run up to 21 checks across Claude Code, Codex CLI, and shared categories (frontmatter, openai.yaml, encoding, naming, size).
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

Before converting or building, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** convert a skill, validate cross-platform compatibility, or build a skills index (selects `codex_skill_converter.py` vs `cross_platform_validator.py` vs `skills_index_builder.py`).
- **Source path:** the SKILL.md or skill directory to operate on (the input the scripts read).
- **Strictness:** strict validation mode and whether to fail on warnings (sets `--strict` and the pass/fail gate).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start Workflow

```bash
# 1. Convert a skill. Without --output-dir it writes agents/openai.yaml into the source skill.
python scripts/codex_skill_converter.py ../code-tour/SKILL.md --output-dir /tmp/code-tour-codex

# 2. Validate both sides: Claude frontmatter, openai.yaml structure, encoding, naming, size
python scripts/cross_platform_validator.py /tmp/code-tour-codex        # 21/21, exit 0
python scripts/cross_platform_validator.py ../code-tour                 # no openai.yaml yet, exit 1

# 3. Build a skills-index.json for a directory of skills
python scripts/skills_index_builder.py .. --output /tmp/skills-index.json --format human
```

## Tools Overview

| Tool | Purpose | Key flags |
|------|---------|-----------|
| `codex_skill_converter.py` | Generate `agents/openai.yaml` from SKILL.md frontmatter and copy scripts/references/assets | `--output-dir DIR`, `--json` |
| `cross_platform_validator.py` | Up to 21 checks (13 without `agents/openai.yaml`) across Claude Code, Codex and shared rules | `--strict` (warnings fail), `--json` |
| `skills_index_builder.py` | Scan skill folders into a `skills-index.json` manifest | `--output FILE`, `--format json\|human`, `--category CAT` |

The generated `agents/openai.yaml` leaves `model` unset so the skill inherits the user's Codex CLI
default; pin a model only when the skill truly needs one, using an id from OpenAI's current list.
Codex CLI flags and config file names have changed between releases, so confirm commands from
`references/codex-cli-guide.md` with `codex --help` on the installed version.

**Exit codes.** `0` converted / compatible / index written; `1` conversion failed or the skill is
not compatible (with `--strict`, warnings count); `2` the SKILL.md or directory does not exist.

**Done when:** the validator passes on the converted skill, a Codex session picks the skill up and
runs one of its scripts, and the Claude Code copy still passes its own lint.

## Anti-Patterns

### Forking the skill per platform
**Mistake:** Keeping a Claude copy and a Codex copy of the same skill and editing them separately.
**Why it happens:** Converting once feels simpler than wiring a sync.
**Instead:** Keep one `scripts/`, `references/` and `assets/` tree and regenerate `agents/openai.yaml` from SKILL.md in CI or a hook.

### Pinning model ids in skill config
**Mistake:** Hard-coding a model name in every `openai.yaml`.
**Why it happens:** Templates often ship with one filled in.
**Instead:** Omit `model` and inherit the CLI default; pinned ids go stale and break when a model is retired.

### Trusting the conversion blindly
**Mistake:** Shipping the generated `openai.yaml` without reading it.
**Why it happens:** The converter prints "Conversion complete".
**Instead:** Read the instructions and tool list it extracted, then run the validator and one real Codex invocation.

## Files

- `scripts/codex_skill_converter.py`, `scripts/cross_platform_validator.py`, `scripts/skills_index_builder.py` — the three CLIs above.
- `assets/openai-yaml-template.yaml` — annotated `agents/openai.yaml` template.
- `references/` — workflows, configuration and distribution, Codex CLI guide, cross-platform authoring, best practices.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows.md](references/workflows.md)** — Quick Start, Tools Overview, the 5 core workflows (install, author, convert, validate, build index), Common Patterns, and deep per-tool parameter/output reference. Read when running a workflow or needing exact tool arguments.
- **[references/configuration-and-distribution.md](references/configuration-and-distribution.md)** — `agents/openai.yaml` structure, discovery/locations, invocation patterns, cross-platform patterns, frontmatter compatibility, install/versioning, and sync/CI/CD/GitHub distribution. Read when configuring openai.yaml or distributing a library.
- **[references/best-practices-and-troubleshooting.md](references/best-practices-and-troubleshooting.md)** — best practices (authoring, Codex usage, cross-platform, performance), anti-patterns, troubleshooting table, and success criteria. Read before shipping or when a tool misbehaves.
- **[references/codex-cli-guide.md](references/codex-cli-guide.md)** — full Codex CLI reference: installation, configuration, approval modes, skill system, invocation, built-in features, environment variables.
- **[references/cross-platform-skills.md](references/cross-platform-skills.md)** — writing skills for multiple agents (Claude Code, Codex, Cursor, Copilot, Goose): platform comparison, universal structure, per-platform config files, template.
- **[assets/openai-yaml-template.yaml](assets/openai-yaml-template.yaml)** — annotated Codex config template (instructions, tools, optional model, versioning).

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

## See Also

- [code-reviewer](../code-reviewer/SKILL.md) — a multi-script skill that makes a good first conversion test.
- [claude-code-mastery](../claude-code-mastery/SKILL.md) — authoring the Claude Code side of a skill.
- [senior-devops](../senior-devops/SKILL.md) — wiring validation and index builds into CI.
