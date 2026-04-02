---
description: Assess overall project health across code quality, tests, docs, and activity.
---

Run a project health assessment:

1. **Code Quality:**
   - Count TODO/FIXME/HACK/XXX comments — flag if > 20
   - Check for large files (> 500 lines) — suggest splitting
   - Look for code duplication patterns
   - Check for console.log/print debugging left in code
2. **Test Coverage:**
   - Identify test directories and frameworks
   - Count test files vs source files ratio
   - Flag source files with zero test coverage
   - Check if CI runs tests automatically
3. **Dependency Health:**
   - Count total dependencies (direct + transitive)
   - Check for outdated packages (if lockfile available)
   - Flag known security vulnerabilities
   - Check for unused dependencies
4. **Documentation:**
   - README exists and is non-trivial (> 50 lines)?
   - API documentation exists?
   - Contributing guide exists?
   - Changelog maintained?
5. **Git Activity:**
   - Commits in last 30 days
   - Active contributors
   - Open PRs age (flag if > 7 days old)
   - Branch count (flag if > 20 stale branches)
6. **Score each area** on a 1-5 scale. Output a health dashboard with overall grade (A-F) and top 5 recommended improvements.
