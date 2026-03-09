<p align="center">
  <img src="assets/header.svg" alt="AI Skills Library" width="100%"/>
</p>

# AI Skills Library

**The universal AI skills library for every coding assistant** — 199 expert-level skills with 210+ Python automation tools, 7 subagents, and 12 sample CI/CD workflows across 13 professional domains.

[![License: MIT + Commons Clause](https://img.shields.io/badge/License-MIT_+_Commons_Clause-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-purple.svg)](https://claude.ai/code)
[![Cursor](https://img.shields.io/badge/Cursor-00D1FF.svg)](https://cursor.com)
[![GitHub Copilot](https://img.shields.io/badge/Copilot-000000.svg)](https://github.com/features/copilot)
[![OpenAI Codex](https://img.shields.io/badge/Codex-412991.svg)](https://openai.com/codex)
[![Windsurf](https://img.shields.io/badge/Windsurf-0EA5E9.svg)](https://codeium.com/windsurf)
[![Cline](https://img.shields.io/badge/Cline-EC4899.svg)](https://github.com/cline/cline)
[![Aider](https://img.shields.io/badge/Aider-14B8A6.svg)](https://aider.chat)
[![117 Skills](https://img.shields.io/badge/Skills-199-brightgreen.svg)](#skills-library-117-skills)
[![215+ Tools](https://img.shields.io/badge/Python_Tools-210+-blue.svg)](#python-automation-tools-215)

## What You Get

| | |
|---|---|
| **199 Skills** | Production-ready expertise across engineering, marketing, product, finance, HR, sales, compliance, and more |
| **210+ Python Tools** | CLI scripts for code quality, SEO, DCF valuation, RICE prioritization, compliance auditing, and beyond — all standard library, no ML dependencies |
| **13 Domains** | Engineering, Marketing, Product, Project Management, C-Level Advisory, RA/QM Compliance, Business Growth, Finance, Data Analytics, HR, Sales, Advanced Engineering, Standards |
| **7 Subagents** | Autonomous Claude Code agents for code review, security audit, QA, docs, changelog, git workflows, and **compliance auditing** |
| **12 Sample Workflows** | Ready-to-use GitHub Actions for quality gates, release drafting, skill validation, auto-updates — copy to your `.github/workflows/` |
| **10 Platforms** | Claude Code, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose, Jules, RooCode |

### What's New

**March 9, 2026, 11:30 PM — Skills Mega-Expansion (109 → 199 skills)**
- **82 NEW skills** across all domains — C-Level (21 new), Marketing (25 new), Business Growth (13 new), Engineering (22 new), Product (1 new)
- Every skill from competing repos now included PLUS unique skills only we have
- All shared skills upgraded with deeper content, better frameworks, and cross-references
- **199 total skills** — the largest open-source AI skills library available

**March 9, 2026, 8:00 PM — Compliance Mega-Upgrade**
- **8 NEW compliance skills** — SOC 2 Type II, EU AI Act, NIS2, DORA, NIST CSF 2.0, PCI-DSS v4.0, CCPA/CPRA, ISO 42001
- **Infrastructure Compliance Auditor** — Vanta-level infrastructure security checks across cloud, DNS, TLS, endpoints, access controls, containers, CI/CD, secrets, and logging — mapped to ALL compliance frameworks
- **Compliance Auditor Agent** — Multi-framework audit agent covering 18 compliance standards with automated gap analysis, remediation roadmaps, and compliance scorecards
- **Enhanced existing RA/QM skills** — Updated GDPR, ISO 27001, FDA, MDR, ISO 13485, and risk management skills with cross-framework mapping, AI governance integration, and infrastructure security references
- **Hardware security key support** — YubiKey/FIDO2 deployment guides and phishing-resistant MFA requirements across all frameworks
- **Total compliance coverage:** 20 skills, 35+ Python tools, 18 frameworks, 1 compliance agent

**March 2026**
- **PM Skills Expansion** — 22 project management skills with discovery and execution frameworks, 10 Python CLI tools, and Atlassian MCP integration

---

## Table of Contents

- [What You Get](#what-you-get)
- [Supported Platforms](#supported-platforms)
- [How to Install](#how-to-install)
- [How to Use](#how-to-use)
  - [Using Skills](#1-using-skills-domain-expertise)
  - [Using Subagents](#2-using-subagents-autonomous-workflows)
  - [Using Workflows](#3-using-workflows-cicd-automation)
- [Skills Library (199 Skills)](#skills-library-117-skills)
- [Claude Code Subagents](#claude-code-subagents)
- [Sample GitHub Workflows (12)](#sample-github-workflows-12)
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

The 12 sample GitHub workflows are located in `templates/workflows/`. Copy the ones you need into your project's `.github/workflows/` directory:

```bash
# Copy all workflows
mkdir -p .github/workflows
cp templates/workflows/*.yml .github/workflows/

# Or copy individual workflows
cp templates/workflows/ci-quality-gate.yml .github/workflows/
```

Once installed, they run automatically on PRs and pushes based on file changes.

**Code Quality Gate** — Triggers on every PR with Python changes:
```
✓ Python Syntax Check     — 180/180 scripts compiled successfully
✓ Flake8 Lint             — 0 errors (E9, F63, F7, F82)
✓ Bandit Security Scan    — 0 high-severity issues
✓ CLI Standards           — 180/180 scripts have argparse + --help
```

**Documentation Check** — Triggers on PRs with markdown changes:
```
✓ YAML Frontmatter        — 109/109 SKILL.md files have valid frontmatter
✓ Required Fields          — All files have name + description
✓ Internal Links           — 0 broken links detected
✓ Skill Count              — 109 skills across 13 domains
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
- **109** skills across **13** domains
- **180** Python automation tools
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

## Skills Library (199 Skills)

### Engineering Team (24)
Core software engineering expertise with Python automation tools, references, and templates.

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

### Advanced Engineering (33)
Enterprise-grade skills with sophisticated analysis tooling — including MCP server building, Playwright testing, CI/CD pipelines, SaaS scaffolding, and more.

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
| [agent-protocol](engineering/agent-protocol/SKILL.md) | AI agent communication protocols, MCP, A2A, tool schemas | - |
| [agent-workflow-designer](engineering/agent-workflow-designer/SKILL.md) | Multi-agent orchestration, workflow DAGs, agent routing | - |
| [api-test-suite-builder](engineering/api-test-suite-builder/SKILL.md) | API testing frameworks, contract testing, load testing | - |
| [ci-cd-pipeline-builder](engineering/ci-cd-pipeline-builder/SKILL.md) | CI/CD design, GitHub Actions, GitLab CI, deployment strategies | - |
| [codebase-onboarding](engineering/codebase-onboarding/SKILL.md) | New developer onboarding, codebase docs, architecture guides | - |
| [database-schema-designer](engineering/database-schema-designer/SKILL.md) | Schema design, normalization, migration planning, ERD | - |
| [env-secrets-manager](engineering/env-secrets-manager/SKILL.md) | Secrets management, .env security, Vault, rotation policies | - |
| [git-worktree-manager](engineering/git-worktree-manager/SKILL.md) | Git worktree workflows, parallel development, branches | - |
| [mcp-server-builder](engineering/mcp-server-builder/SKILL.md) | MCP server development, tool definition, transport protocols | - |
| [monorepo-navigator](engineering/monorepo-navigator/SKILL.md) | Monorepo tooling, workspace management, build caching | - |
| [performance-profiler](engineering/performance-profiler/SKILL.md) | Performance analysis, flame graphs, memory profiling | - |
| [playwright-pro](engineering/playwright-pro/SKILL.md) | E2E testing with Playwright, page objects, CI integration | - |
| [changelog-generator](engineering/changelog-generator/SKILL.md) | Automated changelogs, conventional commits, release notes | - |
| [pr-review-expert](engineering/pr-review-expert/SKILL.md) | PR review best practices, automated checks, checklists | - |
| [runbook-generator](engineering/runbook-generator/SKILL.md) | Operational runbooks, incident procedures, automation | - |
| [saas-scaffolder](engineering/saas-scaffolder/SKILL.md) | SaaS boilerplate, auth, billing, multi-tenancy | - |
| [skill-security-auditor](engineering/skill-security-auditor/SKILL.md) | Security audit for AI skills, prompt injection detection | - |
| [context-engine](engineering/context-engine/SKILL.md) | Context management for AI agents, memory systems | - |
| [self-improving-agent](engineering/self-improving-agent/SKILL.md) | Self-improving AI patterns, feedback loops, metrics | - |
| [prompt-engineer-toolkit](engineering/prompt-engineer-toolkit/SKILL.md) | Prompt engineering frameworks, evaluation, optimization | - |
| [stripe-integration-expert](engineering/stripe-integration-expert/SKILL.md) | Stripe API, payment flows, subscriptions, webhooks | - |

### C-Level Advisory (26)
Strategic decision-making for executive leadership — from board governance to M&A playbooks.

| Skill | Description | Tools |
|-------|-------------|-------|
| [ceo-advisor](c-level-advisor/ceo-advisor/SKILL.md) | Strategic planning, board governance, investor relations, M&A | 2 |
| [cto-advisor](c-level-advisor/cto-advisor/SKILL.md) | Technical strategy, architecture decisions, engineering leadership | 2 |
| [cfo-advisor](c-level-advisor/cfo-advisor/SKILL.md) | Financial planning, fundraising, unit economics, treasury | - |
| [cmo-advisor](c-level-advisor/cmo-advisor/SKILL.md) | Brand strategy, demand generation, marketing leadership | - |
| [coo-advisor](c-level-advisor/coo-advisor/SKILL.md) | Operations strategy, process optimization, scaling | - |
| [chief-of-staff](c-level-advisor/chief-of-staff/SKILL.md) | Executive operations, cross-functional alignment, strategic initiatives | - |
| [chro-advisor](c-level-advisor/chro-advisor/SKILL.md) | People strategy, org design, compensation, workforce planning | - |
| [ciso-advisor](c-level-advisor/ciso-advisor/SKILL.md) | Security strategy, risk quantification, compliance roadmap | - |
| [cpo-advisor](c-level-advisor/cpo-advisor/SKILL.md) | Product strategy, portfolio management, product-market fit | - |
| [cro-advisor](c-level-advisor/cro-advisor/SKILL.md) | Revenue strategy, sales/CS alignment, NRR optimization | - |
| [culture-architect](c-level-advisor/culture-architect/SKILL.md) | Company culture design, values, engagement, remote culture | - |
| [decision-logger](c-level-advisor/decision-logger/SKILL.md) | Decision documentation, ADRs, decision frameworks | - |
| [executive-mentor](c-level-advisor/executive-mentor/SKILL.md) | Executive coaching, leadership development, board prep | - |
| [founder-coach](c-level-advisor/founder-coach/SKILL.md) | Founder coaching, fundraising, pivots, co-founder dynamics | - |
| [org-health-diagnostic](c-level-advisor/org-health-diagnostic/SKILL.md) | Organization assessment, health scoring, alignment analysis | - |
| [board-deck-builder](c-level-advisor/board-deck-builder/SKILL.md) | Board presentation design, investor updates, narrative structure | - |
| [board-meeting](c-level-advisor/board-meeting/SKILL.md) | Board meeting facilitation, agenda, minutes, governance | - |
| [change-management](c-level-advisor/change-management/SKILL.md) | Organizational change, ADKAR, Kotter's 8 steps, transformation | - |
| [company-os](c-level-advisor/company-os/SKILL.md) | Operating system for companies, cadences, OKRs, rituals | - |
| [competitive-intel](c-level-advisor/competitive-intel/SKILL.md) | Competitive analysis, battlecards, market intelligence | - |
| [intl-expansion](c-level-advisor/intl-expansion/SKILL.md) | International expansion, market entry, localization | - |
| [ma-playbook](c-level-advisor/ma-playbook/SKILL.md) | M&A strategy, due diligence, integration playbook | - |
| [strategic-alignment](c-level-advisor/strategic-alignment/SKILL.md) | Strategy alignment, OKR cascade, cross-functional sync | - |
| [internal-narrative](c-level-advisor/internal-narrative/SKILL.md) | Internal communications, all-hands, company narratives | - |
| [scenario-war-room](c-level-advisor/scenario-war-room/SKILL.md) | Scenario planning, war gaming, crisis simulation | - |
| [cs-onboard](c-level-advisor/cs-onboard/SKILL.md) | C-suite onboarding, first 90 days, stakeholder mapping | - |

### Marketing (35)
Data-driven marketing with Python automation tools — from content strategy to paid ads, SEO to CRO.

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
| [ad-creative](marketing-skill/ad-creative/SKILL.md) | Ad creative design, A/B testing, platform-specific formats | - |
| [ai-seo](marketing-skill/ai-seo/SKILL.md) | AI-powered SEO, SGE optimization, semantic search | - |
| [brand-guidelines](marketing-skill/brand-guidelines/SKILL.md) | Brand identity systems, style guides, voice & tone | - |
| [cold-email](marketing-skill/cold-email/SKILL.md) | Cold outreach, personalization, sequences, deliverability | - |
| [content-humanizer](marketing-skill/content-humanizer/SKILL.md) | Natural writing patterns, AI detection avoidance, authenticity | - |
| [content-production](marketing-skill/content-production/SKILL.md) | Content ops, editorial calendar, workflow management | - |
| [content-strategy](marketing-skill/content-strategy/SKILL.md) | Content pillars, audience research, funnel mapping | - |
| [copywriting](marketing-skill/copywriting/SKILL.md) | Persuasive writing, PAS, AIDA, BAB frameworks | - |
| [copy-editing](marketing-skill/copy-editing/SKILL.md) | Style consistency, grammar, editorial standards | - |
| [landing-page-generator](marketing-skill/landing-page-generator/SKILL.md) | Landing page design, conversion optimization, CTA strategy | - |
| [marketing-context](marketing-skill/marketing-context/SKILL.md) | Market research, customer insights, positioning context | - |
| [marketing-ideas](marketing-skill/marketing-ideas/SKILL.md) | Campaign ideation, creative brainstorming, trend analysis | - |
| [marketing-ops](marketing-skill/marketing-ops/SKILL.md) | Marketing automation, MarTech stack, data management | - |
| [marketing-psychology](marketing-skill/marketing-psychology/SKILL.md) | Behavioral psychology, cognitive biases, persuasion | - |
| [paid-ads](marketing-skill/paid-ads/SKILL.md) | PPC campaigns, Google/Meta/LinkedIn Ads, budget optimization | - |
| [social-content](marketing-skill/social-content/SKILL.md) | Social media content creation, platform-specific formats | - |
| [programmatic-seo](marketing-skill/programmatic-seo/SKILL.md) | Programmatic page generation, template-based SEO at scale | - |
| [schema-markup](marketing-skill/schema-markup/SKILL.md) | Structured data, JSON-LD, rich snippets, Knowledge Graph | - |
| [seo-audit](marketing-skill/seo-audit/SKILL.md) | Technical SEO audits, Core Web Vitals, crawl analysis | - |
| [site-architecture](marketing-skill/site-architecture/SKILL.md) | Information architecture, URL structure, internal linking | - |
| [analytics-tracking](marketing-skill/analytics-tracking/SKILL.md) | GTM, event tracking, conversion tracking, GA4 | - |
| [email-sequence](marketing-skill/email-sequence/SKILL.md) | Email automation, drip campaigns, nurture flows | - |
| [email-template-builder](marketing-skill/email-template-builder/SKILL.md) | Email HTML templates, responsive design, deliverability | - |
| [social-media-manager](marketing-skill/social-media-manager/SKILL.md) | Social media management, scheduling, community management | - |
| [launch-strategy](marketing-skill/launch-strategy/SKILL.md) | Product launch playbooks, pre/post-launch analysis | - |

### Product Team (8)
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
| [ab-test-setup](product-team/ab-test-setup/SKILL.md) | A/B testing design, statistical significance, feature flags | - |

### Project Management (22)
Delivery excellence with discovery, execution frameworks, Atlassian MCP integration, and 10 Python CLI tools.

**Role-Based Skills (10)**

| Skill | Description | Tools |
|-------|-------------|-------|
| [senior-pm](project-management/senior-pm/SKILL.md) | Portfolio management, stakeholder mapping, risk analysis, WSJF | 4 |
| [scrum-master](project-management/scrum-master/SKILL.md) | Sprint analytics, velocity forecasting, capacity planning, team health | 4 |
| [delivery-manager](project-management/delivery-manager/SKILL.md) | Release management, deployment, incident response | - |
| [jira-expert](project-management/jira-expert/SKILL.md) | JQL mastery, workflows, automation, dashboards | - |
| [confluence-expert](project-management/confluence-expert/SKILL.md) | Knowledge management, space architecture | - |
| [atlassian-admin](project-management/atlassian-admin/SKILL.md) | System administration, security, integrations | - |
| [atlassian-templates](project-management/atlassian-templates/SKILL.md) | Template design, custom blueprints | - |
| [agile-coach](project-management/agile-coach/SKILL.md) | Transformation, framework implementation, coaching | - |
| [program-manager](project-management/program-manager/SKILL.md) | Multi-project coordination, portfolio governance | - |

**Discovery Skills (4)**

| Skill | Description | Tools |
|-------|-------------|-------|
| [brainstorm-ideas](project-management/discovery/brainstorm-ideas/SKILL.md) | Product Trio ideation, Opportunity Solution Trees | - |
| [brainstorm-experiments](project-management/discovery/brainstorm-experiments/SKILL.md) | Lean experiment design, XYZ hypotheses | 1 |
| [identify-assumptions](project-management/discovery/identify-assumptions/SKILL.md) | Assumption mapping across 4-8 risk categories | 1 |
| [pre-mortem](project-management/discovery/pre-mortem/SKILL.md) | Tiger/Paper Tiger/Elephant risk classification | 1 |

**Execution Skills (8)**

| Skill | Description | Tools |
|-------|-------------|-------|
| [create-prd](project-management/execution/create-prd/SKILL.md) | PRD scaffolding with 8-section structure | 1 |
| [brainstorm-okrs](project-management/execution/brainstorm-okrs/SKILL.md) | OKR brainstorming and validation (Wodtke) | 1 |
| [outcome-roadmap](project-management/execution/outcome-roadmap/SKILL.md) | Output→outcome roadmap transformation | 1 |
| [prioritization-frameworks](project-management/execution/prioritization-frameworks/SKILL.md) | Multi-framework scoring (RICE, ICE, MoSCoW) | 1 |
| [release-notes](project-management/execution/release-notes/SKILL.md) | Release notes from tickets/changelogs | 1 |
| [summarize-meeting](project-management/execution/summarize-meeting/SKILL.md) | Structured meeting summaries with action items | - |
| [job-stories](project-management/execution/job-stories/SKILL.md) | JTBD When/Want/So backlog format | - |
| [wwas](project-management/execution/wwas/SKILL.md) | Why-What-Acceptance structured backlog items | - |

### Regulatory Affairs, Quality Management & Compliance (20)
Enterprise compliance across 18 frameworks — medical devices, information security, privacy, AI governance, financial resilience, and infrastructure security.

**Medical Device & Quality (12 skills)**

| Skill | Description | Tools |
|-------|-------------|-------|
| [regulatory-affairs-head](ra-qm-team/regulatory-affairs-head/SKILL.md) | Regulatory strategy, FDA/EU pathways, market access | 1 |
| [quality-manager-qmr](ra-qm-team/quality-manager-qmr/SKILL.md) | QMS effectiveness, compliance dashboards | 1 |
| [quality-manager-qms-iso13485](ra-qm-team/quality-manager-qms-iso13485/SKILL.md) | ISO 13485 compliance, design control | 1 |
| [capa-officer](ra-qm-team/capa-officer/SKILL.md) | CAPA management, root cause analysis | 1 |
| [quality-documentation-manager](ra-qm-team/quality-documentation-manager/SKILL.md) | Document control, 21 CFR Part 11 | 1 |
| [risk-management-specialist](ra-qm-team/risk-management-specialist/SKILL.md) | Risk register, FMEA, ISO 14971 | 1 |
| [information-security-manager-iso27001](ra-qm-team/information-security-manager-iso27001/SKILL.md) | ISO 27001:2022 ISMS, 93 Annex A controls | 2 |
| [gdpr-dsgvo-expert](ra-qm-team/gdpr-dsgvo-expert/SKILL.md) | GDPR/DSGVO compliance, DPIA, German BDSG | 3 |
| [mdr-745-specialist](ra-qm-team/mdr-745-specialist/SKILL.md) | EU MDR 2017/745, GSPR, EUDAMED, UDI | 1 |
| [fda-consultant-specialist](ra-qm-team/fda-consultant-specialist/SKILL.md) | FDA 510(k)/PMA, QSR/QMSR, HIPAA, cybersecurity | 3 |
| [qms-audit-expert](ra-qm-team/qms-audit-expert/SKILL.md) | ISO 13485 audit planning, nonconformity management | 1 |
| [isms-audit-expert](ra-qm-team/isms-audit-expert/SKILL.md) | ISO 27001 ISMS audits, security control testing | 1 |

**Information Security & Cybersecurity (3 skills)** — NEW

| Skill | Description | Tools |
|-------|-------------|-------|
| [soc2-compliance-expert](ra-qm-team/soc2-compliance-expert/SKILL.md) | SOC 2 Type I/II, Trust Services Criteria, infrastructure security, evidence collection | 3 |
| [nist-csf-specialist](ra-qm-team/nist-csf-specialist/SKILL.md) | NIST CSF 2.0, 6 functions, maturity assessment, cross-framework mapping | 2 |
| [pci-dss-specialist](ra-qm-team/pci-dss-specialist/SKILL.md) | PCI-DSS v4.0, 12 requirements, CDE scoping, tokenization | 2 |

**AI Governance (2 skills)** — NEW

| Skill | Description | Tools |
|-------|-------------|-------|
| [eu-ai-act-specialist](ra-qm-team/eu-ai-act-specialist/SKILL.md) | EU AI Act risk classification, GPAI, conformity assessment, bias detection | 3 |
| [iso42001-ai-management](ra-qm-team/iso42001-ai-management/SKILL.md) | ISO 42001:2023 AIMS, AI lifecycle governance, impact assessment | 2 |

**Privacy, Financial & Cybersecurity Directives (3 skills)** — NEW

| Skill | Description | Tools |
|-------|-------------|-------|
| [ccpa-cpra-privacy-expert](ra-qm-team/ccpa-cpra-privacy-expert/SKILL.md) | CCPA/CPRA consumer privacy, data mapping, opt-out mechanisms | 2 |
| [dora-compliance-expert](ra-qm-team/dora-compliance-expert/SKILL.md) | DORA 5 pillars, ICT risk management, resilience testing, third-party oversight | 2 |
| [nis2-directive-specialist](ra-qm-team/nis2-directive-specialist/SKILL.md) | NIS2 10 minimum measures, incident reporting, supply chain security | 2 |

**Cross-Cutting Infrastructure (1 skill)** — NEW

| Skill | Description | Tools |
|-------|-------------|-------|
| [infrastructure-compliance-auditor](ra-qm-team/infrastructure-compliance-auditor/SKILL.md) | Vanta-level infrastructure audit: cloud, DNS, TLS, endpoints, access controls, containers, CI/CD, secrets, logging — mapped to ALL 18 frameworks | 3 |

### Business Growth (16)
Revenue optimization, CRO, pricing strategy, and customer success with Python tools.

| Skill | Description | Tools |
|-------|-------------|-------|
| [customer-success-manager](business-growth/customer-success-manager/SKILL.md) | Health scoring, churn prediction, expansion analysis | 3 |
| [revenue-operations](business-growth/revenue-operations/SKILL.md) | Pipeline analytics, forecast accuracy, GTM efficiency | 3 |
| [sales-engineer](business-growth/sales-engineer/SKILL.md) | RFP analysis, competitive positioning, POC planning | 3 |
| [form-cro](business-growth/form-cro/SKILL.md) | Form optimization, field reduction, multi-step forms | - |
| [onboarding-cro](business-growth/onboarding-cro/SKILL.md) | User onboarding optimization, activation, time-to-value | - |
| [page-cro](business-growth/page-cro/SKILL.md) | Landing page CRO, above-the-fold, social proof | - |
| [paywall-upgrade-cro](business-growth/paywall-upgrade-cro/SKILL.md) | Paywall optimization, upgrade triggers, pricing pages | - |
| [popup-cro](business-growth/popup-cro/SKILL.md) | Exit-intent popups, timing optimization, frequency capping | - |
| [signup-flow-cro](business-growth/signup-flow-cro/SKILL.md) | Registration optimization, SSO, progressive profiling | - |
| [churn-prevention](business-growth/churn-prevention/SKILL.md) | Churn prediction, retention strategies, win-back campaigns | - |
| [competitive-teardown](business-growth/competitive-teardown/SKILL.md) | Competitor analysis, feature comparison, positioning gaps | - |
| [competitor-alternatives](business-growth/competitor-alternatives/SKILL.md) | Alternative positioning, comparison pages, switching guides | - |
| [free-tool-strategy](business-growth/free-tool-strategy/SKILL.md) | Free tool marketing, product-led growth, conversion funnels | - |
| [pricing-strategy](business-growth/pricing-strategy/SKILL.md) | Pricing models, value-based pricing, packaging | - |
| [referral-program](business-growth/referral-program/SKILL.md) | Referral mechanics, viral loops, incentive design | - |
| [contract-and-proposal-writer](business-growth/contract-and-proposal-writer/SKILL.md) | Contract templates, proposals, SOW, MSA | - |

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

Seven specialized subagents in `.claude/agents/` and `agents/` for autonomous code review, documentation, QA, security, changelog, git workflows, and enterprise compliance auditing.

| Agent | What It Does | Invoke With |
|-------|-------------|-------------|
| **code-reviewer** | Scores code across 5 categories (1-10), flags bugs, security holes, performance issues | `/agents/code-reviewer` |
| **security-auditor** | OWASP Top 10 audit, secrets scanning, infrastructure security checks | `/agents/security-auditor` |
| **qa-engineer** | Test coverage analysis, bug hunting, test generation, quality metrics | `/agents/qa-engineer` |
| **doc-generator** | Generates README, API docs, architecture docs, changelog entries from code | `/agents/doc-generator` |
| **changelog-manager** | Builds Keep a Changelog entries from git history, determines semver | `/agents/changelog-manager` |
| **git-workflow** | Conventional commits, branch strategy, PR creation, release workflow | `/agents/git-workflow` |
| **cs-compliance-auditor** | Multi-framework compliance audit across 18 standards (SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS, EU AI Act, NIS2, DORA, NIST CSF 2.0, CCPA, and more). Audits infrastructure, code, policies, and access controls with Vanta-level depth | `agents/compliance/` |

See the [How to Use](#how-to-use) section above for detailed output examples from each agent.

---

## Sample GitHub Workflows (12)

Ready-to-use GitHub Actions templates in [`templates/workflows/`](templates/workflows/). Copy to your `.github/workflows/` to activate.

```bash
mkdir -p .github/workflows
cp templates/workflows/*.yml .github/workflows/
```

| Workflow | Triggers On | What It Does |
|----------|------------|--------------|
| `ci-quality-gate.yml` | PR | YAML lint, Python syntax, security audit |
| `qa-validation.yml` | PR with `*.py` changes | Flake8, bandit security, CLI standards |
| `skill-validation.yml` | PR touching skills | Package structure validation, tier classification |
| `documentation-check.yml` | PR with `*.md` changes | YAML frontmatter validation, link checking, skill inventory |
| `changelog-enforcer.yml` | PR to main/dev | Ensures CHANGELOG.md is updated when code changes |
| `release-drafter.yml` | Push to main | Auto-generates release notes with full repo stats |
| `skill-auto-update.yml` | Daily + manual | Detects changed skills, generates update manifest |
| `claude-code-review.yml` | PR | AI-powered code review |
| `claude.yml` | @claude mentions | Interactive Claude Code in issues/PRs |
| `pr-issue-auto-close.yml` | PR merged | Auto-close linked issues on merge |
| `smart-sync.yml` | Issue label/state changes | Bidirectional issue/project board sync |
| `sync-codex-skills.yml` | SKILL.md changes | Codex compatibility sync |

See [`templates/workflows/README.md`](templates/workflows/README.md) for setup instructions, required secrets, and customization guide.

---

## Repository Structure

```
Claude-Skills/
├── .claude/              # Claude Code config + 6 subagents
│   └── agents/           # code-reviewer, doc-generator, qa-engineer, etc.
├── .claude-plugin/       # Plugin marketplace config
├── .codex/               # OpenAI Codex compatibility (109 skill symlinks)
├── .github/              # GitHub config (Copilot, issue templates, PR template)
│   └── copilot-instructions.md  # GitHub Copilot config
├── agents/               # 6 production agents (incl. compliance auditor)
├── business-growth/      # 16 skills + 9 Python tools
├── c-level-advisor/      # 26 skills + 4 Python tools
├── data-analytics/       # 5 skills
├── engineering/          # 33 advanced skills + 33 Python tools
├── engineering-team/     # 24 core engineering skills + 50 Python tools
├── finance/              # 1 skill + 4 Python tools
├── hr-operations/        # 4 skills
├── marketing-skill/      # 35 skills + 6 Python tools
├── product-team/         # 8 skills + 6 Python tools
├── project-management/   # 22 skills + 10 Python tools
├── ra-qm-team/           # 20 skills + 35 Python tools (enterprise compliance)
├── sales-success/        # 5 skills
├── scripts/              # Skill installer + utility scripts
├── standards/            # Best practices library
├── templates/            # Reusable templates + 12 sample GitHub workflows
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
5. Submit a pull request

---

## License

**MIT + Commons Clause** — Free to use in open-source projects, personal use, education, and internal business workflows. You cannot sell this software or repackage it as a paid product. See [LICENSE](LICENSE) for full terms.

---

<p align="center">
  <strong>The universal AI skills library. 199 skills. 210+ Python tools. 12 sample workflows. 13 domains.</strong><br>
  Works with Claude, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose & more.
</p>

<p align="center">
  <a href="https://borghei.me">borghei.me</a>
</p>
