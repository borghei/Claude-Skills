# Browser Automation Guide

## Being a Good Bot

Permitted automation does not need to look like a person. Make the script easy for the site owner
to identify, throttle and contact, and stay inside the site's rules:

- **Identify yourself.** A User-Agent with the bot name, a URL describing it and a contact
  address, for example `MyCrawler/1.0 (+https://example.com/bot; ops@example.com)`. Do not copy a
  browser's User-Agent or rotate User-Agents.
- **Do not mask automation.** No `navigator.webdriver` overrides, fingerprint or TLS spoofing,
  stealth plugins or rotating proxies. If a site blocks automation, that is its answer: ask for
  access or an API.
- **Follow robots.txt and the terms of service**, and honour `Retry-After`, `X-RateLimit-*`,
  `meta robots` and `X-Robots-Tag`.
- **Keep the load low.** Jittered delays, one connection per host unless the owner allows more,
  backoff on 429/503, a page cap, and caching so nothing is fetched twice.

### What `anti_detection_checker.py` flags
- Concealment: webdriver masking, browser fingerprint rewrites, browser-impersonating User-Agents, proxies.
- Load: sub-second or fixed delays with no back-pressure.
- Missing protections: rate limiting, robots.txt, backoff, jitter, an identifying User-Agent, a reused session.

## Rate Limiting Strategies

| Strategy | Delay Range | Use Case |
|----------|-------------|----------|
| Aggressive | 0.5-1s | Own APIs, test environments |
| Normal | 1-3s | General scraping |
| Polite | 3-7s | Respectful scraping |
| Gentle | 5-15s | Small or fragile sites |

### Exponential Backoff
On HTTP 429 or 503 responses:
1. Wait 1s, retry
2. Wait 2s, retry
3. Wait 4s, retry
4. Wait 8s, retry
5. Abort after 5 retries

## Ethical Scraping Guidelines

1. **Always check robots.txt** before scraping
2. **Respect rate limits** in HTTP headers (X-RateLimit-*)
3. **Identify your bot** with a descriptive User-Agent
4. **Don't scrape personal data** without legal basis
5. **Cache aggressively** to minimize server load
6. **Honor opt-out mechanisms** (meta robots, X-Robots-Tag)
7. **Contact site owners** if scraping at scale

## Form Automation Patterns

### Field Type Handling
- **Text inputs**: Direct value injection
- **Select/dropdown**: Option matching by value or text
- **Radio buttons**: Group-aware selection
- **Checkboxes**: Boolean state management
- **File uploads**: Multipart form data handling
- **Date pickers**: JavaScript-based date injection
- **CAPTCHA**: Detection and flagging (no bypass)

### Session Management
- Maintain cookies across form steps
- Handle CSRF tokens in hidden fields
- Follow redirect chains after submission
- Validate form state before submission
