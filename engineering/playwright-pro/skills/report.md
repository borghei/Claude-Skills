# Sub-Skill: Test Execution Reports

**Parent:** playwright-pro
**Trigger:** "generate test report", "summarize test results", "parse Playwright report"

## Purpose

Generate human-readable test execution reports from Playwright JSON output. Includes pass/fail summary, duration stats, flaky test detection, and trend analysis across runs.

## Workflow

### Step 1: Collect Results

Ensure Playwright is configured to output JSON:
```typescript
// playwright.config.ts
reporter: [
  ['html'],
  ['json', { outputFile: 'test-results.json' }],
],
```

### Step 2: Parse Single Run

Use the `test_report_parser.py` script:
```bash
python scripts/test_report_parser.py test-results.json --flaky-threshold 3
```

This produces:
- Pass/fail/flaky/skip counts with visual bar
- Duration breakdown (total, average, P90, slowest)
- Per-project breakdown (chromium, firefox, mobile)
- Flaky test list with attempt counts
- Failed test details with error messages
- Top N slowest tests

### Step 3: Trend Analysis (Multi-Run)

When multiple result files are available, compare across runs:
- Is the flaky rate trending up or down?
- Are specific tests getting slower over time?
- Are new failures appearing in specific browsers?

### Step 4: Generate Verdict

| Condition | Verdict |
|-----------|---------|
| All tests pass, flaky < threshold | PASSED |
| All pass but flaky > threshold | UNSTABLE |
| Any test fails | FAILED |
| Suite > 10 minutes | SLOW |

### Step 5: Distribute

Output formats:
- **Terminal:** Human-readable summary (default)
- **JSON:** Machine-parseable for CI integration
- **Markdown:** For PR comments or Slack notifications

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Report file | Yes | Playwright JSON report |
| Flaky threshold | No | Percentage threshold (default: 5%) |
| Top slow count | No | Number of slowest tests to show (default: 5) |

## Outputs

- Formatted test execution summary
- Flaky test warnings (if above threshold)
- Verdict (PASSED / UNSTABLE / FAILED / SLOW)
