#!/usr/bin/env python3
"""
Threat Signal Analyzer - Analyze log files for suspicious activity patterns.

Detects brute force attempts, injection attacks, path traversals,
unusual access patterns, and other threat indicators. Lines are URL-decoded
(twice, to catch double encoding) before matching; evidence keeps the raw line.

Counts are per file, not per time window: slice long logs by time before running.
Exit codes: 0 no critical signal, 1 at least one critical signal, 2 bad input.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import unquote_plus
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple


@dataclass
class ThreatSignal:
    """A detected threat signal."""
    severity: str  # critical, high, medium, low
    category: str
    source_ip: Optional[str]
    timestamp: Optional[str]
    message: str
    evidence: str
    recommendation: str


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# Injection patterns
SQL_INJECTION_PATTERNS = [
    re.compile(r"(?i)(?:union\s+(?:all\s+)?select)", re.IGNORECASE),
    re.compile(r"(?i)(?:or\s+1\s*=\s*1)", re.IGNORECASE),
    re.compile(r"(?i)(?:and\s+1\s*=\s*1)", re.IGNORECASE),
    # Quoted tautology: ' OR '1'='1  /  " or "a"="a
    re.compile(r"""['"]\s*(?:or|and)\s+['"]?(\w+)['"]?\s*=\s*['"]?\1\b""", re.IGNORECASE),
    re.compile(r"(?i)(?:drop\s+table)", re.IGNORECASE),
    re.compile(r"(?i)(?:insert\s+into)", re.IGNORECASE),
    re.compile(r"(?i)(?:delete\s+from)", re.IGNORECASE),
    re.compile(r"(?i)(?:update\s+\w+\s+set)", re.IGNORECASE),
    re.compile(r"(?i)(?:exec\s*\(|execute\s)", re.IGNORECASE),
    # Comment used to cut off the rest of a query, right after a closing quote
    re.compile(r"""['"]\s*(?:--|#|/\*)"""),
    re.compile(r"(?i)(?:sleep\s*\(\s*\d+\s*\))", re.IGNORECASE),
    re.compile(r"(?i)(?:benchmark\s*\()", re.IGNORECASE),
    re.compile(r"(?i)(?:waitfor\s+delay)", re.IGNORECASE),
]

XSS_PATTERNS = [
    re.compile(r"<script[\s>]", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"on(?:load|error|click|mouseover)\s*=", re.IGNORECASE),
    re.compile(r"<iframe[\s>]", re.IGNORECASE),
    re.compile(r"<img[^>]+onerror", re.IGNORECASE),
    re.compile(r"eval\s*\(", re.IGNORECASE),
    re.compile(r"document\.(?:cookie|location|write)", re.IGNORECASE),
]

CMD_INJECTION_PATTERNS = [
    re.compile(r";\s*(?:cat|ls|id|whoami|pwd|uname)\b"),
    re.compile(r"\|\s*(?:nc|ncat|netcat)\b"),
    re.compile(r"`[^`]+`"),
    re.compile(r"\$\([^)]+\)"),
    re.compile(r";\s*(?:curl|wget)\s"),
    re.compile(r"(?:rm\s+-rf|mkfs|dd\s+if=)"),
]

PATH_TRAVERSAL_PATTERNS = [
    re.compile(r"\.\./"),
    re.compile(r"\.\.\\"),
    re.compile(r"%2e%2e[/\\]", re.IGNORECASE),
    re.compile(r"%252e%252e", re.IGNORECASE),
    # Direct requests for well-known sensitive files (file disclosure, not command injection)
    re.compile(r"/etc/(?:passwd|shadow|hosts)|/proc/self/environ|win\.ini", re.IGNORECASE),
]

ADMIN_PROBE_PATHS = [
    "/admin", "/wp-admin", "/wp-login", "/phpmyadmin", "/administrator",
    "/manager", "/console", "/.env", "/config", "/backup",
    "/api/admin", "/debug", "/server-status", "/server-info",
    "/.git", "/.svn", "/wp-config.php", "/xmlrpc.php",
]

# Log parsing patterns
IP_PATTERN = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
TIMESTAMP_PATTERNS = [
    re.compile(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})'),
    re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})'),
    re.compile(r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'),
]
HTTP_STATUS_PATTERN = re.compile(r'\s(\d{3})(?:\s|$)')
AUTH_FAIL_PATTERNS = [
    re.compile(r'(?i)(?:failed|invalid|rejected)\s+(?:login|password|authentication)'),
    re.compile(r'(?i)authentication\s+failure'),
    re.compile(r'(?i)access\s+denied'),
    re.compile(r'(?i)unauthorized'),
    re.compile(r'(?i)invalid\s+user'),
    re.compile(r'(?i)failed\s+password'),
]


class ThreatAnalyzer:
    """Analyzes log entries for threat signals."""

    def __init__(self, min_severity: str = "low", category: Optional[str] = None):
        self.signals: List[ThreatSignal] = []
        self.min_severity = min_severity
        self.category = category
        self.failed_logins: Dict[str, List[str]] = defaultdict(list)
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.ip_status_codes: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))

    def analyze_file(self, filepath: Path) -> List[ThreatSignal]:
        """Analyze a log file for threats."""
        try:
            lines = filepath.read_text(errors="replace").split("\n")
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return []

        for line in lines:
            if not line.strip():
                continue
            self._analyze_line(line)

        # Post-analysis aggregation checks
        self._check_brute_force()
        self._check_rate_flooding()

        return self._filter_by_severity()

    def _extract_ip(self, line: str) -> Optional[str]:
        """Extract IP address from log line."""
        match = IP_PATTERN.search(line)
        return match.group(1) if match else None

    def _extract_timestamp(self, line: str) -> Optional[str]:
        """Extract timestamp from log line."""
        for pattern in TIMESTAMP_PATTERNS:
            match = pattern.search(line)
            if match:
                return match.group(1)
        return None

    def _analyze_line(self, line: str):
        """Analyze a single log line."""
        ip = self._extract_ip(line)
        ts = self._extract_timestamp(line)

        if ip:
            self.request_counts[ip] += 1

        # Track HTTP status codes
        status_match = HTTP_STATUS_PATTERN.search(line)
        if status_match and ip:
            code = int(status_match.group(1))
            self.ip_status_codes[ip][code] += 1

        # Match on the decoded request so %27%20OR%20... is seen as ' OR ...
        raw = line
        decoded = unquote_plus(unquote_plus(line))

        # Check categories
        if not self.category or self.category == "injection":
            self._check_sql_injection(decoded, ip, ts, raw)
            self._check_xss(decoded, ip, ts, raw)
            self._check_command_injection(decoded, ip, ts, raw)

        if not self.category or self.category == "traversal":
            # Encoded forms (%2e%2e) are matched on the raw line; plain ../ on the decoded one
            self._check_path_traversal(line + "\n" + decoded, ip, ts, raw)

        if not self.category or self.category == "auth":
            self._check_auth_failures(line, ip, ts)

        if not self.category or self.category == "probe":
            self._check_admin_probing(line, ip, ts)

    def _check_sql_injection(self, line: str, ip: Optional[str], ts: Optional[str], raw: Optional[str] = None):
        """Check for SQL injection patterns."""
        for pattern in SQL_INJECTION_PATTERNS:
            if pattern.search(line):
                self.signals.append(ThreatSignal(
                    severity="critical",
                    category="sql_injection",
                    source_ip=ip,
                    timestamp=ts,
                    message="SQL injection attempt detected.",
                    evidence=(raw or line).strip()[:200],
                    recommendation="Block source IP. Review application input validation. Check for successful exploitation.",
                ))
                return  # One finding per line

    def _check_xss(self, line: str, ip: Optional[str], ts: Optional[str], raw: Optional[str] = None):
        """Check for XSS patterns."""
        for pattern in XSS_PATTERNS:
            if pattern.search(line):
                self.signals.append(ThreatSignal(
                    severity="high",
                    category="xss",
                    source_ip=ip,
                    timestamp=ts,
                    message="Cross-site scripting (XSS) attempt detected.",
                    evidence=(raw or line).strip()[:200],
                    recommendation="Block source IP. Review output encoding. Check for stored XSS.",
                ))
                return

    def _check_command_injection(self, line: str, ip: Optional[str], ts: Optional[str], raw: Optional[str] = None):
        """Check for command injection patterns."""
        for pattern in CMD_INJECTION_PATTERNS:
            if pattern.search(line):
                self.signals.append(ThreatSignal(
                    severity="critical",
                    category="command_injection",
                    source_ip=ip,
                    timestamp=ts,
                    message="Command injection attempt detected.",
                    evidence=(raw or line).strip()[:200],
                    recommendation="Block source IP immediately. Audit command execution paths. Check for successful exploitation.",
                ))
                return

    def _check_path_traversal(self, line: str, ip: Optional[str], ts: Optional[str], raw: Optional[str] = None):
        """Check for path traversal attempts."""
        for pattern in PATH_TRAVERSAL_PATTERNS:
            if pattern.search(line):
                self.signals.append(ThreatSignal(
                    severity="high",
                    category="path_traversal",
                    source_ip=ip,
                    timestamp=ts,
                    message="Path traversal attempt detected.",
                    evidence=(raw or line).strip()[:200],
                    recommendation="Block source IP. Validate file path inputs. Ensure no sensitive files were accessed.",
                ))
                return

    def _check_auth_failures(self, line: str, ip: Optional[str], ts: Optional[str]):
        """Track authentication failures for brute force detection."""
        for pattern in AUTH_FAIL_PATTERNS:
            if pattern.search(line):
                if ip:
                    self.failed_logins[ip].append(ts or "unknown")
                break

    def _check_admin_probing(self, line: str, ip: Optional[str], ts: Optional[str]):
        """Check for admin page probing."""
        line_lower = line.lower()
        for probe_path in ADMIN_PROBE_PATHS:
            if probe_path in line_lower:
                # Only flag if we see 404 or 403 (probing, not legitimate)
                status_match = HTTP_STATUS_PATTERN.search(line)
                if status_match:
                    code = int(status_match.group(1))
                    if code in (401, 403, 404):
                        self.signals.append(ThreatSignal(
                            severity="medium",
                            category="admin_probe",
                            source_ip=ip,
                            timestamp=ts,
                            message=f"Admin/sensitive path probe detected: {probe_path}",
                            evidence=line.strip()[:200],
                            recommendation="Monitor source IP for further reconnaissance. Consider rate limiting.",
                        ))
                        return

    def _check_brute_force(self):
        """Detect brute force patterns from aggregated auth failures."""
        if self.category and self.category != "auth":
            return

        for ip, timestamps in self.failed_logins.items():
            if len(timestamps) >= 5:
                self.signals.append(ThreatSignal(
                    severity="high",
                    category="brute_force",
                    source_ip=ip,
                    timestamp=timestamps[0],
                    message=f"Brute force attack: {len(timestamps)} failed login attempts from {ip}.",
                    evidence=f"Failed attempts: {len(timestamps)}, First: {timestamps[0]}, Last: {timestamps[-1]}",
                    recommendation=f"Block IP {ip}. Enforce account lockout. Check if any attempts succeeded.",
                ))
            elif len(timestamps) >= 3:
                self.signals.append(ThreatSignal(
                    severity="medium",
                    category="brute_force",
                    source_ip=ip,
                    timestamp=timestamps[0],
                    message=f"Possible brute force: {len(timestamps)} failed login attempts from {ip}.",
                    evidence=f"Failed attempts: {len(timestamps)}",
                    recommendation=f"Monitor IP {ip} for continued attempts.",
                ))

    def _check_rate_flooding(self):
        """Detect request flooding."""
        if self.category and self.category != "rate":
            return

        for ip, count in self.request_counts.items():
            if count > 500:
                self.signals.append(ThreatSignal(
                    severity="high",
                    category="rate_flooding",
                    source_ip=ip,
                    timestamp=None,
                    message=f"Request flooding: {count} requests from {ip}.",
                    evidence=f"Total requests: {count}",
                    recommendation=f"Rate limit or block IP {ip}. Check if this is a legitimate bot or attack.",
                ))
            elif count > 200:
                self.signals.append(ThreatSignal(
                    severity="medium",
                    category="rate_flooding",
                    source_ip=ip,
                    timestamp=None,
                    message=f"High request volume: {count} requests from {ip}.",
                    evidence=f"Total requests: {count}",
                    recommendation=f"Monitor IP {ip}. Consider rate limiting.",
                ))

    def _filter_by_severity(self) -> List[ThreatSignal]:
        """Filter by minimum severity."""
        min_order = SEVERITY_ORDER.get(self.min_severity, 3)
        return [s for s in self.signals if SEVERITY_ORDER.get(s.severity, 3) <= min_order]


def format_text(signals: List[ThreatSignal], filepath: str) -> str:
    """Format as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("THREAT SIGNAL ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append(f"Log file: {filepath}")
    lines.append(f"Signals detected: {len(signals)}")

    by_severity = {}
    for s in signals:
        by_severity.setdefault(s.severity, []).append(s)

    for sev in ["critical", "high", "medium", "low"]:
        count = len(by_severity.get(sev, []))
        if count:
            lines.append(f"  {sev.upper()}: {count}")

    lines.append("-" * 60)

    for sev in ["critical", "high", "medium", "low"]:
        group = by_severity.get(sev, [])
        if not group:
            continue
        lines.append(f"\n[{sev.upper()}]")
        for s in group:
            ip_str = f" from {s.source_ip}" if s.source_ip else ""
            ts_str = f" at {s.timestamp}" if s.timestamp else ""
            lines.append(f"  [{s.category}]{ip_str}{ts_str}")
            lines.append(f"    {s.message}")
            lines.append(f"    Evidence: {s.evidence[:120]}")
            lines.append(f"    Action: {s.recommendation}")
            lines.append("")

    if not signals:
        lines.append("\nNo threat signals detected.")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_json(signals: List[ThreatSignal], filepath: str) -> str:
    """Format as JSON."""
    return json.dumps({
        "file": filepath,
        "signals": [asdict(s) for s in signals],
        "summary": {
            "total": len(signals),
            "critical": sum(1 for s in signals if s.severity == "critical"),
            "high": sum(1 for s in signals if s.severity == "high"),
            "medium": sum(1 for s in signals if s.severity == "medium"),
            "low": sum(1 for s in signals if s.severity == "low"),
            "categories": dict(Counter(s.category for s in signals)),
        }
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze log files for suspicious activity and threat signals."
    )
    parser.add_argument("--file", "-f", required=True, help="Path to log file")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--min-severity", choices=["critical", "high", "medium", "low"],
                       default="low", help="Minimum severity to report")
    parser.add_argument("--category", choices=["injection", "auth", "traversal", "probe", "rate"],
                       help="Focus on specific threat category")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(2)
    try:
        path.read_text(errors="replace")
    except OSError as exc:
        print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
        sys.exit(2)

    analyzer = ThreatAnalyzer(min_severity=args.min_severity, category=args.category)
    signals = analyzer.analyze_file(path)

    if args.format == "json":
        print(format_json(signals, str(path)))
    else:
        print(format_text(signals, str(path)))

    if any(s.severity == "critical" for s in signals):
        sys.exit(1)


if __name__ == "__main__":
    main()
