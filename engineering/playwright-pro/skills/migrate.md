# Sub-Skill: Migration from Cypress/Selenium

**Parent:** playwright-pro
**Trigger:** "migrate from Cypress", "convert Selenium tests", "switch to Playwright"

## Purpose

Migrate an existing Cypress or Selenium test suite to Playwright. Handles API translation, pattern modernization, and validation of migrated tests.

## Workflow

### Step 1: Audit Existing Suite

Inventory the current test suite:
- Count of test files and test cases
- Frameworks used (Cypress, Selenium WebDriver, Protractor, TestCafe)
- Custom commands and plugins in use
- CI integration points
- Test data management approach

### Step 2: Translate API Calls

Apply the translation table from the parent SKILL.md. Key mappings:

**Cypress to Playwright:**
- `cy.visit()` -> `page.goto()`
- `cy.get()` -> `page.locator()` (then upgrade to `getByRole`)
- `cy.contains()` -> `page.getByText()`
- `cy.intercept()` -> `page.route()`
- `cy.should('be.visible')` -> `expect(locator).toBeVisible()`
- Custom commands -> Page Object methods or fixtures

**Selenium to Playwright:**
- `driver.findElement(By.css())` -> `page.locator()`
- `driver.findElement(By.xpath())` -> `page.getByRole()` (eliminate XPath)
- `WebDriverWait` -> web-first assertions (auto-retry)
- `driver.get()` -> `page.goto()`

### Step 3: Modernize Patterns

During migration, upgrade patterns:
1. Replace CSS/XPath selectors with semantic locators
2. Replace explicit waits with web-first assertions
3. Extract Page Objects from inline locators
4. Replace custom retry logic with Playwright's built-in retries
5. Convert fixture files to proper test data management

### Step 4: Validate Migration

For each migrated test:
1. Run and confirm it passes
2. Compare behavior with the original test
3. Check that no `waitForTimeout` was introduced
4. Verify locator strategy follows priority order

### Step 5: Remove Old Framework

After all tests are migrated and passing:
1. Remove old framework dependencies
2. Update CI configuration
3. Remove old config files (cypress.config.js, etc.)
4. Update documentation and contributing guides

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Source framework | Yes | Cypress, Selenium, Protractor, or TestCafe |
| Test directory | Yes | Path to existing test files |
| Priority | No | Migrate all at once or incrementally |

## Outputs

- Migrated Playwright test files
- New Page Object classes
- Updated playwright.config.ts
- Migration report (tests migrated, patterns upgraded, issues found)
