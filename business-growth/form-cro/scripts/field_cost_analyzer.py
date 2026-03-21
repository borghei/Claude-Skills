#!/usr/bin/env python3
"""
Field Cost Analyzer

Calculate the estimated abandonment cost of each form field and recommend
fields to remove, keep, or enrich post-submission. Includes dollar impact
estimation based on traffic and lead value.

Usage:
    python field_cost_analyzer.py form_fields.json
    python field_cost_analyzer.py form_fields.json --monthly-visitors 5000 --current-rate 30 --value-per-lead 100
    python field_cost_analyzer.py form_fields.json --json
"""

import argparse
import json
import sys


FIELD_COSTS = {
    "email": {"drop_pct": 1, "enrichable": False, "category": "essential"},
    "first_name": {"drop_pct": 3, "enrichable": False, "category": "standard"},
    "last_name": {"drop_pct": 3, "enrichable": False, "category": "standard"},
    "full_name": {"drop_pct": 2, "enrichable": False, "category": "standard"},
    "phone": {"drop_pct": 8, "enrichable": False, "category": "high_friction"},
    "company": {"drop_pct": 4, "enrichable": True, "category": "enrichable"},
    "company_size": {"drop_pct": 4, "enrichable": True, "category": "enrichable"},
    "job_title": {"drop_pct": 4, "enrichable": True, "category": "enrichable"},
    "industry": {"drop_pct": 3, "enrichable": True, "category": "enrichable"},
    "message": {"drop_pct": 6, "enrichable": False, "category": "high_friction"},
    "textarea": {"drop_pct": 6, "enrichable": False, "category": "high_friction"},
    "budget": {"drop_pct": 10, "enrichable": False, "category": "high_friction"},
    "website": {"drop_pct": 3, "enrichable": True, "category": "enrichable"},
    "country": {"drop_pct": 2, "enrichable": True, "category": "enrichable"},
    "dropdown": {"drop_pct": 3, "enrichable": False, "category": "standard"},
    "checkbox": {"drop_pct": 1, "enrichable": False, "category": "low_friction"},
    "radio": {"drop_pct": 2, "enrichable": False, "category": "low_friction"},
    "custom": {"drop_pct": 4, "enrichable": False, "category": "standard"},
}


def analyze_fields(data: dict, monthly_visitors: int, current_rate: float,
                   value_per_lead: float) -> dict:
    """Analyze form fields for abandonment cost."""
    fields = data.get("fields", [])
    if not fields:
        return {"error": "No field data provided."}

    current_leads = monthly_visitors * (current_rate / 100.0)
    current_monthly_value = current_leads * value_per_lead

    field_results = []
    cumulative_drop = 0

    for f in fields:
        ftype = f.get("type", "custom").lower()
        label = f.get("label", ftype)
        required = f.get("required", True)

        cost_data = FIELD_COSTS.get(ftype, FIELD_COSTS["custom"])
        drop_pct = cost_data["drop_pct"]
        enrichable = cost_data["enrichable"]
        category = cost_data["category"]

        if not required:
            drop_pct = max(1, drop_pct // 2)

        cumulative_drop += drop_pct

        # Dollar impact of this field
        leads_lost = monthly_visitors * (drop_pct / 100.0)
        dollar_impact = leads_lost * value_per_lead

        if enrichable and required:
            action = "REMOVE -- enrichable post-submission"
        elif drop_pct >= 8:
            action = "REMOVE unless business-critical"
        elif drop_pct >= 5:
            action = "REVIEW -- high cost, justify or remove"
        else:
            action = "KEEP"

        field_results.append({
            "field": label,
            "type": ftype,
            "required": required,
            "category": category,
            "estimated_drop_pct": drop_pct,
            "enrichable": enrichable,
            "monthly_leads_lost": round(leads_lost, 1),
            "monthly_dollar_impact": round(dollar_impact, 2),
            "action": action,
        })

    # Calculate optimized scenario (remove enrichable + high friction optional)
    removable_drop = sum(f["estimated_drop_pct"] for f in field_results
                         if f["action"].startswith("REMOVE"))
    optimized_rate = min(95, current_rate + removable_drop * 0.7)  # 70% recovery factor
    optimized_leads = monthly_visitors * (optimized_rate / 100.0)
    optimized_value = optimized_leads * value_per_lead

    return {
        "summary": {
            "total_fields": len(fields),
            "required_fields": sum(1 for f in field_results if f["required"]),
            "enrichable_fields": sum(1 for f in field_results if f["enrichable"]),
            "estimated_cumulative_drop_pct": min(80, cumulative_drop),
        },
        "current_performance": {
            "monthly_visitors": monthly_visitors,
            "current_rate_pct": current_rate,
            "current_monthly_leads": round(current_leads, 1),
            "current_monthly_value": round(current_monthly_value, 2),
        },
        "optimized_projection": {
            "removable_drop_pct": removable_drop,
            "projected_rate_pct": round(optimized_rate, 1),
            "projected_monthly_leads": round(optimized_leads, 1),
            "projected_monthly_value": round(optimized_value, 2),
            "monthly_value_gain": round(optimized_value - current_monthly_value, 2),
            "annual_value_gain": round((optimized_value - current_monthly_value) * 12, 2),
        },
        "field_analysis": field_results,
        "recommendations": _generate_recommendations(field_results),
    }


def _generate_recommendations(fields: list) -> list:
    """Generate recommendations."""
    recs = []
    removable = [f for f in fields if f["action"].startswith("REMOVE")]
    if removable:
        names = ", ".join(f["field"] for f in removable[:3])
        total_drop = sum(f["estimated_drop_pct"] for f in removable)
        recs.append({
            "priority": "HIGH",
            "recommendation": f"Remove {len(removable)} field(s): {names}. Estimated {total_drop}% drop reduction.",
        })

    high_cost = [f for f in fields if f["estimated_drop_pct"] >= 8 and not f["action"].startswith("REMOVE")]
    if high_cost:
        for f in high_cost:
            recs.append({
                "priority": "MEDIUM",
                "recommendation": f"'{f['field']}' has {f['estimated_drop_pct']}% drop cost. Keep only if directly used within 24 hours of submission.",
            })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("FIELD COST ANALYZER")
    lines.append("=" * 70)

    s = result["summary"]
    lines.append(f"\nTotal Fields: {s['total_fields']} ({s['required_fields']} required, {s['enrichable_fields']} enrichable)")
    lines.append(f"Cumulative Abandonment Estimate: {s['estimated_cumulative_drop_pct']}%")

    cp = result["current_performance"]
    lines.append(f"\n--- Current Performance ---")
    lines.append(f"Monthly Visitors: {cp['monthly_visitors']:,}")
    lines.append(f"Current Rate: {cp['current_rate_pct']}%")
    lines.append(f"Monthly Leads: {cp['current_monthly_leads']:,.0f}")
    lines.append(f"Monthly Value: ${cp['current_monthly_value']:,.2f}")

    op = result["optimized_projection"]
    lines.append(f"\n--- After Removing Low-Value Fields ---")
    lines.append(f"Projected Rate: {op['projected_rate_pct']}%")
    lines.append(f"Projected Leads: {op['projected_monthly_leads']:,.0f}")
    lines.append(f"Monthly Value Gain: ${op['monthly_value_gain']:,.2f}")
    lines.append(f"Annual Value Gain: ${op['annual_value_gain']:,.2f}")

    lines.append(f"\n--- Field-by-Field Analysis ---")
    lines.append(f"{'Field':<18} {'Type':<12} {'Drop%':>6} {'$/mo Lost':>10} {'Action'}")
    for f in result["field_analysis"]:
        lines.append(
            f"{f['field']:<18} {f['type']:<12} {f['estimated_drop_pct']:>5d}% "
            f"${f['monthly_dollar_impact']:>8,.0f} {f['action']}"
        )

    if result["recommendations"]:
        lines.append(f"\n--- Recommendations ---")
        for r in result["recommendations"]:
            lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate abandonment cost of each form field."
    )
    parser.add_argument("input_file", help="JSON file with form fields")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--monthly-visitors", type=int, default=1000,
                        help="Monthly form visitors (default: 1000)")
    parser.add_argument("--current-rate", type=float, default=25,
                        help="Current completion rate %% (default: 25)")
    parser.add_argument("--value-per-lead", type=float, default=50,
                        help="Dollar value per lead (default: 50)")

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    result = analyze_fields(data, args.monthly_visitors, args.current_rate,
                            args.value_per_lead)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
