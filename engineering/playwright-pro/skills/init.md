# Sub-Skill: Project Initialization

**Parent:** playwright-pro
**Trigger:** "set up Playwright", "initialize e2e tests", "add Playwright to project"

## Purpose

Bootstrap a Playwright testing environment from scratch in an existing project. Handles installation, configuration, directory structure, first test, and CI integration.

## Workflow

### Step 1: Install Dependencies

```bash
# Detect package manager
pnpm add -D @playwright/test
pnpm exec playwright install --with-deps chromium firefox
```

### Step 2: Generate Configuration

Create `playwright.config.ts` following the golden rules:
- `baseURL` from environment variable with localhost fallback
- `retries: 2` in CI, `0` locally
- `trace: 'on-first-retry'`
- `screenshot: 'only-on-failure'`
- Projects: chromium + firefox + mobile-chrome
- Auth setup project with `storageState`

### Step 3: Create Directory Structure

```
tests/
├── e2e/
│   ├── auth.setup.ts        # Shared authentication
│   ├── smoke.spec.ts         # First smoke test
│   └── __fixtures__/         # Test data
├── pages/                    # Page Objects
│   └── base.page.ts          # Base page class
└── helpers/                  # Test utilities
    └── test-data.ts          # Data factory helpers
```

### Step 4: Write Smoke Test

Generate a minimal smoke test that validates the app loads, the page title is correct, and no console errors appear. This confirms the setup works end-to-end.

### Step 5: Add to CI

Add a GitHub Actions job or extend existing pipeline with the Playwright step. Include artifact upload for reports on failure.

### Step 6: Verify

```bash
npx playwright test tests/e2e/smoke.spec.ts --reporter=list
```

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Package manager | No | Auto-detected (pnpm > npm > yarn) |
| Base URL | No | Defaults to http://localhost:3000 |
| Browsers | No | Defaults to chromium + firefox + mobile |

## Outputs

- `playwright.config.ts` configured per golden rules
- Directory structure with first smoke test
- CI workflow step (if requested)
- Confirmation the smoke test passes
