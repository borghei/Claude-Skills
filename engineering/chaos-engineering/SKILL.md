---
name: chaos-engineering
description: >
  Chaos engineering: hypothesis-driven fault injection to surface weakness before users do.
  Use when designing a chaos experiment, planning a gameday, choosing what to inject,
  computing blast radius, or building a chaos maturity model.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: engineering
  updated: 2026-06-17
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

Before designing the experiment, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target & fault type** — the service and what to inject (dependency-timeout, network, pod-kill, resource exhaustion) (drives the experiment doc via `--target`/`--fault`)
- [ ] **Steady-state hypothesis** — the metric that defines "healthy" and the expected behavior under fault (the hypothesis the experiment tests)
- [ ] **Blast radius caps** — user count, % targeted, duration, and abort triggers (sizes the experiment via `blast_radius_calculator.py`)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `chaos_experiment_designer.py` | Scaffold a chaos experiment doc (hypothesis stub, steady-state template, abort criteria, checklist) | `python scripts/chaos_experiment_designer.py --target payments-svc --fault dependency-timeout --duration 5m` |
| `blast_radius_calculator.py` | Compute worst-case affected users, recommended caps, and abort triggers | `python scripts/blast_radius_calculator.py --users 100000 --percent-targeted 1 --duration 60` |
| `gameday_planner.py` | Generate a tailored gameday agenda with roles, timeline, and debrief template | `python scripts/gameday_planner.py --service search-api --duration full --scenarios region-failover,dep-outage` |

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
