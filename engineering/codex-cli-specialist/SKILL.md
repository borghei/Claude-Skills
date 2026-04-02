---
name: codex-cli-specialist
description: >
  This skill should be used when the user asks to "set up Codex CLI", "convert
  skills for Codex", "write cross-platform AI skills", "configure
  agents/openai.yaml", "build skills index", "validate skill compatibility",
  "sync skills between Claude Code and Codex", or "optimize Codex CLI
  workflows". Use for OpenAI Codex CLI mastery, cross-platform skill authoring,
  skill conversion, and multi-agent compatibility patterns.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: development-tools
  updated: 2026-03-31
  tags: [openai-codex, cross-platform, skill-conversion, cli]
---
# Codex CLI Specialist

The agent converts Claude Code skills to Codex-compatible format, validates cross-platform compatibility, and builds skill registry manifests. It generates `agents/openai.yaml` configurations from SKILL.md frontmatter, runs 17 compatibility checks across both platforms, and produces `skills-index.json` for discovery systems.

## Table of Contents

- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
- [Core Workflows](#core-workflows)
- [Codex CLI Configuration Deep Dive](#codex-cli-configuration-deep-dive)
- [Cross-Platform Skill Patterns](#cross-platform-skill-patterns)
- [Skill Installation and Management](#skill-installation-and-management)
- [Integration Points](#integration-points)
- [Best Practices](#best-practices)
- [Reference Documentation](#reference-documentation)
- [Common Patterns Quick Reference](#common-patterns-quick-reference)

---

## Quick Start

```bash
# Install Codex CLI
npm install -g @openai/codex

# Verify installation
codex --version

# Convert an existing Claude Code skill to Codex format
python scripts/codex_skill_converter.py path/to/SKILL.md --output-dir ./converted

# Validate a skill works on both Claude Code and Codex
python scripts/cross_platform_validator.py path/to/skill-dir

# Build a skills index from a directory of skills
python scripts/skills_index_builder.py /path/to/skills --output skills-index.json
```

---

## Tools Overview

### 1. Codex Skill Converter

Converts a Claude Code SKILL.md into Codex-compatible format by generating an `agents/openai.yaml` configuration and restructuring metadata.

**Input:** Path to a Claude Code SKILL.md file
**Output:** Codex-compatible skill directory with agents/openai.yaml

**Usage:**
```bash
# Convert a single skill
python scripts/codex_skill_converter.py my-skill/SKILL.md

# Specify output directory
python scripts/codex_skill_converter.py my-skill/SKILL.md --output-dir ./codex-skills/my-skill

# JSON output for automation
python scripts/codex_skill_converter.py my-skill/SKILL.md --json
```

**What it does:**
- Parses YAML frontmatter from SKILL.md
- Extracts name, description, and metadata
- Generates agents/openai.yaml with proper schema
- Copies scripts, references, and assets
- Reports conversion status and any warnings

---

### 2. Cross-Platform Validator

Validates that a skill directory is compatible with both Claude Code and Codex CLI environments.

**Input:** Path to a skill directory
**Output:** Validation report with pass/fail status and recommendations

**Usage:**
```bash
# Validate a skill directory
python scripts/cross_platform_validator.py my-skill/

# Strict mode - treat warnings as errors
python scripts/cross_platform_validator.py my-skill/ --strict

# JSON output
python scripts/cross_platform_validator.py my-skill/ --json
```

**Checks performed:**
- SKILL.md exists and has valid YAML frontmatter
- Required frontmatter fields present (name, description)
- Description uses third-person format for auto-discovery
- agents/openai.yaml exists and is valid YAML
- scripts/ directory contains executable Python files
- No external dependencies beyond standard library
- File structure matches expected patterns

---

### 3. Skills Index Builder

Builds a `skills-index.json` manifest from a directory of skills, useful for skill registries and discovery systems.

**Input:** Path to a directory containing skill subdirectories
**Output:** JSON manifest with skill metadata

**Usage:**
```bash
# Build index from skills directory
python scripts/skills_index_builder.py /path/to/skills

# Custom output file
python scripts/skills_index_builder.py /path/to/skills --output my-index.json

# Human-readable output
python scripts/skills_index_builder.py /path/to/skills --format human

# Include only specific categories
python scripts/skills_index_builder.py /path/to/skills --category engineering
```

**Output includes:**
- Skill name, description, version
- Available scripts and tools
- Category and domain classification
- File counts and sizes
- Platform compatibility flags

---

## Core Workflows

### Workflow 1: Install and Configure Codex CLI

**Step 1: Install Codex CLI**

```bash
# Install globally via npm
npm install -g @openai/codex

# Verify installation
codex --version
codex --help
```

**Step 2: Configure API access**

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Or configure via the CLI
codex configure
```

**Step 3: Choose an approval mode and run**

```bash
# suggest (default) - you approve each change
codex --approval-mode suggest "refactor the auth module"

# auto-edit - auto-applies file edits, asks before shell commands
codex --approval-mode auto-edit "add input validation"

# full-auto - fully autonomous (use in sandboxed environments)
codex --approval-mode full-auto "set up test infrastructure"
```

---

### Workflow 2: Author a Codex Skill from Scratch

**Step 1: Create directory structure**

```bash
mkdir -p my-skill/agents
mkdir -p my-skill/scripts
mkdir -p my-skill/references
mkdir -p my-skill/assets
```

**Step 2: Write SKILL.md with compatible frontmatter**

```markdown
---
name: my-skill
description: This skill should be used when the user asks to "do X",
  "perform Y", or "analyze Z". Use for domain expertise, automation,
  and best practice enforcement.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: development-tools
---

# My Skill

Description and workflows here...
```

**Step 3: Create agents/openai.yaml**

```yaml
# Use the template from assets/openai-yaml-template.yaml
name: my-skill
description: >
  Expert guidance for X, Y, and Z.
instructions: |
  You are an expert at X. When the user asks about Y,
  follow these steps...
tools:
  - name: my_tool
    description: Runs the my_tool.py script
    command: python scripts/my_tool.py
```

**Step 4: Add Python tools**

```bash
# Create your script
touch my-skill/scripts/my_tool.py
chmod +x my-skill/scripts/my_tool.py
```

**Step 5: Validate the skill**

```bash
python cross_platform_validator.py my-skill/
```

---

### Workflow 3: Convert Claude Code Skills to Codex

**Step 1: Identify skills to convert**

```bash
# List all skills in a directory
find engineering/ -name "SKILL.md" -type f
```

**Step 2: Run the converter**

```bash
# Convert a single skill
python scripts/codex_skill_converter.py engineering/code-reviewer/SKILL.md \
  --output-dir ./codex-ready/code-reviewer

# Batch convert (shell loop)
for skill_md in engineering/*/SKILL.md; do
  skill_name=$(basename $(dirname "$skill_md"))
  python scripts/codex_skill_converter.py "$skill_md" \
    --output-dir "./codex-ready/$skill_name"
done
```

**Step 3: Review and adjust generated openai.yaml**

The converter generates a baseline `agents/openai.yaml`. Review it for:
- Accuracy of the instructions field
- Completeness of the tools list
- Correct command paths for scripts

**Step 4: Validate the converted skill**

```bash
python scripts/cross_platform_validator.py ./codex-ready/code-reviewer
```

---

### Workflow 4: Validate Cross-Platform Compatibility

```bash
# Run validator on a skill (outputs PASS/WARN/FAIL for each check)
python scripts/cross_platform_validator.py my-skill/

# Strict mode (warnings become errors)
python scripts/cross_platform_validator.py my-skill/ --strict --json
```

The validator checks both Claude Code compatibility (SKILL.md, frontmatter, scripts) and Codex CLI compatibility (agents/openai.yaml, tool references), plus cross-platform checks (UTF-8 encoding, skill size, name consistency).

---

### Workflow 5: Build and Publish a Skills Index

```bash
# Build index from a directory of skills
python scripts/skills_index_builder.py ./engineering --output skills-index.json

# Human-readable summary
python scripts/skills_index_builder.py ./engineering --format human
```

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
model: o4-mini                      # Preferred model
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
  model: o4-mini
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

---

## Best Practices

### Skill Authoring

1. **Keep descriptions discovery-friendly** - Use third-person, keyword-rich descriptions that start with "This skill should be used when..."
2. **One skill, one concern** - Each skill should cover a coherent domain, not an entire discipline
3. **Scripts use standard library only** - No pip install requirements for core functionality
4. **Include both SKILL.md and agents/openai.yaml** - Makes the skill usable on any platform immediately
5. **Test scripts independently** - Every Python tool should work standalone via `python script.py --help`

### Codex CLI Usage

1. **Start with suggest mode** - Use `--approval-mode suggest` until you trust the skill
2. **Scope skill contexts narrowly** - Pass specific files with `--file` instead of entire directories
3. **Use project-local skills** - Avoid global installation for project-specific skills
4. **Pin versions in teams** - Use skills-index.json for version consistency across team members
5. **Review generated configs** - Always review auto-generated `agents/openai.yaml` before deploying

### Cross-Platform Compatibility

1. **Relative paths everywhere** - Scripts reference `scripts/`, `references/`, `assets/` with relative paths
2. **No shell-specific syntax** - Avoid bash-isms in scripts; stick to Python for portability
3. **Standard YAML only** - No YAML extensions or anchors that might confuse parsers
4. **UTF-8 encoding** - All files should be UTF-8 encoded
5. **Unix line endings** - Use LF, not CRLF (configure `.gitattributes`)

### Performance

1. **Keep skills small** - Under 1MB total for fast loading and distribution
2. **Minimize reference files** - Include only essential knowledge, not entire docs
3. **Lazy-load expensive tools** - Split heavy scripts into separate files
4. **Cache tool outputs** - Use `--json` output for piping into other tools

---

## Reference Documentation

| Resource | Location | Description |
|----------|----------|-------------|
| Codex CLI Guide | [references/codex-cli-guide.md](references/codex-cli-guide.md) | Installation, configuration, features |
| Cross-Platform Skills | [references/cross-platform-skills.md](references/cross-platform-skills.md) | Multi-agent compatibility guide |
| openai.yaml Template | [assets/openai-yaml-template.yaml](assets/openai-yaml-template.yaml) | Ready-to-use Codex config template |

---

## Common Patterns Quick Reference

### Pattern: Quick Skill Conversion

```bash
# One-liner: convert and validate
python scripts/codex_skill_converter.py skill/SKILL.md && \
  python scripts/cross_platform_validator.py skill/
```

### Pattern: Batch Validation

```bash
# Validate all skills in a directory
for d in */; do
  [ -f "$d/SKILL.md" ] && python scripts/cross_platform_validator.py "$d"
done
```

### Pattern: Generate Index for Registry

```bash
python scripts/skills_index_builder.py . --output skills-index.json --format json
```

### Pattern: Codex Quick Task

```bash
# Run a quick task with a skill
codex --approval-mode auto-edit --skill codex-cli-specialist \
  "convert all skills in engineering/ to Codex format"
```

### Pattern: Minimal Codex Skill

```yaml
# agents/openai.yaml - absolute minimum
name: my-skill
description: Does X for Y
instructions: You are an expert at X. Help the user with Y.
```

### Pattern: Full-Featured Codex Skill

See the complete production-grade template at [assets/openai-yaml-template.yaml](assets/openai-yaml-template.yaml), which includes instructions, tools, model selection, and versioning.

---

## Anti-Patterns

- **Converting without reviewing** -- auto-generated `agents/openai.yaml` needs human review for instruction accuracy and tool command paths
- **Global skill installation** -- project-specific skills should stay in `.codex/skills/`, not `~/.codex/skills/`, to avoid version conflicts across projects
- **Duplicating logic in SKILL.md and openai.yaml** -- keep `SKILL.md` as source of truth; `openai.yaml` should reference shared scripts, not rewrite instructions
- **Shell-specific syntax in scripts** -- bash-isms break on Windows; stick to Python for all automation logic
- **Ignoring strict validation warnings** -- optional directories (`references/`, `assets/`) that are missing degrade skill quality even if not required
- **Skipping version pinning** -- teams without `skills-index.json` version pinning get inconsistent behavior across members

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Converter produces empty `instructions` field | SKILL.md has no `## Best Practices` or `### Workflow` headings for the parser to extract | Add clearly labeled `### Workflow N:` and `## Best Practices` sections with bulleted items in the source SKILL.md |
| Validator fails with "No valid YAML frontmatter" | SKILL.md does not start with `---` on the very first line, or the closing `---` delimiter is missing | Ensure the file begins with `---` on line 1, followed by frontmatter fields, followed by a closing `---` line with no leading whitespace |
| `agents/openai.yaml` tool references show "missing script" error | The `command` field path in openai.yaml does not match the actual filename in `scripts/` | Verify that each tool's `command` value uses the exact filename (case-sensitive) under `scripts/` and uses the prefix `python scripts/` |
| Index builder returns 0 skills | Subdirectories scanned do not contain a `SKILL.md` file, or the target path points to a single skill instead of a parent directory | Pass the parent directory that contains skill subdirectories, not a single skill folder. Hidden directories (dot-prefixed) are also skipped |
| Validator warns "Description should use third-person, discovery-friendly format" | The `description` frontmatter field does not contain recognized discovery patterns like "This skill should be used when" | Rewrite the description to begin with "This skill should be used when the user asks to..." or include verbs like "analyzes", "generates", "provides" |
| Converter overwrites existing `agents/openai.yaml` without backup | Running the converter with output-dir set to the same directory as the source skill | Use `--output-dir` to write to a separate directory, or manually back up the existing `agents/openai.yaml` before converting |
| Strict validation fails on optional missing directories | Running `--strict` treats warnings (missing `references/`, `assets/`, license field) as errors | Either create the missing optional directories and fields, or run without `--strict` to allow warnings |

---

## Success Criteria

- Converted skills pass `cross_platform_validator.py --strict` with zero errors and zero warnings
- Generated `agents/openai.yaml` contains a valid `name`, `description`, `instructions`, and `tools` section that matches the source SKILL.md
- Skills index built from 50+ skill directories completes in under 10 seconds with accurate metadata extraction
- All three Python tools exit with code 0 on valid input and exit with code 1 on invalid input, enabling reliable CI/CD integration
- Batch conversion of an entire skill domain (e.g., all `engineering/` skills) produces Codex-compatible output with no manual edits required for structure
- Cross-platform skills load and function correctly in both Claude Code (via SKILL.md) and Codex CLI (via `agents/openai.yaml`) without platform-specific workarounds
- Generated `skills-index.json` is valid JSON parseable by any standard JSON parser and includes complete metadata for every scanned skill

---

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

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| [code-reviewer](../code-reviewer/SKILL.md) | Convert code-reviewer's SKILL.md to Codex format so it can run in Codex CLI | `codex_skill_converter.py` reads code-reviewer's SKILL.md and generates `agents/openai.yaml` |
| [senior-fullstack](../senior-fullstack/SKILL.md) | Validate fullstack skill's cross-platform compatibility after adding Codex support | `cross_platform_validator.py` checks both SKILL.md frontmatter and openai.yaml structure |
| [senior-devops](../senior-devops/SKILL.md) | Embed skill validation and index building into CI/CD pipelines | DevOps workflows call `cross_platform_validator.py --strict --json` and `skills_index_builder.py` as pipeline steps |
| [tech-stack-evaluator](../tech-stack-evaluator/SKILL.md) | Evaluate whether Codex CLI fits a project's AI tooling stack | Tech stack evaluator references Codex CLI capabilities and configuration patterns from this skill |
| [senior-architect](../senior-architect/SKILL.md) | Architect multi-agent skill systems that span Claude Code and Codex CLI | Architect uses cross-platform skill patterns and index manifests to plan skill distribution |

---

## Tool Reference

### codex_skill_converter.py

**Purpose:** Converts a Claude Code SKILL.md into Codex-compatible format by parsing YAML frontmatter, extracting scripts, building instructions, and generating an `agents/openai.yaml` configuration file.

**Usage:**
```bash
python scripts/codex_skill_converter.py <skill_md> [--output-dir DIR] [--json]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skill_md` | positional | Yes | -- | Path to the Claude Code SKILL.md file to convert |
| `--output-dir` | string | No | Same as source directory | Output directory for the converted skill. If different from source, copies `scripts/`, `references/`, `assets/`, and `SKILL.md` alongside the generated `agents/openai.yaml` |
| `--json` | flag | No | Off (human-readable) | Output results in JSON format instead of human-readable text |

**Example:**
```bash
python scripts/codex_skill_converter.py engineering/code-reviewer/SKILL.md \
  --output-dir ./codex-ready/code-reviewer --json
```

**Output Formats:**
- **Human-readable (default):** Displays source path, output path, status (SUCCESS/ERROR), lists of generated files, copied files, warnings, and errors
- **JSON (`--json`):** Structured object with keys: `status`, `source`, `output_dir`, `files_generated`, `files_copied`, `warnings`, `errors`

---

### cross_platform_validator.py

**Purpose:** Validates that a skill directory is compatible with both Claude Code and Codex CLI by running 17 checks across three categories: Claude Code compatibility, Codex CLI compatibility, and cross-platform checks.

**Usage:**
```bash
python scripts/cross_platform_validator.py <skill_dir> [--strict] [--json]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skill_dir` | positional | Yes | -- | Path to the skill directory to validate |
| `--strict` | flag | No | Off | Treat warnings as errors -- the skill is marked NOT COMPATIBLE if any warnings exist |
| `--json` | flag | No | Off (human-readable) | Output results in JSON format instead of human-readable text |

**Example:**
```bash
python scripts/cross_platform_validator.py engineering/codex-cli-specialist/ --strict --json
```

**Output Formats:**
- **Human-readable (default):** Groups checks by platform (Claude Code Compatibility, Codex CLI Compatibility, Cross-Platform Checks) with `[PASS]`, `[WARN]`, `[FAIL]`, or `[INFO]` status per check, plus an overall compatibility verdict and pass/total count
- **JSON (`--json`):** Structured object with keys: `skill_name`, `skill_path`, `compatible` (boolean), `summary` (total_checks, passed, errors, warnings, info), `checks` (array of check objects with `check`, `platform`, `passed`, `message`, `severity`)

---

### skills_index_builder.py

**Purpose:** Scans a directory of skill subdirectories, extracts metadata from each SKILL.md, and builds a `skills-index.json` manifest for skill registries, discovery systems, and version pinning.

**Usage:**
```bash
python scripts/skills_index_builder.py <skills_dir> [--output FILE] [--format FORMAT] [--category CATEGORY]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skills_dir` | positional | Yes | -- | Path to the directory containing skill subdirectories (each with a SKILL.md) |
| `--output`, `-o` | string | No | stdout | Output file path. If omitted, prints to stdout |
| `--format`, `-f` | choice | No | `json` | Output format: `json` (structured manifest) or `human` (tabular summary) |
| `--category`, `-c` | string | No | None (all categories) | Filter skills by category (matches the `metadata.category` frontmatter field, case-insensitive) |

**Example:**
```bash
python scripts/skills_index_builder.py ./engineering \
  --output skills-index.json --format json --category engineering
```

**Output Formats:**
- **JSON (`json`, default):** Full index object with keys: `version`, `generated_at` (UTC ISO 8601), `source_directory`, `skills_count`, `summary` (total_tools, total_references, total_size, categories, domains, platforms), `skills` (array of skill objects with name, title, description, version, license, category, domain, keywords, tools, references, assets, platforms, size_bytes, size_human, path)
- **Human-readable (`human`):** Tabular display with source, generation timestamp, skill count, totals, category breakdown, platform support counts, and a table of skills with name, version, tool count, and platforms
