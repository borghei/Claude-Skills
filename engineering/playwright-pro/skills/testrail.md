# Sub-Skill: TestRail Integration

**Parent:** playwright-pro
**Trigger:** "TestRail", "test management", "sync test results to TestRail"

## Purpose

Integrate Playwright test execution with TestRail for test case management, run tracking, and reporting. Sync test results automatically from CI.

## Workflow

### Step 1: Install Reporter

```bash
pnpm add -D playwright-testrail-reporter
```

### Step 2: Configure Reporter

Add TestRail reporter to `playwright.config.ts`:
```typescript
reporter: [
  ['html'],
  ['playwright-testrail-reporter', {
    host: process.env.TESTRAIL_HOST,
    username: process.env.TESTRAIL_USERNAME,
    password: process.env.TESTRAIL_API_KEY,
    projectId: 1,
    suiteId: 1,
    runName: `Automated Run - ${new Date().toISOString()}`,
    includeAllInTestRun: false,
  }],
],
```

### Step 3: Map Tests to TestRail Cases

Add TestRail case IDs to test titles or annotations:
```typescript
// Option A: In test title
test('C12345 - User can log in with valid credentials', async ({ page }) => {
  // ...
});

// Option B: Via annotation
test('User can log in', async ({ page }) => {
  test.info().annotations.push({ type: 'testrail', description: 'C12345' });
  // ...
});
```

### Step 4: Sync Results

When tests run in CI, the reporter automatically:
1. Creates a new test run in TestRail (or updates existing)
2. Maps Playwright test results to TestRail case IDs
3. Uploads pass/fail status with execution time
4. Attaches failure messages and screenshots

### Step 5: CI Configuration

```yaml
- run: pnpm exec playwright test
  env:
    TESTRAIL_HOST: ${{ secrets.TESTRAIL_HOST }}
    TESTRAIL_USERNAME: ${{ secrets.TESTRAIL_USERNAME }}
    TESTRAIL_API_KEY: ${{ secrets.TESTRAIL_API_KEY }}
```

## Best Practices

1. Use TestRail case IDs consistently (prefix `C` + number)
2. Map every automated test to a TestRail case for full traceability
3. Keep manual-only test cases separate from automated ones in TestRail
4. Use TestRail milestones to group runs by release
5. Review unmapped tests periodically -- they indicate coverage drift

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| TestRail credentials | Yes | Host, username, API key |
| Project and suite IDs | Yes | TestRail project/suite to sync to |
| Case ID mapping | Yes | Test-to-case ID mapping (in titles or annotations) |

## Outputs

- TestRail reporter configured in Playwright
- Test runs created and synced automatically
- Pass/fail results with failure details in TestRail
