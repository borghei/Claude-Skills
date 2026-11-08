#!/usr/bin/env python3
"""interview_synthesizer.py

Synthesize customer interview transcripts into:
  1. Themed insight clusters
  2. An opportunity solution tree (Teresa Torres)
  3. A follow-up question list

Input:  JSON file with interview transcripts (see assets/interview_input_template.json)
Output: Markdown, JSON, Mermaid, Confluence, Notion, or Linear

Standard library only. No ML calls. Deterministic keyword + code matching.

Usage:
  python interview_synthesizer.py --input interviews.json --format markdown --output synthesis.md
  python interview_synthesizer.py --demo --format mermaid
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any

SCHEMA = "pm/interview-synthesis/v1"

# Lightweight code lexicons. The tool is deterministic; richer NLP belongs out of
# scope (see SKILL.md "Out of Scope").
PAIN_LEXICON = {
    "manual": ["manual", "re-key", "rekey", "by hand", "exported", "rebuild"],
    "trust": ["don't trust", "do not trust", "can't trust", "cannot trust", "verify", "verification"],
    "duplicate": ["duplicate", "duplicates", "dupe"],
    "slow": ["slow", "took hours", "took days", "spent hours", "9pm", "all night"],
    "opaque": ["didn't tell", "did not tell", "no explanation", "couldn't see", "cannot see", "unclear why"],
    "switching": ["export to excel", "switched to", "fall back to", "open another tab"],
}

GAIN_LEXICON = {
    "audit-trail": ["audit", "trace", "explain why", "show me why", "rule"],
    "speed": ["faster", "quicker", "fewer days", "save time"],
    "trust": ["trust it", "confidence", "sign off"],
    "automation": ["automate", "automatic", "no manual"],
}

EMOTION_LEXICON = {
    "frustration": ["frustrat", "annoyed", "painful", "hate"],
    "fear": ["worry", "scared", "afraid", "risk"],
    "relief": ["relief", "finally", "thank goodness"],
    "delight": ["love", "great", "amazing", "perfect"],
}

STORY_MARKERS = [
    "last week", "last month", "last tuesday", "last wednesday", "last thursday",
    "last friday", "last quarter", "yesterday", "this morning",
    "started on the", "walked through", "spent", "took", "ended up",
]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Snippet:
    participant: str
    role: str
    segment: str
    text: str
    snippet_type: str  # story | emotion | contradiction | surprise | quote
    pain_codes: list[str] = field(default_factory=list)
    gain_codes: list[str] = field(default_factory=list)
    emotion_codes: list[str] = field(default_factory=list)


@dataclass
class Theme:
    headline: str
    code: str
    snippets: list[Snippet] = field(default_factory=list)

    @property
    def participants(self) -> set[str]:
        return {s.participant for s in self.snippets}

    @property
    def strength(self) -> int:
        # 1 = single mention, 2 = >=2 participants, 3 = >=2 participants + a story
        if len(self.participants) < 2:
            return 1
        has_story = any(s.snippet_type == "story" for s in self.snippets)
        return 3 if has_story else 2


@dataclass
class Opportunity:
    title: str
    evidence_themes: list[str]
    affected_segments: list[str]
    strength: int
    solutions: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Extraction + coding
# ---------------------------------------------------------------------------

def _match_codes(text: str, lexicon: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    return sorted({code for code, terms in lexicon.items() if any(t in lowered for t in terms)})


def _classify_snippet_type(text: str) -> str:
    lowered = text.lower()
    if any(marker in lowered for marker in STORY_MARKERS):
        return "story"
    if any(any(t in lowered for t in terms) for terms in EMOTION_LEXICON.values()):
        return "emotion"
    return "quote"


def extract_snippets(interviews: list[dict[str, Any]]) -> list[Snippet]:
    snippets: list[Snippet] = []
    for entry in interviews:
        participant = entry.get("participant", "P?")
        role = entry.get("role", "unknown")
        segment = entry.get("segment", "unknown")
        for qa in entry.get("qa", []):
            answer = (qa.get("answer") or "").strip()
            if not answer:
                continue
            # Split long answers into sentences for finer-grained coding.
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer) if s.strip()]
            for sent in sentences:
                snippet = Snippet(
                    participant=participant,
                    role=role,
                    segment=segment,
                    text=sent,
                    snippet_type=_classify_snippet_type(sent),
                    pain_codes=_match_codes(sent, PAIN_LEXICON),
                    gain_codes=_match_codes(sent, GAIN_LEXICON),
                    emotion_codes=_match_codes(sent, EMOTION_LEXICON),
                )
                # Keep snippets that produced at least one code, are a story, or are emotional.
                if snippet.pain_codes or snippet.gain_codes or snippet.snippet_type in {"story", "emotion"}:
                    snippets.append(snippet)
    return snippets


# ---------------------------------------------------------------------------
# Theme clustering
# ---------------------------------------------------------------------------

THEME_HEADLINES = {
    "pain:manual": "Users fall back to manual workarounds because the automated path is not trusted",
    "pain:trust": "Users do not trust automated decisions because the rule behind each decision is opaque",
    "pain:duplicate": "Duplicate handling breaks user trust and forces manual re-keying",
    "pain:slow": "End-to-end workflow runs long because exception handling dominates the timeline",
    "pain:opaque": "Users cannot inspect why the system made a given decision",
    "pain:switching": "Users export to external tools (Excel, etc.) to feel in control",
    "gain:audit-trail": "Users want a per-decision audit trail to sign off with confidence",
    "gain:speed": "Users want to compress the end-to-end timeline meaningfully",
    "gain:trust": "Users want to reach trusted-automation faster than today's 3-week probe",
    "gain:automation": "Users want automation that does not require manual verification",
}


def cluster_themes(snippets: list[Snippet], min_strength: int = 1) -> list[Theme]:
    buckets: dict[str, list[Snippet]] = defaultdict(list)
    for s in snippets:
        for c in s.pain_codes:
            buckets[f"pain:{c}"].append(s)
        for c in s.gain_codes:
            buckets[f"gain:{c}"].append(s)
    themes: list[Theme] = []
    for code, items in buckets.items():
        if len(items) < 2:
            # Need >=2 snippets to call it a theme candidate
            continue
        theme = Theme(
            headline=THEME_HEADLINES.get(code, f"Recurring signal: {code}"),
            code=code,
            snippets=items,
        )
        if theme.strength >= min_strength:
            themes.append(theme)
    # Strongest themes first
    themes.sort(key=lambda t: (-t.strength, -len(t.snippets)))
    return themes


# ---------------------------------------------------------------------------
# Opportunity tree
# ---------------------------------------------------------------------------

OPPORTUNITY_TEMPLATES = {
    "pain:manual": ("Users cannot complete the workflow without falling back to manual re-keying", [
        "Surface and resolve duplicates inline before they enter the ledger",
        "Provide a one-click re-run of the automation against a corrected dataset",
        "Do nothing (baseline comparison)",
    ]),
    "pain:trust": ("Users cannot verify automated decisions fast enough to trust the system", [
        "Show the rule trace and confidence score per decision",
        "Offer a sample-and-confirm flow for the first N decisions",
        "Do nothing (baseline comparison)",
    ]),
    "pain:duplicate": ("Duplicate detection lacks transparency and recovery options", [
        "Group duplicates with explanations and bulk-resolve UI",
        "Surface duplicates pre-import rather than post-import",
    ]),
    "pain:slow": ("End-to-end timeline is dominated by exception handling, not automation runtime", [
        "Move exception triage to an asynchronous queue with SLAs",
        "Prioritize exceptions by financial impact rather than chronological order",
    ]),
    "pain:opaque": ("System decisions are not inspectable at the time of review", [
        "Add a per-decision drill-down with rule, inputs, and timestamp",
    ]),
    "pain:switching": ("Users abandon the product mid-workflow to reach a more controllable tool", [
        "Bring spreadsheet-grade flexibility into the in-product review surface",
    ]),
    "gain:audit-trail": ("Users want a defensible audit trail per decision", [
        "Generate exportable audit reports per close period",
    ]),
    "gain:speed": ("Users want to compress the workflow by removing the verification tax", [
        "Reduce verification load via trust-building UI signals",
    ]),
    "gain:trust": ("Users want a shorter time-to-trust on new integrations", [
        "Guided trust-building onboarding for new integrations",
    ]),
    "gain:automation": ("Users want true hands-off automation, not assisted automation", [
        "Identify and remove top-3 mandatory manual checkpoints",
    ]),
}


def build_opportunities(themes: list[Theme]) -> list[Opportunity]:
    opps: list[Opportunity] = []
    seen_titles: set[str] = set()
    for theme in themes:
        template = OPPORTUNITY_TEMPLATES.get(theme.code)
        if not template:
            continue
        title, solutions = template
        if title in seen_titles:
            # Merge segment evidence rather than duplicating
            for opp in opps:
                if opp.title == title:
                    opp.evidence_themes.append(theme.code)
                    opp.affected_segments = sorted(set(opp.affected_segments + sorted({s.segment for s in theme.snippets})))
                    opp.strength = max(opp.strength, theme.strength)
            continue
        opps.append(Opportunity(
            title=title,
            evidence_themes=[theme.code],
            affected_segments=sorted({s.segment for s in theme.snippets}),
            strength=theme.strength,
            solutions=solutions,
        ))
        seen_titles.add(title)
    # Strongest opportunities first
    opps.sort(key=lambda o: -o.strength)
    return opps


# ---------------------------------------------------------------------------
# Follow-up questions
# ---------------------------------------------------------------------------

FOLLOWUP_TEMPLATES = {
    "pain:manual": [
        "Walk me through the last time you had to manually re-key data. What triggered it?",
        "If the manual re-key step disappeared tomorrow, what would you do differently?",
    ],
    "pain:trust": [
        "Tell me about the moment you decided to start trusting (or distrusting) the automation.",
        "What would you need to see to trust an automated match the first time you saw it?",
    ],
    "pain:duplicate": [
        "Tell me about the last duplicate you encountered. How did you resolve it?",
        "What is the cost (time, risk) of a missed duplicate today?",
    ],
    "pain:slow": [
        "If your workflow only had to handle the clean cases, how long would it take?",
        "Where in the timeline are you waiting on something or someone else?",
    ],
    "pain:opaque": [
        "When a decision surprises you, what is the first thing you do to investigate?",
        "Describe the ideal explanation the system could give you for a single decision.",
    ],
    "pain:switching": [
        "Walk me through the last time you exported the data to a different tool. What were you trying to do?",
        "What does the external tool let you do that the in-product surface does not?",
    ],
    "gain:audit-trail": [
        "Who consumes the audit trail downstream? What do they need to see?",
        "What is the worst audit experience you have had with a vendor product?",
    ],
}


def build_followups(themes: list[Theme]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for theme in themes:
        if theme.strength >= 3:
            continue  # Strong themes do not need more evidence
        questions = FOLLOWUP_TEMPLATES.get(theme.code, [
            f"Tell me about the last time {theme.code.split(':')[-1]} came up in your workflow.",
        ])
        out.append({
            "theme_code": theme.code,
            "headline": theme.headline,
            "current_strength": theme.strength,
            "questions": questions,
        })
    return out


# ---------------------------------------------------------------------------
# Synthesis pipeline
# ---------------------------------------------------------------------------

def synthesize(payload: dict[str, Any], min_strength: int = 1, outcome_override: str | None = None) -> dict[str, Any]:
    study = payload.get("study", {})
    outcome = outcome_override or study.get("outcome") or "Improve customer outcome"
    interviews = payload.get("interviews", [])
    snippets = extract_snippets(interviews)
    themes = cluster_themes(snippets, min_strength=min_strength)
    opportunities = build_opportunities(themes)
    followups = build_followups(themes)
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data": {
            "study": study,
            "outcome": outcome,
            "stats": {
                "interview_count": len(interviews),
                "snippet_count": len(snippets),
                "theme_count": len(themes),
                "opportunity_count": len(opportunities),
            },
            "themes": [
                {
                    "headline": t.headline,
                    "code": t.code,
                    "strength": t.strength,
                    "participant_count": len(t.participants),
                    # A sentence coded under several themes is evidence for each, but it is one
                    # quote: count it so a reader does not take two themes as two sources.
                    "shared_snippet_count": sum(1 for s in t.snippets if sum(s in o.snippets for o in themes) > 1),
                    "snippets": [dict(asdict(s), shared=sum(s in o.snippets for o in themes) > 1) for s in t.snippets],
                }
                for t in themes
            ],
            "opportunities": [asdict(o) for o in opportunities],
            "followups": followups,
        },
    }


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def render_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2)


def render_markdown(result: dict[str, Any]) -> str:
    data = result["data"]
    lines: list[str] = []
    lines.append(f"# Interview Synthesis: {data['study'].get('title', 'Untitled study')}")
    lines.append("")
    lines.append(f"**Outcome:** {data['outcome']}")
    lines.append(f"**Generated:** {result['generated_at']}")
    stats = data["stats"]
    lines.append(f"**Stats:** {stats['interview_count']} interviews, {stats['snippet_count']} snippets, "
                 f"{stats['theme_count']} themes, {stats['opportunity_count']} opportunities")
    lines.append("")
    lines.append("## Themes")
    if not data["themes"]:
        lines.append("_No themes met the evidence threshold. Lower `--min-strength` or add interviews._")
    for t in data["themes"]:
        lines.append("")
        lines.append(f"### {t['headline']}")
        lines.append(f"- Code: `{t['code']}`")
        shared = f", {t['shared_snippet_count']} shared with another theme" if t["shared_snippet_count"] else ""
        lines.append(f"- Strength: {t['strength']}/3 ({t['participant_count']} participants, {len(t['snippets'])} snippets{shared})")
        lines.append("- Evidence:")
        for s in t["snippets"][:5]:
            mark = " [shared]" if s.get("shared") else ""
            lines.append(f"  - _\"{s['text']}\"_ -- {s['participant']} ({s['role']}){mark}")
    lines.append("")
    lines.append("## Opportunity Solution Tree")
    lines.append("")
    lines.append("```mermaid")
    lines.append(render_mermaid_tree(data))
    lines.append("```")
    lines.append("")
    lines.append("### Opportunity detail")
    for i, opp in enumerate(data["opportunities"], 1):
        lines.append("")
        lines.append(f"#### Opportunity {i}: {opp['title']}")
        lines.append(f"- Strength: {opp['strength']}/3")
        lines.append(f"- Evidence themes: {', '.join(opp['evidence_themes'])}")
        lines.append(f"- Affected segments: {', '.join(opp['affected_segments'])}")
        lines.append("- Candidate solutions:")
        for s in opp["solutions"]:
            lines.append(f"  - {s}")
    lines.append("")
    lines.append("## Follow-up Questions for Next Round")
    if not data["followups"]:
        lines.append("_All themes are strongly evidenced. No follow-ups required._")
    for f in data["followups"]:
        lines.append("")
        lines.append(f"### {f['headline']} (current strength {f['current_strength']}/3)")
        for q in f["questions"]:
            lines.append(f"- {q}")
    lines.append("")
    return "\n".join(lines)


def render_mermaid_tree(data: dict[str, Any]) -> str:
    lines = ["graph LR"]
    outcome_id = "O"
    lines.append(f"  {outcome_id}[\"Outcome: {data['outcome']}\"]")
    for oi, opp in enumerate(data["opportunities"], 1):
        opp_id = f"Op{oi}"
        # Mermaid label escaping: replace double quotes
        title = opp["title"].replace('"', "'")
        lines.append(f"  {opp_id}[\"{title}\"]")
        lines.append(f"  {outcome_id} --> {opp_id}")
        for si, sol in enumerate(opp["solutions"], 1):
            sol_id = f"S{oi}_{si}"
            label = sol.replace('"', "'")
            lines.append(f"  {sol_id}[\"{label}\"]")
            lines.append(f"  {opp_id} --> {sol_id}")
    return "\n".join(lines)


def render_mermaid(result: dict[str, Any]) -> str:
    return "```mermaid\n" + render_mermaid_tree(result["data"]) + "\n```"


def render_confluence(result: dict[str, Any]) -> str:
    data = result["data"]
    parts: list[str] = []
    parts.append(f"<h1>Interview Synthesis: {data['study'].get('title', 'Untitled study')}</h1>")
    parts.append(f"<p><strong>Outcome:</strong> {data['outcome']}</p>")
    parts.append("<h2>Themes</h2>")
    for t in data["themes"]:
        parts.append(f"<h3>{t['headline']}</h3>")
        parts.append(f"<p>Code: <code>{t['code']}</code> -- Strength {t['strength']}/3 -- "
                     f"{t['participant_count']} participants -- {len(t['snippets'])} snippets</p>")
        parts.append("<ul>")
        for s in t["snippets"][:5]:
            parts.append(f"<li><em>\"{s['text']}\"</em> -- {s['participant']} ({s['role']})</li>")
        parts.append("</ul>")
    parts.append("<h2>Opportunity Solution Tree</h2>")
    parts.append("<ul>")
    parts.append(f"<li><strong>Outcome:</strong> {data['outcome']}<ul>")
    for opp in data["opportunities"]:
        parts.append(f"<li><strong>Opportunity:</strong> {opp['title']}<ul>")
        for sol in opp["solutions"]:
            parts.append(f"<li>{sol}</li>")
        parts.append("</ul></li>")
    parts.append("</ul></li>")
    parts.append("</ul>")
    parts.append("<h2>Follow-up Questions</h2>")
    parts.append("<ul>")
    for f in data["followups"]:
        parts.append(f"<li><strong>{f['headline']}</strong> (strength {f['current_strength']}/3)<ul>")
        for q in f["questions"]:
            parts.append(f"<li>{q}</li>")
        parts.append("</ul></li>")
    parts.append("</ul>")
    return "\n".join(parts)


def render_notion(result: dict[str, Any]) -> str:
    # Notion accepts close-to-GitHub Markdown with callouts.
    md = render_markdown(result)
    callout = ("> [!NOTE]\n"
               f"> Generated by interview_synthesizer v1 -- schema {result['schema']}\n\n")
    return callout + md


def render_linear(result: dict[str, Any]) -> str:
    data = result["data"]
    lines: list[str] = []
    lines.append(f"## Interview Synthesis -- {data['study'].get('title', 'Untitled')}")
    lines.append(f"**Outcome:** {data['outcome']}")
    lines.append("")
    lines.append("**Top opportunities:**")
    for i, opp in enumerate(data["opportunities"][:5], 1):
        priority = "~~High~~" if opp["strength"] >= 3 else "~~Medium~~" if opp["strength"] == 2 else "~~Low~~"
        lines.append(f"{i}. {priority} {opp['title']}")
    lines.append("")
    lines.append("**Suggested next experiments (one issue each):**")
    for opp in data["opportunities"][:3]:
        if opp["solutions"]:
            lines.append(f"- [ ] {opp['solutions'][0]}")
    return "\n".join(lines)


RENDERERS = {
    "json": render_json,
    "markdown": render_markdown,
    "mermaid": render_mermaid,
    "confluence": render_confluence,
    "notion": render_notion,
    "linear": render_linear,
}


# ---------------------------------------------------------------------------
# Demo fixture
# ---------------------------------------------------------------------------

DEMO_PAYLOAD = {
    "study": {
        "title": "Finance close workflow discovery",
        "outcome": "Reduce time-to-close from 14 days to 5 days",
        "round": 1,
    },
    "interviews": [
        {
            "participant": "P1",
            "role": "Senior Finance Lead",
            "segment": "enterprise",
            "qa": [
                {"question": "Walk me through your last close.",
                 "answer": "Last Wednesday I pulled the bank feed. Two transactions came in as duplicates, so I spent four hours to re-key the ledger manually. The automation flagged a conflict but did not tell me which rule produced the match."},
            ],
        },
        {
            "participant": "P2",
            "role": "Controller",
            "segment": "mid-market",
            "qa": [
                {"question": "How do you verify automated matches?",
                 "answer": "I check every single one for the first three weeks. I do not trust it. I cannot see why it made each decision."},
            ],
        },
        {
            "participant": "P3",
            "role": "AP Specialist",
            "segment": "enterprise",
            "qa": [
                {"question": "Tell me about a smooth close.",
                 "answer": "Last quarter took 6 days. The slow part is always reconciling duplicates when rules change underneath us. I usually export to Excel and rebuild."},
            ],
        },
    ],
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synthesize customer interview transcripts into themes, an opportunity tree, and follow-up questions.",
    )
    parser.add_argument("--input", help="Path to interview JSON file (see assets/interview_input_template.json)")
    parser.add_argument("--format", choices=sorted(RENDERERS.keys()), default="markdown",
                        help="Output format (default: markdown)")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    parser.add_argument("--outcome", help="Override the outcome label at the top of the tree")
    parser.add_argument("--min-strength", type=int, default=1, choices=[1, 2, 3],
                        help="Drop themes below this evidence strength (default: 1)")
    parser.add_argument("--demo", action="store_true", help="Run on a built-in demo fixture (no --input needed)")
    args = parser.parse_args(argv)

    if not args.demo and not args.input:
        parser.error("--input is required (or pass --demo)")

    if args.demo:
        payload = DEMO_PAYLOAD
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except FileNotFoundError:
            print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
            return 2
        except json.JSONDecodeError as e:
            print(f"ERROR: invalid JSON in {args.input}: {e}", file=sys.stderr)
            return 2

    result = synthesize(payload, min_strength=args.min_strength, outcome_override=args.outcome)
    rendered = RENDERERS[args.format](result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(rendered)
            if not rendered.endswith("\n"):
                f.write("\n")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
        print(f"error: bad input ({type(exc).__name__}): {exc}", file=sys.stderr)
        sys.exit(2)
