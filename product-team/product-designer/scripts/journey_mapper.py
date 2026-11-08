#!/usr/bin/env python3
"""
User Journey Mapper

Creates structured user journey maps from stage definitions.
Identifies pain points, emotional curves, and opportunity areas, and flags
low points in the journey that have no opportunity recorded against them.

Pre-built templates live in references/journey-templates.json.
Uses ONLY Python standard library.

Usage:
    python journey_mapper.py --template saas
    python journey_mapper.py --stages stages.json
    python journey_mapper.py --template ecommerce --format json

Exit codes:
    0  journey mapped, every low point (emotion <= 2) has at least one opportunity
    1  a low point has no opportunity recorded (finding 'unaddressed-low-point')
    2  bad input (missing file, invalid JSON, no stages, emotion score outside 1-5)
"""

import argparse
import json
import os
import sys
from typing import Dict, List

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "journey-templates.json")
LOW_POINT = 2

with open(DATA_PATH, "r", encoding="utf-8") as _f:
    JOURNEY_TEMPLATES = json.load(_f)


class InputError(Exception):
    """Raised for a journey file the mapper cannot read; reported with exit code 2."""


def validate_journey(journey: Dict) -> None:
    """Check the fields the map and metrics depend on."""
    if not isinstance(journey, dict):
        raise InputError("journey file must be a JSON object with 'name', 'persona', 'goal' and 'stages'")
    for key in ("name", "persona", "goal"):
        if not isinstance(journey.get(key), str) or not journey[key].strip():
            raise InputError(f"journey needs a non-empty '{key}'")
    stages = journey.get("stages")
    if not isinstance(stages, list) or not stages:
        raise InputError("journey needs a non-empty 'stages' list")
    for i, stage in enumerate(stages, 1):
        if not isinstance(stage, dict) or not stage.get("name"):
            raise InputError(f"stage {i} needs a 'name'")
        score = (stage.get("emotions") or {}).get("score") if isinstance(stage.get("emotions"), dict) else None
        if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
            raise InputError(f"stage '{stage['name']}': emotions.score must be an integer 1-5, got {score!r}")
        for key in ("actions", "touchpoints", "pain_points", "opportunities"):
            if not isinstance(stage.get(key, []), list):
                raise InputError(f"stage '{stage['name']}': '{key}' must be a list")
        stage.setdefault("actions", [])
        stage.setdefault("touchpoints", [])
        stage["emotions"].setdefault("label", "")


def calculate_journey_metrics(stages: List[Dict]) -> Dict:
    """Calculate journey health metrics."""
    emotion_scores = [s["emotions"]["score"] for s in stages]

    # Find biggest drops
    drops = []
    for i in range(1, len(emotion_scores)):
        diff = emotion_scores[i] - emotion_scores[i - 1]
        if diff < 0:
            drops.append({
                "from_stage": stages[i - 1]["name"],
                "to_stage": stages[i]["name"],
                "drop": abs(diff),
            })

    drops.sort(key=lambda x: -x["drop"])

    all_pain_points = []
    for stage in stages:
        for pp in stage.get("pain_points", []):
            all_pain_points.append({"stage": stage["name"], "pain_point": pp})

    total_opportunities = sum(len(s.get("opportunities", [])) for s in stages)

    return {
        "total_stages": len(stages),
        "avg_emotion_score": round(sum(emotion_scores) / len(emotion_scores), 1),
        "lowest_emotion_stage": stages[emotion_scores.index(min(emotion_scores))]["name"],
        "highest_emotion_stage": stages[emotion_scores.index(max(emotion_scores))]["name"],
        "biggest_drops": drops[:3],
        "total_pain_points": len(all_pain_points),
        "total_opportunities": total_opportunities,
        "critical_stage": stages[emotion_scores.index(min(emotion_scores))]["name"],
    }


def find_gaps(journey: Dict, custom: bool) -> List[Dict]:
    """Findings: low points with no opportunity (fail) or no recorded pain point (warn)."""
    findings = []
    for stage in journey["stages"]:
        if stage["emotions"]["score"] > LOW_POINT:
            continue
        if not stage.get("opportunities"):
            findings.append({"level": "fail", "rule": "unaddressed-low-point", "stage": stage["name"],
                             "message": "emotion is at or below 2 and no opportunity is recorded"})
        if not stage.get("pain_points"):
            findings.append({"level": "warn", "rule": "unexplained-low-point", "stage": stage["name"],
                             "message": "emotion is at or below 2 but no pain point says why"})
    if custom and not journey.get("evidence"):
        findings.append({"level": "warn", "rule": "no-evidence", "stage": None,
                         "message": "no 'evidence' field: name the interviews, tickets or analytics behind this map"})
    return findings


def format_human_output(journey: Dict, metrics: Dict) -> str:
    """Format journey map as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"USER JOURNEY MAP: {journey['name']}")
    lines.append("=" * 60)
    lines.append(f"\n  Persona: {journey['persona']}")
    lines.append(f"  Goal:    {journey['goal']}")
    if journey.get("evidence"):
        lines.append(f"  Evidence: {journey['evidence']}")

    lines.append("\n  EMOTION CURVE")
    lines.append("  " + "-" * 50)
    width = max([15] + [len(s["name"]) for s in journey["stages"]])  # long names keep the bars aligned
    for stage in journey["stages"]:
        score = stage["emotions"]["score"]
        bar = "*" * (score * 6)
        label = stage["emotions"]["label"]
        lines.append(f"  {stage['name']:<{width}} {'|' + bar:<32} {score}/5 - {label}")

    for stage in journey["stages"]:
        lines.append(f"\n  STAGE: {stage['name'].upper()}")
        lines.append("  " + "-" * 40)
        for title, key, mark in (("Actions", "actions", "-"), ("Touchpoints", "touchpoints", "-"),
                                 ("Pain Points", "pain_points", "!"), ("Opportunities", "opportunities", ">")):
            lines.append(f"  {title}:")
            for item in stage.get(key, []):
                lines.append(f"    {mark} {item}")

    lines.append("\n  JOURNEY HEALTH METRICS")
    lines.append("  " + "-" * 50)
    lines.append(f"  Avg emotion score:   {metrics['avg_emotion_score']}/5")
    lines.append(f"  Lowest point:        {metrics['lowest_emotion_stage']}")
    lines.append(f"  Highest point:       {metrics['highest_emotion_stage']}")
    lines.append(f"  Total pain points:   {metrics['total_pain_points']}")
    lines.append(f"  Total opportunities: {metrics['total_opportunities']}")

    if metrics["biggest_drops"]:
        lines.append("\n  BIGGEST EMOTION DROPS (prioritize these transitions)")
        for drop in metrics["biggest_drops"]:
            lines.append(f"    {drop['from_stage']} -> {drop['to_stage']} (dropped {drop['drop']} points)")

    return "\n".join(lines)


def format_findings(findings: List[Dict]) -> str:
    """Text block for gaps; empty when the map has none."""
    if not findings:
        return ""
    lines = ["\n  FINDINGS"]
    for f in findings:
        where = f" [{f['stage']}]" if f["stage"] else ""
        lines.append(f"    {f['level'].upper():<4} {f['rule']}{where}: {f['message']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Create structured user journey maps with emotion curves and opportunity analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python journey_mapper.py --template saas
  python journey_mapper.py --template mobile_app --format json
  python journey_mapper.py --stages my_journey.json

Available templates: saas, ecommerce, mobile_app
Exit codes: 0 mapped, 1 a low point (emotion <= 2) has no opportunity, 2 bad input
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--template", "-t", choices=list(JOURNEY_TEMPLATES.keys()), help="Use pre-built journey template")
    group.add_argument("--stages", "-s", help="Path to custom stages JSON file")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--json", action="store_true", help="Same as --format json")

    args = parser.parse_args()
    as_json = args.json or args.format == "json"

    try:
        if args.template:
            journey = JOURNEY_TEMPLATES[args.template]
        else:
            with open(args.stages, "r", encoding="utf-8") as f:
                journey = json.load(f)
        validate_journey(journey)
    except (OSError, json.JSONDecodeError, InputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    metrics = calculate_journey_metrics(journey["stages"])
    findings = find_gaps(journey, custom=bool(args.stages))

    if as_json:
        output = {"journey": journey, "metrics": metrics}
        if findings:
            output["findings"] = findings
        print(json.dumps(output, indent=2))
    else:
        print(format_human_output(journey, metrics) + format_findings(findings))
    return 1 if any(f["level"] == "fail" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
