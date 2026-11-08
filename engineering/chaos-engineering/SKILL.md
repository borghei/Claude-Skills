---
name: chaos-engineering
description: >
  Designs hypothesis-driven fault-injection experiments, sizes their blast radius and plans
  gamedays. Use when designing a chaos experiment, planning a gameday, choosing what to inject,
  or building a chaos maturity model.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: engineering
  updated: 2026-11-08
  tags: [chaos-engineering, resilience, fault-injection, gameday, sre, reliability, blast-radius]
---

# Chaos Engineering

End-to-end chaos engineering: experiment design, fault injection catalog, gameday execution, and the maturity model that turns one-off "let's break stuff" exercises into a reliable discipline. Provider-agnostic — works whether you use Litmus, Chaos Mesh, AWS FIS, Gremlin, ChaosToolkit, or hand-rolled scripts.

This skill answers four questions: **what to inject, where to inject it, how to size the blast, and how to extract durable learning** from each run.

## Core Capabilities

- **Principles & maturity** — the five Principles of Chaos and a four-level maturity model (L0 none → L4 always-on production chaos) with level-up criteria.
- **Experiment design loop** — a nine-step loop (steady state → hypothesis → variables → blast radius → abort → run → analyze → act → document) with worked good/bad examples.
- **Fault catalog** — what to inject per layer: pod/host, network, dependency, resource, state, and traffic, with tool mappings.
- **Blast-radius sizing** — quantify worst-case affected users and recommended caps; experiments start tiny (1 pod / 1% / 1 min) and grow only after passing.
- **Gameday execution** — scheduled multi-scenario exercises with roles, agendas, scenario selection, and debrief templates.
- **Discipline** — anti-patterns to avoid, the "first five experiments" for new teams, and end-to-end workflows (single experiment, gameday, kill-switch verification, post-incident verification).

## When to Use

| Situation | Skill applies |
|-----------|---------------|
| Spinning up a chaos program from scratch | Yes — start with **maturity model** + **first 5 experiments** |
| Designing a single experiment for a known concern | Yes — use the **experiment design loop** |
| Planning a gameday for a team or service | Yes — use `scripts/gameday_planner.py` |
| Validating a kill switch or fallback path actually works | Yes — chaos is the way to test these in prod-like conditions |
| Post-incident verification: "did the fix really fix it?" | Yes — re-inject the original fault, confirm the new behavior |
| Compliance evidence (SOC 2 A1 / DORA Art. 25) | Yes — chaos runs produce auditable resilience-testing evidence |
| Improving SLOs / error budgets | Pair with `engineering/observability-designer` — chaos surfaces SLO violations |

## Clarify First

Before designing the experiment, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target & fault type:** the service and what to inject (dependency-timeout, network, pod-kill, resource exhaustion) (drives the experiment doc via `--target`/`--fault`).
- **Steady-state hypothesis:** the metric that defines "healthy" and the expected behavior under fault (the hypothesis the experiment tests).
- **Blast radius caps:** user count, % targeted, duration, and abort triggers (sizes the experiment via `blast_radius_calculator.py`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

The scripts write plans and documents only; they never touch a system.

```bash
# 1. Scaffold the experiment doc (hypothesis, steady state, abort criteria, checklist)
python scripts/chaos_experiment_designer.py --target payments-svc --fault dependency-timeout --duration 5m
python scripts/chaos_experiment_designer.py --list-faults          # the nine fault types

# 2. Size the blast: worst-case affected users, recommended caps, abort timing
python scripts/blast_radius_calculator.py --users 100000 --percent-targeted 1 --duration 60

# 3. Plan a gameday from scenario ids
python scripts/gameday_planner.py --service search-api --duration full --scenarios dep-timeout,partition,az-degraded
python scripts/gameday_planner.py --list-scenarios                 # pod-kill, rolling-restart, latency, partition,
                                                                   # dep-error, dep-timeout, cpu-stress, memory-pressure,
                                                                   # disk-fill, cache-flush, traffic-spike, az-degraded
```

All three take `--format markdown|json` (`human|json` for the calculator) and `--output FILE`.
**Exit codes:** `0` document written; `2` bad arguments (unknown fault or scenario id, out-of-range percent).

**Go / no-go before any run.** Do not inject until every item is true, because a run without them produces risk and no learning:
1. The steady-state metric and its normal range are written down and visible on a dashboard.
2. The hypothesis names the expected behaviour under the fault ("p99 stays under 800 ms, fallback serves cached prices").
3. Abort criteria are numeric, agreed, and someone owns the abort command.
4. The blast radius is within the calculator's recommended cap for the current maturity level.
5. On-call knows the window, and production runs have a rollback that was tested in staging.

**Done when:** the run's result is recorded against the hypothesis, any weakness found has a ticket with an owner, and the experiment is either promoted to a recurring run or retired with a reason.

## Anti-Patterns

### Breaking things without a hypothesis
**Mistake:** Killing pods "to see what happens", with no steady-state metric or expected outcome.
**Why it happens:** Injection tools make faults easy; writing a hypothesis feels like paperwork.
**Instead:** Write the hypothesis and steady state first. Without them you cannot tell a pass from a fail, so nothing is learned.

### Starting at full blast
**Mistake:** The first experiment on a service hits 50% of production traffic for 30 minutes.
**Why it happens:** Small experiments feel too small to prove anything.
**Instead:** Start at one pod, 1% or one minute and grow only after a pass. `blast_radius_calculator.py` shows the worst case before you commit.

### Findings with no follow-up
**Mistake:** The gameday surfaces three weaknesses, the debrief notes them, and nothing is ticketed.
**Why it happens:** The exercise ends when the faults stop, and the action items have no owner.
**Instead:** End every run with owned tickets and re-run the same fault after the fix lands to confirm it.

## Files

- `scripts/chaos_experiment_designer.py` — experiment document scaffold for nine fault types.
- `scripts/blast_radius_calculator.py` — affected users, sessions, revenue at risk, caps and abort timing.
- `scripts/gameday_planner.py` — half- or full-day agenda, roles, scenario blocks, debrief template.
- `references/` — design loop, fault catalog, maturity model, gameday playbook (listed below).

## Scope & Limitations

**In Scope:**
- Experiment design with the nine-step loop, and experiment documents scaffolded by `chaos_experiment_designer.py` for nine fault types (CPU, memory, disk, network latency and partition, pod kill, dependency error and timeout, traffic spike)
- Blast-radius sizing with `blast_radius_calculator.py`: worst-case affected users and sessions, fallback success, optional revenue at risk, recommended caps and abort timing
- Gameday plans from `gameday_planner.py`: half- or full-day agendas, role assignments, scenario blocks and debrief templates
- The five principles, a maturity model, a fault catalog mapped to Chaos Mesh, Litmus, AWS FIS, Gremlin and ChaosToolkit, and the first five experiments for a new program

**Out of Scope:**
- Injecting faults; the scripts write plans and documents and never touch a system
- Building the metrics and SLOs that define steady state (see `engineering/observability-designer/`)
- Running live incident response (see `engineering/incident-commander/`)
- Kill-switch and flag design (see `engineering/feature-flags-architect/`)
- Mapping chaos results to DORA resilience-testing obligations (see `ra-qm-team/dora-compliance-expert/`)

**Important Caveats:**
- Blast-radius numbers are arithmetic on the user's inputs for user count, percent targeted, detection and abort time. They are only as accurate as those estimates.
- A generated experiment document leaves the steady-state metric and the hypothesis for the team to fill in. Its abort criteria are templates, not tuned thresholds.
- Running experiments in production carries real risk. The skill's advice is to start with one pod, 1% of traffic or one minute and grow scope only after a run passes.
- Fault-injection tool features differ by version and platform. Confirm a fault type is supported in the tool you use before planning around it.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/experiment-design-loop.md](references/experiment-design-loop.md)** — the five principles, the four-level maturity model, the full nine-step design loop with worked steady-state/hypothesis/abort examples, and the "first five experiments." Read when designing or running an experiment.
- **[references/gameday-workflows-and-antipatterns.md](references/gameday-workflows-and-antipatterns.md)** — the gameday agenda and roles, scenario selection, the chaos anti-patterns, all four end-to-end workflows, and the script tooling-output table. Read when planning a gameday or running a workflow.
- **[references/chaos-principles-and-maturity.md](references/chaos-principles-and-maturity.md)** — per-level maturity scorecard, the L0→L1 "first five experiments" list, and the org/SRE prerequisites for each level. Read when assessing or leveling up a program.
- **[references/gameday-playbook.md](references/gameday-playbook.md)** — 12 scenario templates by domain (API service, database, frontend, async pipeline, multi-region, etc.), half-day/full-day agendas, and post-gameday writeup templates. Read when choosing gameday scenarios.
- **[references/fault-injection-catalog.md](references/fault-injection-catalog.md)** — fault types per layer (network, host, dependency, resource, state, traffic) with tool mappings (Chaos Mesh / Litmus / AWS FIS / Gremlin / ChaosToolkit). Read when choosing what to inject.

## Related skills

- `engineering/observability-designer` — wire metrics needed to define steady state
- `engineering/incident-commander` — chaos is rehearsal for the incident response you'll need
- `engineering/feature-flags-architect` — kill switches verified by chaos; chaos verified by flags
- `ra-qm-team/dora-compliance-expert` — DORA Article 25 requires resilience testing; chaos runs are evidence
