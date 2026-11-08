# Codex Configuration, Cross-Platform Patterns & Distribution

Read this when configuring `agents/openai.yaml`, structuring a dual-target skill,
installing/managing skills locally, or distributing a skill library.

---

## Codex CLI Configuration Deep Dive

### agents/openai.yaml Structure

The `agents/openai.yaml` file is the primary configuration for Codex CLI skills. It tells Codex how to discover, describe, and invoke the skill.

```yaml
# Required fields
name: skill-name                    # Unique identifier (kebab-case)
description: >                      # What the skill does (for discovery)
  Expert guidance for X. Analyzes Y and generates Z.

# Instructions define the skill's behavior
instructions: |
  You are a senior X specialist. When the user asks about Y:
  1. First, analyze the context
  2. Then, apply framework Z
  3. Finally, produce output in format W

  Always follow these principles:
  - Principle A
  - Principle B

# Tools expose scripts to the agent
tools:
  - name: tool_name                 # Tool identifier (snake_case)
    description: >                  # When to use this tool
      Analyzes X and produces Y report
    command: python scripts/tool.py # Execution command
    args:                           # Optional: define accepted arguments
      - name: input_path
        description: Path to input file
        required: true
      - name: output_format
        description: Output format (json or text)
        required: false
        default: text

# Optional metadata
# model: <model-id>               # optional; omit to inherit the CLI default
version: 1.0.0                     # Skill version
```

### Skill Discovery and Locations

Codex CLI discovers skills from these locations (in priority order):

1. **Project-local:** `.codex/skills/` in the current working directory
2. **User-global:** `~/.codex/skills/` for user-wide skills
3. **System-wide:** `/usr/local/share/codex/skills/` (rare, admin-managed)
4. **Registry:** Remote skills index (when configured)

**Precedence rule:** Project-local overrides user-global overrides system-wide.

```bash
# Install a skill locally to a project
cp -r my-skill/ .codex/skills/my-skill/

# Install globally for all projects
cp -r my-skill/ ~/.codex/skills/my-skill/
```

### Invocation Patterns

```bash
# Direct invocation by name
codex --skill code-reviewer "review the latest PR"

# Codex auto-discovers relevant skills from context
codex "analyze code quality of the auth module"

# Chain with specific approval mode
codex --approval-mode auto-edit --skill senior-fullstack \
  "scaffold a Next.js app with GraphQL"

# Pass files as context
codex --skill code-reviewer --file src/auth.ts "review this file"
```

---

## Cross-Platform Skill Patterns

### Shared Structure Convention

A skill that works on both Claude Code and Codex CLI follows this layout:

```
my-skill/
├── SKILL.md              # Claude Code reads this (primary documentation)
├── agents/
│   └── openai.yaml       # Codex CLI reads this (agent configuration)
├── scripts/              # Shared - both platforms execute these
│   ├── tool_a.py
│   └── tool_b.py
├── references/           # Shared - knowledge base
│   └── guide.md
└── assets/               # Shared - templates and resources
    └── template.yaml
```

**Key insight:** `SKILL.md` and `agents/openai.yaml` serve the same purpose (skill definition) for different platforms. The `scripts/`, `references/`, and `assets/` directories are fully shared.

### Frontmatter Compatibility

Claude Code and Codex use different frontmatter fields. A cross-platform SKILL.md should include all relevant fields:

```yaml
---
# Claude Code fields (required)
name: my-skill
description: This skill should be used when the user asks to "do X"...

# Extended metadata (optional, used by both)
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: development-tools

# Codex-specific hints (optional, ignored by Claude Code)
codex:
  approval_mode: suggest
---
```

### Dual-Target Skill Layout

When writing instructions in SKILL.md, structure them so they work regardless of platform:

1. **Use standard markdown** - both platforms parse markdown well
2. **Reference scripts by relative path** - `scripts/tool.py` works everywhere
3. **Show both invocation patterns** - document Claude Code natural language and Codex CLI command-line usage side by side

---

## Skill Installation and Management

### Installing Skills Locally

```bash
# Clone a skill into your project
git clone https://github.com/org/skills-repo.git /tmp/skills
cp -r /tmp/skills/code-reviewer .codex/skills/code-reviewer

# Or use a git submodule for version tracking
git submodule add https://github.com/org/skills-repo.git .codex/skills-repo
```

### Managing and Versioning Skills

```bash
# List installed skills
ls -d .codex/skills/*/

# Update all skills from source
cd .codex/skills-repo && git pull origin main
```

Use `skills-index.json` for version pinning across team members. The index builder tool generates this manifest automatically.

---

## Integration Points

### Syncing Skills Between Claude Code and Codex

**Strategy 1: Shared repository (recommended)** - Keep all skills in one repo with both `SKILL.md` and `agents/openai.yaml`. Both platforms read from the same source.

**Strategy 2: CI/CD conversion** - Maintain Claude Code skills as source of truth. Use a GitHub Actions workflow that triggers on `**/SKILL.md` changes to auto-run `codex_skill_converter.py` and commit the generated `agents/openai.yaml` files.

**Strategy 3: Git hooks** - Add a pre-commit hook that detects modified `SKILL.md` files and regenerates `agents/openai.yaml` automatically before each commit.

### CI/CD for Skill Libraries

Add a validation workflow that runs `cross_platform_validator.py --strict --json` on all skill directories during push/PR, and uses `skills_index_builder.py` to generate and upload an updated `skills-index.json` artifact.

### GitHub-Based Skill Distribution

```bash
# Tag, build index, and create release
git tag v1.0.0 && git push origin v1.0.0
python skills_index_builder.py . --output skills-index.json
gh release create v1.0.0 skills-index.json --title "Skills v1.0.0"
```
