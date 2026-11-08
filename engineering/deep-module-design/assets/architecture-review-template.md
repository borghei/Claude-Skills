# Architecture Review — <area or codebase>

**Reviewer:** <name>  **Date:** YYYY-MM-DD  **Commit:** <sha>
**Scope:** <paths reviewed and why: requester's pain point, or change-frequency hotspots>
**Inputs read:** glossary <yes/no>, decision records <list>, `module_depth.py` output <attached>

## Summary

<Two or three sentences: the main friction found and the top recommendation.>

## Candidates

### 1. <Concept name from the glossary> — Strong | Worth exploring | Speculative

| Field | Detail |
|-------|--------|
| Modules involved | `path/a.py`, `path/b.py` |
| Friction | <what is hard today; evidence: churn count, bug ids, duplicated rule locations> |
| Tool signals | depth <n>, pass-through <n>%, leaks <list>, changes <n> |
| Proposed deepening | <what merges; what becomes hidden; no signatures yet> |
| Leverage gain | <what callers will no longer need to know> |
| Locality gain | <which rule or change will live in one place> |
| Test impact | <tests that move to the new interface; tests that get deleted> |
| Conflicts with decisions | <none, or "contradicts DR-0007; worth reopening because …"> |
| Ranking (1–3 each) | change <n>, pain <n>, locality <n>, tests <n>, risk <n> = <total>/15 |

**Before**

```
caller -> ServiceA.get -> RepoA.get -> db
caller -> validate_x(); validate_y(); ServiceA.save -> RepoA.save -> db
```

**After**

```
caller -> Intake.place(draft)   [validation, pricing, persistence, events hidden]
```

### 2. <Concept> — <strength>

<Same table and sketch.>

## Top recommendation

<Which candidate to tackle first and why — tie the reason to change frequency
and pain evidence, not to elegance.>

## Rejected or deferred

| Candidate | Reason | Record as decision? |
|-----------|--------|---------------------|
| | | yes / no |

## Next step

Pick one candidate. The review continues with interrogation and at least two
interface designs compared before any code changes.
