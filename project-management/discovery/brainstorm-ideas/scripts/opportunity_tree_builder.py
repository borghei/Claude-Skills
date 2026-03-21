#!/usr/bin/env python3
"""Opportunity Tree Builder - Generate Opportunity Solution Trees from structured data.

Reads outcome, opportunity, and solution data and produces a structured
tree visualization with coverage analysis.

Usage:
    python opportunity_tree_builder.py --tree tree.json
    python opportunity_tree_builder.py --tree tree.json --json
    python opportunity_tree_builder.py --example
"""

import argparse
import json
import sys


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def build_tree(data: dict) -> dict:
    outcome = data.get("outcome", "Undefined Outcome")
    opportunities = data.get("opportunities", [])

    tree_nodes = []
    total_solutions = 0
    opportunities_without_evidence = []
    opportunities_without_solutions = []

    for opp in opportunities:
        opp_name = opp.get("name", "Unknown")
        evidence = opp.get("evidence", [])
        solutions = opp.get("solutions", [])

        if not evidence:
            opportunities_without_evidence.append(opp_name)
        if not solutions:
            opportunities_without_solutions.append(opp_name)

        solution_nodes = []
        for sol in solutions:
            sol_name = sol.get("name", "Unknown")
            effort = sol.get("effort", "M")
            confidence = sol.get("confidence", "Medium")
            status = sol.get("status", "Proposed")
            total_solutions += 1

            solution_nodes.append({
                "name": sol_name,
                "effort": effort,
                "confidence": confidence,
                "status": status,
            })

        tree_nodes.append({
            "opportunity": opp_name,
            "evidence_count": len(evidence),
            "evidence_sources": evidence[:3],
            "solution_count": len(solutions),
            "solutions": solution_nodes,
        })

    # Analysis
    avg_solutions_per_opp = round(total_solutions / len(opportunities), 1) if opportunities else 0

    recs = []
    if opportunities_without_evidence:
        recs.append(f"{len(opportunities_without_evidence)} opportunity(ies) without evidence. Conduct user interviews to validate: {', '.join(opportunities_without_evidence[:3])}")
    if opportunities_without_solutions:
        recs.append(f"{len(opportunities_without_solutions)} opportunity(ies) without solutions. Run ideation sessions for: {', '.join(opportunities_without_solutions[:3])}")
    if avg_solutions_per_opp < 2:
        recs.append("Average solutions per opportunity is low. Aim for 3+ solutions per opportunity to enable comparison.")
    single_solution_opps = [n["opportunity"] for n in tree_nodes if n["solution_count"] == 1]
    if single_solution_opps:
        recs.append(f"Opportunities with only 1 solution (risky -- add alternatives): {', '.join(single_solution_opps[:3])}")

    return {
        "outcome": outcome,
        "total_opportunities": len(opportunities),
        "total_solutions": total_solutions,
        "avg_solutions_per_opportunity": avg_solutions_per_opp,
        "tree": tree_nodes,
        "gaps": {
            "without_evidence": opportunities_without_evidence,
            "without_solutions": opportunities_without_solutions,
        },
        "recommendations": recs,
    }


def print_tree(result: dict) -> None:
    print(f"\nOpportunity Solution Tree")
    print("=" * 60)
    print(f"Outcome: {result['outcome']}")
    print(f"Opportunities: {result['total_opportunities']}  |  Solutions: {result['total_solutions']}  |  Avg: {result['avg_solutions_per_opportunity']:.1f}/opp")

    for node in result["tree"]:
        evidence_str = f" ({node['evidence_count']} evidence)" if node["evidence_count"] > 0 else " (NO EVIDENCE)"
        print(f"\n  +-- {node['opportunity']}{evidence_str}")
        for sol in node["solutions"]:
            status_icon = {"Proposed": "?", "Testing": "~", "Validated": "+", "Rejected": "x"}.get(sol["status"], "?")
            print(f"      [{status_icon}] {sol['name']}  (Effort: {sol['effort']}, Confidence: {sol['confidence']})")
        if not node["solutions"]:
            print(f"      (no solutions yet)")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    example = {
        "outcome": "Reduce time-to-value from 14 days to 3 days",
        "opportunities": [
            {
                "name": "Users don't know what to do after signup",
                "evidence": ["Interview #3: 'I signed up but had no idea what to do next'", "Analytics: 60% drop-off before first action"],
                "solutions": [
                    {"name": "Guided onboarding wizard", "effort": "M", "confidence": "High", "status": "Testing"},
                    {"name": "Contextual tooltips", "effort": "S", "confidence": "Medium", "status": "Proposed"},
                    {"name": "Welcome video series", "effort": "S", "confidence": "Low", "status": "Proposed"},
                ],
            },
            {
                "name": "Initial configuration is too complex",
                "evidence": ["Support tickets: 40% about setup", "Interview #7: 'Too many settings before I can do anything'"],
                "solutions": [
                    {"name": "Smart defaults based on industry", "effort": "L", "confidence": "Medium", "status": "Proposed"},
                    {"name": "Setup template library", "effort": "M", "confidence": "High", "status": "Proposed"},
                ],
            },
            {
                "name": "Value not visible until data accumulates",
                "evidence": [],
                "solutions": [],
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Build Opportunity Solution Trees.")
    parser.add_argument("--tree", type=str, help="Path to tree data JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.tree:
        parser.error("--tree is required")

    data = load_data(args.tree)
    result = build_tree(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_tree(result)


if __name__ == "__main__":
    main()
