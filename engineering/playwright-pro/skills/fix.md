# Sub-Skill: Fix Failing Tests

**Parent:** playwright-pro
**Trigger:** "fix flaky test", "Playwright test failing", "debug e2e failure"

## Purpose

Diagnose and fix failing or flaky Playwright tests. Uses trace analysis, error pattern matching, and the 10 golden rules to identify root causes and apply fixes.

## Workflow

### Step 1: Reproduce and Classify

Run the failing test with full diagnostics:
```bash
npx playwright test <test-file> --trace on --retries 3 --reporter=list
```

Classify the failure:
- **Deterministic failure:** Fails every time (likely a real bug or broken locator)
- **Flaky failure:** Passes sometimes (timing, state isolation, or environment issue)
- **Environment failure:** Only fails in CI (font rendering, network, resource constraints)

### Step 2: Analyze Trace

Open the trace viewer to inspect the failure point:
```bash
npx playwright show-trace test-results/<test>/trace.zip
```

Check for:
- Element not found at the moment of interaction
- Network request timing vs assertion timing
- Console errors or uncaught exceptions
- Screenshot showing unexpected UI state

### Step 3: Match Error Pattern

| Error Pattern | Root Cause | Fix |
|---------------|-----------|-----|
| `waiting for locator` timeout | Element not rendered or selector wrong | Add `await expect(locator).toBeVisible()` before interaction |
| `strict mode violation` | Multiple elements match locator | Make locator more specific with `.first()`, `.nth()`, or tighter role/name |
| `Target closed` | Page navigated during action | Add `waitForURL()` or `waitForLoadState()` before assertion |
| `net::ERR_CONNECTION_REFUSED` | Dev server not running | Check `webServer` config in `playwright.config.ts` |
| `toHaveScreenshot` mismatch | Visual diff from baseline | Update snapshot or fix the CSS regression |

### Step 4: Apply Fix

Apply the appropriate fix from the pattern table. After fixing:
1. Run the test 5 times locally to confirm stability
2. Run with `--retries 0` to ensure it passes without retries
3. If the fix involved adding a wait, verify it uses web-first assertions (not `waitForTimeout`)

### Step 5: Prevent Recurrence

- Add the failure pattern to team knowledge base
- If the root cause is a common anti-pattern, flag it for the test analyzer

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Test file or name | Yes | The failing test to diagnose |
| Error message | No | The error output (speeds up diagnosis) |
| CI vs local | No | Where the failure occurs |

## Outputs

- Root cause diagnosis with evidence
- Applied fix with explanation
- Stability verification (5x pass confirmation)
