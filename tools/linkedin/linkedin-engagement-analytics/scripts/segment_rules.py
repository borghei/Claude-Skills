#!/usr/bin/env python3
"""Title-parsing vocabularies and fit rules behind the engager segmenter.

Classifies a job headline into a seniority band and a function using ordered
keyword rules, splits "Title at Company" headlines, decides how well an engager
fits a stated target audience, and computes a Wilson interval for a share.
Run directly to print the vocabularies or to test one headline.

Usage:
    python3 segment_rules.py --list-rules
    python3 segment_rules.py --classify "VP Platform Engineering at Example Co"
    python3 segment_rules.py --classify "Head of Data" --format json

Exit codes:
    0  output printed
    2  bad arguments
"""

import argparse
import json
import math
import re
import sys
from typing import Any, Dict, List, Tuple

# Ordered: the first band whose pattern matches wins. Order resolves overlaps
# such as "Vice President" (vp) versus "President" (executive).
SENIORITY: List[Tuple[str, str]] = [
    ("individual_contributor", r"\b(?:executive assistant|personal assistant|assistant to)\b"),
    ("founder_owner", r"\b(?:co-?founder|founder|owner|proprietor|founding partner)\b"),
    ("vp", r"\b(?:s?vp|evp|avp|vice[- ]president)\b"),
    ("executive", r"\b(?:chief|ceo|cto|cfo|coo|cmo|cro|cpo|cio|ciso|chro|president|"
                  r"managing director|general manager|managing partner)\b|^(?:senior |equity |general )?partner$"),
    ("director", r"\b(?:director|head of|head,)\b"),
    ("manager_lead", r"\b(?:manager|supervisor|team leader)\b|\blead\b(?! gen)"),
    ("early_career", r"\b(?:student|intern|trainee|apprentice|graduate|undergraduate)\b"),
    ("individual_contributor",
     r"\b(?:engineer|developer|analyst|designer|consultant|specialist|executive|"
     r"representative|associate|coordinator|scientist|architect|writer|recruiter|"
     r"accountant|advisor|adviser|researcher|officer|administrator|strategist|"
     r"marketer|editor|planner|technician|nurse|teacher|lecturer|counsel)\b"),
]

# Ordered: specific functions before general ones.
FUNCTION: List[Tuple[str, str]] = [
    ("people", r"\b(?:hr|human resources|people (?:ops|operations|partner|team|and culture|& culture)|"
               r"(?:head|director|vp|chief) of people|chief people|talent|recruiter|recruiting|"
               r"recruitment|chro|learning and development)\b"),
    ("data", r"\b(?:data|analytics|machine learning|ml|ai|business intelligence|statistician)\b"),
    ("engineering", r"\b(?:engineer(?:ing)?|developer|software|devops|sre|platform|infrastructure|"
                    r"architect|cto|technical|qa|security|information technology|it (?:manager|director|lead))\b"),
    ("design", r"\b(?:design(?:er)?|ux|ui|creative|art director)\b"),
    ("marketing", r"\b(?:marketing|marketer|brand|content|growth|seo|demand generation|lead generation|"
                  r"communications|public relations|cmo|social media)\b"),
    ("product", r"\b(?:product|cpo)\b"),
    ("sales", r"\b(?:sales|account executive|business development|bdr|sdr|revenue|cro|"
              r"partnerships|account manager|commercial)\b"),
    ("customer_success", r"\b(?:customer success|customer support|technical support|support (?:engineer|"
                         r"specialist|lead|manager)|customer experience|implementation|client services)\b"),
    ("finance", r"\b(?:finance|financial|accounting|accountant|controller|cfo|treasury|fp&a|audit)\b"),
    ("legal", r"\b(?:legal|counsel|lawyer|attorney|solicitor|compliance|paralegal)\b"),
    ("operations", r"\b(?:operations|ops|supply chain|logistics|procurement|coo|project manager|"
                   r"programme manager|program manager|chief of staff)\b"),
    ("consulting", r"\b(?:consultant|consulting|advisor|adviser|coach|freelance|agency)\b"),
    ("education", r"\b(?:professor|lecturer|teacher|student|phd|researcher|academic)\b"),
    ("general_management", r"\b(?:ceo|founder|co-?founder|owner|president|managing director|"
                           r"general manager|managing partner)\b"),
]

SENIORITY_BANDS: Tuple[str, ...] = tuple(dict.fromkeys(n for n, _ in SENIORITY)) + ("unknown",)
FUNCTIONS: Tuple[str, ...] = tuple(name for name, _ in FUNCTION) + ("unknown",)
FIT_LEVELS: Tuple[str, ...] = ("core", "adjacent", "off")
COMPANY_SPLIT = re.compile(r"\s(?:at|@)\s", re.IGNORECASE)


def split_headline(headline: str, company: str = "") -> Tuple[str, str]:
    """Split a headline into (title text, company), preferring a supplied company."""
    headline = " ".join(str(headline or "").split())
    company = " ".join(str(company or "").split())
    if company:
        return headline, company
    parts = COMPANY_SPLIT.split(headline)
    if len(parts) < 2:
        return headline, ""
    tail = re.split(r"\s[|•·]\s", parts[-1])[0].strip(" .,")
    return " at ".join(parts[:-1]).strip(), tail


def first_match(text: str, rules: List[Tuple[str, str]]) -> str:
    """Return the name of the first rule whose pattern matches, else 'unknown'."""
    lowered = text.lower()
    for name, pattern in rules:
        if re.search(pattern, lowered):
            return name
    return "unknown"


def classify(headline: str, company: str = "") -> Dict[str, str]:
    """Classify one headline into title, company, seniority band and function."""
    title, org = split_headline(headline, company)
    seniority = first_match(title, SENIORITY)
    function = first_match(title, FUNCTION)
    if seniority == "unknown" and function != "unknown":
        seniority = "individual_contributor"
    return {"title": title, "company": org, "seniority": seniority, "function": function}


def norm_company(name: str) -> str:
    """Normalise a company name for matching: case, punctuation, legal suffixes."""
    cleaned = re.sub(r"[^a-z0-9& ]+", " ", str(name or "").lower())
    cleaned = re.sub(r"\b(?:inc|ltd|llc|gmbh|plc|limited|corp|corporation|co|bv|ab|sa|ag)\b", " ", cleaned)
    return " ".join(cleaned.split())


def fit_level(person: Dict[str, str], target: Dict[str, Any]) -> str:
    """Rate an engager against the target audience as core, adjacent or off.

    Core needs the seniority to match and either the function or a title
    keyword to match. Adjacent means exactly one of those two held. An empty
    list in the target means that dimension is unconstrained.
    """
    wanted_seniority = [str(s).lower() for s in target.get("seniority") or []]
    wanted_functions = [str(f).lower() for f in target.get("functions") or []]
    keywords = [str(k).lower() for k in target.get("title_keywords") or []]
    title = person["title"].lower()
    seniority_ok = not wanted_seniority or person["seniority"] in wanted_seniority
    keyword_hit = any(re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", title)
                      for k in keywords)
    role_ok = (not wanted_functions and not keywords) or person["function"] in wanted_functions or keyword_hit
    if seniority_ok and role_ok:
        return "core"
    return "adjacent" if seniority_ok or role_ok else "off"


def wilson(successes: int, total: int, z: float = 1.96) -> Tuple[float, float]:
    """Return the Wilson score interval for a proportion (95% by default)."""
    if total <= 0:
        return 0.0, 0.0
    p = successes / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def compare(low: float, high: float, reference: float) -> str:
    """Say whether a reference share sits below, inside or above an interval."""
    if low > reference:
        return "above"
    if high < reference:
        return "below"
    return "within"


def validate_target(target: Dict[str, Any]) -> List[str]:
    """Return problems with a target audience definition; empty when usable."""
    problems: List[str] = []
    for value in target.get("seniority") or []:
        if str(value).lower() not in SENIORITY_BANDS:
            problems.append(f"unknown seniority band '{value}'")
    for value in target.get("functions") or []:
        if str(value).lower() not in FUNCTIONS:
            problems.append(f"unknown function '{value}'")
    if not any(target.get(k) for k in ("seniority", "functions", "title_keywords")):
        problems.append("target needs at least one of seniority, functions, title_keywords")
    return problems


def list_rules(fmt: str) -> None:
    """Print the seniority and function vocabularies in match order."""
    if fmt == "json":
        print(json.dumps({"seniority": [{"band": n, "pattern": p} for n, p in SENIORITY],
                          "function": [{"function": n, "pattern": p} for n, p in FUNCTION],
                          "fit_levels": FIT_LEVELS}, indent=2))
        return
    print("Seniority bands (first match wins)")
    print("=" * 72)
    for name, pattern in SENIORITY:
        print(f"  {name:<24}{pattern}")
    print("\nFunctions (first match wins)")
    print("=" * 72)
    for name, pattern in FUNCTION:
        print(f"  {name:<24}{pattern}")
    print("\nA headline with a function but no seniority cue is an individual_contributor.")
    print("Fit: core = seniority and (function or keyword); adjacent = one of the two; off = neither.")


def main() -> None:
    """Parse arguments, then list the rules or classify one headline."""
    parser = argparse.ArgumentParser(
        description="Print the title-parsing rules used by engager_segmenter.py, "
                    "or classify a single headline to test them.",
        epilog="Exit codes: 0 output printed, 2 bad arguments.")
    parser.add_argument("--list-rules", action="store_true",
                        help="Print seniority and function patterns in match order.")
    parser.add_argument("--classify", metavar="HEADLINE", default=None,
                        help="Classify one job headline and print the result.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if args.classify is not None:
        if not args.classify.strip():
            print("ERROR: --classify needs a non-empty headline in quotes.", file=sys.stderr)
            sys.exit(2)
        result = classify(args.classify)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            for key, value in result.items():
                print(f"{key:<10} {value or '-'}")
        return
    if not args.list_rules:
        parser.print_help(sys.stderr)
        print("\nERROR: nothing to do. Pass --list-rules or --classify \"<headline>\".", file=sys.stderr)
        sys.exit(2)
    list_rules(args.format)


if __name__ == "__main__":
    main()
