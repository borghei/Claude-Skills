# Phases 3–6 — Validation, Records, Verification, Reporting

A hunter's candidate is a claim. It becomes a finding only after an agent that
did not write it has tried to break it, the record has passed the validators,
and a second fresh reader has checked the record against the source.

## Phase 3 — Try to refute every candidate

Give each unique candidate — both proposed `confirmed` and proposed
`needs_validation`, plus every record carried from a prior run — to a fresh
verifier that took no part in hunting it. One candidate per verifier.

The verifier receives: the candidate, the checks and evidence files from its
linked units, the parts of `architecture.md` needed to read the path, the
`Evidence bar` of each companion involved, the three record definitions from
`assets/findings.schema.json`, and any prior record with the same fingerprint.
It does not receive another verifier's opinion.

### Verifier prompt

```text
Someone else produced the candidate below. Your job is to disprove it using
the repository and, where permitted, a small local check. If you cannot disprove
it, say exactly what it does and does not establish.

Do not contact any deployed or shared system. Run target code only inside the
sandbox the lead confirmed (no external network, allowlisted environment,
read-only target, scratch-only writes, resource and time limits). If the
sandbox is not available, do not run anything; that missing control becomes a
blocker.

1. Open every file and line the candidate cites. Is the entry really reachable
   by the stated actor? Is the sink really where the trace says it ends?
2. Look for whatever would stop this: input checks, identity and permission
   decisions, canonicalization, protections the framework applies by default,
   sandboxing. The hunter may have missed one.
3. For a proposed confirmed candidate, reproduce the smallest result yourself
   when you safely can. Check the inputs, the preconditions, and who or what
   is affected. Do not go beyond that result.
4. Check that the ratings and the suggested fix claim no more than the
   evidence shows.
5. Where the candidate is offered as needs_validation, test the blocker: can
   the source or a local check really not settle it? If the source disproves the
   trace, reject. If the fact is still decisive and still unknown, keep it and
   make the resolution steps exact and harmless.
6. Keep the fingerprint unless you found a different root cause.

Return exactly one JSON object, nothing else:
{"decision": "confirmed | needs_validation | rejected", "record": { ... }}
The record must match that decision's definition in the schema. Your record
replaces the hunter's wording.
```

### Deciding

- **Promote** `needs_validation` to `confirmed` only when the verifier itself
  established the whole path and a bounded observed result.
- **Demote** `confirmed` to `needs_validation` when one specific deployment or
  runtime fact is still unknown.
- **Reject** when the source, local behaviour, a visible control, an absent
  consequence, or an impossible precondition refutes the claim.

`needs_validation` is for a specific, source-grounded hypothesis with a named
missing fact. It is not a shelf for ideas nobody could support.

The lead then: promotes any evidence the verifier produced, adds the
verifier's check to the linked unit under the verifier's own `agent_id`
(the unit keeps its original owner), and keeps one final record per
fingerprint. For a carried record whose unit was seeded `planned`, the
verifier becomes the unit's owner and its re-check moves the unit to
`candidate`. If a verifier returns anything other than the single JSON object, throw the
result away and give the candidate to another fresh verifier.

When there are more candidates than the budget can verify, hunting ends.
Verify as many as the budget allows, taking them in fingerprint order, and set
`run_status` to `incomplete`
with `incomplete_reason: "validation_budget_exhausted"`. An unvalidated
candidate stays in the ledger only. It never enters `findings.json` under any
verdict.

## Phase 4 — Records

The lead writes every decided record, sorted by fingerprint, into
`{"schema_version": 1, "run_id": "...", "findings": [...]}`. The verdict
decides the fields; the schema rejects anything else.

| Field | `confirmed` | `needs_validation` | `rejected` |
|---|---|---|---|
| `fingerprint`, `title`, `summary`, `trace`, `evidence` | required | required | required |
| `root_cause`, `violated_invariant`, `actor`, `affected` | required | — | — |
| `preconditions`, `reproduction`, `fix`, `severity`, `confidence` | required | — | — |
| `suspected_root_cause` | — | required | required |
| `blockers`, `resolution` (`local` and/or `owner_check`) | — | required | — |
| `rejection_reason` | — | — | required |

Notes on the fields that carry the weight:

- **`trace`** — ordered steps of `entry`, `flow`, `sink`. A multi-step trace
  starts with `entry` and ends with `sink`. Files are repository-relative.
- **`reproduction`** — written in the target's own interface, which is not
  always HTTP: a function call for a library, a fixture for a parser, a command
  for a CLI, a message for a consumer, a rendered policy for infrastructure.
  `inputs` holds the minimum test input. `observed` is what actually happened
  locally, stated plainly.
- **`fix`** — the rule the code must uphold, the smallest edit that makes it
  hold at the point where the decision is actually taken, and the regression
  test that would have caught it. The audit describes the fix; it does not edit the target.
- **`severity`** — likelihood and impact rated separately with reasons.
  `overall` may not exceed `impact`. A `needs_validation` record has no
  severity at all.
- **`resolution.owner_check`** — something the system's owner observes in
  their own environment (a config value, a route, a policy). It is never an
  instruction to probe a live target.

Rejected records are kept so the next run does not raise the same unsupported
claim again without new evidence.

```bash
python3 scripts/validate_findings.py <run-dir>/findings.json
python3 scripts/validate_coverage_ledger.py <run-dir>/coverage-ledger.json \
  --metadata <run-dir>/run-metadata.json \
  --findings <run-dir>/findings.json --run-dir <run-dir>
```

Fix every error before continuing. Passing means the records are well formed
and consistent with the ledger. It does not mean they are true — that is
Phase 5.

## Phase 5 — Check the final records with fresh eyes

Every `confirmed` and `needs_validation` record now gets its own new
read-only reader; these can run side by side. Each reads the record as written,
not the hunter's notes.

For a `confirmed` record it verifies: every cited path and line; that the
entry interface and input shape are real; each precondition and each control
on the path; who is affected and that the stated impact was demonstrated; that
severity does not exceed impact; and that the fix enforces the invariant
instead of moving the trust somewhere else.

For a `needs_validation` record it verifies: the cited code exists and backs
the suspected root cause without overreaching; each blocker is decisive and
cannot be settled locally; the lead names a boundary and a concrete possible
result; and the resolution steps are exact and harmless.

It returns one JSON object: `{"outcome": "accepted", "fingerprint": "..."}` or
`{"outcome": "revise", "why": "...", "record": {...}}`.

A replacement is **material** if it raises the verdict, or changes the root
cause, trace, reproduction input or result, demonstrated impact, or severity.
A material replacement is not applied directly. It goes to another fresh
verifier — one that did not hunt, validate, or propose it — and is applied only
when that verifier returns `accepted`. If independence or budget runs out,
the contested record comes out of `findings.json`, its unit stays an
unresolved candidate, and mark the run `incomplete` with the reason. Wording
and line-number corrections that change no meaning may be applied directly.

Re-run both validators after every applied replacement. In a `quick` run,
Phases 3 and 5 are done by the same single fresh verifier per candidate; every
other profile keeps them separate. No profile skips independent review of a
`confirmed` record, and unresolved leads are verified too — a misleading lead
costs the owner real time.

Set `run_status: "complete"` only when every candidate in the ledger has a
final record and every retained record has passed this phase.

## Phase 6 — Write the reports

Run the final gate first:

```bash
python3 scripts/validate_coverage_ledger.py <run-dir>/coverage-ledger.json \
  --metadata <run-dir>/run-metadata.json \
  --findings <run-dir>/findings.json --run-dir <run-dir> --final
python3 scripts/audit_run.py summary --run-dir <run-dir>
```

The reports are derived from the records, the ledger, and the retained
hardening notes. Prose never changes a verdict, a severity, a blocker, or a
demonstrated impact. `assets/report_template.md` gives the layout.

### `REPORT.md`

1. **Run facts** — tier, profile, scope, source ref, budget and agents spent,
   prior runs used, and the statement that evidence came from source review
   and sandboxed local checks only. A `core` or `focused` tier, a `quick`
   profile, a scoped run, a budget-limited run, or an incomplete run says in
   the first paragraph that it is a partial pass and why.
2. **Posture** — one short paragraph.
3. **Confirmed findings table** — severity, title, boundary, observed result.
4. **Each confirmed finding** — location, actor, bounded reproduction,
   preconditions, result, impact, why it has this priority, smallest fix.
5. **Needs validation** — a separate table: title, trace, exact blocker, local
   next step, owner check. No severity, and never described as a vulnerability.
6. **Hardening notes and good patterns found.**
7. **Coverage** — the `audit_run.py summary` tables: unit counts by status,
   every deferred, blocked, and out-of-scope unit with its reason, and the
   final critic's result.

Rejected records are not findings. Mention a rejected fingerprint only to
explain a coverage decision.

### `FINDINGS-DETAIL.md`

For each `confirmed` record rated medium or above: the full trace and
evidence, the dummy actor and the dummy resource affected, the exact input and
steps, the observed output and the rule it breaks, the preconditions, and the
fix with its regression test.

### `NEEDS-VALIDATION.md`

For each unresolved record: the trace, the verified evidence, the exact
blocker, the boundary at stake, and each resolution step. These are leads
ranked for follow-up. They carry no severity and include no instructions for
testing a live system.

### Proportion

A run with no confirmed findings says so, states what was and was not covered,
and stops. Do not manufacture low-severity findings to fill a table.
