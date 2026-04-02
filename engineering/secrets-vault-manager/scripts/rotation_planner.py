#!/usr/bin/env python3
"""
Rotation Planner - Plan and schedule secret rotation cycles.

Reads a secrets inventory and generates rotation schedules based on
classification, compliance requirements, and organizational policy.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


@dataclass
class SecretEntry:
    """A secret in the inventory."""
    name: str
    classification: str  # critical, high, medium, low
    secret_type: str  # database, api-key, certificate, token, encryption-key, ssh-key, password
    owner: str
    last_rotated: str  # ISO date
    auto_rotation: bool = False
    compliance_tags: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class RotationSchedule:
    """Planned rotation for a secret."""
    name: str
    classification: str
    secret_type: str
    owner: str
    last_rotated: str
    next_rotation: str
    days_until_rotation: int
    overdue: bool
    rotation_frequency_days: int
    auto_rotation: bool
    priority: str  # urgent, upcoming, scheduled, ok
    action_required: str
    compliance_tags: List[str] = field(default_factory=list)


# Default rotation frequencies by classification (days)
DEFAULT_FREQUENCIES = {
    "critical": 30,
    "high": 60,
    "medium": 90,
    "low": 180,
}

# Override frequencies by secret type
TYPE_OVERRIDES = {
    "certificate": {"critical": 90, "high": 180, "medium": 365, "low": 365},
    "encryption-key": {"critical": 90, "high": 180, "medium": 365, "low": 365},
    "token": {"critical": 7, "high": 30, "medium": 60, "low": 90},
    "ssh-key": {"critical": 30, "high": 60, "medium": 90, "low": 180},
}

# Compliance-specific requirements
COMPLIANCE_FREQUENCIES = {
    "pci-dss": 90,    # PCI-DSS requires credential rotation at least quarterly
    "hipaa": 90,      # HIPAA recommends quarterly
    "soc2": 90,       # SOC 2 quarterly typical
    "nist": 60,       # NIST recommends 60 days for privileged
    "gdpr": 180,      # GDPR no specific requirement, 6 months recommended
}


def get_rotation_frequency(entry: SecretEntry, policy: Optional[Dict] = None) -> int:
    """Determine rotation frequency for a secret."""
    # Start with default based on classification
    freq = DEFAULT_FREQUENCIES.get(entry.classification, 90)

    # Apply type overrides
    if entry.secret_type in TYPE_OVERRIDES:
        type_freq = TYPE_OVERRIDES[entry.secret_type].get(entry.classification)
        if type_freq:
            freq = type_freq

    # Apply compliance requirements (use strictest)
    for tag in entry.compliance_tags:
        compliance_freq = COMPLIANCE_FREQUENCIES.get(tag.lower())
        if compliance_freq:
            freq = min(freq, compliance_freq)

    # Apply custom policy overrides
    if policy:
        custom = policy.get(entry.classification) or policy.get(entry.secret_type)
        if custom:
            freq = min(freq, int(custom))

    return freq


def create_schedule(entry: SecretEntry, policy: Optional[Dict] = None) -> RotationSchedule:
    """Create a rotation schedule for a secret."""
    freq = get_rotation_frequency(entry, policy)
    now = datetime.now()

    try:
        last = datetime.fromisoformat(entry.last_rotated.replace("Z", "+00:00").replace("+00:00", ""))
    except (ValueError, AttributeError):
        # If date can't be parsed, assume never rotated
        last = now - timedelta(days=freq * 2)

    next_rotation = last + timedelta(days=freq)
    days_until = (next_rotation - now).days

    overdue = days_until < 0

    if overdue:
        priority = "urgent"
        action = f"OVERDUE by {abs(days_until)} days. Rotate immediately."
    elif days_until <= 7:
        priority = "upcoming"
        action = f"Due in {days_until} days. Schedule rotation now."
    elif days_until <= 30:
        priority = "scheduled"
        action = f"Due in {days_until} days. Plan rotation."
    else:
        priority = "ok"
        action = f"Next rotation in {days_until} days."

    if entry.auto_rotation:
        action += " (auto-rotation enabled)"

    return RotationSchedule(
        name=entry.name,
        classification=entry.classification,
        secret_type=entry.secret_type,
        owner=entry.owner,
        last_rotated=entry.last_rotated,
        next_rotation=next_rotation.strftime("%Y-%m-%d"),
        days_until_rotation=days_until,
        overdue=overdue,
        rotation_frequency_days=freq,
        auto_rotation=entry.auto_rotation,
        priority=priority,
        action_required=action,
        compliance_tags=entry.compliance_tags,
    )


def load_inventory(path: Path) -> List[SecretEntry]:
    """Load secrets inventory from JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = []
    for item in data.get("secrets", data if isinstance(data, list) else []):
        entries.append(SecretEntry(
            name=item["name"],
            classification=item.get("classification", "medium"),
            secret_type=item.get("secret_type", item.get("type", "password")),
            owner=item.get("owner", "unknown"),
            last_rotated=item.get("last_rotated", "2025-01-01"),
            auto_rotation=item.get("auto_rotation", False),
            compliance_tags=item.get("compliance_tags", []),
            description=item.get("description", ""),
        ))
    return entries


def generate_sample_inventory() -> str:
    """Generate a sample inventory file."""
    sample = {
        "secrets": [
            {
                "name": "prod-database-root",
                "classification": "critical",
                "secret_type": "database",
                "owner": "dba-team",
                "last_rotated": "2026-02-15",
                "auto_rotation": False,
                "compliance_tags": ["soc2", "pci-dss"],
                "description": "Production database root credentials"
            },
            {
                "name": "api-gateway-key",
                "classification": "high",
                "secret_type": "api-key",
                "owner": "platform-team",
                "last_rotated": "2026-03-01",
                "auto_rotation": True,
                "compliance_tags": ["soc2"],
                "description": "API gateway master key"
            },
            {
                "name": "stripe-api-key",
                "classification": "high",
                "secret_type": "api-key",
                "owner": "payments-team",
                "last_rotated": "2026-01-10",
                "auto_rotation": False,
                "compliance_tags": ["pci-dss"],
                "description": "Stripe payment processing API key"
            },
            {
                "name": "tls-wildcard-cert",
                "classification": "high",
                "secret_type": "certificate",
                "owner": "infra-team",
                "last_rotated": "2025-12-01",
                "auto_rotation": True,
                "compliance_tags": [],
                "description": "Wildcard TLS certificate for *.example.com"
            },
            {
                "name": "ci-deploy-token",
                "classification": "medium",
                "secret_type": "token",
                "owner": "devops-team",
                "last_rotated": "2026-03-15",
                "auto_rotation": False,
                "compliance_tags": [],
                "description": "CI/CD deployment token"
            }
        ]
    }
    return json.dumps(sample, indent=2)


def format_human(schedules: List[RotationSchedule]) -> str:
    """Format rotation plan for human reading."""
    lines = []
    lines.append("=" * 70)
    lines.append("SECRET ROTATION PLAN")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    # Summary
    urgent = [s for s in schedules if s.priority == "urgent"]
    upcoming = [s for s in schedules if s.priority == "upcoming"]
    scheduled = [s for s in schedules if s.priority == "scheduled"]

    lines.append(f"\nTotal secrets: {len(schedules)}")
    lines.append(f"  URGENT (overdue): {len(urgent)}")
    lines.append(f"  UPCOMING (< 7 days): {len(upcoming)}")
    lines.append(f"  SCHEDULED (< 30 days): {len(scheduled)}")
    lines.append(f"  OK: {len(schedules) - len(urgent) - len(upcoming) - len(scheduled)}")
    lines.append("")

    # Sort: urgent first, then by days until rotation
    sorted_schedules = sorted(schedules, key=lambda s: (
        {"urgent": 0, "upcoming": 1, "scheduled": 2, "ok": 3}[s.priority],
        s.days_until_rotation
    ))

    for s in sorted_schedules:
        marker = "!!!" if s.priority == "urgent" else "! " if s.priority == "upcoming" else "  "
        auto = " [AUTO]" if s.auto_rotation else ""
        lines.append(f"{marker} {s.name}{auto}")
        lines.append(f"     Classification: {s.classification} | Type: {s.secret_type} | Owner: {s.owner}")
        lines.append(f"     Last rotated: {s.last_rotated} | Next: {s.next_rotation} | Frequency: {s.rotation_frequency_days}d")
        lines.append(f"     Action: {s.action_required}")
        if s.compliance_tags:
            lines.append(f"     Compliance: {', '.join(s.compliance_tags)}")
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def format_json(schedules: List[RotationSchedule]) -> str:
    """Format as JSON."""
    data = {
        "generated": datetime.now().isoformat(),
        "total": len(schedules),
        "summary": {
            "urgent": sum(1 for s in schedules if s.priority == "urgent"),
            "upcoming": sum(1 for s in schedules if s.priority == "upcoming"),
            "scheduled": sum(1 for s in schedules if s.priority == "scheduled"),
            "ok": sum(1 for s in schedules if s.priority == "ok"),
        },
        "schedules": [asdict(s) for s in schedules],
    }
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Rotation Planner - Plan and schedule secret rotation cycles"
    )
    parser.add_argument("--inventory", help="Path to secrets inventory JSON file")
    parser.add_argument("--generate-sample", action="store_true",
                        help="Generate a sample inventory file")
    parser.add_argument("--policy", help="Path to custom rotation policy JSON")
    parser.add_argument("--filter-priority", choices=["urgent", "upcoming", "scheduled", "ok"],
                        help="Show only secrets with this priority")
    parser.add_argument("--filter-owner", help="Show only secrets owned by this team")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    args = parser.parse_args()

    if args.generate_sample:
        print(generate_sample_inventory())
        return

    if not args.inventory:
        print("Error: --inventory required (or use --generate-sample)", file=sys.stderr)
        sys.exit(1)

    inv_path = Path(args.inventory)
    if not inv_path.exists():
        print(f"Error: File not found: {args.inventory}", file=sys.stderr)
        sys.exit(1)

    entries = load_inventory(inv_path)

    policy = None
    if args.policy:
        policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))

    schedules = [create_schedule(e, policy) for e in entries]

    if args.filter_priority:
        schedules = [s for s in schedules if s.priority == args.filter_priority]

    if args.filter_owner:
        schedules = [s for s in schedules if s.owner == args.filter_owner]

    if args.format == "json":
        print(format_json(schedules))
    else:
        print(format_human(schedules))

    # Exit with code based on urgent items
    urgent_count = sum(1 for s in schedules if s.priority == "urgent")
    sys.exit(1 if urgent_count > 0 else 0)


if __name__ == "__main__":
    main()
