---
name: feature-flags-architect
description: >
  Feature flag strategy, lifecycle, and operations. Use when designing a flag taxonomy,
  planning a gradual rollout, building kill switches, auditing flag debt, defining governance,
  running progressive delivery, or rolling back via flags.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: engineering
  updated: 2026-11-08
  tags: [feature-flags, progressive-delivery, rollouts, kill-switches, release-engineering, experimentation, flag-governance]
---

# Feature Flags Architect

End-to-end feature flag design, rollout, and lifecycle management. Covers flag taxonomy (release vs ops vs experiment vs permission), gradual rollout patterns with blast-radius math, kill-switch runbooks, governance (who can flip what), and the flag-debt cleanup loop that keeps a codebase from drowning in stale flags.

This skill is provider-agnostic: the patterns work whether you run LaunchDarkly, Statsig, Unleash, Flagsmith, ConfigCat, GrowthBook, OpenFeature, or a homegrown system backed by Redis/DynamoDB/Postgres.

## Core Capabilities

- **Flag taxonomy** — classify every flag as one of four types (release, ops, experiment, permission); the type sets lifetime, who flips it, and auto-expiry.
- **Rollout ramps** — dogfood → canary → 100% schedules with per-step blast-radius math and ramp templates by change type.
- **Kill switches** — ops-flag pattern with fail-open/closed decisions, runbooks, and alerting for risky dependencies or code paths.
- **Governance** — role-based who-can-flip-what matrix plus audit-log/retention requirements, mappable onto any flag system.
- **Flag debt cleanup** — quarterly inventory → classify → decide → execute → measure loop to keep flag count flat or shrinking.
- **End-to-end workflows** — add a release flag, build a kill switch, audit flag debt, flag-based rollback after a bad release.

## Flag taxonomy — the four types

Every flag belongs to exactly one of these four types. The type determines the lifecycle, who can flip it, and whether it should auto-expire. Mixing types in one flag is a root cause of flag debt.

| Type | Purpose | Lifetime | Who flips | Auto-expire? |
|------|---------|----------|-----------|--------------|
| **Release** | Decouple deploy from release. Ship code dark, ramp to users. | Days to weeks | Engineer who owns the feature | Yes — remove after 100% rollout + 1 release |
| **Ops** | Kill switches, circuit breakers, throttles. Turn off risky behavior fast. | Permanent or long-lived | Oncall / SRE / platform team | No — but review quarterly |
| **Experiment** | A/B test, multi-arm bandit, hold-out group. Measure causal impact. | Weeks to months (test duration) | Product / data / growth | Yes — remove after winner is shipped |
| **Permission** | Entitle users to features based on plan, role, beta-list. | Permanent | Product / billing | No — but consolidate into entitlement system |

**Decision rule when adding a flag:** name the type. If you can't, the flag shouldn't exist yet — clarify intent first.

## When to Use

- Designing a flag system from scratch — start with the **flag taxonomy**.
- Planning a risky release (DB migration, payment-provider swap, framework upgrade) — use the **rollout ramp** + **kill switch**.
- Auditing a codebase with hundreds of growing flags — use **flag debt cleanup** + `scripts/flag_audit.py`.
- Setting up an A/B test or hold-out — covers the flag side; use `data-analytics/statistical-analyst` for sample size and significance.
- Building a kill switch for a third-party dependency outage — use the **kill switch runbook** generator.
- Defining who in the org can flip production flags — use the **governance** matrix.
- Building entitlements / paid-tier gating — use this for flag mechanics; `business-growth/paywall-upgrade-cro` for the UX.

## Clarify First

Before designing or operating flags, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Flag type:** release, ops, experiment, or permission (sets the lifecycle, who can flip it, and auto-expiry — the root decision).
- **Task:** design a taxonomy, simulate a rollout ramp, generate a kill-switch runbook, or audit flag debt (selects `flag_audit.py` vs `rollout_simulator.py` vs `kill_switch_runbook.py`).
- **Blast radius / population:** user count and ramp profile, or the dependency a kill switch guards (drives `--users`/`--profile` and the runbook content).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Name the type** of every new flag (release, ops, experiment, permission) and give it an owner and, for release and experiment flags, a removal date.
2. **Plan the ramp** with `rollout_simulator.py` for the user count and risk profile; each step needs the metric that would stop it.
3. **Build the kill switch** for risky dependencies with `kill_switch_runbook.py`, passing the real owner team, oncall rotation and flag-console URL so the runbook has no placeholders.
4. **Audit debt** quarterly with `flag_audit.py` against a control-plane export: delete dead flags, remove stranded 100% release flags and their dead branches, investigate orphan references.
5. **Verify** that the kill switch actually flips in staging (or under fault injection) and that the audit's debt list shrinks quarter over quarter.

## Quick Start

```bash
python3 scripts/flag_audit.py --path assets --flag-export assets/sample_flag_export.json --as-of 2026-06-01   # 1 dead, 1 orphan, 1 stranded at 100%
python3 scripts/rollout_simulator.py --users 500000 --profile standard
python3 scripts/kill_switch_runbook.py --flag ops.recs.kill_switch --feature Recommendations --dependency recs-svc \
  --owner-team recs-team --oncall recs-oncall --flag-console-url https://flags.example.com/flags/ops.recs.kill_switch
```

## Tools Overview

| Tool | What it does | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `flag_audit.py` | Find flag reads in code, join with a control-plane export, classify each flag (dead, orphan, stranded at 0/100%, should-be-config, ghost owner, healthy) with an action | `--path`, `--flag-export`, `--as-of`, `--pattern <regex>` (repeatable), `--owner-team`, `--include-active`, `--format json|markdown|human` | 0 report, 2 bad path, export or pattern |
| `rollout_simulator.py` | Per-step blast radius, time to detect, recommended schedule | `--users`, `--profile`, `--format` | 0, 2 bad arguments |
| `kill_switch_runbook.py` | Runbook: default state, fail mode, flip procedure, validation, escalation | `--flag`, `--feature`, `--dependency`, `--owner-team`, `--oncall`, `--flag-console-url`, `--fail-mode open|closed`, thresholds | 0, 2 bad arguments |

`flag_audit.py` recognises LaunchDarkly (`variation`, `boolVariation`), OpenFeature (`getBooleanValue`, `useBooleanFlagValue`), Statsig (`checkGate`), Unleash (`isEnabled`), generic `flags.isEnabled/evaluate/getVariant`, homegrown helpers (`getFlag`, `useFlag`, `isFeatureEnabled`, `get_feature_flag`) and flag decorators. For other SDKs pass `--pattern` with a regex whose first group is the flag key. Flags read through variables built at runtime are not found; grep for those by hand. The runbook defaults (`unknown-team`, a placeholder console URL) are there to be overridden.

## Anti-Patterns

**Mistake:** Release flags without a removal date.
**Why it happens:** Once the feature is at 100%, removing the flag has no visible payoff.
**Instead:** Set the date when the flag is created and let the quarterly audit enforce it; stranded flags double the code paths to test.

**Mistake:** A kill switch that has never been flipped.
**Why it happens:** It exists for emergencies, so nobody tries it.
**Instead:** Flip it in staging on a schedule (or under fault injection) and record the time to effect.

**Mistake:** One flag doing two jobs (a release ramp that later becomes a permission gate).
**Why it happens:** Reusing an existing flag is quicker than creating one.
**Instead:** Create a new flag of the right type. Mixed-type flags cannot be removed without breaking someone.

## Files

- `scripts/flag_audit.py`, `scripts/rollout_simulator.py`, `scripts/kill_switch_runbook.py` — the tools above.
- `assets/sample_checkout.ts` (flag reads through three SDK shapes), `assets/sample_flag_export.json` (control-plane export).

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/flag-types-and-patterns.md](references/flag-types-and-patterns.md)** — the four flag types in depth, code patterns per type, evaluation-context schema, naming conventions, server-vs-client trade-offs, and storage models. Read when designing a flag system or writing the gating code.
- **[references/operations-governance-and-workflows.md](references/operations-governance-and-workflows.md)** — the standard ramp table, blast-radius math, kill-switch design, the governance matrix + audit-log requirements, the flag-debt cleanup loop, all four end-to-end workflows, the anti-patterns list, and the tooling input/output reference. Read when running a rollout, defining governance, or executing a workflow.
- **[references/rollout-and-kill-switch-playbook.md](references/rollout-and-kill-switch-playbook.md)** — rollout decision tree, ramp templates by change type, cohort/segment selection, kill-switch design, and monitoring/alerting hookup. Read when planning a specific ramp or wiring kill-switch alerting.
- **[references/flag-debt-and-cleanup.md](references/flag-debt-and-cleanup.md)** — what flag debt costs, the cleanup cadence, dead-code detection, safe removal procedures, PR templates, and governance for flag count. Read when paying down stale flags.

## Scope & Limitations

**This skill covers:** flag taxonomy and lifecycle, rollout ramps with blast-radius math, kill-switch design and runbooks, governance/audit requirements, and flag-debt cleanup — provider-agnostic across LaunchDarkly, Statsig, Unleash, Flagsmith, ConfigCat, GrowthBook, OpenFeature, and homegrown systems.

**This skill does NOT cover:** the statistical design of A/B tests (`data-analytics/statistical-analyst`), the paywall/upgrade UX for entitlements (`business-growth/paywall-upgrade-cro`), or the metric instrumentation needed to make ramp decisions (`engineering/observability-designer`).

## Related skills

- `engineering/observability-designer` — wire the metrics needed to make ramp decisions
- `engineering/incident-commander` — flag-based rollback during incidents
- `engineering/chaos-engineering` — verify kill switches actually work under fault injection
- `data-analytics/statistical-analyst` — sample size and significance for A/B tests behind flags
