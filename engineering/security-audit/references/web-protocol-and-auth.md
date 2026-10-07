# Web Protocol and Authentication Companion

Tier: focused, full.

## Select this companion when

Reconnaissance found code that parses or forwards HTTP itself, sits behind or
acts as a proxy, cache, CDN, or gateway, or implements sign-in: sessions,
cookies, CSRF defences, JWT, OAuth or OIDC, SAML, MFA, passkeys, recovery,
account linking, API keys, or client certificates.

Use it with the core `Access control` and `Injection` classes, not instead of
them. This file covers how identity is established and carried; the core
classes cover what an established identity may do. Split large targets into
separate units for protocol handling, session, federation, and recovery.

## Ground rules

```text
- An absent header, flag, or recommended setting proves nothing alone.
  Show the request an attacker sends, the victim or resource affected, and the
  result.
- Identity must be bound at every hop. Name what binds the credential to the
  user, to the client, to the request, and to the intended recipient, and show
  which binding is absent.
- Behaviour of a proxy, CDN, load balancer, identity provider, or browser that
  is not in the repository is unknown. If the defect depends on it, the lead
  is needs_validation with that behaviour as the blocker.
- Two components reading the same bytes differently is the pattern to hunt:
  front end versus back end, validator versus consumer, cache key versus
  response.
- Test with two dummy accounts and a local instance only. Never send requests
  to a deployed host or a real identity provider.
```

## Hunting classes

### Request framing disagreement

Where the target parses HTTP or forwards it, compare how each layer decides
where a request ends: conflicting or repeated length headers, chunked encoding
variants, bare line feeds, header folding, upgrade and tunnel handling,
HTTP/2-to-1 downgrades. The defect is a second request hidden from the layer
that applies the security check. Custom parsers and hand-written proxies are
the priority; a framework default is rarely the bug.

### Cache poisoning through unkeyed input

A response varies on input the cache key ignores: a forwarded host, a scheme
header, a query parameter stripped from the key, a cookie. Find where the
application reflects or acts on that input, then check what the cache
configuration in the repository keys on. Stored harm to other users is the
result to establish.

### Cache deception and private responses

A response containing one user's data is stored and served to another. Look
for path-suffix tricks that make a private route look static, missing or
overridden cache directives on authenticated responses, and normalization
differences between the cache and the router.

### Host and forwarded-header trust

Code that builds links, reset URLs, redirects, tenant selection, or
allowlist decisions from `Host` or forwarded headers. Establish which hop is
supposed to set the header and whether the application accepts it from anyone.
Password-reset links built from a caller-supplied host are the classic result.

### Response header injection

Caller-controlled text placed in a response header or status line without
removing line breaks: redirect targets, filenames in disposition headers,
cookie values, custom headers echoing input.

### Cross-site request forgery

State-changing requests that a third-party page can cause a logged-in browser
to send. Check every method the route accepts, content types that bypass
preflight, token validation that passes when the token is absent, tokens not
tied to the session, and same-site assumptions broken by sibling subdomains.

### Session fixation and incomplete logout

The session identifier survives a privilege change, or a session stays valid
after logout, password change, MFA reset, or role removal. Trace issue,
rotation, and invalidation, including long-lived refresh and remember-me
tokens and sessions on other devices.

### Cookie scope and transport

Cookies scoped to a parent domain shared with less-trusted sites, session
cookies readable by script or sent over plaintext, and prefix or path rules
that let another application on the domain overwrite them. Only a cookie that
carries authority matters.

### Token verification and claim binding

For signed tokens: is the algorithm fixed by the verifier or chosen by the
token, is the key selected by an untrusted header, are issuer, audience,
expiry, and not-before all checked, and is the token accepted by a service it
was not minted for? Follow each claim the code trusts to the decision it
drives.

### OAuth and OIDC flow binding

Redirect URI matching that allows open patterns, missing or unbound `state`
and nonce, authorization codes not tied to the client or the PKCE verifier,
tokens from one client accepted by another, and identity taken from an
unverified field of the provider's response. Mix-up between several
configured providers belongs here.

### SAML assertion binding

Signature checked on one element while another is consumed, comments or
duplicate nodes changing the parsed identity, assertions without audience,
recipient, or time bounds, and replay of an already used assertion.

### MFA enrollment and downgrade

A second factor that can be added, replaced, or removed with only the first
factor; fallback methods weaker than the primary; "remember this device" that
outlives a credential change; endpoints that skip the factor check.

### Step-up authentication binding

A recent-authentication or elevated state that is not tied to the specific
action, session, or time window, so it can be obtained for a harmless action
and spent on a sensitive one.

### Passkey and WebAuthn verification

Server-side checks on origin, relying-party ID, challenge freshness and
single use, user-presence and user-verification flags, signature counter, and
that the credential belongs to the account being signed in.

### Account linking and identity collision

Accounts merged or matched on an unverified email, case or Unicode variants of
the same identifier, a social login attached to an existing account without
proof of control, and pre-registration takeover.

### Password reset and account recovery

Tokens that are guessable, long-lived, reusable, not invalidated by a newer
request or a password change, or sent to an address the requester can
influence. Recovery through support flows, security questions, and backup
codes is part of the same boundary.

### API key scope and exposure

Keys that carry more reach than the integration needs, are not bound to a
tenant or resource, appear in URLs, logs, or client bundles, or remain valid
after the owner loses access.

### Mutual TLS identity mapping

A valid client certificate treated as authorization: any certificate from the
trusted CA accepted for any role, identity taken from a field the client
controls, a forwarded-certificate header trusted from the wrong hop, and
revocation or expiry failures that fall back to allow.

## Cross-cutting moves

- For every credential, write the four bindings — user, client, request,
  recipient — and find the one the code does not enforce.
- Repeat each check on the legacy route, the mobile API, the admin API, and
  the internal endpoint.
- Change one thing at a time: method, content type, parameter location,
  duplicate parameter, encoding, case.
- Look at failure handling: verification error, provider timeout, missing
  claim, expired key. Fail-open is the finding.
- Compare what is checked at sign-in with what is checked at refresh, reset,
  and link.

## Evidence bar

- Confirmed needs a local reproduction between two dummy principals or a
  dummy client and server, with the request and the wrong outcome recorded.
- A defect that needs a specific proxy, cache, CDN, browser, or identity
  provider behaviour is `needs_validation` unless that component's
  configuration is in the repository and was exercised locally.
- Missing security headers, cookie flags, or rate limits are hardening notes
  unless a traced attack depends on the gap.
- Severity follows what was demonstrated: account takeover, cross-user data,
  or a forced action — not the name of the bug class.
