#!/usr/bin/env python3
"""
Prompt Optimizer - Analyze prompts for token reduction opportunities.

Identifies verbose patterns, redundancies, and optimization opportunities
in LLM prompts to reduce token usage while preserving intent.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple


@dataclass
class Optimization:
    """A single optimization opportunity."""
    category: str
    description: str
    original_text: str
    suggested_text: str
    token_savings_estimate: int
    line_number: Optional[int] = None
    confidence: str = "medium"  # high, medium, low


@dataclass
class OptimizationReport:
    """Full optimization analysis."""
    original_tokens: int
    optimized_tokens_estimate: int
    reduction_pct: float
    optimizations: List[Optimization] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


# Filler phrases that can be removed without changing meaning
FILLER_PHRASES = [
    (r'\bplease\s+', '', "Remove 'please' - LLMs don't need politeness tokens"),
    (r'\bkindly\s+', '', "Remove 'kindly'"),
    (r'\bbasically\b\s*,?\s*', '', "Remove filler word 'basically'"),
    (r'\bactually\b\s*,?\s*', '', "Remove filler word 'actually'"),
    (r'\bessentially\b\s*,?\s*', '', "Remove filler word 'essentially'"),
    (r'\bliterally\b\s*,?\s*', '', "Remove filler word 'literally'"),
    (r'\bhonestly\b\s*,?\s*', '', "Remove filler word 'honestly'"),
    (r'\bobviously\b\s*,?\s*', '', "Remove filler word 'obviously'"),
    (r'\bclearly\b\s*,?\s*', '', "Remove filler word 'clearly'"),
    (r'\bsimply\b\s*,?\s*', '', "Remove filler word 'simply'"),
    (r'\bjust\b\s+', '', "Remove filler word 'just'"),
    (r'\breally\b\s*', '', "Remove filler word 'really'"),
    (r'\bvery\b\s+', '', "Remove filler word 'very'"),
    (r'\bin order to\b', 'to', "Simplify 'in order to' -> 'to'"),
    (r'\bdue to the fact that\b', 'because', "Simplify verbose conjunction"),
    (r'\bat this point in time\b', 'now', "Simplify verbose phrase"),
    (r'\bin the event that\b', 'if', "Simplify 'in the event that' -> 'if'"),
    (r'\bfor the purpose of\b', 'to', "Simplify verbose phrase"),
    (r'\bwith regard to\b', 'about', "Simplify 'with regard to' -> 'about'"),
    (r'\bin light of\b', 'given', "Simplify verbose phrase"),
    (r'\bit is important to note that\b', '', "Remove unnecessary preamble"),
    (r'\bI would like you to\b', '', "Remove unnecessary preamble"),
    (r'\bcould you please\b', '', "Remove unnecessary politeness"),
    (r'\bI want you to\b', '', "Remove unnecessary preamble"),
    (r'\bmake sure to\b', '', "Simplify - the instruction itself implies this"),
    (r'\bensure that you\b', '', "Remove unnecessary emphasis"),
]

# Redundant instruction patterns
REDUNDANT_PATTERNS = [
    (r'(?:be|try to be)\s+(?:as\s+)?(?:concise|brief|short)\s+(?:as\s+possible|and\s+clear)',
     "Redundant conciseness instruction - set max tokens instead"),
    (r'(?:do not|don\'t)\s+(?:make up|hallucinate|fabricate)\s+(?:information|data|facts)',
     "Common instruction that most models already follow - consider removing"),
    (r'(?:you are|act as)\s+(?:a|an)\s+(?:helpful|expert|professional|skilled)',
     "Role preamble can often be shortened to just the role name"),
    (r'(?:remember|keep in mind|note)\s+that\s+you\s+',
     "Unnecessary meta-instruction - state the requirement directly"),
    (r'(?:the following|below)\s+(?:is|are)\s+(?:the|a)\s+',
     "Verbose introduction to content - just present the content"),
]


def estimate_tokens(text: str) -> int:
    """Quick token estimation."""
    if not text:
        return 0
    chars = len(text)
    words = len(text.split())
    return max(1, int((chars / 4.0 * 0.4) + (words / 0.75 * 0.4) + (len(re.findall(r'\w+|[^\w\s]', text)) * 0.85 * 0.2)))


def find_repeated_content(text: str) -> List[Optimization]:
    """Find repeated phrases and sentences."""
    optimizations = []
    sentences = re.split(r'[.!?]\s+', text)
    seen = {}

    for i, sent in enumerate(sentences):
        normalized = sent.strip().lower()
        if len(normalized) < 20:
            continue
        if normalized in seen:
            tokens_saved = estimate_tokens(sent)
            optimizations.append(Optimization(
                category="repetition",
                description=f"Sentence repeated (first at position {seen[normalized]})",
                original_text=sent.strip()[:80],
                suggested_text="[remove duplicate]",
                token_savings_estimate=tokens_saved,
                confidence="high",
            ))
        else:
            seen[normalized] = i

    # Find repeated phrases (3+ words, appearing 3+ times)
    words = text.split()
    for n in range(3, 8):
        phrase_counts: Dict[str, int] = {}
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i:i+n]).lower()
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

        for phrase, count in phrase_counts.items():
            if count >= 3 and len(phrase) > 15:
                tokens_saved = estimate_tokens(phrase) * (count - 1)
                optimizations.append(Optimization(
                    category="repetition",
                    description=f"Phrase repeated {count} times",
                    original_text=phrase[:80],
                    suggested_text=f"[define once, reference {count-1} times]",
                    token_savings_estimate=tokens_saved,
                    confidence="medium",
                ))

    return optimizations


def find_filler_optimizations(text: str) -> List[Optimization]:
    """Find filler words and verbose phrases."""
    optimizations = []
    lines = text.split("\n")

    for filler_pattern, replacement, desc in FILLER_PHRASES:
        for i, line in enumerate(lines, 1):
            matches = list(re.finditer(filler_pattern, line, re.IGNORECASE))
            for match in matches:
                original = match.group()
                tokens_saved = max(1, estimate_tokens(original) - estimate_tokens(replacement))
                optimizations.append(Optimization(
                    category="filler",
                    description=desc,
                    original_text=original.strip(),
                    suggested_text=replacement if replacement else "[remove]",
                    token_savings_estimate=tokens_saved,
                    line_number=i,
                    confidence="high",
                ))

    return optimizations


def find_redundant_instructions(text: str) -> List[Optimization]:
    """Find redundant or unnecessary instructions."""
    optimizations = []
    lines = text.split("\n")

    for pattern, desc in REDUNDANT_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                match = re.search(pattern, line, re.IGNORECASE)
                tokens_saved = estimate_tokens(match.group()) if match else 3
                optimizations.append(Optimization(
                    category="redundant",
                    description=desc,
                    original_text=line.strip()[:80],
                    suggested_text="[consider removing or simplifying]",
                    token_savings_estimate=tokens_saved,
                    line_number=i,
                    confidence="medium",
                ))

    return optimizations


def find_formatting_optimizations(text: str) -> List[Optimization]:
    """Find formatting-based optimization opportunities."""
    optimizations = []
    lines = text.split("\n")

    # Excessive blank lines
    consecutive_blank = 0
    blank_start = 0
    for i, line in enumerate(lines, 1):
        if not line.strip():
            if consecutive_blank == 0:
                blank_start = i
            consecutive_blank += 1
        else:
            if consecutive_blank >= 3:
                optimizations.append(Optimization(
                    category="formatting",
                    description=f"{consecutive_blank} consecutive blank lines (lines {blank_start}-{blank_start+consecutive_blank-1})",
                    original_text=f"[{consecutive_blank} blank lines]",
                    suggested_text="[1 blank line]",
                    token_savings_estimate=consecutive_blank - 1,
                    line_number=blank_start,
                    confidence="high",
                ))
            consecutive_blank = 0

    # Long markdown headers/dividers
    for i, line in enumerate(lines, 1):
        if re.match(r'^[-=*#]{10,}$', line.strip()):
            tokens_saved = max(1, estimate_tokens(line) - 2)
            optimizations.append(Optimization(
                category="formatting",
                description="Long decorative divider line",
                original_text=line.strip()[:40],
                suggested_text="---",
                token_savings_estimate=tokens_saved,
                line_number=i,
                confidence="high",
            ))

    # Verbose list markers
    numbered_items = [i for i, l in enumerate(lines) if re.match(r'^\s*\d+\.\s', l)]
    if len(numbered_items) > 10:
        optimizations.append(Optimization(
            category="formatting",
            description=f"Long numbered list ({len(numbered_items)} items) - consider condensing",
            original_text=f"[{len(numbered_items)} numbered items]",
            suggested_text="Use dash lists (-) or combine related items",
            token_savings_estimate=len(numbered_items),
            confidence="low",
        ))

    return optimizations


def analyze_prompt(text: str, target_reduction: Optional[float] = None) -> OptimizationReport:
    """Perform full prompt optimization analysis."""
    original_tokens = estimate_tokens(text)

    all_optimizations = []
    all_optimizations.extend(find_filler_optimizations(text))
    all_optimizations.extend(find_redundant_instructions(text))
    all_optimizations.extend(find_repeated_content(text))
    all_optimizations.extend(find_formatting_optimizations(text))

    # Deduplicate by line number and category
    seen = set()
    unique_optimizations = []
    for opt in all_optimizations:
        key = (opt.category, opt.line_number, opt.original_text[:30])
        if key not in seen:
            seen.add(key)
            unique_optimizations.append(opt)

    # Sort by savings descending
    unique_optimizations.sort(key=lambda x: x.token_savings_estimate, reverse=True)

    total_savings = sum(o.token_savings_estimate for o in unique_optimizations)
    optimized_estimate = max(1, original_tokens - total_savings)
    reduction_pct = (total_savings / max(original_tokens, 1)) * 100

    # Category summary
    summary: Dict[str, int] = {}
    for opt in unique_optimizations:
        summary[opt.category] = summary.get(opt.category, 0) + opt.token_savings_estimate

    report = OptimizationReport(
        original_tokens=original_tokens,
        optimized_tokens_estimate=optimized_estimate,
        reduction_pct=round(reduction_pct, 1),
        optimizations=unique_optimizations,
        summary=summary,
    )

    if target_reduction and reduction_pct < target_reduction:
        report.warnings.append(
            f"Target reduction of {target_reduction}% not achievable through automated "
            f"optimization alone ({reduction_pct:.1f}% found). Consider manual rewriting."
        )

    return report


def format_human(report: OptimizationReport) -> str:
    """Format for human reading."""
    lines = []
    lines.append("=" * 65)
    lines.append("PROMPT OPTIMIZATION REPORT")
    lines.append("=" * 65)
    lines.append(f"Original tokens (est.): {report.original_tokens:,}")
    lines.append(f"Optimized tokens (est.): {report.optimized_tokens_estimate:,}")
    lines.append(f"Potential reduction: {report.reduction_pct}%")
    lines.append(f"Token savings: ~{report.original_tokens - report.optimized_tokens_estimate:,}")
    lines.append("")

    if report.summary:
        lines.append("Savings by Category:")
        for cat, savings in sorted(report.summary.items(), key=lambda x: -x[1]):
            lines.append(f"  {cat}: ~{savings} tokens")
        lines.append("")

    if report.warnings:
        for w in report.warnings:
            lines.append(f"  WARNING: {w}")
        lines.append("")

    lines.append(f"Optimization Opportunities ({len(report.optimizations)} found):")
    lines.append("-" * 55)

    for i, opt in enumerate(report.optimizations[:20], 1):
        ln = f" (line {opt.line_number})" if opt.line_number else ""
        lines.append(f"  {i}. [{opt.category.upper()}]{ln} ~{opt.token_savings_estimate} tokens")
        lines.append(f"     {opt.description}")
        lines.append(f"     Before: {opt.original_text}")
        lines.append(f"     After:  {opt.suggested_text}")
        lines.append("")

    if len(report.optimizations) > 20:
        lines.append(f"  ... and {len(report.optimizations) - 20} more optimizations")

    lines.append("=" * 65)
    return "\n".join(lines)


def format_json(report: OptimizationReport) -> str:
    """Format as JSON."""
    data = {
        "original_tokens": report.original_tokens,
        "optimized_tokens_estimate": report.optimized_tokens_estimate,
        "reduction_pct": report.reduction_pct,
        "summary": report.summary,
        "warnings": report.warnings,
        "optimizations": [asdict(o) for o in report.optimizations],
    }
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Optimizer - Analyze prompts for token reduction opportunities"
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file", help="Path to prompt file")
    input_group.add_argument("--text", help="Prompt text")
    input_group.add_argument("--stdin", action="store_true", help="Read from stdin")

    parser.add_argument("--target-reduction", type=float,
                        help="Target token reduction percentage (e.g., 30 for 30%%)")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    args = parser.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        text = path.read_text(encoding="utf-8", errors="ignore")
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("Error: Empty input", file=sys.stderr)
        sys.exit(1)

    report = analyze_prompt(text, args.target_reduction)

    if args.format == "json":
        print(format_json(report))
    else:
        print(format_human(report))


if __name__ == "__main__":
    main()
