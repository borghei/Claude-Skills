#!/usr/bin/env python3
"""Convert raw headcount into effective delivery capacity for a quarter.

Applies PTO, holidays, on-call load, meeting/ceremony overhead, non-delivery
overhead and new-hire ramp curves to produce defensible effective-hour totals
per person, per discipline and per team.

Usage:
    python3 capacity_model.py --input sample_team.json
    python3 capacity_model.py --input sample_team.json --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Monthly productivity multipliers from first day on the job. Index = months of
# tenure completed. Values past the end of a curve are treated as 1.0.
RAMP_CURVES: Dict[str, List[float]] = {
    "junior": [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00],
    "mid": [0.15, 0.35, 0.55, 0.75, 0.90, 1.00],
    "senior": [0.25, 0.50, 0.75, 0.90, 1.00],
    "staff": [0.30, 0.55, 0.80, 1.00],
    "principal": [0.30, 0.55, 0.80, 1.00],
}

# Share of a person's capacity consumed while carrying the primary on-call pager.
ONCALL_LOSS_PER_WEEK = 0.40

# Effective-hours ratio below which a team is structurally overloaded by overhead.
LOW_UTILISATION_FLOOR = 0.55
# Effective-hours ratio above which the plan is almost certainly optimistic.
OPTIMISTIC_CEILING = 0.80


def ramp_multiplier(seniority: str, tenure_months: float) -> float:
    """Return the productivity multiplier for a given seniority and tenure."""
    curve = RAMP_CURVES.get(seniority.lower(), RAMP_CURVES["mid"])
    if tenure_months < 0:
        return 0.0
    index = int(tenure_months)
    if index >= len(curve):
        return 1.0
    return curve[index]


def quarter_ramp(seniority: str, tenure_months: float) -> float:
    """Average the ramp multiplier across the three months of a quarter."""
    samples = [ramp_multiplier(seniority, tenure_months + m) for m in range(3)]
    return sum(samples) / len(samples)


def member_capacity(member: Dict[str, Any], working_days: int, hours_per_day: float) -> Dict[str, Any]:
    """Compute gross, available and effective hours for one team member."""
    name = member.get("name", "unnamed")
    fte = float(member.get("fte", 1.0))
    seniority = str(member.get("seniority", "mid"))
    tenure = float(member.get("tenure_months", 24))

    gross = working_days * hours_per_day * fte

    pto_hours = float(member.get("pto_days", 0)) * hours_per_day * fte
    oncall_hours = float(member.get("oncall_weeks", 0)) * 5 * hours_per_day * ONCALL_LOSS_PER_WEEK * fte
    after_absence = max(gross - pto_hours - oncall_hours, 0.0)

    meeting_pct = float(member.get("meeting_load_pct", 15)) / 100.0
    overhead_pct = float(member.get("overhead_pct", 10)) / 100.0
    drag = min(meeting_pct + overhead_pct, 0.95)
    available = after_absence * (1 - drag)

    ramp = quarter_ramp(seniority, tenure)
    effective = available * ramp

    return {
        "name": name,
        "discipline": member.get("discipline", "engineering"),
        "seniority": seniority,
        "fte": round(fte, 2),
        "gross_hours": round(gross, 1),
        "pto_hours": round(pto_hours, 1),
        "oncall_hours": round(oncall_hours, 1),
        "meeting_overhead_hours": round(after_absence * drag, 1),
        "available_hours": round(available, 1),
        "ramp_multiplier": round(ramp, 3),
        "effective_hours": round(effective, 1),
        "effective_fte": round(effective / gross, 3) if gross else 0.0,
    }


def analyse(data: Dict[str, Any]) -> Dict[str, Any]:
    """Model effective capacity for the whole team described in the input."""
    team = data.get("team", [])
    if not team:
        raise ValueError("input JSON needs a non-empty 'team' array")

    working_days = int(data.get("working_days_in_quarter", 62))
    hours_per_day = float(data.get("hours_per_day", 8))

    members = [member_capacity(m, working_days, hours_per_day) for m in team]

    by_discipline: Dict[str, Dict[str, float]] = {}
    for m in members:
        bucket = by_discipline.setdefault(
            m["discipline"], {"headcount_fte": 0.0, "gross_hours": 0.0, "effective_hours": 0.0}
        )
        bucket["headcount_fte"] += m["fte"]
        bucket["gross_hours"] += m["gross_hours"]
        bucket["effective_hours"] += m["effective_hours"]

    for bucket in by_discipline.values():
        gross = bucket["gross_hours"]
        bucket["utilisation_ratio"] = round(bucket["effective_hours"] / gross, 3) if gross else 0.0
        bucket["headcount_fte"] = round(bucket["headcount_fte"], 2)
        bucket["gross_hours"] = round(gross, 1)
        bucket["effective_hours"] = round(bucket["effective_hours"], 1)

    total_gross = sum(m["gross_hours"] for m in members)
    total_effective = sum(m["effective_hours"] for m in members)
    ratio = total_effective / total_gross if total_gross else 0.0

    warnings: List[str] = []
    if ratio < LOW_UTILISATION_FLOOR:
        warnings.append(
            f"Effective-hours ratio {ratio:.0%} is below {LOW_UTILISATION_FLOOR:.0%} — "
            "overhead is eating the team; audit meeting load and on-call rotation size."
        )
    if ratio > OPTIMISTIC_CEILING:
        warnings.append(
            f"Effective-hours ratio {ratio:.0%} exceeds {OPTIMISTIC_CEILING:.0%} — "
            "the model is almost certainly missing PTO, interrupts or ceremony time."
        )
    ramping = [m["name"] for m in members if m["ramp_multiplier"] < 0.95]
    if ramping:
        warnings.append(
            f"{len(ramping)} member(s) still ramping this quarter: {', '.join(ramping)}. "
            "Do not commit their nominal capacity."
        )
    solo_disciplines = [d for d, b in by_discipline.items() if b["headcount_fte"] <= 1.0]
    if solo_disciplines:
        warnings.append(
            "Single-person discipline(s) with no redundancy: " + ", ".join(sorted(solo_disciplines))
        )

    return {
        "quarter": data.get("quarter", "unspecified"),
        "working_days_in_quarter": working_days,
        "hours_per_day": hours_per_day,
        "members": members,
        "by_discipline": by_discipline,
        "totals": {
            "headcount_fte": round(sum(m["fte"] for m in members), 2),
            "gross_hours": round(total_gross, 1),
            "effective_hours": round(total_effective, 1),
            "effective_fte_equivalent": round(
                total_effective / (working_days * hours_per_day), 2
            )
            if working_days
            else 0.0,
            "utilisation_ratio": round(ratio, 3),
        },
        "warnings": warnings,
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the capacity model as JSON or a human-readable report."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    t = result["totals"]
    print(f"CAPACITY MODEL — {result['quarter']}")
    print("=" * 68)
    print(
        f"{result['working_days_in_quarter']} working days x {result['hours_per_day']}h  "
        f"| {t['headcount_fte']} FTE on payroll"
    )
    print()
    print(f"{'Name':<20}{'Sen.':<11}{'Gross':>8}{'Avail':>8}{'Ramp':>7}{'Effective':>11}")
    print("-" * 68)
    for m in result["members"]:
        print(
            f"{m['name'][:19]:<20}{m['seniority'][:10]:<11}{m['gross_hours']:>8.0f}"
            f"{m['available_hours']:>8.0f}{m['ramp_multiplier']:>7.2f}{m['effective_hours']:>11.0f}"
        )
    print("-" * 68)
    print()
    print("BY DISCIPLINE")
    for name, bucket in sorted(result["by_discipline"].items()):
        print(
            f"  {name:<18} {bucket['effective_hours']:>8.0f}h effective "
            f"({bucket['utilisation_ratio']:.0%} of gross, {bucket['headcount_fte']} FTE)"
        )
    print()
    print(
        f"TOTAL: {t['effective_hours']:.0f} effective hours "
        f"= {t['effective_fte_equivalent']} delivery-FTE "
        f"({t['utilisation_ratio']:.0%} of {t['gross_hours']:.0f} gross)"
    )
    if result["warnings"]:
        print()
        print("WARNINGS")
        for w in result["warnings"]:
            print(f"  ! {w}")


def main() -> None:
    """Parse arguments, run the capacity model, and print the result."""
    parser = argparse.ArgumentParser(
        description="Convert raw headcount into effective delivery capacity for a quarter.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input", required=True, help="Path to a team definition JSON file (see assets/sample_team.json)"
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args()

    try:
        raw = Path(args.input).read_text(encoding="utf-8")
        data = json.loads(raw)
        output(analyse(data), args.format)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError) as exc:
        print(f"Error: could not model capacity — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
