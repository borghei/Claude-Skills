---
name: test-scenarios
description: >
  Writes QA cases from a feature spec across happy, edge, error, empty,
  concurrent, accessibility and security paths, then audits coverage. Use when
  planning QA for a feature, or finding coverage gaps after an incident.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: execution
  updated: 2026-11-08
  python-tools: test_scenario_generator.py
  tech-stack: test-scenarios, qa, edge-cases, acceptance-criteria
  tags:
    - test-scenarios
    - edge-cases
    - qa
    - test-coverage
    - acceptance-testing
---

# Test Scenarios

The agent writes the scenarios from the spec; `test_scenario_generator.py` then audits the list by counting scenarios per category against what the feature type needs. The script generates nothing despite its name.

**Done looks like:** every user goal has a happy path; each input has boundary and weird-but-valid cases; each failure mode has a user-visible outcome; empty states, accessibility and security are covered for every UI feature; concurrency for anything shared or financial; localization when more than one locale ships; at least one P0; the audit exits 0.

## When to Use

- After PRD approval and before implementation, or when sizing test effort in sprint planning
- Reviewing whether a test plan or a PR's tests cover enough
- Bug-bash preparation, or after a production incident to find the missed category

## Categories

Happy path, edge, error, empty state, concurrent, accessibility (`a11y`), security; plus performance, localization and cross-platform when they apply. Examples per category: `references/scenario-categories.md`.

## Clarify First

Before generating scenarios, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Feature type:** form, browse/list, real-time/collab, file upload, payment, or bulk operation (drives the scenario count per category in the coverage rubric).
- **Risk / sensitivity profile:** auth, payment, or PII involved (scales up security and concurrency coverage in the risk-weighted selection).
- **The spec's inputs, outputs, and side effects:** what users provide, expect, and what changes in the system (drives edge cases in Step 3 and error handling in Step 4).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Signup form with full coverage: exit 0
python3 project-management/execution/test-scenarios/scripts/test_scenario_generator.py \
  --input project-management/execution/test-scenarios/assets/sample_scenarios.json --format markdown
```

```bash
# Payment step with no error or security scenarios and a mistyped category: exit 1
python3 project-management/execution/test-scenarios/scripts/test_scenario_generator.py \
  --input project-management/execution/test-scenarios/assets/sample_scenarios_flawed.json --format markdown
```

```bash
# Input schema and flags
python3 project-management/execution/test-scenarios/scripts/test_scenario_generator.py --help
```

## Tools Overview

`test_scenario_generator.py` is the quality gate for this skill. **What the audit checks:** scenario counts per category against the feature type's recommended range (fail when happy path, edge, error or security has none; warn when below range; info when above); unknown category names; concurrency for collaborative features; localization when several locales are supported; cross-platform coverage; at least one P0. It counts; it does not judge whether a scenario is any good.

**Exit codes:** `0` no fail findings · `1` at least one fail (a core category with zero scenarios) · `2` unreadable file, invalid JSON or a top level that is not an object. JSON by default, `--format markdown`, `--output FILE`.

## Workflow

1. **Read the spec** for user goals, inputs, outputs and side effects.
2. **Write scenarios per category.** You know the standard techniques (boundaries, wrong types, 4xx/5xx/timeouts, keyboard and screen reader, authorisation and injection); spend the effort on what is specific to this feature: its side effects, its shared state, its money or PII. Payment and collaboration features need concurrency and idempotency cases; uploads need file-abuse cases.
3. **Weight by risk.** Always cover happy paths and empty states; cover edge cases by likelihood x severity; scale security with sensitivity. Mark P0 the scenarios whose failure would stop the release.
4. **Audit.** Write the list as JSON (schema in `--help`; `assets/sample_scenarios.json`) and run the audit. It must pass with no fail findings; then verify that each under-covered category is either filled or consciously out of scope. Recommended counts per feature type are in the appendix of `references/scenario-categories.md`.
5. **Hand to QA** with the automated/manual split from the same appendix.

## Anti-Patterns

### Only happy paths
**Mistake:** The plan tests that the feature works when everything goes right.
**Why it happens:** Happy paths come straight from the spec; failures have to be imagined.
**Instead:** Write at least the recommended error and edge counts for the feature type before anything else is added.

### "QA will figure it out"
**Mistake:** Scenarios are left to QA after the build.
**Why it happens:** Scenario writing feels like QA's job.
**Instead:** Write them before implementation; QA tests what is specified, and engineers build for cases they can see.

### No concurrency for shared or financial state
**Mistake:** A payment or collaborative feature ships with no race or idempotency scenarios.
**Why it happens:** Concurrency bugs do not show up in single-user demos.
**Instead:** Cover double-submit, simultaneous edit and retry-after-timeout explicitly.

More gaps with fixes: `references/coverage-anti-patterns.md`.

## Scope & Limitations

**In Scope:**
- Test scenarios across seven categories: happy path, edge, error, empty state, concurrent, accessibility and security, plus performance, localization and cross-platform where they apply
- Scenario counts per category by feature type: form, browse, real-time, upload, payment and bulk (table in the reference appendix, matching the script)
- Risk-weighted selection and a default split between manual and automated testing per scenario type
- A coverage audit that flags under-covered categories for the feature type (`test_scenario_generator.py`)
- Test-plan audits and post-incident scenario gap analysis

**Out of Scope:**
- Writing the PRD or acceptance criteria the scenarios come from (see `project-management/execution/create-prd/` and `project-management/execution/wwas/`)
- Implementing automated tests (see `engineering/senior-qa/` and `engineering/playwright-pro/`)
- A full WCAG accessibility audit (see `engineering/a11y-audit/`)
- Security testing and penetration work (see `engineering/security-audit/`)

**Important Caveats:**
- Despite its name, `test_scenario_generator.py` does not write scenarios. It audits a hand-written JSON list and counts scenarios per category.
- The tool checks coverage by count, not scenario quality. A category can pass with weak scenarios.
- The per-category counts are starting defaults. The team adjusts them for the risk profile of the feature.
- The team decides which scenarios to automate and which edge cases matter enough to test.

## Files

| File | Purpose |
|------|---------|
| `scripts/test_scenario_generator.py` | Coverage audit by category (it does not generate scenarios) |
| `assets/sample_scenarios.json` | Signup form, 19 scenarios; exits 0 |
| `assets/sample_scenarios_flawed.json` | Under-covered payment step; exits 1 |
| `assets/scenario_template.md` | Scenario template |

## Reference Documentation

- [references/scenario-categories.md](references/scenario-categories.md): Categories with examples; appendix with recommended counts and manual vs automated
- [references/coverage-anti-patterns.md](references/coverage-anti-patterns.md): Common gaps and fixes

## Related skills

- `project-management/execution/create-prd` — upstream spec
- `project-management/execution/wwas` — acceptance criteria
- `engineering/senior-qa` — implementation
- `engineering/code-reviewer` — review coverage
- `product-team/spec-to-repo` — translating spec to tickets
