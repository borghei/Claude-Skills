---
title: CLI Reference
---

# CLI Reference

## Skill Installer

The skill installer is a Python CLI tool for managing skill installation and updates.

**Location:** `scripts/skill-installer.py`

### Commands

#### install

Install one or more skills to your project.

```bash
python scripts/skill-installer.py install <skill-name> [skill-name ...] [options]
```

| Option | Description | Default |
|---|---|---|
| `--agent` | Target agent: `claude`, `cursor`, `copilot`, `codex`, `windsurf`, `cline`, `aider`, `goose` | `claude` |
| `--target` | Installation directory | `.claude/skills/` |
| `--no-config` | Skip config file updates | `false` |

**Examples:**

```bash
# Install one skill for Claude Code
python scripts/skill-installer.py install senior-fullstack --agent claude

# Install multiple skills for Cursor
python scripts/skill-installer.py install code-reviewer senior-qa --agent cursor

# Install to custom directory
python scripts/skill-installer.py install senior-backend --target ./my-skills/
```

#### list

List all available skills with metadata.

```bash
python scripts/skill-installer.py list [options]
```

| Option | Description |
|---|---|
| `--domain` | Filter by domain (e.g., `engineering`, `marketing`) |
| `--format` | Output format: `text` or `json` |

#### update

Update previously installed skills to the latest version.

```bash
python scripts/skill-installer.py update <skill-name> [skill-name ...]
```

#### info

Show detailed information about a skill.

```bash
python scripts/skill-installer.py info <skill-name>
```

## Python Tool Conventions

All Python tools in `scripts/` folders follow these conventions:

```bash
python path/to/tool.py <input> [options]
```

### Common Options

Most tools support these flags:

| Flag | Description |
|---|---|
| `--format json` | Output as JSON (default: human-readable text) |
| `--format text` | Output as human-readable text |
| `-h`, `--help` | Show help message |
| `--verbose` | Verbose output |

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Error (invalid input, analysis failure) |
| `2` | Invalid arguments |

### Examples

```bash
# Code quality analysis
python engineering/code-reviewer/scripts/code_quality_analyzer.py /path/to/project

# CLAUDE.md optimization
python engineering/claude-code-mastery/scripts/claudemd_optimizer.py CLAUDE.md

# Financial analysis
python finance/financial-analyst/scripts/dcf_valuation.py --revenue 1000000 --growth 0.2

# Security scanning
python engineering/senior-security/scripts/security_scanner.py . --format json
```
