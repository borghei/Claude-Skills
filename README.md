<p align="center">
  <img src="assets/header.svg" alt="AI Skills Library" width="100%"/>
</p>

# AI Skills Library

**The universal AI skills library for every coding assistant** — 97 expert-level skills with 178 Python automation tools, 6 subagents, and 12 CI/CD workflows across 13 professional domains.

[![License: MIT + Commons Clause](https://img.shields.io/badge/License-MIT_+_Commons_Clause-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-purple.svg)](https://claude.ai/code)
[![Cursor](https://img.shields.io/badge/Cursor-00D1FF.svg)](https://cursor.com)
[![GitHub Copilot](https://img.shields.io/badge/Copilot-000000.svg)](https://github.com/features/copilot)
[![OpenAI Codex](https://img.shields.io/badge/Codex-412991.svg)](https://openai.com/codex)
[![Windsurf](https://img.shields.io/badge/Windsurf-0EA5E9.svg)](https://codeium.com/windsurf)
[![Cline](https://img.shields.io/badge/Cline-EC4899.svg)](https://github.com/cline/cline)
[![Aider](https://img.shields.io/badge/Aider-14B8A6.svg)](https://aider.chat)
[![97 Skills](https://img.shields.io/badge/Skills-97-brightgreen.svg)](#skills-library-97-skills)
[![178 Tools](https://img.shields.io/badge/Python_Tools-178-blue.svg)](#python-automation-tools-178)

## What You Get

| | |
|---|---|
| **97 Skills** | Production-ready expertise across engineering, marketing, product, finance, HR, sales, compliance, and more |
| **178 Python Tools** | CLI scripts for code quality, SEO, DCF valuation, RICE prioritization, scaffolding, and beyond — all standard library, no ML dependencies |
| **13 Domains** | Engineering, Marketing, Product, Project Management, C-Level Advisory, RA/QM Compliance, Business Growth, Finance, Data Analytics, HR, Sales, Advanced Engineering, Standards |
| **6 Subagents** | Autonomous Claude Code agents for code review, security audit, QA, docs, changelog, and git workflows |
| **12 CI/CD Workflows** | Quality gates, release drafting, skill validation, auto-updates — zero configuration needed |
| **10 Platforms** | Claude Code, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose, Jules, RooCode |

---

## Table of Contents

- [What You Get](#what-you-get)
- [Supported Platforms](#supported-platforms)
- [How to Install](#how-to-install)
- [How to Use](#how-to-use)
  - [Using Skills](#1-using-skills-domain-expertise)
  - [Using Subagents](#2-using-subagents-autonomous-workflows)
  - [Using Workflows](#3-using-workflows-cicd-automation)
- [Skills Library (97 Skills)](#skills-library-97-skills)
- [Claude Code Subagents](#claude-code-subagents)
- [GitHub Workflows (12)](#github-workflows-12)
- [Repository Structure](#repository-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Supported Platforms

Works out of the box with every major AI coding assistant:

| Platform | Config File | Status |
|----------|------------|--------|
| **Claude Code** | `CLAUDE.md` | Primary |
| **OpenAI Codex** | `AGENTS.md` | Full |
| **Cursor** | `.cursorrules` | Full |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Full |
| **Windsurf** | `.windsurfrules` | Full |
| **Cline** | `.clinerules` | Full |
| **Goose** | `.goosehints` | Full |
| **Aider** | `AGENTS.md` | Full |
| **Jules** | `AGENTS.md` | Full |
| **RooCode / Kilo Code** | `AGENTS.md` | Full |

---

## How to Install

### Option A: Clone & Use the Skill Installer (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/borghei/Claude-Skills.git
cd Claude-Skills

# 2. Browse available skills
python scripts/skill-installer.py list
python scripts/skill-installer.py list --group engineering-team

# 3. Install a skill to your agent of choice
python scripts/skill-installer.py install senior-fullstack --agent claude --auto-update
python scripts/skill-installer.py install content-creator --agent cursor --auto-update
python scripts/skill-installer.py install ceo-advisor --agent vscode

# 4. Keep skills up to date
python scripts/skill-installer.py update
```

The installer enforces **one skill per domain group** by default (use `--force` to override), tracks installed skills in a `.claude-skills.json` manifest, and supports auto-updates.

**Supported agents:** `claude`, `cursor`, `vscode`, `copilot`, `codex`, `goose`, `project`

### Option B: Claude Code Plugin Marketplace

```bash
# In Claude Code, run:
/plugin marketplace add borghei/Claude-Skills

# Install entire domain bundles:
/plugin install engineering-skills@claude-code-skills   # 24 skills
/plugin install marketing-skills@claude-code-skills     # 10 skills
/plugin install ra-qm-skills@claude-code-skills         # 12 skills

# Or install individual skills:
/plugin install senior-fullstack@claude-code-skills
/plugin install content-creator@claude-code-skills

# Update anytime:
/plugin update
```

### Option C: Universal Installer (40+ AI Agents)

```bash
# Install to all supported agents at once
npx agent-skills-cli add borghei/Claude-Skills

# Or target a specific agent
npx agent-skills-cli add borghei/Claude-Skills --agent claude
npx agent-skills-cli add borghei/Claude-Skills --agent cursor
npx agent-skills-cli add borghei/Claude-Skills --agent vscode
```

### Option D: OpenAI Codex

```bash
git clone https://github.com/borghei/Claude-Skills.git
cd Claude-Skills
./scripts/codex-install.sh
```

### Option E: Manual / Direct Use

Copy any skill folder into your agent's skills directory, or simply paste the `SKILL.md` content directly into a Claude conversation:

```bash
# Copy a skill to Claude Code
cp -r engineering-team/senior-fullstack ~/.claude/skills/senior-fullstack

# Copy a skill to Cursor
cp -r marketing-skill/content-creator .cursor/skills/content-creator
```

Or paste directly:
```
[Paste the content of any SKILL.md into Claude]

Now help me with: [your specific task]
```

See [INSTALLATION.md](INSTALLATION.md) for the full guide with auto-update configuration, troubleshooting, and per-agent details.

---

## How to Use

### 1. Using Skills (Domain Expertise)

Skills give Claude deep domain knowledge. Once installed, Claude automatically activates the right skill based on your request. You can also reference them directly.

**Example — Code Quality Analysis:**
```bash
# Run the Python tool directly
python engineering-team/senior-fullstack/scripts/code_quality_analyzer.py /path/to/project
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

**Example — Feature Prioritization:**
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

**Example — CLAUDE.md Optimization:**
```bash
python engineering-team/claude-code-mastery/scripts/claudemd_optimizer.py CLAUDE.md
```
```
CLAUDE.md Optimization Report
==============================
  File:         CLAUDE.md
  Lines:        142
  Est. Tokens:  ~1,850
  Budget Used:  9.3% of 20,000 token budget

Section Completeness:
  ✓ Project Overview
  ✓ Architecture
  ✓ Development Commands
  ✗ Missing: Code Style (recommended)
  ✗ Missing: Testing Strategy (recommended)

Redundancy Issues:
  - Line 34: Generic instruction "Be careful with..." (remove or make specific)
  - Lines 67-69: Duplicate of lines 12-14

Score: 72/100
  Recommendations:
  1. [HIGH] Add Code Style section with linter config
  2. [MEDIUM] Remove 3 redundant instructions to save ~120 tokens
  3. [LOW] Add Testing Strategy section
```

**Example — CI/CD Workflow Generation:**
```bash
python engineering-team/devops-workflow-engineer/scripts/workflow_generator.py --type ci --language python
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

**Example — Financial DCF Valuation:**
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

**Example — Mobile App Scaffolding:**
```bash
python engineering-team/senior-mobile/scripts/mobile_scaffold.py my-app --platform react-native --state zustand
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

### 2. Using Subagents (Autonomous Workflows)

Subagents are specialized Claude Code instances that run independently with their own tools and instructions. Invoke them with `/agents/name` in Claude Code.

**Example — Code Review:**
```
> /agents/code-reviewer Review the last commit for security and quality issues
```
```markdown
## Code Review Summary

**Overall Score:** 7/10
**Risk Level:** Medium

### Critical Issues (Must Fix)
- [ ] **SQL Injection** at `src/db/queries.ts:45`
  - **Why:** User input concatenated directly into SQL query
  - **Fix:** Use parameterized queries: `db.query('SELECT * FROM users WHERE id = $1', [userId])`

- [ ] **Missing auth check** at `src/routes/admin.ts:12`
  - **Why:** Admin endpoint accessible without role verification
  - **Fix:** Add `requireRole('admin')` middleware before handler

### Important (Should Fix)
- [ ] N+1 query in `src/services/orders.ts:78` — fetching user for each order in loop
  - **Fix:** Use `JOIN` or batch fetch with `WHERE id IN (...)`

### Suggestions (Nice to Have)
- [ ] Consider adding rate limiting to `src/routes/auth.ts:30`

### Positive Highlights
- Clean separation of concerns in service layer
- Good error handling patterns in API middleware

### Scores
| Category        | Score | Notes                          |
|-----------------|-------|--------------------------------|
| Correctness     | 8/10  | Logic is sound                 |
| Security        | 5/10  | SQL injection + missing auth   |
| Performance     | 7/10  | One N+1 query                  |
| Maintainability | 8/10  | Clean code, good naming        |
| Architecture    | 7/10  | Well-structured                |
```

**Example — Security Audit:**
```
> /agents/security-auditor Audit all API endpoints for OWASP Top 10 vulnerabilities
```
```markdown
## Security Audit Report

**Risk Level:** High
**Findings:** 1 critical, 2 high, 3 medium
**Scan Date:** 2026-02-27

### Critical Findings
| # | Finding              | File:Line            | OWASP | Severity |
|---|----------------------|----------------------|-------|----------|
| 1 | Command injection    | src/utils/exec.ts:23 | A03   | Critical |

**Details:**
1. **Command Injection via user input**
   - **Location:** src/utils/exec.ts:23
   - **Description:** `exec(`ffmpeg ${userInput}`)` passes unsanitized input to shell
   - **Impact:** Remote code execution — attacker can run arbitrary commands
   - **Remediation:**
     ```typescript
     // Before (vulnerable)
     exec(`ffmpeg ${userInput}`)
     // After (safe)
     execFile('ffmpeg', ['-i', sanitizedInput])
     ```
   - **References:** CWE-78

### High Findings
| # | Finding                    | File:Line             | OWASP |
|---|----------------------------|-----------------------|-------|
| 2 | JWT with no expiry         | src/auth/jwt.ts:15    | A07   |
| 3 | Secrets in error responses | src/middleware/err.ts:8| A09   |

### Recommendations
1. **Immediate:** Fix command injection, add JWT expiry
2. **Short-term:** Sanitize all error responses, add rate limiting
3. **Long-term:** Implement security headers (CSP, HSTS), add SAST to CI
```

**Example — QA Analysis:**
```
> /agents/qa-engineer Analyze test coverage for the payment service
```
```markdown
## QA Report

**Quality Score:** 6/10
**Test Coverage:** ~45% (estimated)
**Critical Gaps:** 3 areas needing immediate attention

### Coverage Map
| Module                | Functions | Tested | Coverage | Priority |
|-----------------------|-----------|--------|----------|----------|
| src/services/payment  | 12        | 5      | 42%      | Critical |
| src/services/refund   | 6         | 1      | 17%      | Critical |
| src/validators/card   | 4         | 4      | 100%     | Done     |
| src/utils/currency    | 8         | 6      | 75%      | Medium   |

### Critical Gaps (Must Test)
1. **processPayment()** — Handles real money, zero test coverage
2. **handleWebhook()** — Stripe webhook processing, no edge case tests
3. **issueRefund()** — Only happy path tested, no failure scenarios

### Bugs Found
1. **[High]** Race condition in `processPayment` at src/services/payment.ts:67
   - **Impact:** Double charge possible if two requests hit simultaneously
   - **Reproduction:** Concurrent POST to /api/payments with same idempotency key

### Recommendations
1. Add integration tests for payment → refund flow
2. Add concurrency tests with idempotency key enforcement
3. Mock Stripe in tests instead of skipping payment tests entirely
```

**Example — Documentation Generation:**
```
> /agents/doc-generator Generate API documentation for src/routes/
```
```markdown
## Generated Documentation

### API Endpoints

| Method | Endpoint          | Auth     | Description              |
|--------|-------------------|----------|--------------------------|
| POST   | /api/auth/login   | None     | Authenticate user        |
| POST   | /api/auth/signup  | None     | Register new account     |
| GET    | /api/users/:id    | Bearer   | Get user profile         |
| PUT    | /api/users/:id    | Bearer   | Update user profile      |
| GET    | /api/orders       | Bearer   | List user orders         |
| POST   | /api/orders       | Bearer   | Create new order         |
| POST   | /api/payments     | Bearer   | Process payment          |

### POST /api/auth/login
**Request:**
```json
{ "email": "user@example.com", "password": "..." }
```
**Response (200):**
```json
{ "token": "eyJhbG...", "user": { "id": "123", "email": "..." } }
```
**Response (401):**
```json
{ "error": "Invalid credentials" }
```

Updated: README.md, docs/api.md
Created: docs/architecture.md
```

**Example — Changelog Generation:**
```
> /agents/changelog-manager Generate changelog for the upcoming release
```
```markdown
## [2.1.0] - 2026-02-27

### Added
- Add payment retry logic with exponential backoff (#142)
- Add Stripe webhook signature verification (#138)
- Add user export endpoint for GDPR compliance (#135)

### Changed
- Upgrade Node.js from 18 to 22 in CI pipeline
- Improve error messages in authentication flow

### Fixed
- Fix race condition in concurrent payment processing (#141)
- Fix timezone handling in order timestamps (#139)

### Security
- Update jsonwebtoken to 9.0.2 to patch CVE-2024-XXXXX
- Add rate limiting to authentication endpoints

**Version:** MINOR bump (new features, backwards compatible)
```

**Example — Git Workflow:**
```
> /agents/git-workflow Prepare a release for v2.1.0
```
```
Pre-commit check:
  ✓ No secrets detected
  ✓ No .env files staged
  ✓ All changes match intended scope

Branch: release/v2.1.0 (created from dev)

Updated files:
  ✓ CHANGELOG.md — Added [2.1.0] section
  ✓ README.md — Updated version badge to 2.1.0

Commit: release: prepare v2.1.0

PR created: #156 "Release v2.1.0" (base: main)
  - Title: Release v2.1.0
  - Labels: release
  - Reviewers: assigned

Next steps after merge:
  git tag -a v2.1.0 -m "Release v2.1.0"
  git push origin v2.1.0
```

---

### 3. Using Workflows (CI/CD Automation)

The 12 GitHub workflows run automatically on PRs and pushes. No configuration needed — they activate based on file changes.

**Code Quality Gate** — Triggers on every PR with Python changes:
```
✓ Python Syntax Check     — 178/178 scripts compiled successfully
✓ Flake8 Lint             — 0 errors (E9, F63, F7, F82)
✓ Bandit Security Scan    — 0 high-severity issues
✓ CLI Standards           — 178/178 scripts have argparse + --help
```

**Documentation Check** — Triggers on PRs with markdown changes:
```
✓ YAML Frontmatter        — 97/97 SKILL.md files have valid frontmatter
✓ Required Fields          — All files have name + description
✓ Internal Links           — 0 broken links detected
✓ Skill Count              — 97 skills across 13 domains
```

**Changelog Enforcer** — Triggers on PRs to main/dev:
```
⚠ CHANGELOG.md was not updated in this PR.

  Changed files:
    - engineering-team/senior-fullstack/scripts/code_quality_analyzer.py
    - engineering-team/senior-fullstack/SKILL.md

  Suggested changelog entry:
    ### Changed
    - Improve code quality analyzer scoring algorithm in senior-fullstack
```

**Skill Validation** — Triggers on PRs touching skill packages:
```
✓ senior-fullstack         — SKILL.md (342 lines), 3 scripts, 2 refs, 1 asset → Tier 1
✓ claude-code-mastery      — SKILL.md (488 lines), 3 scripts, 3 refs, 2 assets → Tier 1
✗ senior-cloud-architect   — SKILL.md (89 lines), 0 scripts → Tier 3 (needs upgrade)

Quality Report:
  Tier 1 (full stack):  52 skills
  Tier 2 (partial):     28 skills
  Tier 3 (docs only):   17 skills
```

**Release Drafter** — Auto-generates release notes on push to main:
```markdown
## What's New in v2.0.0

### Repository Stats
- **97** skills across **13** domains
- **178** Python automation tools
- **6** Claude Code subagents
- **12** CI/CD workflows

### New Skills
- claude-code-mastery (engineering-team)
- codex-cli-specialist (engineering-team)
- devops-workflow-engineer (engineering-team)

### Installation
git clone https://github.com/borghei/Claude-Skills.git
python scripts/skill-installer.py install <skill-name> --agent claude
```

---

## Skills Library (97 Skills)

### Engineering Team (24)
Core engineering expertise with Python automation tools, references, and templates.

| Skill | Description | Tools |
|-------|-------------|-------|
| [senior-architect](engineering-team/senior-architect/SKILL.md) | System design, distributed systems, architectural patterns | 2 |
| [senior-frontend](engineering-team/senior-frontend/SKILL.md) | React patterns, state management, performance, accessibility | 2 |
| [senior-backend](engineering-team/senior-backend/SKILL.md) | API design, microservices, databases, caching, queues | 2 |
| [senior-fullstack](engineering-team/senior-fullstack/SKILL.md) | React, Node.js, databases, API design, system architecture | 3 |
| [senior-qa](engineering-team/senior-qa/SKILL.md) | Test strategy, automation frameworks, performance testing | 2 |
| [senior-devops](engineering-team/senior-devops/SKILL.md) | Docker, Kubernetes, Terraform, CI/CD, monitoring, SRE | 2 |
| [senior-secops](engineering-team/senior-secops/SKILL.md) | Security operations, vulnerability management, incident response | 2 |
| [senior-security](engineering-team/senior-security/SKILL.md) | OWASP, threat modeling, penetration testing, compliance | 2 |
| [senior-mobile](engineering-team/senior-mobile/SKILL.md) | React Native, iOS, Android, cross-platform, app store | 3 |
| [senior-cloud-architect](engineering-team/senior-cloud-architect/SKILL.md) | AWS, GCP, Azure, multi-cloud, cost optimization | - |
| [senior-data-scientist](engineering-team/senior-data-scientist/SKILL.md) | A/B testing, statistical analysis, feature engineering | 3 |
| [senior-data-engineer](engineering-team/senior-data-engineer/SKILL.md) | Airflow, Spark, data pipelines, warehousing | 3 |
| [senior-ml-engineer](engineering-team/senior-ml-engineer/SKILL.md) | ML pipelines, model deployment, MLOps, RAG systems | 3 |
| [senior-prompt-engineer](engineering-team/senior-prompt-engineer/SKILL.md) | Prompt optimization, LLM evaluation, agents | 3 |
| [senior-computer-vision](engineering-team/senior-computer-vision/SKILL.md) | Object detection, image segmentation, model training | 3 |
| [aws-solution-architect](engineering-team/aws-solution-architect/SKILL.md) | Serverless patterns, CloudFormation, cost optimization | 2 |
| [code-reviewer](engineering-team/code-reviewer/SKILL.md) | PR analysis, code quality checking, review automation | 2 |
| [incident-commander](engineering-team/incident-commander/SKILL.md) | Incident response, severity classification, RCA | 3 |
| [ms365-tenant-manager](engineering-team/ms365-tenant-manager/SKILL.md) | Office 365/Azure AD administration | 2 |
| [tdd-guide](engineering-team/tdd-guide/SKILL.md) | Test-driven development workflow | 2 |
| [tech-stack-evaluator](engineering-team/tech-stack-evaluator/SKILL.md) | Framework comparison, TCO analysis | 2 |
| [claude-code-mastery](engineering-team/claude-code-mastery/SKILL.md) | CLAUDE.md optimization, skill authoring, subagents, hooks | 3 |
| [codex-cli-specialist](engineering-team/codex-cli-specialist/SKILL.md) | Cross-platform skill authoring, Codex CLI, conversion tools | 3 |
| [devops-workflow-engineer](engineering-team/devops-workflow-engineer/SKILL.md) | GitHub Actions, CI/CD pipelines, deployment strategies | 3 |

### Advanced Engineering (12)
Enterprise-grade skills with sophisticated analysis tooling.

| Skill | Description | Tools |
|-------|-------------|-------|
| [agent-designer](engineering/agent-designer/SKILL.md) | Multi-agent architecture, tool schema generation | 3 |
| [api-design-reviewer](engineering/api-design-reviewer/SKILL.md) | REST API linting, breaking change detection, scoring | 3 |
| [database-designer](engineering/database-designer/SKILL.md) | Schema analysis, ERD generation, index optimization | 3 |
| [dependency-auditor](engineering/dependency-auditor/SKILL.md) | Multi-language dependency scanning, license compliance | 3 |
| [interview-system-designer](engineering/interview-system-designer/SKILL.md) | Interview loop design, question banks, calibration | 3 |
| [migration-architect](engineering/migration-architect/SKILL.md) | Zero-downtime migration planning, rollback strategies | 3 |
| [observability-designer](engineering/observability-designer/SKILL.md) | SLO design, alert optimization, dashboard generation | 3 |
| [rag-architect](engineering/rag-architect/SKILL.md) | RAG pipeline building, chunking optimization | 3 |
| [release-manager](engineering/release-manager/SKILL.md) | Automated changelog, semantic versioning | 3 |
| [skill-tester](engineering/skill-tester/SKILL.md) | Meta-skill validator, quality scoring | 3 |
| [tech-debt-tracker](engineering/tech-debt-tracker/SKILL.md) | AST parsing, debt prioritization, trend analysis | 3 |

### C-Level Advisory (5)
Strategic decision-making for executive leadership.

| Skill | Description | Tools |
|-------|-------------|-------|
| [ceo-advisor](c-level-advisor/ceo-advisor/SKILL.md) | Strategic planning, board governance, investor relations, M&A | 2 |
| [cto-advisor](c-level-advisor/cto-advisor/SKILL.md) | Technical strategy, architecture decisions, engineering leadership | 2 |
| [cfo-advisor](c-level-advisor/cfo-advisor/SKILL.md) | Financial planning, fundraising, unit economics, treasury | - |
| [cmo-advisor](c-level-advisor/cmo-advisor/SKILL.md) | Brand strategy, demand generation, marketing leadership | - |
| [coo-advisor](c-level-advisor/coo-advisor/SKILL.md) | Operations strategy, process optimization, scaling | - |

### Marketing (10)
Data-driven marketing with Python automation tools.

| Skill | Description | Tools |
|-------|-------------|-------|
| [content-creator](marketing-skill/content-creator/SKILL.md) | Brand voice analyzer, SEO optimizer, content frameworks | 2 |
| [marketing-demand-acquisition](marketing-skill/marketing-demand-acquisition/SKILL.md) | Demand gen, paid media, SEO, partnerships | 1 |
| [marketing-strategy-pmm](marketing-skill/marketing-strategy-pmm/SKILL.md) | Positioning, GTM, competitive intelligence | - |
| [app-store-optimization](marketing-skill/app-store-optimization/SKILL.md) | ASO for iOS & Android | - |
| [campaign-analytics](marketing-skill/campaign-analytics/SKILL.md) | Multi-touch attribution, funnel analysis, ROI | 3 |
| [social-media-analyzer](marketing-skill/social-media-analyzer/SKILL.md) | Social media performance tracking, engagement metrics | - |
| [brand-strategist](marketing-skill/brand-strategist/SKILL.md) | Brand positioning, identity systems, brand architecture | - |
| [growth-marketer](marketing-skill/growth-marketer/SKILL.md) | Experimentation, funnel optimization, viral loops, retention | - |
| [marketing-analyst](marketing-skill/marketing-analyst/SKILL.md) | Attribution modeling, ROI analysis, campaign optimization | - |
| [seo-specialist](marketing-skill/seo-specialist/SKILL.md) | Technical SEO, keyword research, link building, analytics | - |

### Product Team (7)
User-centered product development with automation tools.

| Skill | Description | Tools |
|-------|-------------|-------|
| [product-manager-toolkit](product-team/product-manager-toolkit/SKILL.md) | RICE prioritizer, interview analyzer, PRD templates | 2 |
| [agile-product-owner](product-team/agile-product-owner/SKILL.md) | User stories, sprint planning, velocity tracking | 1 |
| [product-strategist](product-team/product-strategist/SKILL.md) | OKR cascade, market analysis, vision setting | 1 |
| [ui-design-system](product-team/ui-design-system/SKILL.md) | Design tokens, component documentation, responsive design | 1 |
| [ux-researcher-designer](product-team/ux-researcher-designer/SKILL.md) | Personas, journey mapping, usability research | 1 |
| [product-designer](product-team/product-designer/SKILL.md) | UI/UX design, prototyping, user research, design systems | - |
| [design-system-lead](product-team/design-system-lead/SKILL.md) | Design tokens, component libraries, documentation | - |

### Project Management (9)
Delivery excellence with Atlassian MCP integration.

| Skill | Description | Tools |
|-------|-------------|-------|
| [senior-pm](project-management/senior-pm/SKILL.md) | Portfolio management, quantitative risk analysis, WSJF | 3 |
| [scrum-master](project-management/scrum-master/SKILL.md) | Sprint analytics, velocity forecasting, team health | 3 |
| [jira-expert](project-management/jira-expert/SKILL.md) | JQL mastery, workflows, automation, dashboards | - |
| [confluence-expert](project-management/confluence-expert/SKILL.md) | Knowledge management, space architecture | - |
| [atlassian-admin](project-management/atlassian-admin/SKILL.md) | System administration, security, integrations | - |
| [atlassian-templates](project-management/atlassian-templates/SKILL.md) | Template design, custom blueprints | - |
| [agile-coach](project-management/agile-coach/SKILL.md) | Transformation, framework implementation, coaching | - |
| [delivery-manager](project-management/delivery-manager/SKILL.md) | Release management, deployment, incident response | - |
| [program-manager](project-management/program-manager/SKILL.md) | Multi-project coordination, portfolio governance | - |

### Regulatory Affairs & Quality Management (12)
HealthTech/MedTech compliance across ISO, MDR, FDA, and GDPR.

| Skill | Description |
|-------|-------------|
| [regulatory-affairs-head](ra-qm-team/regulatory-affairs-head/SKILL.md) | Regulatory strategy, FDA/EU pathways, market access |
| [quality-manager-qmr](ra-qm-team/quality-manager-qmr/SKILL.md) | QMS effectiveness, compliance dashboards |
| [quality-manager-qms-iso13485](ra-qm-team/quality-manager-qms-iso13485/SKILL.md) | ISO 13485 compliance, design control |
| [capa-officer](ra-qm-team/capa-officer/SKILL.md) | CAPA management, root cause analysis |
| [quality-documentation-manager](ra-qm-team/quality-documentation-manager/SKILL.md) | Document control, technical file building |
| [risk-management-specialist](ra-qm-team/risk-management-specialist/SKILL.md) | Risk register, FMEA, ISO 14971 |
| [information-security-manager-iso27001](ra-qm-team/information-security-manager-iso27001/SKILL.md) | ISMS compliance, security risk assessment |
| [gdpr-dsgvo-expert](ra-qm-team/gdpr-dsgvo-expert/SKILL.md) | GDPR/DSGVO compliance, DPIA generation |
| [mdr-745-specialist](ra-qm-team/mdr-745-specialist/SKILL.md) | EU MDR compliance, UDI management |
| [fda-consultant-specialist](ra-qm-team/fda-consultant-specialist/SKILL.md) | FDA submissions, QSR 820 compliance |
| [qms-audit-expert](ra-qm-team/qms-audit-expert/SKILL.md) | Audit planning, finding tracking |
| [isms-audit-expert](ra-qm-team/isms-audit-expert/SKILL.md) | ISMS audit planning, security controls |

### Business Growth (3)
Revenue optimization and customer success with Python tools.

| Skill | Description | Tools |
|-------|-------------|-------|
| [customer-success-manager](business-growth/customer-success-manager/SKILL.md) | Health scoring, churn prediction, expansion analysis | 3 |
| [revenue-operations](business-growth/revenue-operations/SKILL.md) | Pipeline analytics, forecast accuracy, GTM efficiency | 3 |
| [sales-engineer](business-growth/sales-engineer/SKILL.md) | RFP analysis, competitive positioning, POC planning | 3 |

### Finance (1)
Financial analysis and valuation with Python tools.

| Skill | Description | Tools |
|-------|-------------|-------|
| [financial-analyst](finance/financial-analyst/SKILL.md) | DCF valuation, ratio analysis, budget variance, forecasting | 4 |

### Data & Analytics (5)
Data-driven insights and ML operations.

| Skill | Description |
|-------|-------------|
| [data-analyst](data-analytics/data-analyst/SKILL.md) | SQL, visualization, statistical analysis, reporting |
| [data-scientist](data-analytics/data-scientist/SKILL.md) | ML modeling, experimentation, statistical inference |
| [business-intelligence](data-analytics/business-intelligence/SKILL.md) | Dashboard design, KPI development, data storytelling |
| [analytics-engineer](data-analytics/analytics-engineer/SKILL.md) | dbt, data modeling, transformation, semantic layer |
| [ml-ops-engineer](data-analytics/ml-ops-engineer/SKILL.md) | Model deployment, monitoring, feature stores, pipelines |

### Sales & Success (5)
Revenue generation and customer success.

| Skill | Description |
|-------|-------------|
| [account-executive](sales-success/account-executive/SKILL.md) | MEDDIC, pipeline management, negotiation, closing |
| [customer-success-manager](sales-success/customer-success-manager/SKILL.md) | Onboarding, retention, health scoring, expansion |
| [sales-engineer](sales-success/sales-engineer/SKILL.md) | Technical demos, POC design, RFP responses |
| [solutions-architect](sales-success/solutions-architect/SKILL.md) | Solution design, integration architecture, technical sales |
| [sales-operations](sales-success/sales-operations/SKILL.md) | CRM, territory planning, compensation, forecasting |

### HR & People (4)
People operations and workforce analytics.

| Skill | Description |
|-------|-------------|
| [hr-business-partner](hr-operations/hr-business-partner/SKILL.md) | Talent strategy, performance management, org design |
| [talent-acquisition](hr-operations/talent-acquisition/SKILL.md) | Recruiting, sourcing, employer branding, hiring analytics |
| [operations-manager](hr-operations/operations-manager/SKILL.md) | Process optimization, resource management, efficiency |
| [people-analytics](hr-operations/people-analytics/SKILL.md) | Workforce analytics, predictive modeling, survey analysis |

---

## Claude Code Subagents

Six specialized subagents in `.claude/agents/` for autonomous code review, documentation, QA, security, changelog, and git workflows.

| Agent | What It Does | Invoke With |
|-------|-------------|-------------|
| **code-reviewer** | Scores code across 5 categories (1-10), flags bugs, security holes, performance issues | `/agents/code-reviewer` |
| **security-auditor** | OWASP Top 10 audit, secrets scanning, infrastructure security checks | `/agents/security-auditor` |
| **qa-engineer** | Test coverage analysis, bug hunting, test generation, quality metrics | `/agents/qa-engineer` |
| **doc-generator** | Generates README, API docs, architecture docs, changelog entries from code | `/agents/doc-generator` |
| **changelog-manager** | Builds Keep a Changelog entries from git history, determines semver | `/agents/changelog-manager` |
| **git-workflow** | Conventional commits, branch strategy, PR creation, release workflow | `/agents/git-workflow` |

See the [How to Use](#how-to-use) section above for detailed output examples from each agent.

---

## GitHub Workflows (12)

CI/CD automation that runs automatically — no configuration required.

| Workflow | Triggers On | What It Does |
|----------|------------|--------------|
| `qa-validation.yml` | PR with `*.py` changes | Python syntax check, flake8, bandit security, CLI standards |
| `documentation-check.yml` | PR with `*.md` changes | YAML frontmatter validation, link checking, skill inventory |
| `changelog-enforcer.yml` | PR to main/dev | Ensures CHANGELOG.md is updated when code changes |
| `skill-validation.yml` | PR touching skills | Package structure validation, tier classification report |
| `release-drafter.yml` | Push to main | Auto-generates release notes with full repo stats |
| `skill-auto-update.yml` | Daily + manual | Detects changed skills, generates update manifest |
| `ci-quality-gate.yml` | PR | Lint, test, build verification |
| `claude-code-review.yml` | PR | AI-powered code review |
| `smart-sync.yml` | Push | Cross-platform skill synchronization |
| `pr-issue-auto-close.yml` | Merge | Auto-close linked issues on merge |
| `claude.yml` | Various | Claude Code integration |
| `sync-codex-skills.yml` | Push | Codex compatibility sync |

See the [Using Workflows](#3-using-workflows-cicd-automation) section above for sample output from each workflow.

---

## Repository Structure

```
Claude-Skills/
├── .claude/              # Claude Code config + 6 subagents
│   └── agents/           # code-reviewer, doc-generator, qa-engineer, etc.
├── .claude-plugin/       # Plugin marketplace config
├── .codex/               # OpenAI Codex compatibility (97 skill symlinks)
├── .github/              # 12 CI/CD workflows, templates, automation
│   ├── copilot-instructions.md  # GitHub Copilot config
│   └── workflows/        # Quality gates, release drafting, auto-update
├── agents/               # 5 production agents
├── business-growth/      # 3 skills + 9 Python tools
├── c-level-advisor/      # 5 skills + 4 Python tools
├── data-analytics/       # 5 skills
├── engineering/          # 12 advanced skills + 33 Python tools
├── engineering-team/     # 24 core engineering skills + 50 Python tools
├── finance/              # 1 skill + 4 Python tools
├── hr-operations/        # 4 skills
├── marketing-skill/      # 10 skills + 6 Python tools
├── product-team/         # 7 skills + 6 Python tools
├── project-management/   # 9 skills + 5 Python tools
├── ra-qm-team/           # 12 skills + 10 Python tools
├── sales-success/        # 5 skills
├── scripts/              # Skill installer + utility scripts
├── standards/            # Best practices library
├── templates/            # Reusable templates
├── AGENTS.md             # Universal agent config (Codex, Aider, Jules, etc.)
├── CLAUDE.md             # Claude Code development guide
├── CHANGELOG.md          # Version history
├── CODE_OF_CONDUCT.md    # Community guidelines
├── CONTRIBUTING.md       # Contribution guidelines
├── INSTALLATION.md       # Comprehensive installation guide
├── LICENSE               # MIT License
├── README.md             # This file
├── SECURITY.md           # Security policy
├── .clinerules           # Cline config
├── .cursorrules          # Cursor config
├── .goosehints           # Goose config
└── .windsurfrules        # Windsurf config
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

1. Fork this repository
2. Create a skill following the [standard package structure](#repository-structure)
3. Include Python tools (standard library only), references, and assets
4. Add YAML frontmatter to your SKILL.md
5. Submit a pull request — CI workflows will validate your skill automatically

---

## License

**MIT + Commons Clause** — Free to use in open-source projects, personal use, education, and internal business workflows. You cannot sell this software or repackage it as a paid product. See [LICENSE](LICENSE) for full terms.

---

<p align="center">
  <strong>The universal AI skills library. 97 skills. 178 Python tools. 12 workflows. 13 domains.</strong><br>
  Works with Claude, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose & more.
</p>

<p align="center">
  <a href="https://medium.com/@borghei">borghei.me</a>
</p>
