---
name: code-reviewer
description: >
  Heuristic code-review pre-pass for TS, JS, Python, Go, Swift and Kotlin: PR risk, smells, SOLID
  issues, and a two-axis (standards vs spec) review method. Use when reviewing a PR or preparing a
  review checklist.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: code-quality
  updated: 2026-11-08
  tags: [code-review, pull-request, code-quality, best-practices, spec-fidelity]
---
# Code Reviewer

Automated code review tooling that analyzes pull requests for complexity and risk, scans source for code smells and SOLID violations, and consolidates findings into structured review reports with a verdict, score, and prioritized action items. Supports TypeScript, JavaScript, Python, Go, Swift, and Kotlin.

## Core Capabilities

- **PR risk analysis** — scan git diffs for hardcoded secrets, SQL injection, debug statements, lint bypasses, `any` types, and TODO/FIXME, with a 1-10 complexity score.
- **Code quality checking** — detect long functions, large files, god classes, deep nesting, too many params, high cyclomatic complexity, missing error handling, unused imports, and magic numbers against fixed thresholds.
- **SOLID & antipattern detection** — flag structural, logic, security, performance, testing, and async antipatterns with fixes.
- **Review reports** — merge PR and quality findings into a verdict (approve / request changes / block), 0-100 score, and ranked action items in text, markdown, or JSON. An empty diff gives `nothing_to_review` and a failed diff analysis `incomplete`, never an approval. The scripts are regex heuristics: they point a human or model reviewer at likely problems; they do not replace reading the diff.
- **Review order prioritization** — sort files so security-sensitive code is inspected first.
- **Commit hygiene** — validate conventional-commit format across a branch.
- **Two-axis review** — review the diff since a fixed base twice, independently: once against repo standards, once against the original spec or issue (missed requirements, scope creep), then merge.

## When to Use

- Reviewing a PR and needing fast pre-screening before manual logic review.
- Analyzing code quality or auditing a codebase for smells and SOLID violations.
- Generating a structured review report or review checklist.
- Gating merges in CI/CD on a quality score or review verdict.
- Checking that a branch built what its ticket or spec asked for, especially agent-written changes.

## Clarify First

Before producing the review, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **What to review:** the git diff/branch (base and head) or a source directory (sets `--base`/`--head` or the path the analyzers scan).
- **Language:** TypeScript, JavaScript, Python, Go, Swift, or Kotlin (selects the rules `code_quality_checker.py` applies via `--language`).
- **Output & gate:** report format (text/markdown/JSON) and any pass/fail score threshold (sets the artifact format and CI verdict).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

For a two-axis review, two more inputs matter: the **fixed base** (branch, tag, SHA or `HEAD~N`; without it the scope drifts) and the **spec source** (issue, ticket or spec file; without it Axis B is skipped and the report says so).

## Quick Start

```bash
# Pin the scope and print both reviewer briefs (exit 2 bad ref, 1 empty diff)
python scripts/review_scope.py --repo . --base main

# Automated pre-screen of the same diff
python scripts/pr_analyzer.py . --base main --head HEAD --json
```

## Two-Axis Review Workflow [RECOMMENDED]

Use this for any change that implements a ticket or spec. It separates "is it written the way this repo writes code?" from "does it do what was asked?", because one reviewer answering both tends to answer one of them badly. Full method: [references/two-axis-review.md](references/two-axis-review.md).

1. **Pin the base.** Run `review_scope.py --base <ref>`. It resolves the ref, takes the diff against the merge-base (`git diff <base>...HEAD`), and fails before any review starts on a bad ref or empty diff. Record the base SHA in the report.
2. **Find the spec.** Use the path the author gave, else issue references in commit messages, else a spec file matching the branch name, else ask. No spec means Axis B is skipped and reported as skipped.
3. **Find the standards.** Collect the repo's documented rules (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, steering files, linter config). Skip anything a linter already enforces. If the repo documents nothing, fall back to `references/coding_standards.md` and label those findings as judgement calls.
4. **Run Axis A (standards) with fresh context.** The agent hands a separate reviewer or sub-agent only the standards brief from `review_scope.py`: diff command, commits, standards files. It reports location, rule broken, hard or judgement.
5. **Run Axis B (spec fidelity) with fresh context.** A second independent reviewer gets only the spec brief: diff command, commits, spec text. It reports missing or partial requirements, behaviour nobody asked for, and requirements built wrongly, quoting the spec line for each.
6. **Merge without re-ranking across axes.** Present Standards and Spec under separate headings with a one-line summary each, list overlaps once, then give the verdict. A missing or wrongly built requirement is at least request-changes however clean Axis A is; judgement calls alone never block. Layout: `assets/two-axis-review-template.md`.

Run the passes in parallel when sub-agents are available. A lone human reviewer runs them in sequence and starts the spec pass from the spec, not from the diff.

## Tools Overview

| Tool | Purpose | Command |
|------|---------|---------|
| `pr_analyzer.py` | Assess PR complexity and risk from a git diff | `python scripts/pr_analyzer.py . --base main --head feature-branch --json` |
| `code_quality_checker.py` | Detect code smells and SOLID violations in source | `python scripts/code_quality_checker.py ./src --language typescript --json` |
| `review_report_generator.py` | Combine PR + quality findings into a review report | `python scripts/review_report_generator.py . --format markdown --output review.md` |
| `review_scope.py` | Pin the base, list commits and files, extract issue refs, find spec and standards sources, print both two-axis briefs | `python scripts/review_scope.py --repo . --base main --format json` |

## Anti-Patterns

### The Blended Review
**Mistake:** One reviewer reads the diff top to bottom and mixes style notes with requirement gaps in a single list.
**Why it happens:** It is the habitual way to read a PR, and it feels efficient.
**Instead:** Run the two axes as separate passes with fresh context. Style findings crowd out the one missing requirement that actually matters.

### The Floating Base
**Mistake:** Reviewing "the branch" without pinning a base, so the diff changes as `main` moves or the author rebases.
**Why it happens:** The PR view hides the base; it seems obvious.
**Instead:** Name the base, record its SHA, and use the three-dot diff against the merge-base.

### Reviewing What the Linter Checks
**Mistake:** Spending the human pass on formatting and import order.
**Why it happens:** Those issues are easy to see and easy to write up.
**Instead:** Read the linter config first and skip every rule it enforces. Spend the pass on judgement the tools cannot make.

### Spec Invented From the Code
**Mistake:** With no spec available, the reviewer infers what the change "must have been meant to do" and reviews against that.
**Why it happens:** Skipping a whole axis feels like an incomplete review.
**Instead:** Report "no spec found" and ask the author where the requirement lives. A review against an invented spec only confirms the code agrees with itself.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tool_reference.md](references/tool_reference.md)** — full per-tool usage, detection lists, threshold/verdict tables, all CLI flags, JSON output samples, supported-language extensions, troubleshooting table, and success criteria. Read when running, configuring, or debugging the scripts.
- **[references/code_review_checklist.md](references/code_review_checklist.md)** — systematic checklists for pre-review, correctness, security, performance, maintainability, testing, and language-specific checks. Read when performing a manual review pass.
- **[references/coding_standards.md](references/coding_standards.md)** — language-specific standards for TypeScript, JavaScript, Python, Go, Swift, and Kotlin (types, null safety, async, error handling, class design). Read when judging style and idiom compliance.
- **[references/two-axis-review.md](references/two-axis-review.md)** — the two-axis method: pinning the base, finding spec and standards sources, writing each pass's brief, scope-creep buckets, merging and verdict rules. Read when reviewing a change against its ticket or spec.
- **[assets/two-axis-review-template.md](assets/two-axis-review-template.md)** — report layout with Standards and Spec sections, overlaps and verdict.
- **[references/common_antipatterns.md](references/common_antipatterns.md)** — antipattern catalog (structural, logic, security, performance, testing, async) with examples, detection cues, and fixes. Read when explaining or fixing a flagged smell.

## Scope & Limitations

**Covers:**
- Static pattern-based risk detection in git diffs (secrets, SQL injection, debug statements, lint bypasses)
- Structural code quality analysis: function length, class size, cyclomatic complexity, parameter count, SOLID violations
- PR metadata assessment: file categorization by risk priority, commit message validation, complexity scoring
- Consolidated review reports with verdicts, scores, and prioritized action items across text, markdown, and JSON formats
- Two-axis review of a diff since a fixed base: repo-standards conformance and fidelity to the originating spec or issue, with `review_scope.py` pinning the scope and writing both briefs

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
