#!/usr/bin/env python3
"""
Sprint Capacity Calculator

Calculates sprint capacity from team data, accounting for ceremony overhead,
PTO, allocation percentages, and focus factor. Supports historical velocity
for story point estimation and provides both JSON and human-readable output.

Usage:
    python sprint_capacity_calculator.py team_data.json
    python sprint_capacity_calculator.py team_data.json --format json
    python sprint_capacity_calculator.py --demo
    python sprint_capacity_calculator.py --demo --format json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Constants and Configuration
# ---------------------------------------------------------------------------

DEFAULT_HOURS_PER_DAY: float = 6.0  # Productive hours per day
DEFAULT_ALLOCATION_PERCENT: float = 100.0
DEFAULT_SPRINT_LENGTH_DAYS: int = 10  # 2-week sprint

FOCUS_FACTOR_RANGE: Dict[str, float] = {
    "optimistic": 0.85,
    "realistic": 0.80,
}

# Ceremony durations in hours (for the entire sprint)
CEREMONY_DEFAULTS: Dict[str, Any] = {
    "sprint_planning_hours": 2.0,
    "daily_standup_minutes": 15,  # Per day
    "sprint_review_hours": 1.0,
    "sprint_retro_hours": 1.0,
    "backlog_refinement_hours": 1.0,
}

DEMO_DATA: Dict[str, Any] = {
    "sprint_length_days": 10,
    "historical_velocity": 42,
    "team_members": [
        {
            "name": "Alice Chen",
            "role": "Senior Developer",
            "available_days": 10,
            "hours_per_day": 6,
            "allocation_percent": 100,
            "planned_pto_days": 0,
        },
        {
            "name": "Bob Martinez",
            "role": "Developer",
            "available_days": 10,
            "hours_per_day": 6,
            "allocation_percent": 100,
            "planned_pto_days": 2,
        },
        {
            "name": "Carol Johnson",
            "role": "Developer",
            "available_days": 10,
            "hours_per_day": 6,
            "allocation_percent": 80,
            "planned_pto_days": 0,
        },
        {
            "name": "David Kim",
            "role": "QA Engineer",
            "available_days": 10,
            "hours_per_day": 6,
            "allocation_percent": 100,
            "planned_pto_days": 1,
        },
        {
            "name": "Eva Patel",
            "role": "Tech Lead",
            "available_days": 10,
            "hours_per_day": 6,
            "allocation_percent": 50,
            "planned_pto_days": 0,
        },
    ],
}


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

class TeamMember:
    """Represents a single team member's capacity data."""

    def __init__(self, data: Dict[str, Any]):
        self.name: str = data.get("name", "Unknown")
        self.role: str = data.get("role", "Developer")
        self.available_days: int = data.get("available_days", DEFAULT_SPRINT_LENGTH_DAYS)
        self.hours_per_day: float = data.get("hours_per_day", DEFAULT_HOURS_PER_DAY)
        self.allocation_percent: float = data.get("allocation_percent", DEFAULT_ALLOCATION_PERCENT)
        self.planned_pto_days: int = data.get("planned_pto_days", 0)
        self.ceremonies_hours_override: Optional[float] = data.get("ceremonies_hours", None)


class CapacityResult:
    """Complete capacity calculation results."""

    def __init__(self):
        self.team_size: int = 0
        self.sprint_length_days: int = DEFAULT_SPRINT_LENGTH_DAYS
        self.member_breakdown: List[Dict[str, Any]] = []
        self.ceremony_overhead: Dict[str, Any] = {}
        self.total_gross_hours: float = 0.0
        self.total_ceremony_hours: float = 0.0
        self.total_net_hours: float = 0.0
        self.focus_adjusted_hours: Dict[str, float] = {}
        self.estimated_story_points: Optional[Dict[str, Any]] = None
        self.warnings: List[str] = []


# ---------------------------------------------------------------------------
# Core Calculation Functions
# ---------------------------------------------------------------------------

def calculate_ceremony_overhead(sprint_length_days: int) -> Dict[str, Any]:
    """Calculate total ceremony overhead for the sprint."""
    daily_standup_total = (
        CEREMONY_DEFAULTS["daily_standup_minutes"] * sprint_length_days / 60.0
    )
    planning = CEREMONY_DEFAULTS["sprint_planning_hours"]
    review = CEREMONY_DEFAULTS["sprint_review_hours"]
    retro = CEREMONY_DEFAULTS["sprint_retro_hours"]
    refinement = CEREMONY_DEFAULTS["backlog_refinement_hours"]

    total = daily_standup_total + planning + review + retro + refinement

    return {
        "sprint_planning": planning,
        "daily_standups": round(daily_standup_total, 2),
        "sprint_review": review,
        "sprint_retro": retro,
        "backlog_refinement": refinement,
        "total_per_member": round(total, 2),
    }


def calculate_member_capacity(
    member: TeamMember,
    ceremony_hours: float,
) -> Dict[str, Any]:
    """Calculate capacity for a single team member."""
    working_days = member.available_days - member.planned_pto_days
    if working_days < 0:
        working_days = 0

    gross_hours = working_days * member.hours_per_day * (member.allocation_percent / 100.0)

    if member.ceremonies_hours_override is not None:
        member_ceremony_hours = member.ceremonies_hours_override
    else:
        # Scale ceremony hours by allocation (partially allocated members attend fewer ceremonies)
        member_ceremony_hours = ceremony_hours * (member.allocation_percent / 100.0)

    net_hours = gross_hours - member_ceremony_hours
    if net_hours < 0:
        net_hours = 0.0

    return {
        "name": member.name,
        "role": member.role,
        "available_days": member.available_days,
        "pto_days": member.planned_pto_days,
        "working_days": working_days,
        "allocation_percent": member.allocation_percent,
        "gross_hours": round(gross_hours, 2),
        "ceremony_hours": round(member_ceremony_hours, 2),
        "net_hours": round(net_hours, 2),
    }


def calculate_capacity(data: Dict[str, Any]) -> CapacityResult:
    """Perform full sprint capacity calculation."""
    result = CapacityResult()

    sprint_length_days = data.get("sprint_length_days", DEFAULT_SPRINT_LENGTH_DAYS)
    result.sprint_length_days = sprint_length_days
    historical_velocity = data.get("historical_velocity", None)

    team_members_data = data.get("team_members", [])
    if not team_members_data:
        result.warnings.append("No team members provided.")
        return result

    members = [TeamMember(m) for m in team_members_data]
    result.team_size = len(members)

    # Calculate ceremony overhead
    ceremony_info = calculate_ceremony_overhead(sprint_length_days)
    result.ceremony_overhead = ceremony_info
    ceremony_hours_per_member = ceremony_info["total_per_member"]

    # Calculate per-member capacity
    total_gross = 0.0
    total_ceremony = 0.0
    total_net = 0.0

    for member in members:
        breakdown = calculate_member_capacity(member, ceremony_hours_per_member)
        result.member_breakdown.append(breakdown)
        total_gross += breakdown["gross_hours"]
        total_ceremony += breakdown["ceremony_hours"]
        total_net += breakdown["net_hours"]

    result.total_gross_hours = round(total_gross, 2)
    result.total_ceremony_hours = round(total_ceremony, 2)
    result.total_net_hours = round(total_net, 2)

    # Apply focus factor
    result.focus_adjusted_hours = {
        "optimistic_85pct": round(total_net * FOCUS_FACTOR_RANGE["optimistic"], 2),
        "realistic_80pct": round(total_net * FOCUS_FACTOR_RANGE["realistic"], 2),
    }

    # Estimate story points if historical velocity is provided
    if historical_velocity is not None and historical_velocity > 0:
        # Historical velocity is points per sprint at some capacity level
        # We use the realistic focus-adjusted hours as the baseline
        realistic_hours = result.focus_adjusted_hours["realistic_80pct"]
        optimistic_hours = result.focus_adjusted_hours["optimistic_85pct"]

        result.estimated_story_points = {
            "historical_velocity": historical_velocity,
            "note": "Story point estimates based on historical velocity ratio",
            "realistic_estimate": historical_velocity,
            "optimistic_estimate": round(
                historical_velocity * (optimistic_hours / max(realistic_hours, 1)), 1
            ),
            "conservative_estimate": round(historical_velocity * 0.85, 1),
        }

    # Generate warnings
    for breakdown in result.member_breakdown:
        if breakdown["pto_days"] > breakdown["available_days"] * 0.5:
            result.warnings.append(
                f"{breakdown['name']} has PTO for >{50}% of the sprint "
                f"({breakdown['pto_days']}/{breakdown['available_days']} days)."
            )
        if breakdown["allocation_percent"] < 50:
            result.warnings.append(
                f"{breakdown['name']} is allocated at only "
                f"{breakdown['allocation_percent']}%. Consider team focus."
            )

    return result


# ---------------------------------------------------------------------------
# Output Formatting
# ---------------------------------------------------------------------------

def format_text_output(result: CapacityResult) -> str:
    """Format capacity results as readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("SPRINT CAPACITY CALCULATION REPORT")
    lines.append("=" * 60)
    lines.append("")

    if not result.member_breakdown:
        lines.append("No team data available.")
        return "\n".join(lines)

    # Sprint info
    lines.append("SPRINT CONFIGURATION")
    lines.append("-" * 30)
    lines.append(f"Sprint Length: {result.sprint_length_days} days")
    lines.append(f"Team Size: {result.team_size} members")
    lines.append("")

    # Ceremony overhead
    lines.append("CEREMONY OVERHEAD (per member)")
    lines.append("-" * 30)
    ceremony = result.ceremony_overhead
    lines.append(f"Sprint Planning:      {ceremony['sprint_planning']:.1f}h")
    lines.append(f"Daily Standups:       {ceremony['daily_standups']:.1f}h")
    lines.append(f"Sprint Review:        {ceremony['sprint_review']:.1f}h")
    lines.append(f"Sprint Retrospective: {ceremony['sprint_retro']:.1f}h")
    lines.append(f"Backlog Refinement:   {ceremony['backlog_refinement']:.1f}h")
    lines.append(f"Total Per Member:     {ceremony['total_per_member']:.1f}h")
    lines.append("")

    # Team member breakdown
    lines.append("TEAM MEMBER CAPACITY")
    lines.append("-" * 30)
    header = f"{'Name':<20} {'Role':<18} {'Days':<6} {'PTO':<5} {'Alloc%':<7} {'Gross':<7} {'Cere.':<7} {'Net':<7}"
    lines.append(header)
    lines.append("-" * len(header))

    for m in result.member_breakdown:
        lines.append(
            f"{m['name']:<20} {m['role']:<18} {m['working_days']:<6} "
            f"{m['pto_days']:<5} {m['allocation_percent']:<7.0f} "
            f"{m['gross_hours']:<7.1f} {m['ceremony_hours']:<7.1f} {m['net_hours']:<7.1f}"
        )

    lines.append("")

    # Totals
    lines.append("CAPACITY SUMMARY")
    lines.append("-" * 30)
    lines.append(f"Total Gross Hours:         {result.total_gross_hours:.1f}h")
    lines.append(f"Total Ceremony Overhead:   {result.total_ceremony_hours:.1f}h")
    lines.append(f"Total Net Hours:           {result.total_net_hours:.1f}h")
    lines.append("")
    lines.append("Focus-Adjusted Capacity:")
    lines.append(f"  Optimistic (85%):        {result.focus_adjusted_hours['optimistic_85pct']:.1f}h")
    lines.append(f"  Realistic  (80%):        {result.focus_adjusted_hours['realistic_80pct']:.1f}h")
    lines.append("")

    # Story point estimates
    if result.estimated_story_points:
        sp = result.estimated_story_points
        lines.append("STORY POINT ESTIMATE")
        lines.append("-" * 30)
        lines.append(f"Historical Velocity:       {sp['historical_velocity']} points/sprint")
        lines.append(f"Conservative Estimate:     {sp['conservative_estimate']:.0f} points")
        lines.append(f"Realistic Estimate:        {sp['realistic_estimate']} points")
        lines.append(f"Optimistic Estimate:       {sp['optimistic_estimate']:.0f} points")
        lines.append("")

    # Warnings
    if result.warnings:
        lines.append("WARNINGS")
        lines.append("-" * 30)
        for i, warning in enumerate(result.warnings, 1):
            lines.append(f"{i}. {warning}")
        lines.append("")

    return "\n".join(lines)


def format_json_output(result: CapacityResult) -> Dict[str, Any]:
    """Format capacity results as JSON."""
    output = {
        "sprint_configuration": {
            "sprint_length_days": result.sprint_length_days,
            "team_size": result.team_size,
        },
        "ceremony_overhead": result.ceremony_overhead,
        "member_breakdown": result.member_breakdown,
        "capacity_summary": {
            "total_gross_hours": result.total_gross_hours,
            "total_ceremony_hours": result.total_ceremony_hours,
            "total_net_hours": result.total_net_hours,
            "focus_adjusted_hours": result.focus_adjusted_hours,
        },
        "estimated_story_points": result.estimated_story_points,
        "warnings": result.warnings,
    }
    return output


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------

def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate sprint capacity from team data with ceremony overhead and focus factor"
    )
    parser.add_argument(
        "data_file",
        nargs="?",
        help="JSON file containing team capacity data",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with sample demo data",
    )

    args = parser.parse_args()

    if not args.demo and not args.data_file:
        parser.error("Either provide a data_file or use --demo")

    try:
        if args.demo:
            data = DEMO_DATA
        else:
            with open(args.data_file, "r") as f:
                data = json.load(f)

        # Perform calculation
        result = calculate_capacity(data)

        # Output results
        if args.format == "json":
            output = format_json_output(result)
            print(json.dumps(output, indent=2))
        else:
            output = format_text_output(result)
            print(output)

        return 0

    except FileNotFoundError:
        print(f"Error: File '{args.data_file}' not found", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.data_file}': {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
