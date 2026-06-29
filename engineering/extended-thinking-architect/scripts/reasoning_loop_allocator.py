#!/usr/bin/env python3
"""
Reasoning Loop Allocator - Spread reasoning effort across agent-loop phases.

Most agent budgets are wasted by spending the same high reasoning effort on every
turn. The cheap, robust pattern is to FRONT-LOAD reasoning at planning and at error
recovery, and run thin (none/low) effort on routine tool selection and observation.

This tool maps overall task difficulty + expected step count to a per-phase effort
plan, then enforces a total budget cap (a multiple of one no-thinking call) as a hard
stop so a stuck loop cannot run away.

Model-agnostic: effort levels are conceptual (none/low/medium/high), not API params.
Standard library only. No network, no LLM calls. Deterministic.

Author: borghei (AI Skills Library)
License: MIT + Commons Clause
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from typing import List, Dict


EFFORT_ORDER = ["none", "low", "medium", "high"]

# Rough per-call output cost multiplier vs. a no-thinking call (mid-point of a range).
EFFORT_WEIGHT = {"none": 1.0, "low": 2.0, "medium": 5.0, "high": 15.0}

# Canonical agent-loop phases and the BASE effort each deserves at "medium"
# difficulty. Reasoning belongs at plan & recover, not at every act/observe.
PHASE_BASE = {
    "plan":     {"effort": "medium", "per_run": True,  "note": "Decompose once, up front — the highest-leverage place to think."},
    "act":      {"effort": "low",    "per_run": False, "note": "Tool selection is mostly routing; keep it cheap per step."},
    "observe":  {"effort": "none",   "per_run": False, "note": "Parsing tool output rarely needs deduction."},
    "recover":  {"effort": "high",   "per_run": False, "note": "Only when stuck: spend here to replan, not everywhere."},
    "finalize": {"effort": "medium", "per_run": True,  "note": "Synthesis of results benefits from a coherent pass."},
}

# Difficulty shifts every phase up or down the effort ladder.
DIFFICULTY_SHIFT = {"low": -1, "medium": 0, "high": +1}


def _shift(effort: str, delta: int, cap: str = "high") -> str:
    idx = EFFORT_ORDER.index(effort) + delta
    idx = max(0, min(idx, EFFORT_ORDER.index(cap)))
    return EFFORT_ORDER[idx]


@dataclass
class PhasePlan:
    phase: str
    effort: str
    invocations: int          # rough number of times this phase runs over the loop
    note: str


@dataclass
class LoopPlan:
    difficulty: str
    steps: int
    realtime: bool
    effort_cap: str
    phases: List[PhasePlan] = field(default_factory=list)
    projected_cost_multiplier: float = 0.0
    max_budget_multiplier: float = 0.0
    within_budget: bool = True
    guardrails: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def build_plan(difficulty: str, steps: int, max_budget_multiplier: float, realtime: bool) -> LoopPlan:
    delta = DIFFICULTY_SHIFT[difficulty]
    # Realtime loops cap effort at "medium" everywhere to protect latency.
    cap = "medium" if realtime else "high"

    guardrails: List[str] = []
    warnings: List[str] = []
    phases: List[PhasePlan] = []
    projected = 0.0

    # Assume recovery fires on a fraction of steps (stuck turns). Conservative: ~1/3.
    recover_invocations = max(1, steps // 3) if steps >= 3 else 0

    for name, base in PHASE_BASE.items():
        effort = _shift(base["effort"], delta, cap=cap)

        if name in ("plan", "finalize"):
            invocations = 1
        elif name == "recover":
            invocations = recover_invocations
        else:  # act / observe run roughly once per step
            invocations = steps

        if invocations == 0:
            continue

        projected += EFFORT_WEIGHT[effort] * invocations
        phases.append(PhasePlan(phase=name, effort=effort, invocations=invocations, note=base["note"]))

    within = projected <= max_budget_multiplier

    # Guardrails
    guardrails.append(
        f"Hard stop: cap total loop spend at ~{max_budget_multiplier:g}x one no-thinking call; abort/escalate to a human past it."
    )
    guardrails.append("Front-load reasoning at PLAN; keep ACT/OBSERVE thin; reserve HIGH effort for RECOVER only.")
    guardrails.append("Trigger RECOVER's higher effort on failure signals (errors, loops, low confidence) — not on a timer.")

    if realtime:
        warnings.append("Realtime loop: effort capped at 'medium' per phase to protect latency.")
    if not within:
        warnings.append(
            f"Projected ~{projected:g}x exceeds the {max_budget_multiplier:g}x cap. "
            "Reduce steps, lower per-phase effort, or split the task."
        )
    if steps >= 8 and difficulty == "high":
        warnings.append("Long, hard loop: highest runaway risk — verify the total cap is wired as a real circuit breaker.")

    return LoopPlan(
        difficulty=difficulty,
        steps=steps,
        realtime=realtime,
        effort_cap=cap,
        phases=phases,
        projected_cost_multiplier=round(projected, 1),
        max_budget_multiplier=max_budget_multiplier,
        within_budget=within,
        guardrails=guardrails,
        warnings=warnings,
    )


def render_human(plan: LoopPlan) -> str:
    lines = []
    lines.append("=" * 68)
    lines.append("  AGENT-LOOP REASONING ALLOCATION")
    lines.append("=" * 68)
    lines.append(f"  Difficulty: {plan.difficulty}   Steps: {plan.steps}   "
                 f"Realtime: {plan.realtime}   Per-phase cap: {plan.effort_cap}")
    lines.append("")
    lines.append(f"  {'Phase':<10} {'Effort':<8} {'Runs':<6} Note")
    lines.append(f"  {'-'*10} {'-'*8} {'-'*6} {'-'*30}")
    for ph in plan.phases:
        lines.append(f"  {ph.phase:<10} {ph.effort:<8} {ph.invocations:<6} {ph.note}")
    lines.append("")
    status = "WITHIN BUDGET" if plan.within_budget else "OVER BUDGET"
    lines.append(f"  Projected spend : ~{plan.projected_cost_multiplier:g}x one no-thinking call  [{status}]")
    lines.append(f"  Budget cap      : ~{plan.max_budget_multiplier:g}x")
    lines.append("")
    lines.append("  Guardrails:")
    for g in plan.guardrails:
        lines.append(f"    * {g}")
    if plan.warnings:
        lines.append("")
        lines.append("  Warnings:")
        for w in plan.warnings:
            lines.append(f"    ! {w}")
    lines.append("=" * 68)
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Allocate reasoning effort across the phases of an agent loop, under a total budget cap.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--difficulty", default="medium", choices=sorted(DIFFICULTY_SHIFT.keys()),
                   help="Overall task difficulty; shifts every phase up/down the effort ladder.")
    p.add_argument("--steps", type=int, default=5, help="Expected number of loop steps (act/observe iterations).")
    p.add_argument("--max-budget-multiplier", type=float, default=30.0,
                   help="Hard cap on total loop spend, as a multiple of one no-thinking call.")
    p.add_argument("--realtime", action="store_true", help="Latency-tight loop: cap per-phase effort at 'medium'.")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of a human-readable report.")
    args = p.parse_args(argv)

    if args.steps < 1:
        p.error("--steps must be >= 1")
    if args.max_budget_multiplier < 1:
        p.error("--max-budget-multiplier must be >= 1")

    plan = build_plan(
        difficulty=args.difficulty,
        steps=args.steps,
        max_budget_multiplier=args.max_budget_multiplier,
        realtime=args.realtime,
    )

    if args.json:
        print(json.dumps(asdict(plan), indent=2))
    else:
        print(render_human(plan))
    return 0 if plan.within_budget else 0  # advisory tool: non-zero reserved for usage errors


if __name__ == "__main__":
    sys.exit(main())
