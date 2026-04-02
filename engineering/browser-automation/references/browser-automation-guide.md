# Browser Automation Guide

## Anti-Detection Techniques

### Browser Fingerprinting Signals
Modern bot detection systems check for:

1. **Navigator Properties**: `navigator.webdriver`, `navigator.plugins`, `navigator.languages`
2. **WebGL Fingerprint**: Canvas and WebGL rendering differences between headless and real browsers
3. **Timing Patterns**: Consistent request intervals indicate automation
4. **Mouse/Keyboard Events**: Lack of human-like interaction events
5. **JavaScript API Presence**: Missing APIs that real browsers expose
6. **HTTP Header Order**: Automated clients often send headers in different order
7. **TLS Fingerprint (JA3)**: Client TLS handshake characteristics

### Common Detection Signatures in Code
- Hardcoded `navigator.webdriver = false` overrides
- Missing viewport or screen size randomization
- Fixed User-Agent strings that don't rotate
- No cookie handling between requests
- Predictable wait times (e.g., `sleep(2)` vs randomized delays)
- Missing referrer headers on navigation

## Rate Limiting Strategies

| Strategy | Delay Range | Use Case |
|----------|-------------|----------|
| Aggressive | 0.5-1s | Own APIs, test environments |
| Normal | 1-3s | General scraping |
| Polite | 3-7s | Respectful scraping |
| Stealth | 5-15s | Sensitive targets |

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
