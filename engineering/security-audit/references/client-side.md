# Client-Side and Browser Companion

Tier: full.

## Select this companion when

The repository ships code that runs in a browser or a browser-like host and
makes trust decisions there: single-page applications, browser extensions,
embedded web views, service workers, cross-window messaging, client storage of
tokens or user data, cross-origin configuration, or WebSocket clients.

Server-rendered injection belongs to the core `Injection` class. This file
covers defects that exist because of how the client builds the page, talks
across origins, or stores state.

## Ground rules

```text
- Name the attacker's position: another website the victim visits, another
  frame or window, a lower-privileged user whose content the victim views, or
  a script already running in a less-trusted part of the page.
- Trace from a source the attacker controls (location, referrer, message
  data, storage, fetched content, another user's input) to a sink that acts
  (markup insertion, script evaluation, navigation, a privileged API call).
- Framework escaping is a real control. The finding is where the code steps
  around it: raw HTML insertion, dynamic attribute or URL construction,
  template compilation at run time.
- Browser behaviour that varies by version or vendor, and response headers
  set by infrastructure outside the repository, are unknown unless the
  repository pins them.
- Reproduce in a local browser or a DOM test harness with dummy accounts and
  a local origin. No third-party sites, no deployed hosts.
```

## Hunting classes

### DOM-based script injection

Attacker-controlled data reaches an HTML, script, or URL sink in client code:
raw markup insertion, framework escape hatches, script or handler attributes,
`javascript:` URLs, dynamically chosen component or template names. Include
sanitizers configured too loosely or applied before a later mutation.

### DOM clobbering

Markup the attacker can supply defines named elements that shadow variables or
properties the script later reads as configuration, turning harmless-looking
HTML into control over a URL, a flag, or a script path.

### Prototype pollution

Recursive merge, deep clone, path-set, or query-string parsing that lets input
write to a shared prototype. A pollution primitive needs a gadget: find the
later code that reads the polluted property and what it does with it.

### Cross-window message trust

A message listener that does not check the sender's origin, checks it with a
loose match, or trusts the message's own claims; and a sender that posts
sensitive data to a wildcard target. Follow accepted message data to its sink.

### Cross-site WebSocket use

A socket endpoint that authenticates with ambient cookies and does not check
the origin of the handshake, letting another site open a connection as the
victim and read or send messages.

### Credentialed cross-origin policy

Cross-origin rules that reflect the caller's origin, accept a null origin, or
match by prefix or suffix, while allowing credentials. Establish which
authenticated responses become readable to another site.

### Service worker scope and takeover

A worker script that can be influenced by user content, registered from a
path an attacker can write to, or scoped more widely than the feature that
owns it, giving persistent control over requests for that origin.

### Service worker cache and identity

A worker serving cached responses without regard to who is signed in, or
after logout, so one user's data is shown to the next on a shared device, or
stale authorization persists offline.

### Browser storage of sensitive state

Tokens, keys, or personal data kept in script-readable storage where any
injection or extension reads them; data that survives logout; authorization
decisions made from client-held values the server does not re-check.

### Shared storage and broadcast channels

Several apps or trust levels on one origin sharing storage, channels, or
events, so a less-trusted area can read or forge messages meant for another.

### Cross-site state leaks

Another site can learn something about the victim's state without reading
the response: timing, frame counts, error versus load events, redirect
behaviour, cache probes, navigation length. Matters when the state is
sensitive — membership, search results, identity.

### Opener and window reference leaks

Links and pop-ups that leave the opened page with a reference to the opener,
or expose a window handle that lets a less-trusted page navigate or message a
trusted one.

### Framing and UI redress

Sensitive single-click actions on a page that can be framed by another site.
Establish which action, whether it needs only clicks, and whether the
repository sets framing policy or leaves it to infrastructure.

### Client-side routing and redirect confusion

Router or redirect logic that takes a destination from the URL, accepts
scheme-relative or encoded forms, or parses differently from the server, used
to send a signed-in user or a token to an attacker's page.

## Cross-cutting moves

- List sources and sinks for each route, then connect them.
- Search for every escape hatch the framework offers and justify each use.
- Check the signed-out, signed-in, and just-signed-out states of the same
  page.
- Test encodings and the URL fragment as well as the query; client code often
  reads both.
- Read third-party script inclusion: what loads from where, with what
  integrity guarantee, and with what access to the page.

## Evidence bar

- Confirmed needs a local reproduction: the crafted URL, message, or stored
  value, and the script-controlled result in a local page or DOM harness.
- Where exploitability depends on a response header or browser default not
  fixed in the repository, record `needs_validation` with that fact as the
  blocker.
- Injection that only affects the user who supplies it is not a finding
  unless another user or a higher-privilege context renders it.
- Missing content security policy or framing headers are hardening notes
  unless they are the only thing between a traced input and a sink.
