# Codex CLI Reference Guide

Comprehensive reference for OpenAI Codex CLI: installation, configuration, skill system, invocation patterns, and advanced features.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Approval Modes](#approval-modes)
- [Skill System](#skill-system)
  - [Skill Locations](#skill-locations)
  - [Skill Discovery](#skill-discovery)
  - [agents/openai.yaml Schema](#agentsopenai-yaml-schema)
  - [Tool Definitions](#tool-definitions)
- [Invocation Patterns](#invocation-patterns)
- [Built-in Features](#built-in-features)
- [Environment Variables](#environment-variables)
- [Sandboxing and Security](#sandboxing-and-security)
- [UI Metadata and Output](#ui-metadata-and-output)
- [Troubleshooting](#troubleshooting)

---

## Overview

Codex CLI is OpenAI's terminal-native coding agent. It connects to OpenAI models (o4-mini, o3, GPT-4.1) and executes tasks autonomously or with human approval. Codex reads, writes, and executes code directly in your local environment.

**Key capabilities:**
- File creation and modification
- Shell command execution
- Multi-step task planning and execution
- Skill-based specialization
- Sandboxed execution for safety

---

## Installation

### Prerequisites

- Node.js 22 or newer
- npm (comes with Node.js)
- Git (recommended)
- An OpenAI API key

### Install via npm

```bash
npm install -g @openai/codex
```

### Verify installation

```bash
codex --version
codex --help
```

### Update to latest

```bash
npm update -g @openai/codex
```

### First-time setup

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Or add to shell profile for persistence
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
source ~/.zshrc

# Run initial configuration
codex configure
```

---

## Configuration

### Configuration file location

Codex CLI reads configuration from:

1. `~/.codex/config.yaml` - Global user config
2. `.codex/config.yaml` - Project-local config (overrides global)

### Configuration options

```yaml
# ~/.codex/config.yaml
model: o4-mini                    # Default model
approval_mode: suggest            # Default approval mode
history: true                     # Enable conversation history
notify: true                      # Desktop notifications on completion
```

### Model selection

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| o4-mini | General coding tasks | Fast | Low |
| o3 | Complex reasoning, architecture | Slower | Higher |
| gpt-4.1 | Broad knowledge, writing | Fast | Medium |

```bash
# Override model per invocation
codex --model o3 "design the database schema"
```

---

## Approval Modes

Codex CLI supports three approval modes that control how much autonomy the agent has.

### suggest (default)

The agent proposes changes. You approve or reject each one.

```bash
codex --approval-mode suggest "add input validation"
```

**Use when:** Learning the tool, working on critical code, reviewing each step.

### auto-edit

The agent automatically applies file edits but asks before executing shell commands.

```bash
codex --approval-mode auto-edit "refactor auth module"
```

**Use when:** You trust the agent with file changes but want to control command execution.

### full-auto

The agent executes everything autonomously. All file edits and shell commands run without approval.

```bash
codex --approval-mode full-auto "set up test infrastructure"
```

**Use when:** Working in sandboxed environments, CI/CD pipelines, or trusted automated workflows. Codex applies network-disabled sandboxing by default in this mode.

---

## Skill System

Skills are modular packages that give Codex specialized capabilities and domain knowledge.

### Skill Locations

Codex discovers skills from these directories (in priority order):

| Priority | Location | Scope |
|----------|----------|-------|
| 1 | `.codex/skills/` | Project-local |
| 2 | `~/.codex/skills/` | User-global |
| 3 | `/usr/local/share/codex/skills/` | System-wide |

**Priority rule:** Project-local skills override global skills with the same name.

### Skill Discovery

When invoked, Codex:

1. Scans skill directories for `agents/openai.yaml` files
2. Reads skill names and descriptions
3. Matches user queries to relevant skills
4. Loads matched skill instructions and tools

**Explicit invocation:**
```bash
codex --skill code-reviewer "review the latest PR"
```

**Auto-discovery:** Codex matches the user prompt against skill descriptions:
```bash
codex "analyze code quality"   # Matches skills with "code quality" in description
```

### agents/openai.yaml Schema

The `agents/openai.yaml` file is the primary skill configuration for Codex CLI.

#### Required fields

```yaml
name: my-skill                    # Unique identifier (kebab-case)
description: >                    # What this skill does (discovery text)
  Expert guidance for X. Analyzes Y, generates Z.
```

#### Recommended fields

```yaml
instructions: |                   # Behavioral instructions for the agent
  You are a senior X specialist.

  When the user asks about Y:
  1. First, analyze the context
  2. Apply framework Z
  3. Produce structured output

tools:                            # Tool definitions (see below)
  - name: analyzer
    description: Analyzes X
    command: python scripts/analyzer.py
```

#### Optional fields

```yaml
model: o4-mini                    # Preferred model for this skill
version: 1.0.0                   # Skill version
```

#### Complete example

```yaml
name: code-reviewer
description: >
  Automated code review. Analyzes pull requests for complexity,
  risk, and quality. Generates review reports with prioritized findings.
instructions: |
  You are an expert code reviewer with deep knowledge of software
  engineering best practices, security patterns, and code quality.

  ## Review Process
  1. Understand the PR context (what changed and why)
  2. Run the PR analyzer tool for automated checks
  3. Review findings and add human-level insights
  4. Generate a structured review report

  ## Priorities
  - Security vulnerabilities (critical)
  - Logic errors (high)
  - Performance issues (medium)
  - Style and conventions (low)

  ## Output Format
  Always provide:
  - Summary of changes
  - Risk assessment (low/medium/high/critical)
  - Specific findings with file and line references
  - Actionable recommendations
tools:
  - name: pr_analyzer
    description: >
      Analyzes git diff between branches for review complexity,
      risk patterns, and generates review priorities
    command: python scripts/pr_analyzer.py
  - name: code_quality_checker
    description: >
      Checks source code for SOLID violations, code smells,
      complexity metrics, and structural issues
    command: python scripts/code_quality_checker.py
  - name: review_report_generator
    description: >
      Generates a formatted review report from analysis results
    command: python scripts/review_report_generator.py
model: o4-mini
version: 1.0.0
```

### Tool Definitions

Tools expose scripts to the Codex agent. Each tool maps to a command that Codex can execute.

```yaml
tools:
  - name: tool_name               # Identifier (snake_case)
    description: >                # When and why to use this tool
      Detailed description of what the tool does and
      what output to expect
    command: python scripts/tool.py   # Execution command
    args:                         # Optional argument definitions
      - name: input_path
        description: Path to input file or directory
        required: true
      - name: format
        description: Output format
        required: false
        default: text
```

**Tool naming conventions:**
- Use snake_case for tool names
- Match the Python script name (without .py extension)
- Be descriptive: `pr_analyzer` not `analyze`

**Command path rules:**
- Paths are relative to the skill directory
- `python scripts/tool.py` resolves to `<skill-dir>/scripts/tool.py`
- Ensure scripts are executable and have proper shebangs

---

## Invocation Patterns

### Basic usage

```bash
# Simple task
codex "add error handling to the API routes"

# With specific model
codex --model o3 "design the caching architecture"

# With specific skill
codex --skill senior-fullstack "scaffold a Next.js app"
```

### File context

```bash
# Pass specific files as context
codex --file src/auth.ts --file src/types.ts "add JWT validation"

# Work in a specific directory
cd my-project && codex "fix the failing tests"
```

### Multi-turn conversation

Codex maintains conversation context within a session:
```bash
codex
> Create a User model with email and name fields
> Add validation for the email field
> Now create a migration for this model
> exit
```

### Piping and integration

```bash
# Pipe file content as context
cat error.log | codex "explain these errors and suggest fixes"

# Use output in scripts
codex --quiet "generate a .gitignore for a Node.js project" > .gitignore
```

---

## Built-in Features

### Conversation history

Codex saves conversation history for context continuity:
```bash
# Continue previous conversation
codex --resume "now add the tests we discussed"
```

### File watching

Codex monitors file changes in the working directory to maintain up-to-date context.

### Multimodal input

```bash
# Pass an image for analysis
codex --image screenshot.png "implement this UI design"
```

### Quiet mode

```bash
# Suppress UI, output only the result
codex --quiet "what is the main entry point of this project"
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API key for authentication | (required) |
| `CODEX_HOME` | Override config directory | `~/.codex` |
| `CODEX_MODEL` | Default model | `o4-mini` |
| `CODEX_APPROVAL_MODE` | Default approval mode | `suggest` |
| `CODEX_QUIET` | Suppress UI output | `false` |

---

## Sandboxing and Security

### Default sandbox behavior

In `full-auto` mode, Codex applies sandboxing by default:

- **Network disabled** - no outbound connections
- **Filesystem restricted** - writes only to project directory
- **No secret access** - environment variables filtered

### macOS sandbox

On macOS, Codex uses Apple's `sandbox-exec` to enforce restrictions.

### Linux sandbox

On Linux, Codex uses a combination of namespace isolation and seccomp filters.

### Disabling sandbox (advanced)

```bash
# Only when you explicitly need network access
codex --approval-mode full-auto --no-sandbox "install dependencies and run tests"
```

**Warning:** Disabling the sandbox removes safety guardrails. Only use in trusted environments.

---

## UI Metadata and Output

### Terminal UI

Codex renders a rich terminal UI showing:
- Current task and progress
- File modifications (diff view)
- Command execution output
- Approval prompts

### Structured output

```bash
# Get JSON-structured output
codex --output-format json "list all TODO comments in the codebase"
```

### Notification support

```bash
# Desktop notification on task completion
codex --notify "run the full test suite"
```

---

## Troubleshooting

### Common issues

**"API key not found"**
```bash
# Verify key is set
echo $OPENAI_API_KEY

# Set it
export OPENAI_API_KEY="sk-..."
```

**"Skill not found"**
```bash
# Check skill location
ls .codex/skills/
ls ~/.codex/skills/

# Verify agents/openai.yaml exists
cat .codex/skills/my-skill/agents/openai.yaml
```

**"Permission denied" when executing tools**
```bash
# Ensure scripts are executable
chmod +x .codex/skills/my-skill/scripts/*.py
```

**"Model not available"**
```bash
# Check available models
codex models list

# Fall back to default
codex --model o4-mini "your task"
```

### Debug mode

```bash
# Verbose output for debugging
codex --verbose "your task"

# Show full request/response logs
CODEX_DEBUG=1 codex "your task"
```

### Reset configuration

```bash
# Reset global config
rm ~/.codex/config.yaml
codex configure

# Clear conversation history
rm -rf ~/.codex/history/
```
