#!/usr/bin/env python3
"""Referral Funnel Analyzer - Analyze the 4-stage referral loop with diagnostics.

Evaluates each stage (trigger, share, convert, reward) against benchmarks, identifies
the weakest stage, and provides prioritized improvement recommendations.

Usage:
    python referral_funnel_analyzer.py funnel.json
    python referral_funnel_analyzer.py funnel.json --format json
"""

import argparse
import json
import sys
from typing import Any


STAGE_BENCHMARKS = {
    "awareness": {"target": 40, "good": 25, "label": "Program Awareness (% of active users who know it exists)"},
    "active_referrers": {"target": 15, "good": 5, "label": "Active Referrers (% of aware users who send referrals)"},
    "share_rate": {"target": 40, "good": 20, "label": "Share Rate (% of prompted users who share)"},
    "referred_conversion": {"target": 25, "good": 15, "label": "Referred Conversion (% of referrals that convert)"},
    "reward_redemption": {"target": 90, "good": 70, "label": "Reward Redemption (% redeemed within 30 days)"},
}

STAGE_RECOMMENDATIONS = {
    "awareness": [
        "Add persistent referral widget to user dashboard",
        "Trigger referral prompt after NPS 9-10 responses",
        "Send post-activation email with referral link (3-5 days after activation)",
        "Add referral CTA to monthly usage digest emails",
        "Show referral prompt after milestone achievements",
    ],
    "active_referrers": [
        "Improve incentive visibility (show reward prominently in prompt)",
        "Use double-sided rewards if currently single-sided",
        "Time triggers to high-satisfaction moments (post-milestone, post-support resolution)",
        "Test different reward types (credit vs cash vs feature unlock)",
        "Add tiered rewards for multiple referrals (gamification)",
    ],
    "share_rate": [
        "Add one-click copy link button (most popular share method)",
        "Pre-fill share messages in first person (sounds personal, not marketing)",
        "Add native share sheet on mobile for frictionless sharing",
        "Include multiple share channels (email, Slack, LinkedIn, Twitter)",
        "Reduce steps between referral prompt and actual share action",
    ],
    "referred_conversion": [
        "Personalize landing page with referrer name and photo",
        "Display the incentive above the fold on referral landing page",
        "Pre-fill referred user email if available from share mechanism",
        "Add SSO/social login to reduce signup friction",
        "Ensure 30-day attribution cookie for multi-session conversion",
    ],
    "reward_redemption": [
        "Auto-apply account credits immediately (no manual redemption)",
        "Send instant notification when referral converts",
        "Show cumulative earnings in referral dashboard",
        "Send reminder email for unredeemed rewards after 7 days",
        "Make redemption one-click (no extra steps or forms)",
    ],
}


def safe_divide(num: float, den: float, default: float = 0.0) -> float:
    """Safely divide."""
    return num / den if den != 0 else default


def rate_stage(value: float, benchmark: dict) -> str:
    """Rate a stage against benchmarks."""
    if value >= benchmark["target"]:
        return "Excellent"
    elif value >= benchmark["good"]:
        return "Good"
    elif value >= benchmark["good"] * 0.5:
        return "Needs Improvement"
    else:
        return "Critical"


def analyze_funnel(data: dict) -> dict:
    """Analyze referral funnel stages."""
    stages = data.get("stages", {})
    active_users = data.get("active_users", 0)

    stage_analysis = []
    weakest_stage = None
    weakest_score = 100

    for stage_key, benchmark in STAGE_BENCHMARKS.items():
        value = stages.get(stage_key)
        if value is None:
            continue

        rating = rate_stage(value, benchmark)
        gap_to_target = benchmark["target"] - value

        stage_data = {
            "stage": stage_key,
            "label": benchmark["label"],
            "current_value_pct": value,
            "target_pct": benchmark["target"],
            "good_pct": benchmark["good"],
            "gap_to_target_pp": round(gap_to_target, 1),
            "rating": rating,
        }

        # Track weakest stage
        normalized_score = safe_divide(value, benchmark["target"]) * 100
        if normalized_score < weakest_score:
            weakest_score = normalized_score
            weakest_stage = stage_key

        stage_analysis.append(stage_data)

    # Generate recommendations for weakest stages (sorted by gap)
    recommendations = []
    for stage in sorted(stage_analysis, key=lambda s: -s["gap_to_target_pp"]):
        if stage["gap_to_target_pp"] > 0:
            recs = STAGE_RECOMMENDATIONS.get(stage["stage"], [])
            recommendations.append({
                "stage": stage["stage"],
                "priority": "Critical" if stage["rating"] == "Critical" else "High" if stage["rating"] == "Needs Improvement" else "Medium",
                "gap_pp": stage["gap_to_target_pp"],
                "actions": recs[:3],  # Top 3 actions
            })

    # Overall funnel health
    avg_gap = sum(s["gap_to_target_pp"] for s in stage_analysis) / len(stage_analysis) if stage_analysis else 0
    if avg_gap <= 5:
        overall = "Healthy"
    elif avg_gap <= 15:
        overall = "Needs Optimization"
    else:
        overall = "Underperforming"

    # Impact estimation
    impact = None
    if active_users > 0 and weakest_stage:
        # If we fix the weakest stage to target, what's the downstream impact?
        awareness_pct = stages.get("awareness", 40) / 100
        referrer_pct = stages.get("active_referrers", 10) / 100
        share_rate = stages.get("share_rate", 30) / 100
        conversion_rate = stages.get("referred_conversion", 20) / 100
        avg_invitations = data.get("avg_invitations_per_referrer", 3)

        current_monthly_customers = int(
            active_users * awareness_pct * referrer_pct * avg_invitations * conversion_rate
        )

        # Simulate fixing weakest stage to target
        fixed_values = dict(stages)
        if weakest_stage in STAGE_BENCHMARKS:
            fixed_values[weakest_stage] = STAGE_BENCHMARKS[weakest_stage]["target"]

        fixed_awareness = fixed_values.get("awareness", 40) / 100
        fixed_referrer = fixed_values.get("active_referrers", 10) / 100
        fixed_conversion = fixed_values.get("referred_conversion", 20) / 100

        fixed_monthly_customers = int(
            active_users * fixed_awareness * fixed_referrer * avg_invitations * fixed_conversion
        )

        impact = {
            "weakest_stage": weakest_stage,
            "current_monthly_referred_customers": current_monthly_customers,
            "projected_monthly_after_fix": fixed_monthly_customers,
            "incremental_customers_per_month": fixed_monthly_customers - current_monthly_customers,
        }

    return {
        "summary": {
            "overall_health": overall,
            "stages_analyzed": len(stage_analysis),
            "weakest_stage": weakest_stage,
            "avg_gap_to_target_pp": round(avg_gap, 1),
        },
        "stage_analysis": stage_analysis,
        "recommendations": recommendations,
        "impact_estimate": impact,
    }


def format_text(result: dict) -> str:
    """Format analysis as human-readable text."""
    lines = []
    s = result["summary"]

    lines.append("=" * 60)
    lines.append("REFERRAL FUNNEL ANALYSIS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Overall Health: {s['overall_health']}")
    lines.append(f"Weakest Stage: {s['weakest_stage']}")
    lines.append(f"Avg Gap to Target: {s['avg_gap_to_target_pp']}pp")
    lines.append("")

    lines.append("-" * 60)
    lines.append("STAGE-BY-STAGE ANALYSIS")
    lines.append("-" * 60)
    for stage in result["stage_analysis"]:
        lines.append(f"\n  {stage['label']}")
        lines.append(f"    Current: {stage['current_value_pct']}%  |  Target: {stage['target_pct']}%  |  Gap: {stage['gap_to_target_pp']}pp  |  {stage['rating']}")

    if result["recommendations"]:
        lines.append("")
        lines.append("-" * 60)
        lines.append("PRIORITIZED RECOMMENDATIONS")
        lines.append("-" * 60)
        for rec in result["recommendations"]:
            lines.append(f"\n  [{rec['priority']}] {rec['stage']} (gap: {rec['gap_pp']}pp)")
            for action in rec["actions"]:
                lines.append(f"    - {action}")

    if result.get("impact_estimate"):
        imp = result["impact_estimate"]
        lines.append("")
        lines.append("-" * 40)
        lines.append("IMPACT ESTIMATE")
        lines.append("-" * 40)
        lines.append(f"  If '{imp['weakest_stage']}' reaches target:")
        lines.append(f"    Current: {imp['current_monthly_referred_customers']:,} customers/month")
        lines.append(f"    Projected: {imp['projected_monthly_after_fix']:,} customers/month")
        lines.append(f"    Incremental: +{imp['incremental_customers_per_month']:,} customers/month")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze the 4-stage referral funnel with diagnostics."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with referral funnel metrics",
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

    result = analyze_funnel(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
