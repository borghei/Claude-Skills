---
name: qa-browser-automation
description: >
  Live browser QA through Chrome MCP plus Python tools for health scoring, static WCAG
  checks, screenshot baselines and reports. Use when running a QA sweep on a web app,
  auditing accessibility, or tracking visual regressions.
license: MIT + Commons Clause
metadata:
  version: 2.2.0
  author: borghei
  category: engineering
  domain: quality-assurance
  updated: 2026-11-08
  tags: [browser-qa, wcag, visual-regression, health-scoring]
  python-tools: qa_health_scorer.py, accessibility_auditor.py, visual_regression_tracker.py, test_report_generator.py
  tech-stack: python, chrome-mcp, accessibility, wcag
---
# QA Browser Automation

The agent drives Chrome MCP for live browser testing and uses four Python tools for deterministic health scoring, accessibility auditing, visual regression tracking, and report generation.

## When to Use

- Running a structured QA sweep on a web app before a release, with evidence for every finding.
- Auditing saved HTML for common WCAG failures.
- Tracking screenshot changes between releases.
- Turning a QA session into a scored, comparable report.

---

## Clarify First

Before the QA sweep, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target URL/app + auth:** what to test and how to log in (the subject of the entire sweep).
- **Testing tier:** Quick / Standard / Deep / Exhaustive (sets scope, breakpoints, and duration).
- **Fix autonomy:** auto-fix P3/P4 and commit, vs report-only / ask before any code change (changes whether the working tree is modified).
- **WCAG target level:** A / AA / AAA (sets the accessibility pass bar).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Score QA findings (0-100 weighted across 10 categories); the sample scores 87.1 but fails on its P0
python3 scripts/qa_health_scorer.py assets/sample_findings.json --threshold 85

# Static WCAG checks: sound page exits 0, flawed page exits 1 with 6 violations
python3 scripts/accessibility_auditor.py assets/sound_page.html --level AA
python3 scripts/accessibility_auditor.py assets/flawed_page.html --level AA

# Track visual regressions (screenshots come from the browser session; empty dirs here)
VR=$(mktemp -d); mkdir -p "$VR/baselines" "$VR/screenshots"
python3 scripts/visual_regression_tracker.py --init --baseline-dir "$VR/baselines"
python3 scripts/visual_regression_tracker.py --register "$VR/baselines"
python3 scripts/visual_regression_tracker.py --baseline "$VR/baselines" --current "$VR/screenshots" --threshold 5   # exit 1: nothing compared yet

# Generate the QA report (computes the health score from the findings when the session has none)
python3 scripts/test_report_generator.py assets/sample_findings.json --format markdown -o "$VR/report.md"
```

## Tools Overview

| Tool | Input | Output |
|------|-------|--------|
| `qa_health_scorer.py` | Findings JSON | Score 0-100, grade A-F, category breakdown, trend data |
| `accessibility_auditor.py` | HTML file (or stdin) | WCAG violations by level with remediation guidance |
| `visual_regression_tracker.py` | Baseline + current screenshot dirs | Pass/fail per page, change percentages |
| `test_report_generator.py` | Session data JSON | Markdown or JSON report with recommendations |

The health scorer, accessibility auditor and regression tracker take `--json` for machine output; the report generator uses `--format json`.

**Exit codes:** 0 pass; 1 gate failed (scorer: below `--threshold` or any P0; auditor: must-fix violations; tracker: regressions, or nothing compared); 2 unreadable input (missing file, bad JSON, missing directory).

---

## Workflow 1: Full Application QA Sweep (11 Phases)

**Phase 1-2: Pre-flight and authentication.**
- Verify `git status` is clean. Abort if dirty.
- Create session directory: `.qa-sessions/{timestamp}/`
- Authenticate via Chrome MCP if needed.

**Phase 3-4: Orient and explore.**
- Use `mcp__claude-in-chrome__read_page` to build sitemap/page map.
- Navigate each route. Check `read_console_messages` for errors, `read_network_requests` for 4xx/5xx.
- Test all forms with valid data, empty submissions, and boundary values.

**Phase 5: State testing.**
- Verify loading states (skeleton screens, not blank), empty states (guides to first action), error states, success states, partial states.
- **Four shadow paths per interaction:** happy path, nil input, empty input, error upstream.

**Phase 6: Cross-device and security.**
- Resize to 320px, 768px, 1024px, 1440px, 1920px.
- Check touch targets (44x44px min), layout shifts.
- Verify security headers (CSP, HSTS, X-Frame-Options), cookie flags.

**Phase 7-8: Document and score.**
- Record every finding with screenshot evidence. No finding without evidence.
- Classify by severity (P0-P4) and category (10 categories).
- Run: `python3 scripts/qa_health_scorer.py findings.json --baseline .qa-baselines/latest.json`

**Phase 9: Triage and fix loop.**
- P3/P4: fix directly only if the user chose auto-fix in Clarify First; commit atomically and verify.
- P0/P1/P2: present the evidence and a proposed fix, and wait for approval before changing code.
- After each fix: re-run check. If fail: `git revert`.
- Hard stop at 50 fixes.

**Phase 10-11: Regression check and report.**
- Re-visit fixed pages. Verify no new errors.
- Save the score as the next baseline: `python3 scripts/qa_health_scorer.py findings.json --save-baseline` (writes `.qa-baselines/{date}.json` and `.qa-baselines/latest.json`)
- Generate report: `python3 scripts/test_report_generator.py session.json -o report.md`

**Validation checkpoint:** `qa_health_scorer.py --threshold 85` exits 0, which requires a score of at least 85 and zero P0 findings. `accessibility_auditor.py --level AA` reports no must-fix violations; contrast and anything rendered by JavaScript still need a manual check, because the auditor reads static HTML.

---

## Workflow 2: Visual Regression Testing

```bash
# Where the browser session saves screenshots (outside the repo); both must exist
BASE="${QA_DIR:-$(mktemp -d)}/baselines"; SHOTS="$(dirname "$BASE")/screenshots"; mkdir -p "$BASE" "$SHOTS"
# Set up baseline, then save the reference screenshots into $BASE and register them
python3 scripts/visual_regression_tracker.py --init --baseline-dir "$BASE"
python3 scripts/visual_regression_tracker.py --register "$BASE"
# After changes, save new screenshots into $SHOTS and compare (exit 1 on regressions or when nothing was compared)
python3 scripts/visual_regression_tracker.py --baseline "$BASE" --current "$SHOTS" --threshold 5 --json
# Accept intentional changes
python3 scripts/visual_regression_tracker.py --update-baseline --baseline "$BASE" --current "$SHOTS"
```

Pages exceeding the threshold (default 5%) are flagged as regressions. The tracker compares SHA-256 hashes and the raw bytes of the image files, not decoded pixels, so the change percentage is a rough signal and a re-encoded but visually identical screenshot can still read as changed.

---

## Workflow 3: Accessibility Audit

```bash
python3 scripts/accessibility_auditor.py assets/flawed_page.html --level AA --json
curl -s https://example.com | python3 scripts/accessibility_auditor.py - --level AAA
```

**What gets checked by level:**
- **A (Must Fix):** Alt text, page language, page title, heading hierarchy, duplicate IDs, form labels, empty link text, media captions and autoplay, main and nav landmarks, positive tabindex
- **AA (Should Fix):** Adds focus indicators removed with `outline:none`, and flags elements with inline color styles for manual contrast review. Contrast ratios are not measured, because the tool cannot compute styles
- **AAA (Nice to Have):** Adds generic link text such as "click here" (2.4.9). There is no enhanced-contrast measurement and no reading-level check; review those by hand

Each violation includes: WCAG criterion, severity, element selector, and remediation guidance.

---

## Testing Tiers

| Tier | Duration | Scope |
|------|----------|-------|
| **Quick** | 30s | Console errors, broken links, basic a11y, mobile resize |
| **Standard** | 2-5 min | + Top 10 routes, forms, contrast, Core Web Vitals |
| **Deep** | 10-20 min | + Full sitemap, state testing, WCAG AA, performance, visual regression, security headers |
| **Exhaustive** | 30+ min | + Every element, WCAG AAA, all pages performance, 5 breakpoints, auth edge cases, memory leaks |

---

## Health Scoring System

10 weighted categories, score 0-100:

| Category | Weight | Measures |
|----------|--------|----------|
| Functional | 18% | Forms, CRUD, navigation flows |
| Accessibility | 13% | WCAG compliance, keyboard nav |
| Console Errors | 12% | JS errors, unhandled rejections |
| UX Flow | 12% | Logical navigation, clear feedback |
| Performance | 12% | Core Web Vitals within thresholds |
| Visual Consistency | 10% | Layout shifts, alignment, z-index |
| Broken Links | 8% | HTTP 4xx/5xx, dead anchors |
| Content Quality | 5% | Spelling, placeholder text, truncation |
| Security Headers | 5% | CSP, HSTS, cookie flags |
| Mobile Responsive | 5% | Breakpoints, touch targets, no h-scroll |

**Severity deductions:** P0: -30, P1: -18, P2: -10, P3: -4, P4: -1.

**Grades:** A (90-100), B (80-89), C (70-79), D (60-69), F (0-59).

---

## Safety Controls

- **Clean working tree required** -- abort if `git status` dirty.
- **Max 50 fixes per session** -- hard stop.
- **Risk budget** -- each fix adds risk points: style +2, component +5, config +8, a revert +15. Stop fixing and report once the session reaches 25 points, because risk compounds and late fixes are the ones least reviewed.
- **Three strikes** -- three fix verifications in a row that fail means the fix loop does not understand the problem; stop and report rather than keep editing.
- **Atomic commits** -- one fix = one commit: `fix(qa): [P{severity}] {description}`

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Scorer exits code 1 | Score below `--threshold` (default 70) or at least one P0 finding | Read the `Blocked by` line; fix the P0 or the findings dragging the score |
| Scorer exits code 2 | Findings file missing or not valid JSON | Check the path and JSON syntax |
| Auditor reports `parse-error` | Malformed HTML | Verify file is complete; check curl is not returning redirect |
| Regression tracker reports FAIL with "Nothing was compared" | No registered baselines, so every page counts as new | Run `--init`, then `--register` the baseline directory, then compare |
| Findings default to P3/functional | Missing `severity` or `category` keys | Include both keys in each finding dict |
| Chrome MCP returns stale content after SPA nav | DOM updated without full page load | Wait for transition, call `read_page` again |

---

## Anti-Patterns

**Mistake:** Reporting a pass because the health score cleared the threshold.
**Why it matters:** A weighted score can absorb a P0 blocker; one broken checkout outweighs twenty clean pages.
**Instead:** Treat any P0 as a failed gate (the scorer does) and fix or escalate it before release.

**Mistake:** Comparing screenshots before baselines are registered.
**Why it matters:** Every page shows up as new and nothing is compared, which looks like no regressions.
**Instead:** `--init`, `--register`, then compare; the tracker now fails when it compared nothing.

**Mistake:** Calling a page WCAG AA compliant from the static auditor alone.
**Why it matters:** It cannot measure contrast, focus visibility or JavaScript-rendered content.
**Instead:** Report its findings as a floor and add keyboard and contrast checks in the browser.

---

## Reference Documentation

| Guide | Path |
|-------|------|
| Browser Testing Methodology | `references/browser_testing_methodology.md` |
| WCAG Compliance Guide | `references/wcag_compliance_guide.md` |
| Performance Benchmarks | `references/performance_benchmarks.md` |

---

## Scope & Limitations

**In Scope:**
- A live QA sweep driven through Chrome MCP: page discovery, console and network errors, forms, UI states, breakpoints and security headers, with the testing tiers and safety controls above.
- Weighted health scoring from a findings JSON with `qa_health_scorer.py`: 0-100 score, A-F grade, ten categories, baseline trend, and exit 1 below `--threshold` or on any P0 (exit 2 on unreadable input).
- Static checks for a subset of WCAG 2.1 success criteria on saved HTML with `accessibility_auditor.py` at level A, AA or AAA. WCAG 2.2 additions such as target size and focus not obscured need a rendered page, so check them in the browser.
- Screenshot baseline tracking with `visual_regression_tracker.py`, and Markdown or JSON session reports with `test_report_generator.py`.

**Out of Scope:**
- Writing and maintaining an automated end-to-end test suite (see `engineering/playwright-pro/`).
- A full accessibility program with screen-reader and keyboard testing (see `engineering/a11y-audit/`).
- Detailed performance profiling (see `engineering/performance-profiler/`).
- Security testing beyond header and cookie checks (see `engineering/security-audit/`).

**Important Caveats:**
- The Python tools do not open a browser. Browser work depends on Chrome MCP being available, and the scorer and report generator only process findings that were recorded by hand or by the agent.
- `accessibility_auditor.py` parses static HTML. It cannot compute styles, so color contrast is flagged for manual review rather than measured, and content rendered by JavaScript is missed unless the saved HTML includes it.
- `visual_regression_tracker.py` compares file hashes and bytes of image files, not pixels. Its change percentage is a rough signal, and a re-encoded but identical screenshot can still read as changed.
- The fix loop edits and commits code. The clean-tree check, fix cap and approval rules above limit that, and a passing health score does not mean the application is free of defects.
