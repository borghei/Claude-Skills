---
name: browser-automation
description: >
  This skill should be used when the user asks to "build web automation scripts",
  "check browser automation for detection", "generate web scraping code",
  "create form filling automation", or "build anti-detection browser scripts".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: web-automation
  updated: 2026-04-02
  tags: [browser-automation, web-scraping, anti-detection, form-automation, selenium]
---

# Browser Automation

> **Category:** Engineering
> **Domain:** Web Automation

## Overview

The **Browser Automation** skill provides tools for building robust web automation, checking scripts for bot detection signatures, generating form automation code, and creating web scraping solutions with rate limiting and best practices.

## Clarify First

Before generating automation, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target site & task:** the URL and exactly what to automate or scrape (drives the generated selectors and flow).
- **Which tool:** audit an existing script, build form automation, or generate a scraper (selects `anti_detection_checker.py` vs `form_automation_builder.py` vs `scraping_toolkit.py`).
- **Politeness strategy & authorization:** polite vs aggressive, robots.txt compliance, and that you are permitted to automate this target (sets request delays and backoff in the generated code).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Check automation script for detection signatures
python scripts/anti_detection_checker.py --file ./my_scraper.py

# Generate form automation code from a locally saved HTML page
python scripts/form_automation_builder.py --html-file ./form.html --base-url https://example.com --output form_script.py

# Generate scraping code with rate limiting
python scripts/scraping_toolkit.py --url https://example.com --strategy polite --output scraper.py
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `anti_detection_checker.py` | Audit automation code for bot detection signatures | `--file`, `--format` |
| `form_automation_builder.py` | Generate form filling scripts from a saved HTML file | `--html-file`, `--base-url`, `--output` |
| `scraping_toolkit.py` | Generate web scraping code with rate limiting | `--url`, `--strategy`, `--output` |

## Workflows

### Build Reliable Scraper
1. Analyze target with `scraping_toolkit.py` to generate base code
2. Check generated code with `anti_detection_checker.py`
3. Address any detection signatures found
4. Test with progressive rate limiting

### Automate Form Submission
1. Save the page HTML locally and pass it to `form_automation_builder.py` with `--html-file` (add `--base-url` so relative form actions resolve)
2. Review generated script for field mappings
3. Customize data sources and validation
4. Run anti-detection check on final script

## Scope & Limitations

**In Scope:**
- Auditing an automation script with `anti_detection_checker.py` for common bot-detection signatures
- Generating a Python `requests` form-submission script with `form_automation_builder.py` from a locally saved HTML file, with field mapping and form selection by index
- Generating a scraper template with `scraping_toolkit.py`: rate-limit strategy (polite, normal, aggressive, stealth), robots.txt checking, a page cap and CSV, JSON or JSONL output
- Guidance on rate limiting, backoff and ethical scraping from the browser automation reference

**Out of Scope:**
- End-to-end testing of your own web app (see `engineering/playwright-pro/` and `engineering/qa-browser-automation/`)
- Agents that drive a GUI from screenshots (see `engineering/computer-use-automation/`)
- Solving CAPTCHAs or getting past logins, paywalls or other access controls; the form builder only flags CAPTCHA fields for manual handling
- Legal review of whether scraping a given site is permitted; terms of service and data-protection questions need a lawyer, and `legal/privacy-compliance/` covers privacy law in general

**Important Caveats:**
- None of the tools fetch pages. `form_automation_builder.py` needs `--html-file`; passed `--url` alone, it exits with an error.
- Generated scripts use the `requests` library and do not run JavaScript. Pages that build forms or content client-side need a real browser tool instead.
- The anti-detection check is a static review of script text. It does not test the script against a live bot-detection system.
- Users are responsible for permission to automate a target, for honouring robots.txt and terms of service, and for how they handle any personal data collected.

## Reference Documentation

- [Browser Automation Guide](references/browser-automation-guide.md) - Anti-detection techniques, rate limiting strategies, ethical scraping practices

## Common Patterns

### Polite Scraping
- Respect robots.txt directives
- Implement exponential backoff on errors
- Use 2-5 second delays between requests
- Identify your bot with a descriptive User-Agent
- Cache responses to minimize repeat requests

### Anti-Detection Best Practices
- Rotate User-Agent strings realistically
- Randomize request timing (avoid fixed intervals)
- Handle cookies and sessions properly
- Avoid headless browser fingerprinting tells
