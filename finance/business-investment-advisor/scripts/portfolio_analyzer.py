#!/usr/bin/env python3
"""
Portfolio Analyzer

Analyzes investment portfolio for diversification, concentration risk, sector
exposure, performance metrics, and liquidity profile.

Expected JSON input: {"portfolio": {"total_invested": N, "holdings": [...]}}

Usage:
    python portfolio_analyzer.py portfolio.json
    python portfolio_analyzer.py portfolio.json --format json
    python portfolio_analyzer.py portfolio.json --profile moderate
"""

import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


PROFILES = {
    "conservative": {"max_single": 0.15, "min_sectors": 4, "max_sector": 0.40, "min_liquid": 0.20},
    "moderate": {"max_single": 0.20, "min_sectors": 3, "max_sector": 0.50, "min_liquid": 0.15},
    "aggressive": {"max_single": 0.30, "min_sectors": 2, "max_sector": 0.60, "min_liquid": 0.10},
}


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string."""
    if not date_str or date_str.strip() == "":
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def calculate_hhi(weights: List[float]) -> float:
    """Calculate Herfindahl-Hirschman Index for concentration measurement.
    HHI ranges from 1/N (perfect diversification) to 1.0 (complete concentration).
    """
    return sum(w ** 2 for w in weights)


def analyze_holdings(holdings: List[Dict], total_invested: float) -> Dict[str, Any]:
    """Analyze individual holdings."""
    analyzed = []
    for h in holdings:
        invested = h.get("invested", 0)
        current = h.get("current_value", invested)
        weight = invested / total_invested if total_invested > 0 else 0
        gain_loss = current - invested
        gain_loss_pct = (gain_loss / invested * 100) if invested > 0 else 0

        # Calculate holding period
        date_invested = parse_date(h.get("date_invested", ""))
        holding_months = None
        if date_invested:
            now = datetime.now()
            holding_months = (now.year - date_invested.year) * 12 + (now.month - date_invested.month)

        # Annualized return
        annual_return = None
        if holding_months and holding_months > 0 and invested > 0:
            total_return = current / invested
            years = holding_months / 12
            if years > 0 and total_return > 0:
                annual_return = (total_return ** (1 / years) - 1) * 100

        analyzed.append({
            "name": h.get("name", "Unknown"),
            "type": h.get("type", "unknown"),
            "sector": h.get("sector", "unknown"),
            "stage": h.get("stage", "unknown"),
            "invested": invested,
            "current_value": current,
            "weight_pct": round(weight * 100, 1),
            "gain_loss": round(gain_loss, 2),
            "gain_loss_pct": round(gain_loss_pct, 1),
            "annual_return_pct": round(annual_return, 1) if annual_return else None,
            "holding_months": holding_months,
            "liquidity": h.get("liquidity", "unknown"),
            "status": h.get("status", "active"),
        })

    return analyzed


def analyze_diversification(holdings: List[Dict], total_invested: float,
                            profile: Dict) -> Dict[str, Any]:
    """Analyze portfolio diversification."""
    if not holdings or total_invested <= 0:
        return {"status": "empty", "issues": ["Portfolio is empty"]}

    # Sector analysis
    sector_totals = defaultdict(float)
    for h in holdings:
        sector_totals[h.get("sector", "unknown")] += h.get("invested", 0)

    sector_weights = {s: v / total_invested for s, v in sector_totals.items()}

    # Type analysis
    type_totals = defaultdict(float)
    for h in holdings:
        type_totals[h.get("type", "unknown")] += h.get("invested", 0)

    type_weights = {t: v / total_invested for t, v in type_totals.items()}

    # Stage analysis
    stage_totals = defaultdict(float)
    for h in holdings:
        stage_totals[h.get("stage", "unknown")] += h.get("invested", 0)

    stage_weights = {s: v / total_invested for s, v in stage_totals.items()}

    # Concentration metrics
    holding_weights = [h.get("invested", 0) / total_invested for h in holdings]
    hhi = calculate_hhi(holding_weights)
    max_weight = max(holding_weights) if holding_weights else 0
    top_3_weight = sum(sorted(holding_weights, reverse=True)[:3])

    # Effective number of holdings (inverse HHI)
    effective_n = 1 / hhi if hhi > 0 else 0

    # Issues detection
    issues = []
    recommendations = []

    if max_weight > profile["max_single"]:
        largest = max(holdings, key=lambda h: h.get("invested", 0))
        issues.append(f"Single investment concentration: {largest.get('name')} is "
                      f"{max_weight*100:.1f}% (limit: {profile['max_single']*100:.0f}%)")
        recommendations.append(f"Reduce position in {largest.get('name')} or increase total portfolio size")

    max_sector_weight = max(sector_weights.values()) if sector_weights else 0
    if max_sector_weight > profile["max_sector"]:
        top_sector = max(sector_weights, key=sector_weights.get)
        issues.append(f"Sector concentration: {top_sector} is {max_sector_weight*100:.1f}% "
                      f"(limit: {profile['max_sector']*100:.0f}%)")
        recommendations.append(f"Diversify away from {top_sector} sector")

    if len(sector_totals) < profile["min_sectors"]:
        issues.append(f"Insufficient sector diversification: {len(sector_totals)} sectors "
                      f"(minimum: {profile['min_sectors']})")
        recommendations.append("Add investments in underrepresented sectors")

    # Liquidity analysis
    liquid_total = sum(h.get("invested", 0) for h in holdings
                       if h.get("liquidity", "").lower() in ("liquid", "semi-liquid"))
    liquid_pct = liquid_total / total_invested if total_invested > 0 else 0

    if liquid_pct < profile["min_liquid"]:
        issues.append(f"Low liquidity: {liquid_pct*100:.1f}% liquid/semi-liquid "
                      f"(minimum: {profile['min_liquid']*100:.0f}%)")
        recommendations.append("Increase allocation to liquid or semi-liquid investments")

    return {
        "sector_allocation": {s: round(w * 100, 1) for s, w in sorted(sector_weights.items())},
        "type_allocation": {t: round(w * 100, 1) for t, w in sorted(type_weights.items())},
        "stage_allocation": {s: round(w * 100, 1) for s, w in sorted(stage_weights.items())},
        "concentration": {
            "hhi": round(hhi, 4),
            "effective_holdings": round(effective_n, 1),
            "max_single_weight_pct": round(max_weight * 100, 1),
            "top_3_weight_pct": round(top_3_weight * 100, 1),
        },
        "liquidity": {
            "liquid_pct": round(liquid_pct * 100, 1),
            "illiquid_pct": round((1 - liquid_pct) * 100, 1),
        },
        "issues": issues,
        "recommendations": recommendations,
        "health_score": max(0, 100 - len(issues) * 15),
    }


def analyze_performance(analyzed_holdings: List[Dict], total_invested: float) -> Dict[str, Any]:
    """Analyze portfolio performance."""
    total_current = sum(h["current_value"] for h in analyzed_holdings)
    total_gain = total_current - total_invested
    total_return_pct = (total_gain / total_invested * 100) if total_invested > 0 else 0

    winners = [h for h in analyzed_holdings if h["gain_loss"] > 0]
    losers = [h for h in analyzed_holdings if h["gain_loss"] < 0]
    flat = [h for h in analyzed_holdings if h["gain_loss"] == 0]

    best = max(analyzed_holdings, key=lambda h: h["gain_loss_pct"]) if analyzed_holdings else None
    worst = min(analyzed_holdings, key=lambda h: h["gain_loss_pct"]) if analyzed_holdings else None

    return {
        "total_invested": round(total_invested, 2),
        "total_current_value": round(total_current, 2),
        "total_gain_loss": round(total_gain, 2),
        "total_return_pct": round(total_return_pct, 1),
        "winners": len(winners),
        "losers": len(losers),
        "flat": len(flat),
        "best_performer": {"name": best["name"], "return_pct": best["gain_loss_pct"]} if best else None,
        "worst_performer": {"name": worst["name"], "return_pct": worst["gain_loss_pct"]} if worst else None,
    }


def format_currency(amount: float) -> str:
    if abs(amount) >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    elif abs(amount) >= 1_000:
        return f"${amount/1_000:.1f}K"
    return f"${amount:,.0f}"


def print_human(holdings_data: List[Dict], diversification: Dict, performance: Dict,
                profile_name: str) -> None:
    """Print portfolio analysis in human-readable format."""
    print("=" * 72)
    print(f"  Portfolio Analysis Report (Profile: {profile_name})")
    print("=" * 72)

    # Performance summary
    p = performance
    print(f"\n  --- Performance Summary ---")
    print(f"  Total Invested:      {format_currency(p['total_invested'])}")
    print(f"  Current Value:       {format_currency(p['total_current_value'])}")
    gain_sign = "+" if p['total_gain_loss'] >= 0 else ""
    print(f"  Gain/Loss:           {gain_sign}{format_currency(p['total_gain_loss'])} ({gain_sign}{p['total_return_pct']:.1f}%)")
    print(f"  Winners/Losers/Flat: {p['winners']}/{p['losers']}/{p['flat']}")
    if p["best_performer"]:
        print(f"  Best Performer:      {p['best_performer']['name']} (+{p['best_performer']['return_pct']:.1f}%)")
    if p["worst_performer"]:
        print(f"  Worst Performer:     {p['worst_performer']['name']} ({p['worst_performer']['return_pct']:.1f}%)")

    # Holdings detail
    print(f"\n  --- Holdings ---")
    print(f"  {'Name':<20} {'Invested':>10} {'Current':>10} {'Return':>8} {'Weight':>7} {'Status':<8}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*8} {'-'*7} {'-'*8}")
    for h in sorted(holdings_data, key=lambda x: x["weight_pct"], reverse=True):
        ret = f"{h['gain_loss_pct']:+.1f}%"
        print(f"  {h['name']:<20} {format_currency(h['invested']):>10} "
              f"{format_currency(h['current_value']):>10} {ret:>8} "
              f"{h['weight_pct']:>6.1f}% {h['status']:<8}")

    # Diversification
    d = diversification
    print(f"\n  --- Sector Allocation ---")
    for sector, weight in sorted(d["sector_allocation"].items(), key=lambda x: -x[1]):
        bar = "#" * int(weight / 2)
        print(f"  {sector:<18} {weight:>5.1f}%  {bar}")

    print(f"\n  --- Concentration ---")
    c = d["concentration"]
    print(f"  HHI Index:           {c['hhi']:.4f} (lower is more diversified)")
    print(f"  Effective Holdings:  {c['effective_holdings']:.1f}")
    print(f"  Largest Position:    {c['max_single_weight_pct']:.1f}%")
    print(f"  Top 3 Concentration: {c['top_3_weight_pct']:.1f}%")

    print(f"\n  --- Liquidity ---")
    print(f"  Liquid/Semi-liquid:  {d['liquidity']['liquid_pct']:.1f}%")
    print(f"  Illiquid:            {d['liquidity']['illiquid_pct']:.1f}%")

    # Issues and recommendations
    if d["issues"]:
        print(f"\n  --- Issues ({len(d['issues'])}) ---")
        for issue in d["issues"]:
            print(f"  [!] {issue}")

    if d["recommendations"]:
        print(f"\n  --- Recommendations ---")
        for rec in d["recommendations"]:
            print(f"  --> {rec}")

    print(f"\n  Portfolio Health Score: {d['health_score']}/100")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze portfolio diversification, risk exposure, and performance"
    )
    parser.add_argument("file", help="JSON file with portfolio holdings")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument("--profile", choices=["conservative", "moderate", "aggressive"],
                        default="moderate", help="Investor risk profile (default: moderate)")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        data = json.load(f)

    portfolio = data.get("portfolio", data)
    total_invested = portfolio.get("total_invested", 0)
    holdings = portfolio.get("holdings", [])

    if not holdings:
        print("Error: No holdings found in portfolio data", file=sys.stderr)
        sys.exit(1)

    # If total_invested not set, calculate from holdings
    if total_invested <= 0:
        total_invested = sum(h.get("invested", 0) for h in holdings)

    profile = PROFILES[args.profile]
    analyzed = analyze_holdings(holdings, total_invested)
    diversification = analyze_diversification(holdings, total_invested, profile)
    performance = analyze_performance(analyzed, total_invested)

    if args.format == "json":
        output = {
            "profile": args.profile,
            "holdings": analyzed,
            "diversification": diversification,
            "performance": performance,
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        print_human(analyzed, diversification, performance, args.profile)


if __name__ == "__main__":
    main()
