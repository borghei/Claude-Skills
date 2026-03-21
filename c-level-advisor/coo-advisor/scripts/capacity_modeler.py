#!/usr/bin/env python3
"""
Capacity Modeler - Model headcount capacity requirements.

Uses formula: Required HC = Volume / (Productivity x Utilization).
Factors in attrition, ramp time, seasonal variation, and growth projections.
Generates quarterly hiring plans with cost estimates.

Usage:
    python capacity_modeler.py --input capacity_data.json
    python capacity_modeler.py --input capacity_data.json --json
"""

import argparse
import json
import math
import sys
from datetime import datetime


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def calculate_required_hc(volume, productivity, utilization):
    """Core capacity formula: Required HC = Volume / (Productivity x Utilization)."""
    if productivity <= 0 or utilization <= 0:
        return 0
    return volume / (productivity * utilization)


def apply_adjustments(base_hc, adjustments):
    """Apply adjustment factors to base headcount."""
    attrition_rate = adjustments.get("attrition_rate_pct", 15) / 100
    ramp_factor = adjustments.get("ramp_factor", 0.85)
    buffer_pct = adjustments.get("buffer_pct", 10) / 100

    # Attrition adjustment: need extra HC to cover expected departures
    attrition_adjusted = base_hc / (1 - attrition_rate)

    # Ramp adjustment: new hires not at full productivity
    ramp_adjusted = attrition_adjusted / ramp_factor

    # Buffer for unexpected demand
    buffered = ramp_adjusted * (1 + buffer_pct)

    return {
        "base_hc": round(base_hc, 1),
        "after_attrition": round(attrition_adjusted, 1),
        "after_ramp": round(ramp_adjusted, 1),
        "with_buffer": round(buffered, 1),
        "final_required": math.ceil(buffered),
    }


def model_quarters(data):
    """Model capacity across multiple quarters with growth."""
    teams = data.get("teams", [])
    quarters = data.get("quarters", 4)
    growth_rate_pct = data.get("quarterly_growth_rate_pct", 10)
    adjustments = data.get("adjustments", {})
    cost_per_fte = data.get("cost_per_fte_annual", 80000)
    seasonal_factors = data.get("seasonal_factors", [1.0] * quarters)

    results = {
        "timestamp": datetime.now().isoformat(),
        "organization": data.get("organization", "Organization"),
        "quarters_modeled": quarters,
        "team_models": [],
        "quarterly_totals": [],
        "hiring_plan": [],
        "cost_projection": {},
        "summary": {},
        "recommendations": [],
    }

    grand_total_current = 0
    grand_total_required = 0
    total_hiring_cost = 0

    for team in teams:
        team_name = team.get("name", "Team")
        current_hc = team.get("current_headcount", 0)
        base_volume = team.get("volume_per_period", 0)
        productivity = team.get("productivity_per_person", 1)
        utilization = team.get("utilization_pct", 80) / 100

        grand_total_current += current_hc

        team_quarters = []
        prev_required = current_hc

        for q in range(quarters):
            growth_mult = (1 + growth_rate_pct / 100) ** q
            seasonal = seasonal_factors[q] if q < len(seasonal_factors) else 1.0
            projected_volume = base_volume * growth_mult * seasonal

            raw_hc = calculate_required_hc(projected_volume, productivity, utilization)
            adjusted = apply_adjustments(raw_hc, adjustments)

            gap = adjusted["final_required"] - current_hc if q == 0 else adjusted["final_required"] - prev_required
            hires_needed = max(0, gap)

            team_quarters.append({
                "quarter": f"Q{q + 1}",
                "projected_volume": round(projected_volume, 0),
                "raw_required": round(raw_hc, 1),
                "adjusted_required": adjusted["final_required"],
                "gap": gap,
                "hires_needed": math.ceil(hires_needed) if hires_needed > 0 else 0,
                "adjustments": adjusted,
            })

            prev_required = adjusted["final_required"]

        total_hires = sum(q["hires_needed"] for q in team_quarters)
        final_hc = team_quarters[-1]["adjusted_required"] if team_quarters else current_hc

        team_model = {
            "name": team_name,
            "current_headcount": current_hc,
            "final_required": final_hc,
            "total_hires_needed": total_hires,
            "quarters": team_quarters,
        }
        results["team_models"].append(team_model)
        grand_total_required += final_hc

    # Aggregate quarterly totals
    for q in range(quarters):
        q_total_required = 0
        q_total_hires = 0
        for team in results["team_models"]:
            if q < len(team["quarters"]):
                q_total_required += team["quarters"][q]["adjusted_required"]
                q_total_hires += team["quarters"][q]["hires_needed"]

        results["quarterly_totals"].append({
            "quarter": f"Q{q + 1}",
            "total_required": q_total_required,
            "total_hires": q_total_hires,
            "quarterly_cost": round(q_total_hires * cost_per_fte * 0.25, 0),
        })

    # Cost projection
    total_hires = sum(qt["total_hires"] for qt in results["quarterly_totals"])
    total_hiring_cost = total_hires * cost_per_fte
    recruiting_cost = total_hires * cost_per_fte * 0.2
    onboarding_cost = total_hires * 10000

    results["cost_projection"] = {
        "total_new_hires": total_hires,
        "annual_salary_cost": round(total_hiring_cost, 0),
        "recruiting_cost": round(recruiting_cost, 0),
        "onboarding_cost": round(onboarding_cost, 0),
        "total_investment": round(total_hiring_cost + recruiting_cost + onboarding_cost, 0),
        "cost_per_fte": cost_per_fte,
    }

    # Summary
    results["summary"] = {
        "current_total_hc": grand_total_current,
        "projected_required_hc": grand_total_required,
        "total_hiring_gap": grand_total_required - grand_total_current,
        "growth_percentage": round(((grand_total_required / max(grand_total_current, 1)) - 1) * 100, 1),
        "teams_modeled": len(teams),
    }

    # Recommendations
    recs = results["recommendations"]
    growth = results["summary"]["growth_percentage"]
    if growth > 50:
        recs.append(f"High growth ({growth}%) -- implement structured onboarding and mentorship programs")
        recs.append("Consider phased hiring to avoid diluting team quality")
    if growth > 100:
        recs.append("CAUTION: >100% growth planned -- review if timeline is realistic given recruiting capacity")

    max_quarterly_hires = max((qt["total_hires"] for qt in results["quarterly_totals"]), default=0)
    if max_quarterly_hires > grand_total_current * 0.25:
        recs.append(f"Peak quarter needs {max_quarterly_hires} hires -- ensure recruiting capacity (1 recruiter per 15-20 hires/quarter)")

    attrition = adjustments.get("attrition_rate_pct", 15)
    if attrition > 20:
        recs.append(f"Attrition rate {attrition}% is high -- address retention before scaling")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "CAPACITY MODEL",
        "=" * 60,
        f"Organization: {results['organization']}",
        f"Quarters Modeled: {results['quarters_modeled']}",
        f"Analysis Date: {results['timestamp'][:10]}",
        "",
        "SUMMARY",
        f"  Current Headcount: {results['summary']['current_total_hc']}",
        f"  Projected Required: {results['summary']['projected_required_hc']}",
        f"  Hiring Gap: {results['summary']['total_hiring_gap']}",
        f"  Growth: {results['summary']['growth_percentage']}%",
        "",
        "QUARTERLY TOTALS",
    ]

    for qt in results["quarterly_totals"]:
        lines.append(f"  {qt['quarter']}: {qt['total_required']} required (+{qt['total_hires']} hires, ${qt['quarterly_cost']:,.0f})")

    lines.append("")
    lines.append("TEAM DETAIL")
    for team in results["team_models"]:
        lines.append(f"\n  {team['name']}")
        lines.append(f"    Current: {team['current_headcount']} | Target: {team['final_required']} | Hires: {team['total_hires_needed']}")
        for q in team["quarters"]:
            lines.append(
                f"      {q['quarter']}: volume={q['projected_volume']:.0f}, "
                f"required={q['adjusted_required']}, hires={q['hires_needed']}"
            )

    lines.append("")
    lines.append("COST PROJECTION")
    cp = results["cost_projection"]
    lines.append(f"  Total New Hires: {cp['total_new_hires']}")
    lines.append(f"  Annual Salary Cost: ${cp['annual_salary_cost']:,.0f}")
    lines.append(f"  Recruiting Cost: ${cp['recruiting_cost']:,.0f}")
    lines.append(f"  Onboarding Cost: ${cp['onboarding_cost']:,.0f}")
    lines.append(f"  Total Investment: ${cp['total_investment']:,.0f}")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Model headcount capacity requirements with growth projections")
    parser.add_argument("--input", required=True, help="Path to JSON capacity data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = model_quarters(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
