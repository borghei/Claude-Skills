#!/usr/bin/env python3
"""Impact Matrix Calculator - Calculate compound impact across multiple risk variables.

Models compound risk when multiple adverse events co-occur. Calculates expected value,
worst-case scenarios, and cascade risk scores for strategic decision-making.

Usage:
    python impact_matrix_calculator.py --variables "churn:500000:0.2" "fundraise_delay:0:0.3" "key_departure:0:0.15" --arr 2000000 --runway-months 14
    python impact_matrix_calculator.py --variables "market_shift:300000:0.25" "pricing_pressure:200000:0.35" --arr 5000000 --runway-months 18 --json
"""

import argparse
import json
import sys
from datetime import datetime
from itertools import combinations


def parse_variable(var_str):
    """Parse 'name:impact:probability' format."""
    parts = var_str.split(":")
    if len(parts) < 3:
        print(f"Error: Variable must be in format 'name:impact:probability'. Got: {var_str}", file=sys.stderr)
        sys.exit(1)
    return {
        "name": parts[0].strip(),
        "impact": float(parts[1]),
        "probability": float(parts[2])
    }


def calculate_combinations(variables):
    """Calculate all possible combinations of variables occurring."""
    combos = []

    # Individual variables
    for v in variables:
        combos.append({
            "variables": [v["name"]],
            "combined_probability": v["probability"],
            "total_impact": v["impact"],
            "severity": "base"
        })

    # Pairs
    if len(variables) >= 2:
        for pair in combinations(variables, 2):
            combined_prob = pair[0]["probability"] * pair[1]["probability"]
            total_impact = sum(p["impact"] for p in pair)
            # Cascade multiplier: compound events are worse than sum of parts
            cascade_multiplier = 1.3
            combos.append({
                "variables": [p["name"] for p in pair],
                "combined_probability": round(combined_prob, 4),
                "total_impact": round(total_impact * cascade_multiplier),
                "cascade_multiplier": cascade_multiplier,
                "severity": "stress"
            })

    # All three
    if len(variables) >= 3:
        combined_prob = 1.0
        for v in variables:
            combined_prob *= v["probability"]
        total_impact = sum(v["impact"] for v in variables)
        cascade_multiplier = 1.6  # Full cascade is significantly worse
        combos.append({
            "variables": [v["name"] for v in variables],
            "combined_probability": round(combined_prob, 4),
            "total_impact": round(total_impact * cascade_multiplier),
            "cascade_multiplier": cascade_multiplier,
            "severity": "severe"
        })

    return combos


def calculate_expected_values(variables, combos, arr, runway_months):
    """Calculate expected values and risk-adjusted impacts."""
    monthly_burn = arr / 12 * 1.5 if arr > 0 else 50000

    # Expected value (probability-weighted average impact)
    expected_value = sum(v["impact"] * v["probability"] for v in variables)

    # Risk-adjusted scenarios
    scenarios = []
    for combo in combos:
        runway_impact = combo["total_impact"] / monthly_burn if monthly_burn > 0 else 0
        new_runway = runway_months - runway_impact

        scenarios.append({
            "variables": combo["variables"],
            "severity": combo["severity"],
            "probability": f"{combo['combined_probability'] * 100:.1f}%",
            "probability_raw": combo["combined_probability"],
            "total_impact": combo["total_impact"],
            "arr_impact_pct": round(combo["total_impact"] / arr * 100, 1) if arr > 0 else 0,
            "runway_change": round(-runway_impact, 1),
            "new_runway": round(new_runway, 1),
            "existential": new_runway < 6,
            "expected_value": round(combo["total_impact"] * combo["combined_probability"])
        })

    # Risk score (0-100)
    max_impact = max(c["total_impact"] for c in combos) if combos else 0
    max_prob = max(v["probability"] for v in variables) if variables else 0
    risk_score = round(min(100, (max_impact / arr * 50 if arr > 0 else 50) + (max_prob * 50)))

    # Determine risk level
    if risk_score >= 70:
        risk_level = "CRITICAL"
    elif risk_score >= 50:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    return {
        "calculation_date": datetime.now().strftime("%Y-%m-%d"),
        "inputs": {
            "variables": [{"name": v["name"], "impact": v["impact"], "probability": f"{v['probability']*100:.0f}%"} for v in variables],
            "arr": arr,
            "runway_months": runway_months,
            "estimated_monthly_burn": round(monthly_burn)
        },
        "expected_value": round(expected_value),
        "expected_value_pct_arr": round(expected_value / arr * 100, 1) if arr > 0 else 0,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "worst_case_impact": max_impact,
        "worst_case_pct_arr": round(max_impact / arr * 100, 1) if arr > 0 else 0,
        "scenarios": sorted(scenarios, key=lambda s: -s["total_impact"]),
        "key_insights": generate_insights(variables, scenarios, arr, runway_months, risk_level)
    }


def generate_insights(variables, scenarios, arr, runway_months, risk_level):
    insights = []

    existential = [s for s in scenarios if s.get("existential")]
    if existential:
        insights.append(f"EXISTENTIAL RISK: {len(existential)} scenario(s) reduce runway below 6 months")

    high_prob = [v for v in variables if v["probability"] > 0.25]
    if high_prob:
        insights.append(f"HIGH PROBABILITY: {', '.join(v['name'] for v in high_prob)} have >25% likelihood")

    high_impact = [v for v in variables if arr > 0 and v["impact"] / arr > 0.15]
    if high_impact:
        insights.append(f"HIGH IMPACT: {', '.join(v['name'] for v in high_impact)} would affect >15% of ARR")

    if risk_level in ("CRITICAL", "HIGH"):
        insights.append("Recommend immediate war room session with full leadership team")
        insights.append("Implement hedging strategies before next board meeting")

    return insights


def print_human(result):
    print(f"\n{'='*70}")
    print(f"IMPACT MATRIX ANALYSIS")
    print(f"Date: {result['calculation_date']}")
    print(f"{'='*70}\n")

    inp = result["inputs"]
    print(f"Context: ARR ${inp['arr']:,}  |  Runway: {inp['runway_months']} months  |  Burn: ${inp['estimated_monthly_burn']:,}/mo\n")

    print(f"RISK SCORE: {result['risk_score']}/100 ({result['risk_level']})")
    print(f"Expected Value of Loss: ${result['expected_value']:,} ({result['expected_value_pct_arr']}% of ARR)")
    print(f"Worst Case Impact: ${result['worst_case_impact']:,} ({result['worst_case_pct_arr']}% of ARR)\n")

    print("INPUT VARIABLES:")
    print("-" * 50)
    for v in result["inputs"]["variables"]:
        print(f"  {v['name']:<30s} Impact: ${v['impact']:>10,}  Prob: {v['probability']}")

    print(f"\nSCENARIO MATRIX:")
    print("-" * 70)
    for s in result["scenarios"]:
        existential_flag = " [EXISTENTIAL]" if s.get("existential") else ""
        print(f"  [{s['severity'].upper():<8s}] {' + '.join(s['variables'])}")
        print(f"    Probability: {s['probability']:>6s}  Impact: ${s['total_impact']:>10,}  Runway: {s['new_runway']:>5.1f}mo  EV: ${s['expected_value']:>8,}{existential_flag}")

    if result["key_insights"]:
        print(f"\nKEY INSIGHTS:")
        for i in result["key_insights"]:
            print(f"  -> {i}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Calculate compound risk impact across multiple variables")
    parser.add_argument("--variables", nargs="+", required=True, help="Variables in format 'name:impact:probability'")
    parser.add_argument("--arr", type=float, required=True, help="Current ARR ($)")
    parser.add_argument("--runway-months", type=float, required=True, help="Current runway in months")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    variables = [parse_variable(v) for v in args.variables]
    if len(variables) > 3:
        print("Warning: Maximum 3 variables. Using first 3.", file=sys.stderr)
        variables = variables[:3]

    combos = calculate_combinations(variables)
    result = calculate_expected_values(variables, combos, args.arr, args.runway_months)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
