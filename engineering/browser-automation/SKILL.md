---
name: browser-automation
description: >
  Generates polite, rate-limited scraper and form-submission scripts (requests, no JS) and audits
  automation code for blocking and overload risks. Use when writing a permitted scraper, scripting
  a form post, or reviewing a crawler.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: web-automation
  updated: 2026-11-08
  tags: [browser-automation, web-scraping, rate-limiting, form-automation, robots-txt]
---

# Browser Automation

> **Category:** Engineering
> **Domain:** Web Automation

## Overview

The agent uses this skill to write automation that a site owner would accept: identified, rate-limited, robots.txt-aware and resilient to errors. The generated code uses Python `requests`, so it handles server-rendered HTML only; for JavaScript-heavy pages or full browser control use Playwright (`engineering/playwright-pro`).

**Authorization comes first.** Confirm the user may automate the target (their own site, a test environment, a public API, or terms that allow it). Do not help defeat a site's bot protection, CAPTCHAs, logins or rate limits where the site has not allowed automation; the audit tool exists to make permitted automation reliable and polite, not invisible.

## When to Use

- Writing a scraper for a site you own or are permitted to crawl, with rate limits and robots.txt handling.
- Scripting a form submission from a saved page (internal tools, test environments, permitted targets).
- Reviewing an existing crawler or automation script for overload and blocking risks before it runs.

## Clarify First

Before generating automation, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target site & task:** the URL and exactly what to automate or scrape (drives the generated selectors and flow).
- **Which tool:** audit an existing script, build form automation, or generate a scraper (selects `anti_detection_checker.py` vs `form_automation_builder.py` vs `scraping_toolkit.py`).
- **Politeness strategy & authorization:** polite vs aggressive, robots.txt compliance, and that you are permitted to automate this target (sets request delays and backoff in the generated code).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start Workflow

```bash
# 1. Generate a scraper template: polite strategy, robots.txt check, page cap, JSON output
python scripts/scraping_toolkit.py --url https://example.com/catalog --strategy polite --output /tmp/scraper.py

# 2. Generate a form-submission script from a saved page (pages are never fetched)
python scripts/form_automation_builder.py --html-file assets/sample_contact_form.html \
    --base-url https://example.com --output /tmp/form.py

# 3. Audit any automation script before it runs
python scripts/anti_detection_checker.py --file assets/sample_bare_scraper.py   # 68/100, exit 1
python scripts/anti_detection_checker.py --file /tmp/scraper.py                 # 0/100, exit 0
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `scraping_toolkit.py` | Scraper template with delays, backoff, robots.txt check and page cap | `--url`, `--strategy polite\|normal\|aggressive\|gentle`, `--max-pages`, `--output-format csv\|json\|jsonl`, `--no-robots`, `--output` |
| `form_automation_builder.py` | Field map (required, CSRF, CAPTCHA, uploads) and a `requests` script for one form | `--html-file`, `--base-url`, `--form-index`, `--output` |
| `anti_detection_checker.py` | Risk score from concealment (webdriver masking, fingerprint spoofing, browser-impersonating User-Agent, proxies) and load patterns (sub-second or fixed delays), plus missing protections (rate limit, robots.txt, backoff, jitter, identifying User-Agent) | `--file` |

All take `--format human|json`. Default to `--strategy polite`; use `gentle` (5-15 s between requests) for small or fragile sites, and `aggressive` only for targets the user controls or has explicit permission to load-test. Generated scripts send an identifying User-Agent (`ExampleCrawler/1.0 (+URL; contact)`) that you edit before running; they never rotate User-Agents or proxies.

**Exit codes.** `anti_detection_checker.py`: `0` risk below 50, `1` risk 50 or more, `2` missing or unreadable file. The two generators: `0` script generated, `2` missing file, no form found, `--form-index` out of range, or `--url` without a saved page.

**Done when:**
1. Authorization for the target is confirmed and written down.
2. The audit scores below 50 and every critical or high signature is fixed or explained.
3. The script identifies itself (User-Agent with bot name and contact), masks nothing, honours robots.txt and the terms of service, and stops at a page cap.
4. A dry run against a handful of pages produced the expected fields.

## Workflows

### Build a Reliable Scraper
1. Generate the base code with `scraping_toolkit.py --strategy polite`.
2. Fill in the selectors, then audit it with `anti_detection_checker.py`.
3. Fix critical and high items and add any missing protection.
4. Run it on a few pages at the polite rate before raising the page cap.

### Automate a Form Submission
1. Save the page HTML locally and pass it to `form_automation_builder.py` with `--html-file` (add `--base-url` so relative actions resolve).
2. Check the field map: required fields, CSRF token, CAPTCHA (handled manually, never bypassed).
3. Wire in the data source and validation, then audit the final script.

## Anti-Patterns

### Hammering the target
**Mistake:** A loop of requests with no delay, no page cap and no backoff on 429 or 5xx.
**Why it happens:** It works on the first ten pages, so nobody adds the brakes.
**Instead:** Use the polite strategy: jittered delays, exponential backoff, a page cap. The audit adds risk for each missing protection.

### Evasion instead of permission
**Mistake:** Rotating proxies and User-Agents to keep scraping a site that blocks the bot.
**Why it happens:** A block looks like a technical problem.
**Instead:** Treat a block as the site's answer. Ask for API access or permission, or stop.

### requests on a JavaScript app
**Mistake:** Scraping a single-page app with `requests` and getting empty templates.
**Why it happens:** The page looks like HTML in the browser.
**Instead:** Check the raw response first. If the data arrives via XHR, call that documented endpoint; otherwise use Playwright.

## Files

- `scripts/scraping_toolkit.py`, `scripts/form_automation_builder.py`, `scripts/anti_detection_checker.py` — the three CLIs above.
- `assets/sample_bare_scraper.py` — careless scraper for the audit (exit 1); `assets/sample_contact_form.html` — form for the builder.
- `references/browser-automation-guide.md` — rate limiting, backoff and ethical scraping detail.

## Scope & Limitations

**In Scope:**
- Auditing an automation script with `anti_detection_checker.py` for blocking and overload risks (signatures plus missing protections)
- Generating a Python `requests` form-submission script with `form_automation_builder.py` from a locally saved HTML file, with field mapping and form selection by index
- Generating a scraper template with `scraping_toolkit.py`: rate-limit strategy (polite, normal, aggressive, gentle) and an identifying User-Agent, robots.txt checking, a page cap and CSV, JSON or JSONL output
- Guidance on rate limiting, backoff and ethical scraping from the browser automation reference

**Out of Scope:**
- End-to-end testing of your own web app (see `engineering/playwright-pro/` and `engineering/qa-browser-automation/`)
- Agents that drive a GUI from screenshots (see `engineering/computer-use-automation/`)
- Solving CAPTCHAs or getting past logins, paywalls or other access controls; the form builder only flags CAPTCHA fields for manual handling
- Legal review of whether scraping a given site is permitted; terms of service and data-protection questions need a lawyer, and `legal/privacy-compliance/` covers privacy law in general

**Important Caveats:**
- None of the tools fetch pages. `form_automation_builder.py` needs `--html-file`; passed `--url` alone, it exits with an error.
- Generated scripts use the `requests` library and do not run JavaScript. Pages that build forms or content client-side need a real browser tool instead.
- The audit is a static regex review of script text, comments included. It does not run the script or test it against a live site.
- Users are responsible for permission to automate a target, for honouring robots.txt and terms of service, and for how they handle any personal data collected.

## Reference Documentation

- [Browser Automation Guide](references/browser-automation-guide.md) - Being a good bot, rate limiting strategies, ethical scraping practices

## Common Patterns

### Polite Scraping
- Respect robots.txt directives
- Implement exponential backoff on errors
- Use 2-5 second delays between requests
- Identify your bot with a descriptive User-Agent
- Cache responses to minimize repeat requests
