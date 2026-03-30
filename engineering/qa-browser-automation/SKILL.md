---
name: qa-browser-automation
description: >
  Production-grade browser QA automation with visual regression testing,
  accessibility auditing, performance profiling, and intelligent bug triage
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: engineering
  domain: quality-assurance
  updated: 2026-03-18
  tags: [browser-qa, wcag, visual-regression, health-scoring]
  python-tools: qa_health_scorer.py, accessibility_auditor.py, visual_regression_tracker.py, test_report_generator.py
  tech-stack: python, chrome-mcp, accessibility, wcag, performance
---
# QA Browser Automation

The most comprehensive browser QA skill available for AI coding assistants. Combines live Chrome MCP browser control with deterministic Python analysis tools to deliver systematic, repeatable quality assurance across any web application.

**What sets this apart:** Four testing tiers, 10-category weighted health scoring, five severity levels, WCAG 2.1 AAA coverage, visual regression tracking, Core Web Vitals profiling, and full Python automation — all integrated with live browser interaction via Chrome MCP.

---

## Keywords

browser-testing, qa-automation, visual-regression, accessibility-audit, wcag-compliance, performance-profiling, core-web-vitals, health-scoring, bug-triage, chrome-mcp, cross-browser, responsive-testing, e2e-testing, smoke-testing, regression-testing

---

## Table of Contents

- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
  - [1. Full Application QA Sweep](#1-full-application-qa-sweep)
  - [2. Visual Regression Testing](#2-visual-regression-testing)
  - [3. Accessibility Compliance Audit](#3-accessibility-compliance-audit)
  - [4. Performance Profiling](#4-performance-profiling)
  - [5. Diff-Aware QA](#5-diff-aware-qa)
- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Testing Tiers](#testing-tiers)
- [Health Scoring System](#health-scoring-system)
- [Bug Severity Classification](#bug-severity-classification)
- [Integration Points](#integration-points)

---

## Quick Start

1. **Navigate to target application** using Chrome MCP (`mcp__claude-in-chrome__navigate`)
2. **Choose a testing tier** — Quick (30s), Standard (2-5min), Deep (10-20min), or Exhaustive (30min+)
3. **Run the appropriate workflow** from the Core Workflows section below
4. **Generate report** using `test_report_generator.py` with collected findings

```bash
# Score findings after a QA session
python scripts/qa_health_scorer.py findings.json

# Audit a page for accessibility
python scripts/accessibility_auditor.py page.html --level AA

# Track visual regressions
python scripts/visual_regression_tracker.py --baseline baselines/ --current screenshots/

# Generate full report
python scripts/test_report_generator.py session_data.json --format markdown -o report.md
```

---

## Core Workflows

### 1. Full Application QA Sweep (11-Phase Protocol)

Fully prescriptive, phase-gated QA workflow. Each phase must complete before the next begins.

**Phase 1 — Pre-Flight**
- Verify `git status` is clean (no uncommitted changes). **Abort if dirty.**
- Create session directory: `.qa-sessions/{timestamp}/`
- Record starting branch, commit hash, and timestamp
- Check if a previous baseline exists for regression comparison

**Phase 2 — Authenticate**
- If the application requires login, handle authentication first
- Use `mcp__claude-in-chrome__form_input` to fill credentials
- Verify session established via `mcp__claude-in-chrome__read_console_messages`
- Store auth state for subsequent phases

**Phase 3 — Orient**
- Use `mcp__claude-in-chrome__read_page` to capture the sitemap or navigation structure
- Enumerate all unique routes, modals, and dynamic views
- Identify authentication gates and role-based views
- Detect framework (React, Vue, Next.js, etc.) from page source
- Build the page map — this drives all subsequent testing

**Phase 4 — Systematic Exploration**
- Navigate each route with `mcp__claude-in-chrome__navigate`
- Check `mcp__claude-in-chrome__read_console_messages` for errors and warnings
- Verify all pages render without HTTP 4xx/5xx via `mcp__claude-in-chrome__read_network_requests`
- Test all forms with `mcp__claude-in-chrome__form_input` — valid data, empty submissions, boundary values
- Exercise interactive elements: dropdowns, modals, tabs, accordions, tooltips
- Verify CRUD operations complete successfully
- Test navigation flows: login, onboarding, checkout, multi-step wizards

**Phase 5 — State Testing**
- Verify loading states (skeleton screens, spinners — not blank pages)
- Check empty states (no data, first-time user — must guide to first action)
- Trigger error states (invalid input, network failure simulation)
- Confirm success states (toast notifications, redirects, confirmation screens)
- Test partial states (incomplete data, pagination boundaries, stale cache)
- **Four shadow paths per interaction:** happy path, nil input, empty input, error upstream

**Phase 6 — Cross-Device & Security**
- Use `mcp__claude-in-chrome__resize_window` to test at 320px, 768px, 1024px, 1440px, 1920px
- Verify responsive breakpoints, touch targets (44x44px minimum), and layout shifts
- Check security headers via network requests (CSP, HSTS, X-Frame-Options)
- Test for open redirects, XSS reflection in URL params
- Verify CSRF tokens on forms, cookie flags (Secure, HttpOnly, SameSite)

**Phase 7 — Document**
- Record every finding immediately with screenshot evidence
- Use `mcp__claude-in-chrome__computer` to capture visual state
- Classify each finding by severity (P0-P4) and category (10 categories)
- Save findings incrementally to `.qa-sessions/{timestamp}/findings.json`
- **Rule:** No finding exists without evidence. Screenshots are mandatory.

**Phase 8 — Score**
- Run `python scripts/qa_health_scorer.py findings.json` to compute health score
- If baseline exists, include `--baseline .qa-baselines/latest.json` for trend comparison
- Record score in session artifacts

**Phase 9 — Triage & Fix Loop**
- Sort findings by severity (P0 first, P4 last)
- For each finding (respecting safety controls — see Safety Controls section):
  - P3/P4: AUTO-FIX — apply fix, commit atomically, verify
  - P0/P1/P2: ASK — present finding with evidence, propose fix, wait for approval
  - After each fix: re-run the specific check to verify the fix works
  - If fix fails verification: `git revert` and move to next finding
- **Hard stop at 50 fixes** regardless of remaining findings

**Phase 10 — Regression Check**
- Re-visit pages affected by fixes
- Verify no new console errors, broken links, or visual regressions
- Run `mcp__claude-in-chrome__read_console_messages` and `read_network_requests` on fixed pages
- If new P0/P1 found: revert the causing commit and flag

**Phase 11 — Report & Baseline Update**
- Generate comprehensive report: `python scripts/test_report_generator.py session.json`
- Save health score as new baseline: `--save-baseline`
- Output: session directory with findings, scores, screenshots, fixes log, and final report
- Print summary: score, grade, findings by severity, fixes applied, regressions (if any)

### 2. Visual Regression Testing

Before/after screenshot comparison to catch unintended visual changes.

**Setup Baseline**
```bash
# Initialize baseline manifest
python scripts/visual_regression_tracker.py --init --baseline-dir ./baselines
```

**Capture Baselines**
- Use `mcp__claude-in-chrome__upload_image` or screenshot tools to capture each page
- Store screenshots organized by route: `baselines/home.png`, `baselines/dashboard.png`
- Register in manifest: `python scripts/visual_regression_tracker.py --register baselines/`

**Run Comparison**
```bash
# After code changes, capture new screenshots and compare
python scripts/visual_regression_tracker.py --baseline baselines/ --current screenshots/ --threshold 5
```

**Review Diffs**
- Pages exceeding the threshold (default 5%) are flagged as regressions
- Review diff report to accept intentional changes or file bugs for unintended ones
- Update baselines for accepted changes: `--update-baseline`

### 3. Accessibility Compliance Audit

WCAG 2.1 compliance checking across three conformance levels.

**Automated Checks**
```bash
# Get page HTML via Chrome MCP, save to file, then audit
python scripts/accessibility_auditor.py page.html --level AA --json
```

**What Gets Checked**
- **Level A (Must Fix):** Alt text, page language, form labels, heading presence, duplicate IDs, auto-playing media
- **Level AA (Should Fix):** Color contrast (4.5:1 text, 3:1 large), heading hierarchy, focus visible, error identification, resize to 200%
- **Level AA (Should Fix):** Link purpose, consistent navigation, input purpose
- **Level AAA (Nice to Have):** Enhanced contrast (7:1), sign language, extended audio, reading level

**Browser-Assisted Checks**
- Use `mcp__claude-in-chrome__javascript_tool` to run focus-order tests
- Tab through all interactive elements to verify keyboard accessibility
- Check ARIA roles and live regions with JS inspection

**Reporting**
- Each violation includes: WCAG criterion, severity, element selector, remediation guidance
- Summary shows compliance percentage per level

### 4. Performance Profiling

Core Web Vitals measurement and network analysis.

**Capture Metrics**
- Use `mcp__claude-in-chrome__read_network_requests` to capture waterfall data
- Use `mcp__claude-in-chrome__javascript_tool` to extract performance timing:
  ```javascript
  JSON.stringify(performance.getEntriesByType('navigation')[0])
  ```
- Measure CLS, LCP, FID/INP from Performance Observer data

**Analyze Results**
- Compare against thresholds in `references/performance_benchmarks.md`
- Identify blocking resources, excessive bundle sizes, unoptimized images
- Check for memory leaks via heap snapshot comparison
- Verify caching headers on static assets

**Mobile Performance**
- Resize to mobile viewport and re-measure
- Check for lazy loading on below-fold images
- Verify touch responsiveness and input latency

### 5. Diff-Aware QA

Git-based change detection for targeted, efficient testing.

**Step 1 — Detect Changes**
```bash
git diff --name-only main...HEAD
```

**Step 2 — Map Changes to Routes**
- Component file changes map to specific pages/routes
- API changes map to features consuming those endpoints
- Style changes map to visual regression candidates
- Config changes trigger broader smoke testing

**Step 3 — Targeted Testing**
- Only test routes affected by the diff
- Run visual regression on changed pages only
- Accessibility audit on modified components
- Full suite if infrastructure files changed (webpack, package.json, CI config)

**Step 4 — Risk Assessment**
- Changes to auth/payment/data-mutation get automatic Deep tier
- Style-only changes get Quick tier visual regression
- New routes get Standard tier full workflow

---

## Tools

### QA Health Scorer — `scripts/qa_health_scorer.py`

Computes a weighted health score (0-100) from QA findings across 10 categories.

```bash
# Basic scoring
python scripts/qa_health_scorer.py findings.json

# JSON output for CI integration
python scripts/qa_health_scorer.py findings.json --json

# Compare against baseline
python scripts/qa_health_scorer.py findings.json --baseline previous_score.json

# Set custom passing threshold
python scripts/qa_health_scorer.py findings.json --threshold 80
```

### Accessibility Auditor — `scripts/accessibility_auditor.py`

Analyzes HTML for WCAG 2.1 violations across all three conformance levels.

```bash
# Audit at AA level (default)
python scripts/accessibility_auditor.py page.html

# Audit at AAA level with JSON output
python scripts/accessibility_auditor.py page.html --level AAA --json

# Audit from stdin (pipe from curl)
curl -s https://example.com | python scripts/accessibility_auditor.py - --level A
```

### Visual Regression Tracker — `scripts/visual_regression_tracker.py`

Manages screenshot baselines and detects visual regressions between test runs.

```bash
# Initialize baseline directory
python scripts/visual_regression_tracker.py --init --baseline-dir ./baselines

# Register screenshots as baselines
python scripts/visual_regression_tracker.py --register ./baselines

# Compare current against baseline
python scripts/visual_regression_tracker.py --baseline ./baselines --current ./screenshots

# Custom threshold (default 5%)
python scripts/visual_regression_tracker.py --baseline ./baselines --current ./screenshots --threshold 3

# Update baseline with current screenshots
python scripts/visual_regression_tracker.py --update-baseline --baseline ./baselines --current ./screenshots
```

### Test Report Generator — `scripts/test_report_generator.py`

Generates comprehensive QA reports from session data.

```bash
# Markdown report (default)
python scripts/test_report_generator.py session_data.json

# JSON summary
python scripts/test_report_generator.py session_data.json --format json

# Write to file
python scripts/test_report_generator.py session_data.json --format markdown -o report.md

# Include trend data
python scripts/test_report_generator.py session_data.json --history scores_history.json
```

---

## Reference Guides

| Guide | Location | Content |
|-------|----------|---------|
| Browser Testing Methodology | `references/browser_testing_methodology.md` | Page exploration strategies, element interaction patterns, state testing, auth flows |
| WCAG Compliance Guide | `references/wcag_compliance_guide.md` | WCAG 2.1 A/AA/AAA requirements, common violations, testing techniques |
| Performance Benchmarks | `references/performance_benchmarks.md` | Core Web Vitals thresholds, network analysis, memory profiling, mobile considerations |

---

## Testing Tiers

### Quick (30 seconds)
- Console error check on current page
- Broken link scan (current page only)
- Basic accessibility check (alt text, headings)
- Viewport resize to mobile and back

### Standard (2-5 minutes)
- All Quick checks plus:
- Navigate top 5-10 routes, check console and network
- Form validation on primary forms
- Heading hierarchy and color contrast audit
- Core Web Vitals capture on landing page

### Deep (10-20 minutes)
- All Standard checks plus:
- Full sitemap traversal
- State testing (empty, error, loading, success, partial)
- Complete WCAG AA audit
- Performance profiling on 3 key pages
- Visual regression on changed pages
- Security header verification

### Exhaustive (30+ minutes)
- All Deep checks plus:
- Every interactive element exercised
- WCAG AAA audit
- Performance profiling on all pages
- Full visual regression suite
- Cross-device testing at 5 breakpoints
- Authentication flow edge cases
- Third-party integration verification
- Memory leak detection via repeated navigation

---

## Health Scoring System

Score range: **0-100** computed from 10 weighted categories.

| Category | Weight | What It Measures |
|----------|--------|------------------|
| Console Errors | 12% | JavaScript errors, unhandled rejections, deprecation warnings |
| Broken Links | 8% | HTTP 4xx/5xx responses, dead anchors, missing assets |
| Visual Consistency | 10% | Layout shifts, overflow, alignment, z-index issues |
| Functional | 18% | Forms work, CRUD operations complete, navigation flows succeed |
| UX Flow | 12% | Logical navigation, clear feedback, expected behavior |
| Performance | 12% | Core Web Vitals within thresholds, fast load times |
| Content Quality | 5% | Spelling, placeholder text, lorem ipsum, truncation |
| Accessibility | 13% | WCAG compliance, keyboard navigation, screen reader support |
| Security Headers | 5% | CSP, HSTS, X-Frame-Options, cookie flags |
| Mobile Responsive | 5% | Breakpoints work, touch targets adequate, no horizontal scroll |

**Grading Scale:**
- **A (90-100):** Production-ready, no critical issues
- **B (80-89):** Ship with minor fixes planned
- **C (70-79):** Needs attention before release
- **D (60-69):** Significant issues, delay recommended
- **F (0-59):** Critical failures, do not ship

**Deduction System by Severity:**
- P0 Critical: -30 points per finding
- P1 High: -18 points per finding
- P2 Medium: -10 points per finding
- P3 Low: -4 points per finding
- P4 Cosmetic: -1 point per finding

Deductions are distributed proportionally across their applicable categories. Score floors at 0.

---

## Bug Severity Classification

### P0 — Critical
Application crash, data loss, security vulnerability, payment failure, complete feature broken. **Must fix before any release.** Examples: white screen of death, XSS vulnerability, checkout sends wrong amount, auth bypass.

### P1 — High
Major feature partially broken, significant UX degradation, accessibility blocker, performance regression >50%. **Must fix within current sprint.** Examples: form silently drops data, keyboard users cannot complete core flow, LCP >8s.

### P2 — Medium
Feature works but with friction, moderate visual issues, accessibility violation (AA), performance below threshold. **Fix within next 2 sprints.** Examples: date picker requires manual format, contrast ratio 3.5:1 on body text, CLS >0.25.

### P3 — Low
Minor inconvenience, cosmetic issue with workaround, accessibility nice-to-have, slight performance gap. **Backlog prioritization.** Examples: tooltip misaligned by 2px on hover, alt text could be more descriptive, TTFB 900ms.

### P4 — Cosmetic
Purely visual polish, no functional impact, enhancement opportunity. **Fix when convenient.** Examples: inconsistent border-radius across cards, font-weight 500 vs 600 inconsistency, extra whitespace in footer.

---

## Safety Controls & Self-Regulation

Production QA requires guardrails to prevent runaway fixes from destabilizing the codebase.

### Fix Session Limits
- **Maximum 50 fixes per session** — hard stop. After 50 fixes, generate report and exit regardless of remaining findings.
- **Risk accumulator** — each fix increments a risk score: component file changes (+5), style changes (+2), config changes (+8), reverts (+15). **Stop if cumulative risk exceeds 25%** of total risk budget (100).
- **Revert protocol** — if a fix introduces a new P0 or P1 finding (verified by re-running the affected check), immediately `git revert` the commit and flag for manual review.
- **WTF-likelihood heuristic** — if 3 consecutive fixes fail verification after commit, stop the fix loop entirely and report. The codebase likely has a systemic issue that individual fixes cannot address.

### Pre-Conditions
- **Clean working tree required** — refuse to start if `git status` shows uncommitted changes. This ensures every fix is a clean, revertible commit.
- **Branch verification** — warn if running on `main` or `master`. QA fix sessions should run on feature branches.

### Atomic Commits
Every fix produces exactly one commit:
```
fix(qa): [P{severity}] {short description}

Finding: {original finding description}
Evidence: {screenshot reference or console output}
Verified: {pass|fail} after fix applied
```

### Interaction Model
- **AUTO-FIX (no confirmation):** P3 (Low) and P4 (Cosmetic) — spacing, typos, minor style fixes
- **ASK (requires confirmation):** P0, P1, P2 — structural changes, logic fixes, accessibility remediation
- **One issue = one question** — never batch multiple findings into a single prompt. Each fix decision is independent.
- **Rollback instruction** — every ASK includes: what changes, why, evidence, and exact `git revert <hash>` command

---

## State Persistence & Trend Tracking

### Baseline Management
Save health scores after each session for regression comparison:

```bash
# Save current score as baseline
python scripts/qa_health_scorer.py findings.json --save-baseline

# Compare against saved baseline
python scripts/qa_health_scorer.py findings.json --baseline .qa-baselines/latest.json
```

**Storage:** `.qa-baselines/{YYYY-MM-DD}.json` — contains score, grade, category breakdown, finding counts, timestamp.

### Regression Mode
Compare current run against a saved baseline to detect regressions:
1. Run full QA sweep → generate findings JSON
2. Score findings with `--baseline` flag pointing to previous run
3. Report delta: categories that improved, degraded, or held steady
4. Flag any category that dropped >10 points as a regression warning

### Session Artifacts
Each QA session creates a directory: `.qa-sessions/{timestamp}/`
- `findings.json` — all findings from this session
- `health_score.json` — scored results
- `screenshots/` — evidence screenshots (if using Chrome MCP)
- `report.md` — generated markdown report
- `fixes.log` — list of commits made during fix loop

### Trend Dashboard
After 3+ sessions, the scorer can generate trend analysis:
- Week-over-week health score trajectory
- Most frequently failing categories
- Persistent findings that recur across sessions
- Estimated time to reach target score

---

## Integration Points

| Skill | Integration |
|-------|-------------|
| `code-reviewer` | Feed QA findings into PR review context for informed approval decisions |
| `senior-frontend` | Visual regression baselines align with component library standards |
| `senior-devops` | Health scores gate CI/CD deployment pipelines (threshold check) |
| `senior-secops` | Security header findings escalate to security review workflow |
| `incident-commander` | P0 findings trigger incident response if found in production |
| `senior-qa` | Extends manual QA checklist with automated browser verification |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Health scorer exits with code 1 but no errors printed | Score fell below the `--threshold` value (default 70) | Check the score in the report output; raise with `--threshold 50` if intentional, or fix findings to increase the score |
| Accessibility auditor reports `parse-error` violation | Malformed or truncated HTML fed to the auditor | Ensure the HTML file is complete and well-formed; if piping from `curl`, verify the response is not a redirect or error page |
| Visual regression tracker shows 100% change on all pages | Baseline manifest is empty or was never initialized | Run `--init --baseline-dir ./baselines` followed by `--register ./baselines` before comparing |
| Visual regression reports `baseline_missing` for known pages | Screenshot filenames changed between runs (e.g., route slug renamed) | Re-register baselines with `--register` after renaming, or use `--update-baseline` to refresh from current screenshots |
| Findings JSON loads but all findings default to P3/functional | Finding objects missing `severity` or `category` keys | Ensure each finding dict includes `"severity": "P0"-"P4"` and `"category"` matching one of the 10 scoring categories |
| Test report generator produces empty Findings section | Session JSON has findings at the top level instead of under a `"findings"` key | Structure the session JSON with a `"findings"` array; see the expected schema in `test_report_generator.py` docstring |
| Chrome MCP `read_page` returns stale content after SPA navigation | Single-page app updated the DOM without a full page load | Wait for the SPA transition to complete, then call `mcp__claude-in-chrome__read_page` again; use `read_console_messages` to confirm the route change landed |

---

## Success Criteria

- **Health score above 85/100** on the target application after a Standard-tier sweep, indicating ship-ready quality with only minor issues remaining.
- **Zero P0 (Critical) findings** at the end of the QA session; any P0 discovered during the sweep must be resolved or escalated before the session closes.
- **WCAG AA compliance at or above 95%** as reported by `accessibility_auditor.py`, with zero `must-fix` violations remaining.
- **Visual regression pass rate of 100%** against the established baseline at the configured threshold (default 5%), confirming no unintended visual changes.
- **All Core Web Vitals within "Good" thresholds** — LCP under 2.5s, CLS below 0.1, INP under 200ms — on at least the three highest-traffic pages.
- **Fewer than 5 P2 (Medium) findings** remaining after the triage-and-fix loop, demonstrating that functional friction has been addressed.
- **Trend line stable or improving** across consecutive sessions; no category drops more than 10 points compared to the previous baseline.

---

## Scope & Limitations

**This skill covers:**

- End-to-end browser QA via Chrome MCP: navigation, form interaction, console monitoring, network inspection, responsive testing, and screenshot capture.
- Static HTML accessibility auditing against WCAG 2.1 levels A, AA, and AAA using deterministic Python checks (no external services required).
- Visual regression tracking through file-hash comparison and byte-level diff analysis with configurable thresholds.
- Weighted health scoring across 10 quality categories with severity-based deductions, baseline trend tracking, and CI-friendly exit codes.

**This skill does NOT cover:**

- Cross-browser testing beyond Chrome (Safari, Firefox, Edge). For multi-browser matrix testing, integrate with `senior-devops` CI pipeline skills.
- Pixel-perfect image diffing or perceptual hashing — the visual regression tracker uses byte-level comparison, not computer-vision-based diffing. For advanced visual AI comparison, pair with `senior-computer-vision`.
- Backend API testing, database validation, or load/stress testing. Use `senior-backend` for API contract verification and `senior-devops` for load testing infrastructure.
- Runtime color contrast computation from rendered CSS. The accessibility auditor flags inline-style risk patterns and recommends manual verification; it does not compute contrast ratios from computed styles.

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `code-reviewer` | Feed the health score and findings summary into PR review context so reviewers can make informed approval decisions | QA session `report.md` or `--json` output attached to the PR body or review comment |
| `senior-frontend` | Visual regression baselines align with component library standards; baseline updates happen alongside design system releases | `visual_regression_tracker.py` baseline directory shared in the component library repo |
| `senior-devops` | Health score gates CI/CD deployment pipelines via the scorer's non-zero exit code on threshold failure | `qa_health_scorer.py --threshold 80 --json` runs as a pipeline step; exit code 1 blocks deploy |
| `senior-secops` | Security header findings (CSP, HSTS, X-Frame-Options) from the QA sweep escalate to the security review workflow | P0/P1 findings with `category: security_headers` forwarded to the secops triage queue |
| `incident-commander` | P0 findings discovered on production URLs trigger the incident response protocol | P0 finding JSON payload sent to the incident channel with evidence screenshots |
| `senior-qa` | Extends manual QA checklists with automated browser verification; manual testers review automated findings and add exploratory context | `test_report_generator.py` markdown report used as the starting point for manual QA sign-off |

---

## Tool Reference

### qa_health_scorer.py

**Purpose:** Computes a weighted health score (0-100) from QA findings across 10 categories. Produces a letter grade (A-F), supports trend tracking against previous baselines, and returns a non-zero exit code when the score falls below the passing threshold.

**Usage:**

```bash
python scripts/qa_health_scorer.py <findings_file> [options]
```

**Parameters:**

| Flag / Argument | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `findings_file` | positional | Yes | — | Path to a JSON file containing QA findings (array of finding objects, or an object with a `"findings"` key) |
| `--json` | flag | No | off | Output results as machine-readable JSON instead of the human-readable text report |
| `--baseline` | string | No | `None` | Path to a previous score JSON file for trend comparison (computes delta and direction) |
| `--threshold` | int | No | `70` | Minimum passing score; the tool exits with code 1 if the score falls below this value |
| `--save-baseline` | flag | No | off | Save the current score to `.qa-baselines/{YYYY-MM-DD}.json` and `.qa-baselines/latest.json` for future trend comparison |

**Example:**

```bash
# Score findings with an 85-point threshold, compare against last run, save result as new baseline
python scripts/qa_health_scorer.py findings.json --threshold 85 --baseline .qa-baselines/latest.json --save-baseline --json
```

**Output Formats:**

- **Human-readable (default):** Tabular report with overall score, grade, pass/fail status, severity breakdown, category breakdown with weights/scores/findings, and priority areas for categories scoring below 70%.
- **JSON (`--json`):** Object with keys `overall_score`, `grade`, `passed`, `threshold`, `timestamp`, `severity_summary`, `total_findings`, `categories` (per-category weight, score_pct, deductions, finding_counts), and optional `trend`.

---

### accessibility_auditor.py

**Purpose:** Analyzes HTML content for WCAG 2.1 violations across conformance levels A, AA, and AAA. Detects missing alt text, page language, heading hierarchy issues, duplicate IDs, unlabeled form inputs, empty link text, media without captions, autoplay media, missing landmark regions, positive tabindex values, focus indicator removal, and inline color contrast risk patterns. Returns a non-zero exit code when must-fix violations are present.

**Usage:**

```bash
python scripts/accessibility_auditor.py <html_file> [options]
```

**Parameters:**

| Flag / Argument | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `html_file` | positional | Yes | — | Path to an HTML file to audit; use `"-"` to read from stdin |
| `--level` | choice | No | `AA` | WCAG conformance level to check: `A`, `AA`, or `AAA` |
| `--json` | flag | No | off | Output results as JSON instead of the human-readable text report |

**Example:**

```bash
# Audit a page at AAA level, output JSON for downstream processing
curl -s https://example.com | python scripts/accessibility_auditor.py - --level AAA --json
```

**Output Formats:**

- **Human-readable (default):** Report with level checked, elements checked, total violations, compliance percentage, violations broken down by level and severity, and a numbered list of each violation with rule ID, WCAG criterion, issue description, element, and remediation guidance.
- **JSON (`--json`):** Object with keys `level_checked`, `total_elements_checked`, `total_violations`, `compliance_percentage`, `by_level`, `by_severity`, and `violations` (array of objects each containing `rule_id`, `wcag_criterion`, `level`, `severity`, `message`, `element`, `selector_hint`, `remediation`).

---

### visual_regression_tracker.py

**Purpose:** Manages screenshot baselines and detects visual regressions between test runs. Maintains a JSON manifest of baseline screenshots with SHA-256 file hashes. Compares current screenshots against baselines using byte-level analysis and flags pages exceeding a configurable change threshold. Returns a non-zero exit code when regressions are detected.

**Usage:**

```bash
python scripts/visual_regression_tracker.py [action] [options]
```

**Parameters:**

| Flag / Argument | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `--init` | flag | No | off | Initialize a new baseline directory with an empty manifest |
| `--register` | string (DIR) | No | — | Scan the given directory and register all image files (png, jpg, jpeg, bmp, gif, webp) in the baseline manifest |
| `--update-baseline` | flag | No | off | Copy current screenshots into the baseline directory and update the manifest |
| `--baseline-dir` / `--baseline` | string | Conditional | — | Path to the baseline screenshot directory (required for `--init`, comparison, and `--update-baseline`) |
| `--current` | string | Conditional | — | Path to the current screenshot directory (required for comparison and `--update-baseline`) |
| `--threshold` | float | No | `5.0` | Change percentage threshold above which a page is flagged as a regression |
| `--json` | flag | No | off | Output results as JSON instead of the human-readable text report |

**Example:**

```bash
# Initialize, register baselines, then compare with a tight 2% threshold
python scripts/visual_regression_tracker.py --init --baseline-dir ./baselines
python scripts/visual_regression_tracker.py --register ./baselines
python scripts/visual_regression_tracker.py --baseline ./baselines --current ./screenshots --threshold 2 --json
```

**Output Formats:**

- **Human-readable (default):** Report with timestamp, threshold, counts of compared/passed/failed/new/missing pages, overall pass/fail result, and per-page status with change percentages.
- **JSON (`--json`):** Object with keys `timestamp`, `threshold`, `baseline_dir`, `current_dir`, `pages` (per-page status, change_pct, hashes, sizes), and `summary` (total_compared, passed, failed, new_pages, missing_pages).

---

### test_report_generator.py

**Purpose:** Generates comprehensive QA reports from session data. Consumes a JSON file containing findings, health scores, accessibility results, performance metrics, and visual regression data, then produces a detailed markdown or JSON report with executive summary, health score dashboard, category breakdown, findings grouped by severity, accessibility and performance sections, visual regression results, and prioritized recommendations.

**Usage:**

```bash
python scripts/test_report_generator.py <session_file> [options]
```

**Parameters:**

| Flag / Argument | Type | Required | Default | Description |
|-----------------|------|----------|---------|-------------|
| `session_file` | positional | Yes | — | Path to the QA session data JSON file (expected keys: `project`, `url`, `tester`, `tier`, `findings`, and optionally `health_score`, `accessibility`, `performance`, `visual_regression`, `screenshots`, `notes`) |
| `--format` | choice | No | `markdown` | Output format: `markdown` or `json` |
| `-o` / `--output` | string | No | stdout | Write the report to the specified file path instead of printing to stdout |
| `--history` | string | No | `None` | Path to a score history JSON file for trend analysis (array of objects with `score` or `overall_score` keys) |

**Example:**

```bash
# Generate a markdown report with trend data, written to a file
python scripts/test_report_generator.py session_data.json --format markdown --history .qa-baselines/history.json -o reports/qa-report-2026-03-21.md
```

**Output Formats:**

- **Markdown (default):** Full report with header (project, URL, tester, tier), executive summary, health score dashboard with category breakdown table, optional trend section, findings grouped by severity with details (title, category, location, description, steps, expected/actual), accessibility results, performance metrics table against thresholds, visual regression results, numbered recommendations, optional notes, and timestamped footer.
- **JSON (`--format json`):** Object with keys `report_type`, `generated`, `project`, `url`, `tier`, `health_score`, `grade`, `passed`, `total_findings`, `findings_by_severity`, `findings_by_category`, `accessibility_violations`, `accessibility_compliance_pct`, `visual_regressions`, `performance_metrics`, `trend`, and `recommendations`.

---

**Last Updated:** 2026-03-21
**Version:** 2.1.0
