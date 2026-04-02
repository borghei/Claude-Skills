#!/usr/bin/env python3
"""
Audit Log Analyzer - Analyze vault audit logs for suspicious access patterns.

Parses Vault audit log files (JSON format) and detects anomalies including
off-hours access, bulk reads, failed auth attempts, and privilege escalation.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple


@dataclass
class AuditEvent:
    """Parsed audit log event."""
    timestamp: str
    event_type: str  # request, response
    operation: str   # read, create, update, delete, list
    path: str
    client_token: str
    accessor: str
    remote_address: str
    error: Optional[str] = None
    auth_type: Optional[str] = None
    policies: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Alert:
    """A security alert."""
    severity: str  # critical, high, medium, low
    category: str
    title: str
    description: str
    evidence: List[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class AnalysisReport:
    """Full analysis report."""
    log_file: str
    total_events: int
    time_range: str
    alerts: List[Alert] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)


def parse_vault_log_line(line: str) -> Optional[AuditEvent]:
    """Parse a single Vault audit log line (JSON format)."""
    line = line.strip()
    if not line:
        return None

    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None

    event_type = data.get("type", "")
    request = data.get("request", {})
    auth = data.get("auth", {})
    error_msg = data.get("error", "")

    return AuditEvent(
        timestamp=data.get("time", ""),
        event_type=event_type,
        operation=request.get("operation", ""),
        path=request.get("path", ""),
        client_token=auth.get("client_token", "")[:8] + "..." if auth.get("client_token") else "",
        accessor=auth.get("accessor", ""),
        remote_address=request.get("remote_address", ""),
        error=error_msg if error_msg else None,
        auth_type=auth.get("token_type", ""),
        policies=auth.get("policies", []),
        metadata=auth.get("metadata", {}),
    )


def parse_log_file(path: Path) -> List[AuditEvent]:
    """Parse entire log file."""
    events = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError) as e:
        print(f"Error reading log file: {e}", file=sys.stderr)
        return events

    for line in content.split("\n"):
        event = parse_vault_log_line(line)
        if event:
            events.append(event)

    return events


def detect_off_hours_access(events: List[AuditEvent]) -> List[Alert]:
    """Detect access outside business hours (6am-10pm local)."""
    alerts = []
    off_hours_events = []

    for e in events:
        try:
            ts = datetime.fromisoformat(e.timestamp.replace("Z", "+00:00").replace("+00:00", ""))
            if ts.hour < 6 or ts.hour >= 22:
                off_hours_events.append(e)
        except (ValueError, AttributeError):
            continue

    if len(off_hours_events) > 5:
        ips = Counter(e.remote_address for e in off_hours_events)
        top_ips = ips.most_common(3)
        alerts.append(Alert(
            severity="medium",
            category="off-hours",
            title=f"Off-hours access detected ({len(off_hours_events)} events)",
            description=f"{len(off_hours_events)} vault accesses occurred outside business hours (10pm-6am).",
            evidence=[f"IP {ip}: {count} events" for ip, count in top_ips],
            recommendation="Review off-hours access. If automated, verify the service accounts. If manual, investigate.",
        ))

    return alerts


def detect_bulk_reads(events: List[AuditEvent], threshold: int = 50) -> List[Alert]:
    """Detect bulk secret reads (potential exfiltration)."""
    alerts = []

    # Group reads by IP in 5-minute windows
    ip_windows: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for e in events:
        if e.operation in ("read", "list"):
            try:
                ts = datetime.fromisoformat(e.timestamp.replace("Z", "+00:00").replace("+00:00", ""))
                window = ts.strftime("%Y-%m-%d %H:%M")[:-1] + "0"  # 10-min window
                ip_windows[e.remote_address][window] += 1
            except (ValueError, AttributeError):
                continue

    for ip, windows in ip_windows.items():
        for window, count in windows.items():
            if count >= threshold:
                alerts.append(Alert(
                    severity="high",
                    category="bulk-read",
                    title=f"Bulk read detected from {ip}",
                    description=f"{count} read/list operations from {ip} in 10-minute window at {window}.",
                    evidence=[f"Window: {window}", f"Operations: {count}", f"IP: {ip}"],
                    recommendation="Investigate potential data exfiltration. Check if this is an authorized batch operation.",
                ))

    return alerts


def detect_failed_auth(events: List[AuditEvent], threshold: int = 10) -> List[Alert]:
    """Detect repeated authentication failures (brute force)."""
    alerts = []
    failed_by_ip: Dict[str, int] = Counter()

    for e in events:
        if e.error and ("permission denied" in e.error.lower() or
                        "invalid" in e.error.lower() or
                        "denied" in e.error.lower()):
            failed_by_ip[e.remote_address] += 1

    for ip, count in failed_by_ip.items():
        if count >= threshold:
            severity = "critical" if count >= 50 else "high"
            alerts.append(Alert(
                severity=severity,
                category="failed-auth",
                title=f"Repeated auth failures from {ip} ({count} attempts)",
                description=f"{count} failed authentication/authorization attempts detected from {ip}.",
                evidence=[f"IP: {ip}", f"Failed attempts: {count}"],
                recommendation="Potential brute force attack. Consider blocking this IP and investigating the source.",
            ))

    return alerts


def detect_root_token_usage(events: List[AuditEvent]) -> List[Alert]:
    """Detect root token usage in non-emergency situations."""
    alerts = []
    root_events = [e for e in events if "root" in e.policies]

    if root_events:
        paths = Counter(e.path for e in root_events)
        alerts.append(Alert(
            severity="high",
            category="root-token",
            title=f"Root token usage detected ({len(root_events)} events)",
            description="Root token was used for vault operations. This should only occur during emergency maintenance.",
            evidence=[f"Path: {p} ({c}x)" for p, c in paths.most_common(5)],
            recommendation="Root tokens should be revoked after initial setup. Investigate if this usage was authorized.",
        ))

    return alerts


def detect_unusual_paths(events: List[AuditEvent]) -> List[Alert]:
    """Detect access to sensitive or unusual paths."""
    alerts = []
    sensitive_patterns = [
        (r'sys/seal', "critical", "Seal/unseal operations"),
        (r'sys/policies', "high", "Policy modifications"),
        (r'sys/auth', "high", "Auth method changes"),
        (r'sys/mounts', "high", "Secrets engine mount changes"),
        (r'sys/audit', "high", "Audit configuration changes"),
        (r'sys/rekey', "critical", "Rekey operations"),
        (r'sys/rotate', "high", "Key rotation"),
        (r'identity/', "medium", "Identity management"),
    ]

    for pattern, severity, desc in sensitive_patterns:
        matching = [e for e in events if re.search(pattern, e.path)]
        if matching:
            ips = Counter(e.remote_address for e in matching)
            alerts.append(Alert(
                severity=severity,
                category="sensitive-path",
                title=f"{desc} detected ({len(matching)} events)",
                description=f"Access to sensitive path pattern '{pattern}' was detected.",
                evidence=[
                    f"Events: {len(matching)}",
                    *[f"IP {ip}: {c}x" for ip, c in ips.most_common(3)],
                ],
                recommendation=f"Verify that {desc.lower()} were authorized and expected.",
            ))

    return alerts


def compute_stats(events: List[AuditEvent]) -> Dict:
    """Compute summary statistics."""
    if not events:
        return {"total": 0}

    ops = Counter(e.operation for e in events)
    ips = Counter(e.remote_address for e in events)
    paths = Counter(e.path for e in events)
    errors = sum(1 for e in events if e.error)

    timestamps = []
    for e in events:
        try:
            timestamps.append(datetime.fromisoformat(e.timestamp.replace("Z", "+00:00").replace("+00:00", "")))
        except (ValueError, AttributeError):
            pass

    time_range = ""
    if timestamps:
        earliest = min(timestamps)
        latest = max(timestamps)
        time_range = f"{earliest.isoformat()} to {latest.isoformat()}"

    return {
        "total_events": len(events),
        "time_range": time_range,
        "operations": dict(ops.most_common()),
        "top_ips": dict(ips.most_common(10)),
        "top_paths": dict(paths.most_common(10)),
        "error_count": errors,
        "error_rate_pct": round(errors / len(events) * 100, 1) if events else 0,
        "unique_ips": len(ips),
        "unique_paths": len(paths),
    }


def analyze_logs(events: List[AuditEvent], log_file: str) -> AnalysisReport:
    """Run all analysis checks."""
    stats = compute_stats(events)

    all_alerts = []
    all_alerts.extend(detect_failed_auth(events))
    all_alerts.extend(detect_bulk_reads(events))
    all_alerts.extend(detect_root_token_usage(events))
    all_alerts.extend(detect_off_hours_access(events))
    all_alerts.extend(detect_unusual_paths(events))

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_alerts.sort(key=lambda a: severity_order.get(a.severity, 4))

    return AnalysisReport(
        log_file=log_file,
        total_events=len(events),
        time_range=stats.get("time_range", "unknown"),
        alerts=all_alerts,
        stats=stats,
    )


def format_human(report: AnalysisReport) -> str:
    """Format for human reading."""
    lines = []
    lines.append("=" * 65)
    lines.append("VAULT AUDIT LOG ANALYSIS")
    lines.append("=" * 65)
    lines.append(f"Log file: {report.log_file}")
    lines.append(f"Total events: {report.total_events}")
    lines.append(f"Time range: {report.time_range}")
    lines.append(f"Alerts: {len(report.alerts)}")
    lines.append("")

    if report.stats:
        lines.append("Statistics:")
        lines.append(f"  Unique IPs: {report.stats.get('unique_ips', 0)}")
        lines.append(f"  Unique paths: {report.stats.get('unique_paths', 0)}")
        lines.append(f"  Error rate: {report.stats.get('error_rate_pct', 0)}%")
        if report.stats.get("operations"):
            lines.append(f"  Operations: {report.stats['operations']}")
        lines.append("")

    if not report.alerts:
        lines.append("No security alerts detected.")
    else:
        lines.append("Security Alerts:")
        lines.append("-" * 55)
        for i, alert in enumerate(report.alerts, 1):
            lines.append(f"\n[{i}] [{alert.severity.upper()}] {alert.title}")
            lines.append(f"    Category: {alert.category}")
            lines.append(f"    {alert.description}")
            if alert.evidence:
                lines.append("    Evidence:")
                for ev in alert.evidence:
                    lines.append(f"      - {ev}")
            lines.append(f"    Recommendation: {alert.recommendation}")

    lines.append("\n" + "=" * 65)
    return "\n".join(lines)


def format_json(report: AnalysisReport) -> str:
    """Format as JSON."""
    data = {
        "log_file": report.log_file,
        "total_events": report.total_events,
        "time_range": report.time_range,
        "alert_count": len(report.alerts),
        "alerts_by_severity": {},
        "alerts": [asdict(a) for a in report.alerts],
        "stats": report.stats,
    }
    for a in report.alerts:
        data["alerts_by_severity"][a.severity] = data["alerts_by_severity"].get(a.severity, 0) + 1
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Audit Log Analyzer - Analyze vault audit logs for suspicious access"
    )
    parser.add_argument("--log-file", required=True, help="Path to vault audit log file (JSON format)")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")
    parser.add_argument("--bulk-threshold", type=int, default=50,
                        help="Threshold for bulk read detection (default: 50)")
    parser.add_argument("--auth-threshold", type=int, default=10,
                        help="Threshold for failed auth detection (default: 10)")

    args = parser.parse_args()
    path = Path(args.log_file)

    if not path.exists():
        print(f"Error: File not found: {args.log_file}", file=sys.stderr)
        sys.exit(1)

    events = parse_log_file(path)

    if not events:
        print("Warning: No audit events parsed from log file.", file=sys.stderr)

    report = analyze_logs(events, args.log_file)

    if args.format == "json":
        print(format_json(report))
    else:
        print(format_human(report))

    critical_alerts = sum(1 for a in report.alerts if a.severity == "critical")
    sys.exit(2 if critical_alerts > 0 else (1 if report.alerts else 0))


if __name__ == "__main__":
    main()
