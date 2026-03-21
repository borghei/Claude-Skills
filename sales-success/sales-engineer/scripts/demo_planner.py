#!/usr/bin/env python3
"""Generate structured demo plans from prospect requirements and discovery data.

Reads prospect information, requirements, and stakeholder data to produce
a tailored demo plan following the CONNECT-CONTEXT-SHOW-SUMMARIZE-CLOSE structure.

Usage:
    python demo_planner.py --data prospect.json
    python demo_planner.py --data prospects.csv --json
    python demo_planner.py --data prospect.json --duration 45
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime


DEFAULT_AGENDA = {
    30: {"connect": 3, "context": 3, "show": 15, "summarize": 4, "close": 5},
    45: {"connect": 5, "context": 5, "show": 20, "summarize": 5, "close": 10},
    60: {"connect": 5, "context": 10, "show": 30, "summarize": 5, "close": 10},
    90: {"connect": 5, "context": 10, "show": 50, "summarize": 10, "close": 15},
}

USE_CASE_PRIORITY = {
    "critical": 3,
    "high": 2,
    "medium": 1,
    "low": 0,
}


def load_data(filepath):
    """Load prospect data from CSV or JSON file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif ext == ".csv":
        with open(filepath, "r") as f:
            return list(csv.DictReader(f))
    else:
        print(f"Error: Unsupported file format '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def parse_list(value):
    """Parse a list from string (semicolon or comma separated) or actual list."""
    if isinstance(value, list):
        return value
    if not value or not str(value).strip():
        return []
    val = str(value).strip()
    if ";" in val:
        return [x.strip() for x in val.split(";") if x.strip()]
    return [x.strip() for x in val.split(",") if x.strip()]


def extract_stakeholders(prospect):
    """Extract attendee/stakeholder information."""
    stakeholders = []

    # Try structured fields first
    for i in range(1, 8):
        name = prospect.get(f"attendee_{i}_name", prospect.get(f"stakeholder_{i}", ""))
        role = prospect.get(f"attendee_{i}_role", prospect.get(f"role_{i}", ""))
        priority = prospect.get(f"attendee_{i}_priority", prospect.get(f"priority_{i}", ""))
        if name:
            stakeholders.append({
                "name": name,
                "role": role or "Unknown",
                "top_priority": priority or "To be determined",
            })

    # Fallback to list fields
    if not stakeholders:
        names = parse_list(prospect.get("attendees", prospect.get("stakeholders", "")))
        roles = parse_list(prospect.get("roles", ""))
        for i, name in enumerate(names):
            stakeholders.append({
                "name": name,
                "role": roles[i] if i < len(roles) else "Unknown",
                "top_priority": "To be determined",
            })

    return stakeholders


def extract_use_cases(prospect):
    """Extract and prioritize use cases for the demo."""
    use_cases = []

    # Structured use case fields
    for i in range(1, 8):
        uc = prospect.get(f"use_case_{i}", "")
        pain = prospect.get(f"pain_point_{i}", prospect.get(f"use_case_{i}_pain", ""))
        priority = prospect.get(f"use_case_{i}_priority", "medium")
        if uc:
            use_cases.append({
                "use_case": uc,
                "pain_point": pain or "To be mapped to discovery findings",
                "priority": priority.lower() if priority else "medium",
            })

    # Fallback to list fields
    if not use_cases:
        ucs = parse_list(prospect.get("use_cases", prospect.get("requirements", "")))
        pains = parse_list(prospect.get("pain_points", ""))
        for i, uc in enumerate(ucs):
            use_cases.append({
                "use_case": uc,
                "pain_point": pains[i] if i < len(pains) else "To be mapped",
                "priority": "medium",
            })

    # Sort by priority
    use_cases.sort(key=lambda x: USE_CASE_PRIORITY.get(x["priority"], 1), reverse=True)
    return use_cases


def extract_objections(prospect):
    """Extract anticipated objections."""
    objections = []
    for i in range(1, 6):
        obj = prospect.get(f"objection_{i}", "")
        response = prospect.get(f"objection_{i}_response", "")
        if obj:
            objections.append({"objection": obj, "prepared_response": response or "Prepare response"})

    if not objections:
        raw = parse_list(prospect.get("objections", prospect.get("concerns", "")))
        for obj in raw:
            objections.append({"objection": obj, "prepared_response": "Prepare response"})

    return objections


def generate_demo_plan(prospect, duration):
    """Generate a complete demo plan for a prospect."""
    name = prospect.get("company", prospect.get("prospect", prospect.get("name", "Unknown")))
    industry = prospect.get("industry", "N/A")
    deal_size = prospect.get("deal_size", prospect.get("amount", prospect.get("acv", "N/A")))
    ae = prospect.get("account_executive", prospect.get("ae", "N/A"))
    demo_date = prospect.get("demo_date", "TBD")

    stakeholders = extract_stakeholders(prospect)
    use_cases = extract_use_cases(prospect)
    objections = extract_objections(prospect)

    # Competitive context
    competitors = parse_list(prospect.get("competitors", prospect.get("competition", "")))
    differentiators = parse_list(prospect.get("differentiators", ""))

    # Select agenda timing
    closest_duration = min(DEFAULT_AGENDA.keys(), key=lambda x: abs(x - duration))
    agenda = DEFAULT_AGENDA[closest_duration]

    # Calculate max use cases for show time
    show_minutes = agenda["show"]
    max_use_cases = max(1, show_minutes // 8)  # ~8 min per use case

    # Technical environment
    tech_stack = parse_list(prospect.get("tech_stack", prospect.get("technology", "")))
    integrations = parse_list(prospect.get("integrations_needed", prospect.get("integrations", "")))

    demo_env = prospect.get("demo_environment", prospect.get("demo_url", "Configure before demo"))
    test_data = prospect.get("test_data", "Load customer-relevant sample data")

    # Success criteria
    success = prospect.get("demo_success_criteria", prospect.get(
        "success_criteria", "Champion confirms technical fit and agrees to next step"
    ))

    # Pre-demo checklist
    checklist = [
        "Discovery findings reviewed and confirmed current",
        "Demo environment tested and functional",
        "Test data loaded with customer-relevant scenarios",
        "Stakeholder priorities mapped to use cases",
        "Competitive differentiators prepared",
        "Anticipated objections and responses reviewed",
        "Dry run completed within 24 hours of demo",
        "Calendar invite sent with agenda preview",
    ]

    return {
        "company": name,
        "industry": industry,
        "deal_size": deal_size,
        "account_executive": ae,
        "demo_date": demo_date,
        "duration_minutes": duration,
        "stakeholders": stakeholders,
        "agenda": {
            "1_connect": f"{agenda['connect']} min - Recap discovery, confirm priorities, set agenda",
            "2_context": f"{agenda['context']} min - Frame solution in prospect's language and pain points",
            "3_show": f"{agenda['show']} min - Demonstrate top {min(len(use_cases), max_use_cases)} use cases",
            "4_summarize": f"{agenda['summarize']} min - Recap value, address open concerns",
            "5_close": f"{agenda['close']} min - Define next steps, owners, and timeline",
        },
        "use_cases": use_cases[:max_use_cases],
        "additional_use_cases": use_cases[max_use_cases:] if len(use_cases) > max_use_cases else [],
        "competitive_context": {
            "competitors": competitors,
            "differentiators": differentiators,
        },
        "anticipated_objections": objections,
        "technical_environment": {
            "tech_stack": tech_stack,
            "integrations_needed": integrations,
            "demo_environment": demo_env,
            "test_data": test_data,
        },
        "success_criteria": success,
        "pre_demo_checklist": checklist,
    }


def format_markdown(plan):
    """Generate demo plan as markdown document."""
    lines = []
    lines.append(f"# Demo Plan: {plan['company']}")
    lines.append(f"\n**Industry:** {plan['industry']}  |  **Deal Size:** {plan['deal_size']}  |  **AE:** {plan['account_executive']}")
    lines.append(f"**Demo Date:** {plan['demo_date']}  |  **Duration:** {plan['duration_minutes']} min")
    lines.append(f"**Prepared:** {datetime.now().strftime('%Y-%m-%d')}")

    if plan["stakeholders"]:
        lines.append(f"\n## Attendees")
        lines.append(f"| Name | Role | Top Priority |")
        lines.append(f"|------|------|-------------|")
        for s in plan["stakeholders"]:
            lines.append(f"| {s['name']} | {s['role']} | {s['top_priority']} |")

    lines.append(f"\n## Agenda ({plan['duration_minutes']} min)")
    for step, desc in plan["agenda"].items():
        step_name = step.split("_", 1)[1].upper()
        lines.append(f"- **{step_name}:** {desc}")

    lines.append(f"\n## Use Cases to Demonstrate")
    for i, uc in enumerate(plan["use_cases"], 1):
        lines.append(f"\n### {i}. {uc['use_case']} [{uc['priority'].upper()}]")
        lines.append(f"- **Addresses:** {uc['pain_point']}")

    if plan["additional_use_cases"]:
        lines.append(f"\n### Deferred Use Cases (time permitting)")
        for uc in plan["additional_use_cases"]:
            lines.append(f"- {uc['use_case']} ({uc['priority']})")

    if plan["competitive_context"]["competitors"]:
        lines.append(f"\n## Competitive Positioning")
        for comp in plan["competitive_context"]["competitors"]:
            lines.append(f"- vs **{comp}**: Highlight [specific differentiator]")
        if plan["competitive_context"]["differentiators"]:
            lines.append(f"\n**Key Differentiators:**")
            for d in plan["competitive_context"]["differentiators"]:
                lines.append(f"- {d}")

    if plan["anticipated_objections"]:
        lines.append(f"\n## Anticipated Objections")
        lines.append(f"| Objection | Prepared Response |")
        lines.append(f"|-----------|------------------|")
        for obj in plan["anticipated_objections"]:
            lines.append(f"| {obj['objection']} | {obj['prepared_response']} |")

    lines.append(f"\n## Demo Environment")
    lines.append(f"- **Instance:** {plan['technical_environment']['demo_environment']}")
    lines.append(f"- **Test Data:** {plan['technical_environment']['test_data']}")
    if plan["technical_environment"]["tech_stack"]:
        lines.append(f"- **Prospect Tech Stack:** {', '.join(plan['technical_environment']['tech_stack'])}")
    if plan["technical_environment"]["integrations_needed"]:
        lines.append(f"- **Integrations to Show:** {', '.join(plan['technical_environment']['integrations_needed'])}")

    lines.append(f"\n## Success Criteria")
    lines.append(f"- {plan['success_criteria']}")

    lines.append(f"\n## Pre-Demo Checklist")
    for item in plan["pre_demo_checklist"]:
        lines.append(f"- [ ] {item}")

    lines.append(f"\n---")
    lines.append(f"*Generated by Demo Planner | {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(lines)


def format_human(plans):
    """Format multiple demo plans for console output."""
    lines = []
    lines.append("=" * 70)
    lines.append("DEMO PLAN GENERATION REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Plans Generated: {len(plans)}")
    lines.append("=" * 70)

    for plan in plans:
        lines.append(f"\n{format_markdown(plan)}")
        lines.append("\n" + "=" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate structured demo plans from prospect requirements."
    )
    parser.add_argument("--data", required=True, help="Path to prospect data CSV or JSON file")
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Demo duration in minutes (default: 60)",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    prospects = load_data(args.data)
    if not prospects:
        print("Error: No prospect data found in input file.", file=sys.stderr)
        sys.exit(1)

    plans = [generate_demo_plan(p, args.duration) for p in prospects]

    if args.json:
        print(json.dumps(plans, indent=2))
    else:
        print(format_human(plans))

    sys.exit(0)


if __name__ == "__main__":
    main()
