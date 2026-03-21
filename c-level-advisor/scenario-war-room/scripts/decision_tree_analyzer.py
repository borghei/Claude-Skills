#!/usr/bin/env python3
"""Decision Tree Analyzer - Build and evaluate decision trees with expected value calculations.

Models strategic decisions with multiple options, each having probability of success,
upside value, and downside cost. Calculates expected value to guide decision-making.

Usage:
    python decision_tree_analyzer.py --decision "Enter Japan market" --option "Direct:0.6:2000000:-500000" --option "Partnership:0.75:1000000:-200000" --option "Wait:1.0:0:0"
    python decision_tree_analyzer.py --decision "Acquire CompanyX" --option "Full acquisition:0.7:5000000:-2000000" --option "Acqui-hire:0.85:1500000:-500000" --option "Build internally:0.5:3000000:-800000" --json
"""

import argparse
import json
import sys
from datetime import datetime


def parse_option(option_str):
    """Parse option in format 'name:probability_success:upside:downside'."""
    parts = option_str.split(":")
    if len(parts) < 4:
        print(f"Error: Option must be 'name:probability:upside:downside'. Got: {option_str}", file=sys.stderr)
        sys.exit(1)
    return {
        "name": parts[0].strip(),
        "probability_success": float(parts[1]),
        "upside": float(parts[2]),
        "downside": float(parts[3])
    }


def analyze_decision(decision_name, options):
    """Analyze all options and compute expected values."""
    analyzed = []

    for opt in options:
        p_success = opt["probability_success"]
        p_failure = 1 - p_success
        upside = opt["upside"]
        downside = opt["downside"]

        expected_value = round(p_success * upside + p_failure * downside)
        expected_upside = round(p_success * upside)
        expected_downside = round(p_failure * downside)
        risk_reward_ratio = round(abs(upside / downside), 2) if downside != 0 else float('inf')
        max_regret = abs(downside)

        analyzed.append({
            "name": opt["name"],
            "probability_success": f"{int(p_success * 100)}%",
            "probability_success_raw": p_success,
            "upside": upside,
            "downside": downside,
            "expected_value": expected_value,
            "expected_upside": expected_upside,
            "expected_downside": expected_downside,
            "risk_reward_ratio": risk_reward_ratio,
            "max_regret": max_regret,
            "reversible": abs(downside) < 100000  # Heuristic
        })

    # Sort by expected value (best first)
    analyzed.sort(key=lambda x: -x["expected_value"])

    # Determine recommendation
    best_ev = analyzed[0]
    lowest_risk = min(analyzed, key=lambda x: x["max_regret"])
    highest_upside = max(analyzed, key=lambda x: x["upside"])

    # Sensitivity check: how much would probability need to change to change the ranking?
    sensitivity = []
    if len(analyzed) >= 2:
        first = analyzed[0]
        second = analyzed[1]
        # At what probability does the second option become better?
        # EV1 = p1 * up1 + (1-p1) * down1
        # EV2 = p2 * up2 + (1-p2) * down2
        # We vary p1: find p where EV1 = EV2_current
        ev2 = second["expected_value"]
        up1 = first["upside"]
        down1 = first["downside"]
        if up1 != down1:
            breakeven_p = (ev2 - down1) / (up1 - down1)
            if 0 <= breakeven_p <= 1:
                sensitivity.append({
                    "insight": f"If '{first['name']}' success probability drops to {int(breakeven_p * 100)}%, '{second['name']}' becomes the better option",
                    "current_probability": first["probability_success"],
                    "breakeven_probability": f"{int(breakeven_p * 100)}%",
                    "margin": f"{int((first['probability_success_raw'] - breakeven_p) * 100)} percentage points"
                })

    return {
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "decision": decision_name,
        "options_analyzed": len(analyzed),
        "options": analyzed,
        "recommendation": {
            "best_expected_value": {"option": best_ev["name"], "ev": best_ev["expected_value"]},
            "lowest_risk": {"option": lowest_risk["name"], "max_regret": lowest_risk["max_regret"]},
            "highest_upside": {"option": highest_upside["name"], "upside": highest_upside["upside"]}
        },
        "sensitivity": sensitivity,
        "decision_framework": {
            "if_reversible": f"Go with '{best_ev['name']}' (highest EV). Speed matters more than perfection for reversible decisions.",
            "if_irreversible": f"Consider '{lowest_risk['name']}' (lowest regret) unless EV difference with '{best_ev['name']}' justifies the risk.",
            "if_constrained": f"'{lowest_risk['name']}' minimizes downside exposure."
        }
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"DECISION TREE ANALYSIS: {result['decision']}")
    print(f"Date: {result['analysis_date']}")
    print(f"{'='*70}\n")

    print("OPTIONS (ranked by Expected Value):")
    print("-" * 70)
    for i, opt in enumerate(result["options"], 1):
        ev_bar_width = max(0, min(20, int(opt["expected_value"] / max(abs(o["expected_value"]) for o in result["options"]) * 20))) if any(o["expected_value"] != 0 for o in result["options"]) else 0
        ev_bar = "#" * ev_bar_width

        print(f"\n  {i}. {opt['name']}")
        print(f"     Success Probability: {opt['probability_success']}")
        print(f"     Upside:   ${opt['upside']:>12,}")
        print(f"     Downside: ${opt['downside']:>12,}")
        print(f"     Expected Value: ${opt['expected_value']:>10,}  {ev_bar}")
        print(f"     Risk/Reward: {opt['risk_reward_ratio']}x  |  Max Regret: ${opt['max_regret']:,}")

    rec = result["recommendation"]
    print(f"\nRECOMMENDATION:")
    print("-" * 50)
    print(f"  Best EV:       {rec['best_expected_value']['option']} (EV: ${rec['best_expected_value']['ev']:,})")
    print(f"  Lowest Risk:   {rec['lowest_risk']['option']} (Max Regret: ${rec['lowest_risk']['max_regret']:,})")
    print(f"  Highest Upside: {rec['highest_upside']['option']} (${rec['highest_upside']['upside']:,})")

    df = result["decision_framework"]
    print(f"\nDECISION FRAMEWORK:")
    print(f"  If reversible:   {df['if_reversible']}")
    print(f"  If irreversible: {df['if_irreversible']}")
    print(f"  If constrained:  {df['if_constrained']}")

    if result["sensitivity"]:
        print(f"\nSENSITIVITY ANALYSIS:")
        for s in result["sensitivity"]:
            print(f"  {s['insight']}")
            print(f"    Current: {s['current_probability']}  |  Breakeven: {s['breakeven_probability']}  |  Margin: {s['margin']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Build and evaluate decision trees with expected value")
    parser.add_argument("--decision", required=True, help="Decision being analyzed")
    parser.add_argument("--option", action="append", required=True,
                        help="Option in format 'name:probability_success:upside:downside' (multiple allowed)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if len(args.option) < 2:
        print("Error: At least 2 options required for meaningful comparison", file=sys.stderr)
        sys.exit(1)

    options = [parse_option(o) for o in args.option]
    result = analyze_decision(args.decision, options)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
