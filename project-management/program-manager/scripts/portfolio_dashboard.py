#!/usr/bin/env python3
"""Portfolio Dashboard - Generate program portfolio status dashboard.

Reads program/project data and produces a RAG-status dashboard with
milestone tracking, budget analysis, and risk summary.

Usage:
    python portfolio_dashboard.py --portfolio portfolio.json
    python portfolio_dashboard.py --portfolio portfolio.json --json
    python portfolio_dashboard.py --example
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path: str) -> dict:
    """Load portfolio data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def classify_rag(schedule_variance_days: int, budget_pct: float, risks_high: int) -> str:
    """Classify project RAG status."""
    if schedule_variance_days > 15 or budget_pct > 110 or risks_high >= 3:
        return "RED"
    elif schedule_variance_days > 5 or budget_pct > 100 or risks_high >= 1:
        return "AMBER"
    return "GREEN"


def analyze_portfolio(data: dict) -> dict:
    """Analyze portfolio and produce dashboard data."""
    portfolio_name = data.get("name", "Unknown Portfolio")
    programs = data.get("programs", [])

    program_results = []
    total_budget = 0
    total_spent = 0
    all_milestones = 0
    completed_milestones = 0
    rag_counts = {"GREEN": 0, "AMBER": 0, "RED": 0}

    for prog in programs:
        name = prog.get("name", "Unknown")
        projects = prog.get("projects", [])

        prog_budget = prog.get("budget", 0)
        prog_spent = prog.get("spent", 0)
        budget_pct = round(prog_spent / prog_budget * 100, 1) if prog_budget > 0 else 0

        schedule_var = prog.get("schedule_variance_days", 0)
        high_risks = prog.get("high_risks", 0)
        rag = classify_rag(schedule_var, budget_pct, high_risks)
        rag_counts[rag] = rag_counts.get(rag, 0) + 1

        total_budget += prog_budget
        total_spent += prog_spent

        # Project details
        project_details = []
        for proj in projects:
            p_milestones = proj.get("milestones_total", 0)
            p_completed = proj.get("milestones_completed", 0)
            all_milestones += p_milestones
            completed_milestones += p_completed

            p_pct = round(p_completed / p_milestones * 100) if p_milestones > 0 else 0
            project_details.append({
                "name": proj.get("name", "Unknown"),
                "status": proj.get("status", "In Progress"),
                "completion_pct": p_pct,
                "next_milestone": proj.get("next_milestone", "N/A"),
                "next_milestone_date": proj.get("next_milestone_date", "TBD"),
            })

        # Benefits
        benefits_target = prog.get("benefits_target", 0)
        benefits_realized = prog.get("benefits_realized", 0)
        benefits_pct = round(benefits_realized / benefits_target * 100, 1) if benefits_target > 0 else 0

        program_results.append({
            "name": name,
            "rag_status": rag,
            "schedule_variance_days": schedule_var,
            "budget": prog_budget,
            "spent": prog_spent,
            "budget_pct": budget_pct,
            "high_risks": high_risks,
            "benefits_target": benefits_target,
            "benefits_realized": benefits_realized,
            "benefits_pct": benefits_pct,
            "projects": project_details,
            "phase": prog.get("phase", "Execution"),
        })

    # Portfolio-level metrics
    portfolio_budget_pct = round(total_spent / total_budget * 100, 1) if total_budget > 0 else 0
    milestone_pct = round(completed_milestones / all_milestones * 100, 1) if all_milestones > 0 else 0

    # Overall portfolio health
    if rag_counts.get("RED", 0) > 0:
        portfolio_health = "AT RISK"
    elif rag_counts.get("AMBER", 0) > len(programs) / 2:
        portfolio_health = "CAUTION"
    else:
        portfolio_health = "ON TRACK"

    # Recommendations
    recs = []
    red_programs = [p for p in program_results if p["rag_status"] == "RED"]
    if red_programs:
        for rp in red_programs:
            recs.append(f"'{rp['name']}' is RED -- escalate to steering committee with recovery plan.")
    amber_long = [p for p in program_results if p["rag_status"] == "AMBER" and p["schedule_variance_days"] > 10]
    if amber_long:
        recs.append(f"{len(amber_long)} program(s) trending toward RED. Review scope and resource options.")
    if portfolio_budget_pct > 90:
        recs.append(f"Portfolio budget is {portfolio_budget_pct:.0f}% consumed. Review remaining scope against available budget.")

    return {
        "portfolio": portfolio_name,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "health": portfolio_health,
        "program_count": len(programs),
        "rag_distribution": rag_counts,
        "budget": {"total": total_budget, "spent": total_spent, "pct": portfolio_budget_pct},
        "milestones": {"total": all_milestones, "completed": completed_milestones, "pct": milestone_pct},
        "programs": program_results,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    """Print human-readable portfolio dashboard."""
    print(f"\nPortfolio Dashboard: {result['portfolio']}")
    print(f"Date: {result['date']}  |  Programs: {result['program_count']}")
    print("=" * 70)
    print(f"Portfolio Health: {result['health']}")

    rag = result["rag_distribution"]
    print(f"RAG: GREEN={rag.get('GREEN',0)} | AMBER={rag.get('AMBER',0)} | RED={rag.get('RED',0)}")

    b = result["budget"]
    print(f"Budget: ${b['spent']:,.0f} / ${b['total']:,.0f} ({b['pct']:.1f}%)")

    m = result["milestones"]
    print(f"Milestones: {m['completed']}/{m['total']} ({m['pct']:.1f}%)")

    for prog in result["programs"]:
        print(f"\n  [{prog['rag_status']}] {prog['name']}  (Phase: {prog['phase']})")
        print(f"       Schedule: {prog['schedule_variance_days']:+d} days  |  Budget: {prog['budget_pct']:.0f}%  |  Risks: {prog['high_risks']} high")
        print(f"       Benefits: ${prog['benefits_realized']:,.0f} / ${prog['benefits_target']:,.0f} ({prog['benefits_pct']:.0f}%)")
        for proj in prog["projects"]:
            print(f"         - {proj['name']}: {proj['status']} ({proj['completion_pct']}%)  Next: {proj['next_milestone']} ({proj['next_milestone_date']})")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    """Print example portfolio JSON."""
    example = {
        "name": "Digital Transformation Portfolio",
        "programs": [
            {
                "name": "Customer Platform Modernization",
                "phase": "Execution",
                "budget": 2000000,
                "spent": 1400000,
                "schedule_variance_days": -3,
                "high_risks": 1,
                "benefits_target": 5000000,
                "benefits_realized": 1200000,
                "projects": [
                    {"name": "API Migration", "status": "Complete", "milestones_total": 4, "milestones_completed": 4, "next_milestone": "N/A", "next_milestone_date": "Done"},
                    {"name": "Frontend Rebuild", "status": "In Progress", "milestones_total": 5, "milestones_completed": 3, "next_milestone": "Beta Release", "next_milestone_date": "2026-04-15"},
                ],
            },
            {
                "name": "Data Analytics Platform",
                "phase": "Planning",
                "budget": 800000,
                "spent": 120000,
                "schedule_variance_days": 0,
                "high_risks": 0,
                "benefits_target": 2000000,
                "benefits_realized": 0,
                "projects": [
                    {"name": "Data Lake Setup", "status": "In Progress", "milestones_total": 3, "milestones_completed": 1, "next_milestone": "Schema Design Complete", "next_milestone_date": "2026-04-01"},
                ],
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Generate program portfolio status dashboard."
    )
    parser.add_argument("--portfolio", type=str, help="Path to portfolio data JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example portfolio JSON and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.portfolio:
        parser.error("--portfolio is required (use --example to see the expected format)")

    data = load_data(args.portfolio)
    result = analyze_portfolio(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
