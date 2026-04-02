---
description: Scan and prioritize technical debt in the codebase.
---

Perform a tech debt audit:

1. **Scan for debt markers:**
   - `TODO`, `FIXME`, `HACK`, `XXX`, `WORKAROUND` comments — count and categorize
   - `@deprecated` annotations without removal timeline
   - Disabled tests (`skip`, `xit`, `@pytest.mark.skip`)
2. **Code complexity:**
   - Files over 500 lines — candidates for splitting
   - Functions over 50 lines — candidates for extraction
   - Deep nesting (> 4 levels) — candidates for early returns
   - Duplicated code blocks (similar patterns in multiple files)
3. **Dependency debt:**
   - Outdated packages (major versions behind)
   - Packages with known vulnerabilities
   - Unused dependencies (imported but never used)
   - Pinned to exact versions without update strategy
4. **Test debt:**
   - Source files with no corresponding test file
   - Test files with no assertions
   - Flaky tests (if CI history available)
5. **Documentation debt:**
   - Public APIs without documentation
   - Stale README sections
   - Missing architecture decision records
6. **Score each item** on Impact (1-5) x Effort (1-5). Priority = Impact / Effort.
7. **Output a prioritized tech debt backlog** with: item, type, location, impact, effort, priority score, and suggested approach.
