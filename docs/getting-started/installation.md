---
title: Installation
---

# Installation

Three ways to get Claude Skills into your workflow, from quickest to most complete.

## Option A: Clone the Full Repository

```bash
git clone https://github.com/borghei/Claude-Skills.git
cd Claude-Skills
```

This gives you all 224 skills, 613 tools, and 25 agents in one checkout.

## Option B: Skill Installer CLI

The built-in installer copies individual skills into your project and configures your AI agent automatically.

```bash
# Install a single skill for Claude Code
python scripts/skill-installer.py install senior-fullstack --agent claude

# Install for Cursor
python scripts/skill-installer.py install senior-fullstack --agent cursor

# List available skills
python scripts/skill-installer.py list
```

The installer:

- Copies the skill folder into your project's `.claude/skills/` (or equivalent)
- Updates your agent's configuration file (CLAUDE.md, .cursorrules, etc.)
- Preserves existing configuration

## Option C: Copy a Skill Manually

Each skill is a self-contained folder. Copy it anywhere you need it.

```bash
# Copy into your project
cp -r engineering/senior-fullstack ~/.claude/skills/senior-fullstack

# Or paste any SKILL.md content directly into your AI assistant's context
```

!!! tip "No dependencies"
    Python tools use the standard library only. No `pip install` needed for most skills.

## Directory Structure After Install

```
your-project/
├── .claude/
│   └── skills/
│       └── senior-fullstack/
│           ├── SKILL.md
│           ├── scripts/
│           └── references/
└── CLAUDE.md  (updated with skill reference)
```

## Auto-Update Configuration

To keep skills current, add a git submodule or use the installer's update command:

```bash
# Submodule approach
git submodule add https://github.com/borghei/Claude-Skills.git skills

# Installer update
python scripts/skill-installer.py update senior-fullstack
```

## Verifying Installation

After installing, verify the skill is accessible:

```bash
# Check that the SKILL.md exists
cat .claude/skills/senior-fullstack/SKILL.md | head -5

# Run a tool from the installed skill
python .claude/skills/senior-fullstack/scripts/code_quality_analyzer.py .
```

See [INSTALLATION.md](https://github.com/borghei/Claude-Skills/blob/main/INSTALLATION.md) in the repo for the full installation reference.
