# <Feature Name> — Specification

**Status:** draft | review | approved | superseded
**Owner:** <name>
**Milestone:** <milestone or release>
**Last parsed:** `python3 scripts/spec_parse.py --spec <this file> --format json > requirements.json`

## Context

Two to four sentences: what problem this solves, for whom, and what happens if it is
not built. No solution detail here.

## Scope

**In scope for this milestone:**
- <capability>

**Explicitly out of scope:**
- <capability> — <why, and where it is tracked>

Requirements outside the milestone boundary must be marked, or the coverage report
will show permanent false gaps and the team will learn to ignore it.

## Definitions

| Term | Definition |
|------|------------|
| <domain term> | <precise meaning in this document> |

Define any term used normatively that a new engineer could interpret two ways.

---

## <Section Name>

Sections become the middle segment of requirement IDs, so name them for stable
concepts (`Rotation`, `Revocation`), not for sprint numbers.

- The <named component> must <single obligation> <quantified constraint>.
  - Given <precondition>, when <action>, then <observable outcome>.
  - Given <edge case>, when <action>, then <observable outcome>.
- The <named component> should <single obligation> <quantified constraint>.
  - Given <precondition>, when <action>, then <observable outcome>.

### Requirement grammar

Every normative statement follows: `The <actor> <modality> <single obligation>
<quantified constraint>.`

- **Actor** — a named component, never "the system" and never absent
- **Modality** — must/shall (gated at 1.0), should (gated at 0.8), may (tracked only)
- **One obligation** — if the sentence contains "and" joining two verbs, split it
- **Quantified** — every adjective carries a number, a unit, and a measurement point

## Non-Functional Requirements

Performance, availability, security, and operability requirements follow the same
grammar. These are the ones most often written as unmeasurable adjectives.

- The <component> must <complete an operation> in under <N ms> at p95 measured at <point>.
  - Given <load profile>, when <operation> runs, then p95 is under <N ms>.

## Open Questions

| # | Question | Blocking? | Owner | Resolve by |
|---|----------|-----------|-------|-----------|
| 1 | <question> | yes/no | <name> | <date> |

Open questions live here, never inline as TBD inside a requirement. A TBD inside a
requirement fails the linter, and correctly so — it means the merge gate would be
enforcing an undecided obligation.

## Decision Record

| Date | Decision | Alternatives rejected | Why |
|------|----------|----------------------|-----|
| <date> | <what was decided> | <what was not chosen> | <reason> |

This is what makes a spec survive its authors. Six months on, the question is never
"what did we decide" — it is "why did we reject the obvious alternative."

## Traceability

Implementations and tests annotate their requirement ID:

```python
def test_rotation_marks_pending_revocation():  # REQ-ROTATION-01
    ...
```

Merge gate:

```bash
python3 scripts/spec_parse.py --spec <this file> --baseline requirements.json --require-acceptance
python3 scripts/trace_coverage.py --requirements requirements.json --code . --min-coverage 1.0
```
