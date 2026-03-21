#!/usr/bin/env python3
"""Scenario Builder - Build structured scenarios with variables, probabilities, and severity levels.

Creates war room scenarios following the 6-step cascade model with variables,
detection signals, severity matrix, and hedge recommendations.

Usage:
    python scenario_builder.py --name "Customer Concentration Risk" --variable "Top customer churns" --probability 20 --impact 500000 --timeline 90
    python scenario_builder.py --name "Fundraise Risk" --variable "Series A delayed 6 months:0.3:0:180" --variable "Key engineer leaves:0.15:100000:60" --variable "Competitor raises $50M:0.25:0:90" --arr 2000000 --runway-months 14 --json
"""

import argparse
import json
import sys
from datetime import datetime

CASCADE_PATTERNS = {
    "revenue_death_spiral": {
        "name": "Revenue-to-Runway Death Spiral",
        "pattern": "Customer churn -> lower runway -> hiring freeze -> slower product -> more churn",
        "interruption": "Emergency revenue diversification or bridge financing"
    },
    "key_person_cascade": {
        "name": "Key Person Cascade",
        "pattern": "Star leaves -> team morale drops -> followers leave -> velocity collapses",
        "interruption": "Retention bonuses before departure, succession planning"
    },
    "market_squeeze": {
        "name": "Market Squeeze",
        "pattern": "Competitor raises -> price war -> margins compress -> can't invest in product",
        "interruption": "Differentiation (not price matching), niche down"
    },
    "trust_cascade": {
        "name": "Trust Cascade",
        "pattern": "Incident -> customer concern -> churn -> press -> more churn",
        "interruption": "Swift, transparent communication"
    },
    "fundraise_burn_spiral": {
        "name": "Fundraise-Burn Spiral",
        "pattern": "Miss target -> raise delayed -> bridge at bad terms -> burn cuts -> team loss",
        "interruption": "Parallel fundraise tracks, pre-negotiated bridge terms"
    }
}


def parse_variable(var_str, default_probability=0.2, default_impact=0, default_timeline=90):
    """Parse variable string in format 'description:probability:impact:timeline_days' or just 'description'."""
    parts = var_str.split(":")
    desc = parts[0].strip()
    prob = float(parts[1]) if len(parts) > 1 else default_probability
    impact = float(parts[2]) if len(parts) > 2 else default_impact
    timeline = int(parts[3]) if len(parts) > 3 else default_timeline
    return {"description": desc, "probability": prob, "impact": impact, "timeline_days": timeline}


def identify_cascade_patterns(variables):
    """Identify likely cascade patterns based on variable descriptions."""
    patterns = []
    descriptions = " ".join(v["description"].lower() for v in variables)

    if any(word in descriptions for word in ["churn", "customer", "cancel", "terminate"]):
        patterns.append(CASCADE_PATTERNS["revenue_death_spiral"])
    if any(word in descriptions for word in ["leave", "depart", "quit", "engineer", "key person"]):
        patterns.append(CASCADE_PATTERNS["key_person_cascade"])
    if any(word in descriptions for word in ["competitor", "raise", "funding", "market"]):
        patterns.append(CASCADE_PATTERNS["market_squeeze"])
    if any(word in descriptions for word in ["incident", "breach", "security", "trust"]):
        patterns.append(CASCADE_PATTERNS["trust_cascade"])
    if any(word in descriptions for word in ["fundraise", "series", "round", "investor"]):
        patterns.append(CASCADE_PATTERNS["fundraise_burn_spiral"])

    return patterns if patterns else [CASCADE_PATTERNS["revenue_death_spiral"]]


def build_scenario(name, variables, arr, runway_months):
    if len(variables) > 3:
        print("Warning: Maximum 3 variables recommended. Using first 3.", file=sys.stderr)
        variables = variables[:3]

    # Calculate severity levels
    total_impact = sum(v["impact"] for v in variables)
    monthly_burn = arr / 12 * 1.5 if arr > 0 else 50000  # Estimate burn from ARR

    # Base scenario (1 variable hits)
    base = {
        "name": "Base (single shock)",
        "variables_hit": 1,
        "arr_impact": variables[0]["impact"] if variables else 0,
        "arr_impact_pct": round(variables[0]["impact"] / arr * 100, 1) if arr > 0 and variables else 0,
        "runway_impact_months": round(variables[0]["impact"] / monthly_burn, 1) if monthly_burn > 0 and variables else 0,
        "new_runway": round(runway_months - (variables[0]["impact"] / monthly_burn), 1) if monthly_burn > 0 and variables else runway_months,
        "recovery": "Manageable with prepared response"
    }

    # Stress scenario (2 variables)
    stress_impact = sum(v["impact"] for v in variables[:2])
    stress = {
        "name": "Stress (compound shock)",
        "variables_hit": min(2, len(variables)),
        "arr_impact": stress_impact,
        "arr_impact_pct": round(stress_impact / arr * 100, 1) if arr > 0 else 0,
        "runway_impact_months": round(stress_impact / monthly_burn, 1) if monthly_burn > 0 else 0,
        "new_runway": round(runway_months - (stress_impact / monthly_burn), 1) if monthly_burn > 0 else runway_months,
        "recovery": "Requires significant pivot, board involvement"
    }

    # Severe scenario (all variables)
    severe = {
        "name": "Severe (full cascade)",
        "variables_hit": len(variables),
        "arr_impact": total_impact,
        "arr_impact_pct": round(total_impact / arr * 100, 1) if arr > 0 else 0,
        "runway_impact_months": round(total_impact / monthly_burn, 1) if monthly_burn > 0 else 0,
        "new_runway": round(runway_months - (total_impact / monthly_burn), 1) if monthly_burn > 0 else runway_months,
        "existential": severe_new_runway < 6 if (severe_new_runway := round(runway_months - (total_impact / monthly_burn), 1) if monthly_burn > 0 else runway_months) else False,
        "recovery": "Emergency action required, board intervention"
    }

    # Cascade patterns
    cascade_patterns = identify_cascade_patterns(variables)

    # Early warning signals
    signals = []
    for v in variables:
        signals.append({
            "variable": v["description"],
            "signal": f"Monitor for early indicators of: {v['description']}",
            "threshold": f"Probability rises above {int(v['probability'] * 100 + 10)}%",
            "response_window": f"{max(7, v['timeline_days'] // 4)} days to respond"
        })

    # Hedges
    hedges = []
    if any(v["impact"] > 0 for v in variables):
        hedges.append({"hedge": "Establish credit line or bridge financing option", "cost": "$5K-15K/year", "protects_against": "Runway shortfall", "owner": "CFO", "deadline": "60 days"})
    if any("key" in v["description"].lower() or "leave" in v["description"].lower() or "engineer" in v["description"].lower() for v in variables):
        hedges.append({"hedge": "Retention bonuses for critical team members", "cost": "$50K-150K", "protects_against": "Key person departure", "owner": "CHRO", "deadline": "30 days"})
    if any("customer" in v["description"].lower() or "churn" in v["description"].lower() for v in variables):
        hedges.append({"hedge": "Diversify revenue concentration below 20% per customer", "cost": "Sales effort", "protects_against": "Customer concentration risk", "owner": "CRO", "deadline": "2 quarters"})
    if any("fundraise" in v["description"].lower() or "series" in v["description"].lower() for v in variables):
        hedges.append({"hedge": "Pre-negotiate bridge terms with existing investors", "cost": "CEO time", "protects_against": "Fundraise delay", "owner": "CEO", "deadline": "45 days"})
    if not hedges:
        hedges.append({"hedge": "Document contingency response plan", "cost": "Leadership time", "protects_against": "General preparedness", "owner": "COO", "deadline": "30 days"})

    return {
        "scenario_date": datetime.now().strftime("%Y-%m-%d"),
        "scenario_name": name,
        "review_date": (datetime.now().replace(month=datetime.now().month % 12 + 1) if datetime.now().month < 12
                        else datetime.now().replace(year=datetime.now().year + 1, month=1)).strftime("%Y-%m-%d"),
        "company_context": {
            "arr": arr,
            "runway_months": runway_months,
            "estimated_monthly_burn": round(monthly_burn)
        },
        "variables": [
            {
                "id": chr(65 + i),
                "description": v["description"],
                "probability": f"{int(v['probability'] * 100)}%",
                "probability_raw": v["probability"],
                "impact": v["impact"],
                "timeline_days": v["timeline_days"]
            }
            for i, v in enumerate(variables)
        ],
        "severity_matrix": {
            "base": base,
            "stress": stress,
            "severe": severe
        },
        "cascade_patterns": [{"name": p["name"], "pattern": p["pattern"], "interruption_point": p["interruption"]} for p in cascade_patterns],
        "early_warning_signals": signals,
        "hedges": hedges,
        "ground_rules": [
            "Maximum 3 variables per scenario",
            "Quantify everything: dollar amounts, percentages, timelines",
            "Don't stop at first-order effects -- trace the cascade",
            "Every scenario must have a recovery path",
            "Review every 90 days or after any variable shifts"
        ]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"SCENARIO: {result['scenario_name']}")
    print(f"Date: {result['scenario_date']}  |  Review by: {result['review_date']}")
    print(f"{'='*70}\n")

    ctx = result["company_context"]
    print(f"Context: ARR ${ctx['arr']:,}  |  Runway: {ctx['runway_months']} months  |  Burn: ${ctx['estimated_monthly_burn']:,}/mo\n")

    print("VARIABLES:")
    print("-" * 60)
    for v in result["variables"]:
        print(f"  [{v['id']}] {v['description']}")
        print(f"      Probability: {v['probability']}  |  Impact: ${v['impact']:,}  |  Timeline: {v['timeline_days']} days")

    print(f"\nSEVERITY MATRIX:")
    print("-" * 60)
    for level in ["base", "stress", "severe"]:
        s = result["severity_matrix"][level]
        existential = " [EXISTENTIAL]" if s.get("existential") else ""
        print(f"  {s['name'].upper()}: ARR impact -${s['arr_impact']:,} ({s['arr_impact_pct']}%), Runway: {s['new_runway']} months{existential}")
        print(f"    Recovery: {s['recovery']}")

    print(f"\nCASCADE PATTERNS:")
    for cp in result["cascade_patterns"]:
        print(f"  {cp['name']}: {cp['pattern']}")
        print(f"    Interruption: {cp['interruption_point']}")

    print(f"\nEARLY WARNING SIGNALS:")
    for s in result["early_warning_signals"]:
        print(f"  -> {s['variable']}: {s['threshold']} (respond within {s['response_window']})")

    print(f"\nHEDGES (implement now):")
    for h in result["hedges"]:
        print(f"  [{h['deadline']:<10s}] {h['hedge']} (cost: {h['cost']}, owner: {h['owner']})")
    print()


def main():
    parser = argparse.ArgumentParser(description="Build structured war room scenarios")
    parser.add_argument("--name", required=True, help="Scenario name")
    parser.add_argument("--variable", action="append", required=True,
                        help="Variable in format 'description:probability:impact:timeline_days' (multiple allowed)")
    parser.add_argument("--arr", type=float, default=2000000, help="Current ARR ($)")
    parser.add_argument("--runway-months", type=float, default=14, help="Current runway in months")
    # Legacy single-variable args
    parser.add_argument("--probability", type=float, help="Probability (0-1) for single variable mode")
    parser.add_argument("--impact", type=float, help="Impact ($) for single variable mode")
    parser.add_argument("--timeline", type=int, help="Timeline (days) for single variable mode")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    variables = []
    for var_str in args.variable:
        v = parse_variable(
            var_str,
            default_probability=args.probability or 0.2,
            default_impact=args.impact or 0,
            default_timeline=args.timeline or 90
        )
        variables.append(v)

    result = build_scenario(args.name, variables, args.arr, args.runway_months)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
