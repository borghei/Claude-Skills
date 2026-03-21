#!/usr/bin/env python3
"""
Feature Prioritizer - Prioritize features using RICE, ICE, or weighted scoring.

Generates stack-ranked backlogs, flags scoring anomalies, and supports
category-level grouping and custom weight configurations.

Usage:
    python feature_prioritizer.py --input features.json
    python feature_prioritizer.py --input features.json --method ice
    python feature_prioritizer.py --input features.json --json
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def score_rice(feature):
    """RICE: (Reach x Impact x Confidence) / Effort."""
    reach = feature.get("reach", 1)
    impact = feature.get("impact", 1)
    confidence = feature.get("confidence", 100) / 100
    effort = max(feature.get("effort", 1), 0.1)
    return round((reach * impact * confidence) / effort, 1)


def score_ice(feature):
    """ICE: Impact x Confidence x Ease (inverse of effort)."""
    impact = feature.get("impact", 1)
    confidence = feature.get("confidence", 100) / 100
    effort = max(feature.get("effort", 1), 0.1)
    ease = 10 / effort  # Invert effort: lower effort = higher ease
    return round(impact * confidence * ease, 1)


def score_weighted(feature, weights):
    """Custom weighted scoring across configurable dimensions."""
    total = 0
    for dim, weight in weights.items():
        val = feature.get(dim, 0)
        total += val * weight
    return round(total, 1)


def detect_anomalies(features, method):
    """Detect scoring anomalies that suggest bias or calibration issues."""
    anomalies = []
    scores = [f["score"] for f in features]
    if not scores:
        return anomalies

    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)

    # Check for extreme outliers (> 3x average)
    for f in features:
        if f["score"] > avg_score * 3:
            anomalies.append({
                "feature": f["name"],
                "issue": f"Score {f['score']} is >3x the average ({avg_score:.1f}) -- verify inputs",
                "type": "outlier_high",
            })

    # Check for suspiciously uniform confidence
    confidences = [f.get("confidence", 100) for f in features]
    if len(set(confidences)) == 1 and len(features) > 3:
        anomalies.append({
            "feature": "ALL",
            "issue": f"All features have identical confidence ({confidences[0]}%) -- likely not calibrated",
            "type": "uniform_confidence",
        })

    # Check for zero-effort features
    for f in features:
        if f.get("effort", 1) == 0:
            anomalies.append({
                "feature": f["name"],
                "issue": "Effort is 0 -- no feature has zero effort",
                "type": "zero_effort",
            })

    # Check for high impact + low confidence (risky bets)
    for f in features:
        if f.get("impact", 0) >= 8 and f.get("confidence", 100) < 50:
            anomalies.append({
                "feature": f["name"],
                "issue": f"High impact ({f.get('impact')}) but low confidence ({f.get('confidence')}%) -- risky bet",
                "type": "risky_bet",
            })

    return anomalies


def prioritize_features(data, method="rice"):
    """Run feature prioritization."""
    features = data.get("features", [])
    weights = data.get("weights", {"impact": 0.4, "reach": 0.3, "confidence": 0.2, "effort": -0.1})
    company = data.get("company", "Company")

    results = {
        "timestamp": datetime.now().isoformat(),
        "company": company,
        "method": method,
        "feature_count": len(features),
        "ranked_features": [],
        "by_category": {},
        "anomalies": [],
        "summary": {},
    }

    scored_features = []
    for f in features:
        entry = {
            "name": f.get("name", "Unnamed"),
            "category": f.get("category", "uncategorized"),
            "reach": f.get("reach", 1),
            "impact": f.get("impact", 1),
            "confidence": f.get("confidence", 100),
            "effort": f.get("effort", 1),
            "owner": f.get("owner", "Unassigned"),
            "source": f.get("source", "unknown"),
        }

        if method == "rice":
            entry["score"] = score_rice(f)
        elif method == "ice":
            entry["score"] = score_ice(f)
        elif method == "weighted":
            entry["score"] = score_weighted(f, weights)
        else:
            entry["score"] = score_rice(f)

        scored_features.append(entry)

    # Sort by score descending
    scored_features.sort(key=lambda x: x["score"], reverse=True)

    # Add rank
    for idx, f in enumerate(scored_features, 1):
        f["rank"] = idx

    results["ranked_features"] = scored_features

    # Group by category
    categories = {}
    for f in scored_features:
        cat = f["category"]
        if cat not in categories:
            categories[cat] = {"features": [], "total_effort": 0, "avg_score": 0}
        categories[cat]["features"].append(f["name"])
        categories[cat]["total_effort"] += f["effort"]

    for cat, info in categories.items():
        cat_features = [f for f in scored_features if f["category"] == cat]
        info["avg_score"] = round(sum(f["score"] for f in cat_features) / max(len(cat_features), 1), 1)
        info["count"] = len(cat_features)
    results["by_category"] = categories

    # Detect anomalies
    results["anomalies"] = detect_anomalies(scored_features, method)

    # Summary
    if scored_features:
        results["summary"] = {
            "highest_score": scored_features[0]["score"],
            "lowest_score": scored_features[-1]["score"],
            "avg_score": round(sum(f["score"] for f in scored_features) / len(scored_features), 1),
            "total_effort": sum(f["effort"] for f in scored_features),
            "top_5_effort": sum(f["effort"] for f in scored_features[:5]),
            "anomaly_count": len(results["anomalies"]),
            "categories": len(categories),
        }

    return results


def format_text(results):
    lines = [
        "=" * 60,
        f"FEATURE PRIORITIZATION ({results['method'].upper()})",
        "=" * 60,
        f"Company: {results['company']}",
        f"Features: {results['feature_count']}",
        f"Method: {results['method']}",
        f"Analysis Date: {results['timestamp'][:10]}",
        "",
        "RANKED BACKLOG",
    ]

    for f in results["ranked_features"]:
        lines.append(
            f"  #{f['rank']}. {f['name']} (score: {f['score']})"
        )
        lines.append(
            f"       Reach={f['reach']}, Impact={f['impact']}, "
            f"Confidence={f['confidence']}%, Effort={f['effort']} | "
            f"Category: {f['category']} | Owner: {f['owner']}"
        )

    if results["by_category"]:
        lines.append("")
        lines.append("BY CATEGORY")
        for cat, info in sorted(results["by_category"].items(), key=lambda x: x[1]["avg_score"], reverse=True):
            lines.append(f"  {cat}: {info['count']} features, avg score={info['avg_score']}, total effort={info['total_effort']}")

    if results["anomalies"]:
        lines.append("")
        lines.append("ANOMALIES DETECTED")
        for a in results["anomalies"]:
            lines.append(f"  [{a['type']}] {a['feature']}: {a['issue']}")

    if results["summary"]:
        lines.append("")
        lines.append("SUMMARY")
        s = results["summary"]
        lines.append(f"  Score range: {s['lowest_score']} - {s['highest_score']} (avg: {s['avg_score']})")
        lines.append(f"  Total effort: {s['total_effort']} | Top 5 effort: {s['top_5_effort']}")
        lines.append(f"  Anomalies: {s['anomaly_count']} | Categories: {s['categories']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Prioritize features using RICE, ICE, or weighted scoring")
    parser.add_argument("--input", required=True, help="Path to JSON features data file")
    parser.add_argument("--method", choices=["rice", "ice", "weighted"], default="rice", help="Scoring method")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = prioritize_features(data, args.method)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
