---
name: pr-review-expert
description: Systematic PR review with blast radius analysis, security scanning, breaking change detection, test coverage delta, and performance impact assessment. Produces prioritized findings with a 35+ item checklist. Use when reviewing PRs that touch shared libraries, APIs, database schemas, auth, or security-sensitive code.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: code-review
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: github, gitlab, review-checklist
---

# PR Review Expert

**Tier:** POWERFUL
**Category:** Engineering / Quality Assurance
**Maintainer:** Claude Skills Team

## Overview

Structured, systematic code review for GitHub PRs and GitLab MRs. Goes beyond style nits to perform blast radius analysis, security vulnerability scanning, breaking change detection, test coverage delta calculation, and performance impact assessment. Produces reviewer-ready reports with prioritized findings categorized as must-fix, should-fix, and suggestions.

## Keywords

PR review, code review, pull request, merge request, blast radius, security scan, breaking changes, test coverage, review checklist, code quality

## Core Capabilities

### 1. Blast Radius Analysis
- Trace which files, services, and downstream consumers could break
- Identify shared libraries, types, and API contracts in the diff
- Map cross-service dependencies in monorepos
- Quantify impact severity (CRITICAL / HIGH / MEDIUM / LOW)

### 2. Security Scanning
- SQL injection via string interpolation
- XSS vectors (innerHTML, dangerouslySetInnerHTML)
- Hardcoded secrets and credentials
- Auth bypass patterns
- Insecure cryptographic functions
- Path traversal risks
- Prototype pollution

### 3. Breaking Change Detection
- API endpoint removals or renames
- Response schema modifications
- Required field additions
- Database column removals
- Environment variable changes
- TypeScript interface modifications

### 4. Test Coverage Analysis
- New code vs new test ratio
- Missing tests for new public functions
- Deleted tests without deleted code
- Coverage delta calculation

### 5. Performance Assessment
- N+1 query pattern detection
- Bundle size regression indicators
- Unbounded queries without LIMIT
- Missing database indexes for new query patterns

## When to Use

- Before merging any PR that touches shared libraries, APIs, or database schemas
- When a PR is large (>200 lines changed) and needs structured review
- For PRs in security-sensitive code paths (auth, payments, PII handling)
- After an incident to proactively review similar code changes
- For onboarding new contributors whose PRs need thorough feedback

## Review Workflow

### Step 1: Gather Context

```bash
PR=123

# PR metadata
gh pr view $PR --json title,body,labels,milestone,assignees | jq .

# Files changed
gh pr diff $PR --name-only

# Full diff for analysis
gh pr diff $PR > /tmp/pr-$PR.diff

# CI status
gh pr checks $PR
```

### Step 2: Blast Radius Analysis

For each changed file, determine its impact scope:

```bash
DIFF_FILES=$(gh pr diff $PR --name-only)

# Find all files that import changed modules
for file in $DIFF_FILES; do
  module=$(basename "$file" .ts | sed 's/\..*$//')
  echo "=== Dependents of $file ==="
  grep -rl "from.*$module\|import.*$module\|require.*$module" src/ --include="*.ts" --include="*.tsx" -l 2>/dev/null
done

# Check if changes span multiple services (monorepo)
echo "$DIFF_FILES" | cut -d/ -f1-2 | sort -u

# Identify shared contracts
echo "$DIFF_FILES" | grep -E "types/|interfaces/|schemas/|models/|shared/"
```

**Blast Radius Severity:**

| Severity | Criteria | Examples |
|----------|----------|---------|
| CRITICAL | Shared library used by 5+ consumers | `packages/utils/`, auth middleware, DB schema |
| HIGH | Cross-service impact, shared config | API contracts, env vars, shared types |
| MEDIUM | Single service internal change | Service handler, utility function |
| LOW | Isolated change, no dependents | UI component, test file, documentation |

### Step 3: Security Scan

```bash
DIFF=/tmp/pr-$PR.diff

# SQL injection — raw string interpolation in queries
grep -n "query\|execute\|raw(" $DIFF | grep -E '\$\{|f"|%s|format\(' | grep "^+"

# Hardcoded secrets
grep -nE "(password|secret|api_key|token|private_key)\s*=\s*['\"][^'\"]{8,}" $DIFF | grep "^+"

# AWS keys
grep -nE "AKIA[0-9A-Z]{16}" $DIFF

# XSS vectors
grep -n "dangerouslySetInnerHTML\|innerHTML\s*=" $DIFF | grep "^+"

# Auth bypass indicators
grep -n "bypass\|skip.*auth\|noauth\|TODO.*auth" $DIFF | grep "^+"

# Insecure crypto
grep -nE "md5\(|sha1\(|createHash\(['\"]md5|createHash\(['\"]sha1" $DIFF | grep "^+"

# eval/exec
grep -nE "\beval\(|\bexec\(|\bsubprocess\.call\(" $DIFF | grep "^+"

# Path traversal
grep -nE "path\.join\(.*req\.|readFile\(.*req\." $DIFF | grep "^+"

# Prototype pollution
grep -n "__proto__\|constructor\[" $DIFF | grep "^+"

# Sensitive data in logs
grep -nE "console\.(log|info|warn|error).*password\|console\.(log|info|warn|error).*token\|console\.(log|info|warn|error).*secret" $DIFF | grep "^+"
```

### Step 4: Breaking Change Detection

```bash
# API endpoint removals
grep "^-" $DIFF | grep -E "router\.(get|post|put|delete|patch)\(|@app\.(get|post|put|delete)"

# TypeScript interface/type removals
grep "^-" $DIFF | grep -E "^-\s*(export\s+)?(interface|type) "

# Required field additions to existing types
grep "^+" $DIFF | grep -E ":\s*(string|number|boolean)\s*$" | grep -v "?" # non-optional additions

# Database migrations: destructive operations
grep -E "DROP TABLE|DROP COLUMN|ALTER.*NOT NULL|TRUNCATE" $DIFF

# Index removals
grep -E "DROP INDEX|remove_index" $DIFF

# Removed env vars
grep "^-" $DIFF | grep -oE "process\.env\.[A-Z_]+" | sort -u

# New env vars (may not be set in production)
grep "^+" $DIFF | grep -oE "process\.env\.[A-Z_]+" | sort -u
```

### Step 5: Test Coverage Delta

```bash
# Count source vs test changes
SRC_FILES=$(gh pr diff $PR --name-only | grep -vE "\.test\.|\.spec\.|__tests__|\.stories\.")
TEST_FILES=$(gh pr diff $PR --name-only | grep -E "\.test\.|\.spec\.|__tests__")

echo "Source files changed: $(echo "$SRC_FILES" | grep -c .)"
echo "Test files changed:   $(echo "$TEST_FILES" | grep -c .)"

# New lines of logic vs test
LOGIC_LINES=$(grep "^+" $DIFF | grep -v "^+++" | grep -v "\.test\.\|\.spec\." | wc -l)
TEST_LINES=$(grep "^+" $DIFF | grep -v "^+++" | grep "\.test\.\|\.spec\." | wc -l)
echo "New logic lines: $LOGIC_LINES"
echo "New test lines:  $TEST_LINES"
```

**Coverage Rules:**
- New public function without tests: flag as must-fix
- Deleted tests without deleted code: flag as must-fix
- Coverage drop >5%: block merge
- Auth/payments paths: require near-100% coverage

### Step 6: Performance Impact

```bash
# N+1 patterns: DB calls that might be inside loops
grep -n "\.find\|\.findOne\|\.query\|db\." $DIFF | grep "^+" | head -20

# Heavy new dependencies
grep "^+" $DIFF | grep -E '"[a-z@].*":\s*"[0-9^~]' | head -10

# Unbounded loops
grep -n "while (true\|while(true" $DIFF | grep "^+"

# Missing await (accidentally sequential)
grep -n "await.*await" $DIFF | grep "^+"

# Large allocations
grep -n "new Array([0-9]\{4,\}\|Buffer\.alloc" $DIFF | grep "^+"
```

## Review Report Format

Structure every review using this format:

```markdown
## PR Review: [PR Title] (#NUMBER)

**Blast Radius:** HIGH — changes `lib/auth` used by 5 services
**Security:** 1 finding (medium severity)
**Tests:** Coverage delta +2% (3 new tests for 5 new functions)
**Breaking Changes:** None detected

---

### MUST FIX (Blocking)

**1. SQL Injection risk in `src/db/users.ts:42`**
Raw string interpolation in WHERE clause.
```diff
- const user = await db.query(`SELECT * FROM users WHERE id = '${userId}'`)
+ const user = await db.query('SELECT * FROM users WHERE id = $1', [userId])
```

**2. Missing auth check on `POST /api/admin/reset`**
No role verification before destructive operation.
Add `requireRole('admin')` middleware.

---

### SHOULD FIX (Non-blocking)

**3. N+1 pattern in `src/services/reports.ts:88`**
`findUser()` called inside `results.map()` — batch with `findManyUsers(ids)`.

**4. New env var `FEATURE_FLAG_X` not in `.env.example`**
Add to `.env.example` with description so other developers know about it.

---

### SUGGESTIONS

**5. Consider pagination for `GET /api/projects`**
Currently returns all projects without limit. Add `?limit=20&offset=0`.

---

### LOOKS GOOD
- Auth flow for new OAuth provider is thorough
- DB migration has proper rollback (`down()` method)
- Error handling is consistent with rest of codebase
- Test names clearly describe what they verify
```

## Complete Review Checklist (35 Items)

```markdown
### Scope and Context
- [ ] PR title accurately describes the change
- [ ] PR description explains WHY, not just WHAT
- [ ] Linked ticket exists and matches scope
- [ ] No unrelated changes (scope creep)
- [ ] Breaking changes documented in PR body

### Blast Radius
- [ ] All files importing changed modules identified
- [ ] Cross-service dependencies checked
- [ ] Shared types/interfaces reviewed for breakage
- [ ] New env vars documented in .env.example
- [ ] DB migrations are reversible (have rollback)

### Security
- [ ] No hardcoded secrets or API keys
- [ ] SQL queries use parameterized inputs
- [ ] User inputs validated and sanitized
- [ ] Auth/authorization on all new endpoints
- [ ] No XSS vectors (innerHTML, dangerouslySetInnerHTML)
- [ ] New dependencies checked for known CVEs
- [ ] No sensitive data in logs (PII, tokens, passwords)
- [ ] File uploads validated (type, size, content)
- [ ] CORS configured correctly for new endpoints

### Testing
- [ ] New public functions have unit tests
- [ ] Edge cases covered (empty, null, max values)
- [ ] Error paths tested (not just happy path)
- [ ] Integration tests for API endpoint changes
- [ ] No tests deleted without clear justification
- [ ] Test names describe what they verify

### Breaking Changes
- [ ] No API endpoints removed without deprecation
- [ ] No required fields added to existing responses
- [ ] No DB columns removed without migration plan
- [ ] No env vars removed that may be in production
- [ ] Backward-compatible for external consumers

### Performance
- [ ] No N+1 query patterns introduced
- [ ] DB indexes added for new query patterns
- [ ] No unbounded loops on large datasets
- [ ] No heavy new dependencies without justification
- [ ] Async operations correctly awaited
- [ ] Caching considered for expensive operations

### Code Quality
- [ ] No dead code or unused imports
- [ ] Error handling present (no empty catch blocks)
- [ ] Consistent with existing patterns
- [ ] Complex logic has explanatory comments
```

## Comment Labels

Use consistent labels so authors can quickly prioritize:

| Label | Meaning | Action Required |
|-------|---------|-----------------|
| `must:` | Blocking issue | Must fix before merge |
| `should:` | Important improvement | Should fix, but not blocking |
| `nit:` | Style/preference | Take it or leave it |
| `question:` | Need clarification | Respond before merge |
| `suggestion:` | Alternative approach | Consider, no action needed |
| `praise:` | Good pattern | No action needed |

## Common Pitfalls

- **Reviewing style over substance** — let the linter handle formatting; focus on logic, security, correctness
- **Missing blast radius** — a 5-line change in a shared utility can break 20 services
- **Approving untested happy paths** — always check that error paths have coverage
- **Ignoring migration risk** — NOT NULL additions need a default or two-phase migration
- **Indirect secret exposure** — secrets in error messages and logs, not just hardcoded values
- **Skipping large PRs** — if too large to review properly, request it be split
- **Trickle feedback** — batch all comments in one review round; do not drip-feed over hours

## Best Practices

1. **Read the linked ticket first** — context prevents false positives in the review
2. **Check CI before reviewing** — do not review code that fails to build
3. **Prioritize blast radius and security over style** — these are where real bugs live
4. **Label every comment** — `must:`, `nit:`, `question:` so authors know what matters
5. **Batch all comments in one round** — multiple partial reviews frustrate authors
6. **Acknowledge good patterns** — specific praise improves code quality culture
7. **Reproduce locally for non-trivial changes** — especially auth and performance-sensitive code
