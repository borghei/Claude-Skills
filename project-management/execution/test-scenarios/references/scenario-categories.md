# Test Scenario Categories — Deep Reference

## 1. Happy paths

The primary user flow, no errors, no surprises.

### Patterns
- User completes the main task successfully
- All required fields filled correctly
- Default settings used
- Standard network conditions

### Examples (signup form)
- User enters valid email + password, clicks signup → account created, verification email sent
- User clicks Google SSO → authenticated, account created
- User signs up via invite link → joins existing org

### How many
- 1-3 per feature, covering the most common user paths

### What to verify
- Final state correct
- User sees confirmation
- System state updated
- Side effects (emails, webhooks) triggered

## 2. Edge cases

Boundary conditions and unusual inputs.

### Patterns
- Empty input where optional allowed
- Minimum value
- Maximum value
- Just below min / just above max
- Wrong data type
- Very long string
- Special characters / Unicode / emoji
- Whitespace-only
- SQL-injection-like input (verify sanitization)
- Combining edge cases (long + special)

### Examples (signup form)
- Empty email
- Email = "a@b" (technically valid?)
- Email 256 chars long
- Password = 1 char (below min)
- Password = 500 chars (above max)
- Password with no special character (if required)
- Email with emoji ("test💎@example.com")
- Email with Unicode ("test@例え.テスト")
- Email matching existing account
- Password = email (security check)

### How many
- 4-8 per input field; cluster related cases

## 3. Error handling

What the user experiences when things fail.

### Failure modes
- Network failure (offline, slow)
- Server error (500, 502, 504)
- Validation error (400, 422)
- Rate limited (429)
- Auth expired (401)
- Permission denied (403)
- Resource not found (404)
- Conflict (409 — concurrent modification)
- Timeout (request, response, idle)

### What to verify per error
- User sees clear message
- Specific suggested action (retry, contact support)
- No corrupt state left behind
- Logged for debugging
- Doesn't leak sensitive info in error
- Recoverable: user can try again
- Errors don't loop infinitely

### Examples (signup form)
- Submit while offline → "Connection lost. Try again."
- Submit during 500 → "Something went wrong. We've been notified." (not "500 Internal Server Error")
- Submit with duplicate email → "Email already in use. Sign in?"
- Slow network → loading state visible; cancellable

## 4. Empty / first-use / after-action states

Often the worst-tested category. Important because:
- First-use is the first impression
- Empty state is when user is most confused

### Patterns
- First use (no data)
- After deleting last item
- After error left partial state
- After cancel
- After signing out
- After timeout
- Filtered to no results

### What to verify
- Friendly message (not "no data")
- Primary action affordance
- Visual hierarchy guides next step
- Doesn't look broken

### Examples
- Empty dashboard (no projects yet) → "Create your first project" with prominent CTA
- After deleting last item → return to friendly empty state, not error
- Filter returns 0 results → "No matches. Clear filters?"

## 5. Concurrent / race scenarios

Critical for collaborative or data-integrity-sensitive features.

### Patterns
- Two users editing same record
- Two users triggering same action
- Race on resource (last seat in cart, etc.)
- Stale data submitted
- Optimistic locking
- Two API calls in flight; results out of order

### What to verify
- Consistent end state
- Clear conflict resolution UX
- No data loss
- No double-effect (idempotency)

### Examples (collaborative doc editing)
- Two users typing in same paragraph
- One user edits while another deletes the section
- User A saves stale version after User B's edit

### Testing approach
Often hard to automate; combination of:
- Targeted integration tests
- Manual scenarios
- Chaos / fuzz testing
- Production canary observation

## 6. Accessibility

Not optional. Compliance + ethics + actual users.

### Patterns
- Keyboard-only navigation (no mouse)
- Screen reader (VoiceOver / NVDA / JAWS)
- High contrast mode
- Reduced motion preference
- Text resize to 200%+
- Voice control
- Switch control

### What to verify
- All interactive elements keyboard-reachable
- Logical tab order
- Visible focus indicators
- Screen reader reads meaningful labels
- Color isn't the only signal (icon + text)
- Touch targets ≥ 44x44pt (mobile)
- Forms label associations correct
- ARIA roles used appropriately (not over-applied)

### Common gaps
- Modal traps focus → keyboard users stuck
- Carousel auto-advances → screen reader stuck
- Color-only validation states → invisible to color-blind
- Custom checkboxes without ARIA → broken for screen reader

## 7. Security + privacy

Scale with sensitivity of data + actions.

### Auth scenarios
- Logged out user accesses (should redirect / reject)
- Logged in but wrong permission
- Session expired during action
- CSRF (form not from your origin)
- Re-auth required for sensitive action

### Permission scenarios
- Role downgrade mid-session
- Permission denied at API but allowed by UI (or vice versa)
- Multi-tenant isolation (data leak across orgs)

### Data scenarios
- PII in error messages (shouldn't be)
- PII in logs (shouldn't be)
- PII in URLs (should be in POST body)
- Sensitive data displayed when not needed

### Injection scenarios
- SQL injection
- XSS (script in input rendered as HTML)
- Command injection
- Path traversal
- LDAP / NoSQL injection where applicable

### Rate limiting
- Brute-force on auth
- Spam on creation endpoints
- Throttle on expensive operations

## 8. Performance scenarios

For performance-sensitive features.

### Patterns
- Cold load (first time, no cache)
- Warm load (cached)
- Large data volume (1000+ items, 1M+ items)
- Slow network (3G simulation)
- Slow device (mid-tier mobile)
- Concurrent users (10, 100, 1000)
- Long-running operations

### What to verify
- P50, P95, P99 latency
- Memory usage doesn't explode
- UI remains responsive during background work
- Errors don't cascade
- Recovery from degradation

## 9. Localization scenarios

For internationalized products.

### Patterns
- Long-string languages (German, Finnish)
- RTL languages (Arabic, Hebrew)
- Multi-byte characters (CJK)
- Different date / number / currency formats
- Pluralization rules vary by language
- Time zones

### What to verify
- Text fits / wraps; doesn't truncate critical info
- RTL layout flips correctly
- Dates render in user's locale
- Currency formats match locale
- Pluralization rules respected
- DST transitions don't break

## 10. Cross-platform scenarios

For multi-platform products.

### Patterns
- Browsers (Chrome, Safari, Firefox, Edge)
- Mobile browsers
- iOS Safari quirks
- Old browser versions (if supported)
- Desktop OS (macOS, Windows, Linux)
- Mobile OS (iOS, Android — multiple versions)
- Screen sizes (320px → 4K)

### What to verify
- Visual consistency
- Functional consistency
- Performance acceptable on lowest-tier
- Touch + click both work where applicable

## 11. Scenario priorities

Risk-weighted prioritization:

```
P0: Will block ship if broken
P1: Will harm user trust if broken
P2: Will inconvenience user
P3: Edge case; nice to cover
```

Map scenarios to priorities:
- Happy paths: usually P0
- Common edge cases: P1
- Empty state: P1
- Error handling for common errors: P1
- Concurrent (for collab): P0-P1
- Accessibility baseline: P1
- Security (auth, payment): P0
- Rare edge cases: P2-P3

## 12. Per-feature templates

### Form submission
- 1 happy / 5 edge / 5 error / 1 empty / 2 a11y / 3 security

### Browse / list
- 2 happy / 3 edge / 2 error / 2 empty / 3 a11y / 2 security

### Real-time / collaborative
- 3 happy / 4 edge / 4 error / 1 empty / 5 concurrent / 3 a11y / 3 security

### File upload
- 2 happy / 8 edge / 4 error / 1 empty / 1 concurrent / 2 a11y / 6 security

### Payment / financial
- 3 happy / 8 edge / 8 error / 1 empty / 4 concurrent / 3 a11y / 10 security

Adjust for your risk profile.

## Appendix: recommended counts, risk weighting, manual vs automated

### Recommended scenario counts (what `test_scenario_generator.py` checks)

Generated from the script's `RECOMMENDED` table; localization and cross-platform are situational. Starting defaults, adjusted for the feature's risk.

| Feature type | happy_path | edge | error | empty | concurrent | a11y | security | performance |
|---|---|---|---|---|---|---|---|---|
| form | 1-3 | 4-8 | 4-6 | 1-2 | 0-2 | 3-5 | 3-5 | 0-2 |
| browse | 2-3 | 3-5 | 2-3 | 2-3 | 0-1 | 3-4 | 2-3 | 1-3 |
| realtime | 2-4 | 4-6 | 4-6 | 1-2 | 4-6 | 3-4 | 3-5 | 1-3 |
| upload | 1-2 | 6-10 | 4-6 | 1-1 | 1-2 | 2-3 | 5-10 | 1-3 |
| payment | 2-3 | 6-10 | 8-12 | 1-2 | 4-6 | 3-4 | 8-12 | 1-3 |
| bulk | 1-2 | 4-6 | 4-6 | 1-1 | 2-4 | 2-3 | 3-5 | 2-4 |
| generic | 1-3 | 3-5 | 3-5 | 1-2 | 0-2 | 3-4 | 2-4 | 0-2 |

### Risk-weighted scenario selection

Not all scenarios need full QA coverage. Apply:
- **Happy path:** always test
- **Edge cases:** test those that matter (likelihood × severity)
- **Error handling:** test all paths that user can recover from
- **Empty state:** always test (first impression!)
- **Concurrent:** test for data-integrity-critical features
- **Accessibility:** baseline coverage on all UI; full coverage on user-facing
- **Security:** scale with sensitivity (full coverage on auth/payment)

### Manual vs automated

| Scenario type | Default |
|----------------|---------|
| Happy path | Automated (E2E or integration) |
| Edge cases (input validation) | Unit tests |
| Error handling | Mix (mocked errors in unit; real in integration) |
| Empty state | Visual regression + manual |
| Concurrent | Hard — usually manual + targeted integration |
| Accessibility | Automated (axe-core) + manual screen-reader |
| Security | SAST + DAST + manual review for critical paths |
| Performance | Automated load tests |
| Localization | Pseudo-localization + manual spot-check |
