#!/usr/bin/env python3
"""
Legal Risk Report Generator

Generates a formatted risk assessment memo in markdown from a risk register
JSON file. Includes risk matrix visualization, distribution summary,
top risks, recommended actions, and monitoring plan.

Usage:
    python risk_report_generator.py --input risk_register.json
    python risk_report_generator.py --input risk_register.json --output memo.md
    python risk_report_generator.py --input risk_register.json --json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


SEVERITY_LABELS: Dict[int, str] = {1: "Negligible", 2: "Minor", 3: "Moderate", 4: "Major", 5: "Critical"}
LIKELIHOOD_LABELS: Dict[int, str] = {1: "Remote", 2: "Unlikely", 3: "Possible", 4: "Likely", 5: "Almost Certain"}
ACTIONS: Dict[str, str] = {"GREEN": "Accept and document. Monitor quarterly.", "YELLOW": "Assign owner. Implement controls. Review monthly.", "ORANGE": "Escalate to senior counsel. Develop contingency plan. Consider outside counsel.", "RED": "Immediate escalation. Assemble response team. Engage outside counsel. Report to board."}
MONITORING: Dict[str, str] = {"GREEN": "Quarterly review", "YELLOW": "Monthly review", "ORANGE": "Bi-weekly review", "RED": "Weekly review (daily during active response)"}


def get_risk_level(score: int) -> str:
    """Return risk level color based on score."""
    if score <= 4: return "GREEN"
    elif score <= 9: return "YELLOW"
    elif score <= 15: return "ORANGE"
    return "RED"


def get_action(level: str) -> str:
    return ACTIONS.get(level, "Unknown")


def get_monitoring_frequency(level: str) -> str:
    return MONITORING.get(level, "Unknown")


def load_register(filepath: str) -> List[Dict[str, Any]]:
    """Load risk register from JSON file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if isinstance(data, dict) and "risks" in data:
        return data["risks"]
    elif isinstance(data, list):
        return data
    else:
        print("Error: Expected 'risks' array or top-level array", file=sys.stderr)
        sys.exit(1)


def enrich_risks(risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate scores and levels for each risk."""
    enriched: List[Dict[str, Any]] = []
    for risk in risks:
        sev: int = risk.get("severity", 1)
        lik: int = risk.get("likelihood", 1)
        score: int = sev * lik
        level: str = get_risk_level(score)
        enriched.append({
            **risk,
            "score": score,
            "level": level,
            "action": get_action(level),
            "monitoring": get_monitoring_frequency(level),
            "severity_label": SEVERITY_LABELS.get(sev, "Unknown"),
            "likelihood_label": LIKELIHOOD_LABELS.get(lik, "Unknown"),
        })
    enriched.sort(key=lambda r: r["score"], reverse=True)
    return enriched


def build_matrix(risks: List[Dict[str, Any]]) -> str:
    """Build ASCII risk matrix showing risk counts per cell."""
    cell_counts: Dict[tuple, int] = {}
    for risk in risks:
        key = (risk["severity"], risk["likelihood"])
        cell_counts[key] = cell_counts.get(key, 0) + 1
    lines: List[str] = ["```", "         L=1    L=2    L=3    L=4    L=5"]
    for sev in range(5, 0, -1):
        row: List[str] = []
        for lik in range(1, 6):
            score = sev * lik
            level = get_risk_level(score)[0]  # G/Y/O/R
            count = cell_counts.get((sev, lik), 0)
            cell = f"{count}x" if count > 0 else f" {level}"
            row.append(f"{score:>2d}({cell})")
        lines.append(f"  S={sev}  {'  '.join(row)}")
    lines.append("  Legend: G=GREEN Y=YELLOW O=ORANGE R=RED  Nx=risk count")
    lines.append("```")
    return "\n".join(lines)


def build_distribution(risks: List[Dict[str, Any]]) -> str:
    """Build risk distribution summary table."""
    dist: Dict[str, int] = {"RED": 0, "ORANGE": 0, "YELLOW": 0, "GREEN": 0}
    for risk in risks:
        dist[risk["level"]] += 1

    total: int = len(risks)
    lines: List[str] = [
        "| Level | Count | Percentage | Action Required |",
        "|-------|-------|------------|-----------------|",
    ]
    for level in ["RED", "ORANGE", "YELLOW", "GREEN"]:
        count = dist[level]
        pct = round(100 * count / total, 1) if total > 0 else 0.0
        action = get_action(level).split(".")[0] + "."
        lines.append(f"| {level} | {count} | {pct}% | {action} |")

    lines.append(f"| **Total** | **{total}** | **100%** | |")
    return "\n".join(lines)


def build_top_risks(risks: List[Dict[str, Any]], limit: int = 10) -> str:
    """Build top risks table."""
    top = risks[:limit]
    lines: List[str] = [
        "| # | Score | Level | Category | Description | Action |",
        "|---|-------|-------|----------|-------------|--------|",
    ]
    for i, risk in enumerate(top, 1):
        desc = risk.get("description", "N/A")
        if len(desc) > 50:
            desc = desc[:47] + "..."
        lines.append(
            f"| {i} | {risk['score']} | {risk['level']} | "
            f"{risk.get('category', 'N/A')} | {desc} | {risk['action'].split('.')[0]}. |"
        )
    return "\n".join(lines)


def build_monitoring_plan(risks: List[Dict[str, Any]]) -> str:
    """Build monitoring plan section."""
    lines: List[str] = [
        "| Risk Level | Review Frequency | Responsible | Reporting |",
        "|------------|-----------------|-------------|-----------|",
        "| RED | Weekly (daily during active response) | General Counsel / Outside Counsel | Board + Executive Team |",
        "| ORANGE | Bi-weekly | Senior Counsel | Legal Leadership |",
        "| YELLOW | Monthly | Assigned Risk Owner | Legal Team |",
        "| GREEN | Quarterly | Legal Operations | Internal Log |",
    ]
    return "\n".join(lines)


def build_category_summary(risks: List[Dict[str, Any]]) -> str:
    """Build category breakdown table."""
    cats: Dict[str, Dict[str, Any]] = {}
    for risk in risks:
        cat = risk.get("category", "Other")
        if cat not in cats:
            cats[cat] = {"count": 0, "total_score": 0, "max_score": 0}
        cats[cat]["count"] += 1
        cats[cat]["total_score"] += risk["score"]
        cats[cat]["max_score"] = max(cats[cat]["max_score"], risk["score"])

    sorted_cats = sorted(cats.items(), key=lambda x: x[1]["max_score"], reverse=True)
    lines: List[str] = [
        "| Category | Count | Avg Score | Max Score |",
        "|----------|-------|-----------|-----------|",
    ]
    for cat, data in sorted_cats:
        avg = round(data["total_score"] / data["count"], 1)
        lines.append(f"| {cat} | {data['count']} | {avg} | {data['max_score']} |")
    return "\n".join(lines)


def generate_memo(risks: List[Dict[str, Any]]) -> str:
    """Generate the full risk assessment memo in markdown."""
    now = datetime.now().strftime("%Y-%m-%d")
    enriched = enrich_risks(risks)

    scores = [r["score"] for r in enriched]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    max_score = max(scores) if scores else 0

    sections: List[str] = []

    # Header
    sections.append(f"# Legal Risk Assessment Memo\n")
    sections.append(f"**Date:** {now}  ")
    sections.append(f"**Total Risks:** {len(enriched)}  ")
    sections.append(f"**Average Score:** {avg_score}  ")
    sections.append(f"**Highest Score:** {max_score}  ")
    sections.append("")

    # Executive Summary
    red_count = sum(1 for r in enriched if r["level"] == "RED")
    orange_count = sum(1 for r in enriched if r["level"] == "ORANGE")
    sections.append("## 1. Executive Summary\n")
    if red_count > 0:
        sections.append(f"**CRITICAL:** {red_count} RED-level risk(s) require immediate escalation and response team activation.\n")
    if orange_count > 0:
        sections.append(f"**ATTENTION:** {orange_count} ORANGE-level risk(s) require senior counsel review and contingency planning.\n")
    if red_count == 0 and orange_count == 0:
        sections.append("No RED or ORANGE risks identified. Current risk posture is within acceptable tolerance.\n")

    # Risk Matrix
    sections.append("## 2. Risk Matrix\n")
    sections.append(build_matrix(enriched))
    sections.append("")

    # Distribution
    sections.append("## 3. Risk Distribution\n")
    sections.append(build_distribution(enriched))
    sections.append("")

    # Category Breakdown
    sections.append("## 4. Category Breakdown\n")
    sections.append(build_category_summary(enriched))
    sections.append("")

    # Top Risks
    sections.append("## 5. Top Risks\n")
    sections.append(build_top_risks(enriched))
    sections.append("")

    # Recommended Actions
    sections.append("## 6. Recommended Actions\n")
    for i, risk in enumerate(enriched, 1):
        if risk["level"] in ("RED", "ORANGE"):
            sections.append(f"### Risk {i}: {risk.get('description', 'N/A')}")
            sections.append(f"- **Score:** {risk['score']} ({risk['level']})")
            sections.append(f"- **Category:** {risk.get('category', 'N/A')}")
            sections.append(f"- **Action:** {risk['action']}")
            sections.append(f"- **Monitoring:** {risk['monitoring']}")
            sections.append("")

    # Monitoring Plan
    sections.append("## 7. Monitoring Plan\n")
    sections.append(build_monitoring_plan(enriched))
    sections.append("")

    # Escalation Summary
    sections.append("## 8. Escalation Summary\n")
    if red_count > 0:
        sections.append("- **Outside counsel engagement:** MANDATORY for RED-level risks")
    if orange_count > 0:
        sections.append("- **Senior counsel review:** REQUIRED for ORANGE-level risks")
    sections.append(f"- **Next review date:** Schedule within {'1 week' if red_count > 0 else '2 weeks' if orange_count > 0 else '1 month'}")
    sections.append("")

    # Footer
    sections.append("---\n")
    sections.append(f"*Generated by Legal Risk Report Generator on {now}*")

    return "\n".join(sections)


def generate_json_metadata(risks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate JSON metadata about the report."""
    enriched = enrich_risks(risks)
    dist: Dict[str, int] = {"RED": 0, "ORANGE": 0, "YELLOW": 0, "GREEN": 0}
    for r in enriched:
        dist[r["level"]] += 1

    scores = [r["score"] for r in enriched]
    return {
        "generated": datetime.now().isoformat(),
        "total_risks": len(enriched),
        "distribution": dist,
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "requires_escalation": dist["RED"] > 0,
        "risks": enriched,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Legal Risk Report Generator — generates risk assessment memos"
    )
    parser.add_argument("--input", required=True, help="Path to risk register JSON file")
    parser.add_argument("--output", type=str, help="Save memo to file (markdown)")
    parser.add_argument("--json", action="store_true", help="Output report metadata as JSON")

    args = parser.parse_args()

    risks = load_register(args.input)
    if not risks:
        print("Error: No risks found in input file", file=sys.stderr)
        sys.exit(1)

    if args.json:
        metadata = generate_json_metadata(risks)
        print(json.dumps(metadata, indent=2))
    else:
        memo = generate_memo(risks)
        if args.output:
            Path(args.output).write_text(memo)
            print(f"Memo written to {args.output}")
        else:
            print(memo)


if __name__ == "__main__":
    main()
