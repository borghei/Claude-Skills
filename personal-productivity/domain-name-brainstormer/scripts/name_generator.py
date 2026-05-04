#!/usr/bin/env python3
"""
Name Generator — produce and score candidate brand / domain names from seed words.

Usage:
    python name_generator.py "data,signal,insight"
    python name_generator.py "data,signal" --count 200 --pattern blend
    python name_generator.py "data,signal" --json
"""

import argparse
import json
import re
import sys


PREFIXES = ["go", "get", "try", "use", "join", "hi", "my", "the"]
SUFFIXES = ["ly", "ify", "io", "ai", "lab", "labs", "hq", "co", "stack", "kit",
            "app", "hub", "base", "box", "loop", "core", "dash", "wave", "deck",
            "ish", "able", "wise", "spark", "flow", "grid"]

# TLD treated as suffix in the brand sound
TLD_SUFFIXES = [".io", ".ai", ".co", ".sh", ".so", ".dev", ".app", ".fyi"]

VOWELS = "aeiou"
COMMON_WORDS = {
    "data", "the", "and", "for", "you", "app", "lab", "hub", "code", "build",
    "make", "ship", "fast", "smart", "easy", "good", "best", "new", "now"
}


def vowel_drop(word):
    """Remove inner vowels but keep first letter and last consonant if vowel-final."""
    if len(word) < 3:
        return [word]
    out = [word[0]]
    for ch in word[1:]:
        if ch.lower() not in VOWELS or len(out) < 2:
            out.append(ch)
    return ["".join(out)]


def prefix_suffix(word):
    candidates = []
    for p in PREFIXES:
        candidates.append(p + word)
    for s in SUFFIXES:
        candidates.append(word + s)
    return candidates


def blend(word_a, word_b):
    if len(word_a) < 2 or len(word_b) < 2:
        return []
    a_half = word_a[: max(2, len(word_a) // 2 + 1)]
    b_half_start = word_b[max(1, len(word_b) // 3) :]
    b_half_end = word_b[: max(2, len(word_b) // 2)]
    return [
        a_half + word_b,
        word_a + b_half_start,
        a_half + b_half_start,
        word_b + word_a[: max(2, len(word_a) // 3)],
        b_half_end + a_half,
    ]


def tld_suffix(word):
    return [word + t for t in TLD_SUFFIXES]


def repeat(word):
    return [word + word, word[: max(2, len(word) // 2)] + word]


def pronounceability(name):
    """Score 0-1: ratio of consonant-vowel transitions to total length."""
    s = re.sub(r"[^a-z]", "", name.lower())
    if len(s) < 2:
        return 0.0
    transitions = 0
    for i in range(1, len(s)):
        prev_v = s[i - 1] in VOWELS
        cur_v = s[i] in VOWELS
        if prev_v != cur_v:
            transitions += 1
    return min(transitions / (len(s) - 1), 1.0)


def length_score(name):
    """Score 0-1: 5-10 chars peak, drops off outside that band."""
    base = re.sub(r"\.\w+$", "", name)
    n = len(base)
    if 5 <= n <= 10:
        return 1.0
    if n < 5:
        return n / 5
    return max(0.0, 1.0 - (n - 10) / 10)


def score_name(name):
    base_score = 50
    base_score += int(length_score(name) * 30)
    base_score += int(pronounceability(name) * 20)
    if "-" in name or any(c.isdigit() for c in name):
        base_score -= 20
    base = re.sub(r"\.\w+$", "", name).lower()
    if base in COMMON_WORDS:
        base_score -= 15
    if len(base) < 3:
        base_score -= 30
    return max(0, min(100, base_score))


def classify_pattern(name, seeds):
    if any(t in name for t in TLD_SUFFIXES):
        return "tld_suffix"
    if any(p + s == name.lower() for p in PREFIXES for s in seeds):
        return "prefix_suffix"
    if any(s + suf == name.lower() for s in seeds for suf in SUFFIXES):
        return "prefix_suffix"
    if any(name.lower() == s + s for s in seeds):
        return "repeat"
    for a in seeds:
        for b in seeds:
            if a != b and (a in name.lower() and b in name.lower()):
                return "blend"
    return "vowel_drop"


def generate(seeds, pattern_filter="all", count=100):
    seeds = [s.strip().lower() for s in seeds if s.strip()]
    candidates = set()

    for seed in seeds:
        if pattern_filter in ("all", "vowel_drop"):
            for c in vowel_drop(seed):
                candidates.add(c)
        if pattern_filter in ("all", "prefix_suffix"):
            for c in prefix_suffix(seed):
                candidates.add(c)
        if pattern_filter in ("all", "tld_suffix"):
            for c in tld_suffix(seed):
                candidates.add(c)
        if pattern_filter in ("all", "repeat"):
            for c in repeat(seed):
                candidates.add(c)
    if pattern_filter in ("all", "blend"):
        for a in seeds:
            for b in seeds:
                if a != b:
                    for c in blend(a, b):
                        candidates.add(c)

    scored = []
    for name in candidates:
        scored.append({
            "name": name,
            "score": score_name(name),
            "pattern": classify_pattern(name, seeds),
        })
    scored.sort(key=lambda r: -r["score"])
    return scored[:count]


def render_human(results):
    if not results:
        return "No candidates generated."
    lines = [f"Generated {len(results)} candidates"]
    lines.append("")
    lines.append(f"{'Score':<7}{'Pattern':<16}Name")
    lines.append("-" * 60)
    for r in results:
        lines.append(f"{r['score']:<7}{r['pattern']:<16}{r['name']}")
    lines.append("")
    lines.append("Next: manually check top 10-15 against domain registrars + USPTO TESS.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate brand/domain name candidates from seed words.")
    parser.add_argument("seeds", help="Comma-separated seed words, e.g. 'data,signal,insight'")
    parser.add_argument("--count", type=int, default=100, help="Max candidates to return")
    parser.add_argument(
        "--pattern",
        choices=["all", "vowel_drop", "prefix_suffix", "blend", "tld_suffix", "repeat"],
        default="all",
        help="Restrict to one naming pattern",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable")
    args = parser.parse_args()

    seeds = [s for s in args.seeds.split(",") if s.strip()]
    if not seeds:
        print("Error: provide at least one seed word.", file=sys.stderr)
        return 1

    results = generate(seeds, args.pattern, args.count)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(render_human(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
