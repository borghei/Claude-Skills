#!/usr/bin/env python3
"""
AI SERP Simulator

Simulates how content might appear when extracted by AI search systems.
Identifies the most likely extractable blocks, previews citation snippets,
and scores extraction readiness per content section.

Usage:
    python serp_simulator.py --content page.md --query "what is cloud cost optimization"
    python serp_simulator.py --content page.md --query "how to reduce AWS costs" --json
    python serp_simulator.py --content page.md --query "best cloud optimization tools" --top 5
"""

import argparse
import json
import re
import sys
from pathlib import Path


def tokenize(text):
    """Simple word tokenization."""
    return re.findall(r'\b[a-z0-9]+\b', text.lower())


def extract_sections(text):
    """Split content into sections by headings."""
    sections = []
    current_heading = "Introduction"
    current_level = 0
    current_content = []

    for line in text.splitlines():
        heading_match = re.match(r'^(#{1,6})\s+(.+)', line)
        if heading_match:
            if current_content:
                content_text = "\n".join(current_content).strip()
                if content_text:
                    sections.append({
                        "heading": current_heading,
                        "level": current_level,
                        "content": content_text,
                        "word_count": len(content_text.split()),
                    })
            current_level = len(heading_match.group(1))
            current_heading = heading_match.group(2).strip()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        content_text = "\n".join(current_content).strip()
        if content_text:
            sections.append({
                "heading": current_heading,
                "level": current_level,
                "content": content_text,
                "word_count": len(content_text.split()),
            })

    return sections


def extract_paragraphs(text):
    """Split content into individual paragraphs."""
    paragraphs = []
    for block in re.split(r'\n\s*\n', text):
        block = block.strip()
        if block and not block.startswith('#') and len(block.split()) >= 10:
            paragraphs.append(block)
    return paragraphs


def extract_lists(text):
    """Extract numbered and bulleted lists."""
    lists = []
    current_list = []
    in_list = False

    for line in text.splitlines():
        is_list_item = bool(re.match(r'^\s*(\d+[\.\)]|\-|\*)\s+', line))
        if is_list_item:
            current_list.append(line.strip())
            in_list = True
        else:
            if in_list and current_list:
                lists.append("\n".join(current_list))
                current_list = []
            in_list = False

    if current_list:
        lists.append("\n".join(current_list))

    return lists


def extract_tables(text):
    """Extract markdown tables."""
    tables = []
    current_table = []
    in_table = False

    for line in text.splitlines():
        if '|' in line and line.strip().startswith('|'):
            current_table.append(line.strip())
            in_table = True
        else:
            if in_table and len(current_table) >= 3:
                tables.append("\n".join(current_table))
            current_table = []
            in_table = False

    if in_table and len(current_table) >= 3:
        tables.append("\n".join(current_table))

    return tables


def score_relevance(query, text):
    """Score relevance of text block to query using term overlap."""
    query_tokens = set(tokenize(query))
    text_tokens = tokenize(text)
    text_token_set = set(text_tokens)

    if not query_tokens:
        return 0.0

    # Term overlap
    overlap = query_tokens & text_token_set
    overlap_ratio = len(overlap) / len(query_tokens)

    # Term frequency boost
    freq_boost = 0
    for token in query_tokens:
        count = text_tokens.count(token)
        if count > 0:
            freq_boost += min(count / len(text_tokens) * 100, 5)

    # Position bonus (earlier = better)
    first_500 = " ".join(text.split()[:500]).lower()
    position_bonus = 0
    for token in query_tokens:
        if token in first_500:
            position_bonus += 0.1

    score = (overlap_ratio * 60) + (freq_boost * 5) + (position_bonus * 10)
    return min(round(score, 1), 100)


def classify_block_type(text):
    """Classify an extractable block by type."""
    if re.search(r'^\s*\d+[\.\)]\s+', text, re.MULTILINE):
        return "numbered_steps"
    if re.search(r'^\s*[\-\*]\s+', text, re.MULTILINE):
        return "bullet_list"
    if '|' in text and text.strip().startswith('|'):
        return "table"
    if re.search(r'\b(is|refers to|means|defined as)\b.*\.', text[:300], re.IGNORECASE):
        return "definition"
    if '?' in text.split('\n')[0] if text.split('\n') else False:
        return "faq_answer"
    return "paragraph"


def generate_snippet(text, max_chars=300):
    """Generate a citation snippet from a block."""
    clean = re.sub(r'\s+', ' ', text).strip()
    if len(clean) <= max_chars:
        return clean
    # Cut at sentence boundary
    truncated = clean[:max_chars]
    last_period = truncated.rfind('.')
    if last_period > max_chars * 0.5:
        return truncated[:last_period + 1]
    return truncated + "..."


def simulate_extraction(content, query, top_n=5):
    """Simulate AI extraction process on content."""
    blocks = []

    # Extract different block types
    paragraphs = extract_paragraphs(content)
    for p in paragraphs:
        blocks.append({"text": p, "source": "paragraph"})

    lists = extract_lists(content)
    for l in lists:
        blocks.append({"text": l, "source": "list"})

    tables = extract_tables(content)
    for t in tables:
        blocks.append({"text": t, "source": "table"})

    sections = extract_sections(content)
    for s in sections:
        if s["word_count"] >= 20:
            blocks.append({"text": s["content"], "source": f"section:{s['heading']}"})

    # Score and rank
    scored_blocks = []
    for block in blocks:
        relevance = score_relevance(query, block["text"])
        block_type = classify_block_type(block["text"])
        word_count = len(block["text"].split())

        # Type bonus
        type_bonus = {
            "definition": 15,
            "numbered_steps": 12,
            "table": 10,
            "faq_answer": 12,
            "bullet_list": 5,
            "paragraph": 0,
        }.get(block_type, 0)

        # Length penalty (too short or too long)
        length_penalty = 0
        if word_count < 20:
            length_penalty = -20
        elif word_count > 500:
            length_penalty = -10

        final_score = min(relevance + type_bonus + length_penalty, 100)

        scored_blocks.append({
            "text": block["text"],
            "source": block["source"],
            "block_type": block_type,
            "word_count": word_count,
            "relevance_score": relevance,
            "type_bonus": type_bonus,
            "final_score": max(final_score, 0),
            "snippet": generate_snippet(block["text"]),
        })

    # Sort by final score
    scored_blocks.sort(key=lambda x: x["final_score"], reverse=True)

    # Deduplicate (remove blocks with >80% text overlap)
    deduplicated = []
    seen_snippets = set()
    for block in scored_blocks:
        snippet_key = block["snippet"][:100]
        if snippet_key not in seen_snippets:
            deduplicated.append(block)
            seen_snippets.add(snippet_key)

    return deduplicated[:top_n]


def main():
    parser = argparse.ArgumentParser(
        description="Simulate AI search extraction from content"
    )
    parser.add_argument(
        "--content", required=True,
        help="Path to content file (Markdown or HTML)"
    )
    parser.add_argument(
        "--query", required=True,
        help="Search query to simulate"
    )
    parser.add_argument(
        "--top", type=int, default=5,
        help="Number of top extractable blocks to show (default: 5)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    filepath = Path(args.content)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    content = filepath.read_text(encoding="utf-8", errors="replace")
    results = simulate_extraction(content, args.query, args.top)

    output = {
        "query": args.query,
        "file": str(filepath),
        "total_word_count": len(content.split()),
        "top_extractable_blocks": results,
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  AI SERP SIMULATION")
        print(f"{'='*60}")
        print(f"  Query: {args.query}")
        print(f"  File: {filepath}")
        print(f"  Content: {len(content.split())} words")
        print()

        if not results:
            print("  No extractable blocks found matching the query.")
        else:
            for i, block in enumerate(results, 1):
                print(f"  --- Block #{i} (Score: {block['final_score']}/100) ---")
                print(f"  Type: {block['block_type']} | Words: {block['word_count']} | Source: {block['source']}")
                print(f"  Snippet preview:")
                # Wrap snippet for display
                snippet = block["snippet"]
                for line in [snippet[j:j+70] for j in range(0, len(snippet), 70)]:
                    print(f"    {line}")
                print()

        print(f"  Total blocks analyzed: {len(results)}")
        print()


if __name__ == "__main__":
    main()
