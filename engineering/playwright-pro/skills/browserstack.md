# Sub-Skill: BrowserStack Integration

**Parent:** playwright-pro
**Trigger:** "BrowserStack", "cloud testing", "cross-browser cloud"

## Purpose

Configure Playwright to run tests on BrowserStack's cloud infrastructure for cross-browser and cross-device testing at scale.

## Workflow

### Step 1: Install BrowserStack SDK

```bash
pnpm add -D browserstack-node-sdk
```

### Step 2: Configure BrowserStack

Create `browserstack.yml` in project root:
```yaml
userName: ${BROWSERSTACK_USERNAME}
accessKey: ${BROWSERSTACK_ACCESS_KEY}
platforms:
  - os: Windows
    osVersion: 11
    browserName: Chrome
    browserVersion: latest
  - os: OS X
    osVersion: Sonoma
    browserName: Safari
    browserVersion: latest
  - deviceName: iPhone 15
    osVersion: 17
    browserName: Safari
  - deviceName: Samsung Galaxy S24
    osVersion: 14.0
    browserName: Chrome
parallelsPerPlatform: 2
projectName: "My Project E2E"
buildName: "Build ${BUILD_NUMBER}"
debug: true
networkLogs: true
```

### Step 3: Update Playwright Config

Add BrowserStack-specific project entries or use the SDK's automatic browser provisioning. The SDK wraps `playwright test` and routes browser connections through BrowserStack.

### Step 4: Run on BrowserStack

```bash
npx browserstack-node-sdk playwright test
```

### Step 5: CI Integration

Add BrowserStack credentials as CI secrets and run the cloud suite on a schedule or for release candidates (not every PR -- too slow and expensive).

```yaml
# GitHub Actions
- run: npx browserstack-node-sdk playwright test
  env:
    BROWSERSTACK_USERNAME: ${{ secrets.BROWSERSTACK_USERNAME }}
    BROWSERSTACK_ACCESS_KEY: ${{ secrets.BROWSERSTACK_ACCESS_KEY }}
```

## Best Practices

1. Run cloud tests on a schedule (nightly) or for release candidates, not every commit
2. Keep a fast local suite (Chromium only) for PR feedback loops
3. Use BrowserStack for Safari/IE/mobile-specific validation
4. Set `debug: true` and `networkLogs: true` for failure investigation
5. Tag builds with commit SHA for traceability

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| BrowserStack credentials | Yes | Username and access key |
| Target platforms | No | Defaults to Chrome + Safari + mobile |
| Parallel count | No | Defaults to 2 per platform |

## Outputs

- `browserstack.yml` configuration
- Updated CI workflow with cloud testing step
- Test results on BrowserStack dashboard
