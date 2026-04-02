---
name: qa-browser-automation
description: >
  Use when performing browser-based QA testing, visual regression tracking,
  WCAG accessibility auditing, performance profiling, or health scoring web
  applications. Combines Chrome MCP browser control with Python analysis tools
  for systematic, repeatable quality assurance.
license: MIT + Commons Clause
metadata:
  version: 2.1.0
  author: borghei
  category: engineering
  domain: quality-assurance
  updated: 2026-04-02
  tags: [browser-qa, wcag, visual-regression, health-scoring]
  python-tools: qa_health_scorer.py, accessibility_auditor.py, visual_regression_tracker.py, test_report_generator.py
  tech-stack: python, chrome-mcp, accessibility, wcag, performance
---
# QA Browser Automation

The agent drives Chrome MCP for live browser testing and uses four Python tools for deterministic health scoring, accessibility auditing, visual regression tracking, and report generation.

---

## Quick Start

```bash
# Score QA findings (0-100 weighted across 10 categories)
python scripts/qa_health_scorer.py findings.json --threshold 85 --baseline .qa-baselines/latest.json --save-baseline --json

# Audit HTML for WCAG 2.1 violations
python scripts/accessibility_auditor.py page.html --level AA --json

# Track visual regressions
python scripts/visual_regression_tracker.py --init --baseline-dir ./baselines
python scripts/visual_regression_tracker.py --register ./baselines
python scripts/visual_regression_tracker.py --baseline ./baselines --current ./screenshots --threshold 5

# Generate full QA report
python scripts/test_report_generator.py session_data.json --format markdown -o report.md
```

## Tools Overview

| Tool | Input | Output |
|------|-------|--------|
| `qa_health_scorer.py` | Findings JSON | Score 0-100, grade A-F, category breakdown, trend data |
| `accessibility_auditor.py` | HTML file (or stdin) | WCAG violations by level with remediation guidance |
| `visual_regression_tracker.py` | Baseline + current screenshot dirs | Pass/fail per page, change percentages |
| `test_report_generator.py` | Session data JSON | Markdown or JSON report with recommendations |

All tools support `--json` for machine output. Health scorer and regression tracker return exit code 1 on failure (CI-friendly).

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
- Run: `python scripts/qa_health_scorer.py findings.json --baseline .qa-baselines/latest.json`

**Phase 9: Triage and fix loop.**
- P3/P4: AUTO-FIX, commit atomically, verify.
- P0/P1/P2: ASK, present evidence, propose fix, wait for approval.
- After each fix: re-run check. If fail: `git revert`.
- Hard stop at 50 fixes.

**Phase 10-11: Regression check and report.**
- Re-visit fixed pages. Verify no new errors.
- Generate report: `python scripts/test_report_generator.py session.json --save-baseline`

**Validation checkpoint:** Health score >= 85. Zero P0 findings. WCAG AA >= 95%.

---

## Workflow 2: Visual Regression Testing

```bash
# Set up baseline
python scripts/visual_regression_tracker.py --init --baseline-dir ./baselines
# Capture and register screenshots
python scripts/visual_regression_tracker.py --register ./baselines
# After changes, compare
python scripts/visual_regression_tracker.py --baseline ./baselines --current ./screenshots --threshold 5 --json
# Accept intentional changes
python scripts/visual_regression_tracker.py --update-baseline --baseline ./baselines --current ./screenshots
```

Pages exceeding the threshold (default 5%) are flagged as regressions. Uses SHA-256 hashing and byte-level comparison.

---

## Workflow 3: Accessibility Audit

```bash
python scripts/accessibility_auditor.py page.html --level AA --json
curl -s https://example.com | python scripts/accessibility_auditor.py - --level AAA
```

**What gets checked by level:**
- **A (Must Fix):** Alt text, page language, form labels, headings, duplicate IDs, autoplay media
- **AA (Should Fix):** Color contrast (4.5:1 text, 3:1 large), heading hierarchy, focus visible, error identification
- **AAA (Nice to Have):** Enhanced contrast (7:1), extended audio, reading level

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
- **Risk accumulator** -- component (+5), style (+2), config (+8), revert (+15). Stop at 25% of budget.
- **WTF heuristic** -- 3 consecutive fix verification failures = stop entirely.
- **Atomic commits** -- one fix = one commit: `fix(qa): [P{severity}] {description}`

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Scorer exits code 1 with no errors | Score below `--threshold` (default 70) | Check score in output; raise threshold or fix findings |
| Auditor reports `parse-error` | Malformed HTML | Verify file is complete; check curl is not returning redirect |
| Regression tracker 100% change on all pages | Baseline manifest empty | Run `--init` then `--register` before comparing |
| Findings default to P3/functional | Missing `severity` or `category` keys | Include both keys in each finding dict |
| Chrome MCP returns stale content after SPA nav | DOM updated without full page load | Wait for transition, call `read_page` again |

---

## References

| Guide | Path |
|-------|------|
| Browser Testing Methodology | `references/browser_testing_methodology.md` |
| WCAG Compliance Guide | `references/wcag_compliance_guide.md` |
| Performance Benchmarks | `references/performance_benchmarks.md` |

---

## Integration Points

| Skill | Integration |
|-------|-------------|
| `code-reviewer` | Health score and findings in PR review context |
| `senior-frontend` | Visual regression baselines align with component library |
| `senior-devops` | Health score gates CI/CD via exit code |
| `senior-secops` | Security header findings escalate to security review |
| `incident-commander` | P0 findings trigger incident response |

---

**Last Updated:** April 2026
**Version:** 2.1.0
