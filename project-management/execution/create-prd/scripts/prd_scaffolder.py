#!/usr/bin/env python3
"""PRD Scaffolder - Generate a structured Product Requirements Document skeleton.

Generates a complete PRD markdown file with all 8 sections pre-filled with
placeholder guidance. Uses a proven 8-section framework: Summary, Contacts,
Background, Objective, Market Segments, Value Propositions, Solution, Release.

Usage:
    python prd_scaffolder.py --product-name "MyProduct" --objective "Short description" --segments "Segment A, Segment B"
    python prd_scaffolder.py --product-name "MyProduct" --objective "..." --segments "..." --output PRD-MyProduct.md

Standard library only. No external dependencies.
"""

import argparse
import sys
import textwrap
from datetime import date


def generate_prd(product_name: str, objective: str, segments: list[str]) -> str:
    """Generate a complete PRD markdown skeleton."""
    today = date.today().isoformat()
    segments_section = _build_segments_section(segments)
    value_props_section = _build_value_props_section(segments)

    return textwrap.dedent(f"""\
# PRD: {product_name}

**Status:** Draft
**Author:** [Your Name]
**Date:** {today}
**Last Updated:** {today}

---

## 1. Summary

<!-- Write 2-3 sentences. Answer: What is this? Who is it for? Why now? -->

{product_name} is [what it is] designed for [target users]. {objective}. This initiative is timely because [reason this matters now].

---

## 2. Contacts

| Name | Role | Responsibility |
|------|------|----------------|
| [Name] | Product Manager | Final decision on scope and priorities |
| [Name] | Engineering Lead | Technical feasibility and architecture |
| [Name] | Design Lead | UX direction and user research |
| [Name] | Stakeholder | Business approval and resourcing |

---

## 3. Background

### Context

<!-- What is the current state? What exists today? -->

[Describe the current product/market/user situation. What do users do today?]

### Why Now?

<!-- What changed that makes this urgent? -->

[Market shift, competitive pressure, customer feedback trend, strategic pivot, etc.]

### What Recently Became Possible?

<!-- New capabilities, data, partnerships, or insights -->

[New technology, API availability, partnership, data insight, or team capacity that enables this.]

---

## 4. Objective

### Business Benefit

<!-- How does this move a business metric? -->

[Specify: revenue impact, retention improvement, cost reduction, market share gain, etc.]

### Customer Benefit

<!-- How does this improve the user's life? -->

[Specify: time saved, friction removed, new capability unlocked, risk reduced, etc.]

### Key Results (OKR Format)

**Objective:** {objective}

| Key Result | Current | Target | Deadline |
|------------|---------|--------|----------|
| KR1: [Metric description] | [Baseline] | [Target] | [Date] |
| KR2: [Metric description] | [Baseline] | [Target] | [Date] |
| KR3: [Metric description] | [Baseline] | [Target] | [Date] |

---

## 5. Market Segment(s)

<!-- Define segments by problems/jobs, not demographics -->

{segments_section}

---

## 6. Value Proposition(s)

<!-- For each segment: jobs, gains, pains, competitive advantage -->

{value_props_section}

### Value Curve

<!-- Where do you compete, exceed, or deliberately underinvest vs alternatives? -->

| Factor | Alternative A | Alternative B | {product_name} |
|--------|--------------|--------------|{'-' * max(len(product_name), 5)}|
| [Factor 1] | Low | Medium | High |
| [Factor 2] | High | Medium | Low (intentional) |
| [Factor 3] | Medium | Low | High |

---

## 7. Solution

### UX / Prototypes

<!-- Key screens, flows, interaction patterns. Link to design files. -->

- [ ] [Screen/Flow 1]: [Description]
- [ ] [Screen/Flow 2]: [Description]
- [ ] [Screen/Flow 3]: [Description]

**Design links:** [Figma/Sketch/etc.]

### Key Features

| # | Feature | Priority | Description |
|---|---------|----------|-------------|
| 1 | [Feature name] | P0 | [One sentence] |
| 2 | [Feature name] | P0 | [One sentence] |
| 3 | [Feature name] | P1 | [One sentence] |
| 4 | [Feature name] | P1 | [One sentence] |
| 5 | [Feature name] | P2 | [One sentence] |

### Technology (Optional)

<!-- Architecture decisions, integrations, infrastructure requirements -->

- **Architecture:** [Relevant constraints or decisions]
- **Integrations:** [Third-party systems involved]
- **Infrastructure:** [Hosting, scaling, data storage considerations]

### Assumptions

<!-- Things believed true but not yet validated. Include validation plan. -->

| # | Assumption | Validation Plan | Status |
|---|-----------|-----------------|--------|
| 1 | [Assumption] | [How to test] | Unvalidated |
| 2 | [Assumption] | [How to test] | Unvalidated |
| 3 | [Assumption] | [How to test] | Unvalidated |

---

## 8. Release

### Timeline

<!-- Use T-shirt sizes or Now/Next/Later -->

| Phase | Scope | Size | Target |
|-------|-------|------|--------|
| v1 (Now) | [Core functionality] | [S/M/L/XL] | [Relative date] |
| v1.1 (Next) | [Enhancements] | [S/M/L/XL] | [Relative date] |
| v2 (Later) | [Expansion] | [S/M/L/XL] | [Relative date] |

### v1 Scope (What Ships First)

- [Feature/capability 1]
- [Feature/capability 2]
- [Feature/capability 3]

### Explicitly Deferred

<!-- What was considered but intentionally excluded from v1 -->

- [Deferred item 1] -- Reason: [why deferred]
- [Deferred item 2] -- Reason: [why deferred]

### Success Criteria

<!-- When do we know v1 succeeded? Reference Key Results from Section 4. -->

v1 is successful when:
1. KR1 reaches [target] (see Section 4)
2. KR2 reaches [target] (see Section 4)
3. No critical usability issues reported in first [timeframe]

---

*Generated by PRD Scaffolder on {today}*
""")


def _build_segments_section(segments: list[str]) -> str:
    """Build the market segments section."""
    lines = []
    for i, segment in enumerate(segments, 1):
        lines.append(f"### Segment {i}: {segment}")
        lines.append("")
        lines.append(f'**Definition:** People who need to [job/problem] because [context].')
        lines.append("")
        lines.append(f"- **Size estimate:** [TAM/SAM/SOM or qualitative size]")
        lines.append(f"- **Current behavior:** [How do they solve this today?]")
        lines.append(f"- **Key pain point:** [Primary frustration or unmet need]")
        lines.append("")
    return "\n".join(lines)


def _build_value_props_section(segments: list[str]) -> str:
    """Build the value propositions section."""
    lines = []
    for i, segment in enumerate(segments, 1):
        lines.append(f"### {segment}")
        lines.append("")
        lines.append(f"- **Jobs addressed:** [What tasks/goals does the product help accomplish?]")
        lines.append(f"- **Gains created:** [What positive outcomes does the user experience?]")
        lines.append(f"- **Pains relieved:** [What frustrations or obstacles are removed?]")
        lines.append(f"- **Competitive advantage:** [Why is this approach better than alternatives?]")
        lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a structured PRD markdown skeleton with 8 sections.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python prd_scaffolder.py --product-name "SearchBoost" --objective "Help users find products 50%% faster" --segments "Power users, New customers"
              python prd_scaffolder.py --product-name "SearchBoost" --objective "..." --segments "Power users, New customers" --output PRD-SearchBoost.md
        """),
    )
    parser.add_argument(
        "--product-name",
        required=True,
        help="Name of the product (used in title and filename suggestion)",
    )
    parser.add_argument(
        "--objective",
        required=True,
        help="Short description of the product objective (1-2 sentences)",
    )
    parser.add_argument(
        "--segments",
        required=True,
        help="Comma-separated list of market segments (e.g., 'Segment A, Segment B')",
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
    segments = [s.strip() for s in args.segments.split(",") if s.strip()]

    if not segments:
        print("Error: At least one market segment is required.", file=sys.stderr)
        sys.exit(1)

    prd = generate_prd(args.product_name, args.objective, segments)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(prd)
        print(f"PRD written to {args.output}", file=sys.stderr)
    else:
        print(prd)


if __name__ == "__main__":
    main()
