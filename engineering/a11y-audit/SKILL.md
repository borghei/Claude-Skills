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

## Quick Start

```bash
# Scan HTML for WCAG violations
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

Checks color contrast ratios against WCAG AA and AAA thresholds.

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
| Large text (>=18pt bold or >=14pt) | 3:1 | 4.5:1 |
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
