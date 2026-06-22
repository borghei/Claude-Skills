---
name: feature-flag-strategy
description: >
  PM-facing playbook for phased rollouts with feature flags -- taxonomy
  (release / experiment / ops / permission), rollout shapes, kill-switch
  decision tree, holdouts, flag debt retirement, and naming conventions.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: feature-flags, dark-launch, kill-switch, rollout, holdout, ab-test, launchdarkly, statsig
---
# Feature Flag Strategy (PM playbook)

## Overview

A feature flag is a runtime switch that decouples deploying code from releasing a feature. Done well, flags turn high-stakes ship dates into low-stakes config changes -- launches become measured ramps, regressions become single-toggle rollbacks, and experiments live alongside production code. Done poorly, flags become permanent technical debt: hundreds of dead toggles in code, conflicting flag states across environments, and nobody remembering what the flag controls.

This skill is the **PM-facing** rollout playbook. It does not describe how to wire a flag library into your codebase (that is the engineering side, e.g. your LaunchDarkly / Statsig / Optimizely / Unleash / OpenFeature install). It describes how a PM plans a phased rollout: what kind of flag this is, how it ramps, what the gate criteria are between stages, who can flip the kill-switch, when the flag retires, and how it is named so the team can find it six months later. The frameworks behind it are Martin Fowler's "Feature Toggles" taxonomy, LaunchDarkly's rollout best practices, Optimizely / Statsig experiment playbooks, and Reforge experimentation foundations.

## Core Capabilities

- **Flag classification** -- release / experiment / ops / permission, each with its own lifespan and ownership rules.
- **Rollout shape selection** -- linear, segmented, geographic, A/B-with-holdout, dark launch, reverse ramp, mobile forced-upgrade.
- **Kill-switch design** -- pre-agreed thresholds per surface and single-config-change rollback authority for on-call.
- **Holdout design** -- short-term and global holdouts for long-term lift attribution.
- **Flag-debt governance** -- retirement dates, retirement checklist, quarterly audit, naming conventions, dependency chains.

## When to Use

- Planning a launch larger than a small team can ship cold (anything customer-facing usually warrants a flag).
- Risky changes to high-traffic surfaces (search, checkout, auth, billing -- always behind a kill-switch).
- Experiments (A/B tests) with hold-out and statistical-significance gates.
- Permission rollouts (enterprise tenants, beta participants, a specific role).
- Operational levers (throttles, circuit breakers, degrade-modes).
- Migration of a deterministic feature to AI (pair with `ai-feature-prd/`; cost gates via `engineering/llm-cost-optimizer/`).

**When NOT to use:** one-time data migrations (use a script with `--dry-run`), environment configuration, permanent A/B variants that never converge (that is personalization), or flag-flagging every change (cost > value when overused).

## Clarify First

Before drafting the rollout plan, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Flag type** — release / experiment / ops / permission sets the lifespan and whether a retirement date even applies (permanent vs temporary)
- [ ] **Rollout shape** — linear / segmented / geo / A-B-with-holdout / dark / reverse-ramp defines the stages and gate criteria of the ramp
- [ ] **Kill-switch threshold + authority** — the metric that triggers rollback and who on-call may flip it; a flag without this is worse than no flag
- [ ] **Retirement date** — for release/experiment flags, the date the toggle is removed; omitting it is how flag debt accrues

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

1. Classify the flag, pick a rollout shape, and define the kill-switch threshold + authority.
2. Set a retirement date (release/experiment toggles), name the flag with the convention, and document the plan in `assets/rollout_plan_template.md`.
3. Ramp through stages with a "green pass" gate metric per step; retire the flag at stable GA; audit inventory quarterly.

See `references/rollout-execution-playbook.md` for the full taxonomy, shape catalog, kill-switch tree, holdout governance, naming, workflow, troubleshooting, and success criteria.

## References

- `references/rollout-execution-playbook.md` -- read this when planning a rollout end-to-end: flag taxonomy, all 7 rollout shapes, kill-switch decision tree + thresholds, holdouts, flag-debt retirement, naming, dependency chains, approval/audit, workflow, troubleshooting, success criteria.
- `references/fowler-feature-toggle-taxonomy-guide.md` -- read this for the deep dive on Martin Fowler's "Feature Toggles" essay, lifespans, ownership patterns, and the operational discipline behind them.
- `references/rollout-shape-comparison-guide.md` -- read this for the worked comparison of the 7 rollout shapes with example use cases and risk profiles.
- `references/red-flags.md` -- read this when reviewing a rollout plan for anti-patterns and failure modes before sign-off.
- `assets/rollout_plan_template.md` -- per-feature rollout plan with stages, gates, owners, dates.
- `assets/kill_switch_decision_tree.md` -- pre-incident kill-switch thresholds + authority + flip steps.
- `assets/flag_debt_retirement_checklist.md` -- retirement workflow + quarterly audit.
- `assets/flag_naming_convention.md` -- team naming sheet.

## Scope & Limitations

**In scope:** flag taxonomy and lifespan rules; rollout shapes; kill-switch decision tree and thresholds; holdout design; flag-debt retirement workflow + audit; naming and dependency-chain governance; approval, audit-trail, and two-person-rule patterns.

**Out of scope:** wiring flag SDKs into a codebase (engineering side); statistical analysis of experiments (pair with `discovery/brainstorm-experiments/` for design; data-analytics for stats); building gating dashboards (BI tooling); customer launch comms (`launch-playbook/`, `prfaq/`, `release-notes/`); end-of-life narrative (`eol-communication/`); code rollback strategy (git revert + deployment pipelines).

**Caveats:** flags reduce launch risk but do not eliminate it -- a flag with a broken kill-switch is worse than no flag. Flag debt grows with velocity. Permission/Ops flags are permanent; release/experiment flags are temporary, and conflating the two is the most common failure mode. Holdouts are politically hard to maintain -- document the policy with leadership sign-off. On mobile, forced-upgrade flows are user-hostile; plan around adoption curves.

## Integration Points

| Integration | Direction | Description |
|---|---|---|
| `launch-playbook/` | Pairs with | Rollout plan is the deployment ramp inside the broader launch playbook |
| `cycle-time-analyzer/` | Pairs with | Long-stuck ramps are a leading indicator of risk |
| `prfaq/` / `release-notes/` | Pairs with | External launch narrative vs the operational rollout plan that produced it |
| `eol-communication/` | Pairs with | Reverse-ramp (Shape F) is the operational side of a sunset |
| `ai-feature-prd/` | Pairs with | The AI PRD's deployment ramp (Section 11.3) executes via this skill |
| `discovery/brainstorm-experiments/` | Pairs with | Experiment toggles operationalize Lean experiments |
| `discovery/pre-mortem/` | Pairs with | Pre-mortem risks inform kill-switch thresholds |
| `engineering/llm-cost-optimizer/` | Pairs with | AI ramp gate: cost budget per stage |
| `status-update-generator/` | Feeds into | Rollout-stage pace + gates appear in weekly status |
