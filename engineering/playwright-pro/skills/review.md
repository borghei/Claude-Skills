# Sub-Skill: Test Quality Review

**Parent:** playwright-pro
**Trigger:** "review test quality", "audit Playwright tests", "check test coverage gaps"

## Purpose

Review a Playwright test suite for quality issues, coverage gaps, anti-patterns, and flaky test indicators. Produces an actionable report with prioritized fixes.

## Workflow

### Step 1: Run Static Analysis

Use the `test_analyzer.py` script to scan for anti-patterns:
```bash
python scripts/test_analyzer.py ./tests/e2e/ --severity low
```

This catches: `waitForTimeout`, CSS/XPath selectors, missing assertions, `force:true` clicks, hardcoded URLs.

### Step 2: Assess Coverage

Map tests to critical user journeys:
- Login / Authentication
- Core CRUD operations
- Checkout / Payment (if applicable)
- Onboarding flow
- Error handling paths

Flag any critical journey without dedicated tests.

### Step 3: Check Flaky Indicators

Review recent CI runs for:
- Tests that needed retries to pass
- Tests with inconsistent durations (>2x variation)
- Tests that were recently disabled or skipped

Use `flaky_detector.py` on CI results:
```bash
python scripts/flaky_detector.py --results-dir ./test-results/ --runs 10
```

### Step 4: Review Architecture

- Every tested page has a Page Object class
- No raw locators in spec files
- `test.describe()` groups are logical
- Fixtures used for shared setup (not global variables)
- Auth setup project configured (not per-test login)

### Step 5: Generate Report

Produce a prioritized report:
1. **Critical:** Tests with no assertions, hardcoded waits, flaky tests above 5% rate
2. **High:** Missing coverage for critical user journeys
3. **Medium:** CSS selectors that should be semantic, missing Page Objects
4. **Low:** Style inconsistencies, test naming conventions

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Test directory | Yes | Path to Playwright test files |
| CI results | No | Recent test result JSON files for flaky analysis |
| User journeys | No | List of critical flows to check coverage against |

## Outputs

- Anti-pattern report with line-level findings
- Coverage gap analysis
- Flaky test list with stability scores
- Prioritized fix recommendations
