#!/usr/bin/env python3
"""
Resume Matcher — score keyword match between a resume and a job description.

Usage:
    python resume_matcher.py resume.txt jd.txt
    python resume_matcher.py resume.txt jd.txt --json
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


STOPWORDS = {
    "a", "an", "and", "or", "but", "if", "while", "with", "at", "by", "for",
    "to", "of", "in", "on", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "should", "could", "may", "might", "must", "can", "shall",
    "the", "this", "that", "these", "those", "it", "its", "their", "our",
    "your", "his", "her", "they", "them", "we", "us", "you", "i", "me",
    "my", "mine", "ours", "yours", "theirs", "who", "whom", "what", "which",
    "when", "where", "why", "how", "all", "any", "both", "each", "few",
    "more", "most", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "s", "t", "just", "now", "also",
    "well", "etc",
}

# Words that look like generic JD filler — boring matches we down-weight
FILLER = {
    "experience", "experienced", "team", "teams", "work", "working", "ability",
    "skills", "skill", "responsibility", "responsibilities", "role", "roles",
    "position", "candidate", "candidates", "job", "company", "companies",
    "year", "years", "months", "month", "day", "days", "person", "people",
    "ideal", "great", "strong", "good", "excellent", "best", "looking",
    "join", "help", "ensure", "support",
}


def tokenize(text: str) -> list:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#./\- ]", " ", text)
    raw = text.split()
    out = []
    for t in raw:
        t = t.strip(".-/")
        if not t:
            continue
        out.append(t)
        # Also emit hyphen-separated parts so "postgres-backed" still
        # contributes "postgres" and "backed" to keyword overlap.
        if "-" in t:
            for part in t.split("-"):
                part = part.strip(".-/")
                if part:
                    out.append(part)
    return out


def keyword_set(tokens: list) -> Counter:
    return Counter(
        t for t in tokens
        if len(t) > 1
        and t not in STOPWORDS
        and not t.isdigit()
    )


def score(resume_text: str, jd_text: str) -> dict:
    resume_tokens = tokenize(resume_text)
    jd_tokens = tokenize(jd_text)

    resume_kw = keyword_set(resume_tokens)
    jd_kw = keyword_set(jd_tokens)

    # JD keywords that survive filler filter — these are what we score against
    jd_signal = Counter({k: v for k, v in jd_kw.items() if k not in FILLER})

    if not jd_signal:
        return {
            "score": 0,
            "kept": [],
            "missing": [],
            "resume_only": [],
            "note": "Job description is empty or contains only filler words.",
        }

    # Weight each JD keyword by its JD frequency (capped to avoid one term dominating)
    weights = {k: min(v, 3) for k, v in jd_signal.items()}
    total_weight = sum(weights.values())

    kept_weight = sum(w for k, w in weights.items() if k in resume_kw)

    raw_score = (kept_weight / total_weight) * 100 if total_weight else 0

    kept = sorted(
        [k for k in jd_signal if k in resume_kw],
        key=lambda k: -weights[k],
    )
    missing = sorted(
        [k for k in jd_signal if k not in resume_kw],
        key=lambda k: -weights[k],
    )
    resume_only = sorted(
        [k for k in resume_kw if k not in jd_signal and k not in FILLER],
        key=lambda k: -resume_kw[k],
    )[:30]

    return {
        "score": round(raw_score, 1),
        "kept": kept[:50],
        "missing": missing[:50],
        "resume_only": resume_only,
    }


def render_human(result: dict) -> str:
    lines = []
    lines.append(f"Match score: {result['score']}%")
    if "note" in result:
        lines.append(f"Note: {result['note']}")
        return "\n".join(lines)
    lines.append("")
    lines.append(f"Kept keywords ({len(result['kept'])}):")
    lines.append("  " + ", ".join(result["kept"]) if result["kept"] else "  (none)")
    lines.append("")
    lines.append(f"Missing keywords ({len(result['missing'])}):")
    lines.append("  " + ", ".join(result["missing"]) if result["missing"] else "  (none)")
    lines.append("")
    lines.append(f"Resume-only keywords (top {len(result['resume_only'])}):")
    lines.append("  " + ", ".join(result["resume_only"]) if result["resume_only"] else "  (none)")
    lines.append("")
    if result["score"] >= 80:
        lines.append("Verdict: strong match — submit and tailor cover letter.")
    elif result["score"] >= 60:
        lines.append("Verdict: moderate match — close 3-5 of the missing keywords first.")
    else:
        lines.append("Verdict: weak match — either rewrite significantly or skip the role.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Score resume vs. job description match.")
    parser.add_argument("resume", help="Path to resume text file")
    parser.add_argument("jd", help="Path to job description text file")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable")
    args = parser.parse_args()

    try:
        resume_text = Path(args.resume).read_text(encoding="utf-8")
        jd_text = Path(args.jd).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = score(resume_text, jd_text)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
