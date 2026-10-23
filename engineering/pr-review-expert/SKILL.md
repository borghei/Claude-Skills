---
name: pr-review-expert
description: >
  Systematic PR review with blast-radius analysis, security scanning, and breaking-change and
  test-coverage deltas. Use when reviewing PRs that touch shared libraries, APIs, database
  schemas, auth, or security-sensitive code.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: code-review
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: github, gitlab, review-checklist
  tags:
    - code-review
    - pull-requests
    - blast-radius
    - breaking-changes
    - test-coverage
---
# PR Review Expert

Structured, systematic code review for GitHub PRs and GitLab MRs. Goes beyond style nits to perform blast-radius analysis, security vulnerability scanning, breaking-change detection, test-coverage delta calculation, and performance impact assessment. Produces reviewer-ready reports with prioritized findings categorized as must-fix, should-fix, and suggestions.

**Keywords:** PR review, code review, pull request, merge request, blast radius, security scan, breaking changes, test coverage, review checklist, code quality

## Core Capabilities

- **Blast radius analysis** — trace which files, services, and downstream consumers a diff could break; quantify severity CRITICAL/HIGH/MEDIUM/LOW.
- **Security scanning** — detect SQL injection, XSS vectors, hardcoded secrets, auth bypass, insecure crypto, path traversal, and prototype pollution in the diff.
- **Breaking-change detection** — flag API removals/renames, response-schema and required-field changes, DB column removals, env-var changes, and TS interface edits.
- **Test coverage analysis** — new-code vs new-test ratio, missing tests for new public functions, deleted tests without deleted code, coverage delta.
- **Performance assessment** — N+1 query patterns, bundle-size regressions, unbounded queries, missing indexes.
- **Reviewer-ready output** — prioritized must-fix / should-fix / suggestion report, a 35-item checklist, and consistent comment labels.

## When to Use

- Before merging any PR that touches shared libraries, APIs, or database schemas.
- When a PR is large (>200 lines changed) and needs structured review.
- For PRs in security-sensitive code paths (auth, payments, PII handling).
- After an incident, to proactively review similar code changes.
- For onboarding new contributors whose PRs need thorough feedback.

## Clarify First

Before reviewing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Which PR and base branch:** blast radius and coverage deltas are computed against the base; a stale base reports changes that aren't in the PR.
- **What the change is for:** (linked ticket or one-line intent) — without it, intended behaviour changes get flagged as bugs.
- **Review depth:** a full blast-radius and security pass, or a quick check of a small change — sets which workflow steps run.

Ask about the two or three inputs that matter most for this request. If the user says "just review it," proceed and state your assumptions at the top of the report.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `blast_radius_calculator.py` | Calculate PR blast radius from import chains / dependency trees of changed files | `git diff --name-only main...HEAD \| python scripts/blast_radius_calculator.py --root src` |
| `diff_analyzer.py` | Analyze a diff for risk indicators (large files, sensitive paths, config/breaking/security patterns) | `gh pr diff $PR \| python scripts/diff_analyzer.py --json` |
| `review_checklist_generator.py` | Generate a tailored review checklist from changed file types/patterns | `git diff --name-only main...HEAD \| python scripts/review_checklist_generator.py` |

## Anti-Patterns

### Reviewing style instead of substance
**Mistake:** Most comments are about naming and formatting.
**Why it happens:** Style problems are visible on a first read; logic and security problems need context.
**Instead:** Leave formatting to the linter. Spend the review on blast radius, security, correctness and error paths, and label every comment `must:`, `nit:` or `question:`.

### Judging risk by diff size
**Mistake:** A five-line change to a shared utility is approved because it is five lines.
**Why it happens:** The diff size is the only risk measure on the screen.
**Instead:** Run `blast_radius_calculator.py` on the changed files. A small change in a shared module can break every service that imports it.

### Approving an untested happy path
**Mistake:** The PR only tests the success case.
**Why it happens:** The tests pass and the coverage number looks fine.
**Instead:** Check that error paths and edge cases have tests, and flag any new public function that has none.

More pitfalls and the troubleshooting table: `references/best-practices-and-troubleshooting.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/review-workflow-commands.md](references/review-workflow-commands.md)** — the 6-step review workflow with the exact `gh`/`grep` command catalog for context gathering, blast radius, security scan, breaking-change detection, coverage delta, and performance impact (plus the blast-radius severity table and coverage rules). Read when actually performing a review.
- **[references/writeup-format-and-checklist.md](references/writeup-format-and-checklist.md)** — the review report template with worked examples, the complete 35-item review checklist, and the comment-label taxonomy. Read when writing up findings.
- **[references/best-practices-and-troubleshooting.md](references/best-practices-and-troubleshooting.md)** — common reviewer pitfalls, best-practice habits, the troubleshooting table, and the success-criteria bar. Read before and after a review for quality control.

## Scope & Limitations

**This skill covers:**
- Structured review of GitHub PRs and GitLab MRs using a 35+ item checklist
- Blast radius analysis for monorepo and multi-service architectures
- Static security scanning of diffs for common vulnerability patterns (SQLi, XSS, secrets, auth bypass)
- Breaking change detection for APIs, database schemas, TypeScript interfaces, and environment variables

**This skill does NOT cover:**
- Automated code fixes or refactoring — use `engineering/saas-scaffolder` or `engineering/migration-architect` for code generation
- Runtime security analysis, SAST/DAST tool orchestration, or CVE database lookups — use `engineering/dependency-auditor` for dependency-level vulnerability scanning
- CI/CD pipeline configuration or build failure triage — use `engineering/ci-cd-pipeline-builder` for pipeline design
- Performance benchmarking or load testing — use `engineering/performance-profiler` for profiling and optimization guidance

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/dependency-auditor` | Run dependency audit before reviewing PRs that add or upgrade packages | Audit report feeds into the Security section of the review report |
| `engineering/ci-cd-pipeline-builder` | Embed review checklist gates into CI pipelines as automated PR checks | Checklist items become pass/fail signals in the pipeline |
| `engineering/performance-profiler` | Escalate N+1 and unbounded query findings for detailed profiling | Flagged code paths from review become profiling targets |
| `engineering/migration-architect` | Validate database migration safety for PRs that include schema changes | Migration risk assessment supplements the Breaking Changes section |
| `engineering/release-manager` | Feed breaking change detection results into release notes and changelogs | Detected breaking changes auto-populate release documentation |
| `engineering/api-design-reviewer` | Cross-reference API endpoint changes with API design standards | API review findings merge into the Blast Radius and Breaking Changes sections |
