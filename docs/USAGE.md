# Usage Guide

Detailed examples for using Claude Skills across all supported platforms.

---

## Using Skills Directly

Skills give your AI assistant deep domain knowledge. Once a skill is available, the assistant automatically activates the right skill based on your request.

### Python CLI Tools

Every skill with a `scripts/` directory includes standalone Python CLI tools. Run them directly from the command line.

**Code Quality Analysis:**
```bash
python engineering/senior-fullstack/scripts/code_quality_analyzer.py /path/to/project
```
```
Code Quality Report
====================
  Overall Score: 85/100
  Security:      90/100 (2 medium issues)
  Performance:   80/100 (3 optimization opportunities)
  Test Coverage: 75% (target: 80%)
  Documentation: 88/100

Recommendations:
  1. Update lodash to 4.17.21 (CVE-2020-8203)
  2. Optimize database queries in UserService
  3. Add integration tests for payment flow
```

**Feature Prioritization (RICE):**
```bash
python product-team/product-manager-toolkit/scripts/rice_prioritizer.py features.csv --json
```
```json
{
  "prioritized_features": [
    {"name": "SSO Integration", "reach": 8, "impact": 9, "confidence": 7, "effort": 5, "rice_score": 100.8},
    {"name": "Dark Mode", "reach": 9, "impact": 4, "confidence": 9, "effort": 3, "rice_score": 108.0},
    {"name": "Export to PDF", "reach": 6, "impact": 5, "confidence": 8, "effort": 2, "rice_score": 120.0}
  ]
}
```

**CLAUDE.md Optimization:**
```bash
python engineering/claude-code-mastery/scripts/claudemd_optimizer.py CLAUDE.md
```
```
CLAUDE.md Optimization Report
==============================
  File:         CLAUDE.md
  Lines:        142
  Est. Tokens:  ~1,850
  Budget Used:  9.3% of 20,000 token budget

Section Completeness:
  [ok] Project Overview
  [ok] Architecture
  [ok] Development Commands
  [!!] Missing: Code Style (recommended)
  [!!] Missing: Testing Strategy (recommended)

Redundancy Issues:
  - Line 34: Generic instruction "Be careful with..." (remove or make specific)
  - Lines 67-69: Duplicate of lines 12-14

Score: 72/100
```

**CI/CD Workflow Generation:**
```bash
python engineering/devops-workflow-engineer/scripts/workflow_generator.py --type ci --language python
```
```yaml
# Generated: CI Pipeline for Python
name: CI
on:
  pull_request:
    branches: [main, dev]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install ruff && ruff check .
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '${{ matrix.python-version }}' }
      - run: pip install -e ".[test]" && pytest --cov
```

**Financial DCF Valuation:**
```bash
python finance/financial-analyst/scripts/dcf_valuation.py valuation_data.json
```
```
DCF Valuation Summary
======================
  Revenue (Year 1):     $2,400,000
  Growth Rate:          25%
  Discount Rate (WACC): 12%
  Terminal Growth:      3%

  Enterprise Value:     $18,750,000
  Net Debt:             ($1,200,000)
  Equity Value:         $17,550,000

  Sensitivity Analysis:
  WACC \ Growth |   20%   |   25%   |   30%
  ------------- | ------- | ------- | -------
  10%           | $21.2M  | $24.1M  | $27.3M
  12%           | $16.8M  | $18.8M  | $21.0M
  14%           | $13.5M  | $14.9M  | $16.5M
```

**Mobile App Scaffolding:**
```bash
python engineering/senior-mobile/scripts/mobile_scaffold.py my-app --platform react-native --state zustand
```
```
Scaffolded: my-app (React Native + Expo Router)
================================================
  Platform:     React Native (Expo)
  Navigation:   Expo Router (file-based)
  State:        Zustand
  TypeScript:   Enabled

  Created:
    my-app/
    ├── app/                    # Expo Router pages
    │   ├── (tabs)/             # Tab navigation
    │   ├── (auth)/             # Auth screens
    │   └── _layout.tsx         # Root layout
    ├── src/
    │   ├── components/         # Reusable components
    │   ├── hooks/              # Custom hooks
    │   ├── services/           # API layer
    │   ├── stores/             # Zustand stores
    │   └── utils/              # Helpers
    ├── app.json
    ├── tsconfig.json
    └── package.json

  Next: cd my-app && npx expo start
```

---

## Using Agents

Agents are specialized AI personas that combine multiple skills with role-specific behavior. They live in the `agents/` directory and are invoked as Claude Code subagents.

**Code Review:**
```
> /agents/code-reviewer Review the last commit for security and quality issues
```
```markdown
## Code Review Summary

**Overall Score:** 7/10
**Risk Level:** Medium

### Critical Issues (Must Fix)
- [ ] **SQL Injection** at `src/db/queries.ts:45`
  - Use parameterized queries: `db.query('SELECT * FROM users WHERE id = $1', [userId])`
- [ ] **Missing auth check** at `src/routes/admin.ts:12`
  - Add `requireRole('admin')` middleware before handler

### Important (Should Fix)
- [ ] N+1 query in `src/services/orders.ts:78`
  - Use `JOIN` or batch fetch with `WHERE id IN (...)`

### Scores
| Category        | Score | Notes                          |
|-----------------|-------|--------------------------------|
| Correctness     | 8/10  | Logic is sound                 |
| Security        | 5/10  | SQL injection + missing auth   |
| Performance     | 7/10  | One N+1 query                  |
| Maintainability | 8/10  | Clean code, good naming        |
```

**Security Audit:**
```
> /agents/security-auditor Audit all API endpoints for OWASP Top 10 vulnerabilities
```
```markdown
## Security Audit Report

**Risk Level:** High
**Findings:** 1 critical, 2 high, 3 medium

### Critical Findings
| # | Finding              | File:Line            | OWASP | Severity |
|---|----------------------|----------------------|-------|----------|
| 1 | Command injection    | src/utils/exec.ts:23 | A03   | Critical |

### Recommendations
1. **Immediate:** Fix command injection, add JWT expiry
2. **Short-term:** Sanitize all error responses, add rate limiting
3. **Long-term:** Implement security headers (CSP, HSTS), add SAST to CI
```

**QA Analysis:**
```
> /agents/qa-engineer Analyze test coverage for the payment service
```
```markdown
## QA Report

**Quality Score:** 6/10
**Test Coverage:** ~45% (estimated)

### Coverage Map
| Module                | Functions | Tested | Coverage | Priority |
|-----------------------|-----------|--------|----------|----------|
| src/services/payment  | 12        | 5      | 42%      | Critical |
| src/services/refund   | 6         | 1      | 17%      | Critical |
| src/validators/card   | 4         | 4      | 100%     | Done     |

### Bugs Found
1. **[High]** Race condition in `processPayment` — double charge possible
```

**Documentation Generation:**
```
> /agents/doc-generator Generate API documentation for src/routes/
```

**Changelog Generation:**
```
> /agents/changelog-manager Generate changelog for the upcoming release
```

**Git Workflow:**
```
> /agents/git-workflow Prepare a release for v2.1.0
```

---

## Multi-Platform Usage

Claude Skills works with every major AI coding assistant. Each platform reads from its own config file.

| Platform | Config File | How to Use |
|----------|------------|------------|
| **Claude Code** | `CLAUDE.md` | Skills auto-activate. Use `/agents/name` for subagents |
| **OpenAI Codex** | `AGENTS.md` | Skills available via `.codex/` symlinks |
| **Cursor** | `.cursorrules` | Skills referenced in rules file |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Skills available in workspace |
| **Windsurf** | `.windsurfrules` | Skills referenced in rules file |
| **Cline** | `.clinerules` | Skills referenced in rules file |
| **Goose** | `.goosehints` | Skills referenced in hints file |
| **Aider** | `AGENTS.md` | Skills available via AGENTS.md |
| **Jules** | `AGENTS.md` | Skills available via AGENTS.md |
| **RooCode** | `AGENTS.md` | Skills available via AGENTS.md |

### Direct Paste Method

For any platform, you can paste the content of any `SKILL.md` directly into a conversation:

```
[Paste the content of any SKILL.md into your AI assistant]

Now help me with: [your specific task]
```

### Manual Copy Method

```bash
# Copy a skill to Claude Code
cp -r engineering/senior-fullstack ~/.claude/skills/senior-fullstack

# Copy a skill to Cursor
cp -r marketing/content-creator .cursor/skills/content-creator
```

---

## CI/CD Workflow Usage

Copy sample workflows from `templates/workflows/` to your project:

```bash
# Copy all workflows
mkdir -p .github/workflows
cp templates/workflows/*.yml .github/workflows/

# Or copy individual workflows
cp templates/workflows/ci-quality-gate.yml .github/workflows/
```

Once installed, workflows trigger automatically based on events (PRs, pushes, labels). See [WORKFLOWS.md](WORKFLOWS.md) for the full list and setup guide.
