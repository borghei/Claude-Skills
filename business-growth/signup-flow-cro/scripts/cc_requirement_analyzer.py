#!/usr/bin/env python3
"""Credit Card Requirement Analyzer - Analyze whether to require CC for trial signup.

Takes business metrics and recommends CC-required, CC-free, or "$0 charge" approach
with projected volume and revenue impact modeling.

Usage:
    python cc_requirement_analyzer.py business.json
    python cc_requirement_analyzer.py business.json --format json
"""

import argparse
import json
import sys
from typing import Any


def safe_divide(num: float, den: float, default: float = 0.0) -> float:
    """Safely divide."""
    return num / den if den != 0 else default


# Industry benchmark ranges
CC_BENCHMARKS = {
    "cc_required": {
        "signup_volume_multiplier": 1.0,
        "trial_to_paid_range": (40, 70),
        "lead_quality": "High (committed buyers)",
    },
    "cc_free": {
        "signup_volume_multiplier": 1.6,  # 40-80% more signups
        "trial_to_paid_range": (2, 15),
        "lead_quality": "Mixed (includes tire-kickers)",
    },
    "zero_charge": {
        "signup_volume_multiplier": 1.3,
        "trial_to_paid_range": (20, 40),
        "lead_quality": "Medium (somewhat committed)",
    },
}


def analyze_cc_requirement(data: dict) -> dict:
    """Analyze credit card requirement decision."""
    metrics = data.get("metrics", {})

    acv_monthly = metrics.get("acv_monthly", 0)
    current_trial_signups = metrics.get("monthly_trial_signups", 0)
    current_trial_to_paid = metrics.get("current_trial_to_paid_pct", 0)
    product_complexity = metrics.get("product_complexity", "medium")  # simple, medium, complex
    sales_motion = metrics.get("sales_motion", "product_led")  # product_led, sales_assisted
    target_audience = metrics.get("target_audience", "smb")  # smb, mid_market, enterprise
    competitors_require_cc = metrics.get("competitors_require_cc", False)
    support_cost_per_trial = metrics.get("support_cost_per_trial", 0)
    avg_ltv = metrics.get("avg_customer_ltv", acv_monthly * 24)

    # Scoring factors (positive = favor CC, negative = favor no CC)
    factors = []
    cc_score = 0  # Positive means CC-required is better

    # ACV check
    if acv_monthly >= 100:
        factors.append({"factor": f"High ACV (${acv_monthly}/mo)", "direction": "CC-required", "weight": 2, "reason": "Higher price = more committed trialists expected"})
        cc_score += 2
    else:
        factors.append({"factor": f"Low ACV (${acv_monthly}/mo)", "direction": "CC-free", "weight": 2, "reason": "Low-cost products benefit from volume; CC friction disproportionate to price"})
        cc_score -= 2

    # Complexity
    if product_complexity == "simple":
        factors.append({"factor": "Simple product", "direction": "CC-required", "weight": 1, "reason": "Quick time-to-value means users see ROI before trial ends"})
        cc_score += 1
    elif product_complexity == "complex":
        factors.append({"factor": "Complex product", "direction": "CC-free", "weight": 2, "reason": "Users need time to explore before committing; CC gate prevents exploration"})
        cc_score -= 2
    else:
        factors.append({"factor": "Medium complexity", "direction": "Neutral", "weight": 0, "reason": "Could go either way -- A/B test recommended"})

    # Sales motion
    if sales_motion == "sales_assisted":
        factors.append({"factor": "Sales-assisted motion", "direction": "CC-required", "weight": 1, "reason": "Sales team can handle lower volume with higher-quality leads"})
        cc_score += 1
    else:
        factors.append({"factor": "Product-led motion", "direction": "CC-free", "weight": 2, "reason": "PLG depends on volume and self-serve conversion"})
        cc_score -= 2

    # Audience
    if target_audience == "enterprise":
        factors.append({"factor": "Enterprise audience", "direction": "CC-required", "weight": 1, "reason": "Enterprise buyers are committed; CC friction is low relative to deal size"})
        cc_score += 1
    elif target_audience == "smb":
        factors.append({"factor": "SMB audience", "direction": "CC-free", "weight": 2, "reason": "SMBs are browsers; CC requirement loses 40-80% of potential trialists"})
        cc_score -= 2

    # Competitors
    if competitors_require_cc:
        factors.append({"factor": "Competitors require CC", "direction": "CC-required", "weight": 1, "reason": "Market norm -- not requiring CC would be a differentiator but may signal low value"})
        cc_score += 1
    else:
        factors.append({"factor": "Competitors offer CC-free trials", "direction": "CC-free", "weight": 2, "reason": "Not offering CC-free trial puts you at a competitive disadvantage"})
        cc_score -= 2

    # Support costs
    if support_cost_per_trial > acv_monthly * 0.1:
        factors.append({"factor": f"High support cost (${support_cost_per_trial}/trial)", "direction": "CC-required", "weight": 1, "reason": "CC requirement reduces trial volume and associated support burden"})
        cc_score += 1

    # Recommendation
    if cc_score >= 3:
        recommendation = "cc_required"
    elif cc_score <= -3:
        recommendation = "cc_free"
    else:
        recommendation = "zero_charge"

    # Revenue projections for each approach
    projections = {}
    for approach, benchmarks in CC_BENCHMARKS.items():
        volume_mult = benchmarks["signup_volume_multiplier"]
        low_rate, high_rate = benchmarks["trial_to_paid_range"]
        mid_rate = (low_rate + high_rate) / 2

        projected_signups = int(current_trial_signups * volume_mult)
        projected_customers_low = int(projected_signups * (low_rate / 100))
        projected_customers_mid = int(projected_signups * (mid_rate / 100))
        projected_customers_high = int(projected_signups * (high_rate / 100))

        projections[approach] = {
            "monthly_signups": projected_signups,
            "trial_to_paid_range_pct": f"{low_rate}-{high_rate}%",
            "monthly_customers_low": projected_customers_low,
            "monthly_customers_mid": projected_customers_mid,
            "monthly_customers_high": projected_customers_high,
            "monthly_revenue_mid": round(projected_customers_mid * acv_monthly, 2),
            "annual_revenue_mid": round(projected_customers_mid * acv_monthly * 12, 2),
            "lead_quality": benchmarks["lead_quality"],
        }

    # Implementation guidance
    if recommendation == "cc_required":
        implementation = [
            "Display prominently: 'You won't be charged until [trial end date]'",
            "Add: 'Cancel anytime before [date]'",
            "Send email reminder 3 days before trial ends",
            "Offer easy one-click cancellation in account settings",
        ]
    elif recommendation == "cc_free":
        implementation = [
            "Email-only signup (or SSO) with no payment information",
            "Gate upgrade prompt to after activation event (aha moment)",
            "Send value-based upgrade emails during trial",
            "Use progressive profiling to collect business info for lead scoring",
        ]
    else:
        implementation = [
            "Collect CC but display '$0.00 charge' confirmation",
            "Show clear trial end date and 'cancel anytime' messaging",
            "Send email reminder 3 days before trial ends",
            "Consider A/B testing $0 charge vs CC-free to validate",
        ]

    return {
        "recommendation": recommendation,
        "recommendation_label": recommendation.replace("_", " ").upper(),
        "confidence": "High" if abs(cc_score) >= 4 else "Medium" if abs(cc_score) >= 2 else "Low -- A/B test recommended",
        "cc_score": cc_score,
        "factors": factors,
        "projections": projections,
        "implementation": implementation,
    }


def format_text(result: dict) -> str:
    """Format analysis as human-readable text."""
    lines = []

    lines.append("=" * 60)
    lines.append("CREDIT CARD REQUIREMENT ANALYSIS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Recommendation: {result['recommendation_label']}")
    lines.append(f"Confidence: {result['confidence']}")
    lines.append("")

    lines.append("-" * 60)
    lines.append("DECISION FACTORS")
    lines.append("-" * 60)
    for f in result["factors"]:
        direction = f["direction"]
        lines.append(f"\n  {f['factor']} -> {direction}")
        lines.append(f"    {f['reason']}")

    lines.append("")
    lines.append("-" * 60)
    lines.append("REVENUE PROJECTIONS BY APPROACH")
    lines.append("-" * 60)
    for approach, proj in result["projections"].items():
        label = approach.replace("_", " ").upper()
        is_rec = " << RECOMMENDED" if approach == result["recommendation"] else ""
        lines.append(f"\n  {label}{is_rec}")
        lines.append(f"    Monthly Signups:    {proj['monthly_signups']:>8,}")
        lines.append(f"    Trial-to-Paid:      {proj['trial_to_paid_range_pct']:>8}")
        lines.append(f"    Customers/mo (mid): {proj['monthly_customers_mid']:>8,}")
        lines.append(f"    Monthly Revenue:    ${proj['monthly_revenue_mid']:>10,.2f}")
        lines.append(f"    Annual Revenue:     ${proj['annual_revenue_mid']:>10,.2f}")
        lines.append(f"    Lead Quality:       {proj['lead_quality']}")

    lines.append("")
    lines.append("-" * 40)
    lines.append("IMPLEMENTATION GUIDANCE")
    lines.append("-" * 40)
    for step in result["implementation"]:
        lines.append(f"  - {step}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze whether to require credit card for trial signup."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with business metrics",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = analyze_cc_requirement(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
