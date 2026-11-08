---
name: focused-fix
description: >
  Constrain a bugfix to the smallest reviewable change: reproduce, patch, add a regression
  test, check the diff for scope creep. Use when asked for a minimal fix, hotfix or
  release-blocker; diagnose unknown causes with bug-diagnosis.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: debugging
  updated: 2026-11-08
  tags: [bugfix, minimal-change, scope-analysis, debugging, focused-fix]
---

# Focused Fix

The agent fixes the reported bug and nothing else: a reproduction, the smallest change that makes it pass, a regression test, and a diff that a reviewer can read in a minute. Small fixes are easier to review, safer to roll back and less likely to hide a second regression.

This skill starts once the cause is known or close to known. When the cause is still a mystery (intermittent failures, no stack trace), run `engineering/bug-diagnosis` first and come back with a confirmed cause.

## When to Use

- "Fix this bug with minimal changes", "do a focused fix", "what is the smallest change for X?"
- A hotfix or release-blocker that must be low-risk and quick to review.
- A fix PR at risk of scope creep (refactors, style changes, "nearby" fixes).

## Clarify First

Before scoping the fix, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Observable failure:** exact symptom, repro steps, expected vs actual behaviour. This is what the fix must resolve, not a guess at the cause.
- **Expected scope:** which files or module the fix should touch, if known (becomes `--allow` for the scope check).
- **Minimal vs structural:** confirm a focused fix is wanted. If the honest fix spans several modules, stop and say so instead of forcing it into a "minimal" patch.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Reproduce.** Write the failing test first, from the bug report's inputs. It must fail for the reported reason before you change any code.
2. **Locate.** Use the stack trace, `grep` for the failing function and its callers, and `git log -p` on the suspect file. `change_scope_analyzer.py` can suggest candidate files from the bug text when there is nothing better to go on; treat its list as a hint.
3. **Patch** the root layer with the smallest change that makes the test pass. No renames, reformatting, or "while I'm here" edits.
4. **Check the diff** with `diff_scope_check.py`: file and line budget, files outside the expected scope, whitespace-only hunks, bundled dependency changes, and whether a test changed.
5. **Verify** that the new test passes and the existing suite still passes; both must pass before the PR opens. The scope check exits 0, or every finding has a one-line justification in the PR. The commit message names the bug and why the fix works.
6. **Stop and escalate** if the fix needs more than the budget (default 3 files / 60 lines outside tests) or crosses module boundaries: propose a separate, scoped refactor instead.

## Quick Start

Check a fix before opening the PR, from a saved diff:

```bash
python3 scripts/diff_scope_check.py --diff assets/sample_focused.diff --allow 'src/auth/*'     # focused (exit 0)
python3 scripts/diff_scope_check.py --diff assets/sample_sprawling.diff --allow 'src/auth/*'   # 5 findings (exit 1)
```

Or straight from git, as a pre-PR checklist step:

```bash
git diff main...HEAD | python3 scripts/diff_scope_check.py --diff - --format json
```

Optional, when there is no stack trace to start from:

```bash
python3 scripts/change_scope_analyzer.py --bug "Login fails when email has + character" --path ./src
```

## Tools Overview

| Tool | What it does | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `diff_scope_check.py` | Reads a unified diff; flags non-test files over budget, lines over budget, files outside `--allow`, whitespace-only hunks, lockfile/manifest changes bundled with code, and a missing test change | `--diff <file or ->`, `--allow <globs>`, `--max-files`, `--max-lines`, `--no-test-required`, `--format text|json` | 0 focused, 1 findings, 2 unreadable or not a diff |
| `change_scope_analyzer.py` | Keyword and import heuristics from the bug text to rank candidate files, estimate scope and risk | `--bug`, `--path`, `--extensions`, `--format human|json` | 0, 2 bad arguments |

`change_scope_analyzer.py` matches words in the bug text against file names and contents. It misses dynamic dispatch, reflection and config-driven paths, and it can rank files on generic words ("fails"). Prefer evidence (traces, tests, git history) over its ranking.

## Anti-Patterns

**Mistake:** "While I'm here" refactors in the bugfix PR.
**Why it happens:** The surrounding code is in view and looks improvable.
**Instead:** Note it and open a separate `refactor:` PR. Mixed PRs multiply review time and mask regressions behind the real fix.

**Mistake:** Reformatting the files you touch.
**Why it happens:** Format-on-save or habit.
**Instead:** Revert formatting-only hunks before committing; `diff_scope_check.py` lists them.

**Mistake:** Skipping the regression test because the fix is obvious.
**Why it happens:** A one-line change feels self-evidently right.
**Instead:** Every fix ships a test that failed before it. Obvious bugs come back during later refactors.

**Mistake:** Fixing the symptom in the wrong layer.
**Why it happens:** The first place the error shows is the easiest to patch.
**Instead:** Trace to where the bad value is produced and fix it there; otherwise the bug returns in a new form.

**Mistake:** Bundling the fix with a dependency upgrade.
**Why it happens:** The upgrade seemed related.
**Instead:** Land the upgrade separately so either change can be rolled back alone.

## Files

- `scripts/diff_scope_check.py`, `scripts/change_scope_analyzer.py` — the tools above.
- `assets/sample_focused.diff` (one source file plus a test), `assets/sample_sprawling.diff` (five files, formatting noise, a dependency bump, no test).
- `evals/` — prompt cases and a grader for this skill's behaviour.

## Reference Documentation

- [references/focused-fix-methodology.md](references/focused-fix-methodology.md) — principles, decision framework for minimal vs structural fixes, and more anti-patterns.
