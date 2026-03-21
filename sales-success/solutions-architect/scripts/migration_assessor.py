#!/usr/bin/env python3
"""Score migration complexity for platform transitions.

Evaluates migration projects across seven weighted dimensions: application
portfolio, infrastructure type, database count, architecture style,
compliance requirements, downtime tolerance, and data volume.
Produces a complexity score with recommended migration strategy.

Usage:
    python migration_assessor.py --data migration.json
    python migration_assessor.py --data migration.csv --json
    python migration_assessor.py --data migration.json --detailed
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime


COMPLEXITY_DIMENSIONS = {
    "application_count": {
        "weight": 0.20,
        "ranges": [(1, 5, 10), (6, 15, 30), (16, 50, 60), (51, 200, 80), (201, 99999, 100)],
        "description": "Number of applications to migrate",
    },
    "infrastructure_type": {
        "weight": 0.15,
        "values": {
            "cloud": 10, "cloud_native": 5, "virtual": 30, "vm": 30,
            "containerized": 15, "bare_metal": 70, "mainframe": 90, "hybrid": 50,
        },
        "description": "Current infrastructure type complexity",
    },
    "database_count": {
        "weight": 0.15,
        "ranges": [(0, 2, 10), (3, 10, 30), (11, 30, 55), (31, 100, 80), (101, 99999, 100)],
        "description": "Number of databases requiring migration",
    },
    "architecture_style": {
        "weight": 0.15,
        "values": {
            "microservices": 15, "serverless": 10, "soa": 40, "service_oriented": 40,
            "monolith": 70, "monolithic": 70, "legacy": 85, "mainframe": 95,
            "distributed": 30, "event_driven": 25,
        },
        "description": "Architectural style complexity for decoupling",
    },
    "compliance_requirements": {
        "weight": 0.10,
        "values": {
            "none": 5, "basic": 15, "soc2": 35, "hipaa": 55, "pci": 50, "pci_dss": 50,
            "gdpr": 40, "fedramp": 75, "financial": 60, "healthcare": 65,
            "government": 70, "multi_framework": 85,
        },
        "description": "Compliance framework complexity during migration",
    },
    "downtime_tolerance": {
        "weight": 0.10,
        "values": {
            "high": 10, "flexible": 15, "moderate": 35, "standard": 35,
            "low": 65, "minimal": 75, "zero": 95, "none": 95,
        },
        "description": "Tolerance for downtime during migration",
    },
    "data_volume_gb": {
        "weight": 0.15,
        "ranges": [(0, 100, 10), (101, 1000, 25), (1001, 10000, 50), (10001, 100000, 75), (100001, 99999999, 95)],
        "description": "Total data volume to migrate",
    },
}

COMPLEXITY_TIERS = {
    (0, 25): {
        "tier": "Low",
        "strategy": "Lift and Shift",
        "description": "Simple migration. Direct rehosting with minimal changes.",
        "estimated_weeks": "4-8",
        "risk_level": "Low",
    },
    (25, 45): {
        "tier": "Moderate",
        "strategy": "Replatform",
        "description": "Moderate complexity. Replatform with containerization and minor refactoring.",
        "estimated_weeks": "8-16",
        "risk_level": "Medium",
    },
    (45, 65): {
        "tier": "High",
        "strategy": "Refactor / Rearchitect",
        "description": "High complexity. Phased migration with significant refactoring required.",
        "estimated_weeks": "16-32",
        "risk_level": "High",
    },
    (65, 85): {
        "tier": "Very High",
        "strategy": "Strangler Fig Pattern",
        "description": "Very high complexity. Incremental migration using strangler fig with parallel-run.",
        "estimated_weeks": "32-52",
        "risk_level": "Very High",
    },
    (85, 101): {
        "tier": "Extreme",
        "strategy": "Full Rearchitecture",
        "description": "Extreme complexity. Multi-phase rearchitecture program. Consider phased approach over 12+ months.",
        "estimated_weeks": "52+",
        "risk_level": "Critical",
    },
}


def load_data(filepath):
    """Load migration assessment data from CSV or JSON file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif ext == ".csv":
        with open(filepath, "r") as f:
            return list(csv.DictReader(f))
    else:
        print(f"Error: Unsupported file format '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def safe_float(value, default=0.0):
    """Parse float safely."""
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """Parse int safely."""
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return default


def score_range_dimension(value, ranges):
    """Score a numeric dimension against defined ranges."""
    num = safe_int(value, 0) if isinstance(value, str) else int(value) if value else 0
    for lo, hi, score in ranges:
        if lo <= num <= hi:
            return score
    return ranges[-1][2] if ranges else 50


def score_value_dimension(value, values_map):
    """Score a categorical dimension against defined values."""
    if not value:
        return 50  # Default moderate complexity
    val = str(value).lower().strip().replace(" ", "_").replace("-", "_")
    for key, score in values_map.items():
        if key in val:
            return score
    return 50  # Default if not recognized


def assess_migration(project):
    """Assess migration complexity for a single project."""
    name = project.get("name", project.get("project", project.get("customer", "Unknown")))
    source = project.get("source_platform", project.get("from", "Unknown"))
    target = project.get("target_platform", project.get("to", "Cloud"))

    dimension_scores = {}
    total_weighted = 0

    for dim_name, dim_config in COMPLEXITY_DIMENSIONS.items():
        raw_value = project.get(dim_name, project.get(dim_name.replace("_", " "), ""))

        if "ranges" in dim_config:
            score = score_range_dimension(raw_value, dim_config["ranges"])
        else:
            score = score_value_dimension(raw_value, dim_config["values"])

        weighted = score * dim_config["weight"]
        total_weighted += weighted

        dimension_scores[dim_name] = {
            "raw_value": str(raw_value) if raw_value else "Not specified",
            "complexity_score": score,
            "weight": dim_config["weight"],
            "weighted_score": round(weighted, 2),
            "description": dim_config["description"],
        }

    overall_score = round(total_weighted, 1)

    # Determine tier and strategy
    tier_info = None
    for (lo, hi), info in COMPLEXITY_TIERS.items():
        if lo <= overall_score < hi:
            tier_info = info
            break
    if not tier_info:
        tier_info = list(COMPLEXITY_TIERS.values())[-1]

    # Risk factors
    risks = []
    high_dims = [(d, v) for d, v in dimension_scores.items() if v["complexity_score"] >= 70]
    for dim, data in high_dims:
        risks.append({
            "dimension": dim.replace("_", " ").title(),
            "score": data["complexity_score"],
            "description": data["description"],
            "mitigation": _get_mitigation(dim),
        })

    # Resource estimation
    team_size = _estimate_team_size(overall_score)

    # Migration phases
    phases = _generate_phases(overall_score, tier_info["strategy"])

    return {
        "name": name,
        "source_platform": source,
        "target_platform": target,
        "complexity_score": overall_score,
        "complexity_tier": tier_info["tier"],
        "recommended_strategy": tier_info["strategy"],
        "strategy_description": tier_info["description"],
        "estimated_duration_weeks": tier_info["estimated_weeks"],
        "risk_level": tier_info["risk_level"],
        "dimension_scores": dimension_scores,
        "top_risks": risks,
        "estimated_team_size": team_size,
        "migration_phases": phases,
    }


def _get_mitigation(dimension):
    """Get mitigation strategy for a high-complexity dimension."""
    mitigations = {
        "application_count": "Prioritize applications by business impact. Migrate in waves of 5-10.",
        "infrastructure_type": "Assess each system individually. Consider interim virtualization layer.",
        "database_count": "Map data dependencies first. Migrate databases in dependency order.",
        "architecture_style": "Use strangler fig pattern. Decouple incrementally rather than big-bang.",
        "compliance_requirements": "Engage compliance team early. Run parallel compliance validation.",
        "downtime_tolerance": "Plan blue-green deployment. Test failback procedures before cutover.",
        "data_volume_gb": "Use incremental data sync. Pre-stage data before cutover window.",
    }
    return mitigations.get(dimension, "Assess specific requirements and plan mitigation.")


def _estimate_team_size(score):
    """Estimate team size based on complexity."""
    if score < 25:
        return {"engineers": 2, "architects": 1, "pm": 1, "total": 4}
    elif score < 45:
        return {"engineers": 4, "architects": 1, "pm": 1, "total": 6}
    elif score < 65:
        return {"engineers": 6, "architects": 2, "pm": 1, "total": 9}
    elif score < 85:
        return {"engineers": 10, "architects": 2, "pm": 2, "total": 14}
    else:
        return {"engineers": 15, "architects": 3, "pm": 2, "total": 20}


def _generate_phases(score, strategy):
    """Generate recommended migration phases."""
    if score < 25:
        return [
            {"phase": "1. Assessment & Planning", "duration": "1-2 weeks"},
            {"phase": "2. Environment Setup", "duration": "1 week"},
            {"phase": "3. Migration Execution", "duration": "1-2 weeks"},
            {"phase": "4. Testing & Validation", "duration": "1 week"},
            {"phase": "5. Cutover & Go-Live", "duration": "1 day"},
        ]
    elif score < 45:
        return [
            {"phase": "1. Discovery & Assessment", "duration": "2 weeks"},
            {"phase": "2. Architecture & Planning", "duration": "2 weeks"},
            {"phase": "3. Environment Build", "duration": "2 weeks"},
            {"phase": "4. Migration Wave 1 (Pilot)", "duration": "2 weeks"},
            {"phase": "5. Migration Wave 2+", "duration": "4 weeks"},
            {"phase": "6. Testing & Optimization", "duration": "2 weeks"},
            {"phase": "7. Cutover & Decommission", "duration": "1 week"},
        ]
    elif score < 65:
        return [
            {"phase": "1. Detailed Discovery", "duration": "3 weeks"},
            {"phase": "2. Architecture Design", "duration": "3 weeks"},
            {"phase": "3. Proof of Concept", "duration": "2 weeks"},
            {"phase": "4. Environment Build & Security", "duration": "3 weeks"},
            {"phase": "5. Wave 1: Foundation", "duration": "4 weeks"},
            {"phase": "6. Wave 2: Core Systems", "duration": "6 weeks"},
            {"phase": "7. Wave 3: Remaining Systems", "duration": "4 weeks"},
            {"phase": "8. Integration Testing", "duration": "3 weeks"},
            {"phase": "9. Performance Tuning", "duration": "2 weeks"},
            {"phase": "10. Cutover & Hypercare", "duration": "2 weeks"},
        ]
    else:
        return [
            {"phase": "1. Enterprise Assessment", "duration": "4 weeks"},
            {"phase": "2. Target Architecture", "duration": "4 weeks"},
            {"phase": "3. Proof of Concept", "duration": "4 weeks"},
            {"phase": "4. Foundation Build", "duration": "6 weeks"},
            {"phase": "5. Wave 1: Low-Risk Systems", "duration": "6 weeks"},
            {"phase": "6. Wave 2: Core Platform", "duration": "8 weeks"},
            {"phase": "7. Wave 3: Complex Systems", "duration": "8 weeks"},
            {"phase": "8. Wave 4: Legacy Decouple", "duration": "8 weeks"},
            {"phase": "9. Integration & Security", "duration": "4 weeks"},
            {"phase": "10. Performance & Chaos Testing", "duration": "3 weeks"},
            {"phase": "11. Staged Cutover", "duration": "4 weeks"},
            {"phase": "12. Decommission & Hypercare", "duration": "4 weeks"},
        ]


def format_human(results):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("MIGRATION COMPLEXITY ASSESSMENT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    for r in results:
        lines.append(f"\n  Project: {r['name']}")
        lines.append(f"  Migration: {r['source_platform']} -> {r['target_platform']}")
        lines.append(f"  Complexity Score: {r['complexity_score']}/100 ({r['complexity_tier']})")
        lines.append(f"  Risk Level: {r['risk_level']}")
        lines.append(f"  Recommended Strategy: {r['recommended_strategy']}")
        lines.append(f"  Description: {r['strategy_description']}")
        lines.append(f"  Estimated Duration: {r['estimated_duration_weeks']} weeks")

        team = r["estimated_team_size"]
        lines.append(f"  Estimated Team: {team['total']} people "
                     f"({team['engineers']} eng, {team['architects']} arch, {team['pm']} PM)")

        lines.append(f"\n  Complexity Dimensions:")
        for dim_name, dim_data in r["dimension_scores"].items():
            score = dim_data["complexity_score"]
            bar_len = int(score / 10)
            bar = "#" * bar_len + "." * (10 - bar_len)
            flag = " << HIGH" if score >= 70 else ""
            lines.append(
                f"    {dim_name.replace('_', ' '):<24} [{bar}] {score:>3}/100 "
                f"(wt: {dim_data['weight']:.0%}) = {dim_data['weighted_score']:.1f}{flag}"
            )
            lines.append(f"      Value: {dim_data['raw_value']}")

        if r["top_risks"]:
            lines.append(f"\n  Top Risks:")
            for risk in r["top_risks"]:
                lines.append(f"    [{risk['score']}] {risk['dimension']}: {risk['description']}")
                lines.append(f"         Mitigation: {risk['mitigation']}")

        lines.append(f"\n  Migration Phases:")
        for phase in r["migration_phases"]:
            lines.append(f"    {phase['phase']:<45} {phase['duration']}")

        lines.append("-" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score migration complexity and recommend migration strategy."
    )
    parser.add_argument("--data", required=True, help="Path to migration data CSV or JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument(
        "--detailed", action="store_true", help="Include detailed phase breakdown (default in text mode)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    projects = load_data(args.data)
    if not projects:
        print("Error: No migration data found in input file.", file=sys.stderr)
        sys.exit(1)

    results = [assess_migration(p) for p in projects]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    high_risk = sum(1 for r in results if r["complexity_score"] >= 65)
    sys.exit(1 if high_risk > 0 else 0)


if __name__ == "__main__":
    main()
