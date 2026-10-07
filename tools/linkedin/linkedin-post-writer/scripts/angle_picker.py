#!/usr/bin/env python3
"""Rank opening patterns and post angles for a LinkedIn brief by the material on hand.

Reads a brief (topic, goal, audience, and whatever raw material the author
really has: a figure, a dated event, a quote, a changed belief...) and ranks
the opening patterns that material can support. Patterns the author lacks the
material for are listed with the one question that would unlock them. The
tool chooses structure only; it never writes sentences or invents facts.

Usage:
    python3 angle_picker.py --input brief.json
    python3 angle_picker.py --input brief.json --top 5 --format json

Exit codes:
    0  at least one pattern is supported by the brief
    1  gate failed: the brief has no usable material for any pattern
    2  bad input (missing or malformed JSON, missing required field)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

GOALS = ("conversation", "saves", "reshares", "inbound")
EVIDENCE = ("figure", "dated_event", "sample_count", "before_after")
# Length bands in characters. Editorial heuristics, not platform rules.
BANDS = {"short": (250, 600), "standard": (600, 1400), "long": (1400, 2600)}

# slug, name, needs, fit per goal (conversation, saves, reshares, inbound),
# opening skeleton, body beats, close, question that unlocks it
_RAW = [
    ("receipt", "Receipt line", ["figure"], (2, 3, 2, 3),
     "{precise figure} + {what it measured} + {the surprising half}",
     ["what the figure measures and over what period", "the one change behind it",
      "what did not move", "what is still unsolved"],
     "question about the reader's equivalent number",
     "What is one exact figure from this work, and what does it count?"),
    ("dated-error", "Dated mistake", ["dated_event"], (3, 1, 2, 2),
     "{when} + {what I or we got wrong} + {what it cost}",
     ["the decision as it looked at the time", "the moment it showed",
      "what was changed and when", "what the author would do first now"],
     "question about a comparable call the reader made",
     "What went wrong, on what date, and what did it cost?"),
    ("cold-scene", "Cold scene", ["scene"], (2, 1, 2, 1),
     "{a moment already in progress: place, person, what was said or seen}",
     ["two more beats of the scene", "what the author understood only afterwards",
      "the practical change that followed"],
     "plain statement of what the author does differently",
     "Describe one moment: where were you, who was there, what was said?"),
    ("belief-flip", "Changed mind", ["changed_belief"], (3, 2, 2, 2),
     "{what I believed, stated fairly} + {what ended that belief}",
     ["why the old belief was reasonable", "the evidence that broke it",
      "the new working rule", "where the old belief still holds"],
     "question asking who still holds the old view and why",
     "Which view on this have you dropped, and what made you drop it?"),
    ("counter-position", "Counter-position", ["opposing_view"], (3, 1, 3, 2),
     "{common practice} + {flat claim that it is wrong for a named case}",
     ["the strongest version of the common view", "the evidence against it",
      "the boundary: when the common view is right", "what to do instead"],
     "invitation to disagree with a specific part",
     "Which common piece of advice in your field do you disagree with, and for whom?"),
    ("gap", "Measured gap", ["before_after"], (2, 3, 2, 3),
     "{before figure} to {after figure} + {time span} + {the unexpected cause}",
     ["how it was measured", "the two or three changes, in order of effect",
      "what was tried and did nothing", "the cost of getting there"],
     "question about which change the reader would try first",
     "What was the number before, what is it now, and over how long?"),
    ("borrowed-line", "Borrowed line", ["quote"], (3, 1, 2, 1),
     "{who said it, described not flattered} + {their exact words}",
     ["the situation in which it was said", "why it landed",
      "what the author changed because of it"],
     "question about a sentence that changed the reader's practice",
     "What did someone say to you, word for word, that stuck?"),
    ("house-rule", "House rule", ["rule"], (2, 3, 2, 2),
     "{the rule, as a rule} + {the incident that created it}",
     ["the incident in detail", "how the rule works day to day",
      "the exception the author allows", "what it costs to keep"],
     "question about a rule the reader keeps that looks odd from outside",
     "What rule do you or your team follow that outsiders find strange?"),
    ("field-count", "Field count", ["sample_count"], (2, 3, 3, 3),
     "{I or we} {reviewed / interviewed / audited} {how many} {of what} + {the pattern}",
     ["how the sample was chosen and its limits", "the pattern with its count",
      "the exception that surprised", "what the author now recommends"],
     "question asking whether the reader's sample matches",
     "How many of something have you looked at closely, and what repeated?"),
    ("asked-question", "Reported question", ["question_received"], (3, 2, 1, 2),
     "{who asked, by role} + {the question in their words}",
     ["the short answer", "the reasoning", "what the author got wrong when first answering it"],
     "the same question handed to the reader",
     "What question do people keep asking you about this?"),
    ("credit", "Named credit", ["person_to_credit"], (1, 0, 3, 1),
     "{name} + {the specific thing they did} + {what it made possible}",
     ["what the situation was before", "exactly what the person did",
      "the result, with a figure if there is one"],
     "no ask; end on the person",
     "Who did a specific thing that made this work, and what was it?"),
    ("plain-definition", "Plain definition", ["term"], (1, 3, 2, 2),
     "{term people nod along to} + {what it means in everyday words}",
     ["the everyday version", "one worked example with real numbers",
      "the common misuse", "when the term is not worth using"],
     "question about another term the reader wants explained",
     "Which term in your field do people use without being able to define?"),
    ("dated-bet", "Dated bet", ["prediction"], (3, 1, 3, 2),
     "{what will be true} + {by when} + {what would prove it wrong}",
     ["the evidence so far", "the strongest reason it might not happen",
      "what the author is doing differently because of it"],
     "invitation to take the other side with a reason",
     "What do you expect to be true by a specific date, and what would change your mind?"),
    ("list-promise", "Counted list", ["steps"], (1, 3, 2, 2),
     "{how many} {what kind of items} + {the context that makes them worth reading}",
     ["one line per item, each with its own detail", "the item most people skip",
      "the item the author is least sure of"],
     "question about the item the reader would add",
     "What are the steps or checks, in order, that you actually follow?"),
]


def fail(message: str) -> None:
    """Print an actionable error to stderr and exit with the bad-input code."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def has(material: Dict[str, Any], key: str) -> bool:
    """Return True when a material field holds something usable."""
    value = material.get(key)
    if isinstance(value, list):
        return len([v for v in value if str(v).strip()]) >= 3
    return bool(str(value or "").strip())


def load_brief(path_arg: str) -> Dict[str, Any]:
    """Load and validate the brief JSON, exiting 2 with guidance on any problem."""
    try:
        data = json.loads(Path(path_arg).read_text(encoding="utf-8"))
    except (FileNotFoundError, IsADirectoryError):
        fail(f"no brief file at {path_arg}. Copy assets/sample_brief.json and edit it.")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {path_arg} ({exc.__class__.__name__}). Save it as UTF-8 JSON.")
    except json.JSONDecodeError as exc:
        fail(f"{path_arg} is not valid JSON (line {exc.lineno}): {exc.msg}")
    if not isinstance(data, dict):
        fail("the brief must be a JSON object. See assets/sample_brief.json for the shape.")
    for key in ("topic", "goal", "audience"):
        if not str(data.get(key, "")).strip():
            fail(f"the brief is missing '{key}'. Topic, goal and audience are required.")
    if data["goal"] not in GOALS:
        fail(f"goal '{data['goal']}' is not one of: {', '.join(GOALS)}.")
    if data.get("length", "standard") not in BANDS:
        fail(f"length must be one of: {', '.join(BANDS)}.")
    if not isinstance(data.get("material", {}), dict):
        fail("'material' must be an object of field -> text. See assets/sample_brief.json.")
    return data


def rank(brief: Dict[str, Any]) -> Dict[str, Any]:
    """Score every pattern against the brief and split into supported and locked."""
    material = brief.get("material", {}) or {}
    goal_index = GOALS.index(brief["goal"])
    evidence = [k for k in EVIDENCE if has(material, k)]
    supported: List[Dict[str, Any]] = []
    locked: List[Dict[str, Any]] = []
    for order, (slug, name, needs, fit, opening, beats, close, unlock) in enumerate(_RAW):
        missing = [n for n in needs if not has(material, n)]
        if missing:
            locked.append({"pattern": slug, "name": name, "missing": missing, "ask": unlock})
            continue
        extra = [e for e in evidence if e not in needs][:2]
        score = 4 + fit[goal_index] + len(extra)
        cautions = []
        if slug in ("counter-position", "dated-bet", "belief-flip") and not evidence:
            cautions.append("no figure, date or sample in the brief: the claim will read as "
                            "opinion; get one piece of evidence before drafting")
        if slug == "credit" and brief["goal"] != "reshares":
            cautions.append("credit posts rarely serve this goal; use only if the thanks is "
                            "the point")
        supported.append({
            "pattern": slug, "name": name, "score": score, "order": order,
            "goal_fit": fit[goal_index], "supporting_evidence": extra,
            "opening_skeleton": opening,
            "opening_material": {n: material[n] for n in needs},
            "body_beats": beats, "close": close, "cautions": cautions})
    supported.sort(key=lambda item: (-item["score"], item["order"]))
    low, high = BANDS[brief.get("length", "standard")]
    return {"topic": brief["topic"], "goal": brief["goal"], "audience": brief["audience"],
            "length_band": {"name": brief.get("length", "standard"), "min_chars": low,
                            "max_chars": high},
            "supported": supported, "locked": locked}


def output(report: Dict[str, Any], fmt: str, top: int) -> None:
    """Print the ranking as JSON or as a readable shortlist."""
    shown = report["supported"][:top]
    if fmt == "json":
        print(json.dumps({**report, "supported": shown}, indent=2, ensure_ascii=False))
        return
    band = report["length_band"]
    print(f"Angle shortlist: {report['topic']}")
    print(f"Goal: {report['goal']}   Audience: {report['audience']}")
    print(f"Length band: {band['name']} ({band['min_chars']}-{band['max_chars']} characters, "
          "editorial heuristic)")
    print("=" * 72)
    for position, item in enumerate(shown, 1):
        print(f"{position}. {item['name']} [{item['pattern']}]  score {item['score']} "
              f"(goal fit {item['goal_fit']}/3)")
        print(f"   open with : {item['opening_skeleton']}")
        for key, value in item["opening_material"].items():
            text = "; ".join(value) if isinstance(value, list) else str(value)
            print(f"   material  : {key} = {text}")
        print(f"   body      : {' -> '.join(item['body_beats'])}")
        print(f"   close     : {item['close']}")
        for caution in item["cautions"]:
            print(f"   caution   : {caution}")
    if not shown:
        print("No pattern is supported. The brief has no concrete material yet.")
    print("-" * 72)
    print(f"Locked patterns ({len(report['locked'])}): ask one of these to unlock more options")
    for item in report["locked"]:
        print(f"   {item['pattern']:<17} needs {', '.join(item['missing'])}: {item['ask']}")


def main() -> None:
    """Parse arguments, rank the patterns and print the shortlist."""
    parser = argparse.ArgumentParser(
        description="Rank LinkedIn opening patterns and angles by the material in a brief.",
        epilog="Exit codes: 0 at least one pattern supported, 1 no usable material in "
               "the brief, 2 bad input. Goal-fit scores are editorial heuristics.")
    parser.add_argument("--input", required=True,
                        help="Brief JSON (topic, goal, audience, material). "
                             "See assets/sample_brief.json.")
    parser.add_argument("--top", type=int, default=3,
                        help="How many supported patterns to show (default: 3).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if args.top < 1:
        fail("--top must be 1 or more.")
    report = rank(load_brief(args.input))
    output(report, args.format, args.top)
    sys.exit(0 if report["supported"] else 1)


if __name__ == "__main__":
    main()
