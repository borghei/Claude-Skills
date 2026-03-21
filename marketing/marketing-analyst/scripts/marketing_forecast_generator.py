#!/usr/bin/env python3
"""Marketing Forecast Generator - Generate marketing performance forecasts.

Uses historical data to project leads, revenue, and pipeline using
linear regression, moving averages, and growth rate extrapolation.

Usage:
    python marketing_forecast_generator.py historical.json --periods 6
    python marketing_forecast_generator.py historical.json --periods 6 --json
    python marketing_forecast_generator.py --demo
"""

import argparse
import json
import sys
import math


def linear_regression(x_vals, y_vals):
    """Simple linear regression returning slope and intercept."""
    n = len(x_vals)
    if n < 2:
        return 0, y_vals[0] if y_vals else 0

    sum_x = sum(x_vals)
    sum_y = sum(y_vals)
    sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
    sum_x2 = sum(x * x for x in x_vals)

    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        return 0, sum_y / n

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    return slope, intercept


def moving_average(values, window=3):
    """Calculate moving average forecast."""
    if len(values) < window:
        return sum(values) / max(len(values), 1)
    return sum(values[-window:]) / window


def growth_rate_forecast(values, periods):
    """Forecast using compound growth rate."""
    if len(values) < 2:
        return [values[-1] if values else 0] * periods

    # Calculate average period-over-period growth
    growth_rates = []
    for i in range(1, len(values)):
        if values[i - 1] > 0:
            rate = (values[i] - values[i - 1]) / values[i - 1]
            growth_rates.append(rate)

    if not growth_rates:
        return [values[-1]] * periods

    avg_growth = sum(growth_rates) / len(growth_rates)
    # Dampen growth rate for longer forecasts
    forecasts = []
    last_val = values[-1]
    for i in range(periods):
        dampened_growth = avg_growth * (0.95 ** i)  # 5% dampening per period
        next_val = last_val * (1 + dampened_growth)
        forecasts.append(round(next_val, 2))
        last_val = next_val

    return forecasts


def generate_forecast(historical_data, forecast_periods=6):
    """Generate multi-method forecast from historical data."""
    metrics = {}

    # Handle different input formats
    if isinstance(historical_data, list):
        # List of period objects
        for period in historical_data:
            for key, value in period.items():
                if key in ("period", "month", "date", "label"):
                    continue
                if isinstance(value, (int, float)):
                    if key not in metrics:
                        metrics[key] = []
                    metrics[key].append(value)
    elif isinstance(historical_data, dict):
        for key, values in historical_data.items():
            if isinstance(values, list) and all(isinstance(v, (int, float)) for v in values):
                metrics[key] = values

    results = {}
    for metric_name, values in metrics.items():
        x_vals = list(range(len(values)))
        n = len(values)

        # Method 1: Linear regression
        slope, intercept = linear_regression(x_vals, values)
        linear_forecast = [round(slope * (n + i) + intercept, 2) for i in range(forecast_periods)]

        # Method 2: Moving average
        ma_value = moving_average(values)
        ma_forecast = [round(ma_value, 2)] * forecast_periods

        # Method 3: Growth rate
        growth_forecast_vals = growth_rate_forecast(values, forecast_periods)

        # Ensemble: weighted average of methods
        ensemble = []
        for i in range(forecast_periods):
            avg = (linear_forecast[i] * 0.4 + growth_forecast_vals[i] * 0.4 + ma_forecast[i] * 0.2)
            ensemble.append(round(max(0, avg), 2))

        # Confidence intervals (simple approach: +/- based on historical variance)
        if len(values) > 2:
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            std_dev = math.sqrt(variance)
            ci_low = [round(max(0, e - 1.96 * std_dev * (1 + i * 0.1)), 2) for i, e in enumerate(ensemble)]
            ci_high = [round(e + 1.96 * std_dev * (1 + i * 0.1), 2) for i, e in enumerate(ensemble)]
        else:
            ci_low = [round(e * 0.8, 2) for e in ensemble]
            ci_high = [round(e * 1.2, 2) for e in ensemble]

        # Historical stats
        avg_val = sum(values) / max(len(values), 1)
        total_growth = ((values[-1] - values[0]) / max(values[0], 1) * 100) if len(values) > 1 else 0

        results[metric_name] = {
            "historical": values,
            "historical_stats": {
                "count": len(values),
                "mean": round(avg_val, 2),
                "min": min(values),
                "max": max(values),
                "total_growth_pct": round(total_growth, 1),
                "avg_period_growth": round(total_growth / max(len(values) - 1, 1), 1),
            },
            "forecast": {
                "ensemble": ensemble,
                "linear": linear_forecast,
                "growth_rate": growth_forecast_vals,
                "moving_average": ma_forecast,
                "confidence_low": ci_low,
                "confidence_high": ci_high,
            },
            "forecast_periods": forecast_periods,
        }

    return results


def get_demo_data():
    return [
        {"month": "Sep", "leads": 850, "revenue": 125000, "pipeline": 380000},
        {"month": "Oct", "leads": 920, "revenue": 138000, "pipeline": 415000},
        {"month": "Nov", "leads": 1050, "revenue": 152000, "pipeline": 460000},
        {"month": "Dec", "leads": 980, "revenue": 145000, "pipeline": 435000},
        {"month": "Jan", "leads": 1120, "revenue": 168000, "pipeline": 505000},
        {"month": "Feb", "leads": 1250, "revenue": 185000, "pipeline": 555000},
    ]


def format_report(results):
    """Format human-readable forecast."""
    lines = []
    lines.append("=" * 70)
    lines.append("MARKETING FORECAST REPORT")
    lines.append("=" * 70)

    for metric_name, data in results.items():
        label = metric_name.replace("_", " ").title()
        lines.append(f"\n--- {label} ---")
        stats = data["historical_stats"]
        lines.append(f"  Historical: {stats['count']} periods, mean={stats['mean']:,.0f}, growth={stats['total_growth_pct']:+.1f}%")

        lines.append(f"  {'Period':>8} {'Forecast':>12} {'Low':>12} {'High':>12}")
        lines.append("  " + "-" * 50)

        for i in range(data["forecast_periods"]):
            f_val = data["forecast"]["ensemble"][i]
            low = data["forecast"]["confidence_low"][i]
            high = data["forecast"]["confidence_high"][i]
            lines.append(f"  {f'P+{i+1}':>8} {f_val:>12,.0f} {low:>12,.0f} {high:>12,.0f}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate marketing performance forecasts")
    parser.add_argument("input", nargs="?", help="JSON file with historical data")
    parser.add_argument("--periods", type=int, default=6, help="Forecast periods")
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

    results = generate_forecast(data, args.periods)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(format_report(results))


if __name__ == "__main__":
    main()
