# Spec Writing Guide

Requirement grammar, acceptance-criteria patterns, and worked rewrites. Load this
while drafting a specification or when a linter finding is unclear.

---

## 1. The requirement sentence

Every normative statement follows one shape:

```
The <actor> <modality> <single obligation> <quantified constraint>.
```

Four parts, each load-bearing.

### Actor

A named component, service, or role. Never "the system," never absent.

- **Bad:** "Notifications should be delivered within a minute."
- **Good:** "The notification dispatcher must deliver a queued notification within 60 seconds of enqueue."

"The system" is where accountability goes to die. In a spec with five services, a
requirement on "the system" is a requirement on nobody, and it is discovered to be
unowned during an incident rather than during review.

### Modality

| Keyword | Class | Meaning | Merge gate |
|---------|-------|---------|------------|
| must, shall | mandatory | Non-negotiable; absence is a defect | 1.0 coverage |
| must not, shall not | mandatory | Prohibition; needs a test that asserts the negative | 1.0 coverage |
| should | recommended | Strong default; deviation needs a recorded reason | 0.8 coverage |
| may, can | optional | Permitted, not required | Tracked only |

Use exactly one modality keyword per statement. A sentence containing both "must" and
"should" is two requirements.

Prohibitions deserve particular care: "must not be reissued" needs a test that
attempts reissue and asserts failure. Prohibitions without such a test are the most
commonly uncovered class of requirement, because there is no feature work that
naturally produces one.

### Single obligation

If the sentence joins two verbs with "and", it is two requirements. This matters
because a partial implementation of a compound requirement passes a single test while
satisfying half the obligation.

- **Bad:** "The service must validate the token and log the attempt."
- **Good:** Two requirements, two IDs, two tests.

The exception is when the two clauses are genuinely one atomic operation — "must
write the record and return its ID" describes one transaction. If they can fail
independently, they are separate.

### Quantified constraint

Every adjective carries a number, a unit, and a measurement point.

| Vague | Quantified |
|-------|-----------|
| fast | p95 latency under 200ms measured at the load balancer |
| scalable | sustains 5,000 rps with p99 under 500ms |
| secure | rejects requests without a valid HMAC signature with status 401 |
| reliable | 99.9% monthly successful-response rate |
| user-friendly | completes the flow in 3 screens with no free-text entry |
| minimal downtime | under 30 seconds of 5xx during deploy |

The measurement point is the part authors drop, and it is where the arguments happen.
"Under 200ms" measured at the load balancer, at the service boundary, or in the
client are three different requirements that differ by a factor of ten.

---

## 2. Acceptance criteria

Every mandatory requirement carries at least one criterion in given/when/then form
directly beneath it. The parser attaches indented bullets starting with `Given`,
`When`, `Then`, or `AC` to the requirement above them.

```markdown
- The issuance service must reject requests from tenants holding 10 or more active keys with status 429.
  - Given a tenant with 10 active keys, when POST /keys is called, then status 429 is returned.
  - Given a tenant with 9 active keys, when POST /keys is called, then status 201 is returned.
```

### The boundary rule

Every numeric constraint needs two criteria: one at the boundary and one just inside
it. A requirement with a threshold and one criterion is half-specified — the criterion
proves the constraint fires, but nothing proves it does not fire early.

### Criteria shapes by requirement type

| Requirement type | Criterion shape |
|-----------------|-----------------|
| State transition | Given <starting state>, when <trigger>, then <ending state> |
| Validation | Given <invalid input>, when <call>, then <specific error code> |
| Idempotency | Given <operation already performed>, when repeated, then <no additional effect> |
| Prohibition | Given <forbidden attempt>, when made, then <rejection with code> |
| Performance | Given <load profile>, when <operation> runs, then <percentile> under <bound> |
| Ordering | Given <events out of order>, when processed, then <deterministic result> |

### What is not an acceptance criterion

- "It works correctly" — restates the requirement
- "The tests pass" — circular
- "The user is happy" — not observable at merge time
- "Performance is acceptable" — the requirement's adjective, moved

A criterion is observable, binary, and checkable by someone who did not write it.

---

## 3. Worked rewrites

### Rewrite 1 — the unmeasurable non-functional

**Before:**

> The service should be scalable and performant under load.

Three failures: two unquantified adjectives, no actor, no measurement point. It cannot
be failed, so it will never block a merge, so it is decoration.

**After:**

> The rotation job must complete a 100,000-key sweep in under 90 seconds at p95,
> measured from job start to completion record write.
>   - Given 100,000 active keys, when the sweep runs, then p95 wall time is under 90 seconds.
>   - Given 150,000 active keys, when the sweep runs, then the job completes without OOM.

### Rewrite 2 — the passive obligation

**Before:**

> Audit records must be written for every revocation.

Passive with no actor: which component writes them? In an incident this is the
difference between a five-minute fix and an hour of ownership archaeology.

**After:**

> The audit service must write one audit record per revocation, containing actor, key ID, and timestamp.
>   - Given a revocation, when the audit log is queried by key ID, then exactly one record exists with actor and timestamp.

### Rewrite 3 — the compound requirement

**Before:**

> It must handle several edge cases and/or retries appropriately.

Undefined antecedent, vague quantifier, compound obligation, unquantified adjective —
this single sentence fires four linter rules and means nothing.

**After:**

> The rotation job must retry a failed notification 3 times with exponential backoff starting at 1 second.
>   - Given a notification that fails twice, when the job retries, then delivery succeeds on the third attempt.
>   - Given a notification that fails 3 times, when the job retries, then the key is marked notification-failed and no further attempts are made.

### Rewrite 4 — the hidden decision

**Before:**

> Revoked keys must not be reissued. TBD whether reuse of the key ID is permitted.

A placeholder inside a normative statement means the merge gate would enforce an
undecided obligation.

**After:** move the question out, keep the decided part:

> The issuance service must not issue a key whose secret matches a previously revoked key.
>   - Given a revoked key's secret, when issuance is attempted, then status 409 is returned.

And in Open Questions: "May a revoked key's *identifier* be reused? Blocking: no.
Owner: <name>. Resolve by: <date>."

---

## 4. Precision ratio as a drafting signal

The linter reports a precision ratio: clean normative statements over total normative
statements.

| Ratio | Interpretation | Action |
|-------|---------------|--------|
| Below 0.50 | Draft-quality; the spec is a sketch | Do not circulate for review yet |
| 0.50 - 0.75 | Reviewable, but review will be spent on ambiguity | Fix errors first |
| 0.75 - 0.85 | Good; remaining findings are usually warnings | Circulate |
| Above 0.85 | Precise enough to implement against | Freeze the baseline |
| 1.00 | Either excellent or the spec avoids hard commitments | Check that thresholds exist |

That last row is worth taking seriously. A perfect ratio on a spec with no numbers in
it means the author dodged every quantified constraint rather than met it.

---

## 5. Specs for generated implementations

When a model implements the spec rather than a person, the failure mode changes.
People escalate ambiguity; generators resolve it silently and plausibly.

Additional requirements for a generation-grade spec:

1. **No undefined domain terms.** Every noun that carries meaning appears in the
   Definitions table.
2. **Error behaviour specified per requirement.** Not just the happy path — what
   status, what message, what side effects on failure.
3. **Explicit non-goals.** Generators fill perceived gaps. If persistence is out of
   scope, say so or you will get an ORM.
4. **Interface shapes given literally.** Field names, types, nullability. A generator
   given "returns key metadata" invents seven fields, and the fifth one is wrong.
5. **Ordering and concurrency stated.** Whether operations are idempotent, whether
   ordering is guaranteed, what happens under concurrent calls.

The test for a generation-grade spec: hand it to two people who have not discussed
it. If their implementations differ observably, the spec is underspecified at exactly
the point where they diverged.

---

## 6. Keeping the spec alive

The spec goes stale unless something breaks when it does. Three forcing functions,
in increasing order of effectiveness:

1. **Convention** — "update the spec in the same PR." Works for about three sprints.
2. **Review checklist** — reviewers check spec changes accompany behaviour changes.
   Works while the checklist is new.
3. **Merge gate** — the drift check and coverage gate fail the build. Works
   indefinitely, because it does not rely on anyone remembering.

Only the third survives a deadline. Set the gate narrow enough that it is never
waived: mandatory requirements only, coverage 1.0, drift as an error. A gate waived
twice is not a gate.
