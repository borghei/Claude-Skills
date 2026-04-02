#!/usr/bin/env python3
"""
A/B Test Plan Designer

Designs comprehensive A/B test plans with hypothesis documentation, metric
definitions, sample size calculations, duration estimates, and risk assessment.

Expected JSON config with: test_name, hypothesis, metric_primary, baseline_rate,
  minimum_detectable_effect, daily_traffic, variants

Usage:
    python test_designer.py test_config.json
    python test_designer.py test_config.json --format json
    python test_designer.py test_config.json --template minimal
"""

import argparse
import json
import math
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


def norm_ppf(p: float) -> float:
    """Inverse normal CDF using rational approximation."""
    if p <= 0 or p >= 1:
        raise ValueError("p must be between 0 and 1")
    if p < 0.5:
        return -norm_ppf(1 - p)
    t = math.sqrt(-2 * math.log(1 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t**2) / (1 + d1 * t + d2 * t**2 + d3 * t**3)


def calculate_sample_size(baseline: float, mde_relative: float,
                          alpha: float, power: float) -> int:
    """Calculate required sample size per variant."""
    treatment = baseline * (1 + mde_relative)
    if treatment <= 0 or treatment >= 1:
        return 0
    z_alpha = norm_ppf(1 - alpha / 2)
    z_beta = norm_ppf(power)
    p_bar = (baseline + treatment) / 2
    numerator = (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) +
                 z_beta * math.sqrt(baseline * (1 - baseline) + treatment * (1 - treatment))) ** 2
    denominator = (baseline - treatment) ** 2
    return math.ceil(numerator / denominator)


def assess_risks(config: Dict[str, Any], duration_days: int) -> List[Dict[str, str]]:
    """Assess test risks and generate mitigations."""
    risks = []

    # Duration risk
    if duration_days > 30:
        risks.append({
            "risk": "Long test duration",
            "severity": "medium",
            "detail": f"Test requires {duration_days} days. External factors may contaminate results.",
            "mitigation": "Consider increasing MDE or traffic allocation to shorten duration.",
        })
    if duration_days > 60:
        risks[-1]["severity"] = "high"

    # Sample size risk
    baseline = config.get("baseline_rate", 0)
    if baseline < 0.01:
        risks.append({
            "risk": "Low baseline rate",
            "severity": "high",
            "detail": f"Baseline rate of {baseline*100:.2f}% requires very large samples.",
            "mitigation": "Consider using a broader metric or accepting larger MDE.",
        })

    # Novelty effect risk
    risks.append({
        "risk": "Novelty/primacy effects",
        "severity": "low",
        "detail": "Users may react differently to new experiences initially.",
        "mitigation": "Run test for minimum 14 days. Consider excluding first 3 days from analysis.",
    })

    # Multiple metrics risk
    secondary = config.get("metric_secondary", [])
    if len(secondary) > 3:
        risks.append({
            "risk": "Multiple comparison inflation",
            "severity": "medium",
            "detail": f"Testing {len(secondary)} secondary metrics increases false positive risk.",
            "mitigation": "Apply Bonferroni correction. Only primary metric determines ship decision.",
        })

    # Interaction risk
    concurrent = config.get("concurrent_tests", [])
    if concurrent:
        risks.append({
            "risk": "Test interaction effects",
            "severity": "medium",
            "detail": f"Running concurrently with: {', '.join(concurrent)}",
            "mitigation": "Ensure non-overlapping audiences or verify no shared metrics.",
        })

    return risks


def generate_test_plan(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a complete test plan from configuration."""
    # Extract config values with defaults
    test_name = config.get("test_name", "Untitled Test")
    hypothesis = config.get("hypothesis", "")
    metric_primary = config.get("metric_primary", "conversion_rate")
    metric_secondary = config.get("metric_secondary", [])
    baseline = config.get("baseline_rate", 0.05)
    mde = config.get("minimum_detectable_effect", 0.10)
    alpha = config.get("significance_level", 0.05)
    power = config.get("power", 0.80)
    variants = config.get("variants", [
        {"name": "control", "description": "Current experience"},
        {"name": "treatment", "description": "New experience"},
    ])
    daily_traffic = config.get("daily_traffic", 0)
    allocation = config.get("allocation", {})

    # Default equal allocation
    if not allocation:
        n_variants = len(variants)
        allocation = {v["name"]: round(1.0 / n_variants, 2) for v in variants}

    # Calculate sample size
    n_per_variant = calculate_sample_size(baseline, mde, alpha, power)
    n_total = n_per_variant * len(variants)

    # Duration estimation
    duration_days = 0
    traffic_per_variant = 0
    if daily_traffic > 0:
        min_allocation = min(allocation.values())
        traffic_per_variant = int(daily_traffic * min_allocation)
        if traffic_per_variant > 0:
            duration_days = math.ceil(n_per_variant / traffic_per_variant)
            duration_days = max(duration_days, 14)  # Minimum 2 weeks

    # Start date (next Monday)
    today = datetime.now()
    days_to_monday = (7 - today.weekday()) % 7
    if days_to_monday == 0:
        days_to_monday = 7
    start_date = today + timedelta(days=days_to_monday)
    end_date = start_date + timedelta(days=duration_days) if duration_days > 0 else None
    analysis_date = end_date + timedelta(days=1) if end_date else None

    # Risk assessment
    risks = assess_risks(config, duration_days)

    # Guardrail metrics
    guardrails = config.get("guardrail_metrics", [])
    if not guardrails:
        guardrails = [
            {"metric": "error_rate", "threshold": "No more than 5% increase"},
            {"metric": "page_load_time", "threshold": "No more than 200ms increase"},
            {"metric": "bounce_rate", "threshold": "No more than 10% relative increase"},
        ]

    # Build plan
    plan = {
        "test_name": test_name,
        "created_date": today.strftime("%Y-%m-%d"),
        "status": "draft",
        "hypothesis": {
            "statement": hypothesis,
            "null_hypothesis": f"There is no difference in {metric_primary} between variants",
            "alternative_hypothesis": f"The treatment variant has a different {metric_primary} than control",
        },
        "metrics": {
            "primary": metric_primary,
            "secondary": metric_secondary,
            "guardrails": guardrails,
        },
        "statistical_design": {
            "test_type": "Two-proportion z-test (two-sided)",
            "baseline_rate": baseline,
            "minimum_detectable_effect": f"{mde*100:.1f}% relative",
            "absolute_effect": f"{baseline*mde*100:.3f}pp",
            "expected_treatment_rate": round(baseline * (1 + mde), 6),
            "significance_level": alpha,
            "power": power,
            "sample_per_variant": n_per_variant,
            "total_sample_required": n_total,
        },
        "variants": [
            {**v, "allocation_pct": round(allocation.get(v["name"], 1/len(variants)) * 100, 1)}
            for v in variants
        ],
        "timeline": {
            "daily_traffic": daily_traffic,
            "traffic_per_variant": traffic_per_variant,
            "estimated_duration_days": duration_days,
            "start_date": start_date.strftime("%Y-%m-%d") if start_date else None,
            "end_date": end_date.strftime("%Y-%m-%d") if end_date else None,
            "analysis_date": analysis_date.strftime("%Y-%m-%d") if analysis_date else None,
        },
        "risks": risks,
        "pre_launch_checklist": [
            {"item": "Hypothesis documented and reviewed by team", "complete": False},
            {"item": "Primary metric instrumented and validated", "complete": False},
            {"item": "Secondary metrics instrumented", "complete": False},
            {"item": "Guardrail metrics monitoring set up", "complete": False},
            {"item": "Variant implementation QA'd in staging", "complete": False},
            {"item": "Random assignment mechanism verified", "complete": False},
            {"item": "Stakeholders aligned on success criteria", "complete": False},
            {"item": "Analysis date committed (no peeking)", "complete": False},
            {"item": "Rollback plan documented", "complete": False},
        ],
        "analysis_plan": {
            "primary_analysis": f"Two-proportion z-test on {metric_primary} at alpha={alpha}",
            "secondary_analysis": f"Report point estimates and CIs for: {', '.join(metric_secondary)}" if metric_secondary else "N/A",
            "subgroup_analysis": config.get("segments", ["device_type", "new_vs_returning"]),
            "decision_framework": {
                "ship": f"Primary metric statistically significant (p < {alpha}) AND positive direction AND no guardrail violations",
                "iterate": "Primary metric trending positive but not significant. Consider extending test or larger MDE.",
                "revert": "Primary metric negative OR guardrail violation",
            },
        },
    }

    return plan


def print_human(plan: Dict[str, Any]) -> None:
    """Print test plan in human-readable format."""
    print("=" * 70)
    print(f"  A/B TEST PLAN: {plan['test_name']}")
    print("=" * 70)
    print(f"  Created: {plan['created_date']}  |  Status: {plan['status']}")

    # Hypothesis
    h = plan["hypothesis"]
    print(f"\n  --- Hypothesis ---")
    print(f"  H1: {h['statement']}")
    print(f"  H0: {h['null_hypothesis']}")

    # Metrics
    m = plan["metrics"]
    print(f"\n  --- Metrics ---")
    print(f"  Primary:    {m['primary']}")
    if m["secondary"]:
        print(f"  Secondary:  {', '.join(m['secondary'])}")
    print(f"  Guardrails:")
    for g in m["guardrails"]:
        print(f"    - {g['metric']}: {g['threshold']}")

    # Statistical design
    s = plan["statistical_design"]
    print(f"\n  --- Statistical Design ---")
    print(f"  Test Type:       {s['test_type']}")
    print(f"  Baseline Rate:   {s['baseline_rate']*100:.2f}%")
    print(f"  MDE:             {s['minimum_detectable_effect']}")
    print(f"  Expected Rate:   {s['expected_treatment_rate']*100:.2f}%")
    print(f"  Alpha:           {s['significance_level']}")
    print(f"  Power:           {s['power']*100:.0f}%")
    print(f"  Sample/Variant:  {s['sample_per_variant']:,}")
    print(f"  Total Sample:    {s['total_sample_required']:,}")

    # Variants
    print(f"\n  --- Variants ---")
    for v in plan["variants"]:
        print(f"  [{v['allocation_pct']:.0f}%] {v['name']}: {v['description']}")

    # Timeline
    t = plan["timeline"]
    print(f"\n  --- Timeline ---")
    if t["daily_traffic"] > 0:
        print(f"  Daily Traffic:    {t['daily_traffic']:,}")
        print(f"  Per Variant:      {t['traffic_per_variant']:,}/day")
        print(f"  Duration:         {t['estimated_duration_days']} days")
        print(f"  Start Date:       {t['start_date']}")
        print(f"  End Date:         {t['end_date']}")
        print(f"  Analysis Date:    {t['analysis_date']}")
    else:
        print(f"  Duration:         Provide daily_traffic to estimate")

    # Risks
    risks = plan["risks"]
    if risks:
        print(f"\n  --- Risks ({len(risks)}) ---")
        for r in risks:
            severity_icon = {"high": "!!!", "medium": " ! ", "low": "   "}.get(r["severity"], "   ")
            print(f"  [{severity_icon}] {r['risk']}: {r['detail']}")
            print(f"         Mitigation: {r['mitigation']}")

    # Decision framework
    d = plan["analysis_plan"]["decision_framework"]
    print(f"\n  --- Decision Framework ---")
    print(f"  SHIP:    {d['ship']}")
    print(f"  ITERATE: {d['iterate']}")
    print(f"  REVERT:  {d['revert']}")

    # Pre-launch checklist
    print(f"\n  --- Pre-Launch Checklist ---")
    for item in plan["pre_launch_checklist"]:
        status = "[x]" if item["complete"] else "[ ]"
        print(f"  {status} {item['item']}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Design comprehensive A/B test plans with hypothesis, metrics, and duration"
    )
    parser.add_argument("file", help="JSON file with test configuration")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        config = json.load(f)

    plan = generate_test_plan(config)

    if args.format == "json":
        print(json.dumps(plan, indent=2, default=str))
    else:
        print_human(plan)


if __name__ == "__main__":
    main()
