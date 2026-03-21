# Cross-Platform Skills Guide

How to write skills compatible with multiple AI coding agents: Claude Code, OpenAI Codex CLI, Cursor, VS Code Copilot, and Goose.

---

## Table of Contents

- [Overview](#overview)
- [Platform Comparison](#platform-comparison)
- [Universal Skill Structure](#universal-skill-structure)
- [Platform-Specific Configuration Files](#platform-specific-configuration-files)
  - [Claude Code: SKILL.md](#claude-code-skillmd)
  - [Codex CLI: agents/openai.yaml](#codex-cli-agentsopenai-yaml)
  - [Cursor: .cursorrules](#cursor-cursorrules)
  - [VS Code Copilot: .github/copilot-instructions.md](#vs-code-copilot-githubcopilot-instructionsmd)
  - [Goose: .goosehints](#goose-goosehints)
- [Shared Components](#shared-components)
- [Writing Portable Instructions](#writing-portable-instructions)
- [Cross-Platform Skill Template](#cross-platform-skill-template)
- [Conversion Strategies](#conversion-strategies)
- [Testing Across Platforms](#testing-across-platforms)
- [Platform Feature Matrix](#platform-feature-matrix)

---

## Overview

AI coding agents are converging on similar skill/instruction patterns but use different configuration formats. A well-designed skill separates its core knowledge (instructions, references, tools) from platform-specific configuration, making it straightforward to support multiple agents from a single source.

**Design principle:** Write once, configure per platform. The domain expertise lives in shared markdown and scripts. Only the entry-point configuration differs.

---

## Platform Comparison

| Feature | Claude Code | Codex CLI | Cursor | VS Code Copilot | Goose |
|---------|-------------|-----------|--------|-----------------|-------|
| Config file | SKILL.md | agents/openai.yaml | .cursorrules | copilot-instructions.md | .goosehints |
| Format | Markdown + YAML FM | YAML | Plain text | Markdown | Markdown |
| Tool support | Python scripts | CLI commands | Limited | Extensions | Python plugins |
| Skill discovery | YAML frontmatter | YAML fields | N/A | N/A | N/A |
| Auto-discovery | By description | By description | No | No | No |
| Max context | Large | Large | Medium | Medium | Large |
| Sandboxing | Yes | Yes (full-auto) | No | No | Yes |

---

## Universal Skill Structure

The recommended cross-platform skill layout:

```
my-skill/
├── SKILL.md                      # Claude Code entry point
├── agents/
│   └── openai.yaml               # Codex CLI entry point
├── .cursorrules                   # Cursor rules (optional)
├── .github/
│   └── copilot-instructions.md   # VS Code Copilot (optional)
├── .goosehints                    # Goose hints (optional)
├── scripts/                      # Shared tools (all platforms)
│   ├── tool_a.py
│   └── tool_b.py
├── references/                   # Shared knowledge base
│   ├── guide.md
│   └── patterns.md
└── assets/                       # Shared templates
    └── template.yaml
```

**Shared directories** (`scripts/`, `references/`, `assets/`) are platform-agnostic. Every platform can reference these files. Only the top-level config files differ.

---

## Platform-Specific Configuration Files

### Claude Code: SKILL.md

Claude Code reads `SKILL.md` as the skill definition. It uses YAML frontmatter for metadata and the markdown body for instructions and documentation.

```markdown
---
name: my-skill
description: This skill should be used when the user asks to "do X",
  "perform Y", or "analyze Z". Use for domain expertise and automation.
license: MIT
metadata:
  version: 1.0.0
  category: engineering
  domain: development-tools
---

# My Skill

Expert guidance for X domain.

## Quick Start

```bash
python scripts/tool_a.py --help
```

## Workflows

### Workflow 1: Analyze X
...

## Best Practices
...
```

**Key characteristics:**
- YAML frontmatter with `name` and `description` (required)
- Description uses third-person, keyword-rich format for auto-discovery
- Markdown body serves as both documentation and instructions
- Tool usage documented inline with bash code blocks

---

### Codex CLI: agents/openai.yaml

Codex CLI reads `agents/openai.yaml` for skill configuration.

```yaml
name: my-skill
description: >
  Expert guidance for X domain. Analyzes Y, generates Z,
  and enforces best practices.
instructions: |
  You are a senior X specialist.

  When the user asks about Y:
  1. Analyze the context using the analyzer tool
  2. Apply framework Z
  3. Generate structured output

  Always reference the knowledge in references/ for details.
tools:
  - name: tool_a
    description: Analyzes X and produces assessment
    command: python scripts/tool_a.py
  - name: tool_b
    description: Generates Y artifacts
    command: python scripts/tool_b.py
model: o4-mini
version: 1.0.0
```

**Key characteristics:**
- YAML format with structured fields
- Separate `instructions` field (not embedded in docs)
- Explicit `tools` array with command mappings
- Optional `model` preference

---

### Cursor: .cursorrules

Cursor reads `.cursorrules` from the project root. It is a plain text file with instructions.

```
You are a senior X specialist with deep expertise in Y and Z.

## Rules
- Always validate input before processing
- Use TypeScript strict mode
- Follow the patterns in references/guide.md

## Workflow
When asked to analyze code:
1. Check the file structure
2. Run scripts/tool_a.py for automated analysis
3. Provide recommendations based on references/patterns.md

## Code Style
- Use camelCase for variables
- Use PascalCase for types
- Prefer const over let
```

**Key characteristics:**
- Plain text (no YAML, no frontmatter)
- Rules-oriented format
- No formal tool definition (tools referenced informally)
- Applies to entire project (not modular)

---

### VS Code Copilot: .github/copilot-instructions.md

GitHub Copilot reads `.github/copilot-instructions.md` for workspace-level instructions.

```markdown
# Copilot Instructions

You are a senior X specialist. Follow these guidelines when generating code.

## Standards
- Use TypeScript strict mode
- Follow SOLID principles
- Write tests for all new functions

## Architecture
Follow the patterns documented in `references/guide.md`.

## Tools
When analysis is needed, suggest running:
```bash
python scripts/tool_a.py <path>
```
```

**Key characteristics:**
- Standard markdown in `.github/` directory
- Read by GitHub Copilot in VS Code
- Instruction-focused (no tool execution)
- Informational only (Copilot suggests, does not execute)

---

### Goose: .goosehints

Goose reads `.goosehints` from the project root for behavioral guidance.

```markdown
# Goose Hints

You are a senior X specialist.

## Capabilities
- Run `python scripts/tool_a.py` for automated analysis
- Reference `references/guide.md` for domain knowledge
- Use templates in `assets/` for output formatting

## Workflow
1. Understand the user request
2. Check existing code context
3. Run tools as needed
4. Apply best practices from references
5. Generate clean, documented code

## Constraints
- Standard library Python only in scripts
- No network calls during analysis
- UTF-8 encoding for all files
```

**Key characteristics:**
- Markdown format with hints and guidance
- Supports tool execution (Goose runs commands)
- Flexible format, no strict schema

---

## Shared Components

### scripts/ directory

Python scripts are the most portable tool format. All platforms can execute Python scripts.

**Portability rules:**
1. Use standard library only (no pip dependencies)
2. Support `--help` via argparse
3. Support `--json` output for machine consumption
4. Use relative paths (resolve from script location)
5. Handle errors gracefully with clear messages
6. Work on macOS, Linux, and Windows (use `pathlib`)

```python
#!/usr/bin/env python3
"""Tool description for discovery."""
import argparse
import json
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Tool description")
    parser.add_argument("input", help="Input path")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = analyze(args.input)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))

if __name__ == "__main__":
    main()
```

### references/ directory

Knowledge base files in markdown. These are referenced by instructions on all platforms.

**Best practices:**
- Use standard markdown (no platform-specific extensions)
- Keep files focused (one topic per file)
- Use relative links between reference files
- Include a table of contents for files longer than 100 lines

### assets/ directory

Templates, configuration samples, and other reusable resources.

**Best practices:**
- Use YAML or JSON for structured templates (both are widely supported)
- Include comments explaining each field
- Provide both minimal and full-featured examples

---

## Writing Portable Instructions

Instructions are the core of any skill. Write them so they translate cleanly to any platform:

### Do

- **Use imperative mood:** "Analyze the code" not "This skill analyzes the code"
- **Reference shared files by path:** "See references/guide.md for details"
- **Describe tools generically:** "Run the analyzer tool" not "Use codex --skill"
- **Structure with markdown headers:** Universally parsed
- **Number steps clearly:** "1. First... 2. Then... 3. Finally..."

### Avoid

- **Platform-specific invocations:** "Ask Claude to..." or "Run codex --skill..."
- **Embedded tool definitions:** Keep tool configs in platform-specific files
- **Assumptions about UI:** Not all platforms have the same approval flow
- **Inline YAML in markdown:** Keep YAML in dedicated files
- **Overly long instructions:** Keep under 2000 words for best context use

### Instruction template

```
You are a senior [DOMAIN] specialist with expertise in [AREAS].

## Core Responsibilities
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]

## Process
When asked to [PRIMARY TASK]:
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Tools
- [tool_name]: [what it does and when to use it]

## Quality Standards
- [Standard 1]
- [Standard 2]

## References
- references/[file].md: [what it covers]
```

---

## Cross-Platform Skill Template

Use this template when creating a new skill that targets all platforms:

### Step 1: Create shared content first

Write references, scripts, and assets before platform configs.

### Step 2: Write SKILL.md (Claude Code)

The most detailed format. Use this as the source of truth.

### Step 3: Generate agents/openai.yaml (Codex CLI)

Extract instructions and tool definitions from SKILL.md. Use the codex_skill_converter.py tool.

### Step 4: Create .cursorrules (Cursor)

Distill instructions to rules and coding standards. Keep under 500 lines.

### Step 5: Create copilot-instructions.md (Copilot)

Focus on code generation guidelines. Omit tool execution details.

### Step 6: Create .goosehints (Goose)

Similar to SKILL.md but more concise. Include tool paths.

---

## Conversion Strategies

### Source of truth: SKILL.md

Maintain `SKILL.md` as the canonical skill definition. Generate other formats from it.

```
SKILL.md (source) ──┬──> agents/openai.yaml (Codex)
                    ├──> .cursorrules (Cursor)
                    ├──> copilot-instructions.md (Copilot)
                    └──> .goosehints (Goose)
```

### Automated conversion

Use the `codex_skill_converter.py` script for SKILL.md to agents/openai.yaml conversion. For other platforms, a general conversion follows this pattern:

1. Parse SKILL.md frontmatter and body
2. Extract instructions, tools, and references
3. Format into the target platform syntax
4. Write the platform-specific file

### Manual conversion checklist

When converting a skill to a new platform:

- [ ] Core instructions preserved
- [ ] Tool references updated to match platform syntax
- [ ] File paths are correct (relative to skill or project root)
- [ ] Platform-specific features leveraged (e.g., Codex tool args)
- [ ] Validated on target platform

---

## Testing Across Platforms

### Validation approach

1. **Structural validation:** Use `cross_platform_validator.py` to check file presence and format
2. **Functional testing:** Run each script independently with `--help` and sample input
3. **Integration testing:** Test the skill on each target platform with a standard prompt

### Standard test prompts

Use these prompts to verify a skill works correctly:

```
# Basic functionality
"Explain what this skill does and what tools are available"

# Tool execution
"Run the [primary tool] on [sample input]"

# Workflow execution
"Walk me through the [primary workflow]"

# Edge case
"What happens when [unusual situation]?"
```

### Platform-specific verification

| Platform | How to test |
|----------|------------|
| Claude Code | Load SKILL.md in project, ask Claude about it |
| Codex CLI | Install skill, run `codex --skill name "test prompt"` |
| Cursor | Place .cursorrules in project root, test in IDE |
| VS Code Copilot | Add copilot-instructions.md, test suggestions |
| Goose | Add .goosehints, run goose with test prompt |

---

## Platform Feature Matrix

Detailed comparison of what each platform supports:

### Skill Discovery

| Capability | Claude Code | Codex CLI | Cursor | Copilot | Goose |
|-----------|-------------|-----------|--------|---------|-------|
| Auto-discovery by description | Yes | Yes | No | No | No |
| Explicit invocation | N/A | --skill flag | N/A | N/A | N/A |
| Multiple skills per project | Yes | Yes | No (1 file) | No (1 file) | No (1 file) |
| Skill versioning | Via metadata | Via YAML | No | No | No |

### Tool Execution

| Capability | Claude Code | Codex CLI | Cursor | Copilot | Goose |
|-----------|-------------|-----------|--------|---------|-------|
| Run Python scripts | Yes | Yes | No | No | Yes |
| Run shell commands | Yes | Yes | No | No | Yes |
| Tool argument schemas | No | Yes (args) | No | No | No |
| Sandboxed execution | Yes | Yes (full-auto) | No | No | Yes |

### Instruction Format

| Capability | Claude Code | Codex CLI | Cursor | Copilot | Goose |
|-----------|-------------|-----------|--------|---------|-------|
| Markdown support | Full | In instructions | Partial | Full | Full |
| YAML frontmatter | Yes | N/A | No | No | No |
| Max instruction size | Large | Large | ~5000 chars | Medium | Large |
| Structured sections | Via markdown | Via YAML | Free-form | Via markdown | Via markdown |

### Distribution

| Capability | Claude Code | Codex CLI | Cursor | Copilot | Goose |
|-----------|-------------|-----------|--------|---------|-------|
| Directory-based skills | Yes | Yes | No | No | No |
| Registry support | No (manual) | Planned | No | No | No |
| Git-based distribution | Yes | Yes | Yes | Yes | Yes |
| Skills index/manifest | Via builder tool | Via builder tool | No | No | No |
