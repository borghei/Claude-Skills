#!/usr/bin/env python3
"""Score a LinkedIn profile section by section and list the fixes in priority order.

Reads a profile pasted into JSON (see assets/profile_template.json) and checks
headline, About, experience, skills, Featured, visuals and credibility against
the catalogue in profile_rules.py. Offline: it never fetches a profile.

Usage:
    python3 profile_auditor.py --input profile.json
    python3 profile_auditor.py --input profile.json --goal job_search --format json
    python3 profile_auditor.py --input profile.json --fail-under 70

Exit codes:
    0  audit completed (and the score met --fail-under, if given)
    1  overall score is below --fail-under
    2  bad input: file missing, not valid JSON, or not a profile object
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profile_rules import (  # noqa: E402
    DEFAULT_URL, FEATURED_SLOTS, GENERIC_TITLE_CUES, GOAL_WEIGHTS, GREETINGS, LIMITS,
    NEXT_STEP_CUES, SECTIONS, SEVERITY_PENALTY, SEVERITY_RANK, THIRD_PERSON, TITLE_ONLY,
    WEAK_OPENERS, audit_visuals, emoji_count, filler_hits, hit, number_count,
    starts_with_any, terms_found)

Finding = Dict[str, str]


def fail(message: str) -> None:
    """Print an actionable error to stderr and exit with the bad-input code."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def load_profile(path: Path) -> Dict[str, Any]:
    """Load the profile JSON, exiting with guidance when it cannot be used."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"profile file not found: {path}. Copy assets/profile_template.json and fill it in.")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {path}: {exc}")
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON (line {exc.lineno}): {exc.msg}")
    if not isinstance(data, dict) or not any(k in data for k in ("headline", "about", "experience")):
        fail("profile must be a JSON object with at least one of 'headline', 'about', "
             "'experience'. See assets/sample_profile.json for the expected shape.")
    return data


def audit_headline(p: Dict[str, Any], limit: int) -> List[Finding]:
    """Check the headline for substance, search terms, audience and length."""
    text = str(p.get("headline") or "").strip()
    if not text:
        return [hit("HL-01", "headline field is blank")]
    out: List[Finding] = []
    if TITLE_ONLY.match(text) or len(text.split()) <= 4:
        out.append(hit("HL-02", f'"{text}"'))
    keywords = [str(k) for k in p.get("target_keywords") or []]
    if keywords and not terms_found(text, keywords):
        out.append(hit("HL-03", "looked for: " + ", ".join(keywords)))
    audience = [str(a) for a in p.get("audience_terms") or []]
    if audience and not terms_found(text, audience):
        out.append(hit("HL-04", "looked for: " + ", ".join(audience)))
    if len(text) > limit:
        out.append(hit("HL-06", f"{len(text)} characters against a limit of {limit}"))
    elif len(text) < 0.4 * limit:
        out.append(hit("HL-05", f"{len(text)} of {limit} characters used"))
    filler = filler_hits(text)
    if filler:
        out.append(hit("HL-07", "found: " + ", ".join(filler)))
    letters = [c for c in text if c.isalpha()]
    if (letters and sum(c.isupper() for c in letters) > 0.7 * len(letters)) or emoji_count(text) > 2:
        out.append(hit("HL-08", "mostly capitals or more than two emoji"))
    return out


def audit_about(p: Dict[str, Any], limit: int, preview: int) -> List[Finding]:
    """Check the About section's preview, voice, evidence, shape and close."""
    text = str(p.get("about") or "").strip()
    if not text:
        return [hit("AB-01", "about field is blank")]
    out: List[Finding] = []
    words = len(text.split())
    first_name = str(p.get("name") or "").split(" ")[0]
    named = bool(first_name) and re.search(
        rf"\b{re.escape(first_name)}\s+(?:is|has|was|leads|works)\b", text) is not None
    if named or THIRD_PERSON.search(text) or not re.search(r"\b(?:I|I'm|I've|my|me)\b", text):
        out.append(hit("AB-02", "no first-person voice detected"))
    opening = text[:preview]
    specifics = [str(t) for t in (p.get("audience_terms") or []) + (p.get("target_keywords") or [])]
    if starts_with_any(opening, GREETINGS) or not (number_count(opening) or terms_found(opening, specifics)):
        out.append(hit("AB-03", f'first {preview} characters: "{opening[:90].strip()}..."'))
    if len(text) > limit:
        out.append(hit("AB-05", f"{len(text)} characters against a limit of {limit}"))
    if words < 80:
        out.append(hit("AB-04", f"{words} words"))
    if number_count(text) < 2:
        out.append(hit("AB-06", f"{number_count(text)} numeric specifics found"))
    paragraphs = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
    if words > 100 and len(paragraphs) < 3:
        out.append(hit("AB-07", f"{words} words in {len(paragraphs)} paragraph(s)"))
    if not any(cue in text[-300:].lower() for cue in NEXT_STEP_CUES):
        out.append(hit("AB-08", "closing lines contain no contact or action cue"))
    filler = filler_hits(text)
    if filler:
        out.append(hit("AB-09", "found: " + ", ".join(filler)))
    keywords = [str(k) for k in p.get("target_keywords") or []]
    found = terms_found(text, keywords)
    if keywords and len(found) < len(keywords) / 2:
        out.append(hit("AB-10", f"{len(found)} of {len(keywords)} target terms present"))
    return out


def audit_experience(p: Dict[str, Any]) -> List[Finding]:
    """Check experience entries for descriptions, result language and proof."""
    roles = [r for r in p.get("experience") or [] if isinstance(r, dict)]
    if not roles:
        return [hit("EX-01", "experience list is empty")]
    out: List[Finding] = []

    def lines_of(role: Dict[str, Any]) -> List[str]:
        """Return a role's description lines and bullets as one list."""
        desc = [ln for ln in str(role.get("description") or "").splitlines() if ln.strip()]
        return desc + [str(b) for b in role.get("bullets") or [] if str(b).strip()]

    current = next((r for r in roles if str(r.get("end") or "present").lower() == "present"), roles[0])
    if not lines_of(current):
        out.append(hit("EX-02", f"{current.get('title', 'current role')} at {current.get('company', '?')}"))
    bare = [r for r in roles if r is not current and not lines_of(r)]
    if bare:
        out.append(hit("EX-03", f"{len(bare)} of {len(roles)} roles: "
                       + ", ".join(str(r.get("title", "?")) for r in bare)))
    bullets = [ln for r in roles for ln in lines_of(r)]
    weak = [b for b in bullets if starts_with_any(b, WEAK_OPENERS)]
    if weak:
        out.append(hit("EX-04", f'{len(weak)} of {len(bullets)} lines, e.g. "{weak[0][:70]}"'))
    measured = sum(1 for b in bullets if number_count(b))
    if bullets and measured < len(bullets) / 3:
        out.append(hit("EX-05", f"{measured} of {len(bullets)} lines contain a figure"))
    unskilled = [r for r in roles if not r.get("skills")]
    if len(unskilled) == len(roles):
        out.append(hit("EX-06", f"0 of {len(roles)} roles list skills"))
    if not any(int(r.get("media") or 0) for r in roles):
        out.append(hit("EX-07", "no role reports attached media"))
    return out


def audit_skills(p: Dict[str, Any]) -> List[Finding]:
    """Check the skills list size, the top slots and target-term coverage."""
    skills = p.get("skills") if isinstance(p.get("skills"), dict) else {}
    listed = [str(s) for s in skills.get("all") or []]
    pinned = [str(s) for s in skills.get("pinned") or []]
    out: List[Finding] = []
    if len(listed) < 5:
        out.append(hit("SK-01", f"{len(listed)} skills listed"))
    if len(pinned) != 3:
        out.append(hit("SK-02", f"{len(pinned)} top skills set"))
    keywords = [str(k) for k in p.get("target_keywords") or []]
    if keywords and pinned and not terms_found(" | ".join(pinned), keywords):
        out.append(hit("SK-03", "top skills: " + ", ".join(pinned)))
    missing = [k for k in keywords if k not in terms_found(" | ".join(listed), keywords)]
    if listed and missing:
        out.append(hit("SK-04", "missing: " + ", ".join(missing)))
    return out


def audit_featured(p: Dict[str, Any], goal: str) -> List[Finding]:
    """Check Featured items against the slots the profile goal needs."""
    items = [i for i in p.get("featured") or [] if isinstance(i, dict)]
    if not items:
        return [hit("FT-01", "featured list is empty")]
    out: List[Finding] = []
    types = {str(i.get("type") or "").lower() for i in items}
    missing = [slot for slot, kinds in FEATURED_SLOTS[goal].items() if not types & set(kinds)]
    if missing:
        out.append(hit("FT-02", f"goal '{goal}' has no item for: " + ", ".join(missing)))
    stale = [i for i in items if float(i.get("age_months") or 0) > 12]
    if stale:
        out.append(hit("FT-03", f"{len(stale)} of {len(items)} items older than 12 months"))
    generic = [str(i.get("title") or "") for i in items
               if len(str(i.get("title") or "").split()) < 3
               or any(cue in str(i.get("title")).lower() for cue in GENERIC_TITLE_CUES)]
    if generic:
        out.append(hit("FT-04", "titles: " + "; ".join(f'"{t}"' for t in generic)))
    if len(items) > 5:
        out.append(hit("FT-05", f"{len(items)} items"))
    return out


def audit_credibility(p: Dict[str, Any]) -> List[Finding]:
    """Check the public URL and the recommendations supplied."""
    out: List[Finding] = []
    url = str(p.get("custom_url") or "").strip()
    if not url or DEFAULT_URL.search(url):
        out.append(hit("CR-01", url or "custom_url is blank"))
    recs = [r for r in p.get("recommendations") or [] if isinstance(r, dict)]
    if not recs:
        return out + [hit("CR-02", "recommendations list is empty")]
    as_of = int(p.get("as_of_year") or 0)
    recent = [r for r in recs if as_of and as_of - int(r.get("year") or 0) <= 3]
    if (as_of and not recent) or not any(r.get("specific") for r in recs):
        out.append(hit("CR-03", f"{len(recent)} recent, "
                       f"{sum(1 for r in recs if r.get('specific'))} specific, of {len(recs)}"))
    if len(recs) > 1 and len({str(r.get("relationship")).lower() for r in recs}) == 1:
        out.append(hit("CR-04", f"all {len(recs)} from: {recs[0].get('relationship')}"))
    return out


def audit(profile: Dict[str, Any], goal: str, limits: Dict[str, int]) -> Dict[str, Any]:
    """Run every section check and assemble the weighted scorecard."""
    by_section = {
        "headline": audit_headline(profile, limits["headline_chars"]),
        "about": audit_about(profile, limits["about_chars"], limits["about_preview_chars"]),
        "experience": audit_experience(profile), "skills": audit_skills(profile),
        "featured": audit_featured(profile, goal), "visuals": audit_visuals(profile),
        "credibility": audit_credibility(profile)}
    weights = GOAL_WEIGHTS[goal]
    scorecard, fixes = [], []
    for section in SECTIONS:
        found = by_section[section]
        score = max(0, 100 - sum(SEVERITY_PENALTY[f["severity"]] for f in found))
        status = "pass" if score >= 80 else "needs work" if score >= 50 else "fail"
        scorecard.append({"section": section, "score": score, "status": status,
                          "weight": weights[section], "findings": len(found)})
        fixes.extend({**f, "priority": SEVERITY_PENALTY[f["severity"]] * weights[section]}
                     for f in found)
    fixes.sort(key=lambda f: (-f["priority"], SEVERITY_RANK[f["severity"]], f["id"]))
    overall = round(sum(s["score"] * s["weight"] for s in scorecard) / sum(weights.values()))
    return {"name": profile.get("name", "unknown"), "goal": goal, "overall_score": overall,
            "limits_used": limits, "scorecard": scorecard, "fixes": fixes}


def render(report: Dict[str, Any], fmt: str, top: int) -> None:
    """Print the scorecard and ordered fix list as JSON or text."""
    shown = report["fixes"][:top] if top else report["fixes"]
    if fmt == "json":
        print(json.dumps({**report, "fixes": shown}, indent=2))
        return
    print(f"Profile audit: {report['name']}   goal: {report['goal']}   "
          f"overall: {report['overall_score']}/100")
    print("=" * 72)
    for row in report["scorecard"]:
        print(f"  {row['section']:<12} {row['score']:>3}/100  {row['status']:<10} "
              f"weight {row['weight']:>2}  findings {row['findings']}")
    print("-" * 72)
    print(f"Fixes in priority order ({len(shown)} of {len(report['fixes'])}):")
    for n, f in enumerate(shown, 1):
        print(f"{n:>2}. [{f['severity'].upper():<6}] {f['id']}  {f['problem']}")
        print(f"      evidence: {f['evidence']}")
        print(f"      fix: {f['fix']}")
    if not shown:
        print("  No findings. Re-check the visuals by eye; the tool only sees your answers.")


def main() -> None:
    """Parse arguments, run the audit, print the report and apply the gate."""
    parser = argparse.ArgumentParser(
        description="Score a LinkedIn profile JSON section by section and list fixes "
                    "in priority order. Offline: reads only the file you supply.",
        epilog="Exit codes: 0 audit completed, 1 score below --fail-under, 2 bad input.")
    parser.add_argument("--input", required=True, help="Path to the profile JSON.")
    parser.add_argument("--goal", choices=sorted(GOAL_WEIGHTS), default=None,
                        help="Profile goal; overrides the 'goal' field in the file "
                             "(default: the file's value, else clients).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--top", type=int, default=0,
                        help="Show only the N highest-priority fixes (default: all).")
    parser.add_argument("--headline-limit", type=int, default=LIMITS["headline_chars"],
                        help="Headline character limit (default: %(default)s; verify in the product).")
    parser.add_argument("--about-preview", type=int, default=LIMITS["about_preview_chars"],
                        help="Characters assumed visible before the About fold (default: %(default)s).")
    parser.add_argument("--fail-under", type=int, default=None,
                        help="Exit 1 if the overall score is below this value.")
    args = parser.parse_args()

    profile = load_profile(Path(args.input))
    goal = args.goal or str(profile.get("goal") or "clients").lower()
    if goal not in GOAL_WEIGHTS:
        fail(f"unknown goal '{goal}' in the profile file. Use one of: " + ", ".join(sorted(GOAL_WEIGHTS)))
    limits = {**LIMITS, "headline_chars": args.headline_limit, "about_preview_chars": args.about_preview}
    try:
        report = audit(profile, goal, limits)
    except (TypeError, ValueError, AttributeError) as exc:
        fail(f"a field has the wrong type ({exc}). Compare your file with assets/profile_template.json.")
    render(report, args.format, args.top)
    if args.fail_under is not None and report["overall_score"] < args.fail_under:
        sys.exit(1)


if __name__ == "__main__":
    main()
