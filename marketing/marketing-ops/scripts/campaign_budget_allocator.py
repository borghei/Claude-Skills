#!/usr/bin/env python3
"""Campaign Budget Allocator - Allocate marketing budget across campaigns and channels.

Distributes a total budget across campaigns based on priority, historical
performance, and strategic objectives.

Usage:
    python campaign_budget_allocator.py campaigns.json --budget 100000
    python campaign_budget_allocator.py campaigns.json --budget 100000 --json
    python campaign_budget_allocator.py --demo
"""

import argparse
import json
import sys


PRIORITY_WEIGHTS = {"critical": 4, "high": 3, "medium": 2, "low": 1}
OBJECTIVE_WEIGHTS = {"revenue": 3, "pipeline": 2.5, "leads": 2, "awareness": 1.5, "retention": 1.5}


def allocate_budget(campaigns, total_budget, strategy="balanced"):
    """Allocate budget across campaigns."""
    if not campaigns:
        return {"error": "No campaigns provided"}

    # Calculate priority scores
    for camp in campaigns:
        priority = camp.get("priority", "medium")
        historical_roas = camp.get("historical_roas", 1.0)
        objective = camp.get("objective", "leads")
        strategic_importance = camp.get("strategic_importance", 5)

        # Composite score
        priority_score = PRIORITY_WEIGHTS.get(priority, 2)
        objective_score = OBJECTIVE_WEIGHTS.get(objective, 2)
        performance_score = min(5, historical_roas)  # Cap at 5

        if strategy == "performance":
            # Weight heavily toward historical performance
            camp["_score"] = performance_score * 3 + priority_score + objective_score
        elif strategy == "strategic":
            # Weight toward strategic importance
            camp["_score"] = strategic_importance * 2 + priority_score * 2 + objective_score
        else:  # balanced
            camp["_score"] = priority_score * 2 + performance_score * 1.5 + objective_score + strategic_importance * 0.5

    # Normalize scores to get allocation percentages
    total_score = sum(c["_score"] for c in campaigns)

    allocations = []
    remaining = total_budget

    for camp in sorted(campaigns, key=lambda x: x["_score"], reverse=True):
        share = camp["_score"] / max(total_score, 1)

        # Apply min/max constraints
        min_budget = camp.get("min_budget", 0)
        max_budget = camp.get("max_budget", total_budget)
        allocated = max(min_budget, min(max_budget, int(total_budget * share)))

        allocations.append({
            "campaign": camp.get("name", "Unnamed"),
            "objective": camp.get("objective", "leads"),
            "priority": camp.get("priority", "medium"),
            "historical_roas": camp.get("historical_roas"),
            "score": round(camp["_score"], 2),
            "allocated_budget": allocated,
            "budget_share": round(share * 100, 1),
        })

    # Normalize to fit exact budget
    total_allocated = sum(a["allocated_budget"] for a in allocations)
    if total_allocated > 0:
        scale = total_budget / total_allocated
        for a in allocations:
            a["allocated_budget"] = int(a["allocated_budget"] * scale)

    # Projected outcomes
    for a in allocations:
        camp_data = next((c for c in campaigns if c.get("name") == a["campaign"]), {})
        roas = camp_data.get("historical_roas", 1.0)
        cpl = camp_data.get("historical_cpl", 100)

        a["projected_revenue"] = round(a["allocated_budget"] * roas, 2)
        a["projected_leads"] = int(a["allocated_budget"] / max(cpl, 1))

    total_projected_revenue = sum(a["projected_revenue"] for a in allocations)
    total_projected_leads = sum(a["projected_leads"] for a in allocations)

    return {
        "strategy": strategy,
        "total_budget": total_budget,
        "total_allocated": sum(a["allocated_budget"] for a in allocations),
        "projected_revenue": round(total_projected_revenue, 2),
        "projected_roas": round(total_projected_revenue / max(total_budget, 1), 2),
        "projected_leads": total_projected_leads,
        "projected_cpl": round(total_budget / max(total_projected_leads, 1), 2),
        "allocations": allocations,
    }


def get_demo_data():
    return {
        "campaigns": [
            {"name": "Paid Search - Brand", "priority": "critical", "objective": "revenue", "historical_roas": 4.2, "historical_cpl": 45, "strategic_importance": 8},
            {"name": "LinkedIn ABM Campaign", "priority": "high", "objective": "pipeline", "historical_roas": 2.8, "historical_cpl": 120, "strategic_importance": 9},
            {"name": "Content Marketing", "priority": "high", "objective": "leads", "historical_roas": 3.5, "historical_cpl": 35, "strategic_importance": 7},
            {"name": "Email Nurture", "priority": "medium", "objective": "revenue", "historical_roas": 8.5, "historical_cpl": 12, "strategic_importance": 6},
            {"name": "Display Retargeting", "priority": "medium", "objective": "leads", "historical_roas": 1.8, "historical_cpl": 85, "strategic_importance": 4},
            {"name": "Brand Awareness", "priority": "low", "objective": "awareness", "historical_roas": 0.5, "historical_cpl": 200, "strategic_importance": 5},
        ],
        "budget": 100000,
    }


def format_report(analysis):
    """Format human-readable allocation report."""
    lines = []
    lines.append("=" * 75)
    lines.append(f"BUDGET ALLOCATION ({analysis['strategy'].upper()} STRATEGY)")
    lines.append("=" * 75)
    lines.append(f"Total Budget:       ${analysis['total_budget']:,.0f}")
    lines.append(f"Projected Revenue:  ${analysis['projected_revenue']:,.0f}")
    lines.append(f"Projected ROAS:     {analysis['projected_roas']:.1f}x")
    lines.append(f"Projected Leads:    {analysis['projected_leads']:,}")
    lines.append(f"Projected CPL:      ${analysis['projected_cpl']:.0f}")
    lines.append("")

    lines.append("--- ALLOCATIONS ---")
    lines.append(f"{'Campaign':<25} {'Budget':>10} {'Share':>6} {'ROAS':>6} {'Proj Rev':>12} {'Leads':>7}")
    lines.append("-" * 70)

    for a in sorted(analysis["allocations"], key=lambda x: x["allocated_budget"], reverse=True):
        roas = a.get("historical_roas", "N/A")
        roas_str = f"{roas:.1f}x" if isinstance(roas, (int, float)) else roas
        lines.append(
            f"{a['campaign']:<25} ${a['allocated_budget']:>9,} {a['budget_share']:>5.0f}% "
            f"{roas_str:>6} ${a['projected_revenue']:>11,.0f} {a['projected_leads']:>7,}"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Allocate marketing budget across campaigns")
    parser.add_argument("input", nargs="?", help="JSON file with campaign data")
    parser.add_argument("--budget", type=float, help="Total budget to allocate")
    parser.add_argument("--strategy", choices=["balanced", "performance", "strategic"], default="balanced")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
        campaigns = data["campaigns"]
        budget = data["budget"]
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            campaigns = data if isinstance(data, list) else data.get("campaigns", [])
            budget = args.budget or data.get("budget", 100000)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    if args.budget:
        budget = args.budget

    analysis = allocate_budget(campaigns, budget, args.strategy)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
