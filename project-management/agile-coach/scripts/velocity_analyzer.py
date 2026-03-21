#!/usr/bin/env python3
"""Velocity Analyzer - Analyze sprint velocity trends and forecast capacity.

Reads sprint history data and produces trend analysis, statistical forecasts,
and stability metrics to support sprint planning decisions.

Usage:
    python velocity_analyzer.py --sprints sprints.json
    python velocity_analyzer.py --sprints sprints.json --forecast 3 --json
    python velocity_analyzer.py --example
"""

import argparse
import json
import math
import sys


def load_data(path: str) -> dict:
    """Load sprint data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def calculate_stats(values: list) -> dict:
    """Calculate descriptive statistics for a list of numbers."""
    if not values:
        return {"mean": 0, "median": 0, "std_dev": 0, "min": 0, "max": 0, "count": 0}
    n = len(values)
    mean = sum(values) / n
    sorted_v = sorted(values)
    median = sorted_v[n // 2] if n % 2 == 1 else (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2
    variance = sum((x - mean) ** 2 for x in values) / n if n > 1 else 0
    std_dev = math.sqrt(variance)
    return {
        "mean": round(mean, 1),
        "median": round(median, 1),
        "std_dev": round(std_dev, 1),
        "min": min(values),
        "max": max(values),
        "count": n,
    }


def analyze_velocity(data: dict, forecast_sprints: int = 3) -> dict:
    """Analyze velocity from sprint data."""
    team = data.get("team", "Unknown")
    sprints = data.get("sprints", [])

    if len(sprints) < 2:
        return {"team": team, "error": "Need at least 2 sprints for analysis"}

    # Extract velocity values
    velocities = [s.get("completed_points", 0) for s in sprints]
    committed = [s.get("committed_points", 0) for s in sprints]
    sprint_names = [s.get("name", f"Sprint {i+1}") for i, s in enumerate(sprints)]

    stats = calculate_stats(velocities)

    # Commitment reliability
    reliability_scores = []
    for c, v in zip(committed, velocities):
        if c > 0:
            reliability_scores.append(min(v / c, 1.5))  # Cap at 150%
    avg_reliability = round(sum(reliability_scores) / len(reliability_scores) * 100, 1) if reliability_scores else 0

    # Trend: compare last 3 sprints avg to previous 3
    recent = velocities[-3:] if len(velocities) >= 3 else velocities
    earlier = velocities[-6:-3] if len(velocities) >= 6 else velocities[:len(velocities)//2] if len(velocities) >= 4 else []
    recent_avg = sum(recent) / len(recent)
    earlier_avg = sum(earlier) / len(earlier) if earlier else recent_avg
    if earlier_avg > 0:
        trend_pct = round((recent_avg - earlier_avg) / earlier_avg * 100, 1)
    else:
        trend_pct = 0

    if trend_pct > 10:
        trend_label = "Improving"
    elif trend_pct < -10:
        trend_label = "Declining"
    else:
        trend_label = "Stable"

    # Stability: coefficient of variation
    cv = round(stats["std_dev"] / stats["mean"] * 100, 1) if stats["mean"] > 0 else 0
    if cv <= 15:
        stability = "High"
    elif cv <= 30:
        stability = "Moderate"
    else:
        stability = "Low"

    # Forecast using recent average +/- 1 std_dev
    recent_stats = calculate_stats(recent)
    forecast = {
        "sprints_ahead": forecast_sprints,
        "optimistic": round(recent_stats["mean"] + recent_stats["std_dev"], 0),
        "expected": round(recent_stats["mean"], 0),
        "conservative": round(max(recent_stats["mean"] - recent_stats["std_dev"], 0), 0),
        "range_total_expected": round(recent_stats["mean"] * forecast_sprints, 0),
    }

    # Sprint-by-sprint detail
    sprint_detail = []
    for i, s in enumerate(sprints):
        detail = {
            "name": sprint_names[i],
            "committed": committed[i],
            "completed": velocities[i],
        }
        if committed[i] > 0:
            detail["reliability_pct"] = round(velocities[i] / committed[i] * 100, 1)
        sprint_detail.append(detail)

    return {
        "team": team,
        "sprint_count": len(sprints),
        "statistics": stats,
        "commitment_reliability_pct": avg_reliability,
        "trend": {"direction": trend_label, "change_pct": trend_pct},
        "stability": {"coefficient_of_variation": cv, "rating": stability},
        "forecast": forecast,
        "sprints": sprint_detail,
    }


def print_report(result: dict) -> None:
    """Print human-readable velocity report."""
    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"\nVelocity Analysis: {result['team']}")
    print(f"Sprints Analyzed: {result['sprint_count']}")
    print("=" * 60)

    s = result["statistics"]
    print(f"\nStatistics:")
    print(f"  Average Velocity:  {s['mean']:.1f} points/sprint")
    print(f"  Median:            {s['median']:.1f}")
    print(f"  Std Deviation:     {s['std_dev']:.1f}")
    print(f"  Range:             {s['min']} - {s['max']}")

    t = result["trend"]
    print(f"\nTrend: {t['direction']} ({t['change_pct']:+.1f}%)")

    st = result["stability"]
    print(f"Stability: {st['rating']} (CV: {st['coefficient_of_variation']:.1f}%)")
    print(f"Commitment Reliability: {result['commitment_reliability_pct']:.1f}%")

    print(f"\nSprint History:")
    print(f"  {'Sprint':<20} {'Committed':>10} {'Completed':>10} {'Reliability':>12}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*12}")
    for sp in result["sprints"]:
        rel = f"{sp.get('reliability_pct', 0):.0f}%" if "reliability_pct" in sp else "N/A"
        print(f"  {sp['name']:<20} {sp['committed']:>10} {sp['completed']:>10} {rel:>12}")

    f = result["forecast"]
    print(f"\nForecast (next {f['sprints_ahead']} sprints):")
    print(f"  Optimistic:    {f['optimistic']:.0f} pts/sprint")
    print(f"  Expected:      {f['expected']:.0f} pts/sprint")
    print(f"  Conservative:  {f['conservative']:.0f} pts/sprint")
    print(f"  Total Expected ({f['sprints_ahead']} sprints): {f['range_total_expected']:.0f} pts")
    print()


def print_example() -> None:
    """Print example sprint data JSON."""
    example = {
        "team": "Team Alpha",
        "sprints": [
            {"name": "Sprint 18", "committed_points": 34, "completed_points": 30},
            {"name": "Sprint 19", "committed_points": 32, "completed_points": 32},
            {"name": "Sprint 20", "committed_points": 35, "completed_points": 28},
            {"name": "Sprint 21", "committed_points": 30, "completed_points": 31},
            {"name": "Sprint 22", "committed_points": 33, "completed_points": 35},
            {"name": "Sprint 23", "committed_points": 35, "completed_points": 33},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze sprint velocity trends and forecast future capacity."
    )
    parser.add_argument("--sprints", type=str, help="Path to sprint data JSON file")
    parser.add_argument("--forecast", type=int, default=3, help="Number of sprints to forecast (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example input JSON and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.sprints:
        parser.error("--sprints is required (use --example to see the expected format)")

    data = load_data(args.sprints)
    result = analyze_velocity(data, args.forecast)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
