---
description: Apply a focused, minimal-change bugfix with minimal blast radius.
---

Execute a focused bugfix workflow:

1. **Understand the bug** — read the bug description, error message, or failing test. Identify the exact symptom.
2. **Locate the root cause** — trace the error to its origin. Use grep, stack traces, and git blame. Do NOT start fixing until the root cause is confirmed.
3. **Scope the fix** — determine the absolute minimum change needed:
   - How many files must change? (target: 1-2)
   - How many lines? (target: < 20)
   - Does any public API change? (target: no)
   - Are there downstream dependencies? (verify none break)
4. **Implement the fix** — make only the scoped changes. Do not refactor surrounding code, add features, or "clean up" nearby code.
5. **Verify the fix:**
   - Confirm the original bug is resolved
   - Run existing tests to ensure no regressions
   - If no test covers the bug, write one minimal test for the specific case
6. **Document** — write a commit message that explains: what broke, why, and what the fix does.

**Rules:**
- No drive-by refactoring
- No "while I'm here" improvements
- If the fix requires > 3 files or > 50 lines, stop and reassess — it may need a different approach
