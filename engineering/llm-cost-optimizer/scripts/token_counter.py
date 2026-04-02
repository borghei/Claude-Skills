#!/usr/bin/env python3
"""
Token Counter - Count tokens in prompts and estimate costs across LLM models.

Uses heuristic tokenization (character and word-based estimation) to provide
accurate token counts without requiring external tokenizer libraries.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple


@dataclass
class ModelPricing:
    """Pricing information for an LLM model."""
    name: str
    provider: str
    input_per_million: float   # USD per 1M input tokens
    output_per_million: float  # USD per 1M output tokens
    context_window: int
    token_ratio: float = 1.0   # Multiplier vs. GPT-4 tokenizer baseline


# Pricing as of Q1 2026
MODEL_CATALOG = {
    "gpt-4o": ModelPricing("GPT-4o", "OpenAI", 2.50, 10.00, 128000, 1.0),
    "gpt-4o-mini": ModelPricing("GPT-4o-mini", "OpenAI", 0.15, 0.60, 128000, 1.0),
    "gpt-4-turbo": ModelPricing("GPT-4 Turbo", "OpenAI", 10.00, 30.00, 128000, 1.0),
    "o1": ModelPricing("o1", "OpenAI", 15.00, 60.00, 200000, 1.0),
    "o1-mini": ModelPricing("o1-mini", "OpenAI", 3.00, 12.00, 128000, 1.0),
    "o3-mini": ModelPricing("o3-mini", "OpenAI", 1.10, 4.40, 200000, 1.0),
    "claude-opus": ModelPricing("Claude Opus 4", "Anthropic", 15.00, 75.00, 200000, 1.05),
    "claude-sonnet": ModelPricing("Claude Sonnet 4", "Anthropic", 3.00, 15.00, 200000, 1.05),
    "claude-haiku": ModelPricing("Claude Haiku 3.5", "Anthropic", 0.80, 4.00, 200000, 1.05),
    "gemini-pro": ModelPricing("Gemini 2.0 Pro", "Google", 1.25, 5.00, 1000000, 0.95),
    "gemini-flash": ModelPricing("Gemini 2.0 Flash", "Google", 0.075, 0.30, 1000000, 0.95),
}


def estimate_tokens(text: str, token_ratio: float = 1.0) -> int:
    """
    Estimate token count using heuristic methods.

    Uses multiple estimation strategies and averages them for accuracy:
    1. Character-based: ~4 chars per token for English
    2. Word-based: ~0.75 words per token
    3. Whitespace + punctuation based
    """
    if not text:
        return 0

    # Strategy 1: Character-based (4 chars per token average)
    char_estimate = len(text) / 4.0

    # Strategy 2: Word-based
    words = text.split()
    word_estimate = len(words) / 0.75

    # Strategy 3: More refined - split on whitespace and punctuation
    # Accounts for subword tokenization
    pieces = re.findall(r'\w+|[^\w\s]', text)
    piece_estimate = len(pieces) * 0.85  # Most pieces are 1 token, some merge

    # Strategy 4: Account for numbers (often multiple tokens)
    numbers = re.findall(r'\d+', text)
    number_extra = sum(max(0, len(n) // 3 - 1) for n in numbers)

    # Strategy 5: Account for code (different tokenization patterns)
    code_indicators = len(re.findall(r'[{}()\[\];:=<>]', text))
    code_adjustment = code_indicators * 0.3

    # Weighted average
    base_estimate = (char_estimate * 0.35 + word_estimate * 0.35 + piece_estimate * 0.30)
    adjusted = base_estimate + number_extra + code_adjustment

    # Apply model-specific ratio
    return max(1, int(math.ceil(adjusted * token_ratio)))


def estimate_costs(token_count: int, models: List[str],
                   assume_output_ratio: float = 1.5) -> List[Dict]:
    """Estimate costs for given token count across models."""
    results = []

    for model_key in models:
        model = MODEL_CATALOG.get(model_key)
        if not model:
            continue

        adjusted_tokens = int(token_count * model.token_ratio)
        estimated_output = int(adjusted_tokens * assume_output_ratio)

        input_cost = (adjusted_tokens / 1_000_000) * model.input_per_million
        output_cost = (estimated_output / 1_000_000) * model.output_per_million
        total_cost = input_cost + output_cost

        fits_context = adjusted_tokens <= model.context_window

        results.append({
            "model": model.name,
            "provider": model.provider,
            "estimated_input_tokens": adjusted_tokens,
            "estimated_output_tokens": estimated_output,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(total_cost, 6),
            "cost_per_1k_requests": round(total_cost * 1000, 2),
            "cost_per_1m_requests": round(total_cost * 1_000_000, 2),
            "fits_context_window": fits_context,
            "context_window": model.context_window,
            "context_utilization_pct": round(adjusted_tokens / model.context_window * 100, 1),
        })

    results.sort(key=lambda x: x["total_cost_usd"])
    return results


def analyze_text_composition(text: str) -> Dict:
    """Analyze the composition of the text for optimization insights."""
    lines = text.split("\n")
    words = text.split()

    # Detect content types
    code_lines = sum(1 for l in lines if re.search(r'[{}()\[\];=].*[{}()\[\];=]', l))
    empty_lines = sum(1 for l in lines if not l.strip())
    comment_lines = sum(1 for l in lines if l.strip().startswith(("#", "//", "/*", "*", "<!--")))

    # Detect repetition
    unique_words = set(w.lower() for w in words)
    repetition_ratio = 1 - (len(unique_words) / max(len(words), 1))

    # Detect verbose patterns
    filler_words = {"please", "kindly", "basically", "actually", "essentially",
                    "literally", "honestly", "obviously", "clearly", "simply",
                    "just", "really", "very", "quite", "rather"}
    filler_count = sum(1 for w in words if w.lower() in filler_words)

    return {
        "total_characters": len(text),
        "total_words": len(words),
        "total_lines": len(lines),
        "empty_lines": empty_lines,
        "code_lines": code_lines,
        "comment_lines": comment_lines,
        "unique_word_ratio": round(1 - repetition_ratio, 3),
        "repetition_ratio": round(repetition_ratio, 3),
        "filler_word_count": filler_count,
        "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 1),
        "avg_line_length": round(sum(len(l) for l in lines) / max(len(lines), 1), 1),
    }


def format_human(text: str, token_count: int, costs: List[Dict],
                 composition: Dict) -> str:
    """Format results for human reading."""
    lines = []
    lines.append("=" * 65)
    lines.append("TOKEN COUNT & COST ESTIMATION")
    lines.append("=" * 65)
    lines.append(f"Estimated tokens: {token_count:,}")
    lines.append(f"Characters: {composition['total_characters']:,}")
    lines.append(f"Words: {composition['total_words']:,}")
    lines.append(f"Lines: {composition['total_lines']:,}")
    lines.append("")

    lines.append("Text Composition:")
    lines.append(f"  Unique word ratio: {composition['unique_word_ratio']:.1%}")
    lines.append(f"  Filler words: {composition['filler_word_count']}")
    lines.append(f"  Code lines: {composition['code_lines']}")
    lines.append(f"  Empty lines: {composition['empty_lines']}")
    lines.append("")

    lines.append("Cost Estimates (sorted by total cost):")
    lines.append(f"  {'Model':<22} {'Input $':>10} {'Output $':>10} {'Total $':>10} {'Per 1K req':>12}")
    lines.append("  " + "-" * 64)

    for c in costs:
        ctx = "OK" if c["fits_context_window"] else "EXCEEDS"
        lines.append(
            f"  {c['model']:<22} "
            f"${c['input_cost_usd']:>8.4f} "
            f"${c['output_cost_usd']:>8.4f} "
            f"${c['total_cost_usd']:>8.4f} "
            f"${c['cost_per_1k_requests']:>10.2f}"
        )
        if not c["fits_context_window"]:
            lines.append(f"    WARNING: {ctx} context window ({c['context_window']:,} tokens)")

    lines.append("")

    if costs:
        cheapest = costs[0]
        most_expensive = costs[-1]
        if len(costs) > 1:
            savings = most_expensive["total_cost_usd"] - cheapest["total_cost_usd"]
            lines.append(f"Cheapest: {cheapest['model']} (${cheapest['total_cost_usd']:.4f}/request)")
            lines.append(f"Most expensive: {most_expensive['model']} (${most_expensive['total_cost_usd']:.4f}/request)")
            if most_expensive["total_cost_usd"] > 0:
                pct = (savings / most_expensive["total_cost_usd"]) * 100
                lines.append(f"Potential savings by switching: ${savings:.4f}/request ({pct:.0f}%)")

    lines.append("=" * 65)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Token Counter - Count tokens and estimate costs across LLM models"
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file", help="Path to text/prompt file")
    input_group.add_argument("--text", help="Text string to count")
    input_group.add_argument("--stdin", action="store_true", help="Read from stdin")

    parser.add_argument("--models", nargs="+", default=["all"],
                        help="Models to estimate costs for (default: all). "
                             f"Options: {', '.join(MODEL_CATALOG.keys())}, all")
    parser.add_argument("--output-ratio", type=float, default=1.5,
                        help="Assumed output/input token ratio (default: 1.5)")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    args = parser.parse_args()

    # Read input
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

    # Resolve models
    if "all" in args.models:
        model_keys = list(MODEL_CATALOG.keys())
    else:
        model_keys = args.models

    # Count and estimate
    token_count = estimate_tokens(text)
    costs = estimate_costs(token_count, model_keys, args.output_ratio)
    composition = analyze_text_composition(text)

    if args.format == "json":
        output = {
            "estimated_tokens": token_count,
            "composition": composition,
            "cost_estimates": costs,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(text, token_count, costs, composition))


if __name__ == "__main__":
    main()
