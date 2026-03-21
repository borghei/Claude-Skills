#!/usr/bin/env python3
"""
Job Posting Analyzer - Analyze job descriptions for bias, readability, and quality.

Reads a job description file (plain text or markdown) and scores it across
multiple dimensions: inclusive language, readability, structure completeness,
requirement inflation, and gendered language.

Usage:
    python job_posting_analyzer.py --file job_description.md
    python job_posting_analyzer.py --file job_description.md --json

Input: Plain text or markdown file containing a job description.

Output: Quality score with category breakdowns and actionable recommendations.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter


# --- Bias and language detection word lists ---

MASCULINE_CODED = [
    "aggressive", "ambitious", "analytical", "assertive", "autonomous",
    "boast", "champion", "competitive", "confident", "courage",
    "decisive", "determined", "dominant", "driven", "fearless",
    "force", "headstrong", "hero", "hostile", "hustle",
    "independent", "individual", "lead", "logic", "ninja",
    "objective", "opinion", "outspoken", "persist", "principle",
    "rockstar", "self-reliant", "strong", "superior", "tackle",
    "thrust", "warrior",
]

FEMININE_CODED = [
    "agree", "affectionate", "caring", "collaborate", "commit",
    "communal", "compassion", "connect", "considerate", "cooperate",
    "depend", "emotional", "empathy", "feel", "gentle",
    "honest", "interpersonal", "kind", "loyal", "modesty",
    "nurture", "pleasant", "polite", "quiet", "responsible",
    "share", "submit", "support", "sympathetic", "tender",
    "together", "trust", "understand", "warm", "yield",
]

EXCLUSIONARY_PHRASES = [
    "native english speaker",
    "young and dynamic",
    "digital native",
    "culture fit",
    "man enough",
    "manpower",
    "chairman",
    "he/his",
    "she/her",
    "able-bodied",
    "normal",
    "walk to",
    "stand for extended",
    "clean-shaven",
    "must be available 24/7",
]

JARGON_WORDS = [
    "synergy", "leverage", "paradigm", "disrupt", "bleeding edge",
    "move the needle", "circle back", "deep dive", "low-hanging fruit",
    "thought leader", "game changer", "best-in-class", "world-class",
    "fast-paced environment", "wear many hats", "self-starter",
    "hit the ground running", "rock star", "guru", "wizard",
]

REQUIRED_SECTIONS = [
    "responsibilities",
    "requirements",
    "qualifications",
    "compensation",
    "salary",
    "benefits",
    "about",
    "the role",
    "what you",
    "who you",
]


def read_file(path: str) -> str:
    """Read file contents."""
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def count_sentences(text: str) -> int:
    """Count sentences in text."""
    sentences = re.split(r"[.!?]+", text)
    return max(1, len([s for s in sentences if s.strip()]))


def flesch_reading_ease(text: str) -> float:
    """
    Approximate Flesch Reading Ease score.
    Higher = easier to read. Target: 60-70 for job postings.
    """
    words = text.split()
    word_count = len(words)
    if word_count == 0:
        return 0.0
    sentence_count = count_sentences(text)
    # Approximate syllables: count vowel groups per word
    syllable_count = 0
    for word in words:
        word_lower = word.lower().strip(".,!?;:'\"()-")
        vowels = re.findall(r"[aeiouy]+", word_lower)
        syllable_count += max(1, len(vowels))
    score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
    return round(max(0, min(100, score)), 1)


def find_word_matches(text: str, word_list: list) -> list:
    """Find words from word_list that appear in text."""
    text_lower = text.lower()
    found = []
    for word in word_list:
        pattern = r"\b" + re.escape(word) + r"\w*\b"
        if re.search(pattern, text_lower):
            found.append(word)
    return found


def find_phrase_matches(text: str, phrase_list: list) -> list:
    """Find phrases from phrase_list that appear in text."""
    text_lower = text.lower()
    return [p for p in phrase_list if p in text_lower]


def count_requirements(text: str) -> dict:
    """Count and categorize requirements."""
    lines = text.split("\n")
    bullet_lines = [l.strip() for l in lines if re.match(r"^\s*[-*]\s+", l)]

    years_mentions = re.findall(r"(\d+)\+?\s*(?:years?|yrs?)", text.lower())
    max_years = max([int(y) for y in years_mentions], default=0)

    must_have = []
    nice_to_have = []
    in_must = False
    in_nice = False

    for line in lines:
        lower = line.lower().strip()
        if "must have" in lower or "required" in lower or "requirements" in lower:
            in_must = True
            in_nice = False
        elif "nice to have" in lower or "preferred" in lower or "bonus" in lower:
            in_nice = True
            in_must = False
        elif re.match(r"^#{1,3}\s+", line):
            in_must = False
            in_nice = False
        elif re.match(r"^\s*[-*]\s+", line):
            if in_must:
                must_have.append(line.strip())
            elif in_nice:
                nice_to_have.append(line.strip())

    return {
        "total_bullet_points": len(bullet_lines),
        "must_have_count": len(must_have),
        "nice_to_have_count": len(nice_to_have),
        "max_years_experience": max_years,
    }


def check_sections(text: str) -> dict:
    """Check which recommended sections are present."""
    text_lower = text.lower()
    found = []
    missing = []
    for section in REQUIRED_SECTIONS:
        if section in text_lower:
            found.append(section)
        else:
            missing.append(section)
    return {"found": found, "missing": missing}


def calculate_scores(text: str) -> dict:
    """Calculate all analysis scores."""
    word_count = count_words(text)
    readability = flesch_reading_ease(text)

    masculine = find_word_matches(text, MASCULINE_CODED)
    feminine = find_word_matches(text, FEMININE_CODED)
    exclusionary = find_phrase_matches(text, EXCLUSIONARY_PHRASES)
    jargon = find_word_matches(text, JARGON_WORDS)
    jargon += find_phrase_matches(text, JARGON_WORDS)
    jargon = list(set(jargon))

    requirements = count_requirements(text)
    sections = check_sections(text)

    # --- Scoring (0-100 per category) ---

    # Gender neutrality: penalize imbalance and exclusionary terms
    masc_count = len(masculine)
    fem_count = len(feminine)
    gender_balance = abs(masc_count - fem_count)
    gender_score = max(0, 100 - gender_balance * 10 - len(exclusionary) * 20)

    # Readability: target 60-70
    if 55 <= readability <= 75:
        readability_score = 100
    elif 45 <= readability < 55 or 75 < readability <= 85:
        readability_score = 80
    elif 30 <= readability < 45 or 85 < readability <= 95:
        readability_score = 60
    else:
        readability_score = 40

    # Length: target 300-800 words
    if 300 <= word_count <= 800:
        length_score = 100
    elif 200 <= word_count < 300 or 800 < word_count <= 1000:
        length_score = 80
    elif 100 <= word_count < 200 or 1000 < word_count <= 1500:
        length_score = 60
    else:
        length_score = 40

    # Requirements: penalize excessive must-haves and high year requirements
    must_haves = requirements["must_have_count"]
    if must_haves <= 7:
        req_score = 100
    elif must_haves <= 10:
        req_score = 80
    elif must_haves <= 15:
        req_score = 60
    else:
        req_score = 40
    if requirements["max_years_experience"] > 10:
        req_score = max(0, req_score - 20)

    # Structure: based on sections found
    section_ratio = len(sections["found"]) / len(REQUIRED_SECTIONS)
    structure_score = round(section_ratio * 100)

    # Jargon: penalize buzzwords
    jargon_score = max(0, 100 - len(jargon) * 15)

    # Overall weighted score
    overall = round(
        gender_score * 0.25
        + readability_score * 0.20
        + length_score * 0.10
        + req_score * 0.15
        + structure_score * 0.15
        + jargon_score * 0.15
    )

    return {
        "overall_score": overall,
        "word_count": word_count,
        "flesch_reading_ease": readability,
        "categories": {
            "gender_neutrality": {
                "score": gender_score,
                "masculine_coded_words": masculine,
                "feminine_coded_words": feminine,
                "exclusionary_phrases": exclusionary,
            },
            "readability": {
                "score": readability_score,
                "flesch_reading_ease": readability,
            },
            "length": {
                "score": length_score,
                "word_count": word_count,
                "target_range": "300-800 words",
            },
            "requirements": {
                "score": req_score,
                "must_have_count": requirements["must_have_count"],
                "nice_to_have_count": requirements["nice_to_have_count"],
                "max_years_experience": requirements["max_years_experience"],
                "total_bullet_points": requirements["total_bullet_points"],
            },
            "structure": {
                "score": structure_score,
                "sections_found": sections["found"],
                "sections_missing": sections["missing"],
            },
            "jargon": {
                "score": jargon_score,
                "jargon_found": jargon,
            },
        },
    }


def build_recommendations(results: dict) -> list:
    """Generate actionable recommendations from scores."""
    recs = []
    cats = results["categories"]

    if cats["gender_neutrality"]["score"] < 80:
        if cats["gender_neutrality"]["masculine_coded_words"]:
            recs.append(
                f"Replace masculine-coded words ({', '.join(cats['gender_neutrality']['masculine_coded_words'][:5])}) "
                "with neutral alternatives to broaden the candidate pool."
            )
        if cats["gender_neutrality"]["exclusionary_phrases"]:
            recs.append(
                f"Remove exclusionary phrases: {', '.join(cats['gender_neutrality']['exclusionary_phrases'])}."
            )

    if cats["readability"]["score"] < 80:
        recs.append(
            f"Improve readability (current Flesch score: {cats['readability']['flesch_reading_ease']}). "
            "Use shorter sentences and simpler vocabulary. Target a Flesch score of 60-70."
        )

    if cats["length"]["score"] < 80:
        wc = cats["length"]["word_count"]
        if wc < 300:
            recs.append(f"Expand the posting ({wc} words). Add more detail about responsibilities, team, and benefits. Target 300-800 words.")
        else:
            recs.append(f"Shorten the posting ({wc} words). Consolidate overlapping requirements and remove filler. Target 300-800 words.")

    if cats["requirements"]["score"] < 80:
        if cats["requirements"]["must_have_count"] > 7:
            recs.append(
                f"Reduce must-have requirements from {cats['requirements']['must_have_count']} to 5-7. "
                "Move non-essential items to nice-to-have. Excessive requirements deter qualified candidates, especially from underrepresented groups."
            )
        if cats["requirements"]["max_years_experience"] > 8:
            recs.append(
                f"Reconsider the {cats['requirements']['max_years_experience']}+ year experience requirement. "
                "Research shows years of experience is a weak predictor of performance beyond 5 years."
            )

    if cats["structure"]["score"] < 80:
        recs.append(
            f"Add missing sections: {', '.join(cats['structure']['sections_missing'][:5])}. "
            "Job postings with compensation info receive 30% more applications."
        )

    if cats["jargon"]["score"] < 80:
        recs.append(
            f"Remove jargon and buzzwords: {', '.join(cats['jargon']['jargon_found'][:5])}. "
            "Use concrete language that describes actual work."
        )

    if not recs:
        recs.append("This job posting scores well across all dimensions. No critical improvements needed.")

    return recs


def format_human(results: dict, recommendations: list) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 60)
    lines.append("JOB POSTING ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append("")

    overall = results["overall_score"]
    grade = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D" if overall >= 40 else "F"
    lines.append(f"  Overall Score: {overall}/100 (Grade: {grade})")
    lines.append(f"  Word Count: {results['word_count']}")
    lines.append(f"  Readability: {results['flesch_reading_ease']} (Flesch Reading Ease)")
    lines.append("")

    lines.append("-" * 60)
    lines.append("CATEGORY SCORES")
    lines.append("-" * 60)

    cats = results["categories"]
    for name, data in cats.items():
        label = name.replace("_", " ").title()
        score = data["score"]
        bar = "#" * (score // 5) + "." * (20 - score // 5)
        lines.append(f"  {label:.<30} {score:>3}/100  [{bar}]")

    lines.append("")
    lines.append("-" * 60)
    lines.append("DETAILS")
    lines.append("-" * 60)

    gender = cats["gender_neutrality"]
    if gender["masculine_coded_words"]:
        lines.append(f"  Masculine-coded: {', '.join(gender['masculine_coded_words'])}")
    if gender["feminine_coded_words"]:
        lines.append(f"  Feminine-coded:  {', '.join(gender['feminine_coded_words'])}")
    if gender["exclusionary_phrases"]:
        lines.append(f"  Exclusionary:    {', '.join(gender['exclusionary_phrases'])}")

    reqs = cats["requirements"]
    lines.append(f"  Must-haves: {reqs['must_have_count']}  |  Nice-to-haves: {reqs['nice_to_have_count']}  |  Max years: {reqs['max_years_experience']}")

    if cats["jargon"]["jargon_found"]:
        lines.append(f"  Jargon found: {', '.join(cats['jargon']['jargon_found'])}")

    lines.append("")
    lines.append("-" * 60)
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 60)
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"  {i}. {rec}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze job descriptions for bias, readability, and quality."
    )
    parser.add_argument("--file", required=True, help="Path to job description file (text or markdown)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    text = read_file(args.file)
    results = calculate_scores(text)
    recommendations = build_recommendations(results)

    if args.json:
        output = {**results, "recommendations": recommendations}
        print(json.dumps(output, indent=2))
    else:
        print(format_human(results, recommendations))


if __name__ == "__main__":
    main()
