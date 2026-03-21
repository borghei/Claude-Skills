#!/usr/bin/env python3
"""Pricing Model Analyzer - Evaluate SaaS pricing model against best practices.

Analyzes value metric alignment, tier architecture, feature allocation, pricing
signals, and anti-patterns. Outputs a health scorecard with prioritized recommendations.

Usage:
    python pricing_model_analyzer.py pricing.json
    python pricing_model_analyzer.py pricing.json --format json
"""

import argparse
import json
import sys
from typing import Any


VALID_VALUE_METRICS = [
    "per_seat", "per_usage", "per_feature", "flat_fee", "per_outcome", "hybrid",
]

ENTERPRISE_FEATURES = [
    "sso", "scim", "audit_logs", "sla", "dedicated_support",
    "custom_integrations", "api_access", "advanced_security",
]

TIER_COUNT_GUIDANCE = {
    1: {"rating": "Poor", "issue": "Single tier provides no upsell path or anchoring"},
    2: {"rating": "Fair", "issue": "Two tiers lack the anchoring effect of Good-Better-Best"},
    3: {"rating": "Excellent", "issue": None},
    4: {"rating": "Good", "issue": "Four tiers acceptable but verify differentiation is clear"},
}


def safe_divide(num: float, den: float, default: float = 0.0) -> float:
    """Safely divide."""
    return num / den if den != 0 else default


def analyze_value_metric(data: dict) -> dict:
    """Analyze value metric selection."""
    metric = data.get("value_metric", "")
    issues = []
    score = 0

    if not metric:
        return {"score": 0, "issues": ["No value metric defined"], "metric": "unknown"}

    if metric not in VALID_VALUE_METRICS:
        issues.append(f"Unknown value metric: {metric}")
    else:
        score += 20

    # Check if metric scales with value
    if data.get("scales_with_customer_value", False):
        score += 30
    else:
        issues.append("Value metric may not scale with customer success -- review if larger customers pay proportionally more")

    # Check if metric is easy to understand
    if data.get("metric_easy_to_understand", True):
        score += 25
    else:
        issues.append("Complex value metric reduces conversion -- simplify or explain clearly on pricing page")

    # Check for gaming risk
    if data.get("metric_gameable", False):
        score -= 15
        issues.append("Value metric can be gamed by customers (e.g., shared seats, artificial usage reduction)")

    # Red flag checks
    if metric == "per_seat" and data.get("single_power_user_common", False):
        issues.append("Per-seat pricing with single power user pattern -- seats do not scale with value; consider usage-based")
        score -= 10

    if metric == "flat_fee" and data.get("usage_varies_10x", False):
        issues.append("Flat fee with 10x usage variance subsidizes heavy users -- add usage tiers or hybrid model")
        score -= 10

    return {"score": min(max(score, 0), 100), "issues": issues, "metric": metric}


def analyze_tiers(data: dict) -> dict:
    """Analyze tier architecture."""
    tiers = data.get("tiers", [])
    issues = []
    score = 0

    tier_count = len(tiers)

    # Tier count
    guidance = TIER_COUNT_GUIDANCE.get(tier_count)
    if guidance:
        if guidance["issue"]:
            issues.append(guidance["issue"])
        if guidance["rating"] in ("Excellent", "Good"):
            score += 30
        elif guidance["rating"] == "Fair":
            score += 15
    elif tier_count > 4:
        score += 10
        issues.append(f"{tier_count} tiers is too many -- simplify to 3-4 (3-4 tiers outperform 5+ in conversion)")
    elif tier_count == 0:
        return {"score": 0, "issues": ["No tiers defined"], "tier_analysis": []}

    # Price jumps between tiers
    tier_analysis = []
    for i, tier in enumerate(tiers):
        tier_info = {
            "name": tier.get("name", f"Tier {i+1}"),
            "price": tier.get("price_monthly", 0),
            "features": tier.get("features", []),
        }

        if i > 0:
            prev_price = tiers[i-1].get("price_monthly", 0)
            if prev_price > 0:
                multiplier = safe_divide(tier.get("price_monthly", 0), prev_price)
                tier_info["price_multiplier"] = round(multiplier, 1)
                if multiplier < 1.5:
                    issues.append(f"{tier_info['name']} is only {multiplier:.1f}x previous tier -- target 2-3x jumps")
                elif multiplier > 5:
                    issues.append(f"{tier_info['name']} is {multiplier:.1f}x previous tier -- large gap may lose mid-market customers")
                else:
                    score += 10

        tier_analysis.append(tier_info)

    # Enterprise features check (top tier)
    if tiers:
        top_tier = tiers[-1]
        top_features = [f.lower() for f in top_tier.get("features", [])]
        missing_enterprise = []
        for ef in ENTERPRISE_FEATURES:
            if not any(ef in f for f in top_features):
                missing_enterprise.append(ef)

        if missing_enterprise and tier_count >= 3:
            issues.append(f"Top tier missing enterprise features: {', '.join(missing_enterprise[:4])}")
        else:
            score += 15

    # Recommended plan highlight
    has_recommended = any(t.get("is_recommended", False) for t in tiers)
    if not has_recommended and tier_count >= 3:
        issues.append("No tier marked as 'recommended' -- highlight the middle tier to anchor purchasing decisions")
    elif has_recommended:
        score += 10

    return {"score": min(max(score, 0), 100), "issues": issues, "tier_analysis": tier_analysis}


def analyze_pricing_signals(data: dict) -> dict:
    """Analyze pricing health signals."""
    signals = data.get("signals", {})
    issues = []
    diagnostics = []

    trial_conversion = signals.get("trial_to_paid_pct")
    if trial_conversion is not None:
        if trial_conversion > 40:
            diagnostics.append({"signal": "Trial-to-paid > 40%", "diagnosis": "Likely underpriced", "action": "Test 20-30% increase"})
        elif 15 <= trial_conversion <= 30:
            diagnostics.append({"signal": f"Trial-to-paid {trial_conversion}%", "diagnosis": "Healthy range", "action": "Optimize packaging, not price"})
        elif trial_conversion < 10:
            diagnostics.append({"signal": f"Trial-to-paid {trial_conversion}%", "diagnosis": "Possibly overpriced or activation issue", "action": "Investigate whether price or trial experience is the problem"})

    monthly_churn = signals.get("monthly_churn_pct")
    if monthly_churn is not None and monthly_churn > 5:
        diagnostics.append({"signal": f"Monthly churn {monthly_churn}%", "diagnosis": "Fix churn before pricing changes", "action": "Use churn-prevention skill first"})

    years_since_change = signals.get("years_since_price_change")
    if years_since_change is not None and years_since_change >= 2:
        diagnostics.append({"signal": f"Price unchanged for {years_since_change} years", "diagnosis": "Inflation alone justifies 10-15%", "action": "Plan a price increase"})

    annual_adoption = signals.get("annual_plan_adoption_pct")
    if annual_adoption is not None and annual_adoption < 40:
        diagnostics.append({"signal": f"Annual adoption {annual_adoption}%", "diagnosis": "Annual plan underperforming", "action": "Default toggle to annual, show savings prominently ('Save 20%' or '2 months free')"})

    return {"diagnostics": diagnostics, "issues": issues}


def analyze_pricing(data: dict) -> dict:
    """Run full pricing model analysis."""
    vm_result = analyze_value_metric(data)
    tier_result = analyze_tiers(data)
    signal_result = analyze_pricing_signals(data)

    # Overall score
    overall_score = int((vm_result["score"] + tier_result["score"]) / 2)

    all_issues = vm_result["issues"] + tier_result["issues"] + signal_result["issues"]

    if overall_score >= 75:
        rating = "Healthy"
    elif overall_score >= 50:
        rating = "Needs Optimization"
    elif overall_score >= 25:
        rating = "Significant Issues"
    else:
        rating = "Critical"

    return {
        "summary": {
            "overall_score": overall_score,
            "rating": rating,
            "total_issues": len(all_issues),
            "value_metric": vm_result["metric"],
            "tier_count": len(data.get("tiers", [])),
        },
        "value_metric_analysis": vm_result,
        "tier_analysis": tier_result,
        "pricing_signals": signal_result,
        "all_issues": all_issues,
    }


def format_text(result: dict) -> str:
    """Format analysis as human-readable text."""
    lines = []
    s = result["summary"]

    lines.append("=" * 60)
    lines.append("PRICING MODEL ANALYSIS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Overall Score: {s['overall_score']}/100  ({s['rating']})")
    lines.append(f"Value Metric: {s['value_metric']}")
    lines.append(f"Tiers: {s['tier_count']}")
    lines.append(f"Issues Found: {s['total_issues']}")
    lines.append("")

    # Value metric
    vm = result["value_metric_analysis"]
    lines.append("-" * 40)
    lines.append(f"VALUE METRIC ({vm['score']}/100)")
    lines.append("-" * 40)
    for issue in vm["issues"]:
        lines.append(f"  - {issue}")
    if not vm["issues"]:
        lines.append("  No issues found.")
    lines.append("")

    # Tiers
    ta = result["tier_analysis"]
    lines.append("-" * 40)
    lines.append(f"TIER ARCHITECTURE ({ta['score']}/100)")
    lines.append("-" * 40)
    for tier in ta.get("tier_analysis", []):
        mult = f" ({tier['price_multiplier']}x prev)" if "price_multiplier" in tier else ""
        lines.append(f"  {tier['name']}: ${tier['price']:,.0f}/mo{mult}")
    lines.append("")
    for issue in ta["issues"]:
        lines.append(f"  - {issue}")
    lines.append("")

    # Signals
    ps = result["pricing_signals"]
    if ps["diagnostics"]:
        lines.append("-" * 40)
        lines.append("PRICING SIGNALS")
        lines.append("-" * 40)
        for diag in ps["diagnostics"]:
            lines.append(f"\n  Signal: {diag['signal']}")
            lines.append(f"  Diagnosis: {diag['diagnosis']}")
            lines.append(f"  Action: {diag['action']}")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze SaaS pricing model against best practices."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with pricing model configuration",
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

    result = analyze_pricing(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
