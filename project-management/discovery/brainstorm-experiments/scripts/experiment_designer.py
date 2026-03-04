#!/usr/bin/env python3
"""
Experiment Designer CLI Tool

Suggests experiment designs for product hypotheses. For each hypothesis,
recommends 2-3 experiment methods with metrics, success thresholds,
effort levels, and duration estimates.

Usage:
    python3 experiment_designer.py input.json [--format json|text]
    python3 experiment_designer.py --demo [--format json|text]

Input JSON format:
    {
        "hypotheses": [
            {
                "hypothesis_text": "At least 20% of trial users will click Upgrade within 7 days",
                "target_segment": "trial users on free plan",
                "product_type": "existing"
            }
        ]
    }

Requires: Python 3.7+ (standard library only)
"""

import argparse
import json
import sys
from typing import Any

# Experiment catalog: method -> details
EXPERIMENTS_NEW = {
    "landing_page": {
        "name": "Landing Page Test",
        "description": "Single-page site describing the product with a sign-up or pre-order CTA. Drive traffic via paid ads or targeted outreach.",
        "default_metric": "Visitor-to-signup conversion rate",
        "default_threshold": "5-10% conversion",
        "effort": "Low",
        "duration": "1-2 weeks",
        "best_for": ["demand", "value_proposition", "willingness_to_pay"],
        "sitg_level": "Medium",
    },
    "explainer_video": {
        "name": "Explainer Video Test",
        "description": "Short (60-90s) video explaining the product concept, distributed via landing page or social media with a CTA.",
        "default_metric": "Video completion rate + CTA conversion",
        "default_threshold": "40% completion, 3-5% CTA conversion",
        "effort": "Low-Medium",
        "duration": "1-2 weeks",
        "best_for": ["comprehension", "interest", "value_proposition"],
        "sitg_level": "Low",
    },
    "pre_order_waitlist": {
        "name": "Pre-Order / Waitlist",
        "description": "Accept payment or email registration for a product that does not yet exist. Strongest demand signal.",
        "default_metric": "Pre-order count or waitlist sign-up rate",
        "default_threshold": "2-5% of visitors pre-order, or 100+ waitlist sign-ups",
        "effort": "Low",
        "duration": "2-4 weeks",
        "best_for": ["willingness_to_pay", "demand"],
        "sitg_level": "High",
    },
    "concierge_mvp": {
        "name": "Concierge MVP",
        "description": "Deliver the service manually to a small group of users as if it were automated. Observe real usage and satisfaction.",
        "default_metric": "Retention rate and willingness to pay after manual service",
        "default_threshold": "70%+ satisfaction, 50%+ would pay",
        "effort": "Medium",
        "duration": "2-4 weeks",
        "best_for": ["solution_fit", "retention", "willingness_to_pay"],
        "sitg_level": "High",
    },
}

EXPERIMENTS_EXISTING = {
    "fake_door": {
        "name": "Fake Door Test",
        "description": "Add a button or link for a feature that does not exist yet. Measure click-through rate. Show a 'coming soon' message on click.",
        "default_metric": "Click-through rate on the fake door element",
        "default_threshold": "3-8% CTR",
        "effort": "Low",
        "duration": "1-2 weeks",
        "best_for": ["demand", "feature_interest"],
        "sitg_level": "Medium",
    },
    "feature_stub": {
        "name": "Feature Stub",
        "description": "Build a minimal, mostly static version of the feature behind a feature flag. Measure adoption and engagement.",
        "default_metric": "Feature adoption rate or engagement rate",
        "default_threshold": "10-20% of exposed users engage",
        "effort": "Low-Medium",
        "duration": "1-2 weeks",
        "best_for": ["engagement", "usability"],
        "sitg_level": "Medium",
    },
    "ab_test": {
        "name": "A/B Test",
        "description": "Randomly assign users to control or variant. Measure a primary metric with statistical significance.",
        "default_metric": "Conversion rate or engagement metric",
        "default_threshold": "Statistically significant improvement (p < 0.05)",
        "effort": "Medium",
        "duration": "2-4 weeks",
        "best_for": ["conversion", "engagement", "retention"],
        "sitg_level": "High",
    },
    "wizard_of_oz": {
        "name": "Wizard of Oz",
        "description": "Feature appears automated to users but is manually operated behind the scenes. Tests complex features before building automation.",
        "default_metric": "Same as if the feature were real (engagement, satisfaction)",
        "default_threshold": "Comparable to automated version targets",
        "effort": "Medium-High",
        "duration": "2-4 weeks",
        "best_for": ["solution_fit", "engagement", "willingness_to_pay"],
        "sitg_level": "High",
    },
    "survey_in_app": {
        "name": "In-App Survey",
        "description": "Targeted survey shown to users matching specific behavioral criteria. Use when behavioral experiments are impractical.",
        "default_metric": "Response rate and preference distribution",
        "default_threshold": "20%+ response rate, clear preference signal",
        "effort": "Low",
        "duration": "1 week",
        "best_for": ["preference", "satisfaction"],
        "sitg_level": "Low",
    },
}

# Keywords in hypothesis text mapped to experiment suitability
KEYWORD_SIGNALS = {
    "pay": ["willingness_to_pay"],
    "purchase": ["willingness_to_pay"],
    "buy": ["willingness_to_pay"],
    "upgrade": ["willingness_to_pay", "conversion"],
    "sign up": ["demand", "conversion"],
    "signup": ["demand", "conversion"],
    "register": ["demand", "conversion"],
    "click": ["feature_interest", "engagement"],
    "use": ["engagement", "retention"],
    "return": ["retention"],
    "retain": ["retention"],
    "adopt": ["engagement", "feature_interest"],
    "prefer": ["preference"],
    "understand": ["comprehension", "usability"],
    "complete": ["usability", "engagement"],
    "share": ["demand", "interest"],
    "recommend": ["satisfaction", "demand"],
    "switch": ["demand", "value_proposition"],
    "engage": ["engagement"],
    "convert": ["conversion"],
}


def detect_signals(hypothesis_text: str) -> list[str]:
    """Extract intent signals from hypothesis text."""
    text_lower = hypothesis_text.lower()
    signals = set()
    for keyword, tags in KEYWORD_SIGNALS.items():
        if keyword in text_lower:
            signals.update(tags)
    if not signals:
        signals.add("demand")
    return list(signals)


def score_experiment(experiment: dict[str, Any], signals: list[str]) -> int:
    """Score how well an experiment matches the detected signals."""
    overlap = set(experiment["best_for"]) & set(signals)
    return len(overlap)


def suggest_experiments(hypothesis: dict[str, Any]) -> dict[str, Any]:
    """Suggest 2-3 experiment designs for a single hypothesis."""
    product_type = hypothesis.get("product_type", "existing").lower()
    hypothesis_text = hypothesis.get("hypothesis_text", "")
    target_segment = hypothesis.get("target_segment", "target users")

    signals = detect_signals(hypothesis_text)

    if product_type == "new":
        catalog = EXPERIMENTS_NEW
    else:
        catalog = EXPERIMENTS_EXISTING

    scored = []
    for key, exp in catalog.items():
        score = score_experiment(exp, signals)
        scored.append((score, key, exp))

    scored.sort(key=lambda x: (-x[0], x[2]["effort"]))

    # Take top 2-3 experiments
    selected = scored[:3] if len(scored) >= 3 else scored

    suggestions = []
    for score, key, exp in selected:
        suggestions.append({
            "method": exp["name"],
            "method_key": key,
            "description": exp["description"],
            "metric": exp["default_metric"],
            "success_threshold": exp["default_threshold"],
            "effort_level": exp["effort"],
            "duration_estimate": exp["duration"],
            "sitg_level": exp["sitg_level"],
            "match_score": score,
        })

    return {
        "hypothesis": hypothesis_text,
        "target_segment": target_segment,
        "product_type": product_type,
        "detected_signals": signals,
        "suggested_experiments": suggestions,
    }


def format_text(results: list[dict[str, Any]]) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("EXPERIMENT DESIGN RECOMMENDATIONS")
    lines.append("=" * 70)

    for i, result in enumerate(results, 1):
        lines.append("")
        lines.append(f"--- Hypothesis {i} ---")
        lines.append(f"  Text:       {result['hypothesis']}")
        lines.append(f"  Segment:    {result['target_segment']}")
        lines.append(f"  Type:       {result['product_type']}")
        lines.append(f"  Signals:    {', '.join(result['detected_signals'])}")
        lines.append("")

        for j, exp in enumerate(result["suggested_experiments"], 1):
            lines.append(f"  Experiment {j}: {exp['method']}")
            lines.append(f"    Description:  {exp['description']}")
            lines.append(f"    Metric:       {exp['metric']}")
            lines.append(f"    Threshold:    {exp['success_threshold']}")
            lines.append(f"    Effort:       {exp['effort_level']}")
            lines.append(f"    Duration:     {exp['duration_estimate']}")
            lines.append(f"    SITG Level:   {exp['sitg_level']}")
            lines.append("")

    lines.append("=" * 70)
    lines.append(f"Total hypotheses analyzed: {len(results)}")
    total_experiments = sum(len(r["suggested_experiments"]) for r in results)
    lines.append(f"Total experiments suggested: {total_experiments}")
    lines.append("=" * 70)

    return "\n".join(lines)


def get_demo_data() -> dict[str, Any]:
    """Return sample input data for demonstration."""
    return {
        "hypotheses": [
            {
                "hypothesis_text": "At least 20% of trial users will click Upgrade to Pro within 7 days",
                "target_segment": "trial users on free plan",
                "product_type": "existing",
            },
            {
                "hypothesis_text": "At least 10% of visitors will sign up for the waitlist after reading the value proposition",
                "target_segment": "developers building internal tools",
                "product_type": "new",
            },
            {
                "hypothesis_text": "At least 60% of onboarded users will complete the setup wizard without help",
                "target_segment": "new users in first session",
                "product_type": "existing",
            },
        ]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Experiment Designer: suggest experiment designs for product hypotheses.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 experiment_designer.py --demo
  python3 experiment_designer.py --demo --format json
  python3 experiment_designer.py hypotheses.json
  python3 experiment_designer.py hypotheses.json --format json

Input JSON format:
  {
    "hypotheses": [
      {
        "hypothesis_text": "At least 20% of trial users will click Upgrade within 7 days",
        "target_segment": "trial users on free plan",
        "product_type": "existing"
      }
    ]
  }
        """,
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to JSON file with hypotheses (omit if using --demo)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with built-in sample data",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
    elif args.input_file:
        try:
            with open(args.input_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    hypotheses = data.get("hypotheses", [])
    if not hypotheses:
        print("Error: No hypotheses found in input data.", file=sys.stderr)
        sys.exit(1)

    results = [suggest_experiments(h) for h in hypotheses]

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
