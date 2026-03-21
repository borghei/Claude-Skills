#!/usr/bin/env python3
"""Score proposed solution architectures against requirements and best practices.

Evaluates architecture proposals across dimensions: scalability, security,
integration complexity, maintainability, performance, and compliance.
Produces an overall fitness score with gap analysis.

Usage:
    python architecture_scorer.py --data architecture.json
    python architecture_scorer.py --data architecture.csv --json
    python architecture_scorer.py --data architecture.json --threshold 70
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime


DIMENSIONS = {
    "scalability": {
        "weight": 0.20,
        "fields": ["horizontal_scaling", "auto_scaling", "load_balancing", "data_partitioning"],
        "description": "Ability to handle growth in users, data, and transactions",
    },
    "security": {
        "weight": 0.20,
        "fields": ["authentication", "authorization", "encryption", "audit_logging"],
        "description": "Security posture across auth, data protection, and compliance",
    },
    "integration": {
        "weight": 0.15,
        "fields": ["api_design", "event_driven", "data_consistency", "error_handling"],
        "description": "Integration architecture quality and patterns",
    },
    "reliability": {
        "weight": 0.15,
        "fields": ["high_availability", "disaster_recovery", "monitoring", "failover"],
        "description": "System reliability, uptime, and recovery capabilities",
    },
    "performance": {
        "weight": 0.15,
        "fields": ["response_time", "throughput", "caching", "optimization"],
        "description": "Performance characteristics and efficiency",
    },
    "maintainability": {
        "weight": 0.15,
        "fields": ["modularity", "documentation", "deployment", "testing"],
        "description": "Ease of maintenance, updates, and operational management",
    },
}

SCORE_LABELS = {
    (0, 40): ("Inadequate", "Architecture has critical gaps. Requires significant redesign."),
    (40, 55): ("Below Standard", "Notable deficiencies. Address gaps before customer presentation."),
    (55, 70): ("Acceptable", "Meets minimum requirements. Strengthen weak areas."),
    (70, 85): ("Strong", "Well-designed architecture. Minor improvements possible."),
    (85, 101): ("Excellent", "Enterprise-grade architecture. Ready for customer presentation."),
}

COMPLIANCE_FRAMEWORKS = {
    "soc2": ["encryption", "audit_logging", "authentication", "authorization", "monitoring"],
    "hipaa": ["encryption", "audit_logging", "authentication", "authorization", "data_partitioning"],
    "gdpr": ["encryption", "data_partitioning", "audit_logging", "documentation"],
    "pci_dss": ["encryption", "authentication", "audit_logging", "monitoring", "failover"],
    "fedramp": ["encryption", "authentication", "authorization", "audit_logging", "monitoring", "disaster_recovery"],
}


def load_data(filepath):
    """Load architecture data from CSV or JSON file."""
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


def parse_score(value, max_val=10):
    """Parse a score value, clamping to 0-max_val."""
    try:
        score = float(value)
        return max(0, min(score, max_val))
    except (ValueError, TypeError):
        return 0


def score_architecture(arch):
    """Score a single architecture proposal."""
    name = arch.get("name", arch.get("project", arch.get("customer", "Unknown")))
    arch_type = arch.get("type", arch.get("architecture_type", "Custom"))
    target_compliance = arch.get("compliance", arch.get("compliance_framework", "")).lower().strip()

    dimension_results = {}
    total_weighted = 0

    for dim_name, dim_config in DIMENSIONS.items():
        field_scores = {}
        for field in dim_config["fields"]:
            raw = arch.get(field, arch.get(f"{dim_name}_{field}", 0))
            field_scores[field] = parse_score(raw, 10)

        populated = sum(1 for v in field_scores.values() if v > 0)
        avg_score = sum(field_scores.values()) / len(dim_config["fields"]) if dim_config["fields"] else 0
        weighted = avg_score * dim_config["weight"]
        total_weighted += weighted

        weak_fields = [f for f, s in field_scores.items() if s < 5]
        strong_fields = [f for f, s in field_scores.items() if s >= 8]

        dimension_results[dim_name] = {
            "score": round(avg_score, 2),
            "weight": dim_config["weight"],
            "weighted_contribution": round(weighted, 2),
            "description": dim_config["description"],
            "field_scores": field_scores,
            "fields_populated": populated,
            "weak_fields": weak_fields,
            "strong_fields": strong_fields,
        }

    overall_score = round(total_weighted * 10, 1)  # Scale to 0-100

    label = "Unknown"
    advice = ""
    for (lo, hi), (lbl, adv) in SCORE_LABELS.items():
        if lo <= overall_score < hi:
            label = lbl
            advice = adv
            break

    # Compliance check
    compliance_result = None
    if target_compliance and target_compliance in COMPLIANCE_FRAMEWORKS:
        required_fields = COMPLIANCE_FRAMEWORKS[target_compliance]
        passed = []
        failed = []
        for field in required_fields:
            score = 0
            for dim_data in dimension_results.values():
                if field in dim_data["field_scores"]:
                    score = dim_data["field_scores"][field]
                    break
            if score >= 7:
                passed.append(field)
            else:
                failed.append({"field": field, "score": score, "required": 7})
        compliance_result = {
            "framework": target_compliance.upper(),
            "passed": len(passed),
            "total": len(required_fields),
            "pass_rate": round(len(passed) / len(required_fields) * 100, 1),
            "gaps": failed,
        }

    # Top risks
    risks = []
    for dim_name, dim_data in dimension_results.items():
        if dim_data["score"] < 5:
            risks.append({
                "dimension": dim_name,
                "score": dim_data["score"],
                "risk": f"Low {dim_name} score ({dim_data['score']}/10) may not meet enterprise requirements",
                "remediation": f"Address weak areas: {', '.join(dim_data['weak_fields'])}",
            })

    return {
        "name": name,
        "architecture_type": arch_type,
        "overall_score": overall_score,
        "label": label,
        "advice": advice,
        "dimensions": dimension_results,
        "compliance": compliance_result,
        "risks": risks,
        "weak_dimensions": [d for d, v in dimension_results.items() if v["score"] < 5],
        "strong_dimensions": [d for d, v in dimension_results.items() if v["score"] >= 8],
    }


def format_human(results, threshold):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("ARCHITECTURE SCORING REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Qualification Threshold: {threshold}/100")
    lines.append("=" * 70)

    for result in results:
        lines.append(f"\n  Architecture: {result['name']}")
        lines.append(f"  Type: {result['architecture_type']}")
        lines.append(f"  Overall Score: {result['overall_score']}/100 ({result['label']})")
        lines.append(f"  Assessment: {result['advice']}")
        status = "QUALIFIED" if result["overall_score"] >= threshold else "BELOW THRESHOLD"
        lines.append(f"  Status: {status}")

        lines.append(f"\n  Dimension Scores:")
        for dim_name, dim_data in result["dimensions"].items():
            bar_len = int(dim_data["score"])
            bar = "#" * bar_len + "." * (10 - bar_len)
            flag = " << WEAK" if dim_data["score"] < 5 else ""
            lines.append(
                f"    {dim_name:<16} [{bar}] {dim_data['score']:.1f}/10 "
                f"(wt: {dim_data['weight']:.0%}, contrib: {dim_data['weighted_contribution']:.2f}){flag}"
            )

            if dim_data["weak_fields"]:
                lines.append(f"      Gaps: {', '.join(dim_data['weak_fields'])}")

        if result["compliance"]:
            comp = result["compliance"]
            lines.append(f"\n  Compliance Check: {comp['framework']}")
            lines.append(f"    Passed: {comp['passed']}/{comp['total']} ({comp['pass_rate']}%)")
            if comp["gaps"]:
                lines.append(f"    Gaps:")
                for gap in comp["gaps"]:
                    lines.append(f"      {gap['field']}: {gap['score']}/10 (need 7+)")

        if result["risks"]:
            lines.append(f"\n  Risks:")
            for risk in result["risks"]:
                lines.append(f"    [{risk['dimension']}] {risk['risk']}")
                lines.append(f"      Fix: {risk['remediation']}")

        lines.append("-" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score proposed solution architectures against best practices."
    )
    parser.add_argument("--data", required=True, help="Path to architecture data CSV or JSON file")
    parser.add_argument(
        "--threshold", type=float, default=70, help="Minimum passing score (default: 70)"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    architectures = load_data(args.data)
    if not architectures:
        print("Error: No architecture data found in input file.", file=sys.stderr)
        sys.exit(1)

    results = [score_architecture(a) for a in architectures]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results, args.threshold))

    below = sum(1 for r in results if r["overall_score"] < args.threshold)
    sys.exit(1 if below > 0 else 0)


if __name__ == "__main__":
    main()
