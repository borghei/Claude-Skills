---
name: senior-qa
description: >
  This skill should be used when the user asks to "generate tests", "write unit
  tests", "analyze test coverage", "scaffold E2E tests", "set up Playwright",
  "configure Jest", "implement testing patterns", or "improve test quality". Use
  for React/Next.js testing with Jest, React Testing Library, and Playwright.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: quality-assurance
  updated: 2026-03-31
  tags: [test-strategy, automation, performance-testing, test-frameworks]
---
# Senior QA Engineer

Test automation, coverage analysis, and quality assurance patterns for React and Next.js applications.

## Table of Contents

- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
  - [Test Suite Generator](#1-test-suite-generator)
  - [Coverage Analyzer](#2-coverage-analyzer)
  - [E2E Test Scaffolder](#3-e2e-test-scaffolder)
- [QA Workflows](#qa-workflows)
  - [Unit Test Generation Workflow](#unit-test-generation-workflow)
  - [Coverage Analysis Workflow](#coverage-analysis-workflow)
  - [E2E Test Setup Workflow](#e2e-test-setup-workflow)
- [Reference Documentation](#reference-documentation)
- [Common Patterns Quick Reference](#common-patterns-quick-reference)

---

## Quick Start

```bash
# Generate Jest test stubs for React components
python scripts/test_suite_generator.py src/components/ --output __tests__/

# Analyze test coverage from Jest/Istanbul reports
python scripts/coverage_analyzer.py coverage/coverage-final.json --threshold 80

# Scaffold Playwright E2E tests for Next.js routes
python scripts/e2e_test_scaffolder.py src/app/ --output e2e/
```

---

## Tools Overview

### 1. Test Suite Generator

Scans React/TypeScript components and generates Jest + React Testing Library test stubs with proper structure.

**Input:** Source directory containing React components
**Output:** Test files with describe blocks, render tests, interaction tests

**Usage:**
```bash
# Basic usage - scan components and generate tests
python scripts/test_suite_generator.py src/components/ --output __tests__/

# Output:
# Scanning: src/components/
# Found 24 React components
#
# Generated tests:
#   __tests__/Button.test.tsx (render, click handler, disabled state)
#   __tests__/Modal.test.tsx (render, open/close, keyboard events)
#   __tests__/Form.test.tsx (render, validation, submission)
#   ...
#
# Summary: 24 test files, 87 test cases

# Include accessibility tests
python scripts/test_suite_generator.py src/ --output __tests__/ --include-a11y

# Generate with custom template
python scripts/test_suite_generator.py src/ --template custom-template.tsx
```

**Supported Patterns:**
- Functional components with hooks
- Components with Context providers
- Components with data fetching
- Form components with validation

---

### 2. Coverage Analyzer

Parses Jest/Istanbul coverage reports and identifies gaps, uncovered branches, and provides actionable recommendations.

**Input:** Coverage report (JSON or LCOV format)
**Output:** Coverage analysis with recommendations

**Usage:**
```bash
# Analyze coverage report
python scripts/coverage_analyzer.py coverage/coverage-final.json

# Output:
# === Coverage Analysis Report ===
# Overall: 72.4% (target: 80%)
#
# BY TYPE:
#   Statements: 74.2%
#   Branches: 68.1%
#   Functions: 71.8%
#   Lines: 73.5%
#
# CRITICAL GAPS (uncovered business logic):
#   src/services/payment.ts:45-67 - Payment processing
#   src/hooks/useAuth.ts:23-41 - Authentication flow
#
# RECOMMENDATIONS:
#   1. Add tests for payment service error handling
#   2. Cover authentication edge cases
#   3. Test form validation branches
#
# Files below threshold (80%):
#   src/components/Checkout.tsx: 45%
#   src/services/api.ts: 62%

# Enforce threshold (exit 1 if below)
python scripts/coverage_analyzer.py coverage/ --threshold 80 --strict

# Generate HTML report
python scripts/coverage_analyzer.py coverage/ --format html --output report.html
```

---

### 3. E2E Test Scaffolder

Scans Next.js pages/app directory and generates Playwright test files with common interactions.

**Input:** Next.js pages or app directory
**Output:** Playwright test files organized by route

**Usage:**
```bash
# Scaffold E2E tests for Next.js App Router
python scripts/e2e_test_scaffolder.py src/app/ --output e2e/

# Output:
# Scanning: src/app/
# Found 12 routes
#
# Generated E2E tests:
#   e2e/home.spec.ts (navigation, hero section)
#   e2e/auth/login.spec.ts (form submission, validation)
#   e2e/auth/register.spec.ts (registration flow)
#   e2e/dashboard.spec.ts (authenticated routes)
#   e2e/products/[id].spec.ts (dynamic routes)
#   ...
#
# Generated: playwright.config.ts
# Generated: e2e/fixtures/auth.ts

# Include Page Object Model classes
python scripts/e2e_test_scaffolder.py src/app/ --output e2e/ --include-pom

# Generate for specific routes
python scripts/e2e_test_scaffolder.py src/app/ --routes "/login,/dashboard,/checkout"
```

---

## QA Workflows

### Unit Test Generation Workflow

Use when setting up tests for new or existing React components.

**Step 1: Scan project for untested components**
```bash
python scripts/test_suite_generator.py src/components/ --scan-only
```

**Step 2: Generate test stubs**
```bash
python scripts/test_suite_generator.py src/components/ --output __tests__/
```

**Step 3: Review and customize generated tests**
```typescript
// __tests__/Button.test.tsx (generated)
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../src/components/Button';

describe('Button', () => {
  it('renders with label', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  // TODO: Add your specific test cases
});
```

**Step 4: Run tests and check coverage**
```bash
npm test -- --coverage
python scripts/coverage_analyzer.py coverage/coverage-final.json
```

---

### Coverage Analysis Workflow

Use when improving test coverage or preparing for release.

**Step 1: Generate coverage report**
```bash
npm test -- --coverage --coverageReporters=json
```

**Step 2: Analyze coverage gaps**
```bash
python scripts/coverage_analyzer.py coverage/coverage-final.json --threshold 80
```

**Step 3: Identify critical paths**
```bash
python scripts/coverage_analyzer.py coverage/ --critical-paths
```

**Step 4: Generate missing test stubs**
```bash
python scripts/test_suite_generator.py src/ --uncovered-only --output __tests__/
```

**Step 5: Verify improvement**
```bash
npm test -- --coverage
python scripts/coverage_analyzer.py coverage/ --compare previous-coverage.json
```

---

### E2E Test Setup Workflow

Use when setting up Playwright for a Next.js project.

**Step 1: Initialize Playwright (if not installed)**
```bash
npm init playwright@latest
```

**Step 2: Scaffold E2E tests from routes**
```bash
python scripts/e2e_test_scaffolder.py src/app/ --output e2e/
```

**Step 3: Configure authentication fixtures**
```typescript
// e2e/fixtures/auth.ts (generated)
import { test as base } from '@playwright/test';

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    await use(page);
  },
});
```

**Step 4: Run E2E tests**
```bash
npx playwright test
npx playwright show-report
```

**Step 5: Add to CI pipeline**
```yaml
# .github/workflows/e2e.yml
- name: Run E2E tests
  run: npx playwright test
- name: Upload report
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

---

## Reference Documentation

| File | Contains | Use When |
|------|----------|----------|
| `references/testing_strategies.md` | Test pyramid, testing types, coverage targets, CI/CD integration | Designing test strategy |
| `references/test_automation_patterns.md` | Page Object Model, mocking (MSW), fixtures, async patterns | Writing test code |
| `references/qa_best_practices.md` | Testable code, flaky tests, debugging, quality metrics | Improving test quality |

---

## Common Patterns Quick Reference

### React Testing Library Queries

```typescript
// Preferred (accessible)
screen.getByRole('button', { name: /submit/i })
screen.getByLabelText(/email/i)
screen.getByPlaceholderText(/search/i)

// Fallback
screen.getByTestId('custom-element')
```

### Async Testing

```typescript
// Wait for element
await screen.findByText(/loaded/i);

// Wait for removal
await waitForElementToBeRemoved(() => screen.queryByText(/loading/i));

// Wait for condition
await waitFor(() => {
  expect(mockFn).toHaveBeenCalled();
});
```

### Mocking with MSW

```typescript
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(ctx.json([{ id: 1, name: 'John' }]));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Playwright Locators

```typescript
// Preferred
page.getByRole('button', { name: 'Submit' })
page.getByLabel('Email')
page.getByText('Welcome')

// Chaining
page.getByRole('listitem').filter({ hasText: 'Product' })
```

### Coverage Thresholds (jest.config.js)

```javascript
module.exports = {
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

---

## Common Commands

```bash
# Jest
npm test                           # Run all tests
npm test -- --watch                # Watch mode
npm test -- --coverage             # With coverage
npm test -- Button.test.tsx        # Single file

# Playwright
npx playwright test                # Run all E2E tests
npx playwright test --ui           # UI mode
npx playwright test --debug        # Debug mode
npx playwright codegen             # Generate tests

# Coverage
npm test -- --coverage --coverageReporters=lcov,json
python scripts/coverage_analyzer.py coverage/coverage-final.json
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Test suite generator finds 0 components | Source directory contains no `.tsx`/`.jsx` files, or components use non-standard export patterns | Verify the source path points to a directory with React components. Check that components start with an uppercase letter and use standard `export const` or `export function` syntax. |
| Coverage analyzer exits with "Could not find or parse coverage data" | The coverage file path is incorrect or the format is unsupported | Ensure you pass a valid `coverage-final.json` (Istanbul) or `lcov.info` file. Run `npm test -- --coverage --coverageReporters=json` first to generate the report. |
| E2E scaffolder detects no routes | The scanned directory lacks `page.tsx` (App Router) or `index.tsx` (Pages Router) files | Confirm you are pointing at the correct Next.js directory (e.g., `src/app/` for App Router or `pages/` for Pages Router). |
| Generated tests fail to compile | Import paths in generated stubs do not match actual project structure | Adjust the relative import paths in each generated `.test.tsx` file to match your project's alias or directory layout. |
| Coverage report shows 100% on files with no executable code | Istanbul counts files with zero statements as fully covered by default | Exclude non-code files (e.g., type declarations, barrel exports) using the `coveragePathIgnorePatterns` option in `jest.config.js`. |
| Flaky E2E tests in CI | Playwright tests depend on a running dev server that is not ready before tests start | Use the `webServer` option in `playwright.config.ts` (generated by the scaffolder) and increase the `timeout` value if the app is slow to start. |
| `--strict` mode fails despite seemingly adequate coverage | Branch coverage is calculated separately and may be below the threshold even when line coverage passes | Run `coverage_analyzer.py` without `--strict` first to review the full breakdown, then add targeted branch-coverage tests for conditional logic. |

---

## Success Criteria

- **Code coverage above 80%** across statements, branches, functions, and lines for all non-trivial source files.
- **Zero critical coverage gaps** in authentication, payment, and security modules as reported by `coverage_analyzer.py --critical-paths`.
- **100% of React components have at least a render test** confirming they mount without crashing.
- **All E2E tests pass on Chromium, Firefox, and WebKit** in CI before merge to main.
- **Branch coverage above 75%** for service layers, API handlers, and middleware modules.
- **No flaky tests** -- every test in the suite produces deterministic results across 3 consecutive CI runs.
- **Test generation covers all detected routes** -- the E2E scaffolder accounts for every page route in the Next.js application, including dynamic segments.

---

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

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-frontend` | Generated test stubs align with component patterns from the frontend skill | Frontend components --> `test_suite_generator.py` --> test files |
| `senior-fullstack` | Code quality analyzer consumes the same coverage reports produced here | `coverage_analyzer.py` output --> fullstack quality dashboard |
| `senior-devops` | E2E test scaffolder generates CI-ready Playwright configs that plug into DevOps pipelines | `e2e_test_scaffolder.py` --> `playwright.config.ts` --> GitHub Actions workflow |
| `code-reviewer` | Coverage gaps feed directly into code review checklists for untested changes | `coverage_analyzer.py` gaps --> review checklist items |
| `tdd-guide` | TDD workflow references this skill's test generator for initial red-phase stub creation | TDD cycle --> `test_suite_generator.py --scan-only` --> write tests --> implement |
| `qa-browser-automation` | Page Object Models generated here are consumed by the browser automation skill for advanced E2E scenarios | `e2e_test_scaffolder.py --include-pom` --> POM classes --> browser automation flows |

---

## Tool Reference

### 1. test_suite_generator.py

**Purpose:** Scans React/TypeScript source directories for components and generates Jest + React Testing Library test stubs with render tests, prop tests, interaction tests, state tests, and optional accessibility tests.

**Usage:**
```bash
python scripts/test_suite_generator.py <source> [options]
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `source` | -- | positional | *(required)* | Source directory containing React components |
| `--output` | `-o` | string | `<source>/__tests__/` | Output directory for generated test files |
| `--include-a11y` | -- | flag | `false` | Include accessibility tests using `jest-axe` |
| `--scan-only` | -- | flag | `false` | Scan and report components without generating test files |
| `--template` | -- | string | `None` | Path to a custom template file for test generation |
| `--verbose` | `-v` | flag | `false` | Enable verbose output showing each detected component |
| `--json` | -- | flag | `false` | Output results as JSON after generation |

**Example:**
```bash
python scripts/test_suite_generator.py src/components/ \
  --output __tests__/ \
  --include-a11y \
  --verbose

# Scanning: src/components/
# Found 24 React components
#   Button.test.tsx (4 test cases)
#   Modal.test.tsx (3 test cases)
#   ...
# Summary: 24 test files, 87 test cases
```

**Output Formats:**
- **Default (text):** Human-readable summary printed to stdout listing each generated file and test case count.
- **JSON (`--json`):** Structured object with `status`, `components` (array of detected component metadata), `generated_files` (array of output paths), and `summary` (totals).

---

### 2. coverage_analyzer.py

**Purpose:** Parses Jest/Istanbul coverage reports (JSON or LCOV format), identifies coverage gaps by severity, flags critical business-logic paths, and generates actionable recommendations in text, HTML, or JSON format.

**Usage:**
```bash
python scripts/coverage_analyzer.py <coverage> [options]
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `coverage` | -- | positional | *(required)* | Path to coverage file (`.json`, `.info`) or directory containing coverage data |
| `--threshold` | `-t` | int | `80` | Coverage threshold percentage for pass/fail determination |
| `--strict` | -- | flag | `false` | Exit with code 1 if overall coverage is below threshold |
| `--critical-paths` | -- | flag | `false` | Focus analysis on critical business paths (auth, payment, security) |
| `--format` | `-f` | choice | `text` | Output format: `text`, `html`, or `json` |
| `--output` | `-o` | string | `None` | Write report to file instead of stdout |
| `--verbose` | `-v` | flag | `false` | Enable verbose output with detailed parsing information |
| `--json` | -- | flag | `false` | Output summary results as JSON (independent of `--format`) |

**Example:**
```bash
python scripts/coverage_analyzer.py coverage/coverage-final.json \
  --threshold 80 \
  --strict \
  --format html \
  --output report.html

# Analyzing coverage from: coverage/coverage-final.json
# Found coverage data for 42 files
# Report written to: report.html
```

**Output Formats:**
- **Text (`--format text`):** Structured report with overall percentages, threshold pass/fail, critical gaps, files below threshold, and prioritized recommendations.
- **HTML (`--format html`):** Styled HTML report with color-coded coverage stats, gap severity table, and per-file breakdown. Suitable for CI artifact upload.
- **JSON (`--json`):** Summary object with `status` (pass/fail), `threshold`, `coverage` (statement/branch/function/line percentages), `files_analyzed`, `files_below_threshold`, `total_gaps`, and `critical_gaps`.

---

### 3. e2e_test_scaffolder.py

**Purpose:** Scans Next.js App Router or Pages Router directories, detects routes (including dynamic segments, route groups, and authenticated pages), and generates Playwright test files with navigation, form, auth, and interaction test stubs. Optionally generates Page Object Model classes and Playwright configuration.

**Usage:**
```bash
python scripts/e2e_test_scaffolder.py <source> [options]
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `source` | -- | positional | *(required)* | Source directory (`src/app/` for App Router or `pages/` for Pages Router) |
| `--output` | `-o` | string | `e2e/` | Output directory for generated test and fixture files |
| `--include-pom` | -- | flag | `false` | Generate Page Object Model classes in `<output>/pages/` |
| `--routes` | -- | string | `None` | Comma-separated list of routes to generate (e.g., `"/login,/dashboard"`) |
| `--verbose` | `-v` | flag | `false` | Enable verbose output showing each detected route |
| `--json` | -- | flag | `false` | Output results as JSON |

**Example:**
```bash
python scripts/e2e_test_scaffolder.py src/app/ \
  --output e2e/ \
  --include-pom \
  --routes "/login,/dashboard,/checkout"

# Scanning: src/app/
# Found 3 routes
#   auth-login.spec.ts
#   pages/AuthLoginPage.ts
#   dashboard.spec.ts
#   pages/DashboardPage.ts
#   checkout.spec.ts
#   pages/CheckoutPage.ts
#   fixtures/auth.ts
#
# Summary: 3 routes, 8 files generated
```

**Output Formats:**
- **Default (text):** Human-readable list of generated files and a route/file count summary.
- **JSON (`--json`):** Structured object with `status`, `routes` (array of route metadata including path, type, params, form/auth detection), `generated_files` (array with type, route, and path), and `summary` (totals and configuration flags).

**Generated Artifacts:**
- `<route>.spec.ts` -- Playwright test file per route with contextual test cases.
- `pages/<RouteName>Page.ts` -- Page Object Model class (when `--include-pom` is set).
- `playwright.config.ts` -- Multi-browser configuration with dev server integration (generated once if not already present).
- `fixtures/auth.ts` -- Authentication fixture with UI and API login patterns (generated once if not already present).
