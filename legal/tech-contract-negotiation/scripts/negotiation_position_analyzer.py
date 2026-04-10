#!/usr/bin/env python3
"""
Negotiation Position Analyzer

Analyzes contract text and classifies each provision as provider-favorable,
balanced, or client-favorable based on keyword patterns and structural analysis.
Generates a position map and recommended negotiation priorities.

Usage:
    python negotiation_position_analyzer.py contract_draft.txt
    python negotiation_position_analyzer.py contract_draft.txt --json
    python negotiation_position_analyzer.py contract_draft.txt --perspective client
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


# Provision detection patterns: (provision_name, section_patterns)
PROVISION_PATTERNS: Dict[str, List[str]] = {
    "liability": [
        r"(?i)\bliabilit(?:y|ies)\b", r"(?i)\bindemnif(?:y|ication|ied)\b",
        r"(?i)\blimit(?:ation)?\s+of\s+liability\b", r"(?i)\bdamages?\b",
        r"(?i)\bcap\s+on\s+(?:liability|damages)\b",
    ],
    "ip_ownership": [
        r"(?i)\bintellectual\s+property\b", r"(?i)\b(?:ip|i\.p\.)\s+(?:rights|ownership)\b",
        r"(?i)\bwork\s+product\b", r"(?i)\bdeliverables?\s+ownership\b",
        r"(?i)\bbackground\s+ip\b", r"(?i)\bforeground\s+ip\b",
        r"(?i)\blicen[cs]e\s+(?:grant|back)\b",
    ],
    "payment_terms": [
        r"(?i)\bpayment\s+terms?\b", r"(?i)\bnet\s+\d+\b", r"(?i)\binvoic(?:e|ing)\b",
        r"(?i)\bmilestone\s+payment\b", r"(?i)\bpayment\s+schedule\b",
        r"(?i)\blate\s+(?:payment|fee)\b", r"(?i)\bprice\s+(?:increase|escalation)\b",
    ],
    "sla": [
        r"(?i)\bservice\s+level\b", r"(?i)\bsla\b", r"(?i)\buptime\b",
        r"(?i)\bavailabilit(?:y|ies)\b", r"(?i)\bservice\s+credit\b",
        r"(?i)\bresponse\s+time\b", r"(?i)\bresolution\s+time\b",
    ],
    "warranties": [
        r"(?i)\bwarrant(?:y|ies|s)\b", r"(?i)\brepresentation(?:s)?\b",
        r"(?i)\bas[- ]is\b", r"(?i)\bdisclaimer\b",
        r"(?i)\bfitness\s+for\s+(?:a\s+)?particular\s+purpose\b",
        r"(?i)\bmerchantabilit(?:y|ies)\b",
    ],
}

# Position indicators: keyword -> (score_delta, explanation)
# Negative = provider-favorable, Positive = client-favorable
POSITION_INDICATORS: Dict[str, List[Tuple[str, float, str]]] = {
    "liability": [
        (r"(?i)\bunlimited\s+liabilit", 2.0, "Unlimited liability favors client"),
        (r"(?i)\bcap(?:ped)?\s+at\s+(?:the\s+)?fees?\s+paid", -1.5, "Liability capped at fees paid favors provider"),
        (r"(?i)\b(?:12|twelve)\s+months?\s+(?:of\s+)?fees", -1.0, "12-month fee cap is moderately provider-favorable"),
        (r"(?i)\b(?:24|twenty.?four)\s+months?\s+(?:of\s+)?fees", 0.0, "24-month fee cap is balanced"),
        (r"(?i)\bexclud(?:e|es|ing)\s+(?:indirect|consequential|special|incidental)", -1.5, "Excluding indirect damages favors provider"),
        (r"(?i)\bindirect\s+(?:and\s+)?consequential\s+damages?\s+(?:are\s+)?(?:included|recoverable)", 1.5, "Including indirect damages favors client"),
        (r"(?i)\bmutual\s+indemnif", 0.0, "Mutual indemnification is balanced"),
        (r"(?i)\bprovider\s+(?:shall\s+)?indemnif", 1.0, "Provider-only indemnification favors client"),
        (r"(?i)\bclient\s+(?:shall\s+)?indemnif", -1.0, "Client-only indemnification favors provider"),
        (r"(?i)\bsuper[- ]?cap\b", 1.0, "Super-cap for specific claims favors client"),
        (r"(?i)\bcarve[- ]?out", 0.5, "Carve-outs from liability cap favor client"),
    ],
    "ip_ownership": [
        (r"(?i)\bclient\s+(?:shall\s+)?own\s+all", 2.0, "Client owns all IP favors client"),
        (r"(?i)\bprovider\s+(?:shall\s+)?(?:retain|own)\s+all", -2.0, "Provider retains all IP favors provider"),
        (r"(?i)\bjoint\s+ownership", 0.0, "Joint IP ownership is balanced"),
        (r"(?i)\bwork\s+(?:made\s+)?for\s+hire", 1.5, "Work-for-hire favors client"),
        (r"(?i)\blicen[cs]e\s+back\s+to\s+(?:the\s+)?provider", -0.5, "License-back to provider is moderately provider-favorable"),
        (r"(?i)\bperpetual.*\blicen[cs]e\s+to\s+(?:the\s+)?client", 1.0, "Perpetual license to client favors client"),
        (r"(?i)\bnon[- ]?exclusive\s+licen[cs]e", -0.5, "Non-exclusive license is moderately provider-favorable"),
        (r"(?i)\bexclusive\s+licen[cs]e", 1.5, "Exclusive license favors client"),
        (r"(?i)\bassignment\s+of\s+(?:all\s+)?(?:ip|intellectual)", 1.5, "IP assignment favors client"),
        (r"(?i)\bbackground\s+ip\s+(?:remains|retained)", 0.0, "Background IP retained is standard/balanced"),
    ],
    "payment_terms": [
        (r"(?i)\bnet\s+15\b", -1.0, "Net 15 payment favors provider"),
        (r"(?i)\bnet\s+30\b", 0.0, "Net 30 is standard/balanced"),
        (r"(?i)\bnet\s+45\b", 0.5, "Net 45 favors client"),
        (r"(?i)\bnet\s+60\b", 1.5, "Net 60 strongly favors client"),
        (r"(?i)\bnet\s+90\b", 2.0, "Net 90 strongly favors client"),
        (r"(?i)\b(?:advance|upfront)\s+payment", -1.5, "Upfront payment favors provider"),
        (r"(?i)\bmilestone[- ]?based\s+payment", 0.5, "Milestone-based payment favors client"),
        (r"(?i)\bprice\s+(?:increase|escalation)\s+(?:cap|limit)", 1.0, "Price increase cap favors client"),
        (r"(?i)\b(?:annual|yearly)\s+(?:price\s+)?increase", -0.5, "Annual price increase favors provider"),
        (r"(?i)\bright\s+to\s+(?:withhold|offset|set[- ]?off)", 1.0, "Right to withhold payment favors client"),
        (r"(?i)\blate\s+(?:payment\s+)?(?:fee|interest|penalty)", -0.5, "Late payment penalties favor provider"),
        (r"(?i)\bmost[- ]?favou?red[- ]?(?:customer|nation)", 1.5, "MFN pricing favors client"),
    ],
    "sla": [
        (r"(?i)\b99\.9{2,}%?\s+(?:uptime|availability)", 1.5, "99.99%+ uptime commitment favors client"),
        (r"(?i)\b99\.9%?\s+(?:uptime|availability)", 0.5, "99.9% uptime is moderately client-favorable"),
        (r"(?i)\b99\.?5?%?\s+(?:uptime|availability)", -0.5, "99.5% or lower uptime favors provider"),
        (r"(?i)\bservice\s+credit(?:s)?\s+(?:up\s+to\s+)?(?:\d+%|100%)", 1.0, "Service credits favor client"),
        (r"(?i)\b(?:sole|exclusive)\s+remed(?:y|ies)", -1.0, "Service credits as sole remedy favors provider"),
        (r"(?i)\btermination\s+(?:right|for)\s+(?:repeated\s+)?(?:sla|service\s+level)\s+(?:failure|breach)", 1.5, "Termination for SLA failure favors client"),
        (r"(?i)\bexclud(?:e|es|ing)\s+(?:scheduled\s+)?maintenance", -0.5, "Excluding maintenance windows favors provider"),
        (r"(?i)\broot\s+cause\s+analysis", 0.5, "Root cause analysis requirement favors client"),
        (r"(?i)\b(?:financial\s+)?penalt(?:y|ies)", 1.0, "Financial penalties for SLA breach favor client"),
    ],
    "warranties": [
        (r"(?i)\bas[- ]is\b.*\bno\s+warrant", -2.0, "As-is/no warranty strongly favors provider"),
        (r"(?i)\bdisclaim(?:s|er|ed)?\s+(?:all\s+)?(?:other\s+)?warrant", -1.5, "Warranty disclaimer favors provider"),
        (r"(?i)\bwarrant(?:s|ies)?\s+(?:that\s+)?(?:the\s+)?(?:services?|deliverables?)\s+(?:shall|will)\s+(?:conform|comply)", 1.0, "Conformity warranty favors client"),
        (r"(?i)\b(?:12|twelve|1[- ]?year)\s+warrant(?:y|ies)", 0.0, "12-month warranty is standard/balanced"),
        (r"(?i)\b(?:24|twenty.?four|2[- ]?year)\s+warrant(?:y|ies)", 0.5, "24-month warranty favors client"),
        (r"(?i)\b(?:90|ninety)\s+day\s+warrant(?:y|ies)", -1.0, "90-day warranty favors provider"),
        (r"(?i)\bfitness\s+for\s+(?:a\s+)?particular\s+purpose", 1.0, "Fitness for particular purpose warranty favors client"),
        (r"(?i)\bmerchantabilit(?:y|ies)", 0.5, "Merchantability warranty favors client"),
        (r"(?i)\bre[- ]?perform(?:ance)?\s+(?:at\s+)?(?:no\s+)?(?:additional\s+)?(?:cost|charge)", 1.0, "Re-performance at no cost favors client"),
    ],
}


def extract_sections(text: str) -> Dict[str, str]:
    """Extract text sections relevant to each provision type."""
    sections: Dict[str, str] = {}
    lines = text.split("\n")

    for provision, patterns in PROVISION_PATTERNS.items():
        relevant_lines: List[str] = []
        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    start = max(0, i - 2)
                    end = min(len(lines), i + 15)
                    relevant_lines.extend(lines[start:end])
                    break
        sections[provision] = "\n".join(relevant_lines) if relevant_lines else ""

    return sections


def analyze_provision(provision: str, text: str) -> Dict[str, Any]:
    """Analyze a single provision and return position assessment."""
    if not text.strip():
        return {
            "provision": provision,
            "detected": False,
            "position": "not_found",
            "score": 0.0,
            "indicators": [],
            "recommendation": f"No {provision.replace('_', ' ')} provisions detected. Review manually.",
        }

    indicators = POSITION_INDICATORS.get(provision, [])
    found_indicators: List[Dict[str, Any]] = []
    total_score = 0.0

    for pattern, score, explanation in indicators:
        matches = re.findall(pattern, text)
        if matches:
            found_indicators.append({
                "pattern": explanation,
                "score": score,
                "matches": len(matches),
            })
            total_score += score

    # Normalize score to -3 to +3 range
    if found_indicators:
        avg_score = total_score / len(found_indicators)
    else:
        avg_score = 0.0

    # Classify position
    if avg_score <= -0.75:
        position = "provider-favorable"
    elif avg_score >= 0.75:
        position = "client-favorable"
    else:
        position = "balanced"

    # Generate recommendation
    recommendations = {
        "provider-favorable": f"Push for balanced or client-favorable {provision.replace('_', ' ')} terms. High negotiation priority.",
        "balanced": f"Current {provision.replace('_', ' ')} terms are reasonable. Low negotiation priority unless strategic.",
        "client-favorable": f"Current {provision.replace('_', ' ')} terms favor client. Protect these in negotiation.",
    }

    return {
        "provision": provision,
        "detected": True,
        "position": position,
        "score": round(avg_score, 2),
        "indicators": found_indicators,
        "recommendation": recommendations[position],
    }


def generate_position_map(results: List[Dict[str, Any]], perspective: str) -> Dict[str, Any]:
    """Generate overall position map and negotiation priorities."""
    detected = [r for r in results if r["detected"]]
    not_detected = [r for r in results if not r["detected"]]

    if not detected:
        return {
            "overall_position": "indeterminate",
            "overall_score": 0.0,
            "distribution": {"provider-favorable": 0, "balanced": 0, "client-favorable": 0, "not_found": len(results)},
            "priorities": ["Unable to analyze -- no recognized provisions found. Verify the input contains contract language."],
            "provisions": results,
        }

    distribution = {"provider-favorable": 0, "balanced": 0, "client-favorable": 0, "not_found": len(not_detected)}
    scores: List[float] = []

    for r in detected:
        distribution[r["position"]] += 1
        scores.append(r["score"])

    avg_score = sum(scores) / len(scores) if scores else 0.0

    if avg_score <= -0.5:
        overall = "provider-favorable"
    elif avg_score >= 0.5:
        overall = "client-favorable"
    else:
        overall = "balanced"

    # Flip perspective if analyzing from provider side
    if perspective == "provider":
        flip = {"provider-favorable": "client-favorable", "client-favorable": "provider-favorable", "balanced": "balanced"}
        overall = flip.get(overall, overall)

    # Generate priorities: sort by how far from client-favorable (from client perspective)
    priority_order = sorted(detected, key=lambda r: r["score"])
    priorities: List[str] = []
    for r in priority_order:
        if r["position"] == "provider-favorable":
            priorities.append(f"HIGH: {r['provision'].replace('_', ' ').title()} -- currently {r['position']} (score: {r['score']})")
        elif r["position"] == "balanced":
            priorities.append(f"LOW: {r['provision'].replace('_', ' ').title()} -- currently {r['position']} (score: {r['score']})")

    if not_detected:
        for r in not_detected:
            priorities.append(f"REVIEW: {r['provision'].replace('_', ' ').title()} -- not detected in contract text")

    return {
        "overall_position": overall,
        "overall_score": round(avg_score, 2),
        "distribution": distribution,
        "priorities": priorities,
        "provisions": results,
    }


def format_text_output(position_map: Dict[str, Any], perspective: str) -> str:
    """Format position map as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 70)
    lines.append("NEGOTIATION POSITION ANALYSIS")
    lines.append(f"Perspective: {perspective.upper()}")
    lines.append("=" * 70)
    lines.append("")

    lines.append(f"Overall Position: {position_map['overall_position'].upper()}")
    lines.append(f"Overall Score:    {position_map['overall_score']:+.2f}  (range: -3.0 provider to +3.0 client)")
    lines.append("")

    dist = position_map["distribution"]
    lines.append("Position Distribution:")
    lines.append(f"  Provider-Favorable: {dist['provider-favorable']}")
    lines.append(f"  Balanced:           {dist['balanced']}")
    lines.append(f"  Client-Favorable:   {dist['client-favorable']}")
    lines.append(f"  Not Found:          {dist['not_found']}")
    lines.append("")

    lines.append("-" * 70)
    lines.append("PROVISION DETAILS")
    lines.append("-" * 70)

    for prov in position_map["provisions"]:
        lines.append("")
        name = prov["provision"].replace("_", " ").title()
        if not prov["detected"]:
            lines.append(f"  {name}: NOT DETECTED")
            lines.append(f"    -> {prov['recommendation']}")
            continue

        pos_display = prov["position"].upper()
        lines.append(f"  {name}: {pos_display} (score: {prov['score']:+.2f})")
        for ind in prov["indicators"]:
            marker = "+" if ind["score"] >= 0 else "-"
            lines.append(f"    [{marker}] {ind['pattern']}")
        lines.append(f"    -> {prov['recommendation']}")

    lines.append("")
    lines.append("-" * 70)
    lines.append("NEGOTIATION PRIORITIES")
    lines.append("-" * 70)
    for i, priority in enumerate(position_map["priorities"], 1):
        lines.append(f"  {i}. {priority}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze contract text and classify provisions by negotiation position."
    )
    parser.add_argument("input_file", help="Path to contract text file (.txt or .md)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument(
        "--perspective", choices=["provider", "client"], default="client",
        help="Analysis perspective (default: client)"
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r", encoding="utf-8") as f:
            contract_text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    if len(contract_text.strip()) < 50:
        print("Error: Input file appears too short to contain contract language.", file=sys.stderr)
        sys.exit(1)

    # Extract and analyze each provision
    sections = extract_sections(contract_text)
    results: List[Dict[str, Any]] = []

    for provision in PROVISION_PATTERNS:
        result = analyze_provision(provision, sections[provision])
        results.append(result)

    # Generate position map
    position_map = generate_position_map(results, args.perspective)

    if args.json:
        print(json.dumps(position_map, indent=2))
    else:
        print(format_text_output(position_map, args.perspective))


if __name__ == "__main__":
    main()
