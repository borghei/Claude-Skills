#!/usr/bin/env python3
"""Rule data and text primitives behind the LinkedIn profile auditor.

Holds the rule catalogue (id, section, severity, fix), the goal-specific
section weights, the filler and duty-language vocabularies, and the small text
helpers the auditor shares. Run it directly to print the catalogue.

Usage:
    python3 profile_rules.py --list-rules
    python3 profile_rules.py --list-rules --section headline --format json

Exit codes:
    0  catalogue printed
    2  bad arguments
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Tuple

# Platform limits, current as of writing. Verify in the product before relying
# on them; both are overridable from the auditor's command line.
LIMITS: Dict[str, int] = {"headline_chars": 220, "about_chars": 2600,
                          "about_preview_chars": 260}

SEVERITY_PENALTY: Dict[str, int] = {"high": 34, "medium": 17, "low": 8}
SEVERITY_RANK: Dict[str, int] = {"high": 0, "medium": 1, "low": 2}
SECTIONS: Tuple[str, ...] = ("headline", "about", "experience", "skills",
                             "featured", "visuals", "credibility")

# How much each section counts toward the overall score, by profile goal.
GOAL_WEIGHTS: Dict[str, Dict[str, int]] = {
    "clients": {"headline": 20, "about": 20, "experience": 10, "skills": 5,
                "featured": 20, "visuals": 15, "credibility": 10},
    "job_search": {"headline": 15, "about": 15, "experience": 25, "skills": 15,
                   "featured": 10, "visuals": 10, "credibility": 10},
    "authority": {"headline": 20, "about": 20, "experience": 10, "skills": 5,
                  "featured": 25, "visuals": 10, "credibility": 10},
    "hiring": {"headline": 20, "about": 25, "experience": 15, "skills": 5,
               "featured": 15, "visuals": 10, "credibility": 10},
}

# Featured item types each goal needs at least one of, per slot.
FEATURED_SLOTS: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "clients": {"proof": ("case_study", "testimonial", "results_post"),
                "door": ("booking_link", "contact_page", "lead_magnet", "newsletter")},
    "job_search": {"proof": ("portfolio", "project", "work_sample", "case_study"),
                   "depth": ("post", "article", "talk")},
    "authority": {"depth": ("article", "post", "talk", "research"),
                  "door": ("newsletter", "book", "podcast", "contact_page")},
    "hiring": {"proof": ("team_story", "culture_post", "engineering_blog", "post"),
               "door": ("careers_page", "open_role", "contact_page")},
}

FILLER: Tuple[str, ...] = (
    "passionate", "results-driven", "results-oriented", "driven professional",
    "thought leader", "visionary", "guru", "ninja", "rockstar", "dynamic",
    "seasoned", "proven track record", "detail-oriented", "go-getter",
    "synergy", "innovative leader", "strategic thinker", "self-starter",
    "out-of-the-box", "world-class", "serial entrepreneur", "evangelist")

WEAK_OPENERS: Tuple[str, ...] = (
    "responsible for", "worked on", "helped", "assisted", "participated in",
    "handled", "duties included", "tasked with", "involved in", "supported",
    "in charge of", "was part of", "contributed to")

GREETINGS: Tuple[str, ...] = ("welcome", "hello", "hi ", "hi,", "hey",
                              "thanks for visiting", "thank you for visiting")

NEXT_STEP_CUES: Tuple[str, ...] = (
    "email", "message me", "send me", "write to", "book", "dm ", "reach me",
    "get in touch", "contact", "subscribe", "apply", "see the featured",
    "link below", "@", "http")

GENERIC_TITLE_CUES: Tuple[str, ...] = (
    "my blog", "blog post", "presentation", "untitled", "document", "pdf",
    "slides", "my website", "link", "article")

TITLE_ONLY = re.compile(r"^[^|•·:–—]{2,50}\s(?:at|@)\s[^|•·:–—]{2,40}$", re.IGNORECASE)
THIRD_PERSON = re.compile(r"\b(?:he|she)\s+(?:is|has|was|leads|works|brings)\b", re.IGNORECASE)
DEFAULT_URL = re.compile(r"-[0-9a-z]*\d[0-9a-z]{4,}/?$", re.IGNORECASE)

# id -> (section, severity, problem, fix)
RULES: Dict[str, Tuple[str, str, str, str]] = {
    "HL-01": ("headline", "high", "Headline is empty",
              "Write one: searchable role, who the work is for, and one reason to believe it."),
    "HL-02": ("headline", "high", "Headline is only a job title and employer",
              "Keep the role as the anchor, then add the audience and an outcome or proof point."),
    "HL-03": ("headline", "medium", "None of the target search terms appear in the headline",
              "Work the one or two terms people actually search for into the first half."),
    "HL-04": ("headline", "medium", "Headline never says who the work is for",
              "Name the audience in their own words (role, sector, or company stage)."),
    "HL-05": ("headline", "low", "Headline uses a small fraction of the available length",
              "Add a second clause: an outcome, a proof point, or a specialism."),
    "HL-06": ("headline", "high", "Headline is over the character limit",
              "Cut the weakest clause; the product will truncate it otherwise."),
    "HL-07": ("headline", "medium", "Headline leans on filler vocabulary",
              "Replace each self-description with the thing it was standing in for."),
    "HL-08": ("headline", "low", "Headline shouts (capitals or an emoji chain)",
              "Use sentence or title case and at most one separator style."),
    "AB-01": ("about", "high", "About section is empty",
              "Draft it with the five-move arc in references/headline-and-about.md."),
    "AB-02": ("about", "medium", "About is written in the third person",
              "Rewrite as 'I'. A profile is a first-person document."),
    "AB-03": ("about", "high", "The preview before the fold carries nothing specific",
              "Open with a claim, a number, or the reader's problem, not a greeting or a biography."),
    "AB-04": ("about", "medium", "About is too thin to carry proof",
              "Add the fit, proof and method moves; aim for several short paragraphs."),
    "AB-05": ("about", "high", "About is over the character limit",
              "Cut biography first, then method detail; keep the proof."),
    "AB-06": ("about", "medium", "About makes claims without concrete evidence",
              "Add at least two specifics: a figure, a scope, a named artefact, a before and after."),
    "AB-07": ("about", "low", "About is a single block of text",
              "Break it into short paragraphs with blank lines between them."),
    "AB-08": ("about", "medium", "About ends without a next step",
              "Close with one action: how to reach you and what to send."),
    "AB-09": ("about", "medium", "About leans on filler vocabulary",
              "Delete each adjective and see whether the sentence still says something."),
    "AB-10": ("about", "low", "Most target search terms are missing from the About",
              "Use the terms in ordinary sentences; do not append a keyword list."),
    "EX-01": ("experience", "high", "No experience entries supplied",
              "Add at least the current role and the one before it."),
    "EX-02": ("experience", "high", "Current role has no description",
              "Add a one-line remit and three result bullets to the role visitors read first."),
    "EX-03": ("experience", "medium", "Earlier roles are titles with no description",
              "Give each role from the last ten years a remit line and one or two results."),
    "EX-04": ("experience", "medium", "Bullets describe duties rather than results",
              "Start with the verb for what changed, then say how much and over what scope."),
    "EX-05": ("experience", "medium", "Few bullets carry a measurable result",
              "Add a figure, a scope, or a before and after to at least one bullet in three."),
    "EX-06": ("experience", "low", "Roles have no skills attached",
              "Attach the skills each role actually used so they are evidenced, not just listed."),
    "EX-07": ("experience", "low", "No role has attached proof",
              "Attach one artefact (talk, write-up, launch page) to the current role."),
    "SK-01": ("skills", "high", "Skills list is nearly empty",
              "List the terms a searcher would type for your work; start with ten."),
    "SK-02": ("skills", "medium", "Top skill slots are not deliberately set",
              "Choose exactly three for the top slots; they are the only ones most visitors see."),
    "SK-03": ("skills", "medium", "Top skills do not match the target search terms",
              "Swap in the skills that mirror your target terms."),
    "SK-04": ("skills", "low", "Target search terms are missing from the skills list",
              "Add each missing term as a skill if you can evidence it in a role."),
    "FT-01": ("featured", "high", "Featured section is empty",
              "Fill the slots for your goal; see references/featured-and-visuals.md."),
    "FT-02": ("featured", "medium", "Featured is missing a slot this goal needs",
              "Add one item of the missing kind before adding anything else."),
    "FT-03": ("featured", "low", "Featured items are stale",
              "Replace anything older than a year unless it is still your best proof."),
    "FT-04": ("featured", "low", "Featured titles describe the format, not the payoff",
              "Retitle each item with what the visitor gets from opening it."),
    "FT-05": ("featured", "low", "Featured holds more items than a visitor will scan",
              "Cut to the strongest three or four."),
    "VS-01": ("visuals", "high", "No profile photo",
              "Add a recent, well-lit head-and-shoulders photo of you alone."),
    "VS-02": ("visuals", "medium", "Photo fails a basic check",
              "Retake it: alone, face clearly visible, plain background, recent."),
    "VS-03": ("visuals", "medium", "Banner is missing or the default",
              "Replace it; the default signals an unfinished profile."),
    "VS-04": ("visuals", "low", "Banner does not say anything",
              "Put one line on it: what you do or what to do next."),
    "VS-05": ("visuals", "medium", "Banner has not been checked against the photo overlap",
              "Keep text clear of the photo area and check it on a phone."),
    "CR-01": ("credibility", "low", "Profile URL is the default or missing",
              "Claim a clean name-based URL in the public profile settings."),
    "CR-02": ("credibility", "medium", "No recommendations",
              "Ask two people who saw specific work; give them the specifics."),
    "CR-03": ("credibility", "low", "Recommendations are old or generic",
              "Request one from current work that names a project and an outcome."),
    "CR-04": ("credibility", "low", "Recommendations all come from one kind of relationship",
              "Add a different vantage point: a client, a manager, a report, a peer."),
}


def hit(rule_id: str, evidence: str) -> Dict[str, str]:
    """Build a finding record for a rule id with the observed evidence."""
    section, severity, problem, fix = RULES[rule_id]
    return {"id": rule_id, "section": section, "severity": severity,
            "problem": problem, "evidence": evidence, "fix": fix}


def has_term(text: str, term: str) -> bool:
    """Return True when a term appears in the text as a whole word or phrase."""
    term = term.strip().lower()
    if not term:
        return False
    return re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])",
                     text.lower()) is not None


def terms_found(text: str, terms: List[str]) -> List[str]:
    """Return the subset of terms that appear in the text."""
    return [t for t in terms if has_term(text, str(t))]


def filler_hits(text: str) -> List[str]:
    """Return the filler phrases present in the text."""
    return [f for f in FILLER if has_term(text, f)]


def number_count(text: str) -> int:
    """Count numeric tokens, treating 1,200 and 3.5 as one token each."""
    return len(re.findall(r"\d+(?:[.,]\d+)*", text))


def emoji_count(text: str) -> int:
    """Count characters in the main emoji and pictograph code-point ranges."""
    return sum(1 for ch in text if 0x1F300 <= ord(ch) <= 0x1FAFF
               or 0x2600 <= ord(ch) <= 0x27BF)


def starts_with_any(text: str, openers: Tuple[str, ...]) -> bool:
    """Return True when the text begins with one of the given phrases."""
    lowered = text.strip().lower().lstrip("-*• ")
    return any(lowered.startswith(o) for o in openers)


def audit_visuals(p: Dict[str, Any]) -> List[Dict[str, str]]:
    """Check the self-reported photo and banner answers."""
    photo = p.get("photo") if isinstance(p.get("photo"), dict) else {}
    banner = p.get("banner") if isinstance(p.get("banner"), dict) else {}
    out: List[Dict[str, str]] = []
    if not photo.get("present"):
        out.append(hit("VS-01", "photo.present is false or unanswered"))
    else:
        failed = [k for k in ("solo", "face_clear", "plain_background") if photo.get(k) is False]
        if float(photo.get("age_years") or 0) > 4:
            failed.append("age_years")
        if failed:
            out.append(hit("VS-02", "failed: " + ", ".join(failed)))
    if not banner.get("present") or not banner.get("custom"):
        out.append(hit("VS-03", "banner absent or default"))
    else:
        if not banner.get("states_value"):
            out.append(hit("VS-04", "banner.states_value is false"))
        if not (banner.get("text_clear_of_photo") and banner.get("checked_on_mobile")):
            out.append(hit("VS-05", "overlap or mobile check not confirmed"))
    return out


def list_rules(section: str, fmt: str) -> None:
    """Print the rule catalogue, optionally filtered to one section."""
    rows = [{"id": rid, "section": r[0], "severity": r[1], "problem": r[2], "fix": r[3]}
            for rid, r in RULES.items() if section in ("all", r[0])]
    if fmt == "json":
        print(json.dumps({"limits": LIMITS, "goal_weights": GOAL_WEIGHTS,
                          "severity_penalty": SEVERITY_PENALTY, "rules": rows}, indent=2))
        return
    print(f"Profile audit rules ({len(rows)})")
    print("=" * 72)
    for row in rows:
        print(f"{row['id']}  [{row['severity']:<6}] {row['section']:<11} {row['problem']}")
        print(f"       fix: {row['fix']}")
    print("-" * 72)
    print("Section weights by goal:")
    for goal, weights in GOAL_WEIGHTS.items():
        print(f"  {goal:<11} " + ", ".join(f"{k} {v}" for k, v in weights.items()))


def main() -> None:
    """Parse arguments and print the rule catalogue."""
    parser = argparse.ArgumentParser(
        description="Print the rule catalogue used by profile_auditor.py.",
        epilog="Exit codes: 0 catalogue printed, 2 bad arguments.")
    parser.add_argument("--list-rules", action="store_true",
                        help="Print every rule with its severity and fix.")
    parser.add_argument("--section", choices=("all",) + SECTIONS, default="all",
                        help="Limit the listing to one profile section (default: all).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if not args.list_rules:
        parser.print_help(sys.stderr)
        print("\nERROR: nothing to do. Pass --list-rules.", file=sys.stderr)
        sys.exit(2)
    list_rules(args.section, args.format)


if __name__ == "__main__":
    main()
