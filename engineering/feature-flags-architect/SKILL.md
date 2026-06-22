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
  updated: 2026-06-17
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
- Setting up an A/B test or hold-out — covers the flag side; pair with `engineering/experiment-design` for statistics.
- Building a kill switch for a third-party dependency outage — use the **kill switch runbook** generator.
- Defining who in the org can flip production flags — use the **governance** matrix.
- Building entitlements / paid-tier gating — use this for flag mechanics; `business-growth/paywall-upgrade-cro` for the UX.

## Clarify First

Before designing or operating flags, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Flag type** — release, ops, experiment, or permission (sets the lifecycle, who can flip it, and auto-expiry — the root decision)
- [ ] **Task** — design a taxonomy, simulate a rollout ramp, generate a kill-switch runbook, or audit flag debt (selects `flag_audit.py` vs `rollout_simulator.py` vs `kill_switch_runbook.py`)
- [ ] **Blast radius / population** — user count and ramp profile, or the dependency a kill switch guards (drives `--users`/`--profile` and the runbook content)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `flag_audit.py` | Scan a codebase for flag references, age, classification, and recommended action (optionally cross-reference a control-plane export) | `python scripts/flag_audit.py --path . --format markdown` |
| `rollout_simulator.py` | Model a rollout: per-step blast radius, time-to-detect, recommended schedule | `python scripts/rollout_simulator.py --users 500000 --profile standard` |
| `kill_switch_runbook.py` | Generate a kill-switch runbook (default state, flip procedure, validation, escalation) | `python scripts/kill_switch_runbook.py --flag ops.recs.kill_switch --feature Recommendations --dependency recs-svc` |

All scripts: standard library only, argparse CLI, JSON + human-readable output. Run `--help` for full usage.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/flag-types-and-patterns.md](references/flag-types-and-patterns.md)** — the four flag types in depth, code patterns per type, evaluation-context schema, naming conventions, server-vs-client trade-offs, and storage models. Read when designing a flag system or writing the gating code.
- **[references/operations-governance-and-workflows.md](references/operations-governance-and-workflows.md)** — the standard ramp table, blast-radius math, kill-switch design, the governance matrix + audit-log requirements, the flag-debt cleanup loop, all four end-to-end workflows, the anti-patterns list, and the tooling input/output reference. Read when running a rollout, defining governance, or executing a workflow.
- **[references/rollout-and-kill-switch-playbook.md](references/rollout-and-kill-switch-playbook.md)** — rollout decision tree, ramp templates by change type, cohort/segment selection, kill-switch design, and monitoring/alerting hookup. Read when planning a specific ramp or wiring kill-switch alerting.
- **[references/flag-debt-and-cleanup.md](references/flag-debt-and-cleanup.md)** — what flag debt costs, the cleanup cadence, dead-code detection, safe removal procedures, PR templates, and governance for flag count. Read when paying down stale flags.

## Scope & Limitations

**This skill covers:** flag taxonomy and lifecycle, rollout ramps with blast-radius math, kill-switch design and runbooks, governance/audit requirements, and flag-debt cleanup — provider-agnostic across LaunchDarkly, Statsig, Unleash, Flagsmith, ConfigCat, GrowthBook, OpenFeature, and homegrown systems.

**This skill does NOT cover:** the statistical design of A/B tests (pair with `product-team/experiment-design`), the paywall/upgrade UX for entitlements (`business-growth/paywall-upgrade-cro`), or the metric instrumentation needed to make ramp decisions (`engineering/observability-designer`).

## Related skills

- `engineering/observability-designer` — wire the metrics needed to make ramp decisions
- `engineering/incident-commander` — flag-based rollback during incidents
- `engineering/chaos-engineering` — verify kill switches actually work under fault injection
- `product-team/experiment-design` (if available) — statistical design of A/B tests behind flags
