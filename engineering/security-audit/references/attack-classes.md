# Core Attack Classes

The nine classes every audit considers, whatever the breadth tier. Each `##`
heading below is a **block**: the ledger references it as
`attack-classes.md#<heading>` and the lead pastes the whole block into the
hunter's prompt. Blocks are self-contained on purpose — a hunter sees only what
it is given.

Pick the classes reconnaissance supports. A CLI with no network listener does
not need a session-handling hunter; a multi-tenant API needs access control
split per subsystem. Add target-specific classes when the product has a trust
decision none of these names.

Two rules apply to every block:

- A class is a place to look, not a finding. A candidate still needs a
  lower-trust actor, a control that should have stopped them, a traced path
  past it, and a concrete result.
- Evidence stops at source review and bounded local checks. No block licenses
  traffic to a deployed system.

## Companion routing

When reconnaissance finds one of these boundaries and the run's tier includes
the companion, select blocks from it alongside the core class.

| Boundary found in source | Companion | Tier |
|---|---|---|
| Sessions, CSRF, JWT, OAuth/OIDC, SAML, MFA, API keys, mTLS, proxies, caches | `web-protocol-and-auth.md` | focused, full |
| Prompts built from untrusted text, RAG, agent memory, tool calls, MCP | `ai-and-llm.md` | focused, full |
| Dependency resolution, CI workflows, release, signing, updaters, plugins | `supply-chain-and-release.md` | focused, full |
| IAM, infrastructure as code, containers, serverless, ingress, secrets config | `cloud-and-deployment.md` | focused, full |
| SPA rendering, extensions, service workers, cross-window messaging, CORS | `client-side.md` | full |
| Multi-tenant stores, caches, search, export, backup, deletion, restore | `data-isolation-and-lifecycle.md` | full |
| Native apps, deep links, webview bridges, privileged helpers, local sockets | `desktop-mobile-and-local-ipc.md` | full |
| C/C++/unsafe Rust, parsers, FFI, loaders, JITs, kernel interfaces | `memory-safety-and-binary.md` | full |
| gRPC, custom wire formats, queues, brokers, webhooks, streaming | `protocols-rpc-and-messaging.md` | full |
| Untrusted work consuming shared CPU, memory, workers, quota, or spend | `resource-exhaustion-and-availability.md` | full |

A boundary whose companion is outside the tier is not skipped silently: seed a
unit for it under the closest core class and mark it `out_of_scope` with the
reason `companion_outside_tier:<file>`, so the report names the gap and a later
run can pick it up.

## Injection

Follow untrusted input from where it enters to where it is interpreted. The
sink decides the bug, so list the sinks first:

- **Query and command builders** — SQL, NoSQL operators, shell command lines,
  LDAP and XPath filters, ORM raw fragments, search DSLs.
- **Renderers and templates** — HTML, server-side templates, email bodies,
  PDF and document generators, log lines read by another system.
- **Path and URL builders** — filesystem paths, redirect targets, request
  URLs, header values, cache keys.
- **Decoders** — deserializers, expression evaluators, regex compiled from
  input, format strings, dynamic imports.

Then look past the direct path:

- Stored-then-used: a value written safely and read later by code that trusts
  the store.
- Names as well as values: object keys, column names, header names, filenames,
  sort and filter parameters.
- Secondary systems: logs, metrics labels, search indexes, analytics exports,
  message payloads consumed elsewhere.
- Encoding seams: a check on the decoded form and a use of the raw form, or
  the reverse.

The check that matters is at the sink: parameter binding, context-correct
encoding, an allowlist of structural tokens. A filter upstream of a second
decode is not a control.

## Access control

Establish, for each state change and each read of protected data, which
principal is allowed and where the code decides. Presence of a check is not
the question; whether it is the right check, on the right object, on every
path, is.

- Does every route to the same effect apply the same decision — the main
  handler, the bulk variant, the import, the internal API, the legacy version?
- Is the object loaded by an identifier the caller supplies, and is ownership
  or tenancy checked on the loaded object rather than on the request?
- Can a request field set something the permission model meant to fix: owner,
  tenant, role, price, status, a foreign key?
- Are there handlers that require a login and nothing else?
- Do list, search, count, and export operations filter per item, or only gate
  the operation?
- Are role and membership changes re-read at decision time, or cached in a
  token or session that outlives the change?

When the model is complex, split the work: one unit for who can authenticate
as what, one for per-object decisions.

## Files, fetches, and resource handling

Anywhere the target opens, writes, fetches, unpacks, or parses something the
caller names:

- **Paths** — traversal through `..`, absolute paths, encoded separators,
  symlinks inside an upload or archive, case and Unicode normalization
  differences between the check and the filesystem.
- **Server-side fetches** — a URL, host, or webhook target the caller
  controls; checks that validate the first URL but not the redirect; resolving
  the name twice; differing URL parsers between the validator and the client.
- **Archives and uploads** — entries that escape the extraction root, type
  decided by extension or client header, files served back from an executable
  or same-origin location.
- **Decoding** — object deserialization of untrusted bytes, XML with external
  entities, parsers with unbounded nesting.
- **Check-then-use gaps** — a file validated and then reopened by name, a temp
  file created in a shared directory with a predictable name.
- **Native memory** — if the target has unsafe code and the tier excludes the
  memory-safety companion, record the surface and mark it out of scope.

## Cryptography and secrets

Look at how the code uses primitives, not which library it imports.

- Security values from a non-cryptographic generator: tokens, reset codes,
  session IDs, nonces, filenames that act as capabilities.
- Secrets in source, fixtures that ship, logs, error bodies, URLs, client
  bundles, or analytics events.
- Verification that can be skipped: a signature checked only when present, an
  algorithm chosen by the message, a comparison that returns early.
- Encryption without authentication, reused nonces or IVs, keys derived from
  low-entropy input without a slow KDF.
- Failure behaviour: when decryption, verification, or key loading fails,
  does the code stop, or continue with a default?
- Key scope: one key for several purposes or tenants, no rotation path, old
  keys accepted indefinitely.

A weak primitive is a finding only when the value it protects matters and an
actor can reach it. Otherwise it is a hardening note.

## Business logic

Scanners do not find these; reading the workflow does. For each multi-step
process that moves money, grants access, or changes ownership:

- **Order of steps** — skip one, repeat one, run them out of order, resume an
  abandoned flow, replay a completed one.
- **Partial failure** — step two fails after step one committed. What state
  remains, and who benefits from it?
- **Concurrency** — two requests that each pass the check before either
  writes: balance, quota, coupon, inventory, approval, uniqueness.
- **Numbers** — negative, zero, fractional, very large, wrong unit, wrong
  currency, rounding in the caller's favour, string where a number is expected.
- **Equivalent operations** — a limit enforced on one operation and absent on
  another that reaches the same outcome.
- **Trusted stored data** — values assumed valid because the write path
  validated them, when a second write path does not.
- **Time** — expiry at the exact boundary, clock differences between
  services, time zones, windows that reset.
- **Defaults** — behaviour when configuration is missing, a flag is off, a
  dependency is down, a migration is half applied.

State the business rule in one sentence before claiming it is broken.

## Feature abuse and data exposure

Working features used for something they were not meant to do.

- **Export, report, backup** — includes rows above the requester's access,
  other users' records, deleted or draft items, fields the UI hides.
- **Import, restore, sync** — overwrites existing records, skips validation
  the normal write path applies, writes into collections the user cannot
  otherwise modify.
- **Search, filter, sort, autocomplete** — reveals existence or values of
  records the caller cannot read; ordering by a hidden field leaks it.
- **Different answers for different reasons** — distinct errors, status
  codes, sizes, or timing for "does not exist" versus "not yours", in login,
  reset, invite, and lookup flows.
- **Previews, drafts, share links** — a token meant for one item that opens
  more; unpublished content reachable through feeds, sitemaps, or listings.
- **User-supplied callbacks** — webhook, notification, avatar, or import URLs
  the server fetches.

## Chained trust gaps

Steps that are each acceptable alone and unsafe together. Build the chain only
from links the source establishes.

- **Guarantee versus assumption** — write down what component A actually
  guarantees about a value (type, length, normalization, tenant) and what
  component B assumes. The gap is the finding.
- **Second-order use** — a slug becomes a path, a display name becomes a
  header, a stored string becomes a template, a field name becomes a query key.
- **Capability growth** — a token, API key, plugin, or delegated grant that
  gains reach after refresh, caching, role change, or composition with another
  feature.
- **Ordering windows** — between validate and consume, revoke and cache
  expiry, soft delete and purge, setup and first use.
- **Undo paths** — restore, undelete, rollback, and cancel must apply today's
  ownership and validation, not the rules in force when the record was made.

Every link is a prerequisite. If one is not established, the chain is a
`needs_validation` lead with that link as the blocker, or nothing.

## Wildcard

No category is assigned. Look for what the other units will not.

- Code that is odd, old, or apologetic: `legacy`, `compat`, `temp`, `hack`,
  comments explaining why something is safe.
- Half-finished or experimental features, and flags that expose them.
- What the API accepts that the product's own client never sends.
- Routes, parameters, and headers registered in code but absent from docs.
- Features combined that were built separately: preview with caching, import
  with plugins, impersonation with API keys.
- Assumptions about the environment: case-sensitive filesystem, accurate
  clock, trusted DNS, local-only database.
- What the tests cover, and the edge cases nobody wrote a test for.
- Version history, where it is available locally: reverted fixes, removed
  checks, secrets committed and later deleted.

Follow anything strange until you can say in one sentence why it is safe or
what boundary it breaks. The evidence bar does not drop because the unit is
open-ended.

## Baseline exposures

Literal, exhaustive, unglamorous. Everyone assumes someone else checked these.

- Credentials, keys, tokens, or private key material in the repository,
  including fixtures, examples, and seed data that could work in production.
- Comments admitting a missing control (`TODO auth`, `FIXME validate`).
- Debug or development modes that a request parameter, header, or environment
  variable can switch on.
- Diagnostic, admin, metrics, health, or config endpoints with no access
  check.
- Ignore rules that fail to cover secrets, uploads, and local config.
- Unpinned dependencies and lockfile entries with known advisories.
- Dynamic code evaluation fed by input.
- Cross-origin policy that reflects any origin with credentials.
- Session cookies missing transport and script-access restrictions.
- Redirect parameters passed through unchecked.
- Error responses that return stack traces, queries, or filesystem paths.

Check every item and record the result for each, including "not present". A
match is a starting point, not a finding: confirm the flagged value is real,
reachable, and protects something before reporting it.
