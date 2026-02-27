---
name: your-skill-name
description: >-
  This skill should be used when the user asks to "action one",
  "action two", "action three", or "action four". Use for
  domain-specific workflows, analysis, and automation.
license: MIT
metadata:
  version: 1.0.0
  category: engineering
  domain: your-domain
---

# Your Skill Title

One-line summary of what this skill provides and who benefits from it.

## Keywords

keyword1, keyword2, keyword3, keyword4, keyword5,
action-verb1, action-verb2, domain-term1, domain-term2

---

## Table of Contents

- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
  - [Tool One](#1-tool-one)
  - [Tool Two](#2-tool-two)
- [Workflows](#workflows)
  - [Primary Workflow](#workflow-1-primary-workflow)
  - [Secondary Workflow](#workflow-2-secondary-workflow)
- [Reference Documentation](#reference-documentation)
- [Quick Reference](#quick-reference)

---

## Quick Start

```bash
# Primary tool - basic usage
python scripts/tool_one.py input_file.txt

# Primary tool - with options
python scripts/tool_one.py input_file.txt --option value --json

# Secondary tool
python scripts/tool_two.py /path/to/dir --format table
```

---

## Tools Overview

### 1. Tool One

Brief description of what this tool does and when to use it.

```bash
# Basic usage
python scripts/tool_one.py input

# With options
python scripts/tool_one.py input --option value

# JSON output for piping
python scripts/tool_one.py input --json
```

| Parameter | Description |
|-----------|-------------|
| `input` | Description of the input parameter |
| `--option, -o` | Description of the option (default: value) |
| `--format` | Output format: table, json, csv (default: table) |
| `--json` | Output in JSON format |

**Example output:**

```
Tool One Report
================
  Input:   example.txt
  Status:  Analyzed
  Score:   85/100

Findings:
  1. Finding description (severity)
  2. Finding description (severity)
```

### 2. Tool Two

Brief description of what this tool does and when to use it.

```bash
python scripts/tool_two.py /path/to/dir
python scripts/tool_two.py /path/to/dir --depth 3 --json
```

| Parameter | Description |
|-----------|-------------|
| `path` | Directory path to analyze |
| `--depth, -d` | Analysis depth (default: 5) |
| `--json` | Output in JSON format |

---

## Workflows

### Workflow 1: Primary Workflow

Description of when and why to use this workflow.

**Step 1: Analyze the Current State**

```bash
python scripts/tool_one.py target --json > analysis.json
```

Review the output and identify areas that need attention.

**Step 2: Apply Changes**

Based on the analysis, take the following actions:

- Action based on finding type A
- Action based on finding type B
- Action based on finding type C

**Step 3: Validate**

```bash
python scripts/tool_one.py target --json
```

Verify the score has improved and no regressions were introduced.

### Workflow 2: Secondary Workflow

Description of the secondary use case.

**Step 1: Setup**

```bash
python scripts/tool_two.py /path/to/project
```

**Step 2: Execute**

Follow the recommendations from the tool output.

**Step 3: Verify**

Re-run the tool and confirm improvements.

---

## Reference Documentation

| Document | Path | When to Use |
|----------|------|-------------|
| Deep Guide | [references/guide.md](references/guide.md) | Detailed patterns and strategies |
| Examples | [references/examples.md](references/examples.md) | Real-world usage examples |

---

## Quick Reference

### Common Commands

| Task | Command |
|------|---------|
| Basic analysis | `python scripts/tool_one.py input` |
| JSON output | `python scripts/tool_one.py input --json` |
| Directory scan | `python scripts/tool_two.py /path` |
| Help | `python scripts/tool_one.py --help` |

### Decision Matrix

| Situation | Use This | Because |
|-----------|----------|---------|
| Scenario A | Tool One | Reason |
| Scenario B | Tool Two | Reason |
| Scenario C | Workflow 1 | Reason |

---

**Last Updated:** Month Year
**Version:** 1.0.0
