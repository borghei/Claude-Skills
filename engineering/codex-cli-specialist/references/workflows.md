# Workflows & Tools Overview

Read this when running the end-to-end conversion, authoring, validation, or
index-building workflows, or when you need the detailed behavior of each tool.

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

See the complete production-grade template at [../assets/openai-yaml-template.yaml](../assets/openai-yaml-template.yaml), which includes instructions, tools, model selection, and versioning.

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

**Purpose:** Validates that a skill directory is compatible with both Claude Code and Codex CLI by running up to 21 checks (13 when no `agents/openai.yaml` exists yet) across three categories: Claude Code compatibility, Codex CLI compatibility, and cross-platform checks.

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
