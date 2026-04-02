# Focused Fix Methodology

## Core Principle

A focused fix changes the **minimum number of lines** needed to resolve a specific bug. Nothing more, nothing less.

## Why Minimal Changes Matter

1. **Reduced Risk**: Every line changed is a line that could introduce a new bug
2. **Faster Review**: Small diffs are reviewed more thoroughly
3. **Clean History**: Git blame stays meaningful when fixes are surgical
4. **Easier Rollback**: Small changes are trivially reverted if problems emerge
5. **Clear Accountability**: Each change has a clear, traceable purpose

## The Focused Fix Decision Framework

### Step 1: Reproduce
- Confirm the bug exists with a concrete reproduction case
- Document exact steps, inputs, and expected vs. actual behavior
- Identify the environment and conditions

### Step 2: Locate
- Trace the execution path from symptom to root cause
- Use the bug description to identify keyword-relevant files
- Follow import chains and call graphs
- Focus on the layer where the bug manifests

### Step 3: Scope
- Identify the minimum set of files that need changes
- Estimate lines of change per file
- Classify: is this a logic error, data error, or configuration error?

### Step 4: Fix
- Change ONLY what is necessary to fix the bug
- Do not refactor, reformat, or "improve" touched code
- If you notice other issues, create separate tickets

### Step 5: Verify
- Confirm the fix resolves the original reproduction case
- Run existing tests to ensure no regressions
- Add a regression test for this specific bug

### Step 6: Review
- Compare actual changes against initial scope estimate
- Remove any accidental scope creep
- Ensure commit message explains the "why"

## Scope Classification

| Category | Files Changed | Lines Changed | Risk |
|----------|--------------|---------------|------|
| Micro Fix | 1 file | 1-5 lines | Very Low |
| Small Fix | 1-2 files | 5-20 lines | Low |
| Medium Fix | 2-4 files | 20-50 lines | Medium |
| Large Fix | 5+ files | 50+ lines | High - consider splitting |

## Anti-Patterns

### The "While I'm Here" Anti-Pattern
Fixing unrelated issues because you happen to be in the file. Create separate tickets instead.

### The Refactor Disguised as a Bugfix
Restructuring code to fix a bug when a simpler change would work. Save refactoring for dedicated PRs.

### The Test-Only Fix
Adding tests that pass without changing production code. The bug is still there.

### The Configuration Shotgun
Changing multiple config values hoping one fixes the issue. Identify the specific root cause.

## Keywords to Scope Mapping

Common bug description keywords map to likely code areas:
- "login", "auth", "password" -> authentication modules
- "crash", "exception", "error" -> error handling, try/catch blocks
- "slow", "timeout", "performance" -> database queries, API calls, loops
- "display", "render", "layout" -> frontend components, CSS, templates
- "data", "missing", "null" -> data validation, null checks, defaults
- "permission", "access", "denied" -> authorization, role checks
- "email", "notification", "send" -> messaging, notification services
