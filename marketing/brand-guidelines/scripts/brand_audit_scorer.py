#!/usr/bin/env python3
"""Brand Audit Scorer - Score brand consistency across seven dimensions.

Reads audit data (scores per dimension per channel) and generates a
comprehensive brand consistency report with priorities and recommendations.

Usage:
    python brand_audit_scorer.py audit_data.json
    python brand_audit_scorer.py audit_data.json --json
    python brand_audit_scorer.py --interactive
"""

import argparse
import json
import sys


DIMENSIONS = [
    "color_usage",
    "typography",
    "logo_usage",
    "voice_consistency",
    "imagery_style",
    "layout_patterns",
    "content_quality",
]

DIMENSION_LABELS = {
    "color_usage": "Color Usage",
    "typography": "Typography",
    "logo_usage": "Logo Usage",
    "voice_consistency": "Voice Consistency",
    "imagery_style": "Imagery Style",
    "layout_patterns": "Layout Patterns",
    "content_quality": "Content Quality",
}

DIMENSION_WEIGHTS = {
    "color_usage": 1.2,
    "typography": 1.0,
    "logo_usage": 1.3,
    "voice_consistency": 1.1,
    "imagery_style": 0.9,
    "layout_patterns": 0.8,
    "content_quality": 1.2,
}

CHANNELS = [
    "website", "email", "social_media", "sales_materials",
    "customer_support", "advertising", "product_ui",
]

CHANNEL_VISIBILITY = {
    "website": "high",
    "email": "high",
    "social_media": "high",
    "sales_materials": "medium",
    "customer_support": "medium",
    "advertising": "high",
    "product_ui": "high",
}


def score_audit(audit_data):
    """Score audit data and generate comprehensive analysis."""
    scores_by_dimension = {d: [] for d in DIMENSIONS}
    scores_by_channel = {}
    all_scores = []

    for entry in audit_data:
        channel = entry.get("channel", "unknown")
        if channel not in scores_by_channel:
            scores_by_channel[channel] = []

        for dim in DIMENSIONS:
            score = entry.get(dim)
            if score is not None:
                score = max(1, min(5, int(score)))
                scores_by_dimension[dim].append(score)
                scores_by_channel[channel].append(score)
                all_scores.append(score)

    # Calculate dimension averages
    dimension_scores = {}
    for dim in DIMENSIONS:
        values = scores_by_dimension[dim]
        if values:
            avg = sum(values) / len(values)
            weighted = avg * DIMENSION_WEIGHTS.get(dim, 1.0)
            dimension_scores[dim] = {
                "average": round(avg, 2),
                "weighted": round(weighted, 2),
                "min": min(values),
                "max": max(values),
                "count": len(values),
                "priority": "high" if avg < 3.0 else ("medium" if avg < 4.0 else "low"),
            }

    # Calculate channel averages
    channel_scores = {}
    for channel, values in scores_by_channel.items():
        if values:
            avg = sum(values) / len(values)
            visibility = CHANNEL_VISIBILITY.get(channel, "medium")
            channel_scores[channel] = {
                "average": round(avg, 2),
                "min": min(values),
                "max": max(values),
                "count": len(values),
                "visibility": visibility,
                "priority": _channel_priority(avg, visibility),
            }

    # Overall score
    total_weighted = sum(d["weighted"] for d in dimension_scores.values())
    total_weights = sum(DIMENSION_WEIGHTS[d] for d in dimension_scores.keys())
    overall_weighted = (total_weighted / total_weights) if total_weights > 0 else 0
    overall_raw = (sum(all_scores) / len(all_scores)) if all_scores else 0

    # Consistency score (inverse of standard deviation)
    if len(all_scores) > 1:
        mean = sum(all_scores) / len(all_scores)
        variance = sum((x - mean) ** 2 for x in all_scores) / len(all_scores)
        std_dev = variance ** 0.5
        consistency = max(0, round(100 - (std_dev * 20), 1))
    else:
        consistency = 100

    # Generate recommendations
    recommendations = []
    for dim, data in sorted(dimension_scores.items(), key=lambda x: x[1]["average"]):
        if data["average"] < 3.0:
            recommendations.append({
                "priority": "critical",
                "dimension": DIMENSION_LABELS.get(dim, dim),
                "score": data["average"],
                "action": _get_recommendation(dim, data["average"]),
            })
        elif data["average"] < 4.0:
            recommendations.append({
                "priority": "medium",
                "dimension": DIMENSION_LABELS.get(dim, dim),
                "score": data["average"],
                "action": _get_recommendation(dim, data["average"]),
            })

    for channel, data in sorted(channel_scores.items(), key=lambda x: x[1]["average"]):
        if data["average"] < 3.0 and data["visibility"] == "high":
            recommendations.append({
                "priority": "critical",
                "channel": channel,
                "score": data["average"],
                "action": f"High-visibility channel '{channel}' scores {data['average']:.1f}/5. "
                f"Prioritize brand alignment audit and remediation.",
            })

    return {
        "overall": {
            "raw_score": round(overall_raw, 2),
            "weighted_score": round(overall_weighted, 2),
            "out_of": 5.0,
            "percentage": round((overall_weighted / 5.0) * 100, 1),
            "consistency_score": consistency,
            "total_assessments": len(all_scores),
            "grade": _grade(overall_weighted),
        },
        "dimensions": dimension_scores,
        "channels": channel_scores,
        "recommendations": sorted(recommendations, key=lambda x: x.get("score", 5)),
    }


def _channel_priority(avg, visibility):
    if avg < 3.0 and visibility == "high":
        return "critical"
    elif avg < 3.0:
        return "high"
    elif avg < 4.0 and visibility == "high":
        return "medium"
    return "low"


def _grade(score):
    if score >= 4.5:
        return "A"
    elif score >= 4.0:
        return "B"
    elif score >= 3.0:
        return "C"
    elif score >= 2.0:
        return "D"
    return "F"


def _get_recommendation(dimension, score):
    recs = {
        "color_usage": "Audit all assets for off-brand colors. Create a color enforcement checklist and provide hex codes to all creators.",
        "typography": "Verify font licensing and distribution. Create a typography cheat sheet with exact fonts, weights, and sizes for each context.",
        "logo_usage": "Collect all logo variations in circulation. Remove unauthorized versions and distribute approved logo kit.",
        "voice_consistency": "Run voice audit across all channels. Create channel-specific tone guidelines with before/after examples.",
        "imagery_style": "Define a clear photography/illustration style guide with approved and prohibited examples.",
        "layout_patterns": "Create reusable templates for each channel. Lock master slides and email templates.",
        "content_quality": "Establish editorial review process. Create a content QA checklist and assign content owners per channel.",
    }
    base = recs.get(dimension, "Review and improve this dimension.")
    if score < 2.0:
        return f"URGENT: {base} Current state requires immediate attention."
    return base


def run_interactive():
    """Run an interactive brand audit session."""
    print("=" * 50)
    print("INTERACTIVE BRAND AUDIT")
    print("=" * 50)
    print("\nScore each dimension 1-5 per channel.")
    print("1=Poor, 2=Below Average, 3=Adequate, 4=Strong, 5=Excellent")
    print("Press Enter to skip a dimension.\n")

    audit_data = []
    channels_to_audit = ["website", "email", "social_media", "sales_materials"]

    for channel in channels_to_audit:
        print(f"\n--- {channel.upper().replace('_', ' ')} ---")
        entry = {"channel": channel}
        for dim in DIMENSIONS:
            label = DIMENSION_LABELS.get(dim, dim)
            try:
                val = input(f"  {label} (1-5): ").strip()
                if val:
                    entry[dim] = int(val)
            except (ValueError, EOFError):
                pass
        audit_data.append(entry)

    return audit_data


def format_report(analysis):
    """Format human-readable brand audit report."""
    lines = []
    overall = analysis["overall"]

    lines.append("=" * 60)
    lines.append("BRAND AUDIT REPORT")
    lines.append("=" * 60)
    lines.append(f"Overall Score:       {overall['weighted_score']:.1f}/5.0 (Grade: {overall['grade']})")
    lines.append(f"Percentage:          {overall['percentage']:.0f}%")
    lines.append(f"Consistency:         {overall['consistency_score']:.0f}/100")
    lines.append(f"Total Assessments:   {overall['total_assessments']}")
    lines.append("")

    # Dimension scores
    lines.append("--- DIMENSION SCORES ---")
    lines.append(f"{'Dimension':<25} {'Avg':>5} {'Min':>5} {'Max':>5} {'Priority':>10}")
    lines.append("-" * 55)
    for dim in DIMENSIONS:
        if dim in analysis["dimensions"]:
            d = analysis["dimensions"][dim]
            label = DIMENSION_LABELS.get(dim, dim)
            lines.append(f"{label:<25} {d['average']:>5.1f} {d['min']:>5} {d['max']:>5} {d['priority']:>10}")
    lines.append("")

    # Channel scores
    if analysis["channels"]:
        lines.append("--- CHANNEL SCORES ---")
        lines.append(f"{'Channel':<25} {'Avg':>5} {'Visibility':>12} {'Priority':>10}")
        lines.append("-" * 55)
        for channel, data in sorted(analysis["channels"].items(), key=lambda x: x[1]["average"]):
            lines.append(f"{channel:<25} {data['average']:>5.1f} {data['visibility']:>12} {data['priority']:>10}")
        lines.append("")

    # Recommendations
    if analysis["recommendations"]:
        lines.append("--- RECOMMENDATIONS ---")
        for rec in analysis["recommendations"]:
            priority = rec["priority"].upper()
            target = rec.get("dimension", rec.get("channel", ""))
            lines.append(f"  [{priority}] {target}: {rec['action']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score brand consistency across seven dimensions"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="JSON file with audit data",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run interactive audit session",
    )
    args = parser.parse_args()

    if args.interactive:
        audit_data = run_interactive()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            audit_data = data if isinstance(data, list) else data.get("audits", data.get("assessments", []))
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = score_audit(audit_data)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
