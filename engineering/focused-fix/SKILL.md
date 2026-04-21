---
name: focused-fix
description: "Analyzes codebases to identify root causes of bugs, determines the minimal set of files requiring changes, and generates focused patches that minimize side effects and scope creep. Use when the user asks to fix a bug with minimal changes, analyze change scope for a bugfix, find the minimal set of files to change, do a focused bugfix, scope a minimal repair, create a hotfix, or make the smallest possible patch."
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

The agent enforces a disciplined minimal-change approach to bug fixing. Instead of refactoring or improving code during a bugfix, it identifies the smallest possible change set that resolves the issue, reducing risk, simplifying code review, and preventing scope creep.

## Core Workflow

### 1. Capture the Bug Description

The agent gathers:
- Exact error message or unexpected behavior
- Steps to reproduce (or failing test case)
- Expected vs actual behavior
- Environment details (OS, runtime version, relevant config)

**Validate:** Bug description includes a reproducible scenario or a failing test.

### 2. Analyze Change Scope

The agent runs the scope analyzer to identify the minimal file set:

```bash
python scripts/change_scope_analyzer.py --bug "Login fails when email has + character" --path ./src
python scripts/change_scope_analyzer.py --bug "API returns 500 on empty array input" --path ./src --format json
python scripts/change_scope_analyzer.py --bug "CSS overflow on mobile" --path ./src --extensions .css .scss .html
```

| Flag | Type | Description |
|------|------|-------------|
| `--bug` | required | Bug description string |
| `--path` | required | Root path to search |
| `--extensions` | optional | File extensions to include (default: all) |
| `--format` | optional | Output format: `text` (default) or `json` |

The tool identifies:
- Files most likely related to the bug (keyword matching, import tracing)
- Estimated change scope (number of files, lines)
- Risk assessment for the change
- Recommended fix approach (minimal vs structural)

**Validate:** Recommended file count is ≤ 5. If more, the agent reassesses whether this is truly a focused fix or requires a broader approach.

### 3. Implement the Minimal Fix

The agent makes ONLY the changes needed to resolve the bug:
- Fix the exact bug reported
- Add a regression test that fails before the fix and passes after
- Touch no code outside the identified scope

**Validate:** Run `git diff --stat` to confirm changes are limited to recommended files. No formatting-only or style changes present.

### 4. Verify the Fix

The agent runs verification:

```bash
# Confirm the regression test passes
python -m pytest tests/test_<module>.py -v

# Verify no unrelated changes leaked in
git diff --stat

# Check that only recommended files were modified
git diff --name-only
```

**Validate:** Regression test passes; `git diff --name-only` output matches the scope analyzer's recommended files (± the new test file).

### 5. Scope Validation Before PR

The agent performs a final scope check:

```bash
# Re-run scope analyzer to confirm alignment
python scripts/change_scope_analyzer.py --bug "<original description>" --path ./src

# Verify diff size is minimal
git diff --shortstat
```

If any out-of-scope modifications are found, the agent flags them for separate PRs.

**Validate:** All changes directly address the bug; any incidental improvements are split into separate PRs.

### 6. Submit Focused PR

The agent writes the commit message documenting:
- What the bug was (root cause)
- Why this specific fix was chosen
- What was deliberately NOT changed

**Validate:** PR diff is reviewable in < 5 minutes; commit message explains the root cause.

## Anti-Patterns

1. **Refactoring surrounding code during a bugfix** — Mixing cleanup with a fix makes the PR harder to review and increases risk. The agent keeps refactoring in a separate PR.
2. **Fixing "nearby" issues in the same PR** — Adjacent bugs noticed during investigation get filed as separate issues, not bundled into the current fix.
3. **Changing formatting or style in touched files** — Auto-formatters applied to modified files inflate the diff. The agent disables auto-formatting for bugfix commits or limits it to changed lines only.
4. **Adding features disguised as bugfixes** — Behavioral changes beyond restoring expected behavior are features, not fixes. The agent flags these for separate feature PRs.
5. **Skipping the regression test** — A fix without a regression test is an invitation for the same bug to return. The agent always adds a test that fails before the fix.

## Reference Documentation

- [Focused Fix Methodology](references/focused-fix-methodology.md) — Principles, decision framework, and detailed examples for choosing between minimal fix and structural repair
