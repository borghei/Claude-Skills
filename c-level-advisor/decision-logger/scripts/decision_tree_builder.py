#!/usr/bin/env python3
"""
Decision Tree Builder - Build decision trees with expected value analysis.

Calculates optimal paths through probability-weighted outcomes, identifies
highest-value decisions, and generates sensitivity analysis on key assumptions.

Usage:
    python decision_tree_builder.py --input tree_data.json
    python decision_tree_builder.py --input tree_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def calculate_expected_value(outcomes):
    """Calculate expected value from probability-weighted outcomes."""
    ev = 0
    for outcome in outcomes:
        probability = outcome.get("probability", 0)
        value = outcome.get("value", 0)
        ev += probability * value
    return round(ev, 2)


def validate_probabilities(outcomes):
    """Validate that probabilities sum to approximately 1.0."""
    total = sum(o.get("probability", 0) for o in outcomes)
    return abs(total - 1.0) < 0.05  # Allow 5% tolerance


def build_tree(node, depth=0, path=""):
    """Recursively build and evaluate a decision tree."""
    node_type = node.get("type", "decision")
    name = node.get("name", f"Node-{depth}")
    current_path = f"{path}/{name}" if path else name

    result = {
        "name": name,
        "type": node_type,
        "depth": depth,
        "path": current_path,
    }

    if node_type == "outcome":
        # Terminal node
        result["value"] = node.get("value", 0)
        result["expected_value"] = node.get("value", 0)
        return result

    if node_type == "chance":
        # Chance node: calculate expected value from outcomes
        outcomes = node.get("outcomes", [])
        prob_valid = validate_probabilities(outcomes)
        result["probability_valid"] = prob_valid

        children = []
        ev = 0
        for outcome in outcomes:
            child = build_tree(outcome.get("node", {"type": "outcome", "value": outcome.get("value", 0)}),
                               depth + 1, current_path)
            child["probability"] = outcome.get("probability", 0)
            child["outcome_label"] = outcome.get("label", "Unknown")
            child_ev = outcome.get("probability", 0) * child.get("expected_value", 0)
            ev += child_ev
            child["weighted_value"] = round(child_ev, 2)
            children.append(child)

        result["children"] = children
        result["expected_value"] = round(ev, 2)
        return result

    if node_type == "decision":
        # Decision node: choose option with highest expected value
        options = node.get("options", [])
        children = []
        best_ev = float("-inf")
        best_option = None

        for option in options:
            child = build_tree(option, depth + 1, current_path)
            children.append(child)
            child_ev = child.get("expected_value", 0)
            cost = option.get("cost", 0)
            net_ev = child_ev - cost
            child["cost"] = cost
            child["net_expected_value"] = round(net_ev, 2)

            if net_ev > best_ev:
                best_ev = net_ev
                best_option = child["name"]

        result["children"] = children
        result["best_option"] = best_option
        result["best_expected_value"] = round(best_ev, 2)
        result["expected_value"] = round(best_ev, 2)
        return result

    return result


def sensitivity_analysis(tree_data, variable_name, range_pct=20, steps=5):
    """Run sensitivity analysis on a key variable."""
    results = []
    base_tree = build_tree(tree_data)
    base_ev = base_tree.get("best_expected_value", base_tree.get("expected_value", 0))

    # Simple sensitivity: vary the first probability we find
    for step in range(-steps, steps + 1):
        factor = 1 + (step * range_pct / 100 / steps)

        # Deep copy and modify
        modified = json.loads(json.dumps(tree_data))
        _apply_sensitivity(modified, variable_name, factor)

        modified_tree = build_tree(modified)
        modified_ev = modified_tree.get("best_expected_value", modified_tree.get("expected_value", 0))

        results.append({
            "factor": round(factor, 3),
            "adjustment_pct": round((factor - 1) * 100, 1),
            "expected_value": modified_ev,
            "change_from_base": round(modified_ev - base_ev, 2),
            "best_option": modified_tree.get("best_option", "N/A"),
        })

    return results


def _apply_sensitivity(node, variable_name, factor):
    """Recursively apply sensitivity factor to matching values."""
    if isinstance(node, dict):
        for key, val in node.items():
            if key == "value" and node.get("name", "").lower() == variable_name.lower():
                node[key] = round(val * factor, 2)
            elif key == "probability" and node.get("label", "").lower() == variable_name.lower():
                node[key] = min(1.0, round(val * factor, 4))
            elif isinstance(val, (dict, list)):
                _apply_sensitivity(val, variable_name, factor)
    elif isinstance(node, list):
        for item in node:
            _apply_sensitivity(item, variable_name, factor)


def flatten_paths(tree, paths=None, current_path=None):
    """Extract all terminal paths with values."""
    if paths is None:
        paths = []
    if current_path is None:
        current_path = []

    current_path = current_path + [tree.get("name", "?")]

    if tree.get("type") == "outcome" or not tree.get("children"):
        paths.append({
            "path": " > ".join(current_path),
            "value": tree.get("expected_value", tree.get("value", 0)),
        })
        return paths

    for child in tree.get("children", []):
        flatten_paths(child, paths, current_path)

    return paths


def analyze_tree(data):
    """Run full decision tree analysis."""
    tree_data = data.get("tree", data)
    decision_name = data.get("decision_name", "Decision")
    sensitivity_var = data.get("sensitivity_variable", None)

    tree = build_tree(tree_data)
    all_paths = flatten_paths(tree)
    all_paths.sort(key=lambda x: x["value"], reverse=True)

    results = {
        "timestamp": datetime.now().isoformat(),
        "decision_name": decision_name,
        "tree": tree,
        "optimal_path": all_paths[0] if all_paths else None,
        "worst_path": all_paths[-1] if all_paths else None,
        "all_paths": all_paths,
        "path_count": len(all_paths),
        "value_range": {
            "min": all_paths[-1]["value"] if all_paths else 0,
            "max": all_paths[0]["value"] if all_paths else 0,
            "spread": round(all_paths[0]["value"] - all_paths[-1]["value"], 2) if all_paths else 0,
        },
        "sensitivity": None,
        "recommendations": [],
    }

    # Best option from root
    if tree.get("best_option"):
        results["recommended_option"] = tree["best_option"]
        results["recommended_ev"] = tree["best_expected_value"]

    # Sensitivity analysis
    if sensitivity_var:
        results["sensitivity"] = {
            "variable": sensitivity_var,
            "results": sensitivity_analysis(tree_data, sensitivity_var),
        }

    # Recommendations
    recs = results["recommendations"]
    if tree.get("best_option"):
        recs.append(f"Recommended: {tree['best_option']} (EV: {tree['best_expected_value']:,.0f})")

    spread = results["value_range"]["spread"]
    if spread > 0:
        recs.append(f"Outcome range: {results['value_range']['min']:,.0f} to {results['value_range']['max']:,.0f} (spread: {spread:,.0f})")

    if results["sensitivity"]:
        sens = results["sensitivity"]["results"]
        option_changes = set(s["best_option"] for s in sens if s["best_option"] != "N/A")
        if len(option_changes) > 1:
            recs.append(f"Sensitivity: optimal option changes with {sensitivity_var} variation -- decision is sensitive to this assumption")
        else:
            recs.append(f"Sensitivity: optimal option stable across {sensitivity_var} variations -- robust decision")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        f"DECISION TREE ANALYSIS: {results['decision_name']}",
        "=" * 60,
        f"Analysis Date: {results['timestamp'][:10]}",
        f"Paths Evaluated: {results['path_count']}",
    ]

    if results.get("recommended_option"):
        lines.extend([
            "",
            f"RECOMMENDATION: {results['recommended_option']}",
            f"  Expected Value: {results['recommended_ev']:,.0f}",
        ])

    lines.extend([
        "",
        "VALUE RANGE",
        f"  Best Outcome: {results['value_range']['max']:,.0f}",
        f"  Worst Outcome: {results['value_range']['min']:,.0f}",
        f"  Spread: {results['value_range']['spread']:,.0f}",
    ])

    if results["optimal_path"]:
        lines.extend([
            "",
            f"OPTIMAL PATH: {results['optimal_path']['path']}",
            f"  Value: {results['optimal_path']['value']:,.0f}",
        ])

    lines.append("")
    lines.append("ALL PATHS (ranked by value)")
    for p in results["all_paths"][:10]:
        lines.append(f"  {p['value']:>12,.0f}  {p['path']}")

    if results["sensitivity"]:
        lines.append("")
        lines.append(f"SENSITIVITY ANALYSIS: {results['sensitivity']['variable']}")
        for s in results["sensitivity"]["results"]:
            lines.append(
                f"  {s['adjustment_pct']:>+6.1f}%: EV={s['expected_value']:>12,.0f} "
                f"(change: {s['change_from_base']:>+10,.0f}) option: {s['best_option']}"
            )

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Build decision trees with expected value analysis")
    parser.add_argument("--input", required=True, help="Path to JSON decision tree data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_tree(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
