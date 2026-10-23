---
name: a11y-audit
description: >
  This skill should be used when the user asks to "check accessibility",
  "audit WCAG compliance", "scan HTML for a11y issues", "check color contrast",
  or "find accessibility violations in web pages".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: accessibility
  updated: 2026-04-02
  tags: [accessibility, a11y, wcag, contrast, html]
---
# Accessibility Audit

> **Category:** Engineering
> **Domain:** Web Accessibility

## Overview

The **Accessibility Audit** skill provides automated scanning of HTML files for WCAG 2.1 compliance violations and color contrast checking against AA/AAA standards. It catches missing alt text, broken heading hierarchies, unlabeled form inputs, and insufficient color contrast early in development.

## Clarify First

Before running the audit, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target & scope:** which HTML files, directory, or CSS to scan (determines what gets checked and the `--file`/`--dir`/`--css` arguments).
- **Conformance level:** A, AA, or AAA target (sets contrast thresholds and which violations are CRITICAL vs WARNING vs INFO).
- **Use context:** one-off remediation vs CI gate (drives `--strict` gating and JSON output).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Scan HTML for WCAG 2.1 violations
python scripts/a11y_scanner.py --file index.html

# Scan a directory of HTML files
python scripts/a11y_scanner.py --dir ./src/templates

# Check color contrast
python scripts/contrast_checker.py --foreground "#333333" --background "#ffffff"

# Parse CSS file for contrast issues
python scripts/contrast_checker.py --css styles.css

# JSON output for CI
python scripts/a11y_scanner.py --file index.html --format json
```

## Tools Overview

### a11y_scanner.py

Scans HTML files for WCAG 2.1 violations including structural, semantic, and interactive element issues.

| Feature | Description |
|---------|-------------|
| Image alt text | Detects missing or empty alt on non-decorative images |
| Heading hierarchy | Validates h1-h6 levels are sequential |
| Form labels | Ensures inputs have associated label elements |
| ARIA attributes | Checks ARIA usage correctness |
| Link text | Flags generic text like "click here" or "read more" |
| Language attribute | Checks for lang on html element |
| Tab order | Detects positive tabindex values |
| Landmarks | Validates semantic landmark usage |

### contrast_checker.py

Checks color contrast ratios against the WCAG 2.1 AA and AAA thresholds.

| Feature | Description |
|---------|-------------|
| Ratio calculation | Computes relative luminance contrast ratio |
| AA compliance | 4.5:1 normal text, 3:1 large text |
| AAA compliance | 7:1 normal text, 4.5:1 large text |
| CSS parsing | Extracts color/background pairs from CSS |
| Color suggestions | Recommends nearest compliant color |

## Workflows

### Full Accessibility Audit

1. **Scan HTML** - Run a11y_scanner.py on all templates
2. **Check contrast** - Run contrast_checker.py on stylesheets
3. **Triage** - Prioritize Level A violations first
4. **Remediate** - Fix critical issues (alt text, form labels, headings)
5. **Re-scan** - Verify fixes pass all checks

### CI Integration

```bash
# Gate on Level A violations
python scripts/a11y_scanner.py --dir ./templates --format json --level A --strict

# Check CSS contrast
python scripts/contrast_checker.py --css ./static/css/main.css --format json
```

### Development Workflow

1. **Pre-commit** - Quick scan of changed HTML files
2. **PR review** - Full scan as part of review checklist
3. **Staging audit** - Comprehensive scan before release
4. **Monitoring** - Regular scheduled audits

## Scope & Limitations

**In Scope:**
- Static scanning of a single HTML file or a directory of `.html`/`.htm` files with `a11y_scanner.py` for WCAG 2.1 issues: image alt text, heading hierarchy, form labels, ARIA attributes, generic link text, the `lang` attribute, positive `tabindex` values and landmarks
- Findings tagged with a WCAG level and success criterion, mapped to critical (A), warning (AA) and info (AAA), with `--level` filtering and a `--strict` exit code for CI gates
- Contrast ratio checks with `contrast_checker.py` for one foreground/background pair or for color pairs pulled from a CSS file, against the AA and AAA thresholds, with a suggested compliant color
- Remediation guidance from the WCAG reference and the quick-fix tables in this file

**Out of Scope:**
- Testing a rendered page in a real browser, including content added by JavaScript, runtime focus order and keyboard traps (see `engineering/qa-browser-automation/` and `engineering/playwright-pro/`)
- Testing with screen readers or other assistive technology, or with users who rely on them
- Visual design review and design-token audits (see `engineering/design-auditor/`)
- Native app accessibility (see `product-team/apple-hig-expert/` for Apple platforms)
- Legal advice on accessibility obligations

**Important Caveats:**
- Both tools read source files only. Markup built at runtime by a framework or template engine, and styles computed in the browser, are not seen the way a user sees them.
- The CSS check pairs `color` with `background-color` or `background` declared in the same rule. Inherited colors, CSS variables, images and gradients behind text are not resolved, so contrast results need visual confirmation.
- A clean scan covers the checks listed above, not every WCAG success criterion. It is not a conformance claim or an accessibility statement, and many criteria still need manual review.
- The rules target WCAG 2.1. Criteria added in WCAG 2.2, such as minimum target size, are not checked.

## Reference Documentation

- [WCAG Guidelines](references/wcag-guidelines.md) - Conformance levels, success criteria, common fixes

## Common Patterns Quick Reference

### WCAG Levels
| Level | Description | Typical Requirement |
|-------|-------------|-------------------|
| A | Minimum baseline | Legal compliance |
| AA | Industry standard | Most regulations, ADA |
| AAA | Enhanced | Best practice goal |

### Contrast Ratios
| Context | AA | AAA |
|---------|-----|-----|
| Normal text (<18pt) | 4.5:1 | 7:1 |
| Large text (>=18pt, or >=14pt bold) | 3:1 | 4.5:1 |
| UI components | 3:1 | 3:1 |

### Quick Fixes
| Issue | Fix |
|-------|-----|
| Missing alt text | `<img alt="Description of image">` |
| Skipped heading | Use sequential h1 through h6 |
| No form label | `<label for="inputId">Label</label>` |
| Generic link text | Replace "click here" with descriptive text |
| Missing lang | `<html lang="en">` |
| Positive tabindex | Use tabindex="0" or tabindex="-1" only |

### Severity Mapping
- **CRITICAL** - WCAG Level A violations
- **WARNING** - WCAG Level AA violations
- **INFO** - WCAG Level AAA recommendations
