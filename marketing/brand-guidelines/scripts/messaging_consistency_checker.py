#!/usr/bin/env python3
"""Messaging Consistency Checker - Check text samples against brand voice standards.

Analyzes text for voice attribute adherence, tone drift, vocabulary violations,
and cross-channel consistency.

Usage:
    python messaging_consistency_checker.py samples.json
    python messaging_consistency_checker.py samples.json --config brand_voice.json --json
    python messaging_consistency_checker.py --text "Your marketing copy here"
"""

import argparse
import json
import re
import sys
from collections import Counter


# Default brand voice config (customize via --config)
DEFAULT_VOICE_CONFIG = {
    "preferred_terms": {
        "utilize": "use",
        "leverage": "use",
        "synergy": "collaboration",
        "paradigm": "approach",
        "disrupt": "change",
        "pivot": "shift",
        "circle back": "follow up",
        "touch base": "connect",
        "move the needle": "make an impact",
        "low-hanging fruit": "quick wins",
        "deep dive": "detailed look",
        "at the end of the day": "ultimately",
        "game-changer": "breakthrough",
        "best-in-class": "leading",
        "world-class": "exceptional",
    },
    "banned_words": [
        "synergize", "incentivize", "revolutionize", "disruptive",
        "bleeding edge", "rockstar", "ninja", "guru", "hack",
        "crushing it", "killing it", "10x",
    ],
    "voice_attributes": {
        "formality": "medium",  # low, medium, high
        "energy": "medium",     # low, medium, high
        "technical": "medium",  # low, medium, high
    },
    "style_rules": {
        "max_sentence_length": 25,
        "prefer_active_voice": True,
        "oxford_comma": True,
        "contractions_allowed": True,
    },
}


def analyze_formality(text):
    """Score text formality on a 0-100 scale."""
    formal_indicators = [
        r"\bfurthermore\b", r"\bmoreover\b", r"\bnevertheless\b",
        r"\bnotwithstanding\b", r"\bsubsequently\b", r"\bherein\b",
        r"\btherefore\b", r"\bconsequently\b", r"\baccordingly\b",
        r"\bpursuant\b", r"\bwherein\b", r"\bthus\b",
    ]
    casual_indicators = [
        r"\byeah\b", r"\bnope\b", r"\bkinda\b", r"\bwanna\b",
        r"\bgonna\b", r"\bgotta\b", r"\bstuff\b", r"\bcool\b",
        r"\bawesome\b", r"\bamazing\b", r"\bsuper\b", r"\btotally\b",
        r"\bbasically\b", r"\bliterally\b", r"\bhonestly\b",
    ]

    text_lower = text.lower()
    formal_count = sum(1 for p in formal_indicators if re.search(p, text_lower))
    casual_count = sum(1 for p in casual_indicators if re.search(p, text_lower))

    # Contractions lower formality
    contraction_count = len(re.findall(r"\b\w+'\w+\b", text))
    words = len(text.split())
    contraction_ratio = contraction_count / max(words, 1)

    score = 50  # neutral baseline
    score += formal_count * 8
    score -= casual_count * 8
    score -= contraction_ratio * 40

    return max(0, min(100, score))


def analyze_energy(text):
    """Score text energy/enthusiasm on a 0-100 scale."""
    high_energy = [
        r"!", r"\bamazing\b", r"\bincredible\b", r"\bexciting\b",
        r"\btransform\b", r"\bunlock\b", r"\bpower\b", r"\bboost\b",
        r"\bsupercharge\b", r"\baccelerate\b", r"\bskyrocket\b",
        r"\bexplosive\b", r"\bgame.?changing\b",
    ]
    low_energy = [
        r"\bmay\b", r"\bperhaps\b", r"\bmight\b", r"\bcould\b",
        r"\bsomewhat\b", r"\bslightly\b", r"\bpossibly\b",
        r"\breasonably\b", r"\bmodestly\b",
    ]

    text_lower = text.lower()
    high_count = sum(1 for p in high_energy if re.search(p, text_lower))
    low_count = sum(1 for p in low_energy if re.search(p, text_lower))

    exclamation_count = text.count("!")
    words = len(text.split())
    excl_ratio = exclamation_count / max(words / 100, 1)

    score = 50
    score += high_count * 6
    score -= low_count * 6
    score += min(excl_ratio * 10, 20)

    return max(0, min(100, score))


def check_vocabulary(text, config):
    """Check for preferred terms and banned words."""
    issues = []
    text_lower = text.lower()

    # Check for terms that should be replaced
    for bad_term, good_term in config.get("preferred_terms", {}).items():
        pattern = r"\b" + re.escape(bad_term) + r"\b"
        matches = re.findall(pattern, text_lower)
        if matches:
            issues.append({
                "type": "vocabulary",
                "severity": "warning",
                "found": bad_term,
                "count": len(matches),
                "suggestion": f"Replace '{bad_term}' with '{good_term}'",
            })

    # Check for banned words
    for word in config.get("banned_words", []):
        pattern = r"\b" + re.escape(word) + r"\b"
        matches = re.findall(pattern, text_lower)
        if matches:
            issues.append({
                "type": "vocabulary",
                "severity": "error",
                "found": word,
                "count": len(matches),
                "suggestion": f"Remove banned word: '{word}'",
            })

    return issues


def check_style_rules(text, config):
    """Check adherence to style rules."""
    issues = []
    rules = config.get("style_rules", {})

    # Sentence length
    max_len = rules.get("max_sentence_length", 25)
    sentences = re.split(r"[.!?]+", text)
    long_sentences = []
    for sent in sentences:
        words = sent.split()
        if len(words) > max_len:
            long_sentences.append(len(words))
    if long_sentences:
        issues.append({
            "type": "style",
            "severity": "warning",
            "rule": "sentence_length",
            "message": f"{len(long_sentences)} sentence(s) exceed {max_len} words "
            f"(longest: {max(long_sentences)} words)",
        })

    # Passive voice detection (simple heuristic)
    if rules.get("prefer_active_voice", True):
        passive_patterns = [
            r"\b(?:is|are|was|were|been|being)\s+(?:\w+ed)\b",
            r"\b(?:is|are|was|were|been|being)\s+(?:\w+en)\b",
        ]
        passive_count = 0
        for pattern in passive_patterns:
            passive_count += len(re.findall(pattern, text.lower()))
        if passive_count > 2:
            issues.append({
                "type": "style",
                "severity": "info",
                "rule": "passive_voice",
                "message": f"Detected {passive_count} potential passive voice constructions. "
                f"Consider rewriting in active voice.",
            })

    # Excessive exclamation marks
    excl_count = text.count("!")
    if excl_count > 3:
        issues.append({
            "type": "style",
            "severity": "warning",
            "rule": "exclamation_marks",
            "message": f"Found {excl_count} exclamation marks. Excessive punctuation can feel unprofessional.",
        })

    # ALL CAPS detection
    caps_words = re.findall(r"\b[A-Z]{4,}\b", text)
    # Filter out common acronyms
    common_acronyms = {"HTML", "CSS", "JSON", "HTTP", "HTTPS", "API", "SDK", "URL", "SEO", "CRM", "ROI", "KPI"}
    non_acronym_caps = [w for w in caps_words if w not in common_acronyms]
    if non_acronym_caps:
        issues.append({
            "type": "style",
            "severity": "warning",
            "rule": "all_caps",
            "message": f"Found ALL CAPS words: {', '.join(non_acronym_caps[:5])}. "
            f"Use bold or italics for emphasis instead.",
        })

    return issues


def analyze_text(text, config=None):
    """Run full analysis on a text sample."""
    if config is None:
        config = DEFAULT_VOICE_CONFIG

    formality = analyze_formality(text)
    energy = analyze_energy(text)

    vocab_issues = check_vocabulary(text, config)
    style_issues = check_style_rules(text, config)
    all_issues = vocab_issues + style_issues

    # Compare against target voice
    target_voice = config.get("voice_attributes", {})
    voice_alignment = {}

    formality_map = {"low": 25, "medium": 50, "high": 75}
    energy_map = {"low": 25, "medium": 50, "high": 75}

    if "formality" in target_voice:
        target = formality_map.get(target_voice["formality"], 50)
        drift = abs(formality - target)
        voice_alignment["formality"] = {
            "actual": formality,
            "target": target,
            "drift": drift,
            "aligned": drift < 20,
        }

    if "energy" in target_voice:
        target = energy_map.get(target_voice["energy"], 50)
        drift = abs(energy - target)
        voice_alignment["energy"] = {
            "actual": energy,
            "target": target,
            "drift": drift,
            "aligned": drift < 20,
        }

    # Word count and readability
    words = text.split()
    word_count = len(words)
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    avg_sentence_length = word_count / max(len(sentences), 1)

    return {
        "metrics": {
            "word_count": word_count,
            "sentence_count": len(sentences),
            "avg_sentence_length": round(avg_sentence_length, 1),
            "formality_score": round(formality, 1),
            "energy_score": round(energy, 1),
        },
        "voice_alignment": voice_alignment,
        "issues": all_issues,
        "issue_summary": {
            "errors": len([i for i in all_issues if i["severity"] == "error"]),
            "warnings": len([i for i in all_issues if i["severity"] == "warning"]),
            "info": len([i for i in all_issues if i["severity"] == "info"]),
        },
    }


def format_report(results, sample_name=None):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("MESSAGING CONSISTENCY CHECK")
    if sample_name:
        lines.append(f"Sample: {sample_name}")
    lines.append("=" * 60)

    metrics = results["metrics"]
    lines.append(f"Words:              {metrics['word_count']}")
    lines.append(f"Sentences:          {metrics['sentence_count']}")
    lines.append(f"Avg sentence len:   {metrics['avg_sentence_length']}")
    lines.append(f"Formality:          {metrics['formality_score']}/100")
    lines.append(f"Energy:             {metrics['energy_score']}/100")
    lines.append("")

    # Voice alignment
    if results["voice_alignment"]:
        lines.append("--- VOICE ALIGNMENT ---")
        for attr, data in results["voice_alignment"].items():
            status = "ALIGNED" if data["aligned"] else "DRIFTED"
            lines.append(
                f"  {attr.title()}: {data['actual']:.0f} (target: {data['target']}) "
                f"[{status}, drift: {data['drift']:.0f}]"
            )
        lines.append("")

    # Issues
    if results["issues"]:
        lines.append("--- ISSUES ---")
        for issue in results["issues"]:
            sev = issue["severity"].upper()
            msg = issue.get("suggestion", issue.get("message", ""))
            lines.append(f"  [{sev}] {msg}")
        lines.append("")

    summary = results["issue_summary"]
    total = summary["errors"] + summary["warnings"] + summary["info"]
    score = max(0, 100 - (summary["errors"] * 15) - (summary["warnings"] * 5) - (summary["info"] * 1))
    lines.append(f"Issues: {total} (Errors: {summary['errors']}, Warnings: {summary['warnings']}, Info: {summary['info']})")
    lines.append(f"Consistency Score: {score}/100")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check text samples against brand voice standards"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="JSON file with text samples",
    )
    parser.add_argument(
        "--text",
        help="Single text string to analyze",
    )
    parser.add_argument(
        "--config",
        help="Brand voice config JSON file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results in JSON format",
    )
    args = parser.parse_args()

    if not args.input and not args.text:
        parser.print_help()
        sys.exit(1)

    # Load config
    config = DEFAULT_VOICE_CONFIG
    if args.config:
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)

    if args.text:
        results = analyze_text(args.text, config)
        if args.json_output:
            print(json.dumps(results, indent=2))
        else:
            print(format_report(results))
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

        samples = data if isinstance(data, list) else data.get("samples", [])
        all_results = []

        for sample in samples:
            text = sample.get("text", sample.get("content", ""))
            name = sample.get("name", sample.get("channel", "unnamed"))
            result = analyze_text(text, config)
            result["sample_name"] = name
            all_results.append(result)

        if args.json_output:
            print(json.dumps(all_results, indent=2))
        else:
            for result in all_results:
                print(format_report(result, result.get("sample_name")))
                print()


if __name__ == "__main__":
    main()
