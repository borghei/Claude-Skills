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
  updated: 2026-06-17
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

Before generating tests, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Test layer** — unit (Jest+RTL) vs E2E (Playwright) (selects `test_suite_generator` vs `e2e_test_scaffolder`)
- [ ] **Source path** — the components or Next.js routes to generate tests from (the scaffolder's input)
- [ ] **Coverage focus** — happy path only vs interaction/state/a11y (`jest-axe`) (sets which test stubs are emitted)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `test_suite_generator.py` | Generate Jest + RTL test stubs from React components | `python scripts/test_suite_generator.py src/components/ --output __tests__/` |
| `coverage_analyzer.py` | Analyze Istanbul/LCOV coverage and report gaps | `python scripts/coverage_analyzer.py coverage/coverage-final.json --threshold 80` |
| `e2e_test_scaffolder.py` | Scaffold Playwright E2E tests from Next.js routes | `python scripts/e2e_test_scaffolder.py src/app/ --output e2e/` |

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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-frontend` | Generated test stubs align with component patterns from the frontend skill | Frontend components --> `test_suite_generator.py` --> test files |
| `senior-fullstack` | Code quality analyzer consumes the same coverage reports produced here | `coverage_analyzer.py` output --> fullstack quality dashboard |
| `senior-devops` | E2E test scaffolder generates CI-ready Playwright configs that plug into DevOps pipelines | `e2e_test_scaffolder.py` --> `playwright.config.ts` --> GitHub Actions workflow |
| `code-reviewer` | Coverage gaps feed directly into code review checklists for untested changes | `coverage_analyzer.py` gaps --> review checklist items |
| `tdd-guide` | TDD workflow references this skill's test generator for initial red-phase stub creation | TDD cycle --> `test_suite_generator.py --scan-only` --> write tests --> implement |
| `qa-browser-automation` | Page Object Models generated here are consumed by the browser automation skill for advanced E2E scenarios | `e2e_test_scaffolder.py --include-pom` --> POM classes --> browser automation flows |
