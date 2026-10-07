#!/usr/bin/env python3
"""Rule catalogue and text primitives behind the LinkedIn machine-tell audit.

Holds the three-tier catalogue (remove / reduce / review) that tell_audit.py
applies, plus the sentence, paragraph and word splitters every tool in this
skill shares. Run it directly to list the rules or to explain one of them.

Usage:
    python3 tell_rules.py --list
    python3 tell_rules.py --list --tier reduce --format json
    python3 tell_rules.py --explain RD-03

Exit codes: 0 ok, 2 bad input (unknown rule id).
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

TIERS = ("remove", "reduce", "review")
FLAGS = re.IGNORECASE | re.MULTILINE

STOCK_WORDS = (
    r"leverag\w*|utili[sz]\w*|harness\w*|unlock\w*|elevat\w*|empower\w*|streamlin\w*|"
    r"foster\w*|robust|seamless\w*|comprehensive|crucial|pivotal|holistic\w*|synerg\w*|"
    r"cutting-edge|game-chang\w*|transformative|revolutioni[sz]\w*|landscape|ecosystem|"
    r"paradigm\w*|nuanced|multifaceted|impactful|actionable|supercharg\w*|skyrocket\w*|"
    r"ever-evolving|fast-paced|best-in-class|world-class|next-level|deep dive|"
    r"move the needle|double down|unpack\w*|thought leader\w*")
STOCK_RE = re.compile(rf"\b(?:{STOCK_WORDS})\b", FLAGS)

# (id, tier, name, allowance, weight, pattern, scope, why, fix, keep_when)
_RAW = [
    ("RM-01", "remove", "Tool residue token", 0, 5,
     r"oaicite|contentReference|turn\d+(?:search|view|news)\d+|【[^】]*】|\[\d+†[^\]]*\]", "all",
     "Citation plumbing from a chat tool was pasted along with the text.",
     "Delete the token, then check the sentence it was attached to reads whole.", "Never."),
    ("RM-02", "remove", "Assistant preamble", 0, 5,
     r"^(?:sure|certainly|absolutely|of course|great question)[,!.]|"
     r"here(?:'s| is) (?:a|an|your|the|my) (?:\w+ ){0,3}(?:post|draft|version|rewrite)\b", "all",
     "The reply wrapper around the draft was copied in with the draft.",
     "Cut everything before the first line the author would actually say.", "Never."),
    ("RM-03", "remove", "Assistant sign-off", 0, 5,
     r"let me know if you(?:'d| would) like|i hope this helps|feel free to (?:adjust|tweak|edit)|"
     r"would you like me to|want me to (?:make|adjust|shorten)", "all",
     "An offer to revise is addressed to the author, not the audience.",
     "Delete the sentence.", "Never."),
    ("RM-04", "remove", "Model self-reference", 0, 5,
     r"as of my (?:last|latest) (?:update|training|knowledge)|as an ai\b|"
     r"i (?:don't|do not|cannot|can't) (?:have access to|browse|verify) ", "all",
     "A disclaimer about training data or access is a machine speaking about itself.",
     "Delete it and state the fact with its real date, or drop the claim.", "Never."),
    ("RM-05", "remove", "Unfilled placeholder", 0, 5,
     r"\[(?:your|insert|company|name|topic|link|number|role|industry|x)\b[^\]]*\]|"
     r"\{\{?\s*[a-z_ ]+\s*\}?\}|\bX{2,}\b|lorem ipsum|\bTK\b", "all",
     "A slot from a template shipped without its value.",
     "Fill it with the real value or delete the sentence. Do not guess the value.", "Never."),
    ("RM-06", "remove", "Unrendered markup", 0, 5,
     r"\*\*[^*\n]+\*\*|^#{1,6}\s+\S|\[[^\]\n]+\]\(https?://[^)]+\)|^```", "all",
     "The post composer shows asterisks and pound signs literally (as of writing).",
     "Strip the markup. Use a blank line or a plain label for emphasis.", "Never."),
    ("RM-07", "remove", "Leftover option label", 0, 5,
     r"^(?:option|version|variant|hook|draft) (?:[a-c]|[1-3])\s*[:.)-]|^(?:subject|title)\s*:",
     "all", "A label from a list of alternatives is still attached.",
     "Delete the label and keep one option.", "Never."),
    ("RD-01", "reduce", "Stock vocabulary", 1, 1, STOCK_WORDS, "all",
     "Abstract business words carry no information and arrive in bulk in generated text.",
     "Name the actual thing: the tool, the action, the number.",
     "It is a literal term of art (an insurer's 'comprehensive cover') or a product name."),
    ("RD-02", "reduce", "Empty intensifier", 2, 1,
     r"\b(?:truly|incredibly|fundamentally|essentially|ultimately|literally|absolutely|"
     r"extremely|undoubtedly|significantly|deeply|genuinely)\b", "all",
     "Intensifiers ask the reader to feel something the sentence did not earn.",
     "Delete the adverb. If the sentence goes flat, the sentence needs a fact.",
     "The word is doing contrast work ('literally' meaning not figuratively)."),
    ("RD-03", "reduce", "Contrast frame", 1, 2,
     r"\b(?:isn't|aren't|wasn't|is not|are not|not)\s+(?:just |only |merely |really |about )?"
     r"[^.,;:!?\n]{2,45}[.,;:—–-]+\s*(?:it's|it is|they're|that's|its)\b|"
     r"\bnot because\b[^.\n]{3,60}\bbut because\b|\bless about\b[^.\n]{2,40}\bmore about\b|"
     r"\bstop\b[^.\n]{2,40}[.,]\s*start\b", "all",
     "Denying a claim nobody made to set up the real one is the most recognisable frame.",
     "State the positive claim on its own and support it.",
     "The denied view is one a named person or the audience really holds; once per post."),
    ("RD-04", "reduce", "Question-and-answer bridge", 0, 2,
     r"\bthe (?:result|truth|catch|kicker|problem|reality|lesson|best part|difference|secret|"
     r"answer|outcome)\?|here's the (?:thing|kicker|catch|truth|deal)|plot twist|spoiler:|"
     r"\bwhy\? because\b|\bsound familiar\?|and (?:guess what|you know what)\?", "all",
     "A staged question answered in the next breath is a drumroll with nothing behind it.",
     "Delete the bridge. The following sentence was the point and stands alone.",
     "Rarely: a real question the author was asked, with the asker named."),
    ("RD-05", "reduce", "Triple list", 1, 1,
     r"\b[\w'-]+, [\w'-]+(?: [\w'-]+)?,? (?:and|or) [\w'-]+\b", "all",
     "Lists of exactly three recur far more often in generated text than in a person's drafts.",
     "Keep the items that are true and specific: usually two, sometimes four.",
     "There really are three things; keep one triple per post at most."),
    ("RD-06", "reduce", "Staccato fragments", 2, 1, None, "computed",
     "Runs of one-to-three-word sentences imitate emphasis without supplying any.",
     "Fold fragments back into the sentence they belong to.",
     "A fragment the author uses in their own past posts (see the voice fingerprint)."),
    ("RD-07", "reduce", "One-word paragraph", 1, 1, None, "computed",
     "A paragraph of one or two words is a dramatic pause the reader did not ask for.",
     "Attach it to the previous paragraph or delete it.", "Once, when the word is the news."),
    ("RD-08", "reduce", "Announced candor", 0, 2,
     r"\blet me be (?:honest|real|clear)\b|\bi'll be (?:honest|real)\b|\bto be honest\b|"
     r"\bhonestly[,?]|\breal talk\b|\bfull transparency\b|\bcan i be vulnerable\b|"
     r"\bhard truth\b|\btruth bomb\b|\bnot gonna lie\b|\bconfession:", "all",
     "Announcing honesty implies the rest was something else, and replaces the hard fact.",
     "Delete the announcement; state the uncomfortable fact with its date and number.",
     "Never as an opener."),
    ("RD-09", "reduce", "Stock opener", 0, 3,
     r"in today's|in a world|in the (?:age|era) of|let's (?:talk about|dive|be real)|"
     r"i(?:'m| am) (?:thrilled|excited|humbled|delighted|proud|pleased|happy) to|"
     r"ever wonder|have you ever|picture this|imagine this|we've all been there", "first",
     "The first line decides whether anyone expands the post; a stock one spends it.",
     "Open with the most specific true thing in the draft: a figure, a date, a moment.",
     "Never; an announcement can open with the news itself."),
    ("RD-10", "reduce", "Stock closer", 0, 2,
     r"what do you think\?|^thoughts\?|\bagree\?|tag someone|repost if|share (?:this )?if you|"
     r"follow (?:me )?for more|let that sink in|read that again|drop a .{1,20} in the comments|"
     r"comment .{1,25} (?:below|and i'll)|who else", "last",
     "A generic ask gets generic replies and reads as engagement bait.",
     "Ask one question only someone with experience of the topic could answer.",
     "Never in the stock wording."),
    ("RD-11", "reduce", "Dash density", 1, 1, None, "computed",
     "Past roughly one dash per hundred words, the dash becomes the rhythm of the piece.",
     "Keep the dash doing the most work; turn the rest into commas, colons or brackets.",
     "The author's own posts run at or above this rate (see the voice fingerprint)."),
    ("RD-12", "reduce", "Participle opener", 1, 1,
     r"(?:^|(?<=[.!?]\s))(?!During|According|Nothing|Something|Anything|Everything|Morning|"
     r"Evening|Spring|Bring)[A-Z][a-z]+ing\s[^.!?\n]{3,70}?,\s", "case",
     "Starting on an '-ing' clause hides who did the thing until halfway through.",
     "Put the actor first: 'We cut the queue by...' not 'Cutting the queue, we...'.",
     "Once, when the action really is the subject."),
    ("RD-13", "reduce", "Signpost phrase", 0, 1,
     r"it's (?:important|worth) (?:to note|noting|mentioning)|\bthat said,|\bin conclusion\b|"
     r"\bin summary\b|\bto sum up\b|at the end of the day|when it comes to|\bmoreover\b|"
     r"\bfurthermore\b|\badditionally,|needless to say|in other words", "all",
     "Essay connectives narrate the structure instead of delivering it.",
     "Delete the connective; if the link is unclear without it, reorder the sentences.",
     "Formal long-form articles, not feed posts."),
    ("RD-14", "reduce", "Noun stack", 2, 1,
     r"\bthe \w+(?:tion|ment|ance|ence|ity) of (?:the |our |a )?\w+", "all",
     "Verbs turned into nouns make a sentence longer and remove the person doing the work.",
     "Use the verb: 'when we rolled out' for 'the implementation of'.",
     "Fixed names of things ('the Department of...')."),
    ("RD-15", "reduce", "Uniform sentence length", 0, 1, None, "computed",
     "Every sentence landing at the same length reads as generated cadence.",
     "Join two related sentences with a real subordinate clause. Change one, not all.",
     "Deliberately clipped announcement posts under about sixty words."),
    ("RD-16", "reduce", "Nothing only the author could know", 1, 2, None, "computed",
     "With no figure, no named person or company and no 'I', anyone could have posted this.",
     "Ask the author for one number with its referent and one name. Never invent them.",
     "Short reshare captions."),
    ("RD-17", "reduce", "Label-and-colon reveal", 1, 1,
     r"^(?:the )?(?:lesson|takeaway|bottom line|pro tip|tl;dr|key insight|moral|my advice|"
     r"the point)\s*:", "all",
     "Labelled takeaways turn a post into a slide.",
     "Say the takeaway as a sentence in the author's voice.", "One label per post."),
    ("RD-18", "reduce", "Hedge stack", 1, 1,
     r"\b(?:may|might|could) (?:potentially|possibly|perhaps)\b|\barguably\b|\bin many ways\b|"
     r"\bto some extent\b|\bmore often than not\b|\bit could be argued\b", "all",
     "Stacked hedges protect a claim the author has not decided to make.",
     "Commit to the claim or state exactly what is unknown.",
     "The uncertainty is real and specific ('we have six weeks of data')."),
    ("RD-19", "reduce", "Vocabulary cluster", 0, 3, None, "computed",
     "Three or more stock words in one paragraph mean the paragraph says nothing concrete.",
     "Rewrite the paragraph from the underlying fact; swapping words will not save it.", "Never."),
    ("RV-01", "review", "Single dash", 0, 0, None, "computed",
     "Some readers treat any long dash as a mark of generated text.",
     "Leave it unless the audience hunts for it.", "Almost always; zero dashes looks scrubbed."),
    ("RV-02", "review", "The one remaining triple", 0, 0, None, "computed",
     "A lone list of three is under the allowance but worth a second look.",
     "Drop any item that was added for the rhythm.", "When three is the true count."),
    ("RV-03", "review", "Passive construction", 0, 0,
     r"\b(?:was|were|is|are|been|being|be) (?:\w+ly )?\w{3,}ed\b(?! (?:to|about|by me))", "all",
     "Passive voice can hide the actor.", "Make it active only where the actor matters.",
     "The actor is unknown or irrelevant ('the server was patched overnight')."),
    ("RV-04", "review", "Typographic quotes", 0, 0, r"[“”‘’]", "raw",
     "Curly quotes are sometimes read as a paste from a generator.",
     "Normalise only for consistency.", "Phones and word processors produce them for everyone."),
    ("RV-05", "review", "Out-of-fashion flagged word", 0, 0,
     r"\b(?:delv\w*|tapestry|realm|testament|beacon|myriad|plethora|embark\w*|navigat\w*)\b", "all",
     "These words were early giveaways and are now avoided by people and generators alike.",
     "Replace if a plainer word exists.", "The literal meaning ('navigating the harbour')."),
    ("RV-06", "review", "Semicolon", 0, 0, r";", "all",
     "Rare in feed writing, so it stands out.",
     "Split into two sentences if the post is casual.", "The author uses them in past posts."),
    ("RV-07", "review", "No contractions", 0, 0, None, "computed",
     "A long post without a single contraction reads as over-edited or generated.",
     "Read it aloud and contract wherever the author would when speaking.",
     "Formal announcements and non-native writers who never contract."),
]


def build_catalogue() -> List[Dict[str, Any]]:
    """Expand the compact rule tuples into dictionaries with compiled patterns."""
    out: List[Dict[str, Any]] = []
    for rid, tier, name, allow, weight, pattern, scope, why, fix, keep in _RAW:
        out.append({"id": rid, "tier": tier, "name": name, "allow": allow, "weight": weight,
                    "regex": re.compile(pattern, re.M if scope == "case" else FLAGS)
                    if pattern else None,
                    "scope": scope, "why": why, "fix": fix, "keep_when": keep})
    return out


CATALOGUE = build_catalogue()


def normalise(text: str) -> str:
    """Return a matching copy with straight quotes so patterns need one spelling."""
    return text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')


def read_text(path_arg: str) -> str:
    """Read a UTF-8 draft from a path or '-' (stdin); exit 2 with guidance on failure."""
    try:
        text = sys.stdin.read() if path_arg == "-" else Path(path_arg).read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        fail(f"no readable file at {path_arg}. Pass a plain-text file or '-' for stdin.")
    except (UnicodeDecodeError, PermissionError, OSError) as exc:
        fail(f"cannot read {path_arg} as UTF-8 text ({exc.__class__.__name__}). "
             "Save the draft as a plain .txt file and retry.")
    if not text.strip():
        fail(f"{path_arg} is empty. Paste the draft text into the file first.")
    return text


def fail(message: str) -> None:
    """Print an actionable error to stderr and exit with the bad-input code."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def words(text: str) -> List[str]:
    """Split text into word tokens (letters, digits, inner apostrophes and hyphens)."""
    return re.findall(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*", text)


def paragraphs(text: str) -> List[str]:
    """Split text into blank-line-separated paragraphs, dropping empties."""
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def sentences(text: str) -> List[str]:
    """Split text into sentences on terminal punctuation and line breaks."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if words(p)]


def get_rule(rule_id: str) -> Optional[Dict[str, Any]]:
    """Look up one rule by id (case-insensitive); None when it does not exist."""
    return next((r for r in CATALOGUE if r["id"] == rule_id.strip().upper()), None)


def public(rule: Dict[str, Any]) -> Dict[str, Any]:
    """Return a JSON-safe copy of a rule (compiled pattern replaced by its source)."""
    return {**{k: v for k, v in rule.items() if k != "regex"},
            "pattern": rule["regex"].pattern if rule["regex"] else None}


def main() -> None:
    """List the catalogue or explain a single rule."""
    parser = argparse.ArgumentParser(
        description="List or explain the machine-tell rules used by tell_audit.py.",
        epilog="Exit codes: 0 ok, 2 bad input (unknown rule id).")
    parser.add_argument("--list", action="store_true", help="List every rule (default action).")
    parser.add_argument("--tier", choices=TIERS, help="Only list rules in this tier.")
    parser.add_argument("--explain", metavar="RULE_ID", help="Why one rule fires and its fix.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()

    if args.explain:
        rule = get_rule(args.explain)
        if rule is None:
            fail(f"unknown rule id '{args.explain}'. Run with --list to see valid ids.")
        if args.format == "json":
            print(json.dumps(public(rule), indent=2, ensure_ascii=False))
            return
        print(f"{rule['id']}  {rule['name']}  [{rule['tier']}]  "
              f"allowance {rule['allow']}, load per excess hit {rule['weight']}")
        print(f"  why it fires : {rule['why']}")
        print(f"  the fix      : {rule['fix']}")
        print(f"  keep it when : {rule['keep_when']}")
        return
    chosen = [r for r in CATALOGUE if not args.tier or r["tier"] == args.tier]
    if args.format == "json":
        print(json.dumps([public(r) for r in chosen], indent=2, ensure_ascii=False))
        return
    for rule in chosen:
        print(f"{rule['id']}  {rule['tier']:<7} allow {rule['allow']}  {rule['name']}")
    print(f"{len(chosen)} rules. Use --explain RULE_ID for the reasoning behind one.")


if __name__ == "__main__":
    main()
