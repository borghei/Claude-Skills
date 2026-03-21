#!/usr/bin/env python3
"""
A/B Test Experiment Planner

Generates a structured experiment plan from a hypothesis, including
test design, metric selection, sample size estimate, implementation
checklist, and documentation template.

Uses ONLY Python standard library.

Usage:
    python experiment_planner.py --hypothesis "Larger CTA button will increase signups by 15%"
    python experiment_planner.py --hypothesis "..." --baseline 0.05 --mde 0.15 --daily-traffic 3000
    python experiment_planner.py --hypothesis "..." --json
"""

import argparse
import json
import math
import sys
from datetime import datetime, timedelta


def z_score(p: float) -> float:
    """Approximate inverse normal CDF."""
    if p <= 0 or p >= 1:
        raise ValueError("p must be between 0 and 1 exclusive")
    if p > 0.5:
        return -z_score(1 - p)
    t = math.sqrt(-2 * math.log(p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)


def calculate_sample_size(baseline: float, mde: float, alpha: float = 0.05, power: float = 0.80) -> int:
    """Calculate required sample size per variant."""
    p1 = baseline
    p2 = baseline * (1 + mde)
    p2 = min(p2, 0.999)
    z_a = z_score(alpha / 2)
    z_b = z_score(1 - power)
    p_bar = (p1 + p2) / 2
    num = (z_a * math.sqrt(2 * p_bar * (1 - p_bar)) + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    denom = (p2 - p1) ** 2
    return math.ceil(num / denom) if denom > 0 else 0


def classify_hypothesis(text: str) -> dict:
    """Classify a hypothesis text into components."""
    text_lower = text.lower()

    # Detect metric type
    metric_keywords = {
        "signup": "signup_rate",
        "sign-up": "signup_rate",
        "registration": "signup_rate",
        "conversion": "conversion_rate",
        "convert": "conversion_rate",
        "purchase": "purchase_rate",
        "buy": "purchase_rate",
        "revenue": "revenue_per_user",
        "click": "click_through_rate",
        "ctr": "click_through_rate",
        "retention": "retention_rate",
        "churn": "churn_rate",
        "engagement": "engagement_rate",
        "activation": "activation_rate",
        "nps": "nps_score",
        "satisfaction": "satisfaction_score",
    }

    primary_metric = "conversion_rate"
    for keyword, metric in metric_keywords.items():
        if keyword in text_lower:
            primary_metric = metric
            break

    # Detect test category
    category_keywords = {
        "button": "ui_element",
        "cta": "ui_element",
        "headline": "copy",
        "copy": "copy",
        "text": "copy",
        "layout": "layout",
        "page": "layout",
        "pricing": "pricing",
        "price": "pricing",
        "onboarding": "flow",
        "flow": "flow",
        "checkout": "flow",
        "form": "flow",
        "color": "visual",
        "image": "visual",
    }

    category = "general"
    for keyword, cat in category_keywords.items():
        if keyword in text_lower:
            category = cat
            break

    # Suggest guardrail metrics
    guardrail_map = {
        "signup_rate": ["page_load_time", "error_rate", "bounce_rate"],
        "conversion_rate": ["average_order_value", "return_rate", "support_tickets"],
        "purchase_rate": ["cart_abandonment_rate", "refund_rate", "customer_satisfaction"],
        "click_through_rate": ["bounce_rate", "time_on_page", "scroll_depth"],
        "retention_rate": ["feature_adoption", "support_tickets", "nps"],
        "engagement_rate": ["session_duration", "error_rate", "churn_rate"],
        "activation_rate": ["time_to_value", "support_tickets", "drop_off_rate"],
    }

    guardrails = guardrail_map.get(primary_metric, ["error_rate", "page_load_time", "support_tickets"])

    # Suggest secondary metrics
    secondary_map = {
        "signup_rate": ["time_to_signup", "form_completion_rate", "activation_rate"],
        "conversion_rate": ["add_to_cart_rate", "checkout_start_rate", "average_order_value"],
        "click_through_rate": ["scroll_depth", "time_on_page", "bounce_rate"],
    }

    secondary = secondary_map.get(primary_metric, ["time_on_task", "completion_rate", "user_satisfaction"])

    return {
        "primary_metric": primary_metric,
        "secondary_metrics": secondary,
        "guardrail_metrics": guardrails,
        "category": category,
    }


def compute_ice_score(hypothesis: str) -> dict:
    """Compute rough ICE score based on hypothesis keywords."""
    text_lower = hypothesis.lower()

    # Impact heuristic
    impact = 5
    if any(w in text_lower for w in ["revenue", "purchase", "conversion", "signup"]):
        impact = 8
    elif any(w in text_lower for w in ["click", "engagement", "retention"]):
        impact = 7
    elif any(w in text_lower for w in ["color", "font", "minor"]):
        impact = 3

    # Confidence heuristic
    confidence = 5
    if any(w in text_lower for w in ["data shows", "research", "heatmap", "analytics"]):
        confidence = 8
    elif any(w in text_lower for w in ["believe", "think", "might"]):
        confidence = 3

    # Ease heuristic
    ease = 5
    if any(w in text_lower for w in ["button", "color", "text", "copy", "headline"]):
        ease = 8
    elif any(w in text_lower for w in ["redesign", "rebuild", "migrate", "architecture"]):
        ease = 2

    overall = round((impact + confidence + ease) / 3, 1)
    return {"impact": impact, "confidence": confidence, "ease": ease, "overall": overall}


def generate_plan(args) -> dict:
    """Generate complete experiment plan."""
    classification = classify_hypothesis(args.hypothesis)
    ice = compute_ice_score(args.hypothesis)

    sample_size = calculate_sample_size(args.baseline, args.mde)
    total_sample = sample_size * 2

    duration_days = max(14, math.ceil(total_sample / args.daily_traffic)) if args.daily_traffic > 0 else None

    start_date = datetime.now() + timedelta(days=3)
    end_date = start_date + timedelta(days=duration_days) if duration_days else None

    plan = {
        "experiment_name": f"EXP-{datetime.now().strftime('%Y%m%d')}",
        "hypothesis": args.hypothesis,
        "classification": classification,
        "ice_score": ice,
        "design": {
            "type": "A/B" if args.variants == 2 else f"A/B/{args.variants - 1}",
            "variants": args.variants,
            "traffic_allocation": f"{100 // args.variants}/{100 // args.variants}" if args.variants == 2 else "equal split",
            "assignment": "user_id hash (sticky)",
        },
        "metrics": {
            "primary": classification["primary_metric"],
            "secondary": classification["secondary_metrics"],
            "guardrails": classification["guardrail_metrics"],
        },
        "sample_size": {
            "per_variant": sample_size,
            "total": total_sample,
            "baseline_rate": args.baseline,
            "mde_relative": args.mde,
            "mde_absolute": round(args.baseline * args.mde, 6),
            "significance_level": 0.05,
            "power": 0.80,
        },
        "timeline": {
            "prep_days": 3,
            "run_days": duration_days,
            "analysis_days": 2,
            "start_date": start_date.strftime("%Y-%m-%d") if duration_days else "TBD",
            "end_date": end_date.strftime("%Y-%m-%d") if end_date else "TBD",
        },
        "pre_launch_checklist": [
            "Hypothesis documented with primary metric and MDE",
            "Sample size calculated and duration estimated",
            "Both variants implemented and QA'd on all devices",
            "Event tracking verified for both variants",
            "No conflicting tests on same page/feature",
            "Stakeholders informed of test duration and no-peeking rule",
            "External factor calendar checked (holidays, launches, press)",
        ],
        "risks": _identify_risks(args, classification),
    }

    return plan


def _identify_risks(args, classification: dict) -> list:
    """Identify experiment risks."""
    risks = []
    if args.daily_traffic > 0:
        total = calculate_sample_size(args.baseline, args.mde) * 2
        days = math.ceil(total / args.daily_traffic)
        if days > 42:
            risks.append({
                "risk": "Insufficient traffic",
                "severity": "high",
                "mitigation": "Increase MDE (test bolder changes) or combine with qualitative methods",
            })
        if days > 28:
            risks.append({
                "risk": "Long test duration increases contamination risk",
                "severity": "medium",
                "mitigation": "Monitor for external events; document anything that may affect results",
            })

    if classification["category"] == "pricing":
        risks.append({
            "risk": "Pricing tests can cause irreversible perception changes",
            "severity": "high",
            "mitigation": "Use conservative traffic split (90/10); add revenue guardrails",
        })

    if args.baseline < 0.02:
        risks.append({
            "risk": "Low baseline rate requires very large sample",
            "severity": "medium",
            "mitigation": "Consider testing a larger effect size or using composite metrics",
        })

    if not risks:
        risks.append({
            "risk": "Standard experiment risk",
            "severity": "low",
            "mitigation": "Follow pre-launch checklist and monitor guardrail metrics",
        })

    return risks


def format_human_output(plan: dict) -> str:
    """Format plan as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("A/B TEST EXPERIMENT PLAN")
    lines.append("=" * 60)

    lines.append(f"\n  Experiment:  {plan['experiment_name']}")
    lines.append(f"  Hypothesis:  {plan['hypothesis']}")
    lines.append(f"  Category:    {plan['classification']['category']}")

    ice = plan["ice_score"]
    lines.append(f"\n  ICE SCORE: {ice['overall']}/10")
    lines.append(f"    Impact: {ice['impact']}/10 | Confidence: {ice['confidence']}/10 | Ease: {ice['ease']}/10")

    lines.append(f"\n  TEST DESIGN")
    d = plan["design"]
    lines.append(f"    Type:       {d['type']}")
    lines.append(f"    Split:      {d['traffic_allocation']}")
    lines.append(f"    Assignment: {d['assignment']}")

    lines.append(f"\n  METRICS")
    m = plan["metrics"]
    lines.append(f"    Primary:    {m['primary']}")
    lines.append(f"    Secondary:  {', '.join(m['secondary'])}")
    lines.append(f"    Guardrails: {', '.join(m['guardrails'])}")

    lines.append(f"\n  SAMPLE SIZE")
    s = plan["sample_size"]
    lines.append(f"    Per variant: {s['per_variant']:,}")
    lines.append(f"    Total:       {s['total']:,}")
    lines.append(f"    Baseline:    {s['baseline_rate']:.2%}")
    lines.append(f"    MDE:         {s['mde_relative']:.0%} relative ({s['mde_absolute']:.4f} absolute)")

    lines.append(f"\n  TIMELINE")
    t = plan["timeline"]
    lines.append(f"    Prep:     {t['prep_days']} days")
    if t["run_days"]:
        lines.append(f"    Run:      {t['run_days']} days")
        lines.append(f"    Analysis: {t['analysis_days']} days")
        lines.append(f"    Start:    {t['start_date']}")
        lines.append(f"    End:      {t['end_date']}")
    else:
        lines.append("    Run:      TBD (provide --daily-traffic for estimate)")

    lines.append(f"\n  PRE-LAUNCH CHECKLIST")
    for item in plan["pre_launch_checklist"]:
        lines.append(f"    [ ] {item}")

    lines.append(f"\n  RISKS")
    for risk in plan["risks"]:
        lines.append(f"    [{risk['severity'].upper()}] {risk['risk']}")
        lines.append(f"           Mitigation: {risk['mitigation']}")

    lines.append("\n" + "=" * 60)
    lines.append("  DOCUMENTATION TEMPLATE")
    lines.append("=" * 60)
    lines.append(f"""
  EXPERIMENT: {plan['experiment_name']}
  DATE: {plan['timeline']['start_date']} to {plan['timeline']['end_date']}
  OWNER: [Your Name]

  HYPOTHESIS:
  {plan['hypothesis']}

  VARIANTS:
  - Control: [describe current experience]
  - Variant: [describe change]

  METRICS:
  - Primary: {m['primary']} (baseline: {s['baseline_rate']:.2%}, MDE: {s['mde_relative']:.0%})
  - Secondary: {', '.join(m['secondary'])}
  - Guardrails: {', '.join(m['guardrails'])}

  RESULTS:
  - Sample size: [actual] / {s['total']:,} (planned)
  - Duration: {t['run_days'] or 'TBD'} days
  - Primary metric: Control [X]% vs Variant [Y]% (p = [Z])
  - Guardrails: [all clear / violation noted]

  DECISION: [Ship variant / Keep control / Iterate]

  LEARNINGS:
  - [What we learned]
  - [What we'd do differently]""")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a structured A/B test experiment plan from a hypothesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic plan
  python experiment_planner.py --hypothesis "Larger CTA will increase signups by 15%"

  # With traffic data for timeline
  python experiment_planner.py --hypothesis "Simplified checkout will boost conversions" \\
    --baseline 0.08 --mde 0.15 --daily-traffic 3000

  # JSON output
  python experiment_planner.py --hypothesis "New pricing page will increase plan selection" --json
        """,
    )

    parser.add_argument("--hypothesis", "-H", required=True, help="Experiment hypothesis text")
    parser.add_argument("--baseline", "-b", type=float, default=0.05, help="Baseline conversion rate (default: 0.05)")
    parser.add_argument("--mde", "-m", type=float, default=0.10, help="Minimum detectable effect as relative lift (default: 0.10)")
    parser.add_argument("--daily-traffic", "-d", type=int, default=0, help="Daily eligible traffic")
    parser.add_argument("--variants", "-v", type=int, default=2, help="Number of variants including control (default: 2)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    plan = generate_plan(args)

    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        print(format_human_output(plan))


if __name__ == "__main__":
    main()
