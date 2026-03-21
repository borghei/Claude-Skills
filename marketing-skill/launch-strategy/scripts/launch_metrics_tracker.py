#!/usr/bin/env python3
"""Launch Metrics Tracker - Track and analyze product launch performance metrics.

Compares actual launch metrics against targets across pre-launch, launch day,
and post-launch phases. Generates performance reports with variance analysis.

Usage:
    python launch_metrics_tracker.py metrics.json
    python launch_metrics_tracker.py metrics.json --json
    python launch_metrics_tracker.py --demo
"""

import argparse
import json
import sys


DEFAULT_TARGETS = {
    "pre_launch": {
        "waitlist_signups": {"target": 500, "unit": "signups", "direction": "higher_better"},
        "email_list_growth_pct": {"target": 10, "unit": "%", "direction": "higher_better"},
        "social_engagement_multiple": {"target": 2.0, "unit": "x", "direction": "higher_better"},
    },
    "launch_day": {
        "landing_page_visitors": {"target": 5000, "unit": "visitors", "direction": "higher_better"},
        "signup_rate": {"target": 8, "unit": "%", "direction": "higher_better"},
        "total_signups": {"target": 400, "unit": "signups", "direction": "higher_better"},
        "social_mentions": {"target": 50, "unit": "mentions", "direction": "higher_better"},
        "product_hunt_rank": {"target": 5, "unit": "rank", "direction": "lower_better"},
    },
    "post_launch_30d": {
        "total_signups_attributed": {"target": 2000, "unit": "signups", "direction": "higher_better"},
        "activation_rate": {"target": 35, "unit": "%", "direction": "higher_better"},
        "press_mentions": {"target": 3, "unit": "mentions", "direction": "higher_better"},
        "seo_keywords_ranking": {"target": 5, "unit": "keywords", "direction": "higher_better"},
        "referral_signups_pct": {"target": 15, "unit": "%", "direction": "higher_better"},
    },
}


def analyze_metrics(data, targets=None):
    """Analyze launch metrics against targets."""
    if targets is None:
        targets = DEFAULT_TARGETS

    phases = {}

    for phase_name, phase_targets in targets.items():
        actuals = data.get(phase_name, {})
        metrics = []

        for metric_name, target_info in phase_targets.items():
            actual = actuals.get(metric_name)
            target = target_info["target"]
            direction = target_info.get("direction", "higher_better")
            unit = target_info.get("unit", "")

            if actual is not None:
                if direction == "higher_better":
                    variance = actual - target
                    variance_pct = ((actual - target) / target * 100) if target != 0 else 0
                    on_track = actual >= target
                else:
                    variance = target - actual
                    variance_pct = ((target - actual) / target * 100) if target != 0 else 0
                    on_track = actual <= target

                status = "exceeded" if (variance_pct > 10) else ("on_track" if on_track else ("at_risk" if variance_pct > -20 else "missed"))
            else:
                variance = None
                variance_pct = None
                on_track = None
                status = "no_data"

            metrics.append({
                "metric": metric_name,
                "target": target,
                "actual": actual,
                "unit": unit,
                "variance": round(variance, 1) if variance is not None else None,
                "variance_pct": round(variance_pct, 1) if variance_pct is not None else None,
                "status": status,
            })

        # Phase summary
        tracked = [m for m in metrics if m["status"] != "no_data"]
        on_track_count = len([m for m in tracked if m["status"] in ("on_track", "exceeded")])
        phase_score = (on_track_count / len(tracked) * 100) if tracked else 0

        phases[phase_name] = {
            "metrics": metrics,
            "total_metrics": len(metrics),
            "tracked": len(tracked),
            "on_track": on_track_count,
            "phase_score": round(phase_score, 1),
            "phase_status": "strong" if phase_score >= 70 else ("moderate" if phase_score >= 40 else "weak"),
        }

    # Overall launch score
    all_tracked = sum(p["tracked"] for p in phases.values())
    all_on_track = sum(p["on_track"] for p in phases.values())
    overall_score = (all_on_track / all_tracked * 100) if all_tracked else 0

    # Key insights
    insights = []
    for phase_name, phase_data in phases.items():
        exceeded = [m for m in phase_data["metrics"] if m["status"] == "exceeded"]
        missed = [m for m in phase_data["metrics"] if m["status"] == "missed"]

        for m in exceeded:
            insights.append({
                "type": "positive",
                "phase": phase_name,
                "insight": f"{m['metric'].replace('_', ' ').title()} exceeded target by {m['variance_pct']:.0f}% ({m['actual']} vs {m['target']} {m['unit']})",
            })
        for m in missed:
            insights.append({
                "type": "negative",
                "phase": phase_name,
                "insight": f"{m['metric'].replace('_', ' ').title()} missed target by {abs(m['variance_pct']):.0f}% ({m['actual']} vs {m['target']} {m['unit']})",
            })

    return {
        "overall_score": round(overall_score, 1),
        "overall_status": "successful" if overall_score >= 70 else ("moderate" if overall_score >= 40 else "underperforming"),
        "phases": phases,
        "insights": insights,
        "metrics_tracked": all_tracked,
        "metrics_on_track": all_on_track,
    }


def get_demo_data():
    return {
        "pre_launch": {
            "waitlist_signups": 720,
            "email_list_growth_pct": 12,
            "social_engagement_multiple": 2.8,
        },
        "launch_day": {
            "landing_page_visitors": 8200,
            "signup_rate": 6.5,
            "total_signups": 533,
            "social_mentions": 87,
            "product_hunt_rank": 3,
        },
        "post_launch_30d": {
            "total_signups_attributed": 2850,
            "activation_rate": 32,
            "press_mentions": 5,
            "seo_keywords_ranking": 8,
            "referral_signups_pct": 11,
        },
    }


def format_report(analysis):
    """Format human-readable metrics report."""
    lines = []
    lines.append("=" * 70)
    lines.append("LAUNCH METRICS REPORT")
    lines.append("=" * 70)
    lines.append(f"Overall Score:   {analysis['overall_score']:.0f}% ({analysis['overall_status'].upper()})")
    lines.append(f"Metrics Tracked: {analysis['metrics_on_track']}/{analysis['metrics_tracked']} on track")
    lines.append("")

    for phase_name, phase_data in analysis["phases"].items():
        label = phase_name.replace("_", " ").title()
        lines.append(f"--- {label} ({phase_data['phase_status'].upper()}, {phase_data['phase_score']:.0f}%) ---")
        lines.append(f"{'Metric':<35} {'Target':>8} {'Actual':>8} {'Var %':>8} {'Status':>10}")
        lines.append("-" * 75)

        for m in phase_data["metrics"]:
            metric_label = m["metric"].replace("_", " ").title()[:34]
            target_str = f"{m['target']}{m['unit']}"
            actual_str = f"{m['actual']}{m['unit']}" if m["actual"] is not None else "N/A"
            var_str = f"{m['variance_pct']:+.0f}%" if m["variance_pct"] is not None else "N/A"

            status_marker = {
                "exceeded": "[++]",
                "on_track": "[OK]",
                "at_risk": "[!!]",
                "missed": "[XX]",
                "no_data": "[--]",
            }[m["status"]]

            lines.append(f"{metric_label:<35} {target_str:>8} {actual_str:>8} {var_str:>8} {status_marker:>10}")
        lines.append("")

    # Insights
    if analysis["insights"]:
        lines.append("--- KEY INSIGHTS ---")
        for insight in analysis["insights"]:
            marker = "+" if insight["type"] == "positive" else "-"
            lines.append(f"  [{marker}] {insight['insight']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Track and analyze launch performance metrics")
    parser.add_argument("input", nargs="?", help="JSON file with actual metrics")
    parser.add_argument("--targets", help="Custom targets JSON file")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    targets = None
    if args.targets:
        with open(args.targets, "r", encoding="utf-8") as f:
            targets = json.load(f)

    analysis = analyze_metrics(data, targets)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
