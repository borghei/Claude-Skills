#!/usr/bin/env python3
"""Score and sequence process-improvement opportunities into a prioritised backlog.

Costs only touch-time savings as labour money; lead-time (wait) reductions are
tracked separately because removing a queue frees no one's hours. Discounts the
benefit by confidence and delivery risk, computes payback against implementation
cost, assigns a tier, and checks that dependencies are sequenced before the work
that needs them.

Usage:
    python3 improvement_scorer.py --input sample_opportunities.json
    python3 improvement_scorer.py --input sample_opportunities.json --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Benefit is discounted by how well the saving is understood.
CONFIDENCE_FACTOR: Dict[str, float] = {"high": 1.00, "medium": 0.75, "low": 0.50}
# And by the chance the change does not survive contact with the organisation.
RISK_FACTOR: Dict[str, float] = {"low": 1.00, "medium": 0.85, "high": 0.65}

# Lean improvement hierarchy: earlier verbs beat later ones on the same step.
TYPE_RANK: Dict[str, int] = {
    "eliminate": 1,
    "consolidate": 2,
    "parallelise": 3,
    "standardise": 4,
    "automate": 5,
}

# Payback thresholds in months.
TIER_NOW_MONTHS = 3.0
TIER_NEXT_MONTHS = 6.0
TIER_LATER_MONTHS = 12.0
# Effort above this many days is a project, not an improvement, regardless of payback.
PROJECT_EFFORT_DAYS = 20.0


def score_opportunity(opp: Dict[str, Any], hourly_cost: float) -> Dict[str, Any]:
    """Compute savings, payback and tier for a single improvement opportunity."""
    name = opp.get("name", "unnamed")
    touch_minutes = float(opp.get("touch_minutes_saved_per_unit", 0))
    lead_minutes = float(opp.get("lead_minutes_saved_per_unit", 0))
    units = float(opp.get("units_per_month", 0))
    effort_days = float(opp.get("effort_days", 0))
    if min(effort_days, touch_minutes, lead_minutes, units) < 0:
        raise ValueError(f"opportunity '{name}' has a negative input value")
    if lead_minutes and lead_minutes < touch_minutes:
        raise ValueError(
            f"opportunity '{name}' saves more touch time than lead time; "
            "lead_minutes_saved_per_unit must include the touch time saved"
        )

    confidence = str(opp.get("confidence", "medium")).lower()
    risk = str(opp.get("risk", "medium")).lower()
    if confidence not in CONFIDENCE_FACTOR:
        raise ValueError(f"opportunity '{name}' has confidence '{confidence}'; expected high/medium/low")
    if risk not in RISK_FACTOR:
        raise ValueError(f"opportunity '{name}' has risk '{risk}'; expected high/medium/low")

    hours_saved = touch_minutes * units / 60.0
    labour_monthly = hours_saved * hourly_cost
    # Cycle-time value is only real if the business has quantified it; never inferred.
    cycle_monthly = float(opp.get("annual_cycle_time_value", 0)) / 12.0
    gross_monthly = labour_monthly + cycle_monthly
    adjusted_monthly = gross_monthly * CONFIDENCE_FACTOR[confidence] * RISK_FACTOR[risk]
    implementation_cost = effort_days * 8 * hourly_cost
    recurring = float(opp.get("recurring_monthly_cost", 0))
    net_monthly = adjusted_monthly - recurring

    if net_monthly <= 0:
        payback = None
        tier = "DROP"
    else:
        payback = implementation_cost / net_monthly
        if effort_days > PROJECT_EFFORT_DAYS:
            tier = "LATER"
        elif payback <= TIER_NOW_MONTHS:
            tier = "NOW"
        elif payback <= TIER_NEXT_MONTHS:
            tier = "NEXT"
        elif payback <= TIER_LATER_MONTHS:
            tier = "LATER"
        else:
            tier = "DROP"

    kind = str(opp.get("type", "standardise")).lower()
    notes: List[str] = []
    if kind == "automate" and str(opp.get("targets_value_type", "")).lower() == "non_value_added":
        notes.append("Automating non-value-added work locks the waste in. Eliminate the step first.")
    if effort_days > PROJECT_EFFORT_DAYS:
        notes.append(f"{effort_days:.0f} days of effort is a project, not an improvement — needs its own plan.")
    if confidence == "low":
        notes.append("Low confidence in the saving. Measure the current step for two weeks before committing.")
    if risk == "high" and not bool(opp.get("reversible", True)):
        notes.append("High risk and irreversible. Pilot on one segment before rolling out.")
    if lead_minutes > 0 and touch_minutes == 0 and cycle_monthly == 0:
        notes.append(
            f"Saves {lead_minutes:.0f} min of lead time but no labour hours, and no cycle-time "
            "value was supplied. The payback figure understates it — justify on customer "
            "experience or revenue, not cost."
        )

    return {
        "name": name,
        "type": kind,
        "type_rank": TYPE_RANK.get(kind, 9),
        "touch_minutes_saved_per_unit": touch_minutes,
        "lead_minutes_saved_per_unit": lead_minutes,
        "units_per_month": units,
        "hours_saved_per_month": round(hours_saved, 1),
        "monthly_labour_saving": round(labour_monthly, 0),
        "monthly_cycle_time_value": round(cycle_monthly, 0),
        "gross_monthly_saving": round(gross_monthly, 0),
        "adjusted_monthly_saving": round(adjusted_monthly, 0),
        "recurring_monthly_cost": round(recurring, 0),
        "net_monthly_saving": round(net_monthly, 0),
        "annual_net_saving": round(net_monthly * 12, 0),
        "effort_days": effort_days,
        "implementation_cost": round(implementation_cost, 0),
        "payback_months": round(payback, 1) if payback is not None else None,
        "confidence": confidence,
        "risk": risk,
        "tier": tier,
        "dependencies": opp.get("dependencies", []),
        "notes": notes,
    }


def check_sequencing(scored: List[Dict[str, Any]]) -> List[str]:
    """Return warnings where an item is scheduled before something it depends on."""
    order = {"NOW": 0, "NEXT": 1, "LATER": 2, "DROP": 3}
    by_name = {s["name"]: s for s in scored}
    warnings: List[str] = []
    for s in scored:
        for dep in s["dependencies"]:
            target = by_name.get(dep)
            if target is None:
                warnings.append(f"'{s['name']}' depends on '{dep}', which is not in this backlog.")
            elif order[target["tier"]] > order[s["tier"]]:
                warnings.append(
                    f"'{s['name']}' is tiered {s['tier']} but depends on '{dep}' "
                    f"which is tiered {target['tier']}. Promote the dependency or demote the item."
                )
    return warnings


def analyse(data: Dict[str, Any]) -> Dict[str, Any]:
    """Score every opportunity, order the backlog, and check sequencing."""
    opportunities = data.get("opportunities", [])
    if not opportunities:
        raise ValueError("input JSON needs a non-empty 'opportunities' array")
    hourly_cost = float(data.get("hourly_cost", 65))
    if hourly_cost <= 0:
        raise ValueError("'hourly_cost' must be greater than zero")

    scored = [score_opportunity(o, hourly_cost) for o in opportunities]
    tier_order = {"NOW": 0, "NEXT": 1, "LATER": 2, "DROP": 3}
    scored.sort(
        key=lambda s: (
            tier_order[s["tier"]],
            s["payback_months"] if s["payback_months"] is not None else 9999,
            s["type_rank"],
        )
    )

    warnings = check_sequencing(scored)
    counts: Dict[str, int] = {}
    for s in scored:
        counts[s["tier"]] = counts.get(s["tier"], 0) + 1

    committed = [s for s in scored if s["tier"] in ("NOW", "NEXT")]
    return {
        "process_name": data.get("process_name", "unnamed process"),
        "hourly_cost": hourly_cost,
        "opportunities": scored,
        "tier_counts": counts,
        "portfolio": {
            "annual_saving_if_now_and_next": round(sum(s["annual_net_saving"] for s in committed), 0),
            "effort_days_now_and_next": round(sum(s["effort_days"] for s in committed), 1),
            "lead_minutes_removed_now_and_next": round(
                sum(s["lead_minutes_saved_per_unit"] for s in committed), 1
            ),
            "annual_saving_all_viable": round(
                sum(s["annual_net_saving"] for s in scored if s["tier"] != "DROP"), 0
            ),
        },
        "sequencing_warnings": warnings,
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the improvement backlog as JSON or a human-readable report."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    print(f"IMPROVEMENT BACKLOG — {result['process_name']}")
    print("=" * 82)
    print(f"Loaded hourly cost: {result['hourly_cost']:,.0f}")
    print()
    print(
        f"{'Tier':<7}{'Opportunity':<32}{'Type':<14}{'Annual':>11}{'Lead-':>8}{'Days':>6}{'Payback':>9}"
    )
    print(f"{'':<64}{'min/u':>8}")
    print("-" * 82)
    for s in result["opportunities"]:
        payback = f"{s['payback_months']:.1f} mo" if s["payback_months"] is not None else "never"
        print(
            f"{s['tier']:<7}{s['name'][:30]:<32}{s['type'][:13]:<14}"
            f"{s['annual_net_saving']:>11,.0f}{s['lead_minutes_saved_per_unit']:>8.0f}"
            f"{s['effort_days']:>6.0f}{payback:>9}"
        )
    print("-" * 82)
    print("Annual = labour + supplied cycle-time value, discounted for confidence and risk.")
    print("Lead-min/u = elapsed time removed per unit; carries no labour saving on its own.")
    p = result["portfolio"]
    print()
    print(
        f"NOW + NEXT: {p['annual_saving_if_now_and_next']:,.0f} annual saving "
        f"for {p['effort_days_now_and_next']:.0f} days of effort, "
        f"removing {p['lead_minutes_removed_now_and_next']:.0f} min of lead time per unit"
    )
    print(f"All viable tiers: {p['annual_saving_all_viable']:,.0f} annual saving")

    noted = [s for s in result["opportunities"] if s["notes"]]
    if noted:
        print()
        print("NOTES")
        for s in noted:
            for n in s["notes"]:
                print(f"  ! {s['name'][:36]}: {n}")
    if result["sequencing_warnings"]:
        print()
        print("SEQUENCING")
        for w in result["sequencing_warnings"]:
            print(f"  ! {w}")


def main() -> None:
    """Parse arguments, score the backlog, and print the result."""
    parser = argparse.ArgumentParser(
        description="Score and sequence process-improvement opportunities into a backlog.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to an opportunities JSON file (see assets/sample_opportunities.json)",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        output(analyse(data), args.format)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError) as exc:
        print(f"Error: could not score opportunities — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
