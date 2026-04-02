---
name: playwright-pro
description: >
  Production-grade end-to-end testing with Playwright. Covers test generation
  from user stories, page object patterns, locator strategy, flaky test
  diagnosis, Cypress/Selenium migration, CI integration, visual regression
  testing, and accessibility auditing. Use when writing E2E tests, fixing flaky
  tests, or migrating from Cypress/Selenium.
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: engineering
  domain: e2e-testing
  tier: POWERFUL
  updated: 2026-04-02
  tags: [playwright, e2e-testing, page-objects, flaky-tests, migration, ci-integration, visual-regression, accessibility]
  frameworks: playwright, vitest, ci-integration
---
# Playwright Pro

**Tier:** POWERFUL
**Category:** Engineering / Testing
**Maintainer:** Claude Skills Team

## Overview

Production-grade end-to-end testing with Playwright. Generate tests from user stories, implement the Page Object pattern for maintainability, apply the correct locator strategy for resilient tests, diagnose and fix flaky tests, migrate from Cypress or Selenium, integrate with CI/CD, run visual regression tests, and perform accessibility audits. Enforces the 10 golden rules that eliminate 90% of E2E test failures.

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

### Sub-Skill Flow

```
Init ──> Generate ──> Review ──> Fix (if needed)
                         │
                    Coverage ──> Generate (fill gaps)
                         │
                    Report ──> BrowserStack / TestRail
```

**Typical lifecycle:** Init sets up the project, Generate creates tests from stories, Review audits quality, Fix resolves failures, Coverage identifies gaps that feed back into Generate, and Report/BrowserStack/TestRail handle reporting and integration.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/test_generator.py` | Generate Playwright test code from user story descriptions |
| `scripts/flaky_detector.py` | Analyze multiple CI runs to detect flaky test patterns |
| `scripts/coverage_mapper.py` | Map tests to user flows and identify coverage gaps |
| `scripts/page_object_generator.py` | Generate Page Object classes from HTML or selector lists |
| `scripts/test_analyzer.py` | Scan test files for anti-patterns and quality issues |
| `scripts/test_report_parser.py` | Parse Playwright JSON reports into summaries |

## Keywords

Playwright, E2E testing, end-to-end testing, page objects, flaky tests, test generation, Cypress migration, Selenium migration, visual regression, accessibility testing, CI integration

## 10 Golden Rules

These rules are non-negotiable. Following them eliminates 90% of E2E test failures.

1. **`getByRole()` over CSS/XPath** — resilient to markup changes
2. **Never `page.waitForTimeout()`** — use web-first assertions instead
3. **`expect(locator)` auto-retries; `expect(await locator.textContent())` does NOT**
4. **Isolate every test** — no shared state between tests
5. **`baseURL` in config** — zero hardcoded URLs in tests
6. **Retries: 2 in CI, 0 locally** — retries mask flakiness in dev
7. **Traces: `'on-first-retry'`** — rich debugging without slowdown
8. **Fixtures over globals** — `test.extend()` for shared setup
9. **One behavior per test** — multiple related assertions are fine
10. **Mock external services only** — never mock your own app

## Locator Priority (Most to Least Preferred)

```
1. getByRole('button', { name: 'Submit' })     — semantic, accessible
2. getByLabel('Email address')                   — form fields with labels
3. getByText('Welcome back')                     — visible text content
4. getByPlaceholder('Enter your email')          — inputs with placeholder
5. getByTestId('submit-button')                  — when no semantic option exists
6. page.locator('.submit-btn')                   — CSS as last resort
7. page.locator('//button[@type="submit"]')      — XPath: avoid entirely
```

### Why This Order Matters

```typescript
// FRAGILE: breaks when CSS class changes
await page.locator('.btn-primary-lg').click();

// FRAGILE: breaks when DOM structure changes
await page.locator('div > form > button:nth-child(2)').click();

// RESILIENT: survives refactors, tests what users see
await page.getByRole('button', { name: 'Create account' }).click();
```

## Configuration

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: process.env.CI
    ? [['html'], ['github'], ['json', { outputFile: 'test-results.json' }]]
    : [['html']],

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    // Auth setup: runs once, shares state with all tests
    { name: 'setup', testMatch: /.*\.setup\.ts/ },

    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
      dependencies: ['setup'],
    },
  ],

  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 30000,
  },
});
```

## Page Object Pattern

```typescript
// pages/login.page.ts
import { type Page, type Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly forgotPasswordLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email address');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
    this.forgotPasswordLink = page.getByRole('link', { name: 'Forgot password?' });
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }

  async expectRedirectToDashboard() {
    await expect(this.page).toHaveURL(/\/dashboard/);
  }
}
```

```typescript
// pages/dashboard.page.ts
import { type Page, type Locator, expect } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly projectList: Locator;
  readonly createProjectButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByRole('heading', { name: 'Dashboard' });
    this.projectList = page.getByRole('list', { name: 'Projects' });
    this.createProjectButton = page.getByRole('button', { name: 'New project' });
  }

  async expectLoaded() {
    await expect(this.heading).toBeVisible();
  }

  async getProjectCount() {
    return this.projectList.getByRole('listitem').count();
  }

  async createProject(name: string) {
    await this.createProjectButton.click();
    await this.page.getByLabel('Project name').fill(name);
    await this.page.getByRole('button', { name: 'Create' }).click();
  }
}
```

## Test Generation from User Stories

Given a user story, generate tests following this pattern:

```typescript
// tests/e2e/auth/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../../pages/login.page';
import { DashboardPage } from '../../pages/dashboard.page';

test.describe('User Login', () => {
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  test('successful login redirects to dashboard', async ({ page }) => {
    await loginPage.login('user@example.com', 'password123');
    const dashboard = new DashboardPage(page);
    await dashboard.expectLoaded();
  });

  test('shows error for invalid credentials', async () => {
    await loginPage.login('user@example.com', 'wrongpassword');
    await loginPage.expectError('Invalid email or password');
  });

  test('shows validation error for empty email', async () => {
    await loginPage.login('', 'password123');
    await loginPage.expectError('Email is required');
  });

  test('shows validation error for invalid email format', async () => {
    await loginPage.login('not-an-email', 'password123');
    await loginPage.expectError('Enter a valid email');
  });

  test('forgot password link navigates to reset page', async ({ page }) => {
    await loginPage.forgotPasswordLink.click();
    await expect(page).toHaveURL(/\/forgot-password/);
  });
});
```

## Authentication Setup (Shared State)

```typescript
// tests/e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate as test user', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email address').fill('test@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Wait for redirect to confirm login succeeded
  await expect(page).toHaveURL(/\/dashboard/);

  // Save authentication state for reuse
  await page.context().storageState({ path: authFile });
});
```

## Flaky Test Diagnosis

### Common Causes and Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `waitForTimeout(2000)` in test | Timing-dependent | Replace with `await expect(locator).toBeVisible()` |
| Test passes locally, fails in CI | Race condition | Add web-first assertion before interaction |
| Element not found after navigation | Page not loaded | `await page.waitForURL('/expected-path')` |
| Stale element reference | DOM re-rendered | Use Playwright locators (auto-retry) |
| Different data between runs | Shared test state | Isolate with `test.beforeEach` setup |
| Flaky on slow CI runners | Insufficient timeout | Increase `expect` timeout, not `waitForTimeout` |

### Diagnosis Commands

```bash
# Run with trace on every test (not just retries)
npx playwright test --trace on

# Run a specific flaky test 10 times
for i in $(seq 1 10); do npx playwright test tests/e2e/checkout.spec.ts; done

# Show test timeline
npx playwright test --trace on
npx playwright show-trace test-results/*/trace.zip

# Run in headed mode for visual debugging
npx playwright test --headed --retries 0

# Debug a specific test interactively
npx playwright test --debug tests/e2e/checkout.spec.ts
```

## Cypress to Playwright Migration

| Cypress | Playwright |
|---------|-----------|
| `cy.visit('/path')` | `await page.goto('/path')` |
| `cy.get('.selector')` | `page.locator('.selector')` |
| `cy.contains('text')` | `page.getByText('text')` |
| `cy.get('[data-testid="x"]')` | `page.getByTestId('x')` |
| `cy.intercept('GET', '/api/*')` | `await page.route('/api/*', ...)` |
| `cy.wait('@alias')` | `await page.waitForResponse('/api/*')` |
| `cy.should('be.visible')` | `await expect(locator).toBeVisible()` |
| `cy.should('have.text', 'x')` | `await expect(locator).toHaveText('x')` |
| `cy.fixture('data.json')` | `JSON.parse(fs.readFileSync(...))` |
| `beforeEach(() => { cy.login() })` | Auth setup project + storageState |

## CI Integration

### GitHub Actions

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec playwright install --with-deps chromium

      - run: pnpm build  # build the app first
      - run: pnpm exec playwright test
        env:
          BASE_URL: http://localhost:3000

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 7
```

## Visual Regression Testing

```typescript
// tests/e2e/visual/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test('dashboard matches visual snapshot', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');

  // Full page screenshot comparison
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixels: 50,  // allow small rendering differences
  });
});

test('project card component snapshot', async ({ page }) => {
  await page.goto('/dashboard');
  const card = page.getByTestId('project-card').first();

  await expect(card).toHaveScreenshot('project-card.png', {
    maxDiffPixelRatio: 0.01,
  });
});
```

```bash
# Generate/update baseline screenshots
npx playwright test --update-snapshots

# Run visual comparison
npx playwright test tests/e2e/visual/
```

## Accessibility Testing

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('login page has no accessibility violations', async ({ page }) => {
  await page.goto('/login');

  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();

  expect(results.violations).toEqual([]);
});

test('dashboard meets WCAG AA standards', async ({ page }) => {
  await page.goto('/dashboard');

  const results = await new AxeBuilder({ page })
    .exclude('.third-party-widget')  // exclude elements you don't control
    .analyze();

  // Log violations for debugging
  for (const violation of results.violations) {
    console.log(`${violation.impact}: ${violation.description}`);
    for (const node of violation.nodes) {
      console.log(`  - ${node.html}`);
    }
  }

  expect(results.violations.filter(v => v.impact === 'critical')).toEqual([]);
});
```

## Common Pitfalls

- **`page.waitForTimeout(N)`** — the single most common cause of flaky tests; use web-first assertions
- **CSS selectors as primary strategy** — breaks on every refactor; use role/label/text locators
- **Shared state between tests** — one test's data pollutes another; isolate with proper setup/teardown
- **No trace configuration** — debugging CI failures without traces wastes hours; enable `on-first-retry`
- **Testing third-party services** — mock external APIs; only test your own application
- **Running all browsers in development** — test Chromium locally, full matrix in CI only
- **No page objects** — duplicate locators across tests create maintenance nightmares

## Best Practices

1. **Page Object per page/component** — centralize locators, expose user-intent methods
2. **Web-first assertions everywhere** — `expect(locator).toBeVisible()` auto-retries, `waitForTimeout` does not
3. **Auth as a setup project** — authenticate once, reuse `storageState` across all tests
4. **One behavior per test** — keeps failures isolated and test names meaningful
5. **Run in CI with `--retries 2`** — but investigate any test that needs retries locally
6. **Trace + screenshot on failure** — upload as CI artifacts for post-mortem debugging
7. **Visual regression for critical UI** — catch unintended visual changes automatically
8. **Accessibility tests in the suite** — WCAG compliance as a regression gate, not an afterthought

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `locator.click()` times out | Element hidden behind overlay/modal or not yet rendered | Add `await expect(locator).toBeVisible()` before clicking; check for z-index overlays blocking the target |
| Visual snapshots fail on every CI run | Different OS font rendering between local and CI | Generate baseline screenshots inside CI (Linux), not locally (macOS); use `maxDiffPixelRatio: 0.02` for tolerance |
| Auth setup project runs but tests get 401 | `storageState` path mismatch or expired token | Verify `storageState` path in `playwright.config.ts` matches the setup script; confirm tokens don't expire mid-suite |
| `page.route()` intercept never triggers | Route pattern doesn't match the actual request URL or glob syntax error | Log requests with `page.on('request', r => console.log(r.url()))` to verify the exact URL; use `**` glob for subpaths |
| Tests pass individually but fail when run together | Shared mutable state or port collision between parallel workers | Ensure test isolation via `test.beforeEach` setup; use unique test data per worker with `test.info().parallelIndex` |
| `toHaveScreenshot()` throws "missing baseline" | Snapshot file not committed to version control | Run `npx playwright test --update-snapshots` and commit the generated files under the `__screenshots__` directory |
| Accessibility audit returns false positives | Axe scanning third-party embedded widgets or iframes | Use `.exclude('.third-party-widget')` or `.include('#app-root')` to scope the audit to your own markup |

## Success Criteria

- **Flaky test rate below 2%** — measured over a rolling 7-day window across all CI runs; any test exceeding 5% flake rate is quarantined and fixed within 48 hours
- **E2E suite completes within 10 minutes** — full cross-browser matrix (Chromium, Firefox, mobile) on CI with 4 parallel workers; alert if wall-clock time exceeds threshold
- **100% of critical user journeys covered** — login, checkout, onboarding, and core CRUD workflows each have dedicated spec files with happy-path and primary error-path tests
- **Zero `waitForTimeout()` calls in the codebase** — enforced via ESLint rule or grep-based CI check; all waits use web-first assertions
- **Page Object coverage for every tested page** — no raw locators in spec files; all element access goes through page object classes with user-intent method names
- **WCAG AA compliance gate passing** — accessibility tests run on every PR; zero critical or serious violations allowed to merge
- **Visual regression baselines reviewed on every UI PR** — screenshot diffs attached to PR as artifacts; baseline updates require explicit reviewer approval

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
