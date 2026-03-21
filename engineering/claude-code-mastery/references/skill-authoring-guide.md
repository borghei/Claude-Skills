# Skill Authoring Guide

Comprehensive reference for writing effective Claude Code skills -- from YAML
frontmatter to progressive disclosure, tool restrictions, and context optimization.

---

## Table of Contents

- [Skill Package Structure](#skill-package-structure)
- [YAML Frontmatter](#yaml-frontmatter)
- [Description Optimization](#description-optimization)
- [SKILL.md Anatomy](#skillmd-anatomy)
- [Progressive Disclosure](#progressive-disclosure)
- [Python Tool Standards](#python-tool-standards)
- [Reference Document Standards](#reference-document-standards)
- [Context Modes and Loading](#context-modes-and-loading)
- [Model Selection Guidance](#model-selection-guidance)
- [Testing Your Skill](#testing-your-skill)

---

## Skill Package Structure

Every skill follows this directory layout:

```
skill-name/
├── SKILL.md              # Master documentation (always the entry point)
├── scripts/              # Python CLI tools
│   ├── tool_one.py
│   └── tool_two.py
├── references/           # Deep-dive knowledge bases
│   ├── guide_one.md
│   └── guide_two.md
└── assets/               # User-facing templates and examples
    ├── template.md
    └── checklist.md
```

**Design rules:**

1. **Self-contained** -- Every skill must work independently. No cross-skill imports.
2. **SKILL.md is the interface** -- Claude reads this first and decides what to use.
3. **Scripts are tools, not libraries** -- Each script is a CLI tool, not a shared module.
4. **References are on-demand** -- Only loaded when Claude needs deep knowledge.
5. **Assets are for users** -- Templates the user copies and customizes.

---

## YAML Frontmatter

The frontmatter at the top of SKILL.md determines how Claude discovers and
activates the skill.

### Required Fields

```yaml
---
name: skill-name
description: >-
  This skill should be used when the user asks to "do X", "analyze Y",
  "generate Z", or "optimize W". Use for domain expertise, workflow
  automation, and analysis.
---
```

**`name`** -- Kebab-case identifier matching the directory name. Used for
referencing and logging.

**`description`** -- The most important field. This is what Claude reads to
decide whether to activate the skill. Write it in third person and load it
with trigger phrases.

### Optional Fields

```yaml
---
name: skill-name
description: >-
  Description text...
license: MIT
metadata:
  version: 1.0.0
  category: engineering
  domain: development-tools
  author: Team Name
  tags: [cli, automation, analysis]
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(python*)
---
```

**`license`** -- License type (MIT, Apache-2.0, proprietary, etc.).

**`metadata`** -- Structured metadata for categorization and versioning.
- `version` -- Semantic version (major.minor.patch)
- `category` -- Broad category (engineering, marketing, product, etc.)
- `domain` -- Specific domain (development-tools, seo, compliance, etc.)
- `author` -- Creator or team name
- `tags` -- Array of discovery keywords

**`allowed-tools`** -- Restricts which tools the skill can use. Useful for
creating read-only analysis skills or skills that should never write files.

---

## Description Optimization

The description field is the skill's discovery mechanism. Claude scans descriptions
to match user requests to relevant skills.

### Writing Effective Descriptions

**Pattern:** Third person, trigger phrases in quotes, use cases at the end.

```yaml
# GOOD -- Packed with trigger phrases, specific use cases
description: >-
  This skill should be used when the user asks to "analyze API performance",
  "benchmark endpoints", "profile response times", "identify bottlenecks",
  or "optimize throughput". Use for REST API performance analysis, load
  testing configuration, latency profiling, and capacity planning.

# BAD -- Vague, no trigger phrases
description: >-
  A skill for working with APIs and performance.

# BAD -- First person, narrative style
description: >-
  I help users analyze their API performance and find issues.
```

### Trigger Phrase Rules

1. Use verb phrases users actually say: "analyze X", "create Y", "optimize Z"
2. Include 5-10 trigger phrases minimum
3. Cover synonyms: "benchmark" and "profile" and "measure"
4. Include the domain: "REST API", "database queries", "frontend rendering"
5. End with a summary of use cases

### Testing Discovery

Ask Claude: "I need to optimize my API response times." If your skill is not
activated, add more trigger phrases related to that phrasing.

---

## SKILL.md Anatomy

A well-structured SKILL.md follows this order:

### 1. YAML Frontmatter
See above.

### 2. Title and One-Line Summary

```markdown
# API Performance Analyzer

Identify bottlenecks, benchmark endpoints, and optimize API throughput.
```

### 3. Keywords

A comma-separated list of discovery terms that supplements the description.

```markdown
## Keywords

api, performance, latency, throughput, benchmarking, profiling, bottleneck,
response-time, load-testing, capacity-planning
```

### 4. Table of Contents

Link to all major sections for quick navigation.

### 5. Quick Start

Three to five commands that demonstrate the skill immediately. A user should be
able to copy-paste these and see results.

### 6. Tools Overview

Each script with usage examples, parameter tables, and sample output.

### 7. Workflows

Step-by-step sequences that combine tools, knowledge, and judgment. Workflows
are the most valuable part of a skill because they encode expertise.

### 8. Reference Documentation

Table linking to files in `references/`.

### 9. Quick Reference

Tables, cheat sheets, and at-a-glance summaries for common operations.

---

## Progressive Disclosure

Structure skills so Claude loads only what it needs for the current task.

### Layer 1: SKILL.md (Always Loaded When Active)

Contains the skill overview, tool descriptions, and workflow summaries.
Keep under 400 lines if possible.

### Layer 2: Reference Documents (Loaded on Demand)

Deep knowledge bases that Claude reads when it needs specific expertise.
These are NOT loaded automatically.

```markdown
## Reference Documentation

| Document | Path | When to Use |
|----------|------|-------------|
| API Patterns | references/api-patterns.md | Designing new API endpoints |
| Error Handling | references/error-handling.md | Implementing error responses |
| Caching Guide | references/caching-guide.md | Optimizing response times |
```

### Layer 3: Assets (User-Facing)

Templates and examples the user copies. Claude references these when helping
users fill them out.

### Loading Control

Use clear indicators in SKILL.md to tell Claude when to load reference docs:

```markdown
> For detailed caching strategies, see [references/caching-guide.md](references/caching-guide.md)
```

This is better than including all caching knowledge directly in SKILL.md.

---

## Python Tool Standards

Every Python script in a skill must follow these standards:

### Structure Template

```python
#!/usr/bin/env python3
"""
Tool Name - One line description

Detailed description of what the tool does, what input it expects,
and what output it produces.

Usage:
    python tool_name.py input_arg
    python tool_name.py input_arg --option value
    python tool_name.py input_arg --json
"""

import argparse
import json
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Tool description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="Input to process")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    result = {"key": "value"}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human_readable(result)

if __name__ == "__main__":
    main()
```

### Rules

1. **Standard library only** -- No pip dependencies. Scripts must run anywhere.
2. **argparse with --help** -- Every script must have useful help text.
3. **--json flag** -- Support machine-readable JSON output.
4. **Module docstring** -- Include usage examples in the docstring.
5. **Error handling** -- Catch exceptions, print useful messages, exit with non-zero.
6. **No LLM calls** -- Scripts must be deterministic and fast.
7. **No network calls** -- Unless the skill explicitly requires it (and documents it).
8. **Executable** -- Set `chmod +x` and include the shebang line.

### Output Conventions

- Human-readable: Clear labels, aligned columns, section headers
- JSON: Flat structure preferred, always include a `success` boolean
- Errors: Print to stderr, exit code 1
- Progress: Use stderr for progress messages so stdout stays clean for piping

---

## Reference Document Standards

### Structure

```markdown
# Document Title

## Overview
One paragraph context.

## Section 1
Content with examples.

## Section 2
Content with examples.

## Quick Reference
Tables and cheat sheets.

---
**Last Updated:** Month Year
```

### Rules

1. **Single topic per file** -- "Caching Strategies" not "Caching and Performance"
2. **Actionable content** -- Every section should tell the reader what to DO
3. **Code examples** -- Show, don't just tell
4. **Tables for comparisons** -- Use tables when comparing options
5. **Under 500 lines** -- Split longer guides into multiple files
6. **No redundancy with SKILL.md** -- Reference docs go deeper, not wider

---

## Context Modes and Loading

Understanding how Claude Code loads files helps you structure skills efficiently.

### Fork vs Main Context Modes

The `context` field in YAML frontmatter controls how the skill's conversation
context relates to the main conversation.

**Fork Mode** (`context: fork`):
- Creates an isolated context branch for the skill
- Skill runs in its own conversation thread
- Does not pollute the main conversation history with file reads
- Results are summarized back to the main thread
- Best for: long-running analyses, tasks that read many files, heavy output

**Main Mode** (`context: main`, default):
- Skill runs in the current conversation context
- Has access to full conversation history
- Results stay in the main thread
- Best for: quick operations, tasks that build on recent conversation

| Scenario | Mode | Reason |
|----------|------|--------|
| Code review of 20 files | `fork` | Avoids flooding main context with file reads |
| Quick config generation | `main` | Needs to reference recent conversation |
| Test suite execution | `fork` | Output-heavy, isolate the noise |
| Editing a file discussed in chat | `main` | Needs conversation context |

### Automatic Loading

These files load for EVERY conversation:
- `~/.claude/CLAUDE.md` (user global)
- `<project>/CLAUDE.md` (project root)
- `<project>/.claude/CLAUDE.md` (project config)

### On-Demand Loading

These load when Claude accesses files in the directory:
- `<project>/subdir/CLAUDE.md` (subdirectory-specific)

### Skill Loading

SKILL.md files load when:
- The user's request matches the skill description
- Claude determines the skill is relevant
- The user explicitly invokes the skill

### Reference Loading

Reference files load when:
- Claude reads them with the Read tool
- They are referenced in a workflow Claude is executing
- The user asks Claude to consult them

### Optimization Strategy

1. Put project-wide rules in root CLAUDE.md (auto-loaded, keep small)
2. Put domain rules in subdirectory CLAUDE.md files (on-demand)
3. Put workflow knowledge in SKILL.md (skill-triggered)
4. Put deep expertise in references/ (explicit read)

---

## String Substitutions

Skills support special string substitutions that are replaced at invocation
time. These allow skills to be parameterized and dynamic.

### Available Substitutions

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `$ARGUMENTS` | Full argument string passed to the skill | `"review the auth module"` |
| `$1` | First positional argument (space-separated) | `"review"` |
| `$2` | Second positional argument | `"the"` |
| `$N` | Nth positional argument | (any word by position) |
| `$PROJECT_DIR` | Absolute path to the project root | `/home/user/my-project` |
| `$FILE` | Currently active file path (if applicable) | `src/auth/login.ts` |

### Using Substitutions in SKILL.md

```markdown
## Quick Start

Analyzing: $ARGUMENTS

\```bash
python scripts/analyzer.py $PROJECT_DIR $1
\```
```

When the user invokes the skill with arguments, the variables are replaced
before the skill content is processed.

### Using Substitutions in Frontmatter

```yaml
custom-instructions: |
  Analyze the following request: $ARGUMENTS
  Focus on the project at: $PROJECT_DIR
  Currently active file: $FILE
```

### Practical Examples

**Skill invoked with:** `/skill my-skill review src/auth/`

| Variable | Resolves To |
|----------|-------------|
| `$ARGUMENTS` | `review src/auth/` |
| `$1` | `review` |
| `$2` | `src/auth/` |
| `$PROJECT_DIR` | `/home/user/my-project` |

### Best Practices for Substitutions

1. **Always provide defaults** -- Do not assume `$ARGUMENTS` is non-empty.
2. **Document expected arguments** -- In the Quick Start section, show what
   arguments the skill expects.
3. **Use `$PROJECT_DIR`** for scripts -- Ensures paths resolve correctly
   regardless of where the skill is invoked from.
4. **Avoid `$FILE` in mandatory flows** -- It may be empty if no file is active.

---

## Model Selection Guidance

When creating agents or suggesting configurations, choose models based on the task:

| Task Type | Recommended Model | Rationale |
|-----------|------------------|-----------|
| Complex reasoning, architecture | claude-opus-4-20250514 | Highest capability |
| General coding, review | claude-sonnet-4-20250514 | Best speed/quality balance |
| Simple tasks, formatting | claude-haiku-3-5-20241022 | Fastest, cheapest |
| Subagent tasks | claude-sonnet-4-20250514 | Good balance for delegated work |

For agent definitions that specify a model:

```yaml
# Complex analysis agent
model: claude-opus-4-20250514

# General-purpose coding agent
model: claude-sonnet-4-20250514

# Quick formatting/linting agent
model: claude-haiku-3-5-20241022
```

---

## Testing Your Skill

### Functional Testing

1. Run every script with `--help` and verify output
2. Run every script with sample input and verify results
3. Run every script with `--json` and verify valid JSON
4. Run every script with invalid input and verify error handling

### Integration Testing

1. Start a Claude Code session in a test project
2. Ask a question that should trigger your skill
3. Verify Claude finds and uses the correct tool
4. Verify the workflow produces expected results

### Discovery Testing

1. Ask Claude variations of questions your skill should handle
2. Note which phrasings do NOT trigger the skill
3. Add those phrasings as trigger phrases in the description

### Quality Checklist

- [ ] SKILL.md has valid YAML frontmatter
- [ ] Description contains 5+ trigger phrases
- [ ] Quick Start has 3+ copy-pasteable commands
- [ ] All scripts run with `--help`
- [ ] All scripts support `--json`
- [ ] All scripts handle errors gracefully
- [ ] Reference docs are single-topic and under 500 lines
- [ ] No dependencies beyond Python standard library
- [ ] No cross-skill imports or dependencies

---

**Last Updated:** February 2026
