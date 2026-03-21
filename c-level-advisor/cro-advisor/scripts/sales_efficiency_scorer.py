#!/usr/bin/env python3
"""
Sales Efficiency Scorer - Score sales efficiency with SaaS benchmarking.

Calculates Magic Number, CAC Payback, quota attainment distribution, win rate,
and sales cycle metrics. Benchmarks against SaaS standards and generates
improvement recommendations.

Usage:
    python sales_efficiency_scorer.py --input sales_data.json
    python sales_efficiency_scorer.py --input sales_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime
from statistics import median, stdev


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def calculate_magic_number(net_new_arr, prior_q_sm_spend):
    """Magic Number = Net New ARR * 4 / Prior Quarter S&M Spend."""
    if prior_q_sm_spend <= 0:
        return 0
    return round((net_new_arr * 4) / prior_q_sm_spend, 2)


def benchmark_magic_number(value):
    if value >= 1.0:
        return {"label": "Excellent", "action": "Invest more aggressively in S&M"}
    elif value >= 0.75:
        return {"label": "Good", "action": "Healthy efficiency -- maintain or scale carefully"}
    elif value >= 0.5:
        return {"label": "Below Average", "action": "Review channel ROI and rep productivity"}
    else:
        return {"label": "Poor", "action": "S&M spend not converting -- diagnose before increasing"}


def calculate_cac_payback(sm_spend, new_customers, avg_arr, gross_margin_pct):
    """CAC Payback = CAC / (Avg ARR * Gross Margin %)."""
    if new_customers <= 0 or avg_arr <= 0 or gross_margin_pct <= 0:
        return 0, 0
    cac = sm_spend / new_customers
    payback_months = round((cac / (avg_arr * (gross_margin_pct / 100))) * 12, 1)
    return round(cac, 0), payback_months


def benchmark_cac_payback(months):
    if months <= 12:
        return {"label": "Excellent", "action": "Very efficient acquisition"}
    elif months <= 18:
        return {"label": "Good", "action": "Healthy payback period"}
    elif months <= 24:
        return {"label": "Acceptable", "action": "Monitor closely -- approaching threshold"}
    else:
        return {"label": "Poor", "action": "CAC payback too long -- reduce CAC or increase ACV"}


def analyze_quota_attainment(rep_attainments):
    """Analyze quota attainment distribution."""
    if not rep_attainments:
        return {}

    hitting = sum(1 for a in rep_attainments if a >= 100)
    over_80 = sum(1 for a in rep_attainments if a >= 80)
    under_50 = sum(1 for a in rep_attainments if a < 50)
    total = len(rep_attainments)

    pct_hitting = round((hitting / total) * 100, 1)
    avg_attainment = round(sum(rep_attainments) / total, 1)
    med_attainment = round(median(rep_attainments), 1)

    distribution_health = "Healthy"
    if pct_hitting < 50:
        distribution_health = "Quota too high or enablement issue"
    elif pct_hitting > 80:
        distribution_health = "Quota too low -- leaving revenue on table"

    result = {
        "total_reps": total,
        "hitting_quota_pct": pct_hitting,
        "above_80_pct": round((over_80 / total) * 100, 1),
        "below_50_pct": round((under_50 / total) * 100, 1),
        "avg_attainment": avg_attainment,
        "median_attainment": med_attainment,
        "distribution_health": distribution_health,
    }

    if total >= 3:
        result["stdev"] = round(stdev(rep_attainments), 1)

    return result


def calculate_win_rate(closed_won, closed_lost):
    """Win Rate = Closed-Won / (Closed-Won + Closed-Lost)."""
    total = closed_won + closed_lost
    if total == 0:
        return 0
    return round((closed_won / total) * 100, 1)


def benchmark_win_rate(rate):
    if rate >= 30:
        return {"label": "Strong", "action": "Maintain qualification rigor"}
    elif rate >= 20:
        return {"label": "Average", "action": "Review qualification criteria -- MEDDPICC"}
    elif rate >= 15:
        return {"label": "Below Average", "action": "Tighten qualification -- too many unqualified deals entering pipeline"}
    else:
        return {"label": "Poor", "action": "Fundamental sales process or ICP issue"}


def analyze_sales_efficiency(data):
    """Run full sales efficiency analysis."""
    company = data.get("company", "Company")
    revenue = data.get("revenue", {})
    costs = data.get("costs", {})
    pipeline = data.get("pipeline", {})
    reps = data.get("rep_attainments", [])

    # Magic Number
    net_new_arr = revenue.get("net_new_arr_quarter", 0)
    sm_spend = costs.get("prior_q_sm_spend", 0)
    magic = calculate_magic_number(net_new_arr, sm_spend)
    magic_bench = benchmark_magic_number(magic)

    # CAC Payback
    total_sm = costs.get("total_sm_spend_period", sm_spend)
    new_customers = revenue.get("new_customers", 0)
    avg_arr = revenue.get("avg_arr_per_customer", 0)
    gross_margin = revenue.get("gross_margin_pct", 75)
    cac, payback = calculate_cac_payback(total_sm, new_customers, avg_arr, gross_margin)
    payback_bench = benchmark_cac_payback(payback)

    # LTV:CAC
    avg_lifetime_months = revenue.get("avg_customer_lifetime_months", 36)
    ltv = round(avg_arr * (gross_margin / 100) * (avg_lifetime_months / 12), 0) if avg_arr > 0 else 0
    ltv_cac_ratio = round(ltv / max(cac, 1), 1) if cac > 0 else 0

    # Win Rate
    closed_won = pipeline.get("closed_won", 0)
    closed_lost = pipeline.get("closed_lost", 0)
    win_rate = calculate_win_rate(closed_won, closed_lost)
    win_bench = benchmark_win_rate(win_rate)

    # Sales Cycle
    avg_cycle_days = pipeline.get("avg_sales_cycle_days", 0)
    cycle_trend = pipeline.get("cycle_trend", "stable")

    # Quota attainment
    quota_analysis = analyze_quota_attainment(reps)

    # Composite efficiency score
    scores = []
    scores.append(min(100, magic * 100))  # Magic number scaled to 0-100
    scores.append(max(0, 100 - (payback * 4)))  # Payback: lower is better
    scores.append(win_rate * 3)  # Win rate scaled
    scores.append(quota_analysis.get("hitting_quota_pct", 50))
    efficiency_score = round(sum(scores) / max(len(scores), 1), 1)

    results = {
        "timestamp": datetime.now().isoformat(),
        "company": company,
        "efficiency_score": efficiency_score,
        "efficiency_label": "Efficient" if efficiency_score >= 60 else ("Moderate" if efficiency_score >= 40 else "Inefficient"),
        "magic_number": {"value": magic, "benchmark": magic_bench["label"], "action": magic_bench["action"]},
        "cac": {"value": cac, "payback_months": payback, "benchmark": payback_bench["label"], "action": payback_bench["action"]},
        "ltv_cac": {"ltv": ltv, "cac": cac, "ratio": ltv_cac_ratio, "healthy": ltv_cac_ratio >= 3},
        "win_rate": {"value": win_rate, "won": closed_won, "lost": closed_lost, "benchmark": win_bench["label"], "action": win_bench["action"]},
        "sales_cycle": {"avg_days": avg_cycle_days, "trend": cycle_trend},
        "quota_attainment": quota_analysis,
        "recommendations": [],
    }

    # Recommendations
    recs = results["recommendations"]
    if magic < 0.5:
        recs.append(f"Magic Number {magic} is poor -- review S&M spend efficiency before scaling")
    if payback > 24:
        recs.append(f"CAC Payback {payback} months exceeds 24-month threshold -- reduce CAC or increase ACV")
    if ltv_cac_ratio < 3 and ltv_cac_ratio > 0:
        recs.append(f"LTV:CAC ratio {ltv_cac_ratio}x below 3x target -- address churn or reduce acquisition cost")
    if win_rate < 20:
        recs.append(f"Win rate {win_rate}% is below average -- tighten qualification with MEDDPICC")
    if quota_analysis.get("below_50_pct", 0) > 25:
        recs.append(f"{quota_analysis['below_50_pct']}% of reps below 50% attainment -- review quota calibration and enablement")
    if cycle_trend == "increasing":
        recs.append("Sales cycle lengthening -- investigate competitive pressure or product alignment")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "SALES EFFICIENCY SCORECARD",
        "=" * 60,
        f"Company: {results['company']}",
        f"Analysis Date: {results['timestamp'][:10]}",
        "",
        f"EFFICIENCY SCORE: {results['efficiency_score']}/100 ({results['efficiency_label']})",
        "",
        "KEY METRICS",
        f"  Magic Number: {results['magic_number']['value']} ({results['magic_number']['benchmark']})",
        f"    {results['magic_number']['action']}",
        "",
        f"  CAC: ${results['cac']['value']:,.0f} | Payback: {results['cac']['payback_months']} months ({results['cac']['benchmark']})",
        f"    {results['cac']['action']}",
        "",
        f"  LTV:CAC: {results['ltv_cac']['ratio']}x (LTV=${results['ltv_cac']['ltv']:,.0f}, CAC=${results['ltv_cac']['cac']:,.0f})",
        f"    {'Healthy' if results['ltv_cac']['healthy'] else 'Below 3x target'}",
        "",
        f"  Win Rate: {results['win_rate']['value']}% ({results['win_rate']['won']}W / {results['win_rate']['lost']}L) ({results['win_rate']['benchmark']})",
        f"    {results['win_rate']['action']}",
        "",
        f"  Sales Cycle: {results['sales_cycle']['avg_days']} days (trend: {results['sales_cycle']['trend']})",
    ]

    qa = results["quota_attainment"]
    if qa:
        lines.extend([
            "",
            "QUOTA ATTAINMENT",
            f"  Reps: {qa['total_reps']}",
            f"  Hitting Quota: {qa['hitting_quota_pct']}%",
            f"  Avg Attainment: {qa['avg_attainment']}%",
            f"  Median Attainment: {qa['median_attainment']}%",
            f"  Below 50%: {qa['below_50_pct']}%",
            f"  Health: {qa['distribution_health']}",
        ])

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score sales efficiency with SaaS benchmarking")
    parser.add_argument("--input", required=True, help="Path to JSON sales data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_sales_efficiency(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
