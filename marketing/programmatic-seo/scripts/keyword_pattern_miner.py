#!/usr/bin/env python3
"""
Keyword Pattern Miner for Programmatic SEO

Analyzes keyword lists to discover repeating patterns suitable for
programmatic page generation. Identifies variable slots, estimates
page set size, classifies volume tiers, and scores pSEO opportunity.

Usage:
    python keyword_pattern_miner.py --keywords keywords.csv --json
    python keyword_pattern_miner.py --keywords keywords.csv --min-pattern 5
    python keyword_pattern_miner.py --keywords keywords.csv --top 10
"""

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


def load_keywords(filepath):
    """Load keywords from CSV or text file."""
    keywords = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            sample = f.read(1024)
            f.seek(0)
            if ',' in sample or '\t' in sample:
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=',\t')
                except csv.Error:
                    dialect = csv.excel
                reader = csv.DictReader(f, dialect=dialect)
                for row in reader:
                    entry = {}
                    for key in ['keyword', 'Keyword', 'query', 'Query', 'term']:
                        if key in row and row[key]:
                            entry["keyword"] = row[key].strip()
                            break
                    if "keyword" not in entry and row:
                        entry["keyword"] = list(row.values())[0].strip()
                    for key in ['volume', 'Volume', 'search_volume']:
                        if key in row and row[key]:
                            try:
                                entry["volume"] = int(str(row[key]).replace(',', '').strip())
                            except ValueError:
                                pass
                    if entry.get("keyword"):
                        keywords.append(entry)
            else:
                for line in f:
                    kw = line.strip()
                    if kw:
                        keywords.append({"keyword": kw})
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    return keywords


def extract_patterns(keywords):
    """Discover repeating keyword patterns."""
    # Tokenize keywords and find common structures
    structures = defaultdict(list)

    for entry in keywords:
        kw = entry["keyword"].lower()
        words = kw.split()

        # Generate n-gram patterns with variable slots
        if len(words) >= 2:
            for i in range(len(words)):
                pattern_words = words[:]
                pattern_words[i] = "[VAR]"
                pattern = " ".join(pattern_words)
                structures[pattern].append(entry)

            # Two-variable patterns
            if len(words) >= 3:
                for i in range(len(words)):
                    for j in range(i + 1, len(words)):
                        pattern_words = words[:]
                        pattern_words[i] = "[VAR1]"
                        pattern_words[j] = "[VAR2]"
                        pattern = " ".join(pattern_words)
                        structures[pattern].append(entry)

    return structures


def analyze_patterns(structures, min_count=3):
    """Analyze and rank discovered patterns."""
    patterns = []

    for pattern, entries in structures.items():
        if len(entries) < min_count:
            continue

        # Extract unique variable values
        var_positions = [i for i, w in enumerate(pattern.split()) if w.startswith("[VAR")]
        variables = defaultdict(set)

        for entry in entries:
            words = entry["keyword"].lower().split()
            for pos in var_positions:
                if pos < len(words):
                    var_name = pattern.split()[pos]
                    variables[var_name].add(words[pos])

        # Calculate volume stats
        volumes = [e.get("volume", 0) or 0 for e in entries]
        total_volume = sum(volumes)
        avg_volume = total_volume / len(entries) if entries else 0

        # Classify volume tiers
        tiers = {"head": 0, "torso": 0, "long_tail": 0, "zero": 0}
        for v in volumes:
            if v >= 1000:
                tiers["head"] += 1
            elif v >= 100:
                tiers["torso"] += 1
            elif v >= 10:
                tiers["long_tail"] += 1
            else:
                tiers["zero"] += 1

        # Unique pages possible
        if len(var_positions) == 1:
            var_key = list(variables.keys())[0]
            unique_values = len(variables[var_key])
            max_pages = unique_values
        elif len(var_positions) == 2:
            keys = list(variables.keys())
            max_pages = len(variables[keys[0]]) * len(variables[keys[1]])
        else:
            max_pages = len(entries)

        patterns.append({
            "pattern": pattern,
            "keyword_count": len(entries),
            "unique_pages": max_pages,
            "variables": {k: list(v)[:20] for k, v in variables.items()},
            "variable_count": len(var_positions),
            "total_volume": total_volume,
            "avg_volume": round(avg_volume),
            "volume_tiers": tiers,
            "sample_keywords": [e["keyword"] for e in entries[:5]],
        })

    # Sort by keyword count * volume
    patterns.sort(key=lambda p: p["keyword_count"] * max(p["avg_volume"], 1), reverse=True)
    return patterns


def score_opportunity(pattern):
    """Score pSEO opportunity for a pattern."""
    score = 0

    # Volume factor (0-30)
    if pattern["total_volume"] >= 50000:
        score += 30
    elif pattern["total_volume"] >= 10000:
        score += 25
    elif pattern["total_volume"] >= 5000:
        score += 20
    elif pattern["total_volume"] >= 1000:
        score += 15
    else:
        score += 5

    # Scale factor (0-25)
    pages = pattern["unique_pages"]
    if 50 <= pages <= 5000:
        score += 25
    elif pages > 5000:
        score += 15  # Very large sets need more infrastructure
    elif pages >= 20:
        score += 15
    else:
        score += 5

    # Volume distribution (0-25)
    tiers = pattern["volume_tiers"]
    total = sum(tiers.values())
    if total > 0:
        head_pct = tiers["head"] / total
        torso_pct = tiers["torso"] / total
        if head_pct >= 0.05 and torso_pct >= 0.15:
            score += 25
        elif torso_pct >= 0.15:
            score += 20
        elif tiers["head"] >= 1:
            score += 15
        else:
            score += 5

    # Pattern simplicity (0-20)
    if pattern["variable_count"] == 1:
        score += 20
    elif pattern["variable_count"] == 2:
        score += 15
    else:
        score += 5

    return min(score, 100)


def main():
    parser = argparse.ArgumentParser(
        description="Mine keyword patterns for programmatic SEO"
    )
    parser.add_argument("--keywords", required=True, help="CSV file with keywords")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--min-pattern", type=int, default=3, help="Minimum keywords per pattern (default: 3)")
    parser.add_argument("--top", type=int, default=20, help="Top N patterns to show (default: 20)")
    args = parser.parse_args()

    fp = Path(args.keywords)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    keywords = load_keywords(fp)
    if not keywords:
        print("No keywords found.", file=sys.stderr)
        sys.exit(1)

    structures = extract_patterns(keywords)
    patterns = analyze_patterns(structures, args.min_pattern)

    # Score each pattern
    for p in patterns:
        p["opportunity_score"] = score_opportunity(p)

    # Re-sort by opportunity score
    patterns.sort(key=lambda p: p["opportunity_score"], reverse=True)
    patterns = patterns[:args.top]

    output = {
        "total_keywords": len(keywords),
        "patterns_found": len(patterns),
        "top_patterns": patterns,
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*70}")
        print(f"  KEYWORD PATTERN MINING — {len(keywords)} keywords")
        print(f"{'='*70}")
        print(f"  Patterns found: {len(patterns)}")

        for i, p in enumerate(patterns, 1):
            print(f"\n  --- Pattern #{i} (Score: {p['opportunity_score']}/100) ---")
            print(f"  Pattern: {p['pattern']}")
            print(f"  Keywords: {p['keyword_count']} | Pages: {p['unique_pages']} | Volume: {p['total_volume']}")
            print(f"  Tiers: Head={p['volume_tiers']['head']} Torso={p['volume_tiers']['torso']} Long-tail={p['volume_tiers']['long_tail']} Zero={p['volume_tiers']['zero']}")
            print(f"  Samples: {', '.join(p['sample_keywords'][:3])}")

        print()


if __name__ == "__main__":
    main()
