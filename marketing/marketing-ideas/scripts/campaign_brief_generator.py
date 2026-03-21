#!/usr/bin/env python3
"""Campaign Brief Generator - Generate structured campaign briefs from parameters.

Creates a complete campaign brief document with objectives, audience,
channels, timeline, budget, and success metrics.

Usage:
    python campaign_brief_generator.py config.json
    python campaign_brief_generator.py config.json --json
    python campaign_brief_generator.py --demo
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


def generate_brief(config):
    """Generate a structured campaign brief."""
    name = config.get("name", "Untitled Campaign")
    objective = config.get("objective", "Generate leads")
    audience = config.get("audience", "Target audience TBD")
    budget = config.get("budget", 0)
    duration_weeks = config.get("duration_weeks", 4)
    channels = config.get("channels", [])
    kpis = config.get("kpis", [])
    start_date = config.get("start_date", datetime.now().strftime("%Y-%m-%d"))

    # Calculate dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = start + timedelta(weeks=duration_weeks)

    # Budget allocation by channel
    channel_budgets = []
    if channels and budget > 0:
        channel_weights = {
            "paid_search": 0.30, "social_paid": 0.25, "email": 0.10,
            "content": 0.15, "display": 0.10, "events": 0.10,
            "retargeting": 0.15, "influencer": 0.20, "podcast": 0.10,
        }
        total_weight = sum(channel_weights.get(ch, 0.1) for ch in channels)
        for ch in channels:
            weight = channel_weights.get(ch, 0.1) / total_weight
            channel_budgets.append({
                "channel": ch,
                "budget": round(budget * weight, 2),
                "percentage": round(weight * 100, 1),
            })

    # Timeline phases
    phases = []
    if duration_weeks >= 4:
        phases = [
            {"phase": "Planning & Setup", "week_start": 1, "week_end": 1,
             "tasks": ["Finalize creative assets", "Set up tracking", "Configure campaigns"]},
            {"phase": "Launch", "week_start": 2, "week_end": 2,
             "tasks": ["Launch campaigns", "Monitor performance", "Optimize targeting"]},
            {"phase": "Optimization", "week_start": 3, "week_end": max(3, duration_weeks - 1),
             "tasks": ["A/B test creatives", "Adjust budgets", "Refine audiences"]},
            {"phase": "Wrap-Up", "week_start": duration_weeks, "week_end": duration_weeks,
             "tasks": ["Generate final report", "Document learnings", "Plan next campaign"]},
        ]
    else:
        phases = [
            {"phase": "Setup & Launch", "week_start": 1, "week_end": 1,
             "tasks": ["Launch campaigns", "Monitor closely"]},
            {"phase": "Run & Optimize", "week_start": 2, "week_end": duration_weeks,
             "tasks": ["Optimize", "Report results"]},
        ]

    # Default KPIs by objective
    if not kpis:
        kpi_map = {
            "leads": ["Total leads", "Cost per lead", "Lead quality score", "Conversion rate"],
            "awareness": ["Impressions", "Reach", "Brand mentions", "Share of voice"],
            "revenue": ["Revenue generated", "ROAS", "Pipeline value", "Deal size"],
            "retention": ["Churn rate change", "Re-engagement rate", "NPS change", "Active users"],
            "traffic": ["Page visits", "Unique visitors", "Bounce rate", "Time on site"],
        }
        kpis = kpi_map.get(config.get("objective_type", "leads"), ["Leads", "Cost per lead", "Conversion rate"])

    brief = {
        "campaign_name": name,
        "objective": objective,
        "objective_type": config.get("objective_type", "leads"),
        "audience": {
            "description": audience,
            "segments": config.get("segments", []),
        },
        "budget": {
            "total": budget,
            "currency": config.get("currency", "USD"),
            "allocation": channel_budgets,
        },
        "timeline": {
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "duration_weeks": duration_weeks,
            "phases": phases,
        },
        "channels": channels,
        "kpis": kpis,
        "creative_requirements": config.get("creative_requirements", [
            "Landing page",
            "Email copy (3 variants)",
            "Ad copy (5 variants)",
            "Social posts (per platform)",
        ]),
        "risks": config.get("risks", [
            "Budget may not be sufficient for desired reach",
            "Creative approval delays could push launch",
            "Seasonal factors may affect performance",
        ]),
    }

    return brief


def get_demo_data():
    return {
        "name": "Q2 Product Launch Campaign",
        "objective": "Generate 500 qualified leads for new product launch",
        "objective_type": "leads",
        "audience": "Mid-market SaaS product managers in US/UK",
        "budget": 25000,
        "currency": "USD",
        "duration_weeks": 6,
        "channels": ["paid_search", "social_paid", "email", "content", "retargeting"],
        "start_date": "2026-04-01",
        "segments": ["Product managers", "Engineering leaders", "CTOs"],
    }


def format_brief(brief):
    """Format human-readable campaign brief."""
    lines = []
    lines.append("=" * 65)
    lines.append(f"CAMPAIGN BRIEF: {brief['campaign_name']}")
    lines.append("=" * 65)

    lines.append(f"\nObjective: {brief['objective']}")
    lines.append(f"Audience:  {brief['audience']['description']}")
    if brief["audience"]["segments"]:
        lines.append(f"Segments:  {', '.join(brief['audience']['segments'])}")
    lines.append(f"Budget:    ${brief['budget']['total']:,.0f} {brief['budget']['currency']}")
    lines.append(f"Timeline:  {brief['timeline']['start_date']} to {brief['timeline']['end_date']} ({brief['timeline']['duration_weeks']} weeks)")
    lines.append(f"Channels:  {', '.join(brief['channels'])}")
    lines.append("")

    # Budget allocation
    if brief["budget"]["allocation"]:
        lines.append("--- BUDGET ALLOCATION ---")
        for alloc in brief["budget"]["allocation"]:
            lines.append(f"  {alloc['channel']:<20} ${alloc['budget']:>10,.0f} ({alloc['percentage']:.0f}%)")
        lines.append("")

    # Timeline
    lines.append("--- TIMELINE ---")
    for phase in brief["timeline"]["phases"]:
        lines.append(f"  Week {phase['week_start']}-{phase['week_end']}: {phase['phase']}")
        for task in phase["tasks"]:
            lines.append(f"    - {task}")
    lines.append("")

    # KPIs
    lines.append("--- SUCCESS METRICS ---")
    for kpi in brief["kpis"]:
        lines.append(f"  - {kpi}")
    lines.append("")

    # Creative requirements
    lines.append("--- CREATIVE REQUIREMENTS ---")
    for req in brief["creative_requirements"]:
        lines.append(f"  [ ] {req}")
    lines.append("")

    # Risks
    lines.append("--- RISKS ---")
    for risk in brief["risks"]:
        lines.append(f"  ! {risk}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate structured campaign briefs")
    parser.add_argument("input", nargs="?", help="JSON config file")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Generate demo brief")
    args = parser.parse_args()

    if args.demo:
        config = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    brief = generate_brief(config)

    if args.json_output:
        print(json.dumps(brief, indent=2))
    else:
        print(format_brief(brief))


if __name__ == "__main__":
    main()
