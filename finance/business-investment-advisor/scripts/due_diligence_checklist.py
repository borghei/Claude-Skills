#!/usr/bin/env python3
"""
Due Diligence Checklist Generator

Generates comprehensive due diligence checklists for investment targets,
customized by company type, stage, and investment amount. Supports scoring
completed checklists to produce a weighted DD score.

Usage:
    python due_diligence_checklist.py --type saas --stage series-a --amount 500000
    python due_diligence_checklist.py --type ecommerce --stage seed --format json
    python due_diligence_checklist.py --type saas --stage series-b --score-file scores.json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional


# Due diligence categories with items, weights, and applicability
DD_CATEGORIES = {
    "financial": {
        "weight": 0.25,
        "label": "Financial Due Diligence",
        "items": [
            {"id": "fin_01", "item": "Historical financial statements (P&L, BS, CF) - 3 years", "priority": "high", "min_stage": "seed"},
            {"id": "fin_02", "item": "Revenue recognition policy and audit trail", "priority": "high", "min_stage": "series-a"},
            {"id": "fin_03", "item": "Unit economics validation (LTV, CAC, margins)", "priority": "high", "min_stage": "seed"},
            {"id": "fin_04", "item": "Cash flow projections and burn rate analysis", "priority": "high", "min_stage": "seed"},
            {"id": "fin_05", "item": "Cap table review and dilution modeling", "priority": "high", "min_stage": "seed"},
            {"id": "fin_06", "item": "Accounts receivable aging and collectability", "priority": "medium", "min_stage": "series-a"},
            {"id": "fin_07", "item": "Debt schedule and covenant compliance", "priority": "medium", "min_stage": "series-a"},
            {"id": "fin_08", "item": "Tax returns and compliance history", "priority": "medium", "min_stage": "series-a"},
            {"id": "fin_09", "item": "Working capital analysis", "priority": "medium", "min_stage": "series-b"},
            {"id": "fin_10", "item": "Audit opinion and management letter review", "priority": "low", "min_stage": "series-b"},
        ],
    },
    "commercial": {
        "weight": 0.20,
        "label": "Commercial Due Diligence",
        "items": [
            {"id": "com_01", "item": "Customer concentration analysis (top 10 customers)", "priority": "high", "min_stage": "seed"},
            {"id": "com_02", "item": "Customer reference calls (minimum 5)", "priority": "high", "min_stage": "series-a"},
            {"id": "com_03", "item": "Market size validation (TAM/SAM/SOM)", "priority": "high", "min_stage": "seed"},
            {"id": "com_04", "item": "Competitive landscape mapping", "priority": "high", "min_stage": "seed"},
            {"id": "com_05", "item": "Sales pipeline and conversion funnel analysis", "priority": "medium", "min_stage": "series-a"},
            {"id": "com_06", "item": "Pricing strategy and competitive positioning", "priority": "medium", "min_stage": "seed"},
            {"id": "com_07", "item": "Customer churn analysis and NPS/CSAT data", "priority": "high", "min_stage": "series-a"},
            {"id": "com_08", "item": "Channel partner and distribution analysis", "priority": "low", "min_stage": "series-b"},
            {"id": "com_09", "item": "Contract terms and renewal rate analysis", "priority": "medium", "min_stage": "series-a"},
        ],
    },
    "technical": {
        "weight": 0.15,
        "label": "Technical Due Diligence",
        "items": [
            {"id": "tech_01", "item": "Architecture review and scalability assessment", "priority": "high", "min_stage": "seed"},
            {"id": "tech_02", "item": "Code quality and technical debt assessment", "priority": "medium", "min_stage": "series-a"},
            {"id": "tech_03", "item": "Security posture and vulnerability assessment", "priority": "high", "min_stage": "series-a"},
            {"id": "tech_04", "item": "Infrastructure and DevOps maturity", "priority": "medium", "min_stage": "series-a"},
            {"id": "tech_05", "item": "Data architecture and privacy compliance", "priority": "high", "min_stage": "seed"},
            {"id": "tech_06", "item": "Third-party dependency and vendor lock-in risk", "priority": "medium", "min_stage": "series-a"},
            {"id": "tech_07", "item": "Disaster recovery and business continuity plans", "priority": "low", "min_stage": "series-b"},
            {"id": "tech_08", "item": "Product roadmap feasibility assessment", "priority": "medium", "min_stage": "seed"},
        ],
    },
    "legal": {
        "weight": 0.15,
        "label": "Legal Due Diligence",
        "items": [
            {"id": "leg_01", "item": "Corporate structure and formation documents", "priority": "high", "min_stage": "seed"},
            {"id": "leg_02", "item": "IP ownership and assignment agreements", "priority": "high", "min_stage": "seed"},
            {"id": "leg_03", "item": "Material contracts review", "priority": "high", "min_stage": "series-a"},
            {"id": "leg_04", "item": "Employment agreements and non-competes", "priority": "medium", "min_stage": "series-a"},
            {"id": "leg_05", "item": "Pending or threatened litigation", "priority": "high", "min_stage": "seed"},
            {"id": "leg_06", "item": "Regulatory compliance assessment", "priority": "medium", "min_stage": "series-a"},
            {"id": "leg_07", "item": "Option pool and equity incentive plan review", "priority": "medium", "min_stage": "seed"},
            {"id": "leg_08", "item": "Insurance coverage adequacy", "priority": "low", "min_stage": "series-b"},
        ],
    },
    "team": {
        "weight": 0.15,
        "label": "Team & Organization",
        "items": [
            {"id": "team_01", "item": "Founder/CEO background and reference checks", "priority": "high", "min_stage": "seed"},
            {"id": "team_02", "item": "Key personnel identification and retention risk", "priority": "high", "min_stage": "seed"},
            {"id": "team_03", "item": "Organizational chart and key role gaps", "priority": "medium", "min_stage": "series-a"},
            {"id": "team_04", "item": "Compensation benchmarking and equity allocation", "priority": "medium", "min_stage": "series-a"},
            {"id": "team_05", "item": "Culture assessment and employee satisfaction", "priority": "low", "min_stage": "series-b"},
            {"id": "team_06", "item": "Board composition and governance structure", "priority": "medium", "min_stage": "series-a"},
            {"id": "team_07", "item": "Hiring plan and talent pipeline assessment", "priority": "medium", "min_stage": "series-a"},
        ],
    },
    "operational": {
        "weight": 0.10,
        "label": "Operational Due Diligence",
        "items": [
            {"id": "ops_01", "item": "Key operational metrics and KPI tracking", "priority": "high", "min_stage": "seed"},
            {"id": "ops_02", "item": "Customer onboarding and support processes", "priority": "medium", "min_stage": "series-a"},
            {"id": "ops_03", "item": "Vendor and supply chain dependencies", "priority": "medium", "min_stage": "series-a"},
            {"id": "ops_04", "item": "Operational scalability assessment", "priority": "medium", "min_stage": "series-a"},
            {"id": "ops_05", "item": "Quality assurance and testing processes", "priority": "low", "min_stage": "series-b"},
        ],
    },
}

# Type-specific additional items
TYPE_EXTRAS = {
    "saas": [
        {"id": "saas_01", "category": "commercial", "item": "MRR/ARR breakdown and growth trend", "priority": "high"},
        {"id": "saas_02", "category": "commercial", "item": "Net revenue retention and expansion analysis", "priority": "high"},
        {"id": "saas_03", "category": "technical", "item": "Multi-tenancy architecture and data isolation", "priority": "medium"},
    ],
    "ecommerce": [
        {"id": "ecom_01", "category": "commercial", "item": "Inventory turnover and fulfillment metrics", "priority": "high"},
        {"id": "ecom_02", "category": "commercial", "item": "Customer repeat purchase rate and cohort analysis", "priority": "high"},
        {"id": "ecom_03", "category": "operational", "item": "Supply chain resilience and vendor diversification", "priority": "high"},
    ],
    "marketplace": [
        {"id": "mkt_01", "category": "commercial", "item": "Supply/demand balance and liquidity metrics", "priority": "high"},
        {"id": "mkt_02", "category": "commercial", "item": "Take rate and GMV growth analysis", "priority": "high"},
        {"id": "mkt_03", "category": "commercial", "item": "Disintermediation risk assessment", "priority": "medium"},
    ],
    "hardware": [
        {"id": "hw_01", "category": "operational", "item": "Manufacturing process and yield rates", "priority": "high"},
        {"id": "hw_02", "category": "legal", "item": "Patent portfolio and freedom-to-operate analysis", "priority": "high"},
        {"id": "hw_03", "category": "operational", "item": "Certification status (UL, CE, FCC, etc.)", "priority": "high"},
    ],
}

STAGE_ORDER = {"seed": 0, "series-a": 1, "series-b": 2, "growth": 3, "late": 4}


def filter_items_by_stage(items: List[Dict], stage: str) -> List[Dict]:
    """Filter DD items applicable to the investment stage."""
    stage_val = STAGE_ORDER.get(stage, 0)
    return [item for item in items if STAGE_ORDER.get(item.get("min_stage", "seed"), 0) <= stage_val]


def generate_checklist(company_type: str, stage: str, amount: float) -> Dict[str, Any]:
    """Generate a due diligence checklist."""
    checklist = {"type": company_type, "stage": stage, "amount": amount, "categories": {}}
    total_items = 0

    for cat_key, cat_data in DD_CATEGORIES.items():
        filtered = filter_items_by_stage(cat_data["items"], stage)
        items_out = []
        for item in filtered:
            items_out.append({
                "id": item["id"],
                "item": item["item"],
                "priority": item["priority"],
                "score": None,
                "notes": "",
            })
        checklist["categories"][cat_key] = {
            "label": cat_data["label"],
            "weight": cat_data["weight"],
            "items": items_out,
        }
        total_items += len(items_out)

    # Add type-specific items
    extras = TYPE_EXTRAS.get(company_type, [])
    for extra in extras:
        cat_key = extra["category"]
        if cat_key in checklist["categories"]:
            checklist["categories"][cat_key]["items"].append({
                "id": extra["id"],
                "item": extra["item"],
                "priority": extra["priority"],
                "score": None,
                "notes": "",
            })
            total_items += 1

    # Adjust depth based on investment size
    depth = "standard"
    if amount >= 1_000_000:
        depth = "comprehensive"
    elif amount < 100_000:
        depth = "lightweight"
        # Remove low-priority items for small investments
        for cat_key in checklist["categories"]:
            checklist["categories"][cat_key]["items"] = [
                i for i in checklist["categories"][cat_key]["items"]
                if i["priority"] != "low"
            ]
            total_items = sum(
                len(c["items"]) for c in checklist["categories"].values()
            )

    checklist["depth"] = depth
    checklist["total_items"] = total_items
    return checklist


def score_checklist(checklist: Dict, scores: Dict[str, float]) -> Dict[str, Any]:
    """Score a completed checklist and produce weighted DD score."""
    category_scores = {}
    total_weighted = 0.0
    total_weight = 0.0

    for cat_key, cat_data in checklist["categories"].items():
        item_scores = []
        for item in cat_data["items"]:
            score = scores.get(item["id"])
            if score is not None:
                item["score"] = score
                item_scores.append(score)

        if item_scores:
            avg = sum(item_scores) / len(item_scores)
            category_scores[cat_key] = {
                "label": cat_data["label"],
                "average_score": round(avg, 1),
                "items_scored": len(item_scores),
                "items_total": len(cat_data["items"]),
                "weight": cat_data["weight"],
            }
            total_weighted += avg * cat_data["weight"]
            total_weight += cat_data["weight"]

    composite = total_weighted / total_weight if total_weight > 0 else 0

    # Recommendation
    if composite >= 8:
        recommendation = "PROCEED - Strong due diligence results across all categories"
    elif composite >= 6:
        recommendation = "PROCEED WITH CONDITIONS - Generally positive, address flagged items"
    elif composite >= 4:
        recommendation = "CAUTION - Material concerns identified, require resolution before closing"
    else:
        recommendation = "DO NOT PROCEED - Significant red flags identified"

    return {
        "composite_score": round(composite, 1),
        "category_scores": category_scores,
        "recommendation": recommendation,
        "items_scored": sum(c["items_scored"] for c in category_scores.values()),
        "items_total": checklist["total_items"],
    }


def format_currency(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    return f"${amount:,.0f}"


def print_human(checklist: Dict, scoring: Optional[Dict] = None) -> None:
    """Print checklist in human-readable format."""
    print("=" * 72)
    print(f"  Due Diligence Checklist")
    print("=" * 72)
    print(f"\n  Type:   {checklist['type']}")
    print(f"  Stage:  {checklist['stage']}")
    print(f"  Amount: {format_currency(checklist['amount'])}")
    print(f"  Depth:  {checklist['depth']}")
    print(f"  Items:  {checklist['total_items']}")

    for cat_key, cat_data in checklist["categories"].items():
        items = cat_data["items"]
        if not items:
            continue
        print(f"\n  --- {cat_data['label']} (Weight: {cat_data['weight']*100:.0f}%) ---")
        for item in items:
            priority_marker = {"high": "[H]", "medium": "[M]", "low": "[L]"}
            marker = priority_marker.get(item["priority"], "[ ]")
            score_str = f" [{item['score']}/10]" if item.get("score") is not None else " [ /10]"
            print(f"  {marker} {item['id']}: {item['item']}{score_str}")

    if scoring:
        print(f"\n  {'=' * 68}")
        print(f"  DD SCORING RESULTS")
        print(f"  {'=' * 68}")
        print(f"\n  Composite Score: {scoring['composite_score']}/10.0")
        print(f"  Items Scored:    {scoring['items_scored']}/{scoring['items_total']}")
        print(f"\n  Category Breakdown:")
        for cat_key, cs in scoring["category_scores"].items():
            bar = "#" * int(cs["average_score"])
            print(f"    {cs['label']:<30} {cs['average_score']:>4.1f}/10  {bar}")
        print(f"\n  --> {scoring['recommendation']}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate due diligence checklist for investment targets"
    )
    parser.add_argument("--type", choices=["saas", "ecommerce", "marketplace", "hardware", "general"],
                        default="general", help="Company type (default: general)")
    parser.add_argument("--stage", choices=["seed", "series-a", "series-b", "growth", "late"],
                        default="series-a", help="Investment stage (default: series-a)")
    parser.add_argument("--amount", type=float, default=500000,
                        help="Investment amount in USD (default: 500000)")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument("--score-file", help="JSON file with item scores to compute DD score")
    args = parser.parse_args()

    checklist = generate_checklist(args.type, args.stage, args.amount)

    scoring = None
    if args.score_file:
        with open(args.score_file, "r", encoding="utf-8") as f:
            scores = json.load(f)
        scoring = score_checklist(checklist, scores)

    if args.format == "json":
        output = {"checklist": checklist}
        if scoring:
            output["scoring"] = scoring
        print(json.dumps(output, indent=2, default=str))
    else:
        print_human(checklist, scoring)


if __name__ == "__main__":
    main()
