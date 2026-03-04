#!/usr/bin/env python3
"""Roadmap Transformer - Convert output-based roadmap items to outcome-driven ones.

Takes a list of feature/project initiatives and generates outcome statement
templates, suggested metrics, and strategic questions for each. Helps teams
shift from "what are we building?" to "what customer outcome are we enabling?"

Usage:
    python roadmap_transformer.py --input roadmap.json
    python roadmap_transformer.py --input roadmap.json --format json
    python roadmap_transformer.py --demo
    python roadmap_transformer.py --demo --format json

Input JSON format:
    {
        "initiatives": [
            {
                "title": "Build advanced search",
                "description": "Add filters, autocomplete, and relevance ranking",
                "quarter": "Q2 2026",
                "type": "feature"
            }
        ]
    }

Standard library only. No external dependencies.
"""

import argparse
import json
import sys
import textwrap
from datetime import date


# Mapping of initiative types to relevant outcome prompts and metric suggestions
TYPE_GUIDANCE = {
    "feature": {
        "outcome_prompts": [
            "What customer problem does this feature solve?",
            "How will the customer's workflow change after this ships?",
            "What would the customer do if this feature did not exist?",
        ],
        "metric_categories": [
            "Adoption (% of target users who use this within 30 days)",
            "Efficiency (time saved or steps reduced for the core task)",
            "Satisfaction (NPS/CSAT change among users of this feature)",
        ],
    },
    "improvement": {
        "outcome_prompts": [
            "What specific friction point does this improvement address?",
            "How much time/effort does the current experience cost users?",
            "What is the measurable gap between current and desired performance?",
        ],
        "metric_categories": [
            "Performance (speed, reliability, or accuracy improvement)",
            "Retention (churn reduction or engagement increase)",
            "Support (reduction in related support tickets or complaints)",
        ],
    },
    "infrastructure": {
        "outcome_prompts": [
            "What user-facing capability does this infrastructure enable?",
            "What becomes possible for customers that was not possible before?",
            "How does this reduce risk or cost for the business?",
        ],
        "metric_categories": [
            "Reliability (uptime, error rate, or recovery time)",
            "Scalability (capacity headroom or performance under load)",
            "Velocity (team shipping speed or deployment frequency)",
        ],
    },
}

DEMO_DATA = {
    "initiatives": [
        {
            "title": "Build advanced search",
            "description": "Add full-text search with filters, autocomplete, and relevance ranking to the product catalog.",
            "quarter": "Q2 2026",
            "type": "feature",
        },
        {
            "title": "Improve onboarding flow",
            "description": "Redesign the first-time user experience to reduce steps and add contextual guidance.",
            "quarter": "Q2 2026",
            "type": "improvement",
        },
        {
            "title": "Migrate to new database",
            "description": "Move from PostgreSQL 12 to PostgreSQL 16 with connection pooling and read replicas.",
            "quarter": "Q3 2026",
            "type": "infrastructure",
        },
        {
            "title": "Launch mobile app",
            "description": "Build iOS and Android apps with core functionality from the web platform.",
            "quarter": "Q3 2026",
            "type": "feature",
        },
        {
            "title": "Add team collaboration features",
            "description": "Shared workspaces, commenting, and real-time editing for team plans.",
            "quarter": "Q4 2026",
            "type": "feature",
        },
    ]
}


def _quarter_to_horizon(quarter: str) -> str:
    """Map a quarter string to Now/Next/Later based on current date.

    Heuristic: current quarter = Now, next quarter = Next, everything else = Later.
    If quarter is empty or unparseable, returns 'Later'.
    """
    today = date.today()
    current_q = (today.month - 1) // 3 + 1
    current_year = today.year

    # Parse quarter like "Q2 2026"
    parts = quarter.strip().upper().split()
    if len(parts) != 2 or not parts[0].startswith("Q"):
        return "Later"

    try:
        q_num = int(parts[0][1:])
        q_year = int(parts[1])
    except (ValueError, IndexError):
        return "Later"

    # Calculate distance in quarters
    distance = (q_year - current_year) * 4 + (q_num - current_q)

    if distance <= 0:
        return "Now"
    elif distance == 1:
        return "Next"
    else:
        return "Later"


def transform_initiative(initiative: dict) -> dict:
    """Transform a single initiative from output to outcome format."""
    title = initiative.get("title", "Untitled")
    description = initiative.get("description", "")
    quarter = initiative.get("quarter", "")
    init_type = initiative.get("type", "feature")

    guidance = TYPE_GUIDANCE.get(init_type, TYPE_GUIDANCE["feature"])
    horizon = _quarter_to_horizon(quarter)

    # Generate outcome statement template
    outcome_template = (
        f'Enable [customer segment] to [desired outcome from "{title}"] '
        f"so that [business impact]"
    )

    # Generate "so what?" chain
    so_what_chain = [
        f'"{title}"',
        f"-> So what? [What changes for the user?]",
        f"-> So what? [What behavior or metric shifts?]",
        f"-> So what? [What business value results?]",
    ]

    return {
        "original": {
            "title": title,
            "description": description,
            "quarter": quarter,
            "type": init_type,
        },
        "transformed": {
            "horizon": horizon,
            "outcome_statement_template": outcome_template,
            "so_what_chain": so_what_chain,
            "strategic_questions": guidance["outcome_prompts"],
            "suggested_metrics": guidance["metric_categories"],
            "dependencies": [
                "[What technical prerequisites must be in place?]",
                "[What organizational alignment is needed?]",
                "[What market conditions must hold true?]",
            ],
        },
    }


def format_markdown(results: list[dict]) -> str:
    """Format transformed roadmap as markdown."""
    lines = []
    today = date.today().isoformat()

    lines.append("# Outcome Roadmap")
    lines.append("")
    lines.append(f"**Generated:** {today}")
    lines.append(f"**Initiatives Transformed:** {len(results)}")
    lines.append("")

    # Group by horizon
    horizons = {"Now": [], "Next": [], "Later": []}
    for r in results:
        h = r["transformed"]["horizon"]
        horizons.setdefault(h, []).append(r)

    for horizon_name in ["Now", "Next", "Later"]:
        items = horizons.get(horizon_name, [])
        if not items:
            continue

        lines.append(f"## {horizon_name}")
        lines.append("")

        commitment = {
            "Now": "High -- team assigned, scope defined",
            "Next": "Medium -- direction set, scope flexible",
            "Later": "Low -- strategic intent only",
        }
        lines.append(f"**Commitment Level:** {commitment.get(horizon_name, 'TBD')}")
        lines.append("")

        for item in items:
            orig = item["original"]
            trans = item["transformed"]

            lines.append(f"### {orig['title']}")
            lines.append("")
            lines.append(f"**Original:** {orig['description']}")
            lines.append(f"**Type:** {orig['type']}  |  **Quarter:** {orig['quarter']}")
            lines.append("")

            lines.append("**Outcome Statement (fill in):**")
            lines.append(f"> {trans['outcome_statement_template']}")
            lines.append("")

            lines.append("**\"So What?\" Chain:**")
            for step in trans["so_what_chain"]:
                lines.append(f"- {step}")
            lines.append("")

            lines.append("**Strategic Questions to Answer:**")
            for q in trans["strategic_questions"]:
                lines.append(f"- [ ] {q}")
            lines.append("")

            lines.append("**Suggested Success Metrics:**")
            for m in trans["suggested_metrics"]:
                lines.append(f"- {m}")
            lines.append("")

            lines.append("**Dependencies:**")
            for d in trans["dependencies"]:
                lines.append(f"- {d}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def format_text(results: list[dict]) -> str:
    """Format transformed roadmap as plain text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("OUTCOME ROADMAP TRANSFORMATION")
    lines.append("=" * 60)
    lines.append("")

    for i, item in enumerate(results, 1):
        orig = item["original"]
        trans = item["transformed"]

        lines.append(f"--- Initiative {i}: {orig['title']} ---")
        lines.append(f"  Original: {orig['description']}")
        lines.append(f"  Type: {orig['type']}  |  Quarter: {orig['quarter']}  |  Horizon: {trans['horizon']}")
        lines.append("")
        lines.append("  Outcome Statement Template:")
        wrapped = textwrap.fill(trans["outcome_statement_template"], width=70, initial_indent="    ", subsequent_indent="    ")
        lines.append(wrapped)
        lines.append("")
        lines.append("  'So What?' Chain:")
        for step in trans["so_what_chain"]:
            lines.append(f"    {step}")
        lines.append("")
        lines.append("  Strategic Questions:")
        for q in trans["strategic_questions"]:
            lines.append(f"    - {q}")
        lines.append("")
        lines.append("  Suggested Metrics:")
        for m in trans["suggested_metrics"]:
            lines.append(f"    - {m}")
        lines.append("")

    lines.append("=" * 60)
    lines.append(f"Total initiatives transformed: {len(results)}")

    horizons = {}
    for r in results:
        h = r["transformed"]["horizon"]
        horizons[h] = horizons.get(h, 0) + 1
    summary = " | ".join(f"{k}: {v}" for k, v in sorted(horizons.items()))
    lines.append(f"By horizon: {summary}")
    lines.append("=" * 60)

    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Transform output-based roadmap items into outcome-driven initiatives.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python roadmap_transformer.py --demo
              python roadmap_transformer.py --input roadmap.json
              python roadmap_transformer.py --input roadmap.json --format json
              python roadmap_transformer.py --demo --format markdown --output roadmap-outcomes.md

            Input JSON format:
              {
                "initiatives": [
                  {
                    "title": "Build advanced search",
                    "description": "Full-text search with filters",
                    "quarter": "Q2 2026",
                    "type": "feature"
                  }
                ]
              }
            Supported types: feature, improvement, infrastructure
        """),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--input",
        help="Path to JSON file containing roadmap initiatives",
    )
    group.add_argument(
        "--demo",
        action="store_true",
        help="Run transformation on built-in demo data",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format: text (default), json, or markdown",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path. If omitted, prints to stdout.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Main entry point."""
    args = parse_args(argv)

    if args.demo:
        data = DEMO_DATA
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.input}: {e}", file=sys.stderr)
            sys.exit(1)

    initiatives = data.get("initiatives", [])
    if not initiatives:
        print("Error: No initiatives found in input data.", file=sys.stderr)
        sys.exit(1)

    results = [transform_initiative(init) for init in initiatives]

    if args.format == "json":
        output = json.dumps(results, indent=2)
    elif args.format == "markdown":
        output = format_markdown(results)
    else:
        output = format_text(results)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
