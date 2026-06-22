---
name: playwright-pro
description: >
  End-to-end testing with Playwright: test generation, page objects, locator strategy, flaky-
  test diagnosis, visual regression, and CI integration. Use when writing E2E tests, fixing
  flaky tests, or migrating from Cypress/Selenium.
license: MIT + Commons Clause
metadata:
  version: 2.1.0
  author: borghei
  category: engineering
  domain: e2e-testing
  tier: POWERFUL
  updated: 2026-06-17
  tags: [playwright, e2e-testing, page-objects, flaky-tests, migration, ci-integration, visual-regression, accessibility]
  frameworks: playwright, vitest, ci-integration
---
# Playwright Pro

Production-grade end-to-end testing with Playwright. Generate tests from user stories, implement the Page Object pattern for maintainability, apply the correct locator strategy for resilient tests, diagnose and fix flaky tests, migrate from Cypress or Selenium, integrate with CI/CD, run visual regression tests, and perform accessibility audits. Enforces the 10 golden rules that eliminate 90% of E2E test failures.

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

Before generating tests, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task / sub-skill** — init, generate, fix-flaky, migrate, or review (routes the entire workflow)
- [ ] **User story or flow to cover** — the happy + error paths the spec must assert (drives test generation)
- [ ] **Locator surface** — whether the app exposes roles/labels/`data-testid` (sets locator strategy and POM resilience)
- [ ] **Source framework (if migrating)** — Cypress or Selenium (selects the command-mapping table)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `test_generator.py` | Generate Playwright test code from user story descriptions | `python scripts/test_generator.py --story "..." --page LoginPage --output tests/` |
| `flaky_detector.py` | Analyze multiple CI runs to detect flaky test patterns | `python scripts/flaky_detector.py --results-dir results/ --runs 10 --threshold 0.05` |
| `coverage_mapper.py` | Map tests to user flows and identify coverage gaps | `python scripts/coverage_mapper.py --tests tests/ --flows flows.json --gaps-only` |
| `page_object_generator.py` | Generate Page Object classes from HTML or selector lists | `python scripts/page_object_generator.py --html page.html --name LoginPage --route /login` |
| `test_analyzer.py` | Scan test files for anti-patterns and quality issues | `python scripts/test_analyzer.py tests/ --severity high` |
| `test_report_parser.py` | Parse Playwright JSON reports into summaries | `python scripts/test_report_parser.py report.json --top-slow 10` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/core-rules-and-patterns.md](references/core-rules-and-patterns.md)** — the 10 golden rules, locator priority, `playwright.config.ts`, Page Object Model classes, test generation from user stories, and shared-auth setup. Read when authoring tests or configuring a project.
- **[references/playwright-patterns.md](references/playwright-patterns.md)** — locator decision tree, web-first vs non-retrying assertion patterns, custom/worker fixtures, network mocking, anti-pattern quick reference, and CI sharding patterns. Read when choosing locators, mocking APIs, or building fixtures.
- **[references/diagnosis-migration-and-ci.md](references/diagnosis-migration-and-ci.md)** — flaky-test causes/fixes and diagnosis commands, Cypress→Playwright migration table, GitHub Actions CI, visual regression, accessibility testing, common pitfalls, best practices, troubleshooting table, and the success-criteria bar. Read when fixing flaky tests, migrating, wiring CI, or auditing a suite.

## Scope & Limitations

**This skill covers:**
- End-to-end test authoring, organization, and maintenance with Playwright
- Page Object Model architecture and locator strategy best practices
- Flaky test diagnosis, CI integration, and trace-based debugging
- Visual regression testing and WCAG accessibility auditing

**This skill does NOT cover:**
- Unit testing or component testing in isolation (see `engineering/testing-strategy` for test pyramid guidance)
- API contract testing or load/performance testing (see `api-test-suite-builder` for API-focused testing)
- Test data management, database seeding, or factory patterns for test fixtures
- Mobile native app testing (Appium, Detox); this skill targets web browsers only

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `ci-cd-pipeline-builder` | E2E tests run as a pipeline stage after build and unit tests | Pipeline config triggers `playwright test`; artifacts (traces, screenshots) upload on failure |
| `api-test-suite-builder` | API tests validate backend contracts; Playwright tests validate UI flows end-to-end | API test results confirm endpoint stability before E2E suite runs against the same environment |
| `pr-review-expert` | PR reviews check for test coverage on UI changes and flag missing E2E specs | Review checklist references Playwright Pro golden rules; flags `waitForTimeout` or raw CSS selectors |
| `performance-profiler` | Performance budgets complement E2E tests to catch regressions | Profiler identifies slow pages; Playwright tests add `networkidle` waits or performance assertions for flagged routes |
| `observability-designer` | Test failures feed into observability dashboards for flake tracking | CI test results export JSON reports; observability pipelines ingest pass/fail/flake metrics over time |
| `release-manager` | E2E suite is a release gate; green suite required before deployment proceeds | Release workflow calls Playwright CI job; blocks release tag creation on any test failure |
