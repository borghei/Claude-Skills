#!/usr/bin/env python3
"""
Stakeholder Mapper

Classifies stakeholders by power/interest into a Mendelow's Matrix grid and
generates a tailored communication plan for each quadrant. Supports optional
influence and attitude fields for richer analysis.

Usage:
    python stakeholder_mapper.py stakeholders.json
    python stakeholder_mapper.py stakeholders.json --format json
    python stakeholder_mapper.py --demo
    python stakeholder_mapper.py --demo --format json

Input JSON schema:
    {
        "project": "Project Name",
        "stakeholders": [
            {
                "name": "Jane Smith",
                "role": "VP Engineering",
                "power": 8,
                "interest": 9,
                "influence": 7,
                "attitude": "supporter"
            }
        ]
    }

Fields:
    name        (required) - Stakeholder name
    role        (required) - Organizational role or title
    power       (required) - Power level 1-10
    interest    (required) - Interest level 1-10
    influence   (optional) - Influence level 1-10
    attitude    (optional) - supporter | neutral | blocker
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Quadrant Configuration
# ---------------------------------------------------------------------------

POWER_THRESHOLD = 5
INTEREST_THRESHOLD = 5

QUADRANTS = {
    "manage_closely": {
        "label": "Manage Closely",
        "description": "High power, high interest - key players requiring active engagement",
        "power": "high",
        "interest": "high",
        "communication": {
            "frequency": "Weekly",
            "channel": "1:1 meetings, steering committee, direct phone/video",
            "key_message": "Detailed progress, decisions needed, risk exposure, strategic alignment",
            "tactics": [
                "Weekly 1:1 meetings with personalized updates",
                "Include in steering committee and governance forums",
                "Proactive issue escalation before they discover problems",
                "Involve in key decisions and trade-off discussions",
                "Share draft deliverables for early feedback"
            ]
        }
    },
    "keep_satisfied": {
        "label": "Keep Satisfied",
        "description": "High power, low interest - influential stakeholders requiring minimal but high-quality touchpoints",
        "power": "high",
        "interest": "low",
        "communication": {
            "frequency": "Monthly",
            "channel": "Executive summary, email briefing, quarterly review",
            "key_message": "High-level status, budget health, strategic impact, escalations only",
            "tactics": [
                "Monthly executive summary (one page max)",
                "Escalate blockers and budget issues immediately",
                "Invite to milestone demos and phase-gate reviews",
                "Keep communications concise and outcome-focused",
                "Respect their time - no unnecessary meetings"
            ]
        }
    },
    "keep_informed": {
        "label": "Keep Informed",
        "description": "Low power, high interest - engaged stakeholders who want visibility",
        "power": "low",
        "interest": "high",
        "communication": {
            "frequency": "Bi-weekly",
            "channel": "Newsletter, demo invites, shared dashboard, Slack/Teams channel",
            "key_message": "Progress updates, upcoming changes, how their area is affected",
            "tactics": [
                "Bi-weekly newsletter or status email",
                "Invite to sprint demos and showcase events",
                "Provide access to project dashboard or wiki",
                "Create feedback channels for input",
                "Acknowledge their contributions and interest"
            ]
        }
    },
    "monitor": {
        "label": "Monitor",
        "description": "Low power, low interest - minimal engagement needed",
        "power": "low",
        "interest": "low",
        "communication": {
            "frequency": "Quarterly",
            "channel": "Organizational newsletter, all-hands updates, intranet",
            "key_message": "Major milestones, organizational impact, general awareness",
            "tactics": [
                "Quarterly status in organizational newsletter",
                "Include in all-hands project updates",
                "Make information available on-demand (wiki/intranet)",
                "Re-assess classification periodically",
                "Watch for changes in power or interest levels"
            ]
        }
    }
}


# ---------------------------------------------------------------------------
# Demo Data
# ---------------------------------------------------------------------------

DEMO_DATA = {
    "project": "Platform Modernization Initiative",
    "stakeholders": [
        {
            "name": "Sarah Chen",
            "role": "VP Engineering",
            "power": 9,
            "interest": 9,
            "influence": 8,
            "attitude": "supporter"
        },
        {
            "name": "Michael Torres",
            "role": "CFO",
            "power": 10,
            "interest": 3,
            "influence": 9,
            "attitude": "neutral"
        },
        {
            "name": "Priya Patel",
            "role": "Lead Developer",
            "power": 4,
            "interest": 10,
            "influence": 6,
            "attitude": "supporter"
        },
        {
            "name": "James Wright",
            "role": "Head of Compliance",
            "power": 7,
            "interest": 8,
            "influence": 7,
            "attitude": "blocker"
        },
        {
            "name": "Lisa Kim",
            "role": "Marketing Director",
            "power": 6,
            "interest": 4,
            "influence": 5,
            "attitude": "neutral"
        },
        {
            "name": "David Okafor",
            "role": "Junior Analyst",
            "power": 2,
            "interest": 3,
            "influence": 2,
            "attitude": "neutral"
        },
        {
            "name": "Emily Rodriguez",
            "role": "Product Manager",
            "power": 7,
            "interest": 9,
            "influence": 7,
            "attitude": "supporter"
        },
        {
            "name": "Tom Anderson",
            "role": "External Auditor",
            "power": 8,
            "interest": 2,
            "influence": 6,
            "attitude": "neutral"
        },
        {
            "name": "Aisha Mohammed",
            "role": "UX Researcher",
            "power": 3,
            "interest": 8,
            "influence": 4,
            "attitude": "supporter"
        },
        {
            "name": "Robert Chang",
            "role": "IT Operations Manager",
            "power": 5,
            "interest": 7,
            "influence": 5,
            "attitude": "blocker"
        }
    ]
}


# ---------------------------------------------------------------------------
# Stakeholder Classification
# ---------------------------------------------------------------------------

class Stakeholder:
    """Represents a single stakeholder with classification data."""

    def __init__(self, data: Dict[str, Any]):
        self.name: str = data.get("name", "Unknown")
        self.role: str = data.get("role", "Unknown")
        self.power: int = max(1, min(10, data.get("power", 5)))
        self.interest: int = max(1, min(10, data.get("interest", 5)))
        self.influence: Optional[int] = data.get("influence")
        self.attitude: str = data.get("attitude", "neutral").lower()

        if self.influence is not None:
            self.influence = max(1, min(10, self.influence))
        if self.attitude not in ("supporter", "neutral", "blocker"):
            self.attitude = "neutral"

        self.quadrant = self._classify()

    def _classify(self) -> str:
        """Classify stakeholder into a power/interest quadrant."""
        high_power = self.power > POWER_THRESHOLD
        high_interest = self.interest > INTEREST_THRESHOLD

        if high_power and high_interest:
            return "manage_closely"
        elif high_power and not high_interest:
            return "keep_satisfied"
        elif not high_power and high_interest:
            return "keep_informed"
        else:
            return "monitor"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize stakeholder to a dictionary."""
        result = {
            "name": self.name,
            "role": self.role,
            "power": self.power,
            "interest": self.interest,
            "attitude": self.attitude,
            "quadrant": self.quadrant,
            "quadrant_label": QUADRANTS[self.quadrant]["label"]
        }
        if self.influence is not None:
            result["influence"] = self.influence
        return result


# ---------------------------------------------------------------------------
# Analysis Functions
# ---------------------------------------------------------------------------

def classify_stakeholders(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse input data and classify all stakeholders."""
    project_name = data.get("project", "Unnamed Project")
    raw_stakeholders = data.get("stakeholders", [])

    if not raw_stakeholders:
        raise ValueError("No stakeholders found in input data")

    stakeholders = [Stakeholder(s) for s in raw_stakeholders]

    # Group by quadrant
    quadrant_groups: Dict[str, List[Stakeholder]] = {
        "manage_closely": [],
        "keep_satisfied": [],
        "keep_informed": [],
        "monitor": []
    }
    for s in stakeholders:
        quadrant_groups[s.quadrant].append(s)

    # Identify blockers
    blockers = [s for s in stakeholders if s.attitude == "blocker"]

    # Summary statistics
    summary = {
        "project": project_name,
        "total_stakeholders": len(stakeholders),
        "classification_threshold": {
            "power": POWER_THRESHOLD,
            "interest": INTEREST_THRESHOLD
        },
        "quadrant_counts": {
            q: len(members) for q, members in quadrant_groups.items()
        },
        "attitude_counts": {
            "supporter": len([s for s in stakeholders if s.attitude == "supporter"]),
            "neutral": len([s for s in stakeholders if s.attitude == "neutral"]),
            "blocker": len([s for s in stakeholders if s.attitude == "blocker"])
        },
        "blocker_count": len(blockers),
        "average_power": sum(s.power for s in stakeholders) / len(stakeholders),
        "average_interest": sum(s.interest for s in stakeholders) / len(stakeholders),
        "analysis_date": datetime.now().strftime("%Y-%m-%d")
    }

    return {
        "summary": summary,
        "quadrant_groups": quadrant_groups,
        "blockers": blockers,
        "all_stakeholders": stakeholders
    }


def build_communication_plan(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a communication plan based on stakeholder classification."""
    plan = {}
    quadrant_groups = analysis["quadrant_groups"]

    for quadrant_key, members in quadrant_groups.items():
        config = QUADRANTS[quadrant_key]
        comm = config["communication"]
        plan[quadrant_key] = {
            "label": config["label"],
            "description": config["description"],
            "stakeholder_count": len(members),
            "stakeholders": [s.name for s in members],
            "frequency": comm["frequency"],
            "channel": comm["channel"],
            "key_message": comm["key_message"],
            "tactics": comm["tactics"]
        }

    return plan


def build_blocker_strategy(blockers: List[Stakeholder]) -> List[Dict[str, Any]]:
    """Generate engagement strategies for blocker stakeholders."""
    strategies = []
    for b in blockers:
        strategy = {
            "name": b.name,
            "role": b.role,
            "power": b.power,
            "interest": b.interest,
            "quadrant": QUADRANTS[b.quadrant]["label"],
            "risk_level": "High" if b.power > POWER_THRESHOLD else "Medium",
            "recommended_actions": []
        }

        if b.power > POWER_THRESHOLD:
            strategy["recommended_actions"] = [
                "Schedule urgent 1:1 to understand concerns",
                "Identify root cause of resistance (technical, political, resource-based)",
                "Find common ground and areas of agreement",
                "Engage their trusted allies to build support",
                "Provide evidence-based responses to objections",
                "Escalate to executive sponsor if resistance persists"
            ]
        else:
            strategy["recommended_actions"] = [
                "Understand their specific concerns via informal conversation",
                "Address concerns through transparency and information sharing",
                "Involve them in relevant discussions to build ownership",
                "Monitor for changes in power or influence",
                "Prevent them from influencing high-power stakeholders negatively"
            ]

        strategies.append(strategy)

    return strategies


# ---------------------------------------------------------------------------
# Output Formatting - Text
# ---------------------------------------------------------------------------

def format_text_output(analysis: Dict[str, Any], comm_plan: Dict[str, Any],
                       blocker_strategies: List[Dict[str, Any]]) -> str:
    """Format the full analysis as human-readable text."""
    lines: List[str] = []
    summary = analysis["summary"]

    lines.append("=" * 64)
    lines.append("STAKEHOLDER MAPPING & COMMUNICATION PLAN")
    lines.append("=" * 64)
    lines.append("")

    # --- Summary ---
    lines.append(f"Project: {summary['project']}")
    lines.append(f"Analysis Date: {summary['analysis_date']}")
    lines.append(f"Total Stakeholders: {summary['total_stakeholders']}")
    lines.append(f"Average Power: {summary['average_power']:.1f} / 10")
    lines.append(f"Average Interest: {summary['average_interest']:.1f} / 10")
    lines.append("")

    # --- Attitude Breakdown ---
    att = summary["attitude_counts"]
    lines.append("ATTITUDE BREAKDOWN")
    lines.append("-" * 30)
    lines.append(f"  Supporters: {att['supporter']}")
    lines.append(f"  Neutral:    {att['neutral']}")
    lines.append(f"  Blockers:   {att['blocker']}")
    lines.append("")

    # --- Power/Interest Grid ---
    lines.append("POWER / INTEREST GRID (Mendelow's Matrix)")
    lines.append("-" * 50)
    lines.append("")
    lines.append("  Power")
    lines.append("  HIGH  | Keep Satisfied      | Manage Closely      |")
    lines.append("        | ({ks})               | ({mc})               |".format(
        ks=summary["quadrant_counts"]["keep_satisfied"],
        mc=summary["quadrant_counts"]["manage_closely"]
    ))
    lines.append("  ------+---------------------+---------------------+")
    lines.append("  LOW   | Monitor             | Keep Informed       |")
    lines.append("        | ({mo})               | ({ki})               |".format(
        mo=summary["quadrant_counts"]["monitor"],
        ki=summary["quadrant_counts"]["keep_informed"]
    ))
    lines.append("        +---------------------+---------------------+")
    lines.append("               LOW                   HIGH")
    lines.append("                       Interest")
    lines.append("")

    # --- Quadrant Details ---
    quadrant_groups = analysis["quadrant_groups"]
    for quadrant_key in ["manage_closely", "keep_satisfied", "keep_informed", "monitor"]:
        config = QUADRANTS[quadrant_key]
        members = quadrant_groups[quadrant_key]
        lines.append(f"{config['label'].upper()} ({len(members)} stakeholders)")
        lines.append("-" * 40)
        lines.append(f"  {config['description']}")
        lines.append("")

        if members:
            for s in members:
                attitude_flag = ""
                if s.attitude == "blocker":
                    attitude_flag = " [BLOCKER]"
                elif s.attitude == "supporter":
                    attitude_flag = " [SUPPORTER]"
                inf_str = f", Influence: {s.influence}" if s.influence is not None else ""
                lines.append(
                    f"  - {s.name} ({s.role}) "
                    f"| Power: {s.power}, Interest: {s.interest}{inf_str}{attitude_flag}"
                )
        else:
            lines.append("  (none)")
        lines.append("")

    # --- Communication Plan ---
    lines.append("=" * 64)
    lines.append("COMMUNICATION PLAN")
    lines.append("=" * 64)
    lines.append("")

    for quadrant_key in ["manage_closely", "keep_satisfied", "keep_informed", "monitor"]:
        plan = comm_plan[quadrant_key]
        lines.append(f"{plan['label'].upper()} (Frequency: {plan['frequency']})")
        lines.append("-" * 40)
        lines.append(f"  Channel:     {plan['channel']}")
        lines.append(f"  Key Message: {plan['key_message']}")
        lines.append(f"  Stakeholders: {', '.join(plan['stakeholders']) if plan['stakeholders'] else '(none)'}")
        lines.append("  Tactics:")
        for tactic in plan["tactics"]:
            lines.append(f"    - {tactic}")
        lines.append("")

    # --- Blocker Strategies ---
    if blocker_strategies:
        lines.append("=" * 64)
        lines.append("BLOCKER ENGAGEMENT STRATEGIES")
        lines.append("=" * 64)
        lines.append("")
        for bs in blocker_strategies:
            lines.append(f"{bs['name']} ({bs['role']}) - Risk: {bs['risk_level']}")
            lines.append(f"  Quadrant: {bs['quadrant']} | Power: {bs['power']}, Interest: {bs['interest']}")
            lines.append("  Recommended Actions:")
            for action in bs["recommended_actions"]:
                lines.append(f"    - {action}")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output Formatting - JSON
# ---------------------------------------------------------------------------

def format_json_output(analysis: Dict[str, Any], comm_plan: Dict[str, Any],
                       blocker_strategies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Format the full analysis as a JSON-serializable dictionary."""
    # Serialize stakeholders per quadrant
    quadrant_details = {}
    for quadrant_key, members in analysis["quadrant_groups"].items():
        quadrant_details[quadrant_key] = {
            "label": QUADRANTS[quadrant_key]["label"],
            "stakeholders": [s.to_dict() for s in members]
        }

    return {
        "summary": analysis["summary"],
        "quadrants": quadrant_details,
        "communication_plan": comm_plan,
        "blocker_strategies": blocker_strategies,
        "all_stakeholders": [s.to_dict() for s in analysis["all_stakeholders"]]
    }


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------

def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=(
            "Stakeholder Mapper - Classify stakeholders by power/interest "
            "into Mendelow's Matrix and generate a communication plan."
        )
    )
    parser.add_argument(
        "data_file",
        nargs="?",
        default=None,
        help="JSON file with stakeholders array (see --demo for sample format)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with built-in sample data to demonstrate output"
    )

    args = parser.parse_args()

    # Determine data source
    if args.demo:
        data = DEMO_DATA
    elif args.data_file:
        try:
            with open(args.data_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File '{args.data_file}' not found", file=sys.stderr)
            return 1
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{args.data_file}': {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        print("\nError: Provide a JSON file or use --demo for sample output", file=sys.stderr)
        return 1

    try:
        # Run analysis
        analysis = classify_stakeholders(data)
        comm_plan = build_communication_plan(analysis)
        blocker_strategies = build_blocker_strategy(analysis["blockers"])

        # Output results
        if args.format == "json":
            output = format_json_output(analysis, comm_plan, blocker_strategies)
            print(json.dumps(output, indent=2))
        else:
            output = format_text_output(analysis, comm_plan, blocker_strategies)
            print(output)

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
