#!/usr/bin/env python3
"""
Reasoning Budget Advisor - Recommend an extended-thinking effort level for a task.

Turns task signals (task type, error cost, step count, ambiguity, latency budget,
verifiability) into a deterministic recommendation:

    none | low | medium | high   -- a reasoning/thinking effort level, OR
    prompt-first                  -- fix the prompt/spec before spending reasoning, OR
    cheaper-model                 -- route to a smaller model + better prompt

It is model-agnostic: it never names API parameters, SDKs, or prices. Effort levels
map to a *rough* cost multiplier relative to a no-thinking call on the same model,
because thinking/reasoning tokens are billed and add latency.

Standard library only. No network, no LLM calls. Deterministic.

Author: borghei (AI Skills Library)
License: MIT + Commons Clause
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from typing import List, Dict


# --------------------------------------------------------------------------- #
# Heuristic tables (explicit and tunable)
# --------------------------------------------------------------------------- #

# How much extended thinking *tends* to help a task class, on a 0-5 scale.
# 0 = deterministic mapping (thinking wasted); 5 = deep multi-step deduction.
TASK_AFFINITY: Dict[str, int] = {
    "extraction": 0,
    "classification": 0,
    "rewrite": 1,
    "summarization": 1,
    "conversation": 1,
    "creative": 1,
    "retrieval-qa": 2,
    "code-gen": 3,
    "planning": 4,
    "code-debug": 4,
    "agent-orchestration": 4,
    "multi-step-reasoning": 5,
    "math": 5,
}

# Task classes that are usually a routing problem, not a thinking problem.
CHEAP_TASKS = {"extraction", "classification", "summarization", "rewrite"}

ERROR_COST_POINTS = {"low": 0, "medium": 1, "high": 2, "critical": 3}
AMBIGUITY_POINTS = {"low": 0, "medium": 1, "high": 2}

# Latency budgets cap the maximum effort we will recommend.
# realtime: user-facing, sub-second/very fast; interactive: a few seconds OK;
# batch: offline/async, latency largely irrelevant.
LATENCY_CAP = {"realtime": "low", "interactive": "medium", "batch": "high"}

EFFORT_ORDER = ["none", "low", "medium", "high"]

# Rough output-side cost multiplier vs. a no-thinking call on the SAME model.
# Ranges, not promises: thinking tokens vary widely by task and model.
COST_MULTIPLIER = {
    "none": (1.0, 1.0),
    "low": (1.5, 3.0),
    "medium": (3.0, 8.0),
    "high": (8.0, 25.0),
}


@dataclass
class Recommendation:
    recommendation: str            # none|low|medium|high|prompt-first|cheaper-model
    effort: str                    # the underlying effort level (none..high)
    value_score: int
    cost_multiplier_range: List[float]
    capped_by_latency: bool
    rationale: List[str] = field(default_factory=list)
    guardrails: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _cap_effort(effort: str, cap: str) -> str:
    """Return the lower of effort and cap in the effort ordering."""
    if EFFORT_ORDER.index(effort) <= EFFORT_ORDER.index(cap):
        return effort
    return cap


def score_to_effort(score: int) -> str:
    if score <= 1:
        return "none"
    if score <= 3:
        return "low"
    if score <= 6:
        return "medium"
    return "high"


def advise(
    task_type: str,
    error_cost: str,
    steps: int,
    ambiguity: str,
    latency_budget: str,
    verifiable: bool,
) -> Recommendation:
    rationale: List[str] = []
    guardrails: List[str] = []
    warnings: List[str] = []

    affinity = TASK_AFFINITY[task_type]
    rationale.append(
        f"Task '{task_type}' has reasoning-affinity {affinity}/5 "
        f"(how much deduction the work inherently requires)."
    )

    score = affinity

    # Step count: more steps => more value from a coherent plan, but also more
    # runaway risk.
    if steps >= 5:
        score += 2
        rationale.append(f"{steps} expected steps add +2 (multi-step work rewards planning).")
    elif steps >= 3:
        score += 1
        rationale.append(f"{steps} expected steps add +1.")
    else:
        rationale.append(f"{steps} expected step(s): no step bonus.")

    # Error cost: expensive mistakes justify spending to get it right once.
    ec = ERROR_COST_POINTS[error_cost]
    if ec:
        score += ec
        rationale.append(f"Error cost '{error_cost}' adds +{ec} (expensive mistakes justify deliberation).")
    else:
        rationale.append("Error cost 'low': no bonus (cheap to be wrong / easy to retry).")

    # Verifiability: reasoning pays most when there's ground truth or a checker.
    # Without it, extra thinking risks confident elaboration with no payoff.
    if not verifiable:
        score = max(0, score - 1)
        rationale.append("Output not verifiable: -1 (no checker to convert reasoning into reliable gains).")
        warnings.append(
            "No ground truth / checker: high effort tends toward verbose over-elaboration, not better answers."
        )
    else:
        rationale.append("Output verifiable: reasoning can be validated, so it converts to real quality.")

    effort = score_to_effort(score)

    # Latency cap.
    cap = LATENCY_CAP[latency_budget]
    capped = EFFORT_ORDER.index(effort) > EFFORT_ORDER.index(cap)
    if capped:
        warnings.append(
            f"Latency budget '{latency_budget}' caps effort at '{cap}'. "
            f"Higher effort would blow the latency budget more than it helps."
        )
    effort = _cap_effort(effort, cap)

    # --- Decide the headline recommendation ---------------------------------- #
    recommendation = effort

    # Ambiguity gate: a vague request is a prompt problem first.
    amb = AMBIGUITY_POINTS[ambiguity]
    if ambiguity == "high":
        recommendation = "prompt-first"
        rationale.append(
            "Ambiguity is high: extra reasoning will confidently solve the wrong problem. "
            "Clarify the goal / add examples first, THEN re-evaluate effort."
        )
        guardrails.append("Resolve ambiguity (clarify spec, add 1-2 examples) before spending any reasoning budget.")
    elif amb:
        score += 0  # medium ambiguity doesn't add reasoning value; it adds risk
        warnings.append("Medium ambiguity: confirm the goal; reasoning amplifies whatever target you give it.")

    # Cheaper-model gate: low-value, low-stakes, routing-style tasks.
    if (
        recommendation not in ("prompt-first",)
        and task_type in CHEAP_TASKS
        and effort in ("none", "low")
        and error_cost in ("low", "medium")
    ):
        recommendation = "cheaper-model"
        rationale.append(
            f"'{task_type}' is a deterministic mapping at low/medium stakes: a smaller/faster "
            "model with a sharper prompt usually beats spending reasoning here."
        )
        guardrails.append("Route to a cheaper model; invest the savings in prompt quality and a few-shot example.")

    # --- Guardrails by effort ------------------------------------------------ #
    if effort in ("medium", "high"):
        guardrails.append("Set a per-call thinking/effort cap so a single call cannot run unbounded.")
    if steps >= 5 and effort in ("medium", "high"):
        guardrails.append(
            "Loop risk: set a loop-level total budget (a multiple of one no-thinking call) as a hard stop."
        )
        warnings.append("High effort x many steps is the classic runaway-budget shape — cap the total, not just per call.")
    if effort != "none":
        guardrails.append("Escalate effort only on failure (retry one notch higher); never start high 'to be safe'.")

    lo, hi = COST_MULTIPLIER[effort]
    rationale.append(
        f"Effort '{effort}' implies roughly {lo:g}x-{hi:g}x the output cost & latency of a no-thinking call "
        f"on the same model (thinking tokens are billed)."
    )

    return Recommendation(
        recommendation=recommendation,
        effort=effort,
        value_score=score,
        cost_multiplier_range=[lo, hi],
        capped_by_latency=capped,
        rationale=rationale,
        guardrails=guardrails,
        warnings=warnings,
    )


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def render_human(rec: Recommendation) -> str:
    lines = []
    lines.append("=" * 64)
    lines.append("  REASONING BUDGET RECOMMENDATION")
    lines.append("=" * 64)
    headline = rec.recommendation.upper()
    if rec.recommendation in EFFORT_ORDER:
        headline = f"{headline} EFFORT"
    lines.append(f"  Recommendation : {headline}")
    if rec.recommendation in ("prompt-first", "cheaper-model"):
        lines.append(f"  (underlying effort if you proceed: {rec.effort})")
    lo, hi = rec.cost_multiplier_range
    lines.append(f"  Value score    : {rec.value_score}")
    lines.append(f"  Cost vs no-think: ~{lo:g}x-{hi:g}x output cost & latency")
    if rec.capped_by_latency:
        lines.append("  (effort was capped by the latency budget)")
    lines.append("")
    lines.append("  Rationale:")
    for r in rec.rationale:
        lines.append(f"    - {r}")
    if rec.guardrails:
        lines.append("")
        lines.append("  Guardrails:")
        for g in rec.guardrails:
            lines.append(f"    * {g}")
    if rec.warnings:
        lines.append("")
        lines.append("  Warnings:")
        for w in rec.warnings:
            lines.append(f"    ! {w}")
    lines.append("=" * 64)
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Recommend an extended-thinking effort level for an LLM task.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--task-type",
        required=True,
        choices=sorted(TASK_AFFINITY.keys()),
        help="What the model is actually doing.",
    )
    p.add_argument(
        "--error-cost",
        default="medium",
        choices=sorted(ERROR_COST_POINTS.keys()),
        help="How expensive a wrong answer is.",
    )
    p.add_argument(
        "--steps",
        type=int,
        default=1,
        help="Expected number of reasoning/tool steps for the task.",
    )
    p.add_argument(
        "--ambiguity",
        default="low",
        choices=sorted(AMBIGUITY_POINTS.keys()),
        help="How underspecified the request is.",
    )
    p.add_argument(
        "--latency-budget",
        default="interactive",
        choices=sorted(LATENCY_CAP.keys()),
        help="Latency tolerance: realtime (caps low), interactive (caps medium), batch (no cap).",
    )
    p.add_argument(
        "--verifiable",
        dest="verifiable",
        action="store_true",
        default=True,
        help="Output has ground truth or a checker (default: assumed true).",
    )
    p.add_argument(
        "--not-verifiable",
        dest="verifiable",
        action="store_false",
        help="Output has no checker / no ground truth.",
    )
    p.add_argument("--json", action="store_true", help="Emit JSON instead of a human-readable report.")
    args = p.parse_args(argv)

    if args.steps < 1:
        p.error("--steps must be >= 1")

    rec = advise(
        task_type=args.task_type,
        error_cost=args.error_cost,
        steps=args.steps,
        ambiguity=args.ambiguity,
        latency_budget=args.latency_budget,
        verifiable=args.verifiable,
    )

    if args.json:
        print(json.dumps(asdict(rec), indent=2))
    else:
        print(render_human(rec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
