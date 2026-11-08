---
name: playwright-pro
description: >
  End-to-end testing with Playwright: test generation, page objects, locator strategy, flaky-
  test diagnosis, visual regression, and CI integration. Use when writing E2E tests, fixing
  flaky tests, or migrating from Cypress/Selenium.
license: MIT + Commons Clause
metadata:
  version: 2.2.0
  author: borghei
  category: engineering
  domain: e2e-testing
  tier: POWERFUL
  updated: 2026-11-08
  tags: [playwright, e2e-testing, page-objects, flaky-tests, migration, ci-integration, visual-regression, accessibility]
  frameworks: playwright, vitest, ci-integration
---
# Playwright Pro

The agent writes and maintains end-to-end tests with Playwright that stay green for the right reasons. It can generate tests from user stories, implement the Page Object pattern for maintainability, apply the correct locator strategy for resilient tests, diagnose and fix flaky tests, migrate from Cypress or Selenium, integrate with CI/CD, run visual regression tests, and perform accessibility audits. The 10 golden rules in the core reference prevent most flaky and brittle tests.

## Core Capabilities

- **Resilient authoring** — `getByRole`/`getByLabel`/`getByText` locator priority, web-first auto-retrying assertions, and the 10 golden rules.
- **Page Object Model** — centralize locators, expose user-intent methods, generate POM classes from HTML/selectors.
- **Test generation** — produce specs from user stories with happy-path and error-path coverage.
- **Flaky-test diagnosis** — trace analysis, headed/debug runs, race-condition and shared-state fixes.
- **Migration** — Cypress/Selenium → Playwright command mapping and auth-setup patterns.
- **CI integration** — GitHub Actions, sharding, conditional browser installs, trace/screenshot artifacts.
- **Visual regression & accessibility** — `toHaveScreenshot` baselines and Axe WCAG AA gates.

## When to Use

- Writing or organizing E2E tests for web apps.
- Fixing flaky tests or diagnosing CI-only failures.
- Migrating a suite from Cypress or Selenium.
- Adding visual regression or WCAG accessibility gates.
- Setting up Playwright CI integration and reporting.

## Clarify First

Before generating tests, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task / sub-skill:** init, generate, fix-flaky, migrate, or review (routes the entire workflow).
- **User story or flow to cover:** the happy + error paths the spec must assert (drives test generation).
- **Locator surface:** whether the app exposes roles/labels/`data-testid` (sets locator strategy and POM resilience).
- **Source framework (if migrating):** Cypress or Selenium (selects the command-mapping table).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Sub-Skills

This skill uses compound sub-skill architecture. Each sub-skill in `skills/` handles a specific workflow:

| Sub-Skill | File | Purpose |
|-----------|------|---------|
| **Init** | `skills/init.md` | Bootstrap Playwright in a project -- install, configure, create first test |
| **Generate** | `skills/generate.md` | Generate test files from user stories or page descriptions |
| **Fix** | `skills/fix.md` | Diagnose and fix failing or flaky tests using trace analysis |
| **Migrate** | `skills/migrate.md` | Migrate from Cypress or Selenium to Playwright |
| **Review** | `skills/review.md` | Audit test quality, coverage gaps, and flaky test indicators |
| **Report** | `skills/report.md` | Generate execution reports from Playwright JSON output |
| **Coverage** | `skills/coverage.md` | Map tests to user stories, identify coverage gaps |
| **BrowserStack** | `skills/browserstack.md` | BrowserStack cloud integration for cross-browser testing |
| **TestRail** | `skills/testrail.md` | TestRail integration for test case management |

**Sub-skill flow:** Init → Generate → Review → Fix (if needed); Coverage → Generate (fill gaps); Report → BrowserStack / TestRail.

## Workflow

1. Pick the sub-skill for the task (table above) and read it.
2. Before writing, map what exists: `coverage_mapper.py` against a flows file shows which user flows have no spec.
3. Write or generate specs with role, label and text locators and web-first assertions; `test_generator.py` and `page_object_generator.py` give a starting skeleton, not finished tests.
4. Validation checkpoint: `test_analyzer.py` on the spec directory must exit 0 (no high-severity findings such as `waitForTimeout` or `force: true`).
5. After CI runs, parse reports with `test_report_parser.py` and track flakiness across runs with `flaky_detector.py`; fix flaky tests by root cause, never by adding retries or sleeps.
6. Done when the critical flows are covered, the analyzer is clean, and the last ten CI runs show no flaky tests.

## Quick Start

```bash
# from engineering/playwright-pro/
python3 scripts/test_analyzer.py assets/tests                    # exit 0: clean
python3 scripts/test_analyzer.py assets/flawed_tests             # exit 1: waitForTimeout, nth-child CSS
python3 scripts/coverage_mapper.py --tests assets/tests --flows assets/sample_flows.json   # 1 of 3 flows covered
```

```bash
python3 scripts/flaky_detector.py --results-dir assets/reports  # checkout spec flaky in 2 of 3 runs
python3 scripts/test_report_parser.py assets/reports/run3.json --top-slow 3
python3 scripts/page_object_generator.py --html assets/sample_login.html --name LoginPage --route /login
python3 scripts/test_generator.py --story "User can log in with email and password" --page LoginPage --route /login
```

## Tools Overview

| Tool | Purpose | Key flags | Exit codes |
|------|---------|-----------|------------|
| `scripts/test_analyzer.py` | Anti-patterns in `.spec.ts` / `.test.ts` files (fixed sleeps, brittle CSS, non-retrying assertions) with line numbers and fixes | `path`, `--severity high\|medium\|low`, `--json` | 0 no high findings; 1 high findings; 2 missing path or no spec files |
| `scripts/coverage_mapper.py` | Matches specs to user flows by keywords, URLs and names; lists gaps by priority | `--tests DIR`, `--flows FILE`, `--threshold 0.3`, `--gaps-only`, `--json` | 0 report; 2 missing dir or invalid flows file |
| `scripts/flaky_detector.py` | Stability per test across several Playwright JSON reports, with duration variance | `--results-dir DIR`, `--runs 10`, `--threshold 0.95`, `--json` | 0 report; 2 no readable reports |
| `scripts/test_report_parser.py` | Summary of one Playwright JSON report: pass, fail, flaky, durations, slowest tests | `report`, `--top-slow 5`, `--flaky-threshold 5`, `--json` | 0 report; 2 unreadable report |
| `scripts/page_object_generator.py` | Page Object class from an HTML file or a selector list | `--html FILE \| --selectors FILE`, `--name`, `--route`, `--json` | 0 generated; 2 missing input |
| `scripts/test_generator.py` | Spec skeleton (happy, validation and negative paths) from a user story | `--story TEXT --page NAME \| --stories FILE`, `--route`, `--output DIR`, `--json` | 0 generated; 2 bad input |

Flows file: a JSON array of `{"id", "name", "priority", "keywords", "pages", "steps"}`; `id` and `name` are required (see `assets/sample_flows.json`). `--gaps-only` filters the listing; the summary always covers every flow. Reports are Playwright's JSON reporter output (`--reporter=json`).

## Anti-Patterns

**Mistake:** Fixing a flaky test with `waitForTimeout` or more retries.
**Why it matters:** Sleeps hide the race and slow every run; retries turn a real bug into a green build.
**Instead:** Wait on the condition (`expect(locator).toBeVisible()`, `waitForResponse`) and isolate shared state; see `skills/fix.md`.

**Mistake:** Locating elements by CSS structure (`div > input:nth-child(2)`).
**Why it matters:** Any layout change breaks the test even when the feature works.
**Instead:** Use `getByRole`, `getByLabel` or `getByText`, then `data-testid` when nothing user-facing is stable.

**Mistake:** Asserting on a one-shot value (`expect(await el.isVisible()).toBe(true)`).
**Why it matters:** It checks once, with no retry, so it fails on slow renders.
**Instead:** Use web-first assertions that retry until the timeout: `await expect(el).toBeVisible()`.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/core-rules-and-patterns.md](references/core-rules-and-patterns.md)** — the 10 golden rules, locator priority, `playwright.config.ts`, Page Object Model classes, test generation from user stories, and shared-auth setup. Read when authoring tests or configuring a project.
- **[references/playwright-patterns.md](references/playwright-patterns.md)** — locator decision tree, web-first vs non-retrying assertion patterns, custom/worker fixtures, network mocking, anti-pattern quick reference, and CI sharding patterns. Read when choosing locators, mocking APIs, or building fixtures.
- **[references/diagnosis-migration-and-ci.md](references/diagnosis-migration-and-ci.md)** — flaky-test causes/fixes and diagnosis commands, Cypress→Playwright migration table, GitHub Actions CI, visual regression, accessibility testing, common pitfalls, best practices, troubleshooting table, and the success-criteria bar. Read when fixing flaky tests, migrating, wiring CI, or auditing a suite.

## Files

| File | Purpose |
|------|---------|
| `skills/*.md` | Nine sub-skill workflows (init, generate, fix, migrate, review, report, coverage, BrowserStack, TestRail) |
| `scripts/*.py` | Six stdlib CLIs (see Tools Overview) |
| `assets/tests/login.spec.ts` | Clean spec; analyzer exits 0 |
| `assets/flawed_tests/profile.spec.ts` | Fixed sleeps and brittle CSS; analyzer exits 1 |
| `assets/sample_flows.json` | Three user flows for the coverage mapper |
| `assets/reports/run1-3.json` | Three Playwright JSON reports with one flaky and one failing test |
| `assets/sample_login.html` | Login form for the Page Object generator |

## Scope & Limitations

**This skill covers:**
- End-to-end test authoring, organization, and maintenance with Playwright
- Page Object Model architecture and locator strategy best practices
- Flaky test diagnosis, CI integration, and trace-based debugging
- Visual regression testing and WCAG accessibility auditing

**This skill does NOT cover:**
- Unit testing or component testing in isolation (see `engineering/senior-qa` for test pyramid guidance)
- API contract testing or load/performance testing (see `engineering/api-test-suite-builder`)
- Test data management, database seeding, or factory patterns for test fixtures
- Mobile native app testing (Appium, Detox); this skill targets web browsers only
