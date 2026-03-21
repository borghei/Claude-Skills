#!/usr/bin/env python3
"""GTM Planner - Generate go-to-market plans with channel strategy and timeline.

Creates a structured GTM plan from product, audience, and market inputs.

Usage:
    python gtm_planner.py config.json
    python gtm_planner.py config.json --json
    python gtm_planner.py --demo
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


MOTION_TEMPLATES = {
    "product_led": {
        "channels": ["free_tier", "content_seo", "community", "product_virality", "partnerships"],
        "sales_model": "self-serve with sales assist",
        "typical_cac": "$50-200",
        "time_to_revenue": "1-3 months",
    },
    "sales_led": {
        "channels": ["outbound_sales", "account_based", "events", "partnerships", "paid_ads"],
        "sales_model": "enterprise sales",
        "typical_cac": "$5,000-50,000",
        "time_to_revenue": "3-12 months",
    },
    "marketing_led": {
        "channels": ["content_seo", "paid_ads", "email_nurture", "webinars", "social"],
        "sales_model": "inbound with SDR qualification",
        "typical_cac": "$200-2,000",
        "time_to_revenue": "1-6 months",
    },
    "community_led": {
        "channels": ["community", "content_seo", "events", "open_source", "developer_relations"],
        "sales_model": "community-assisted sales",
        "typical_cac": "$100-500",
        "time_to_revenue": "3-9 months",
    },
}


def determine_motion(config):
    """Determine the best GTM motion based on inputs."""
    acv = config.get("average_contract_value", 0)
    product_complexity = config.get("product_complexity", "medium")
    buyer_type = config.get("buyer_type", "technical")
    has_free_tier = config.get("has_free_tier", False)

    if has_free_tier and acv < 5000:
        return "product_led"
    elif acv > 25000 or product_complexity == "high":
        return "sales_led"
    elif buyer_type == "technical" and config.get("has_community", False):
        return "community_led"
    return "marketing_led"


def generate_gtm_plan(config):
    """Generate a comprehensive GTM plan."""
    product = config.get("product", "Product")
    market = config.get("market", "Target market")
    acv = config.get("average_contract_value", 1000)
    target_arr = config.get("target_arr", 1000000)
    launch_date = config.get("launch_date", datetime.now().strftime("%Y-%m-%d"))

    # Determine motion
    motion = config.get("motion") or determine_motion(config)
    motion_template = MOTION_TEMPLATES.get(motion, MOTION_TEMPLATES["marketing_led"])

    # Calculate targets
    deals_needed = int(target_arr / max(acv, 1))
    pipeline_needed = deals_needed * 4  # 25% win rate assumption
    mqls_needed = pipeline_needed * 3  # 33% SQL conversion
    budget_estimate = mqls_needed * 100  # $100 avg CAC for MQLs

    # Channel strategy
    channels = []
    for ch in motion_template["channels"]:
        channels.append({
            "channel": ch,
            "role": _channel_role(ch),
            "priority": "primary" if ch in motion_template["channels"][:3] else "secondary",
            "budget_share": _channel_budget_share(ch, motion),
        })

    # Timeline (12-month)
    start = datetime.strptime(launch_date, "%Y-%m-%d")
    timeline = [
        {"phase": "Foundation", "months": "1-2", "start": start.strftime("%Y-%m-%d"),
         "activities": ["Finalize positioning", "Build sales assets", "Set up analytics", "Create content foundation"]},
        {"phase": "Launch", "months": "3-4", "start": (start + timedelta(days=60)).strftime("%Y-%m-%d"),
         "activities": ["Execute launch campaign", "Activate all channels", "Begin outbound", "Monitor and adjust"]},
        {"phase": "Scale", "months": "5-8", "start": (start + timedelta(days=120)).strftime("%Y-%m-%d"),
         "activities": ["Double down on working channels", "Kill underperformers", "Expand content", "Build partnerships"]},
        {"phase": "Optimize", "months": "9-12", "start": (start + timedelta(days=240)).strftime("%Y-%m-%d"),
         "activities": ["Full attribution analysis", "Budget reallocation", "Advanced segmentation", "Prepare for next year"]},
    ]

    # Competitive positioning
    positioning = {
        "framework": "April Dunford methodology",
        "steps": [
            "List competitive alternatives (direct, adjacent, status quo)",
            "Isolate unique attributes (features only we have)",
            "Map attributes to customer value",
            "Define best-fit customers",
            "Choose market category",
        ],
    }

    return {
        "product": product,
        "market": market,
        "motion": motion,
        "motion_details": motion_template,
        "targets": {
            "target_arr": target_arr,
            "average_contract_value": acv,
            "deals_needed": deals_needed,
            "pipeline_needed": pipeline_needed,
            "mqls_needed": mqls_needed,
            "estimated_budget": budget_estimate,
        },
        "channels": channels,
        "timeline": timeline,
        "positioning": positioning,
        "success_metrics": {
            "monthly": ["MQLs generated", "Pipeline created", "Win rate", "CAC"],
            "quarterly": ["Revenue vs target", "Channel ROI", "Market share", "Brand awareness"],
        },
        "risks": [
            "Product-market fit not validated with enough customers",
            "CAC may be higher than modeled in early months",
            "Competitive response to market entry",
            "Channel saturation in target market",
        ],
    }


def _channel_role(channel):
    roles = {
        "content_seo": "Demand generation and thought leadership",
        "paid_ads": "Targeted lead generation",
        "email_nurture": "Lead nurturing and conversion",
        "outbound_sales": "Direct pipeline creation",
        "social": "Brand awareness and engagement",
        "events": "Relationship building and pipeline",
        "partnerships": "Channel expansion and credibility",
        "community": "User engagement and advocacy",
        "free_tier": "Top-of-funnel acquisition",
        "product_virality": "Organic user-to-user growth",
        "account_based": "Strategic account targeting",
        "webinars": "Education and lead qualification",
        "open_source": "Developer adoption and community",
        "developer_relations": "Technical community building",
    }
    return roles.get(channel, "Marketing channel")


def _channel_budget_share(channel, motion):
    shares = {
        "product_led": {"free_tier": 0, "content_seo": 30, "community": 15, "product_virality": 5, "partnerships": 20, "paid_ads": 30},
        "sales_led": {"outbound_sales": 35, "account_based": 25, "events": 20, "partnerships": 10, "paid_ads": 10},
        "marketing_led": {"content_seo": 25, "paid_ads": 30, "email_nurture": 10, "webinars": 15, "social": 20},
        "community_led": {"community": 25, "content_seo": 25, "events": 20, "open_source": 15, "developer_relations": 15},
    }
    return shares.get(motion, {}).get(channel, 10)


def get_demo_data():
    return {
        "product": "DataFlow Analytics",
        "market": "Mid-market SaaS product teams",
        "average_contract_value": 12000,
        "target_arr": 2000000,
        "has_free_tier": True,
        "product_complexity": "medium",
        "buyer_type": "technical",
        "has_community": False,
        "launch_date": "2026-04-01",
    }


def format_report(plan):
    """Format human-readable GTM plan."""
    lines = []
    lines.append("=" * 65)
    lines.append(f"GO-TO-MARKET PLAN: {plan['product']}")
    lines.append("=" * 65)
    lines.append(f"Market:     {plan['market']}")
    lines.append(f"Motion:     {plan['motion'].replace('_', '-').title()}")
    lines.append(f"Sales Model: {plan['motion_details']['sales_model']}")
    lines.append("")

    t = plan["targets"]
    lines.append("--- TARGETS ---")
    lines.append(f"  Target ARR:     ${t['target_arr']:,.0f}")
    lines.append(f"  ACV:            ${t['average_contract_value']:,.0f}")
    lines.append(f"  Deals needed:   {t['deals_needed']:,}")
    lines.append(f"  Pipeline needed: {t['pipeline_needed']:,}")
    lines.append(f"  MQLs needed:    {t['mqls_needed']:,}")
    lines.append(f"  Est. budget:    ${t['estimated_budget']:,.0f}")
    lines.append("")

    lines.append("--- CHANNEL STRATEGY ---")
    for ch in plan["channels"]:
        lines.append(f"  [{ch['priority'].upper()[:3]}] {ch['channel']:<25} {ch['budget_share']:>3}% - {ch['role']}")
    lines.append("")

    lines.append("--- TIMELINE ---")
    for phase in plan["timeline"]:
        lines.append(f"  Months {phase['months']}: {phase['phase']} ({phase['start']})")
        for act in phase["activities"]:
            lines.append(f"    - {act}")
    lines.append("")

    lines.append("--- RISKS ---")
    for risk in plan["risks"]:
        lines.append(f"  ! {risk}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate go-to-market plans")
    parser.add_argument("input", nargs="?", help="JSON config file")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Generate demo plan")
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

    plan = generate_gtm_plan(config)

    if args.json_output:
        print(json.dumps(plan, indent=2))
    else:
        print(format_report(plan))


if __name__ == "__main__":
    main()
