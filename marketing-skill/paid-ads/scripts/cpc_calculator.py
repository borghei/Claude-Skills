#!/usr/bin/env python3
"""
CPC / CPA / ROAS Calculator

Calculates key paid advertising metrics from campaign data
and benchmarks against industry averages.

Usage:
    python cpc_calculator.py --spend 5000 --clicks 1200 --conversions 45 --revenue 12000
    python cpc_calculator.py --file campaign.json --json
"""

import argparse
import json
import sys
from pathlib import Path

BENCHMARKS = {
    "google_search": {"cpc": (2, 5), "ctr": (2, 5), "cvr": (3, 8), "cpa": (30, 80)},
    "google_display": {"cpc": (0.3, 1.5), "ctr": (0.3, 0.8), "cvr": (0.5, 2), "cpa": (50, 150)},
    "meta": {"cpc": (0.5, 2), "ctr": (0.8, 2), "cvr": (1, 5), "cpa": (20, 60)},
    "linkedin": {"cpc": (5, 12), "ctr": (0.4, 1), "cvr": (1, 3), "cpa": (80, 200)},
    "tiktok": {"cpc": (0.3, 1), "ctr": (0.5, 2), "cvr": (0.5, 3), "cpa": (15, 50)},
    "twitter": {"cpc": (0.5, 2), "ctr": (0.5, 1.5), "cvr": (0.5, 2), "cpa": (30, 80)},
}


def calculate(spend: float, clicks: int, impressions: int = 0, conversions: int = 0,
              revenue: float = 0, leads: int = 0, platform: str = "google_search") -> dict:
    cpc = spend / clicks if clicks > 0 else 0
    cpm = (spend / impressions * 1000) if impressions > 0 else 0
    ctr = (clicks / impressions * 100) if impressions > 0 else 0
    cvr = (conversions / clicks * 100) if clicks > 0 else 0
    cpa = spend / conversions if conversions > 0 else 0
    cpl = spend / leads if leads > 0 else 0
    roas = revenue / spend if spend > 0 else 0
    roi = ((revenue - spend) / spend * 100) if spend > 0 else 0

    bench = BENCHMARKS.get(platform, {})

    def benchmark_status(value, key, lower_is_better=True):
        b = bench.get(key)
        if not b:
            return "N/A"
        if lower_is_better:
            if value <= b[0]:
                return "excellent"
            elif value <= b[1]:
                return "good"
            else:
                return "above_average"
        else:
            if value >= b[1]:
                return "excellent"
            elif value >= b[0]:
                return "good"
            else:
                return "below_average"

    metrics = {
        "spend": round(spend, 2),
        "clicks": clicks,
        "impressions": impressions,
        "conversions": conversions,
        "revenue": round(revenue, 2),
        "leads": leads,
    }

    calculated = {
        "cpc": {"value": round(cpc, 2), "label": "Cost Per Click", "benchmark": benchmark_status(cpc, "cpc")},
        "cpm": {"value": round(cpm, 2), "label": "Cost Per 1000 Impressions"},
        "ctr": {"value": round(ctr, 2), "label": "Click-Through Rate %", "benchmark": benchmark_status(ctr, "ctr", lower_is_better=False)},
        "cvr": {"value": round(cvr, 2), "label": "Conversion Rate %", "benchmark": benchmark_status(cvr, "cvr", lower_is_better=False)},
        "cpa": {"value": round(cpa, 2), "label": "Cost Per Acquisition", "benchmark": benchmark_status(cpa, "cpa")},
        "roas": {"value": round(roas, 2), "label": "Return On Ad Spend"},
        "roi": {"value": round(roi, 2), "label": "Return On Investment %"},
    }
    if leads > 0:
        calculated["cpl"] = {"value": round(cpl, 2), "label": "Cost Per Lead"}

    # Recommendations
    recs = []
    if ctr < bench.get("ctr", (0, 0))[0] and impressions > 0:
        recs.append(f"CTR ({ctr:.1f}%) is below benchmark. Test new ad creative and headlines.")
    if cvr < bench.get("cvr", (0, 0))[0] and clicks > 0:
        recs.append(f"Conversion rate ({cvr:.1f}%) is low. Audit landing page and offer-ad match.")
    if cpa > bench.get("cpa", (0, 999))[1] and conversions > 0:
        recs.append(f"CPA (${cpa:.0f}) is above benchmark. Narrow targeting or improve creative.")
    if roas > 0 and roas < 1:
        recs.append(f"ROAS ({roas:.1f}x) is below break-even. Campaign is losing money.")
    elif roas >= 3:
        recs.append(f"Strong ROAS ({roas:.1f}x). Consider scaling budget 20-30% incrementally.")

    if not recs:
        recs.append("Metrics look healthy. Continue monitoring and testing.")

    return {
        "platform": platform,
        "inputs": metrics,
        "metrics": calculated,
        "recommendations": recs,
        "benchmark_source": f"{platform} industry averages (2025-2026)",
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 55, "  CPC / CPA / ROAS CALCULATOR", "=" * 55]
    lines.append(f"\n  Platform: {result['platform'].replace('_', ' ').title()}")

    inp = result["inputs"]
    lines.append(f"  Spend: ${inp['spend']:,.2f} | Clicks: {inp['clicks']:,} | Conversions: {inp['conversions']:,} | Revenue: ${inp['revenue']:,.2f}")

    lines.append(f"\n  Metrics:")
    for key, m in result["metrics"].items():
        prefix = "$" if key in ("cpc", "cpm", "cpa", "cpl") else ""
        suffix = "%" if key in ("ctr", "cvr", "roi") else "x" if key == "roas" else ""
        bench = f" ({m.get('benchmark', '')})" if m.get("benchmark") else ""
        lines.append(f"    {m['label']:<30} {prefix}{m['value']}{suffix}{bench}")

    if result["recommendations"]:
        lines.append(f"\n  Recommendations:")
        for r in result["recommendations"]:
            lines.append(f"    > {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Calculate paid advertising metrics with benchmarks.")
    parser.add_argument("--spend", type=float)
    parser.add_argument("--clicks", type=int)
    parser.add_argument("--impressions", type=int, default=0)
    parser.add_argument("--conversions", type=int, default=0)
    parser.add_argument("--revenue", type=float, default=0)
    parser.add_argument("--leads", type=int, default=0)
    parser.add_argument("--platform", default="google_search", choices=list(BENCHMARKS.keys()))
    parser.add_argument("--file", "-f", help="JSON file with campaign data")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    if args.file:
        try:
            data = json.loads(Path(args.file).read_text())
            result = calculate(
                data.get("spend", 0), data.get("clicks", 0), data.get("impressions", 0),
                data.get("conversions", 0), data.get("revenue", 0), data.get("leads", 0),
                data.get("platform", "google_search"),
            )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.spend is not None and args.clicks is not None:
        result = calculate(args.spend, args.clicks, args.impressions, args.conversions, args.revenue, args.leads, args.platform)
    else:
        parser.print_help()
        sys.exit(1)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
