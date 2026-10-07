# Security Audit Report — {{repo}}

<!--
  Derive every statement from findings.json, coverage-ledger.json, and
  run-metadata.json. Prose never changes a verdict, a severity, a blocker, or a
  demonstrated impact. Delete the comments before delivering.
-->

## Run facts

| | |
|---|---|
| Run | {{run_id}} |
| Source | {{commit}} ({{clean or dirty worktree}}) |
| Breadth tier | {{core / focused / full}} — {{companions in play}} |
| Profile | {{quick / standard / deep}} |
| Scope | {{whole repository, or the listed paths}} |
| Budget | {{agents spent}} of {{budget, or "no cap"}} |
| Prior runs used | {{paths, or "none — this is the first run"}} |
| Evidence | Source review and sandboxed local checks only. No deployed system was contacted. |
| Status | {{complete / incomplete — reason}} |

<!--
  If the tier is core or focused, the profile is quick, the run is scoped,
  budget-limited, or incomplete, the next paragraph must say so plainly:
-->

**This is a partial pass.** {{What limited it, and what that leaves unexamined.}}

## Posture

{{One short paragraph: what the code does well, where the confirmed problems
cluster, and what the unresolved leads have in common.}}

## Confirmed findings

| Severity | Finding | Boundary | Observed result |
|---|---|---|---|
| {{high}} | {{title}} | {{boundary}} | {{one line from reproduction.observed}} |

### {{title}} — {{severity}}

- **Fingerprint:** `{{fingerprint}}`
- **Location:** `{{file}}:{{line}}` ({{symbol}})
- **Who can do it:** {{actor}}
- **What is affected:** {{affected}}
- **Preconditions:** {{preconditions}}
- **Reproduction (local, dummy data):** {{interface}} — {{steps}}
- **Observed:** {{observed}}
- **Why this priority:** likelihood {{level}} ({{why}}); impact {{level}} ({{why}})
- **Smallest fix:** {{fix.strategy}}
- **Regression test:** {{fix.regression_test}}

<!-- Full traces and inputs go in FINDINGS-DETAIL.md for medium and above. -->

## Needs validation

These are source-grounded leads blocked on one fact each. They are not
confirmed vulnerabilities and carry no severity.

| Lead | Trace | Blocker | Local next step | Owner check |
|---|---|---|---|---|
| {{title}} | `{{entry file}}` → `{{sink file}}` | {{blocker}} | {{resolution.local}} | {{resolution.owner_check}} |

## Hardening notes

<!-- Improvements with no demonstrated victim. Not findings. -->

- {{note}}

## Good patterns found

- {{control that held, with its location}}

## Coverage

<!-- Paste the tables from: audit_run.py summary --run-dir <run-dir> -->

{{unit status table}}

{{coverage gap table: every deferred, blocked, and out_of_scope unit with its reason}}

**Final critic:** {{clean / not run — reason / returned N items, deferred}}

**Not covered by this run:** {{companions outside the tier, paths outside the
scope, and anything deferred. State these as open, not as safe.}}

**Suggested next run:** {{tier, profile, and the gaps it should start from}}
