---
name: code-reviewer
description: >
  Code review automation for TypeScript, JavaScript, Python, Go, Swift, and Kotlin. Analyzes
  PRs for complexity, risk, SOLID violations, and code smells. Use when reviewing PRs,
  analyzing code quality, or generating review checklists.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: code-quality
  updated: 2026-06-17
  tags: [code-review, pull-request, code-quality, best-practices]
---
# Code Reviewer

Automated code review tooling that analyzes pull requests for complexity and risk, scans source for code smells and SOLID violations, and consolidates findings into structured review reports with a verdict, score, and prioritized action items. Supports TypeScript, JavaScript, Python, Go, Swift, and Kotlin.

## Core Capabilities

- **PR risk analysis** — scan git diffs for hardcoded secrets, SQL injection, debug statements, lint bypasses, `any` types, and TODO/FIXME, with a 1-10 complexity score.
- **Code quality checking** — detect long functions, large files, god classes, deep nesting, too many params, high cyclomatic complexity, missing error handling, unused imports, and magic numbers against fixed thresholds.
- **SOLID & antipattern detection** — flag structural, logic, security, performance, testing, and async antipatterns with fixes.
- **Review reports** — merge PR and quality findings into a verdict (approve / request changes / block), 0-100 score, and ranked action items in text, markdown, or JSON.
- **Review order prioritization** — sort files so security-sensitive code is inspected first.
- **Commit hygiene** — validate conventional-commit format across a branch.

## When to Use

- Reviewing a PR and needing fast pre-screening before manual logic review.
- Analyzing code quality or auditing a codebase for smells and SOLID violations.
- Generating a structured review report or review checklist.
- Gating merges in CI/CD on a quality score or review verdict.

## Clarify First

Before producing the review, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **What to review** — the git diff/branch (base and head) or a source directory (sets `--base`/`--head` or the path the analyzers scan)
- [ ] **Language** — TypeScript, JavaScript, Python, Go, Swift, or Kotlin (selects the rules `code_quality_checker.py` applies via `--language`)
- [ ] **Output & gate** — report format (text/markdown/JSON) and any pass/fail score threshold (sets the artifact format and CI verdict)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `pr_analyzer.py` | Assess PR complexity and risk from a git diff | `python scripts/pr_analyzer.py . --base main --head feature-branch --json` |
| `code_quality_checker.py` | Detect code smells and SOLID violations in source | `python scripts/code_quality_checker.py ./src --language typescript --json` |
| `review_report_generator.py` | Combine PR + quality findings into a review report | `python scripts/review_report_generator.py . --format markdown --output review.md` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tool_reference.md](references/tool_reference.md)** — full per-tool usage, detection lists, threshold/verdict tables, all CLI flags, JSON output samples, supported-language extensions, troubleshooting table, and success criteria. Read when running, configuring, or debugging the scripts.
- **[references/code_review_checklist.md](references/code_review_checklist.md)** — systematic checklists for pre-review, correctness, security, performance, maintainability, testing, and language-specific checks. Read when performing a manual review pass.
- **[references/coding_standards.md](references/coding_standards.md)** — language-specific standards for TypeScript, JavaScript, Python, Go, Swift, and Kotlin (types, null safety, async, error handling, class design). Read when judging style and idiom compliance.
- **[references/common_antipatterns.md](references/common_antipatterns.md)** — antipattern catalog (structural, logic, security, performance, testing, async) with examples, detection cues, and fixes. Read when explaining or fixing a flagged smell.

## Scope & Limitations

**Covers:**
- Static pattern-based risk detection in git diffs (secrets, SQL injection, debug statements, lint bypasses)
- Structural code quality analysis: function length, class size, cyclomatic complexity, parameter count, SOLID violations
- PR metadata assessment: file categorization by risk priority, commit message validation, complexity scoring
- Consolidated review reports with verdicts, scores, and prioritized action items across text, markdown, and JSON formats

**Does NOT cover:**
- **Runtime or dynamic analysis** -- use `senior-qa` for test execution and `qa-browser-automation` for end-to-end testing
- **Security vulnerability scanning** (CVE databases, dependency audits) -- use `senior-security` or `senior-secops` for SAST/DAST and supply chain analysis
- **Performance profiling or benchmarking** -- use `senior-backend` or `senior-fullstack` for performance optimization workflows
- **Architecture-level review** (system design, service boundaries, API contract validation) -- use `senior-architect` for architectural decision records and design review

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-security` | Feed PR Analyzer critical findings into security review workflows for deeper SAST/DAST analysis | `pr_analyzer.py --json` output `risks.critical[]` → security assessment input |
| `senior-qa` | Gate test execution on review report verdict; block test suites when verdict is `block` | `review_report_generator.py --json` output `summary.verdict` → QA pipeline gate |
| `senior-architect` | Escalate high-complexity PRs (score 7+) to architecture review | `pr_analyzer.py` output `summary.complexity_score` → architecture review trigger |
| `senior-fullstack` | Combine code quality scores with fullstack quality analyzer for end-to-end project health | `code_quality_checker.py --json` output → merged with `code_quality_analyzer.py` metrics |
| `tdd-guide` | Cross-reference review findings with test coverage; flag untested code paths flagged by quality checker | Quality checker `smells[]` by file → TDD coverage gap analysis |
| `senior-devops` | Integrate review reports into CI/CD pipelines as automated quality gates | `review_report_generator.py --json` output `summary.score` → pipeline pass/fail threshold |
