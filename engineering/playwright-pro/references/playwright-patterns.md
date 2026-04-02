# Playwright Patterns Reference

## Locator Strategy Decision Tree

```
Need to find an element?
├── Does it have a semantic role? (button, link, heading, textbox)
│   └── YES → getByRole('role', { name: 'visible text' })
├── Is it a labeled form field?
│   └── YES → getByLabel('Label text')
├── Does it have visible text content?
│   └── YES → getByText('Text content')
├── Does it have a placeholder?
│   └── YES → getByPlaceholder('Placeholder text')
├── Does it have a data-testid?
│   └── YES → getByTestId('test-id')
└── Last resort
    └── page.locator('css-selector')
```

## Assertion Patterns

### Web-First (Auto-Retrying) Assertions

These assertions automatically retry until the condition is met or the timeout expires:

```typescript
await expect(locator).toBeVisible();
await expect(locator).toBeHidden();
await expect(locator).toBeEnabled();
await expect(locator).toBeDisabled();
await expect(locator).toHaveText('exact text');
await expect(locator).toContainText('partial text');
await expect(locator).toHaveValue('input value');
await expect(locator).toHaveAttribute('name', 'value');
await expect(locator).toHaveCount(5);
await expect(locator).toHaveClass(/active/);
await expect(page).toHaveURL(/\/dashboard/);
await expect(page).toHaveTitle('Page Title');
```

### Non-Retrying (Avoid in Tests)

These evaluate once and do NOT retry:

```typescript
// BAD: Does not auto-retry
expect(await locator.textContent()).toBe('text');
expect(await locator.isVisible()).toBe(true);
expect(await page.title()).toBe('Title');
```

## Fixture Patterns

### Custom Test Fixture

```typescript
import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/login.page';

type Fixtures = {
  loginPage: LoginPage;
  authenticatedPage: Page;
};

export const test = base.extend<Fixtures>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await use(loginPage);
  },
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'playwright/.auth/user.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});
```

### Worker-Scoped Fixture (Shared Across Tests)

```typescript
export const test = base.extend<{}, { dbConnection: Connection }>({
  dbConnection: [async ({}, use) => {
    const conn = await createConnection();
    await use(conn);
    await conn.close();
  }, { scope: 'worker' }],
});
```

## Network Mocking Patterns

### Mock API Response

```typescript
await page.route('/api/users', async (route) => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: 'Test User' }]),
  });
});
```

### Intercept and Modify Response

```typescript
await page.route('/api/config', async (route) => {
  const response = await route.fetch();
  const json = await response.json();
  json.featureFlag = true;
  await route.fulfill({ response, body: JSON.stringify(json) });
});
```

### Wait for API Call

```typescript
const responsePromise = page.waitForResponse('/api/submit');
await page.getByRole('button', { name: 'Submit' }).click();
const response = await responsePromise;
expect(response.status()).toBe(200);
```

## Anti-Pattern Quick Reference

| Anti-Pattern | Fix |
|-------------|-----|
| `page.waitForTimeout(N)` | `await expect(locator).toBeVisible()` |
| `expect(await el.textContent())` | `await expect(el).toHaveText()` |
| `page.locator('.class-name')` | `page.getByRole('button', { name: '...' })` |
| `{ force: true }` | Fix underlying visibility issue |
| Global `let page` variable | Use Playwright fixtures |
| `page.goto('http://localhost:3000/path')` | `page.goto('/path')` with baseURL |
| `for` loop running test N times | Use `test.describe.configure({ retries: N })` |
| Shared mutable state between tests | `test.beforeEach` setup or fixtures |

## CI Configuration Patterns

### Sharding (Split Tests Across Workers)

```yaml
strategy:
  matrix:
    shard: [1/4, 2/4, 3/4, 4/4]
steps:
  - run: npx playwright test --shard=${{ matrix.shard }}
```

### Merge Shard Reports

```bash
npx playwright merge-reports --reporter html ./all-blob-reports
```

### Conditional Browser Installation

```bash
# Install only what you need
npx playwright install --with-deps chromium  # CI: fast
npx playwright install --with-deps           # Full: all browsers
```
