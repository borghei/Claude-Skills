---
name: senior-qa
description: >
  Testing for React/Next.js with Jest, React Testing Library, and Playwright. Use when
  generating tests, writing unit tests, analyzing coverage, scaffolding E2E tests, configuring
  Jest, or improving test quality.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: quality-assurance
  updated: 2026-11-08
  tags: [test-strategy, automation, performance-testing, test-frameworks]
---
# Senior QA Engineer

Test automation, coverage analysis, and quality assurance patterns for React and Next.js applications. Generates Jest + React Testing Library unit test stubs, analyzes Istanbul/LCOV coverage for gaps, and scaffolds Playwright E2E suites for App Router and Pages Router projects.

## Core Capabilities

- **Unit test generation** — scan React/TypeScript components and emit Jest + RTL stubs (render, interaction, state, optional `jest-axe` a11y).
- **Coverage analysis** — parse Istanbul/LCOV reports, identify gaps by severity, flag critical business-logic paths, and emit text/HTML/JSON recommendations.
- **E2E scaffolding** — detect Next.js routes (dynamic segments, route groups, auth pages) and generate Playwright specs, Page Object Models, fixtures, and config.
- **Test strategy** — the testing pyramid, coverage targets by code type, and test organization patterns.
- **Automation patterns** — Page Object Model, data factories, MSW mocking, fixtures, and custom render utilities.
- **Quality practices** — testable code design, AAA structure, test isolation, flaky-test elimination, and quality metrics.

## When to Use

- Setting up unit tests for new or existing React components.
- Improving test coverage or preparing for release.
- Setting up Playwright E2E tests for a Next.js project.
- Configuring Jest thresholds or improving overall test quality.

## Clarify First

Before generating tests, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Test layer:** unit (Jest+RTL) vs E2E (Playwright) (selects `test_suite_generator` vs `e2e_test_scaffolder`).
- **Source path:** the components or Next.js routes to generate tests from (the scaffolder's input).
- **Coverage focus:** happy path only vs interaction/state/a11y (`jest-axe`) (sets which test stubs are emitted).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

| Tool | Purpose | Example (runs as written) |
|------|---------|---------|
| `test_suite_generator.py` | Jest + RTL stubs from React components; reads the `XProps` interface to build typed `mockProps` for required props (`--output`, `--include-a11y`, `--scan-only`, `--json`) | `python scripts/test_suite_generator.py assets/sample_components --output /tmp/qa/tests` |
| `coverage_analyzer.py` | Istanbul JSON / LCOV gap analysis with critical-path weighting (`--threshold`, `--strict`, `--critical-paths`, `--format text/html/json`, `--json`) | `python scripts/coverage_analyzer.py assets/sample_lcov.info --threshold 80 --strict` |
| `e2e_test_scaffolder.py` | Playwright specs, page objects, fixtures and `playwright.config.ts` from Next.js routes, all written under `--output` | `python scripts/e2e_test_scaffolder.py assets/sample_app/app --output /tmp/qa/e2e` |

Exit codes: `0` ok; `1` coverage below `--threshold` when `--strict` is set (without
`--strict` the analyzer always reports and exits 0, so use `--strict` in CI); `2` bad input
(path not found, unparseable report). With `--json` the report goes to stderr and stdout is
pure JSON.

Generated stubs are a starting point: they render with valid required props and leave
`TODO` assertions, so they compile but assert nothing until you write the checks. The
sample LCOV has a payment file at 37.5% line coverage, so `--strict --threshold 80` exits 1.

## Workflow

1. Generate stubs or scaffold E2E specs into the project's test folder (always pass `--output`).
2. Replace every `TODO` with an assertion on behaviour the user can see (role, text, called handler); delete stubs that test nothing useful.
3. Run the project's tests with coverage, then `coverage_analyzer.py <report> --threshold <n> --strict`.
4. Done when the suite passes, the analyzer exits 0, and no generated test is still assertion-free.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/qa-workflows-and-tools.md](references/qa-workflows-and-tools.md)** — quick start, the three tool overviews with sample output, the unit-test/coverage/E2E workflows, common pattern snippets (RTL queries, async, MSW, Playwright locators, jest thresholds), common commands, troubleshooting table, and success criteria. Read when running a workflow.
- **[references/tool-cli-reference.md](references/tool-cli-reference.md)** — full flag tables, examples, output formats, and generated artifacts for all three scripts. Read before running the scripts.
- **[references/testing_strategies.md](references/testing_strategies.md)** — the testing pyramid, testing types, coverage targets and thresholds, and test organization patterns. Read when designing test strategy.
- **[references/test_automation_patterns.md](references/test_automation_patterns.md)** — Page Object Model, data factories, fixture management, mocking strategies (MSW), and custom test utilities. Read when writing test code.
- **[references/qa_best_practices.md](references/qa_best_practices.md)** — writing testable code, naming conventions, AAA pattern, test isolation, flaky-test debugging, and quality metrics. Read when improving test quality.

## Scope & Limitations

**This skill covers:**
- Unit test stub generation for React/TypeScript functional and class components using Jest and React Testing Library.
- Coverage analysis and gap identification from Istanbul JSON and LCOV report formats.
- E2E test scaffolding for Next.js App Router and Pages Router projects using Playwright.
- Accessibility test generation via `jest-axe` integration.

**This skill does NOT cover:**
- Backend API testing (see `senior-backend` for Express/Node.js testing patterns).
- Performance or load testing (see `senior-devops` for infrastructure and performance tooling).
- Visual regression testing or screenshot comparison workflows.
- Mobile-native testing (React Native, Flutter) -- this skill targets web browser-based testing only.

## Anti-Patterns

### Shipping Generated Stubs as Tests
**Mistake:** Committing the generated files with their `TODO` assertions still in place.
**Why it happens:** They run green and raise the coverage number.
**Instead:** A render with no assertion only proves the component does not throw. Write the assertion or delete the case.

### Querying by Test ID First
**Mistake:** Reaching for `getByTestId` for every element.
**Why it happens:** It is the most stable selector to write.
**Instead:** Prefer `getByRole` and `getByLabelText`: they test what users and assistive tech see, and fail when accessibility regresses. Keep test IDs for elements with no accessible name.

### Gating on Overall Coverage Only
**Mistake:** Passing CI because the project average clears 80%.
**Why it happens:** One number is easy to configure.
**Instead:** Use `--critical-paths` and read the per-file gaps: a 37% payment module hidden behind a 90% average is the bug that ships.

## Files

| File | Purpose |
|------|---------|
| `scripts/test_suite_generator.py` | Jest + RTL stub generator |
| `scripts/coverage_analyzer.py` | Coverage gap analyzer and CI gate |
| `scripts/e2e_test_scaffolder.py` | Playwright scaffolder for Next.js routes |
| `assets/sample_components/Button.tsx` | Component with a typed props interface for the generator |
| `assets/sample_app/app/` | Two-route Next.js App Router tree for the scaffolder |
| `assets/sample_lcov.info` | LCOV report with an under-tested payment file (strict gate exits 1 at 80) |
| `references/*.md` | Workflows, CLI reference, strategies, automation patterns, best practices |
