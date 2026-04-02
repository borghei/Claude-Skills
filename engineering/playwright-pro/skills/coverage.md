# Sub-Skill: Test Coverage Analysis

**Parent:** playwright-pro
**Trigger:** "analyze test coverage", "map tests to user flows", "coverage gaps"

## Purpose

Map Playwright tests to user stories and requirements. Identify coverage gaps by comparing what is tested against what should be tested based on critical user flows.

## Workflow

### Step 1: Define User Flows

Enumerate critical user journeys. Each flow has:
- **ID:** Unique identifier (e.g., `AUTH-001`)
- **Name:** Human-readable name (e.g., "User login with email")
- **Priority:** Critical / High / Medium / Low
- **Steps:** Ordered list of user actions

### Step 2: Inventory Tests

Scan the test directory and extract:
- Test file paths and describe block names
- Individual test names
- Page Objects referenced
- URLs navigated to

### Step 3: Map Tests to Flows

Use `coverage_mapper.py` to match tests against flows:
```bash
python scripts/coverage_mapper.py --tests ./tests/e2e/ --flows flows.json
```

Matching heuristics:
- Test name contains flow keywords
- Test navigates to flow-related URLs
- Test uses Page Objects for flow pages
- Test assertions match expected flow outcomes

### Step 4: Identify Gaps

For each critical flow without test coverage:
- Generate a recommended test outline
- Estimate effort to implement
- Prioritize by flow criticality

### Step 5: Report

Output a coverage matrix:

| Flow | Priority | Tests | Status |
|------|----------|-------|--------|
| AUTH-001 Login | Critical | login.spec.ts (3 tests) | Covered |
| AUTH-002 Password reset | Critical | -- | GAP |
| CHECKOUT-001 Purchase | Critical | checkout.spec.ts (5 tests) | Covered |

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Test directory | Yes | Path to Playwright test files |
| Flows definition | Yes | JSON file defining critical user flows |

## Outputs

- Coverage matrix (flows vs tests)
- Gap list with recommended test outlines
- Coverage percentage by priority tier
