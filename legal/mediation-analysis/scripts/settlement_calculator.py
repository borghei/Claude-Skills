#!/usr/bin/env python3
"""
Settlement Calculator

Takes dispute parameters and calculates BATNA/WATNA for each party, ZOPA range,
and three settlement scenarios (conservative, balanced, creative). Supports
both inline parameters and JSON input.

Usage:
    python settlement_calculator.py --input params.json
    python settlement_calculator.py --input params.json --json
    python settlement_calculator.py --claimed 500000 --litigation-cost-a 80000 \
        --litigation-cost-b 120000 --probability 0.65 --time-to-trial 18
    python settlement_calculator.py --input params.json --output settlement.json

Input JSON schema:
{
    "claimed_amount": 500000,
    "litigation_cost_a": 80000,
    "litigation_cost_b": 120000,
    "success_probability": 0.65,
    "time_to_trial_months": 18,
    "discount_rate_annual": 0.05,
    "partial_recovery_low": 0.3,
    "partial_recovery_high": 0.8,
    "non_monetary_factors": ["ongoing relationship", "confidentiality"],
    "counterclaim_amount": 0,
    "counterclaim_probability": 0.0,
    "party_a_name": "Claimant",
    "party_b_name": "Respondent"
}
"""

import argparse
import json
import math
import sys
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_PARAMS = {
    "claimed_amount": 0,
    "litigation_cost_a": 0,
    "litigation_cost_b": 0,
    "success_probability": 0.5,
    "time_to_trial_months": 12,
    "discount_rate_annual": 0.05,
    "partial_recovery_low": 0.3,
    "partial_recovery_high": 0.8,
    "non_monetary_factors": [],
    "counterclaim_amount": 0,
    "counterclaim_probability": 0.0,
    "party_a_name": "Party A (Claimant)",
    "party_b_name": "Party B (Respondent)",
}


def present_value(amount: float, months: int, annual_rate: float) -> float:
    """Calculate present value of a future amount."""
    if annual_rate <= 0 or months <= 0:
        return amount
    years = months / 12.0
    return amount / ((1 + annual_rate) ** years)


def calculate_batna_watna(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate BATNA and WATNA for both parties."""
    claimed = params["claimed_amount"]
    cost_a = params["litigation_cost_a"]
    cost_b = params["litigation_cost_b"]
    prob = params["success_probability"]
    months = params["time_to_trial_months"]
    rate = params["discount_rate_annual"]
    low_pct = params["partial_recovery_low"]
    high_pct = params["partial_recovery_high"]
    counterclaim = params.get("counterclaim_amount", 0)
    counter_prob = params.get("counterclaim_probability", 0)

    # Party A (Claimant) analysis
    a_best_case = claimed - cost_a  # Win full amount minus own costs
    a_worst_case = -cost_a - (counterclaim * counter_prob)  # Lose, pay costs, face counterclaim
    a_expected_value = (prob * claimed * (low_pct + high_pct) / 2) - cost_a
    a_expected_pv = present_value(a_expected_value, months, rate)

    # Risk-adjusted expected value
    a_risk_adjusted = (prob * claimed) - cost_a - (counter_prob * counterclaim)

    # Party B (Respondent) analysis
    b_best_case = -cost_b  # Win case, only pay own costs
    b_worst_case = -(claimed + cost_b)  # Lose full amount plus costs
    b_expected_value = -(prob * claimed * (low_pct + high_pct) / 2) - cost_b
    b_expected_pv = present_value(abs(b_expected_value), months, rate) * -1

    # Risk-adjusted for respondent
    b_risk_adjusted = -(prob * claimed) - cost_b + (counter_prob * counterclaim)

    return {
        "party_a": {
            "name": params["party_a_name"],
            "best_case_trial": round(a_best_case, 2),
            "worst_case_trial": round(a_worst_case, 2),
            "expected_value": round(a_expected_value, 2),
            "present_value": round(a_expected_pv, 2),
            "risk_adjusted": round(a_risk_adjusted, 2),
            "litigation_cost": cost_a,
        },
        "party_b": {
            "name": params["party_b_name"],
            "best_case_trial": round(b_best_case, 2),
            "worst_case_trial": round(b_worst_case, 2),
            "expected_value": round(b_expected_value, 2),
            "present_value": round(b_expected_pv, 2),
            "risk_adjusted": round(b_risk_adjusted, 2),
            "litigation_cost": cost_b,
        },
    }


def calculate_zopa(params: Dict[str, Any], batna: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate Zone of Possible Agreement."""
    claimed = params["claimed_amount"]
    prob = params["success_probability"]
    cost_a = params["litigation_cost_a"]
    cost_b = params["litigation_cost_b"]

    # Party A's minimum acceptable: what they'd get at trial minus costs and risk
    a_minimum = max(0, (prob * claimed) - cost_a)

    # Party B's maximum acceptable: what they'd lose at trial plus costs avoided
    b_maximum = (prob * claimed) + cost_b

    zopa_exists = a_minimum < b_maximum
    zopa_range = round(b_maximum - a_minimum, 2) if zopa_exists else 0
    midpoint = round((a_minimum + b_maximum) / 2, 2) if zopa_exists else 0

    return {
        "exists": zopa_exists,
        "party_a_minimum": round(a_minimum, 2),
        "party_b_maximum": round(b_maximum, 2),
        "range": zopa_range,
        "midpoint": midpoint,
        "as_percentage_of_claim": round(midpoint / claimed * 100, 1) if claimed > 0 else 0,
    }


def generate_scenarios(
    params: Dict[str, Any], batna: Dict[str, Any], zopa: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generate three settlement scenarios."""
    claimed = params["claimed_amount"]
    non_monetary = params.get("non_monetary_factors", [])

    scenarios = []

    # Scenario 1: Straightforward Compromise (split-the-difference within ZOPA)
    if zopa["exists"]:
        compromise_amount = zopa["midpoint"]
    else:
        # If no ZOPA, use risk-adjusted midpoint
        compromise_amount = round(claimed * params["success_probability"] * 0.75, 2)

    scenarios.append({
        "name": "Straightforward Compromise",
        "settlement_amount": round(compromise_amount, 2),
        "percentage_of_claim": round(compromise_amount / claimed * 100, 1) if claimed > 0 else 0,
        "rationale": (
            "Pure monetary split based on litigation risk analysis. "
            "Amount reflects the expected value of litigation discounted by costs and uncertainty."
        ),
        "terms": [
            f"Lump sum payment of {compromise_amount:,.2f}",
            "Full and final settlement",
            "Mutual release of all claims",
            "Each party bears own costs",
        ],
        "suitable_when": "Simple monetary dispute with no ongoing relationship",
    })

    # Scenario 2: Interest-Based Solution
    interest_amount = round(compromise_amount * 0.85, 2)  # Slightly less cash
    interest_terms = [
        f"Monetary component: {interest_amount:,.2f}",
        "Mutual release with non-disparagement clause",
        "Confidentiality of settlement terms",
    ]
    if "ongoing relationship" in [f.lower() for f in non_monetary]:
        interest_terms.append("Framework for future business dealings")
    if "confidentiality" in [f.lower() for f in non_monetary]:
        interest_terms.append("Enhanced confidentiality provisions")
    if non_monetary:
        interest_terms.append(f"Non-monetary elements: {', '.join(non_monetary)}")

    scenarios.append({
        "name": "Interest-Based Solution",
        "settlement_amount": interest_amount,
        "percentage_of_claim": round(interest_amount / claimed * 100, 1) if claimed > 0 else 0,
        "rationale": (
            "Lower monetary amount offset by non-monetary value. "
            "Addresses underlying interests beyond pure financial recovery."
        ),
        "terms": interest_terms,
        "suitable_when": "Parties have ongoing relationship or value non-monetary outcomes",
    })

    # Scenario 3: Package Deal (phased payment + non-monetary)
    total_package = round(compromise_amount * 1.05, 2)  # Slightly more total value
    initial_payment = round(total_package * 0.5, 2)
    deferred_payment = round(total_package * 0.5, 2)

    package_terms = [
        f"Initial payment: {initial_payment:,.2f} within 30 days",
        f"Deferred payment: {deferred_payment:,.2f} over 6-12 months",
        f"Total package value: {total_package:,.2f}",
        "Mutual release upon completion of all payments",
        "Performance guarantee / security for deferred payments",
    ]
    if non_monetary:
        package_terms.append(f"Non-monetary elements: {', '.join(non_monetary)}")

    scenarios.append({
        "name": "Package Deal",
        "settlement_amount": total_package,
        "percentage_of_claim": round(total_package / claimed * 100, 1) if claimed > 0 else 0,
        "rationale": (
            "Higher total value delivered through phased payments, reducing immediate "
            "cash burden on paying party while providing certainty to receiving party. "
            "Bundles monetary and non-monetary elements."
        ),
        "terms": package_terms,
        "suitable_when": "Paying party has cash flow constraints; multiple issues to trade off",
    })

    return scenarios


def build_sensitivity(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Run sensitivity analysis across probability ranges."""
    claimed = params["claimed_amount"]
    cost_a = params["litigation_cost_a"]
    cost_b = params["litigation_cost_b"]
    results = []
    for prob in [0.2, 0.35, 0.5, 0.65, 0.8]:
        a_min = max(0, (prob * claimed) - cost_a)
        b_max = (prob * claimed) + cost_b
        mid = round((a_min + b_max) / 2, 2)
        results.append({
            "probability": prob,
            "party_a_minimum": round(a_min, 2),
            "party_b_maximum": round(b_max, 2),
            "midpoint": mid,
            "zopa_exists": a_min < b_max,
        })
    return results


def format_currency(amount: float) -> str:
    """Format number as currency string."""
    if amount < 0:
        return f"-{abs(amount):,.2f}"
    return f"{amount:,.2f}"


def format_human_report(result: Dict[str, Any]) -> str:
    """Format results as human-readable report."""
    lines = []
    lines.append("=" * 72)
    lines.append("SETTLEMENT ANALYSIS REPORT")
    lines.append("=" * 72)

    p = result["parameters"]
    lines.append(f"\nClaimed amount:        {format_currency(p['claimed_amount'])}")
    lines.append(f"Success probability:   {p['success_probability']:.0%}")
    lines.append(f"Time to trial:         {p['time_to_trial_months']} months")
    lines.append(f"Litigation cost (A):   {format_currency(p['litigation_cost_a'])}")
    lines.append(f"Litigation cost (B):   {format_currency(p['litigation_cost_b'])}")

    b = result["batna_watna"]
    lines.append(f"\n--- {b['party_a']['name'].upper()} ---")
    lines.append(f"  Best case at trial:   {format_currency(b['party_a']['best_case_trial'])}")
    lines.append(f"  Worst case at trial:  {format_currency(b['party_a']['worst_case_trial'])}")
    lines.append(f"  Expected value:       {format_currency(b['party_a']['expected_value'])}")
    lines.append(f"  Risk-adjusted:        {format_currency(b['party_a']['risk_adjusted'])}")

    lines.append(f"\n--- {b['party_b']['name'].upper()} ---")
    lines.append(f"  Best case at trial:   {format_currency(b['party_b']['best_case_trial'])}")
    lines.append(f"  Worst case at trial:  {format_currency(b['party_b']['worst_case_trial'])}")
    lines.append(f"  Expected value:       {format_currency(b['party_b']['expected_value'])}")
    lines.append(f"  Risk-adjusted:        {format_currency(b['party_b']['risk_adjusted'])}")

    z = result["zopa"]
    lines.append(f"\n--- ZOPA ---")
    lines.append(f"  ZOPA exists:          {'YES' if z['exists'] else 'NO'}")
    if z["exists"]:
        lines.append(f"  A minimum:            {format_currency(z['party_a_minimum'])}")
        lines.append(f"  B maximum:            {format_currency(z['party_b_maximum'])}")
        lines.append(f"  Range:                {format_currency(z['range'])}")
        lines.append(f"  Midpoint:             {format_currency(z['midpoint'])} ({z['as_percentage_of_claim']}% of claim)")

    lines.append("\n--- SETTLEMENT SCENARIOS ---")
    for i, s in enumerate(result["scenarios"], 1):
        lines.append(f"\n  Scenario {i}: {s['name']}")
        lines.append(f"    Amount:    {format_currency(s['settlement_amount'])} ({s['percentage_of_claim']}% of claim)")
        lines.append(f"    Rationale: {s['rationale'][:150]}")
        lines.append(f"    Suitable:  {s['suitable_when']}")
        lines.append(f"    Terms:")
        for t in s["terms"]:
            lines.append(f"      - {t}")

    lines.append("\n--- SENSITIVITY ANALYSIS ---")
    lines.append(f"  {'Prob':>6s}  {'A Min':>12s}  {'B Max':>12s}  {'Midpoint':>12s}  ZOPA")
    for sa in result["sensitivity"]:
        lines.append(
            f"  {sa['probability']:>5.0%}  {format_currency(sa['party_a_minimum']):>12s}  "
            f"{format_currency(sa['party_b_maximum']):>12s}  "
            f"{format_currency(sa['midpoint']):>12s}  {'Yes' if sa['zopa_exists'] else 'No'}"
        )

    lines.append("\n" + "=" * 72)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate settlement ranges, BATNA/WATNA, ZOPA, and scenarios."
    )
    parser.add_argument("--input", "-i", type=str, help="Path to parameters JSON file")
    parser.add_argument("--claimed", type=float, help="Claimed amount")
    parser.add_argument("--litigation-cost-a", type=float, help="Party A litigation costs")
    parser.add_argument("--litigation-cost-b", type=float, help="Party B litigation costs")
    parser.add_argument("--probability", type=float, help="Success probability (0-1)")
    parser.add_argument("--time-to-trial", type=int, help="Months to trial")
    parser.add_argument("--output", "-o", type=str, help="Path to save output (JSON)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        params = dict(DEFAULT_PARAMS)

        if args.input:
            with open(args.input, "r", encoding="utf-8") as f:
                file_params = json.load(f)
            params.update(file_params)
        elif args.claimed is not None:
            params["claimed_amount"] = args.claimed
            if args.litigation_cost_a is not None:
                params["litigation_cost_a"] = args.litigation_cost_a
            if args.litigation_cost_b is not None:
                params["litigation_cost_b"] = args.litigation_cost_b
            if args.probability is not None:
                params["success_probability"] = args.probability
            if args.time_to_trial is not None:
                params["time_to_trial_months"] = args.time_to_trial
        else:
            parser.print_help()
            sys.exit(1)

        if params["claimed_amount"] <= 0:
            print("Error: Claimed amount must be positive.", file=sys.stderr)
            sys.exit(1)
        if not (0 <= params["success_probability"] <= 1):
            print("Error: Probability must be between 0 and 1.", file=sys.stderr)
            sys.exit(1)

        batna = calculate_batna_watna(params)
        zopa = calculate_zopa(params, batna)
        scenarios = generate_scenarios(params, batna, zopa)
        sensitivity = build_sensitivity(params)

        result = {
            "parameters": params,
            "batna_watna": batna,
            "zopa": zopa,
            "scenarios": scenarios,
            "sensitivity": sensitivity,
        }

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Settlement analysis saved to {args.output}")
        elif args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_human_report(result))

    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
