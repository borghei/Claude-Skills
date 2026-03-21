# Browser Testing Methodology

Expert knowledge base for systematic browser-based quality assurance.

---

## Systematic Page Exploration

### Route Discovery Strategy

1. **Navigation-first:** Inspect the main navigation (header, sidebar, footer) to enumerate all top-level routes.
2. **Sitemap check:** Look for `/sitemap.xml` or `/robots.txt` for a machine-readable route list.
3. **Dynamic routes:** Identify parameterized URLs (e.g., `/users/:id`, `/products/:slug`) and test with valid, invalid, and boundary IDs.
4. **Hidden routes:** Check for admin panels (`/admin`, `/dashboard`), API docs (`/docs`, `/swagger`), and debug pages (`/debug`, `/health`).
5. **Hash routes:** SPAs often use hash-based routing (`/#/page`). Inspect the router configuration or observe URL changes during navigation.

### Exploration Order

- Start from the landing page and follow natural user flows.
- Test the primary conversion path first (signup, purchase, key action).
- Then test secondary paths (settings, profile, help).
- Finally test edge-case paths (error pages, 404, maintenance mode).

---

## Element Interaction Patterns

### Forms

| Element | Test Actions |
|---------|-------------|
| Text input | Valid data, empty, max length, special chars (`<script>`, `'; DROP`), unicode, whitespace-only |
| Email input | Valid format, missing `@`, missing domain, IDN domains |
| Password | Min length, max length, special chars, paste behavior, show/hide toggle |
| Select/dropdown | First option, last option, disabled options, keyboard selection |
| Checkbox | Check, uncheck, indeterminate state, required validation |
| Radio buttons | Each option, default selection, required validation |
| File upload | Valid file, oversized file, wrong type, no file, multiple files |
| Date picker | Valid date, past date, future date, boundary dates, manual entry |
| Textarea | Empty, max length, line breaks, paste large content |

### Interactive Elements

- **Modals/dialogs:** Open, close (X, overlay click, Escape key), scroll within, nested modals.
- **Tabs:** Each tab, keyboard navigation, deep-linking to specific tab.
- **Accordions:** Expand, collapse, expand-all, multiple open simultaneously.
- **Tooltips:** Hover trigger, focus trigger, dismiss, positioning at edges.
- **Drag and drop:** Start, move, drop, cancel, keyboard alternative.
- **Infinite scroll:** Initial load, subsequent loads, scroll-to-top, empty state.
- **Search:** Empty query, partial match, no results, special characters, debounce behavior.

---

## State Testing

### Five Critical States

1. **Loading state:** Verify skeleton screens, spinners, or progress indicators appear during data fetching. Check that interactive elements are disabled or hidden until ready.

2. **Empty state:** Test with zero data. Verify helpful messaging and a clear call-to-action (e.g., "Create your first item"). No broken layouts from missing data.

3. **Error state:** Trigger errors (invalid input, network failure, server error). Verify user-friendly error messages, retry options, and no raw error dumps.

4. **Success state:** Complete actions successfully. Verify confirmation messages, redirects, data persistence, and UI updates.

5. **Partial state:** Test with incomplete data (some fields filled, partial API responses). Verify graceful degradation without crashes.

### Additional States

- **Offline:** Disconnect network and verify offline messaging or cached behavior.
- **Slow network:** Throttle to 3G and verify timeouts are handled, loading indicators appear.
- **Stale data:** Open in two tabs, modify in one, verify the other handles stale state.
- **Session expired:** Let the session timeout and verify redirect to login with appropriate messaging.

---

## Cross-Browser Considerations

### Testing Priority Matrix

| Browser | Priority | Key Concerns |
|---------|----------|-------------|
| Chrome (latest) | P0 | Baseline — most users |
| Safari (latest) | P1 | Date inputs, flexbox gaps, WebKit quirks |
| Firefox (latest) | P1 | Form styling, scrollbar behavior |
| Edge (latest) | P2 | Chromium-based, minimal delta from Chrome |
| Mobile Safari | P1 | Touch events, viewport units, safe area insets |
| Mobile Chrome | P1 | Touch targets, viewport behavior |

### Common Cross-Browser Issues

- **CSS Grid/Flexbox:** Gap property support, subgrid availability.
- **Date/time inputs:** Native picker differences, format localization.
- **Scroll behavior:** `scroll-behavior: smooth` inconsistencies.
- **Font rendering:** Anti-aliasing differences, font-weight rendering.
- **Focus styles:** `:focus-visible` support, default outline styles.
- **Clipboard API:** Permissions model differs across browsers.

---

## Network Condition Simulation

### Throttling Profiles

| Profile | Download | Upload | Latency | Use Case |
|---------|----------|--------|---------|----------|
| Fast 3G | 1.5 Mbps | 750 Kbps | 563ms | Mobile baseline |
| Slow 3G | 500 Kbps | 500 Kbps | 2000ms | Worst-case mobile |
| Offline | 0 | 0 | N/A | Service worker/cache testing |
| High latency | Normal | Normal | 2000ms | Distant server simulation |

### What to Verify Under Throttling

- Loading indicators appear promptly (not after content loads).
- Images use lazy loading and responsive sizes.
- Critical CSS is inlined or loaded first.
- API calls have appropriate timeouts.
- Retry logic works for transient failures.
- No duplicate submissions from impatient clicks.

---

## Authentication Flow Testing

### Login Flows

- Valid credentials (happy path).
- Invalid password (error message, no password leak in URL/logs).
- Non-existent user (same error as invalid password to prevent enumeration).
- Account locked after N attempts (verify lockout and messaging).
- Remember me / persistent session.
- OAuth/SSO redirect and callback.
- Multi-factor authentication (MFA) — code entry, backup codes, timeout.

### Session Management

- Session timeout behavior (redirect to login, preserve intended URL).
- Concurrent sessions (login from second device).
- Logout (session invalidation, redirect, cached page behavior).
- CSRF token rotation on sensitive actions.
- Cookie security flags (Secure, HttpOnly, SameSite).

### Authorization

- Role-based access (admin vs user vs guest).
- Direct URL access to unauthorized pages (proper 403, not broken UI).
- API authorization (token in header, not URL params).
- Privilege escalation attempts (modify user ID in request).

---

## Mobile-Specific Testing

### Touch Interaction

- Touch targets minimum 44x44px (WCAG) or 48x48px (Material Design).
- Swipe gestures (carousels, dismissals) work correctly.
- Long press does not trigger unintended context menus.
- Pinch-to-zoom does not break layout.

### Viewport Considerations

- Test at 320px (iPhone SE), 375px (iPhone), 390px (iPhone 14), 428px (iPhone 14 Pro Max).
- Verify no horizontal scrollbar at any supported width.
- Check that fixed elements (headers, footers, FABs) do not overlap content.
- Test with on-screen keyboard visible (input fields not obscured).

---

*Reference for the QA Browser Automation skill. Use alongside Chrome MCP tools for live browser testing.*
