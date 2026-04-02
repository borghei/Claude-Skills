---
name: focused-fix
description: >
  This skill should be used when the user asks to "fix a bug with minimal changes",
  "analyze change scope for a bugfix", "find the minimal set of files to change",
  "do a focused bugfix", or "scope a minimal repair".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: debugging
  updated: 2026-04-02
  tags: [bugfix, minimal-change, scope-analysis, debugging, focused-fix]
---

# Focused Fix

> **Category:** Engineering
> **Domain:** Debugging & Maintenance

## Overview

The **Focused Fix** skill enforces a disciplined minimal-change approach to bug fixing. Instead of refactoring or improving code during a bugfix, it identifies the smallest possible change set that resolves the issue. This reduces risk, simplifies code review, and prevents scope creep.

## Quick Start

```bash
# Analyze a bug description to identify minimal change scope
python scripts/change_scope_analyzer.py --bug "Login fails when email has + character" --path ./src

# Analyze with JSON output
python scripts/change_scope_analyzer.py --bug "API returns 500 on empty array input" --path ./src --format json

# Analyze with specific file extensions
python scripts/change_scope_analyzer.py --bug "CSS overflow on mobile" --path ./src --extensions .css .scss .html
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `change_scope_analyzer.py` | Identify minimal files to change for a bugfix | `--bug`, `--path`, `--extensions`, `--format` |

### change_scope_analyzer.py

Analyzes a bug description against a codebase to identify:
- Files most likely related to the bug (keyword matching, import tracing)
- Estimated change scope (number of files, lines)
- Risk assessment for the change
- Recommended fix approach (minimal vs. structural)

## Workflows

### Focused Bugfix Workflow
1. Write a clear bug description
2. Run `change_scope_analyzer.py` to identify scope
3. Review the recommended files and approach
4. Make ONLY the changes needed to fix the bug
5. Verify no unrelated changes leaked in
6. Submit PR with focused change set

### Scope Validation
1. After making changes, re-run analyzer
2. Compare actual changes against recommended scope
3. Flag any out-of-scope modifications for separate PRs

## Reference Documentation

- [Focused Fix Methodology](references/focused-fix-methodology.md) - Principles, anti-patterns, and decision framework

## Common Patterns

### Do
- Fix the exact bug reported
- Add a regression test for the fix
- Document why the fix works in the commit message
- Keep the diff as small as possible

### Don't
- Refactor surrounding code during a bugfix
- Fix "nearby" issues in the same PR
- Change formatting or style in touched files
- Add features disguised as bugfixes
