#!/usr/bin/env python3
"""Lead Scoring Simulator - Simulate and validate lead scoring models.

Scores leads based on demographic fit and behavioral signals, validates
model effectiveness against actual outcomes, and tunes thresholds.

Usage:
    python lead_scoring_simulator.py leads.json
    python lead_scoring_simulator.py leads.json --model scoring_model.json --json
    python lead_scoring_simulator.py --demo
"""

import argparse
import json
import sys


DEFAULT_MODEL = {
    "demographic": {
        "title_match": {"values": ["vp", "director", "head", "manager", "lead", "chief"], "score": 20},
        "company_size_fit": {"min": 50, "max": 5000, "score": 15},
        "industry_fit": {"values": ["saas", "technology", "fintech", "software"], "score": 15},
    },
    "behavioral": {
        "pricing_page_visit": {"score": 25},
        "demo_requested": {"score": 30},
        "case_study_viewed": {"score": 15},
        "emails_opened_3plus": {"score": 10},
        "content_downloaded": {"score": 10},
        "webinar_attended": {"score": 15},
        "trial_started": {"score": 30},
        "feature_used": {"score": 20},
    },
    "negative": {
        "competitor_employee": {"score": -50},
        "student_email": {"score": -40},
        "unsubscribed": {"score": -30},
        "bounced_email": {"score": -20},
    },
    "thresholds": {
        "hot": 76,
        "sql": 51,
        "mql": 26,
        "nurture": 0,
    },
}


def score_lead(lead, model=None):
    """Score a single lead against the scoring model."""
    if model is None:
        model = DEFAULT_MODEL

    total_score = 0
    scoring_details = []

    # Demographic scoring
    for signal, config in model.get("demographic", {}).items():
        lead_value = lead.get(signal)
        if lead_value is None:
            continue

        matched = False
        if "values" in config:
            if isinstance(lead_value, str):
                matched = any(v.lower() in lead_value.lower() for v in config["values"])
            elif isinstance(lead_value, bool):
                matched = lead_value
        elif "min" in config and "max" in config:
            try:
                val = float(lead_value)
                matched = config["min"] <= val <= config["max"]
            except (ValueError, TypeError):
                pass

        if matched:
            total_score += config["score"]
            scoring_details.append({
                "signal": signal,
                "type": "demographic",
                "score": config["score"],
                "value": lead_value,
            })

    # Behavioral scoring
    for signal, config in model.get("behavioral", {}).items():
        lead_value = lead.get(signal, False)
        if lead_value:
            total_score += config["score"]
            scoring_details.append({
                "signal": signal,
                "type": "behavioral",
                "score": config["score"],
            })

    # Negative signals
    for signal, config in model.get("negative", {}).items():
        lead_value = lead.get(signal, False)
        if lead_value:
            total_score += config["score"]
            scoring_details.append({
                "signal": signal,
                "type": "negative",
                "score": config["score"],
            })

    # Determine segment
    thresholds = model.get("thresholds", DEFAULT_MODEL["thresholds"])
    if total_score >= thresholds.get("hot", 76):
        segment = "hot"
    elif total_score >= thresholds.get("sql", 51):
        segment = "sql"
    elif total_score >= thresholds.get("mql", 26):
        segment = "mql"
    else:
        segment = "nurture"

    return {
        "lead": lead.get("name", lead.get("email", "Unknown")),
        "total_score": total_score,
        "segment": segment,
        "details": scoring_details,
        "demographic_score": sum(d["score"] for d in scoring_details if d["type"] == "demographic"),
        "behavioral_score": sum(d["score"] for d in scoring_details if d["type"] == "behavioral"),
        "negative_score": sum(d["score"] for d in scoring_details if d["type"] == "negative"),
    }


def simulate_scoring(leads, model=None):
    """Score all leads and generate distribution analysis."""
    results = [score_lead(lead, model) for lead in leads]

    # Segment distribution
    segments = {"hot": 0, "sql": 0, "mql": 0, "nurture": 0}
    for r in results:
        segments[r["segment"]] = segments.get(r["segment"], 0) + 1

    # Score distribution
    scores = [r["total_score"] for r in results]
    avg_score = sum(scores) / max(len(scores), 1)
    min_score = min(scores) if scores else 0
    max_score = max(scores) if scores else 0

    # Validation against outcomes (if available)
    validation = None
    leads_with_outcome = [l for l in leads if "converted" in l]
    if leads_with_outcome:
        scored_with_outcome = []
        for lead in leads_with_outcome:
            result = score_lead(lead, model)
            result["actual_converted"] = lead["converted"]
            scored_with_outcome.append(result)

        # Check if high scores correlate with conversions
        high_scored = [s for s in scored_with_outcome if s["segment"] in ("hot", "sql")]
        low_scored = [s for s in scored_with_outcome if s["segment"] in ("mql", "nurture")]

        high_conversion = (
            sum(1 for s in high_scored if s["actual_converted"]) / max(len(high_scored), 1) * 100
        )
        low_conversion = (
            sum(1 for s in low_scored if s["actual_converted"]) / max(len(low_scored), 1) * 100
        )

        validation = {
            "leads_with_outcome": len(leads_with_outcome),
            "high_score_conversion_rate": round(high_conversion, 1),
            "low_score_conversion_rate": round(low_conversion, 1),
            "model_effective": high_conversion > low_conversion,
            "lift": round(high_conversion / max(low_conversion, 0.1), 1),
        }

    results.sort(key=lambda x: x["total_score"], reverse=True)

    return {
        "total_leads": len(leads),
        "segments": segments,
        "score_stats": {
            "average": round(avg_score, 1),
            "min": min_score,
            "max": max_score,
        },
        "leads": results,
        "validation": validation,
        "segment_percentages": {
            seg: round(count / max(len(leads), 1) * 100, 1)
            for seg, count in segments.items()
        },
    }


def get_demo_data():
    return [
        {"name": "Alice VP", "title_match": "VP of Marketing", "company_size_fit": 200, "industry_fit": "saas", "pricing_page_visit": True, "demo_requested": True, "emails_opened_3plus": True, "converted": True},
        {"name": "Bob Manager", "title_match": "Product Manager", "company_size_fit": 500, "industry_fit": "technology", "case_study_viewed": True, "content_downloaded": True, "converted": True},
        {"name": "Carol Dev", "title_match": "Developer", "company_size_fit": 100, "industry_fit": "saas", "trial_started": True, "feature_used": True, "converted": False},
        {"name": "Dan Student", "title_match": "Student", "company_size_fit": 5, "student_email": True, "content_downloaded": True, "converted": False},
        {"name": "Eve Director", "title_match": "Director of Ops", "company_size_fit": 1000, "industry_fit": "fintech", "pricing_page_visit": True, "webinar_attended": True, "demo_requested": True, "converted": True},
        {"name": "Frank Lead", "title_match": "Team Lead", "company_size_fit": 80, "industry_fit": "retail", "emails_opened_3plus": True, "converted": False},
    ]


def format_report(analysis):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 65)
    lines.append("LEAD SCORING SIMULATION")
    lines.append("=" * 65)
    lines.append(f"Total Leads: {analysis['total_leads']}")
    lines.append(f"Avg Score:   {analysis['score_stats']['average']}")
    lines.append(f"Range:       {analysis['score_stats']['min']} to {analysis['score_stats']['max']}")
    lines.append("")

    # Segment distribution
    lines.append("--- SEGMENT DISTRIBUTION ---")
    for seg in ["hot", "sql", "mql", "nurture"]:
        count = analysis["segments"].get(seg, 0)
        pct = analysis["segment_percentages"].get(seg, 0)
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        lines.append(f"  {seg.upper():<8} [{bar}] {count:>4} ({pct:.0f}%)")
    lines.append("")

    # Top leads
    lines.append("--- LEAD SCORES ---")
    lines.append(f"{'Lead':<20} {'Score':>6} {'Demo':>5} {'Behav':>5} {'Neg':>5} {'Segment':>8}")
    lines.append("-" * 55)
    for lead in analysis["leads"]:
        lines.append(
            f"{lead['lead']:<20} {lead['total_score']:>6} {lead['demographic_score']:>5} "
            f"{lead['behavioral_score']:>5} {lead['negative_score']:>5} {lead['segment']:>8}"
        )
    lines.append("")

    # Validation
    if analysis["validation"]:
        v = analysis["validation"]
        lines.append("--- MODEL VALIDATION ---")
        lines.append(f"  High-score conversion: {v['high_score_conversion_rate']:.0f}%")
        lines.append(f"  Low-score conversion:  {v['low_score_conversion_rate']:.0f}%")
        lines.append(f"  Lift:                  {v['lift']:.1f}x")
        lines.append(f"  Model effective:       {'Yes' if v['model_effective'] else 'No'}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Simulate and validate lead scoring models")
    parser.add_argument("input", nargs="?", help="JSON file with lead data")
    parser.add_argument("--model", help="Custom scoring model JSON")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    model = None
    if args.model:
        with open(args.model, "r") as f:
            model = json.load(f)

    if args.demo:
        leads = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            leads = data if isinstance(data, list) else data.get("leads", [])
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = simulate_scoring(leads, model)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
