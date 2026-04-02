# Sub-Skill: Test Generation

**Parent:** playwright-pro
**Trigger:** "generate tests for", "write e2e tests", "create Playwright tests from"

## Purpose

Generate Playwright test files from user stories, page descriptions, or API endpoint lists. Produces spec files with Page Objects, proper assertions, and test isolation.

## Workflow

### Step 1: Gather Input

Accept one of:
- **User story:** "As a user, I can log in with email and password"
- **Page description:** "Login page with email field, password field, submit button, forgot password link"
- **URL + selectors:** Crawl a page and extract interactive elements

### Step 2: Identify Test Scenarios

For each input, derive:
- **Happy path:** Primary success flow
- **Validation errors:** Empty fields, invalid formats, boundary values
- **Edge cases:** Network failure, timeout, concurrent sessions
- **Negative paths:** Wrong credentials, expired tokens, unauthorized access

### Step 3: Generate Page Object

If no Page Object exists for the target page, generate one using the locator priority from the parent skill (getByRole > getByLabel > getByText > getByTestId > CSS).

### Step 4: Generate Spec File

```typescript
test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate and set up
  });

  test('happy path description', async ({ page }) => {
    // Arrange, Act, Assert
  });

  test('validation: empty required field', async ({ page }) => {
    // Test validation behavior
  });
});
```

### Step 5: Validate Generated Tests

- Every test has at least one `expect()` assertion
- No `waitForTimeout()` calls
- All locators use semantic strategies
- Tests are isolated (no shared mutable state)

## Rules

1. One behavior per test -- multiple related assertions within a behavior are fine
2. Use Page Object methods, never raw locators in spec files
3. Name tests as "expected behavior when condition" (e.g., "redirects to dashboard after valid login")
4. Group related tests in `test.describe()` blocks
5. Use `test.beforeEach()` for common setup, never shared variables

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Source | Yes | User story, page description, or URL |
| Page name | Yes | Target page for Page Object naming |
| Auth required | No | Whether tests need authenticated state |

## Outputs

- Page Object class (if new)
- Spec file with happy path + error path tests
- Suggested additional test scenarios
