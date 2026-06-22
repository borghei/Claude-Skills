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

## Use when

- The user asks to "fix a bug with minimal changes", "do a focused bugfix", or "scope a minimal repair"
- A bug report needs triage to identify the smallest set of files to touch
- A PR is at risk of scope creep (unrelated refactors, style changes, "nearby" fixes)
- A hotfix or release-blocker needs a low-risk, reviewable change set
- The user asks "what is the minimal change to fix X?" or "which files do I need to touch for this bug?"

## Clarify First

Before scoping the fix, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Observable failure** — the exact symptom, repro steps, and expected vs actual behavior (the bug description the analyzer matches against, and what the fix must resolve — not a guess at the cause)
- [ ] **Codebase path & file types** — which directory and extensions to search (sets `--path`/`--extensions`)
- [ ] **Minimal vs structural** — confirm this is a focused fix, not a refactor (determines whether out-of-scope "while I'm here" changes are rejected)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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
1. **Write a clear bug description** — reproduction steps, expected vs actual behavior
   - *Validate:* the description names the observable failure, not a guess at the cause
2. **Run `change_scope_analyzer.py` to identify scope**
   - *Validate:* analyzer output lists concrete files and an estimated line count
3. **Review the recommended files and approach**
   - *Validate:* recommended approach is "minimal" — if it says "structural", stop and scope a refactor PR separately
4. **Make ONLY the changes needed to fix the bug**
   - *Validate:* `git diff --stat` matches (or is smaller than) the analyzer's recommendation
5. **Verify no unrelated changes leaked in**
   - *Validate:* `git diff` shows no formatting-only changes, no unrelated imports, no "while I'm here" edits
6. **Submit PR with focused change set**
   - *Validate:* commit message states the exact bug fixed, and a regression test is included

### Scope Validation
1. After making changes, re-run analyzer
2. Compare actual changes against recommended scope
3. Flag any out-of-scope modifications for separate PRs
   - *Validate:* any file touched that was not in the analyzer recommendation has a one-line justification or is reverted

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

## Anti-patterns

| Anti-pattern | Failure mode | Fix |
|--------------|--------------|-----|
| "While I'm here" refactors in the bugfix PR | Blast radius explodes; review time multiplies; unrelated regressions masked by the real fix | Open a separate PR for the refactor, tagged as `refactor:` not `fix:` |
| Reformatting or auto-save style changes in touched files | Diff becomes unreadable; real fix hidden in 200 lines of whitespace | Revert style changes before committing; configure the editor to format-on-save only for new files |
| Fixing the symptom in the wrong layer | Bug returns in a new form; accumulates workaround debt | Trace to the root layer — analyzer's keyword-match output is a hint, not an answer |
| Skipping the regression test "because the fix is obvious" | Bug silently returns on a refactor 6 months later | Every `fix:` commit adds at least one failing-then-passing test |
| Treating `change_scope_analyzer.py` output as authoritative | Analyzer is keyword/import-based, not semantic — misses dynamic dispatch, reflection, config-driven paths | Use it as a starting set; grep for callers and tests before committing to the scope |
| Bundling the fix with a dependency upgrade | Two risk profiles in one PR; if rollback is needed, both are lost | Land the upgrade separately, then the fix against the upgraded baseline |
