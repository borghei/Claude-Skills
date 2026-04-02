---
description: Generate a changelog from git history since the last tag or release.
---

Generate a structured changelog:

1. **Identify the baseline** — find the most recent git tag or release. If none, use the first commit.
2. **Collect all commits** since baseline using `git log --oneline`.
3. **Categorize by conventional commit type:**
   - **Added**: `feat:` commits — new features
   - **Fixed**: `fix:` commits — bug fixes
   - **Changed**: `refactor:`, `perf:` commits — modifications
   - **Documentation**: `docs:` commits
   - **Deprecated**: any commits marking deprecations
   - **Removed**: any commits removing features
   - **Security**: security-related fixes
4. **Extract breaking changes** — look for `BREAKING CHANGE:` in commit bodies or `!` after type.
5. **Format as Keep a Changelog** (keepachangelog.com):
   ```
   ## [Unreleased] - YYYY-MM-DD
   ### Added
   ### Fixed
   ### Changed
   ### Breaking Changes
   ```
6. **Include PR references** where available (e.g., `(#123)`).
7. Output the changelog content ready to prepend to CHANGELOG.md.
