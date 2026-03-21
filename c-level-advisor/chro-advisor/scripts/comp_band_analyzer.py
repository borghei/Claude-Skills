#!/usr/bin/env python3
"""
Compensation Band Analyzer - Analyze compensation equity and band health.

Evaluates compa-ratios, identifies pay equity issues, flags employees
outside bands, and generates comp adjustment recommendations.
"""

import argparse
import json
import sys
from datetime import datetime


def analyze_bands(data: dict) -> dict:
    """Analyze compensation bands and employee positioning."""
    bands = data.get("bands", {})
    employees = data.get("employees", [])

    results = {
        "timestamp": datetime.now().isoformat(),
        "band_summary": {},
        "employee_analysis": [],
        "equity_flags": [],
        "adjustment_recommendations": [],
        "budget_impact": {},
        "recommendations": [],
    }

    total_adjustment_cost = 0
    outside_band = 0
    below_midpoint = 0

    for emp in employees:
        name = emp.get("name", "")
        level = emp.get("level", "L3")
        current_comp = emp.get("base_salary", 0)
        department = emp.get("department", "")
        tenure_years = emp.get("tenure_years", 0)
        performance = emp.get("performance_rating", 3)
        gender = emp.get("gender", "")
        role_type = emp.get("role_type", "ic")  # ic or management

        # Get band
        band = bands.get(level, {})
        band_min = band.get("min", 0)
        band_mid = band.get("mid", 0)
        band_max = band.get("max", 0)

        if band_mid == 0:
            continue

        # Compa-ratio
        compa_ratio = current_comp / band_mid if band_mid > 0 else 0

        # Position in band
        if current_comp < band_min:
            band_position = "Below Band"
            outside_band += 1
            adjustment = band_min - current_comp
        elif current_comp > band_max:
            band_position = "Above Band"
            outside_band += 1
            adjustment = 0
        elif compa_ratio < 0.90:
            band_position = "Low in Band"
            below_midpoint += 1
            adjustment = band_mid * 0.95 - current_comp if performance >= 3 else 0
        elif compa_ratio > 1.10:
            band_position = "High in Band"
            adjustment = 0
        else:
            band_position = "Midpoint"
            adjustment = 0

        adjustment = max(0, round(adjustment))
        total_adjustment_cost += adjustment

        emp_result = {
            "name": name,
            "level": level,
            "department": department,
            "current_salary": current_comp,
            "band_min": band_min,
            "band_mid": band_mid,
            "band_max": band_max,
            "compa_ratio": round(compa_ratio, 2),
            "band_position": band_position,
            "performance": performance,
            "tenure_years": tenure_years,
            "recommended_adjustment": adjustment,
            "gender": gender,
        }
        results["employee_analysis"].append(emp_result)

        if adjustment > 0:
            results["adjustment_recommendations"].append({
                "name": name,
                "level": level,
                "current": current_comp,
                "recommended": current_comp + adjustment,
                "adjustment": adjustment,
                "reason": f"{band_position} (compa-ratio: {compa_ratio:.2f})",
                "priority": "Immediate" if band_position == "Below Band" else "Next cycle",
            })

    # Pay equity analysis
    by_level_gender = {}
    for emp in results["employee_analysis"]:
        key = (emp["level"], emp["gender"])
        if key not in by_level_gender:
            by_level_gender[key] = []
        by_level_gender[key].append(emp["compa_ratio"])

    # Check for gender gaps
    levels_seen = set(emp["level"] for emp in results["employee_analysis"])
    for level in levels_seen:
        male_ratios = by_level_gender.get((level, "M"), [])
        female_ratios = by_level_gender.get((level, "F"), [])
        if male_ratios and female_ratios:
            avg_m = sum(male_ratios) / len(male_ratios)
            avg_f = sum(female_ratios) / len(female_ratios)
            gap = abs(avg_m - avg_f)
            if gap > 0.05:
                results["equity_flags"].append({
                    "level": level,
                    "type": "Gender pay gap",
                    "detail": f"Avg compa-ratio M={avg_m:.2f} vs F={avg_f:.2f} (gap: {gap:.2f})",
                    "severity": "High" if gap > 0.10 else "Medium",
                })

    # Band summary
    for level, band in bands.items():
        level_emps = [e for e in results["employee_analysis"] if e["level"] == level]
        if level_emps:
            avg_compa = sum(e["compa_ratio"] for e in level_emps) / len(level_emps)
            results["band_summary"][level] = {
                "employees": len(level_emps),
                "band_range": f"${band.get('min', 0):,.0f} - ${band.get('max', 0):,.0f}",
                "midpoint": band.get("mid", 0),
                "avg_compa_ratio": round(avg_compa, 2),
                "below_band": sum(1 for e in level_emps if e["band_position"] == "Below Band"),
                "above_band": sum(1 for e in level_emps if e["band_position"] == "Above Band"),
            }

    # Budget impact
    results["budget_impact"] = {
        "total_adjustment_cost_annual": total_adjustment_cost,
        "employees_needing_adjustment": len(results["adjustment_recommendations"]),
        "employees_outside_band": outside_band,
        "employees_below_midpoint": below_midpoint,
        "pct_within_band": round((len(employees) - outside_band) / len(employees) * 100) if employees else 0,
    }

    # Recommendations
    if outside_band > 0:
        results["recommendations"].append(f"{outside_band} employee(s) outside compensation bands. Adjust to maintain equity.")
    if results["equity_flags"]:
        results["recommendations"].append(f"{len(results['equity_flags'])} pay equity flag(s) detected. Review and remediate.")
    if total_adjustment_cost > 0:
        results["recommendations"].append(f"Total adjustment budget needed: ${total_adjustment_cost:,.0f}/year.")

    return results


def format_text(results: dict) -> str:
    """Format as human-readable report."""
    bi = results["budget_impact"]
    lines = [
        "=" * 75,
        "COMPENSATION BAND ANALYSIS",
        "=" * 75,
        f"Date: {results['timestamp'][:10]}",
        f"Within Band: {bi['pct_within_band']}%  |  Outside: {bi['employees_outside_band']}  |  Adjustments Needed: {bi['employees_needing_adjustment']}",
        f"Adjustment Budget: ${bi['total_adjustment_cost_annual']:,.0f}/year",
        "",
        f"{'Name':<18} {'Level':<5} {'Salary':>10} {'Mid':>10} {'Compa':>6} {'Position':<14} {'Adjust':>8}",
        "-" * 75,
    ]

    for e in sorted(results["employee_analysis"], key=lambda x: x["compa_ratio"]):
        adj = f"${e['recommended_adjustment']:,.0f}" if e["recommended_adjustment"] > 0 else "-"
        icon = "[R]" if e["band_position"] in ["Below Band"] else "[Y]" if e["band_position"] in ["Low in Band", "Above Band"] else "[G]"
        lines.append(
            f"{e['name']:<18} {e['level']:<5} ${e['current_salary']:>9,.0f} ${e['band_mid']:>9,.0f} "
            f"{e['compa_ratio']:>5.2f} {icon} {e['band_position']:<12} {adj:>8}"
        )

    if results["equity_flags"]:
        lines.extend(["", "PAY EQUITY FLAGS:"])
        for ef in results["equity_flags"]:
            lines.append(f"  [{ef['severity']}] {ef['level']}: {ef['detail']}")

    if results["recommendations"]:
        lines.extend(["", "RECOMMENDATIONS:"])
        for r in results["recommendations"]:
            lines.append(f"  -> {r}")

    lines.extend(["", "=" * 75])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze compensation bands and equity")
    parser.add_argument("--input", "-i", help="JSON file with comp data")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {
            "bands": {
                "L2": {"min": 90000, "mid": 110000, "max": 130000},
                "L3": {"min": 130000, "mid": 155000, "max": 180000},
                "L4": {"min": 170000, "mid": 200000, "max": 230000},
                "M1": {"min": 140000, "mid": 165000, "max": 190000},
                "M2": {"min": 170000, "mid": 200000, "max": 230000},
            },
            "employees": [
                {"name": "Alice Chen", "level": "L4", "base_salary": 195000, "department": "Engineering", "tenure_years": 2, "performance_rating": 4, "gender": "F"},
                {"name": "Bob Smith", "level": "L4", "base_salary": 215000, "department": "Engineering", "tenure_years": 3, "performance_rating": 4, "gender": "M"},
                {"name": "Carol Davis", "level": "L3", "base_salary": 125000, "department": "Engineering", "tenure_years": 1, "performance_rating": 3, "gender": "F"},
                {"name": "Dan Lee", "level": "L3", "base_salary": 160000, "department": "Engineering", "tenure_years": 2, "performance_rating": 3, "gender": "M"},
                {"name": "Eve Martinez", "level": "L2", "base_salary": 88000, "department": "Marketing", "tenure_years": 1, "performance_rating": 3, "gender": "F"},
                {"name": "Frank Johnson", "level": "M1", "base_salary": 175000, "department": "Engineering", "tenure_years": 4, "performance_rating": 5, "gender": "M", "role_type": "management"},
            ],
        }

    results = analyze_bands(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
