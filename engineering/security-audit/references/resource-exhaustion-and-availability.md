# Resource Exhaustion and Availability Companion

Tier: full.

## Select this companion when

Work requested by a lower-trust actor consumes something shared: CPU, memory,
disk, connections, worker threads, queue capacity, rate or quota allowances,
or money the operator pays for (compute, storage, third-party API calls).

Availability findings are easy to overstate. This file exists to keep them
honest: a cheap request, a disproportionate cost, and somebody other than the
requester who pays.

## Ground rules

```text
- A finding needs asymmetry and a victim. Show that a small input causes
  large work, and that the cost lands on other users, a shared service, or
  the operator.
- Reason from source: complexity, bounds, limits, and timeouts. Demonstrate
  with one small input and a measurement, inside the sandbox, with strict
  CPU, memory, and time caps. Scale by argument, not by load.
- Never send volume at anything. No stress tests, no floods, no attempts to
  exhaust a real or shared process, and nothing that incurs spend.
- Rate limits, quotas, autoscaling ceilings, and upstream timeouts set
  outside the repository are unknown. If one of them would contain the
  effect, the lead is needs_validation with that limit as the blocker.
- "No rate limit" is a hardening note until you tie it to a specific
  expensive operation and a specific shared resource.
- Slowness or failure that affects only the requester's own session is not a
  finding.
```

## Hunting classes

### Superlinear parsing and matching

Input that drives quadratic or exponential work: backtracking regular
expressions on caller text, nested structures parsed recursively, repeated
string concatenation or rescans, sort and comparison functions on crafted
keys, hash collisions.

### Decompression and expansion

Small input that expands enormously: compressed uploads and request bodies,
archives with many or huge entries, image and document formats with declared
dimensions, entity or reference expansion, templates and macros.

### Query and downstream amplification

One request that causes many or expensive downstream operations: unbounded
page sizes, deep or wide graph queries, filters that defeat indexes, fan-out
to other services, per-item calls inside a loop over caller-supplied lists.

### Unbounded buffering and cardinality

Data accumulated in memory or storage with no cap: request bodies, streaming
uploads read whole, in-memory caches and maps keyed by caller input, metric
labels and log fields with unbounded distinct values, per-user objects with
no count limit.

### Handle and temporary resource leaks

Descriptors, connections, locks, temporary files, or sessions acquired per
request and not released on error, timeout, or disconnect.

### Work that survives cancellation

A client disconnects or a request times out and the expensive work
continues, so cost can be started cheaply and repeatedly.

### Expensive work before authentication

Costly operations reachable before the caller is identified or limited:
password hashing on arbitrary input, signature verification of large
payloads, upload processing, account lookups, report generation behind an
unauthenticated link.

### Quota scope and reset gaps

Limits keyed on something the caller controls or can rotate — an address
header, an account they can recreate, a key they can mint — limits applied on
one route to a resource and missing on another, and counters that reset or
are not shared across instances.

### Worker and pool starvation

A small number of slow or blocking requests occupying a shared pool: sync
calls on an async loop, requests that hold a database connection while
waiting on something slow, one tenant's jobs ahead of everyone's in a single
queue.

### Reachable crash or deadlock

Input that terminates or hangs a process serving others: uncaught exceptions
in shared workers, assertion failures, stack exhaustion, lock cycles.
Establish that the process is shared and what restarts it.

### Retry storms and fail-open

Failure handling that multiplies load — unbounded or synchronized retries,
retries at several layers — or that drops a protection when a dependency is
slow: a limiter, a validator, or an authorization cache that allows on
timeout.

### Poison messages and head-of-line blocking

A message or job that always fails and is always retried, blocking the
partition or queue behind it, with no cap on attempts and no quarantine.

### Unsafe recovery

Restart, replay, or cache-warm procedures that reprocess attacker-supplied
input, re-trigger the original fault, or come up with limits and protections
not yet in force.

## Cross-cutting moves

- For each expensive operation, write the cost as a function of something the
  caller controls, then look for the bound on that input.
- Find every limit and ask what it is keyed on and where it is enforced.
- Check the timeout at each hop, and whether the work stops when it fires.
- Look for the shared thing: one pool, one queue, one lock, one process, one
  bill.
- Measure once with a small input and a doubled input; the ratio is the
  evidence.

## Evidence bar

- Confirmed needs a source-level bound analysis plus one bounded local
  measurement showing the asymmetry — for example, input doubled and time
  quadrupled — and a shared resource named in source.
- Without a sandbox, or where an external limit might contain the effect,
  record `needs_validation` with the limit or the measurement as the blocker.
- Severity is capped by what was shown. An unauthenticated request that stops
  a shared service can be high; degraded latency for a single tenant, or cost
  that scales linearly with the requester's own usage, is low or a hardening
  note.
- Never rate availability findings on an untested claim that "enough
  requests" would take the system down.
