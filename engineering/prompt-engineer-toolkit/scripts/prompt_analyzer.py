#!/usr/bin/env python3
"""Analyze prompt files for quality metrics.

Evaluates prompts against production quality criteria including clarity score,
instruction density, few-shot coverage, token estimation, and structural layer
detection based on the 6-layer system prompt architecture.

No external dependencies -- uses Python standard library only.
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter


# Approximate token count using whitespace + punctuation splitting.
# This is a rough heuristic (~1.3 tokens per whitespace-delimited word for English).
TOKEN_RATIO = 1.3

# Instruction signal words that indicate directive content.
INSTRUCTION_SIGNALS = [
    r"\bmust\b", r"\bshould\b", r"\bshall\b", r"\balways\b", r"\bnever\b",
    r"\bdo not\b", r"\bdon't\b", r"\bavoid\b", r"\bensure\b", r"\brequire",
    r"\bcritical\b", r"\bimportant\b", r"\brule\b", r"\bconstraint\b",
    r"\bprohibit", r"\bforbid", r"\bmandatory\b", r"\bonly\b",
]

# Few-shot indicator patterns.
FEW_SHOT_PATTERNS = [
    r"(?i)\bexample\s*\d*\s*[:(\[]",
    r"(?i)\binput\s*:",
    r"(?i)\boutput\s*:",
    r"(?i)\bsample\b",
    r"(?i)\bdemonstrat",
    r"(?i)\bfor instance\b",
    r"(?i)\be\.g\.\b",
]

# Layer detection heuristics aligned with the 6-layer architecture.
LAYER_PATTERNS = {
    "identity_role": [
        r"(?i)you are\b", r"(?i)act as\b", r"(?i)your role\b",
        r"(?i)you serve as\b", r"(?i)as a .{3,30} expert",
    ],
    "capabilities_constraints": [
        r"(?i)you can\b", r"(?i)you cannot\b", r"(?i)you have access\b",
        r"(?i)you are able\b", r"(?i)capable of\b", r"(?i)limited to\b",
    ],
    "output_format": [
        r"(?i)respond with\b", r"(?i)output format\b", r"(?i)json\b",
        r"(?i)structure your\b", r"(?i)format your\b", r"(?i)schema\b",
    ],
    "quality_standards": [
        r"(?i)quality\b", r"(?i)thorough\b", r"(?i)accurate\b",
        r"(?i)concise\b", r"(?i)include .{0,20}(detail|evidence|citation)",
    ],
    "anti_patterns": [
        r"(?i)never\b", r"(?i)do not\b", r"(?i)don't\b", r"(?i)avoid\b",
        r"(?i)forbidden\b", r"(?i)prohibited\b",
    ],
    "examples": [
        r"(?i)example\b", r"(?i)for instance\b", r"(?i)here is\b",
        r"(?i)sample\b", r"(?i)demonstration\b",
    ],
}

# Clarity deductors -- patterns that reduce clarity.
CLARITY_DEDUCTORS = [
    (r"(?i)\betc\.?\b", 0.03, "vague_etc"),
    (r"(?i)\bstuff\b", 0.04, "informal_stuff"),
    (r"(?i)\bthings\b", 0.02, "vague_things"),
    (r"(?i)\bmaybe\b", 0.03, "hedging_maybe"),
    (r"(?i)\bsomehow\b", 0.04, "vague_somehow"),
    (r"(?i)\bkind of\b", 0.03, "hedging_kind_of"),
    (r"(?i)\bsort of\b", 0.03, "hedging_sort_of"),
    (r"(?i)\bprobably\b", 0.02, "hedging_probably"),
    (r"(?i)\bbasically\b", 0.02, "filler_basically"),
    (r"(?i)\bjust\b", 0.01, "filler_just"),
]


def estimate_tokens(text: str) -> int:
    """Rough token estimate based on word count and punctuation."""
    words = text.split()
    return max(1, int(math.ceil(len(words) * TOKEN_RATIO)))


def compute_instruction_density(text: str) -> dict:
    """Return instruction density and matched signals."""
    sentences = re.split(r"[.!?\n]", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return {"density": 0.0, "instruction_count": 0, "sentence_count": 0, "signals": []}

    instruction_sentences = 0
    matched_signals = []
    for sent in sentences:
        for pattern in INSTRUCTION_SIGNALS:
            if re.search(pattern, sent, re.IGNORECASE):
                instruction_sentences += 1
                matched_signals.append(pattern.strip(r"\b"))
                break

    density = instruction_sentences / len(sentences)
    return {
        "density": round(density, 3),
        "instruction_count": instruction_sentences,
        "sentence_count": len(sentences),
        "signals": list(set(matched_signals)),
    }


def detect_few_shot(text: str) -> dict:
    """Detect few-shot examples and estimate count."""
    example_blocks = re.findall(r"(?i)example\s*\d*\s*[:(]", text)
    input_output_pairs = min(
        len(re.findall(r"(?i)\binput\s*:", text)),
        len(re.findall(r"(?i)\boutput\s*:", text)),
    )
    pattern_hits = sum(1 for p in FEW_SHOT_PATTERNS if re.search(p, text))
    estimated_shots = max(len(example_blocks), input_output_pairs)

    coverage = "none"
    if estimated_shots >= 3:
        coverage = "good"
    elif estimated_shots >= 1:
        coverage = "partial"

    return {
        "estimated_shots": estimated_shots,
        "coverage": coverage,
        "pattern_hits": pattern_hits,
    }


def detect_layers(text: str) -> dict:
    """Detect which of the 6 architecture layers are present."""
    results = {}
    for layer, patterns in LAYER_PATTERNS.items():
        hits = sum(1 for p in patterns if re.search(p, text))
        results[layer] = {
            "detected": hits > 0,
            "signal_strength": min(hits, len(patterns)),
            "max_signals": len(patterns),
        }
    detected_count = sum(1 for v in results.values() if v["detected"])
    return {"layers": results, "detected_count": detected_count, "total_layers": 6}


def compute_clarity_score(text: str, instruction_info: dict, layer_info: dict, few_shot_info: dict) -> dict:
    """Compute an overall clarity score from 0 to 100."""
    # Start at 60 base score.
    score = 60.0
    deductions = []

    # Reward instruction density (up to +15).
    density = instruction_info["density"]
    if density >= 0.3:
        score += 15
    elif density >= 0.15:
        score += 10
    elif density >= 0.05:
        score += 5

    # Reward layer coverage (up to +15).
    layer_ratio = layer_info["detected_count"] / layer_info["total_layers"]
    score += layer_ratio * 15

    # Reward few-shot examples (up to +10).
    if few_shot_info["coverage"] == "good":
        score += 10
    elif few_shot_info["coverage"] == "partial":
        score += 5

    # Deduct for clarity anti-patterns.
    for pattern, penalty, label in CLARITY_DEDUCTORS:
        count = len(re.findall(pattern, text))
        if count > 0:
            deduction = min(penalty * count, 0.10)  # Cap per-pattern.
            score -= deduction * 100
            deductions.append({"pattern": label, "count": count, "penalty": round(deduction * 100, 1)})

    score = max(0, min(100, round(score, 1)))

    grade = "excellent" if score >= 90 else "good" if score >= 75 else "fair" if score >= 60 else "poor"

    return {"score": score, "grade": grade, "deductions": deductions}


def analyze_prompt(text: str, filepath: str = "<stdin>") -> dict:
    """Run full analysis on a prompt text and return results dict."""
    token_count = estimate_tokens(text)
    line_count = text.count("\n") + 1
    char_count = len(text)
    word_count = len(text.split())

    instruction_info = compute_instruction_density(text)
    few_shot_info = detect_few_shot(text)
    layer_info = detect_layers(text)
    clarity_info = compute_clarity_score(text, instruction_info, layer_info, few_shot_info)

    return {
        "file": filepath,
        "metrics": {
            "token_estimate": token_count,
            "line_count": line_count,
            "char_count": char_count,
            "word_count": word_count,
        },
        "clarity": clarity_info,
        "instruction_density": instruction_info,
        "few_shot": few_shot_info,
        "layer_coverage": layer_info,
    }


def format_human(result: dict) -> str:
    """Format analysis result for human-readable console output."""
    lines = []
    lines.append(f"Prompt Analysis: {result['file']}")
    lines.append("=" * 60)

    m = result["metrics"]
    lines.append(f"  Tokens (est):  {m['token_estimate']}")
    lines.append(f"  Lines:         {m['line_count']}")
    lines.append(f"  Words:         {m['word_count']}")
    lines.append(f"  Characters:    {m['char_count']}")
    lines.append("")

    c = result["clarity"]
    lines.append(f"  Clarity Score: {c['score']} / 100  ({c['grade']})")
    if c["deductions"]:
        lines.append("  Deductions:")
        for d in c["deductions"]:
            lines.append(f"    - {d['pattern']}: {d['count']} occurrence(s), -{d['penalty']} pts")
    lines.append("")

    i = result["instruction_density"]
    lines.append(f"  Instruction Density: {i['density']} ({i['instruction_count']}/{i['sentence_count']} sentences)")
    if i["signals"]:
        lines.append(f"  Signal words: {', '.join(i['signals'][:10])}")
    lines.append("")

    fs = result["few_shot"]
    lines.append(f"  Few-Shot Coverage: {fs['coverage']} ({fs['estimated_shots']} example(s) detected)")
    lines.append("")

    lc = result["layer_coverage"]
    lines.append(f"  Layer Coverage: {lc['detected_count']}/{lc['total_layers']} layers detected")
    for name, info in lc["layers"].items():
        status = "YES" if info["detected"] else " - "
        lines.append(f"    [{status}] {name.replace('_', ' ').title()}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze prompt files for quality metrics (clarity, instruction density, few-shot coverage, tokens).",
        epilog="Example: python prompt_analyzer.py my_prompt.txt --json",
    )
    parser.add_argument("files", nargs="+", help="Prompt file(s) to analyze")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    results = []
    for filepath in args.files:
        if not os.path.isfile(filepath):
            print(f"Error: file not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        results.append(analyze_prompt(text, filepath))

    if args.json:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    else:
        for result in results:
            print(format_human(result))


if __name__ == "__main__":
    main()
