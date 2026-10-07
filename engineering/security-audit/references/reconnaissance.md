# Phase 1 — Reconnaissance and the Coverage Ledger

Reconnaissance produces two things: a short architecture summary every later
agent reads, and a coverage ledger that says exactly what the audit intends to
examine. Nothing is hunted until both exist and the ledger validates.

Reconnaissance is read-only. Scouts read the repository and whatever build and
configuration state is already on disk. They do not run the target, install
anything, or contact a deployed service, registry, identity provider, or cloud
API.

## Before launching scouts

1. Run `audit_run.py init` (see SKILL.md). It creates the run directory outside
   the target, records tier, profile, scope, and budget in
   `run-metadata.json`, and refuses a budget too small to fund reconnaissance,
   critics, and one verifier.
2. Read the `prior_runs` it reports. Prior ledgers and findings change the plan
   (see "Using prior runs").

## Scout assignments

Launch four read-only scouts in parallel. Each reports facts, cites the file
and line for every one using paths relative to the repository root, and writes
no files.

### Scout A — what the product is and how it runs

```text
Read the repository at <target>. Do not use the network and do not run anything.
Report, with file:line references:
1. What the product is, who uses it, who operates it, and which everyday
   actions carry trust (login, payment, sharing, admin, publish).
2. The technology in use and how it is built, plus each way of deploying it
   that the repository itself describes.
3. Entry points and the subsystems behind them.
4. Build and test commands that would work offline with what is already
   installed, where they write, and which target-controlled inputs they read.
5. Whether local documentation or dependencies point to a well-known
   comparable system. Say "none" when nothing in the source supports one.
6. Toolchains or runtime facts that are missing and would limit local checks.
Facts only. No findings, no recommendations.
```

### Scout B — principals, authority, and controls

```text
Read every part of the repository that decides who someone is and what they
may do. Report, with file:line references:
1. Each kind of principal, from least to most trusted, and what each can do
   by design.
2. How identity is established at each entry surface.
3. Where per-object and per-tenant decisions are made.
4. Authority held by non-human actors: processes, workloads, CI jobs,
   plugins, model-driven tools, devices, local helpers.
5. Paths that change privilege: elevation, confirmation, revocation,
   recovery, fallback.
6. For each control, whether it is visible in source or depends on a
   deployment fact the repository does not contain.
Do not infer what a live deployment does.
```

### Scout C — entry surfaces, copies, and sinks

```text
List every place lower-trust input enters the system: HTTP and browser, RPC
and messages, files and archives, CLI arguments, environment and config,
plugins and dependencies, CI inputs, cloud events, model context and tool
arguments, mobile and deep links, local IPC.
For each, follow the input through its main transformations, note every
stored or derived copy (cache, index, log, export, queue), and name the
security-relevant sinks it reaches. Note limits the source enforces and any
second route to the same effect.
Give file:line references. Be complete. Do not send or execute any input.
```

### Scout D — what can run locally and what only a deployment knows

```text
Read tests, build files, manifests, packaging, and environment overlays.
Report, with file:line references:
1. Existing offline tests or fixtures that could exercise a trust boundary
   with dummy data.
2. Processes that could run against loopback only, with no shared dependency.
3. Commands that fetch dependencies, publish, call paid or provider APIs, or
   touch shared state. These are prohibited for this run.
4. Controls that only a deployment can establish (proxy rules, provider
   settings, identity policy, network topology).
5. Which code path each deployment mode selects, where the repository makes
   that deterministic.
6. Whether this machine can enforce the sandbox the audit requires: no
   external network, an allowlisted environment, a read-only target,
   scratch-only writes, and CPU, memory, process, file-size, disk, and time
   limits. State each control as available or missing.
```

Add a focused scout for a subsystem or deployment mode these four leave
unmapped. If the budget cannot pay for it, do not drop the area: seed it as a
`deferred` unit with the reason and disclose it in the report.

## Using prior runs

A second run is expected, not exceptional — independent passes surface
different defects. Read every prior `coverage-ledger.json` and `findings.json`
for the same repository and compare them with the current source, not with the
recorded commit hash alone.

| Prior state | Current source | What to seed | `origin` |
|---|---|---|---|
| `confirmed` record | Path and conditions unchanged | A `planned` unit; the record goes to a fresh verifier, hunters are told to skip that root cause | `carried_confirmed` |
| `confirmed` record | Anything relevant changed | A `planned` unit that hunters work normally | `revalidate_confirmed` |
| `needs_validation` record | Trace still holds | A `planned` unit; the record goes to a fresh verifier with its blocker intact | `carried_needs_validation` |
| `deferred`, `blocked`, or `out_of_scope` unit | Any | Current `planned` work if now in scope | `reopened_gap` |
| `covered` unit | Unchanged | Keep visible; assign after changed and gap units | `recheck_covered` |
| `rejected` record | Unchanged | Suppresses that exact claim only; the unit is still reviewed | — |
| Surface not in any prior ledger | — | A `planned` unit | `new` |

With no prior ledger, every unit has origin `none`. A prior `quick` or scoped
run contributes the evidence it recorded and nothing more — never read it as
"the rest was fine". Record unreadable or incompatible prior files in
`run-metadata.json` rather than treating them as empty.

## The architecture summary

The lead writes `architecture.md` from the scouts' facts. Hard limit: about
1,000 words. It is pasted into every hunter prompt, so every sentence costs
tokens many times over.

1. Product, principals, what each may normally do, and what is protected.
2. Stack, deployment shapes visible in source, and what can run offline.
3. Entry surfaces and the important paths from input to sink.
4. Trust boundaries, each with the strongest control visible in source.
5. Starting paths, repository-relative.
6. A comparable system and the trade-offs it accepts, only when the source
   supports the comparison. Use it to calibrate, never to wave a finding away.
7. Prior-run consequences: gaps reopened, records carried, root causes hunters
   must skip.
8. The companions selected, each with the boundary that justified it, and any
   boundary left out because its companion is outside the tier.

Select a companion because a scout found the boundary it describes, not
because a framework or language name appears in the dependency list.

## Seeding the ledger

`coverage-ledger.json` is `{"schema_version": 1, "run_id": "...", "units": []}`.
Seed one unit for each material combination of **surface**, **boundary**,
**subsystem**, and **attack class**.

```json
{
  "coverage_id": "cu-c565fdde20a55cc15828",
  "refs": {
    "surface": "src/api/orders.py#POST /orders/{id}/refund",
    "boundary": "src/authz/policy.py#require_owner",
    "subsystem": "services/orders",
    "attack_class": "attack-classes.md#Access control"
  },
  "label": "Refund endpoint: owner check on order refunds",
  "starting_paths": ["src/api/orders.py", "src/authz/policy.py"],
  "class_blocks": [
    "attack-classes.md#Access control",
    "data-isolation-and-lifecycle.md#Missing tenant or owner scope"
  ],
  "excluded_blocks": [
    {"block": "attack-classes.md#Injection",
     "reason": "handler takes a numeric ID and a fixed enum; no interpreted sink"}
  ],
  "origin": "none",
  "wave": 1,
  "status": "planned",
  "owner": null,
  "reviewed_paths": [],
  "checks": [],
  "fingerprints": [],
  "unresolved": [],
  "attempts": []
}
```

Rules for the fields:

- **`refs`** are source-derived and stable: a path plus the route, message
  name, or symbol defined in source; the control that defines the boundary; a
  package path; the exact block reference. Never a display name, line number,
  wave, agent, or verdict. The same source object gets the same reference in
  every run. Add `refs.lifecycle` only when a lifecycle mode (setup, migration,
  restore) is a materially different unit.
- **`coverage_id`** is derived from `refs`, never invented:
  `audit_run.py coverage-id --surface ... --boundary ... --subsystem ...
  --attack-class ...`. Identical refs give an identical ID, which is how
  duplicates and cross-run matches are detected.
- **`class_blocks`** is the exact set of blocks the hunter will be given:
  `refs.attack_class` first, then any companion classes. Whenever a companion
  class is listed, the hunter also receives that companion's `Ground rules`,
  `Cross-cutting moves`, and `Evidence bar` sections.
- **`excluded_blocks`** records each block considered and ruled out, with the
  source fact behind the decision. An unexplained absence is a coverage gap
  the critic will raise.
- Units are sorted by `coverage_id`.

Granularity follows the profile: `quick` uses one subsystem reference,
`profile/quick/all`, for everything in scope; `standard` splits by subsystem;
`deep` also splits by lifecycle mode. When the run has a scope, only surfaces
inside it become `planned`; anything else the scouts noticed is still written
down, as `out_of_scope` with a reason.

## Unit states

| Status | Owner | Paths and checks | Fingerprints | `unresolved` |
|---|---|---|---|---|
| `planned` | none | empty | empty | empty |
| `in_progress` | agent ID | empty | empty | empty |
| `covered` | agent ID | filled | empty | empty |
| `candidate` | agent ID | filled | filled | optional |
| `blocked` | agent ID | filled (partial review) | empty | the blocker |
| `deferred`, `out_of_scope`, `not_applicable` | none | empty | empty | the reason |

`python3 scripts/ledger_rules.py` prints this table. Agent IDs match
`^[a-z0-9][a-z0-9_-]{0,63}$`.

Each check names its own `agent_id` and the `reviewed_paths` it covered; the
unit's `reviewed_paths` is the union. A `source` check has
`evidence_file: null`. A `local` check points at a file under
`agents/<that agent>/evidence/`, put there by `promote_evidence.py` and nothing
else. A hunter's check and a verifier's check can sit in the same unit, each
owned by its author.

## Validate before assigning work

```bash
python3 scripts/validate_coverage_ledger.py <run-dir>/coverage-ledger.json \
  --metadata <run-dir>/run-metadata.json
```

Run it after seeding and after every later edit. A ledger that fails cannot
drive an assignment or support a coverage claim. The ledger — not the
architecture summary, the number of agents launched, or a sentence saying
"authentication was reviewed" — is the record of what the audit covered.
