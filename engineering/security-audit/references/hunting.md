# Phase 2 — Coverage-Led Hunting

Hunters are assigned from the ledger, not from intuition. Each one owns a small
set of related units, reads the code behind them at depth, and returns one
structured result. A critic then looks for what the wave missed, and the loop
repeats until the critic finds nothing or the run's limits stop it.

## Assigning a wave

1. Take `planned` units in priority order:
   1. surfaces reachable with no authentication, then lowest-trust
      authenticated surfaces;
   2. boundaries guarding credentials, cross-tenant data, code execution, or
      release authority;
   3. reopened gaps, revalidations, and changed source before re-checks of
      unchanged covered units;
   4. ties broken by `coverage_id`, so two runs order work the same way.
2. Group units for one hunter only when they share a subsystem and a boundary.
   Do not mix unrelated boundaries to save an agent.
3. For each assignment, set the units to `in_progress`, set `owner` to a new
   agent ID, and create `agents/<id>/scratch/`. Validate the ledger.
4. A unit the budget cannot reach becomes `deferred` with the reason. It is
   never left `planned` and never dropped.

Hunters read source, write only inside their own `scratch/`, and return their
result as their final message. They do not edit the target, the shared run
files, or another agent's directory.

## Building the hunter prompt

Assemble these parts in this order. Paste content, not names — a hunter cannot
open the skill's files.

1. Role, in two sentences: find source-grounded failures of a security
   invariant in the assigned units; return exactly one JSON object in the
   result format below.
2. `architecture.md`, whole.
3. The assigned units: `coverage_id`, `label`, `refs`, `starting_paths`.
4. Every block in each unit's `class_blocks`, copied in full. For each
   companion involved, also its `Ground rules`, `Cross-cutting moves`, and
   `Evidence bar`.
5. The unit's `excluded_blocks` with reasons.
6. The hunting method and the candidate gate below.
7. Root causes to skip: for each carried confirmed record, its fingerprint,
   title, and root cause only. Plus the coverage IDs other hunters own.
8. The agent's ID, its scratch path, and the result format, including the
   `confirmed` and `needs_validation` definitions from
   `assets/findings.schema.json`.

### Hunting method — paste into every hunter prompt

```text
HOW TO WORK

You are looking for places where the code fails to enforce a security rule it
is supposed to enforce, and for the smallest change that would fix each one.
You work from source and, where permitted, small local checks with dummy data.
You never contact a deployed system, a provider API, a registry, an identity
service, a shared queue, or another person's account.

Start from a rule, not from a pattern. For each assigned unit:
  1. Who is the lower-trust actor, and what can they already do?
  2. What value, action, or state change do they supply?
  3. Which control is supposed to stop it, scope it, or take it back?
  4. What does the code actually do after that control? Trace it.
  5. What is the smallest wrong outcome: a record that should be unreadable,
     a wrong return value, a state that should be impossible?
  6. What source change and what regression test would enforce the rule?

Read deeply. Stay with the input from the moment it is parsed until it lands
somewhere that matters, through every identity and permission decision, every
rewrite, and every place it is stored or copied. Then read the other routes to
the same outcome: older versions, bulk and retry variants, cancellation,
migrations, error handling. Two routes that both have a check may not have the
same check. And where one module hands a value to another, write down what the
first promises and what the second takes for granted.

Try the unhappy inputs the interface accepts: missing, empty, zero, negative,
maximum, over the limit, duplicated, mixed encodings, stale, revoked,
reordered, concurrent, half-migrated, dependency down, mid-rollback.

Stay in scope. Trace only paths that reach your boundary or that your boundary
relies on. When a rule is settled either way, record it and move on. If you
find a different boundary that needs attention, report it under "uncovered";
do not investigate units another hunter owns.

When a serious candidate reveals a reusable mistake, look for the same mistake
elsewhere in your assigned units. One root cause is one candidate; note each
additional path it affects.

LOCAL CHECKS

Run target code only if the lead confirmed a sandbox with: no external
network, an environment built from an explicit allowlist, a read-only target,
writes confined to your scratch directory, and CPU, memory, process,
file-size, disk, and time limits. If any of those is missing, do not run
anything. Return the lead as needs_validation and name the missing control.

Prefer the narrowest check that settles the question: an existing unit test,
a few-line harness around one function, a small malformed fixture, a dummy
second tenant, a rendered policy. Do not install or download anything. Stop at
the first result that proves or disproves the rule. Never stress a service,
use a real credential, publish anything, or go further than that first result.

Record the exact input, the command, the limits, and the result. Record only
the environment variable names you set deliberately, never the ambient
environment. Files you want kept as evidence stay in scratch; list their
relative paths in your result and the lead will promote them.

WHAT YOU CANNOT SEE

A proxy rule, provider setting, browser behaviour, broker ACL, identity
policy, or network layout that is not in the repository is unknown. Do not
assume it is there and do not assume it is absent. If one such fact decides
the question, return needs_validation naming the exact observation that would
settle it and how the owner can safely make it.
```

### Candidate gate — paste into every hunter prompt

```text
BEFORE YOU REPORT A CANDIDATE

1. You have a complete trace with repository-relative files and line numbers,
   from the entry to the sink, including the strongest control on the way.
2. To propose "confirmed" you also have: a bounded local result you observed,
   a consequence that crosses a boundary you can name, every precondition
   listed, and no layer in source that prevents it.
3. Report what you saw. A crash is a crash, not code execution. Extra work for
   the caller is not an outage. Something a user can do to their own data is
   not privilege escalation.
4. A decisive fact you cannot see or reproduce makes the candidate
   needs_validation: list the blocker, give no severity.
5. A missing best practice with nobody harmed is a hardening note. A candidate
   the source disproves is dropped, not parked as needs_validation.
6. Give each root cause one fingerprint, built from stable source facts
   (for example area:control:defect). Letters, digits, and . _ : / @ + - only.
   No line numbers, wave, agent name, severity, or verdict.
7. If nothing passes this gate, return an empty candidates array. That is a
   valid and useful result.
```

## Hunter result format

```json
{
  "units": [
    {
      "coverage_id": "cu-...",
      "disposition": "covered | candidate | blocked",
      "checks": [
        {
          "agent_id": "hunter-03",
          "reviewed_paths": ["src/api/orders.py"],
          "invariant": "the rule this check tested",
          "method": "source | local",
          "result": "what the source or the bounded check established",
          "scratch_file": null
        }
      ],
      "candidate_fingerprints": [],
      "unresolved": []
    }
  ],
  "candidates": [],
  "hardening": ["concrete improvement that is not a finding"],
  "uncovered": [
    {"surface": "...", "boundary": "...", "subsystem": "...",
     "attack_class": "file.md#Heading", "starting_paths": ["..."],
     "reason": "why this needs its own unit"}
  ]
}
```

Each assigned `coverage_id` appears exactly once. Each entry in `candidates` is
a record shaped like the `confirmed` or `needs_validation` definition in the
schema, with `proposed_verdict` in place of `verdict`. A local check names the
scratch-relative file that holds its output; a source check uses null.

## Updating the ledger

The lead is the only writer.

1. Reject a result that is not a single JSON object, omits an assigned unit,
   or names a unit it does not own. Do not repair it. The unit returns to
   `planned` for a new hunter.
2. For each local check, run `promote_evidence.py` for the named file. On
   success, write the returned path as the check's `evidence_file`. On
   rejection, the check is not evidence: if it was decisive, the candidate
   becomes `needs_validation` with the rejection as a blocker.
3. Copy the checks into the unit, set `reviewed_paths` to the union of their
   paths, and set the status: `covered`, `candidate` with fingerprints, or
   `blocked` with the unresolved fact.
4. Keep the hunter's `hardening` notes on the unit for the report.
5. Turn each accepted `uncovered` entry into a new `planned` unit with origin
   `new`; derive its ID and re-sort.
6. Merge candidates that share a fingerprint or describe the same underlying
   defect. A defect reachable several ways is a single candidate; keep the
   most complete trace and list the other routes.
7. Validate the ledger. Increment `agents_spent` in the metadata.

## The coverage critic

After each wave, one fresh read-only critic receives `architecture.md`, the
whole ledger, the current fingerprints, and the prior-run gap list. It reads
source and proposes coverage — never findings. It returns:

```json
{
  "missing_units": [
    {"surface": "...", "boundary": "...", "subsystem": "...",
     "attack_class": "file.md#Heading", "starting_paths": ["..."],
     "class_blocks": ["file.md#Heading"], "reason": "source-backed gap"}
  ],
  "reopen": [{"coverage_id": "cu-...", "reason": "why it did not really close"}],
  "resolved_prior_leads": ["fingerprint"],
  "clean": false
}
```

Tell the critic to look for: entry points with no unit, a second route to the
same effect nobody checked, lifecycle modes not represented, companion classes
selected with no unit, exclusions without a source reason, units closed on thin
paths or checks, and prior leads no current unit addresses.

For each accepted item:

- **Missing unit** — derive the ID, add it as `planned` with origin `critic`.
  Reject proposals outside the scope or the tier; record tier misses as
  `out_of_scope`.
- **Reopen** — move the unit's current terminal state into `attempts` exactly
  as it stands (`wave`, `status`, `owner`, `reviewed_paths`, `checks`,
  `fingerprints`, `unresolved`) and add the critic's `reopen_reason`. Then
  increment `wave`, clear the live evidence, and set `planned`. The next owner
  must be a new agent, and nothing from the archive is copied forward.

## When hunting stops

| Profile | Loop |
|---|---|
| `quick` | One wave, one critic. Accepted missing units and reopens become `deferred` with reason `quick_profile_single_wave`. No second wave. |
| `standard` | Wave, critic, repeat while the critic produces accepted work. When a critic returns clean and nothing is `planned`, a second, different critic must also return clean. |
| `deep` | As `standard`, plus an independent second pass over `recheck_covered` units. |

Before every wave, check the budget with `audit_run.py budget`: the wave's
critic, the final critic, and the verifier reserve are set aside first, and
hunters get what is left. If the reserves do not fit, launch no hunters; mark
the remaining `planned` units `deferred` and say so in the report.

Coverage is complete only when the final critic is clean and no unit is
`planned` or `in_progress`. Running out of waves, agents, or time is a reason
to stop, and it is stated as one. It is never evidence that nothing was left.
