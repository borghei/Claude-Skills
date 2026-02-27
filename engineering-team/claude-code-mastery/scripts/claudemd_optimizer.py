#!/usr/bin/env python3
"""
CLAUDE.md Optimizer - Analyze and optimize CLAUDE.md files

Produces actionable recommendations covering structure, token efficiency,
redundancy detection, and completeness. Helps keep CLAUDE.md files lean
and effective.

Usage:
    python claudemd_optimizer.py path/to/CLAUDE.md
    python claudemd_optimizer.py CLAUDE.md --token-limit 4000
    python claudemd_optimizer.py CLAUDE.md --json
"""

import argparse
import json
import re
import sys
import textwrap
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Approximate characters per token for Claude models
CHARS_PER_TOKEN = 3.5

# Recommended sections for a CLAUDE.md file
RECOMMENDED_SECTIONS = {
    "project purpose": {
        "aliases": ["project purpose", "project overview", "about", "overview", "what is this"],
        "importance": "critical",
        "description": "One paragraph explaining what the project is and who it serves",
    },
    "architecture overview": {
        "aliases": ["architecture", "structure", "directory structure", "repository structure", "project structure"],
        "importance": "critical",
        "description": "Directory layout, key patterns, data flow",
    },
    "development environment": {
        "aliases": ["development environment", "development", "setup", "getting started", "quick start", "dev setup", "build", "environment"],
        "importance": "critical",
        "description": "Build commands, test commands, environment setup",
    },
    "key principles": {
        "aliases": ["key principles", "principles", "guidelines", "rules", "conventions", "standards"],
        "importance": "high",
        "description": "3-7 non-obvious rules Claude must follow",
    },
    "anti-patterns": {
        "aliases": ["anti-patterns", "anti patterns", "don't", "avoid", "pitfalls", "common mistakes"],
        "importance": "high",
        "description": "Things that look reasonable but are wrong in this project",
    },
    "git workflow": {
        "aliases": ["git workflow", "git", "branching", "branch strategy", "commits", "version control"],
        "importance": "medium",
        "description": "Branch strategy, commit conventions, PR process",
    },
    "testing": {
        "aliases": ["testing", "tests", "test", "test commands", "how to test"],
        "importance": "medium",
        "description": "How to run tests, testing conventions, coverage targets",
    },
}

# Patterns that indicate redundant or generic content
GENERIC_PATTERNS = [
    (r"write clean[,\s]+readable code", "Generic advice - Claude already writes clean code"),
    (r"follow best practices", "Too vague - specify which practices"),
    (r"use meaningful variable names", "Generic advice - already default behavior"),
    (r"add comments where necessary", "Generic advice - specify commenting standards if non-obvious"),
    (r"handle errors? (properly|gracefully|appropriately)", "Too vague - specify error handling patterns"),
    (r"write unit tests", "Too vague without specifying framework, coverage target, or patterns"),
    (r"keep (it|things|code) (simple|dry|clean)", "Generic advice - specify concrete constraints"),
    (r"follow the (existing|current) (patterns?|conventions?|style)", "Good intent but vague - specify which patterns"),
    (r"make sure to (test|validate|verify)", "Generic - specify what and how"),
    (r"ensure (code )?quality", "Too vague - specify quality metrics or checks"),
]

# Patterns that suggest content could be more concise
VERBOSITY_PATTERNS = [
    (r"it is important to note that", "Remove filler phrase"),
    (r"please (make sure|ensure|remember) (to|that)", "Remove politeness filler"),
    (r"you should (always|never)", "Simplify to direct instruction"),
    (r"in order to", "Replace with 'to'"),
    (r"at this point in time", "Replace with 'now' or remove"),
    (r"due to the fact that", "Replace with 'because'"),
    (r"it goes without saying", "If obvious, remove entirely"),
    (r"as a matter of fact", "Remove filler"),
]


def estimate_tokens(text: str) -> int:
    """Estimate token count from text length."""
    return int(len(text) / CHARS_PER_TOKEN)


def extract_sections(text: str) -> List[Dict]:
    """Extract markdown sections with their content."""
    sections = []
    lines = text.split("\n")
    current_section = None
    current_content = []
    current_level = 0

    for line in lines:
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            if current_section is not None:
                content_text = "\n".join(current_content).strip()
                sections.append({
                    "title": current_section,
                    "level": current_level,
                    "content": content_text,
                    "line_count": len([l for l in current_content if l.strip()]),
                    "token_estimate": estimate_tokens(content_text),
                })
            current_level = len(heading_match.group(1))
            current_section = heading_match.group(2).strip()
            current_content = []
        else:
            current_content.append(line)

    # Don't forget the last section
    if current_section is not None:
        content_text = "\n".join(current_content).strip()
        sections.append({
            "title": current_section,
            "level": current_level,
            "content": content_text,
            "line_count": len([l for l in current_content if l.strip()]),
            "token_estimate": estimate_tokens(content_text),
        })

    return sections


def check_section_completeness(sections: List[Dict]) -> List[Dict]:
    """Check which recommended sections are present and which are missing."""
    results = []
    section_titles_lower = [s["title"].lower() for s in sections]

    for section_name, info in RECOMMENDED_SECTIONS.items():
        found = False
        matched_title = None
        for alias in info["aliases"]:
            for title in section_titles_lower:
                if alias in title or title in alias:
                    found = True
                    matched_title = title
                    break
            if found:
                break

        results.append({
            "section": section_name,
            "importance": info["importance"],
            "found": found,
            "matched_as": matched_title,
            "description": info["description"],
        })

    return results


def detect_redundancy(text: str) -> List[Dict]:
    """Detect redundant phrases and repeated instructions."""
    issues = []

    # Check for generic/redundant patterns
    for pattern, message in GENERIC_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            issues.append({
                "type": "generic_content",
                "pattern": pattern,
                "message": message,
                "occurrences": len(matches),
            })

    # Check for verbosity patterns
    for pattern, message in VERBOSITY_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            issues.append({
                "type": "verbose_phrasing",
                "pattern": pattern,
                "message": message,
                "occurrences": len(matches),
            })

    # Check for repeated sentences (exact duplicates)
    sentences = re.split(r"[.!?]\s+", text)
    sentences_clean = [s.strip().lower() for s in sentences if len(s.strip()) > 20]
    sentence_counts = Counter(sentences_clean)
    for sentence, count in sentence_counts.items():
        if count > 1:
            issues.append({
                "type": "duplicate_sentence",
                "message": f"Sentence appears {count} times: \"{sentence[:80]}...\"",
                "occurrences": count,
            })

    # Check for repeated phrases (3+ word sequences appearing 3+ times)
    words = text.lower().split()
    trigrams = [" ".join(words[i : i + 3]) for i in range(len(words) - 2)]
    trigram_counts = Counter(trigrams)
    for trigram, count in trigram_counts.items():
        if count >= 4 and len(trigram) > 10:
            # Skip very common phrases
            common_skip = {"in the the", "of the the", "and the the"}
            if trigram not in common_skip:
                issues.append({
                    "type": "repeated_phrase",
                    "message": f"Phrase \"{trigram}\" appears {count} times",
                    "occurrences": count,
                })

    return issues


def suggest_hierarchical_loading(text: str, sections: List[Dict], token_limit: int) -> List[str]:
    """Suggest sections that could be moved to child CLAUDE.md files."""
    suggestions = []
    total_tokens = estimate_tokens(text)

    if total_tokens <= token_limit:
        return suggestions

    overage = total_tokens - token_limit
    suggestions.append(
        f"File is ~{total_tokens} tokens, {overage} tokens over the {token_limit} token target."
    )

    # Find the largest sections that could be moved
    movable_sections = sorted(
        [s for s in sections if s["level"] == 2 and s["token_estimate"] > 200],
        key=lambda s: s["token_estimate"],
        reverse=True,
    )

    tokens_to_move = 0
    for section in movable_sections:
        if tokens_to_move >= overage:
            break
        suggestions.append(
            f"Move \"{section['title']}\" (~{section['token_estimate']} tokens) "
            f"to a child CLAUDE.md or reference file"
        )
        tokens_to_move += section["token_estimate"]

    return suggestions


def generate_recommendations(
    text: str,
    sections: List[Dict],
    completeness: List[Dict],
    redundancies: List[Dict],
    hierarchical: List[str],
    token_limit: int,
) -> List[Dict]:
    """Generate prioritized optimization recommendations."""
    recommendations = []
    total_tokens = estimate_tokens(text)
    line_count = len(text.split("\n"))

    # Check for missing critical sections
    for check in completeness:
        if not check["found"] and check["importance"] == "critical":
            recommendations.append({
                "priority": "high",
                "category": "completeness",
                "message": f"Add missing critical section: {check['section']} -- {check['description']}",
            })

    # Check for missing high-importance sections
    for check in completeness:
        if not check["found"] and check["importance"] == "high":
            recommendations.append({
                "priority": "medium",
                "category": "completeness",
                "message": f"Consider adding section: {check['section']} -- {check['description']}",
            })

    # Token budget recommendations
    if total_tokens > token_limit:
        recommendations.append({
            "priority": "high",
            "category": "token_budget",
            "message": f"File exceeds target of {token_limit} tokens ({total_tokens} current). "
                       f"Use hierarchical loading to reduce.",
        })

    if total_tokens > token_limit * 2:
        recommendations.append({
            "priority": "high",
            "category": "token_budget",
            "message": "File is more than double the target size. Major restructuring recommended.",
        })

    # Redundancy recommendations
    generic_count = sum(1 for r in redundancies if r["type"] == "generic_content")
    if generic_count > 0:
        recommendations.append({
            "priority": "medium",
            "category": "redundancy",
            "message": f"Found {generic_count} generic/vague instructions. "
                       f"Replace with specific, actionable guidance or remove.",
        })

    verbose_count = sum(1 for r in redundancies if r["type"] == "verbose_phrasing")
    if verbose_count > 0:
        recommendations.append({
            "priority": "low",
            "category": "redundancy",
            "message": f"Found {verbose_count} verbose phrases that can be simplified.",
        })

    duplicate_count = sum(1 for r in redundancies if r["type"] == "duplicate_sentence")
    if duplicate_count > 0:
        recommendations.append({
            "priority": "medium",
            "category": "redundancy",
            "message": f"Found {duplicate_count} duplicate sentences. Remove repetition.",
        })

    # Structure recommendations
    if line_count > 300:
        recommendations.append({
            "priority": "medium",
            "category": "structure",
            "message": f"File is {line_count} lines. Consider splitting into hierarchical CLAUDE.md files.",
        })

    h2_sections = [s for s in sections if s["level"] == 2]
    if len(h2_sections) > 10:
        recommendations.append({
            "priority": "low",
            "category": "structure",
            "message": f"File has {len(h2_sections)} top-level sections. Consider consolidating.",
        })

    # Check for YAML frontmatter (not required for CLAUDE.md but good to flag)
    if text.strip().startswith("---"):
        # Check if frontmatter is well-formed
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            if not frontmatter:
                recommendations.append({
                    "priority": "low",
                    "category": "structure",
                    "message": "YAML frontmatter is empty. Either add content or remove the delimiters.",
                })

    # Format recommendations
    bullet_lines = sum(1 for line in text.split("\n") if line.strip().startswith(("- ", "* ", "1.")))
    paragraph_lines = sum(
        1
        for line in text.split("\n")
        if len(line.strip()) > 80 and not line.strip().startswith(("#", "-", "*", "|", "`", ">"))
    )
    if paragraph_lines > bullet_lines and paragraph_lines > 10:
        recommendations.append({
            "priority": "medium",
            "category": "format",
            "message": "Heavy use of paragraphs. Bullet points are ~30% more token-efficient "
                       "and easier for Claude to parse.",
        })

    # Add hierarchical loading suggestions
    for suggestion in hierarchical:
        recommendations.append({
            "priority": "medium",
            "category": "hierarchical_loading",
            "message": suggestion,
        })

    return recommendations


def analyze_claudemd(file_path: str, token_limit: int = 6000) -> Dict:
    """Perform full analysis of a CLAUDE.md file."""
    path = Path(file_path)

    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    if not path.is_file():
        return {"success": False, "error": f"Not a file: {file_path}"}

    text = path.read_text(encoding="utf-8")

    line_count = len(text.split("\n"))
    non_empty_lines = len([l for l in text.split("\n") if l.strip()])
    char_count = len(text)
    token_estimate = estimate_tokens(text)
    word_count = len(text.split())

    sections = extract_sections(text)
    completeness = check_section_completeness(sections)
    redundancies = detect_redundancy(text)
    hierarchical = suggest_hierarchical_loading(text, sections, token_limit)
    recommendations = generate_recommendations(
        text, sections, completeness, redundancies, hierarchical, token_limit
    )

    # Compute a simple score
    score = 100
    for rec in recommendations:
        if rec["priority"] == "high":
            score -= 15
        elif rec["priority"] == "medium":
            score -= 8
        elif rec["priority"] == "low":
            score -= 3
    score = max(0, min(100, score))

    return {
        "success": True,
        "file": str(path.resolve()),
        "metrics": {
            "line_count": line_count,
            "non_empty_lines": non_empty_lines,
            "character_count": char_count,
            "word_count": word_count,
            "token_estimate": token_estimate,
            "token_limit": token_limit,
            "within_budget": token_estimate <= token_limit,
            "section_count": len(sections),
        },
        "sections": [
            {"title": s["title"], "level": s["level"], "tokens": s["token_estimate"], "lines": s["line_count"]}
            for s in sections
        ],
        "completeness": completeness,
        "redundancies": redundancies,
        "recommendations": recommendations,
        "score": score,
    }


def print_human_readable(result: Dict) -> None:
    """Print analysis results in a human-readable format."""
    if not result["success"]:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    m = result["metrics"]
    print("=" * 64)
    print("  CLAUDE.md Analysis Report")
    print("=" * 64)
    print(f"  File:            {result['file']}")
    print(f"  Score:           {result['score']}/100")
    print(f"  Lines:           {m['line_count']} ({m['non_empty_lines']} non-empty)")
    print(f"  Words:           {m['word_count']}")
    print(f"  Characters:      {m['character_count']}")
    print(f"  Token estimate:  ~{m['token_estimate']} tokens")
    budget_status = "WITHIN BUDGET" if m["within_budget"] else "OVER BUDGET"
    print(f"  Token budget:    {m['token_limit']} tokens ({budget_status})")
    print(f"  Sections:        {m['section_count']}")
    print()

    # Section breakdown
    print("--- Section Breakdown ---")
    for s in result["sections"]:
        indent = "  " * (s["level"] - 1)
        print(f"  {indent}{'#' * s['level']} {s['title']}  (~{s['tokens']} tokens, {s['lines']} lines)")
    print()

    # Completeness check
    print("--- Section Completeness ---")
    for check in result["completeness"]:
        icon = "[FOUND]  " if check["found"] else "[MISSING]"
        imp = check["importance"].upper()
        print(f"  {icon} {check['section']} ({imp})")
        if not check["found"]:
            print(f"           -> {check['description']}")
    print()

    # Redundancies
    if result["redundancies"]:
        print("--- Redundancy Issues ---")
        for r in result["redundancies"]:
            print(f"  [{r['type']}] {r['message']}")
        print()

    # Recommendations
    if result["recommendations"]:
        print("--- Recommendations ---")
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_recs = sorted(result["recommendations"], key=lambda r: priority_order.get(r["priority"], 3))
        for rec in sorted_recs:
            tag = rec["priority"].upper()
            print(f"  [{tag}] ({rec['category']}) {rec['message']}")
        print()

    if result["score"] >= 80:
        print("Overall: Good shape. Minor optimizations available.")
    elif result["score"] >= 50:
        print("Overall: Several improvements recommended. Focus on HIGH priority items.")
    else:
        print("Overall: Significant restructuring recommended.")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a CLAUDE.md file and suggest optimizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
Examples:
    python claudemd_optimizer.py CLAUDE.md
    python claudemd_optimizer.py path/to/CLAUDE.md --token-limit 4000
    python claudemd_optimizer.py CLAUDE.md --json
        """),
    )
    parser.add_argument(
        "file_path",
        help="Path to the CLAUDE.md file to analyze",
    )
    parser.add_argument(
        "--token-limit",
        type=int,
        default=6000,
        help="Maximum recommended token count (default: 6000)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    args = parser.parse_args()

    result = analyze_claudemd(args.file_path, args.token_limit)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human_readable(result)

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
