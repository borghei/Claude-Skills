#!/usr/bin/env python3
"""
Product Portfolio Analyzer - BCG matrix classification and portfolio health scoring.

Classifies products as Star/Cash Cow/Question Mark/Dog, calculates portfolio health,
identifies investment misalignment, and generates rebalancing recommendations.

Usage:
    python product_portfolio_analyzer.py --input portfolio.json
    python product_portfolio_analyzer.py --input portfolio.json --json
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def classify_bcg(growth_rate, relative_market_share, growth_threshold=20, share_threshold=1.0):
    """Classify product using BCG matrix."""
    high_growth = growth_rate >= growth_threshold
    high_share = relative_market_share >= share_threshold

    if high_growth and high_share:
        return "Star"
    elif not high_growth and high_share:
        return "Cash Cow"
    elif high_growth and not high_share:
        return "Question Mark"
    else:
        return "Dog"


def determine_posture(bcg_class, retention_trend, revenue_pct):
    """Map BCG classification to investment posture."""
    posture_map = {
        "Star": "Invest",
        "Cash Cow": "Maintain",
        "Question Mark": "Invest" if retention_trend == "improving" else "Kill",
        "Dog": "Kill",
    }
    posture = posture_map.get(bcg_class, "Maintain")

    # Override: Cash Cows with declining retention may need Harvest
    if bcg_class == "Cash Cow" and retention_trend == "declining":
        posture = "Harvest"

    return posture


def check_investment_alignment(product):
    """Check if engineering investment aligns with posture."""
    posture = product["posture"]
    eng_pct = product.get("engineering_investment_pct", 0)
    revenue_pct = product.get("revenue_pct", 0)

    alignment_rules = {
        "Invest": {"min_eng": 25, "check": eng_pct >= 25},
        "Maintain": {"min_eng": 10, "check": 10 <= eng_pct <= 30},
        "Harvest": {"min_eng": 0, "check": eng_pct <= 15},
        "Kill": {"min_eng": 0, "check": eng_pct <= 10},
    }

    rule = alignment_rules.get(posture, {"check": True})
    aligned = rule["check"]

    misalignment = None
    if not aligned:
        if posture == "Invest" and eng_pct < 25:
            misalignment = f"Underinvested: {eng_pct}% eng for Invest posture (need >=25%)"
        elif posture == "Kill" and eng_pct > 10:
            misalignment = f"Over-invested: {eng_pct}% eng on Kill candidate"
        elif posture == "Harvest" and eng_pct > 15:
            misalignment = f"Over-invested: {eng_pct}% eng on Harvest product"

    return aligned, misalignment


def analyze_portfolio(data):
    """Run full portfolio analysis."""
    products = data.get("products", [])
    company = data.get("company", "Company")
    growth_threshold = data.get("growth_threshold_pct", 20)
    share_threshold = data.get("share_threshold", 1.0)

    results = {
        "timestamp": datetime.now().isoformat(),
        "company": company,
        "product_count": len(products),
        "products": [],
        "bcg_distribution": {"Star": 0, "Cash Cow": 0, "Question Mark": 0, "Dog": 0},
        "posture_distribution": {"Invest": 0, "Maintain": 0, "Harvest": 0, "Kill": 0},
        "portfolio_health": {},
        "misalignments": [],
        "recommendations": [],
    }

    total_revenue = sum(p.get("revenue", 0) for p in products)
    total_eng = sum(p.get("engineering_investment_pct", 0) for p in products)

    for prod in products:
        name = prod.get("name", "Unknown")
        growth = prod.get("growth_rate_pct", 0)
        market_share = prod.get("relative_market_share", 0)
        revenue = prod.get("revenue", 0)
        revenue_pct = round((revenue / max(total_revenue, 1)) * 100, 1)
        retention = prod.get("d30_retention_pct", 0)
        retention_trend = prod.get("retention_trend", "stable")
        eng_pct = prod.get("engineering_investment_pct", 0)

        bcg = classify_bcg(growth, market_share, growth_threshold, share_threshold)
        posture = determine_posture(bcg, retention_trend, revenue_pct)

        product_entry = {
            "name": name,
            "bcg_classification": bcg,
            "posture": posture,
            "growth_rate_pct": growth,
            "relative_market_share": market_share,
            "revenue": revenue,
            "revenue_pct": revenue_pct,
            "engineering_investment_pct": eng_pct,
            "d30_retention_pct": retention,
            "retention_trend": retention_trend,
        }

        aligned, misalignment = check_investment_alignment(product_entry)
        product_entry["investment_aligned"] = aligned
        if misalignment:
            product_entry["misalignment"] = misalignment
            results["misalignments"].append({"product": name, "issue": misalignment, "posture": posture})

        results["products"].append(product_entry)
        results["bcg_distribution"][bcg] += 1
        results["posture_distribution"][posture] += 1

    # Portfolio health metrics
    invest_revenue_pct = sum(
        p["revenue_pct"] for p in results["products"] if p["posture"] == "Invest"
    )
    kill_eng_pct = sum(
        p["engineering_investment_pct"] for p in results["products"] if p["posture"] == "Kill"
    )
    no_posture = sum(1 for p in results["products"] if p["posture"] not in ("Invest", "Maintain", "Harvest", "Kill"))
    qm_over_2q = sum(
        1 for p in results["products"]
        if p["bcg_classification"] == "Question Mark" and prod.get("quarters_as_qm", 0) > 2
    )

    health_score = 100
    health_issues = []

    if invest_revenue_pct < 40:
        health_score -= 20
        health_issues.append(f"Only {invest_revenue_pct}% revenue from Invest products (target >60%)")
    if kill_eng_pct > 20:
        health_score -= 20
        health_issues.append(f"{kill_eng_pct}% engineering on Kill candidates (target <10%)")
    if len(results["misalignments"]) > 0:
        health_score -= 10 * len(results["misalignments"])
        health_issues.append(f"{len(results['misalignments'])} products with investment misalignment")

    results["portfolio_health"] = {
        "score": max(0, health_score),
        "label": "Healthy" if health_score >= 70 else ("At Risk" if health_score >= 40 else "Unhealthy"),
        "invest_revenue_pct": round(invest_revenue_pct, 1),
        "kill_engineering_pct": round(kill_eng_pct, 1),
        "issues": health_issues,
    }

    # Recommendations
    recs = results["recommendations"]
    if results["bcg_distribution"]["Dog"] > 0:
        dogs = [p["name"] for p in results["products"] if p["bcg_classification"] == "Dog"]
        recs.append(f"Kill candidates: {', '.join(dogs)} -- set sunset dates and migration plans")
    if results["bcg_distribution"]["Question Mark"] > 0:
        qms = [p["name"] for p in results["products"] if p["bcg_classification"] == "Question Mark"]
        recs.append(f"Decision needed: {', '.join(qms)} -- invest or kill within 90 days")
    for m in results["misalignments"]:
        recs.append(f"Realign: {m['product']} -- {m['issue']}")
    if invest_revenue_pct < 40:
        recs.append("Portfolio risk: majority of revenue from non-growth products")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "PRODUCT PORTFOLIO ANALYSIS",
        "=" * 60,
        f"Company: {results['company']}",
        f"Products: {results['product_count']}",
        f"Analysis Date: {results['timestamp'][:10]}",
        "",
        f"PORTFOLIO HEALTH: {results['portfolio_health']['score']}/100 ({results['portfolio_health']['label']})",
    ]

    for issue in results["portfolio_health"]["issues"]:
        lines.append(f"  ! {issue}")

    lines.append("")
    lines.append("BCG DISTRIBUTION")
    for cls, count in results["bcg_distribution"].items():
        lines.append(f"  {cls}: {count}")

    lines.append("")
    lines.append("PRODUCT DETAIL")
    for p in results["products"]:
        aligned = "OK" if p["investment_aligned"] else "MISALIGNED"
        lines.append(f"\n  {p['name']}")
        lines.append(f"    BCG: {p['bcg_classification']} | Posture: {p['posture']} | Investment: {aligned}")
        lines.append(f"    Growth: {p['growth_rate_pct']}% | Market Share: {p['relative_market_share']}x")
        lines.append(f"    Revenue: {p['revenue_pct']}% | Eng Investment: {p['engineering_investment_pct']}%")
        lines.append(f"    D30 Retention: {p['d30_retention_pct']}% ({p['retention_trend']})")
        if p.get("misalignment"):
            lines.append(f"    ALERT: {p['misalignment']}")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze product portfolio using BCG matrix and investment alignment")
    parser.add_argument("--input", required=True, help="Path to JSON portfolio data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_portfolio(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
