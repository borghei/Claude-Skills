# Performance Benchmarks

Reference thresholds for Core Web Vitals, network analysis, and application performance profiling.

---

## Core Web Vitals Thresholds

Google's Core Web Vitals are the primary performance metrics that affect user experience and search ranking.

| Metric | Good | Needs Improvement | Poor | What It Measures |
|--------|------|-------------------|------|-----------------|
| **LCP** (Largest Contentful Paint) | <= 2.5s | 2.5s - 4.0s | > 4.0s | Loading — time to render largest visible element |
| **FID** (First Input Delay) | <= 100ms | 100ms - 300ms | > 300ms | Interactivity — delay before first input response |
| **CLS** (Cumulative Layout Shift) | <= 0.1 | 0.1 - 0.25 | > 0.25 | Visual stability — unexpected layout movement |
| **INP** (Interaction to Next Paint) | <= 200ms | 200ms - 500ms | > 500ms | Responsiveness — latency of all interactions (replaces FID) |
| **TTFB** (Time to First Byte) | <= 800ms | 800ms - 1800ms | > 1800ms | Server — time to receive first byte |

### Additional Timing Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| FCP (First Contentful Paint) | <= 1.8s | Time to first text/image render |
| TTI (Time to Interactive) | <= 3.8s | Time until page is fully interactive |
| TBT (Total Blocking Time) | <= 200ms | Sum of long task blocking time between FCP and TTI |
| Speed Index | <= 3.4s | How quickly visible content populates |

---

## Network Waterfall Analysis

### Resource Budget Guidelines

| Resource Type | Budget (compressed) | Notes |
|---------------|-------------------|-------|
| HTML document | < 50 KB | Includes inline critical CSS |
| CSS (total) | < 100 KB | Combined, minified, compressed |
| JavaScript (total) | < 300 KB | Combined initial bundle |
| Images (above fold) | < 200 KB | Use WebP/AVIF, lazy load below fold |
| Fonts | < 100 KB | Subset, use `font-display: swap` |
| Total page weight | < 1 MB | First load, compressed |

### Request Count Targets

| Metric | Target | Concern |
|--------|--------|---------|
| Total requests | < 50 | Connection overhead |
| Third-party requests | < 15 | Latency, privacy, reliability |
| Blocking requests | < 5 | Render delay |
| Redirects | 0-1 | Each adds 100-300ms |

### Waterfall Red Flags

- **Long TTFB:** Server processing or DNS issues. Check CDN, caching, database queries.
- **Render-blocking CSS/JS:** Move to async/defer, inline critical CSS.
- **Sequential resource loading:** Resources loading one-after-another instead of parallel. Check for unnecessary dependency chains.
- **Large uncompressed assets:** Enable gzip/brotli compression. Check `Content-Encoding` header.
- **No caching headers:** Static assets should have `Cache-Control: max-age=31536000` with hashed filenames.
- **Unused resources:** JavaScript or CSS loaded but not used on current page. Code-split by route.

---

## JavaScript Execution Profiling

### Long Task Thresholds

| Duration | Classification | Impact |
|----------|---------------|--------|
| < 50ms | Normal | No perceptible delay |
| 50-100ms | Long task | Slight jank possible |
| 100-300ms | Very long task | Noticeable lag |
| > 300ms | Blocking task | User perceives freeze |

### Common Causes of Long Tasks

1. **Synchronous layout (forced reflow):** Reading layout properties after DOM changes.
2. **Large DOM manipulation:** Batch DOM updates, use `requestAnimationFrame`.
3. **Heavy computation:** Move to Web Worker or break into smaller chunks with `setTimeout`.
4. **Third-party scripts:** Analytics, ads, chat widgets blocking main thread.
5. **JSON parsing:** Large API responses parsed on main thread.

### JavaScript Bundle Analysis

| Bundle Size (uncompressed) | Assessment |
|---------------------------|------------|
| < 100 KB | Excellent |
| 100-250 KB | Good |
| 250-500 KB | Review for optimization |
| > 500 KB | Needs code splitting |

---

## Memory Leak Detection Patterns

### Symptoms

- Heap size grows continuously over time without stabilizing.
- Performance degrades with prolonged use.
- Page becomes unresponsive after extended sessions.
- Browser tab crash on low-memory devices.

### Common Leak Sources

1. **Detached DOM nodes:** Elements removed from DOM but still referenced in JavaScript.
2. **Event listeners:** Listeners not removed on component unmount.
3. **Closures:** Functions retaining references to large objects.
4. **Timers:** `setInterval` not cleared on cleanup.
5. **Global state accumulation:** Growing arrays/objects never trimmed.

### Detection Approach

1. Take heap snapshot (baseline).
2. Perform the suspected leaking action 5-10 times.
3. Force garbage collection.
4. Take second heap snapshot.
5. Compare: if retained size grew significantly, investigate the delta.

---

## Mobile Performance Considerations

### Mobile-Specific Budgets

Mobile devices have less CPU, memory, and often slower network connections.

| Metric | Mobile Target | Desktop Target |
|--------|--------------|----------------|
| LCP | <= 2.5s | <= 2.0s |
| TTI | <= 5.0s | <= 3.8s |
| TBT | <= 300ms | <= 200ms |
| JS bundle | < 200 KB | < 300 KB |
| Total weight | < 500 KB | < 1 MB |

### Mobile Optimization Checklist

- Images use `srcset` and `sizes` for responsive loading.
- Below-fold images use `loading="lazy"`.
- Critical CSS is inlined in `<head>`.
- JavaScript is deferred (`defer` or `type="module"`).
- Fonts use `font-display: swap` to prevent FOIT.
- Touch interactions have no delay (no 300ms click delay).
- Viewport meta tag is set: `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- Service worker caches critical resources for repeat visits.

---

## Caching Strategy

### Cache-Control Headers

| Resource | Cache-Control | Rationale |
|----------|--------------|-----------|
| HTML pages | `no-cache` or `max-age=0, must-revalidate` | Always fresh |
| Hashed static assets | `max-age=31536000, immutable` | Content-addressed, safe to cache forever |
| API responses | `no-store` or `max-age=60` | Data freshness depends on use case |
| Images (CDN) | `max-age=86400` | Daily revalidation |
| Fonts | `max-age=31536000` | Rarely change |

### Performance Headers to Verify

| Header | Purpose |
|--------|---------|
| `Content-Encoding: br` or `gzip` | Compression enabled |
| `Cache-Control` | Caching policy set |
| `ETag` / `Last-Modified` | Conditional request support |
| `Vary: Accept-Encoding` | Correct cache variants |
| `Connection: keep-alive` | Connection reuse |

---

*Reference for the QA Browser Automation skill. Use alongside Chrome MCP network inspection tools.*
