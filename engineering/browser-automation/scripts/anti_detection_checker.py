#!/usr/bin/env python3
"""
Automation Risk Checker - audit an automation script before it runs against a site.

Flags patterns that overload a site, break its rules or hide what the script is (spoofed
browser identity, webdriver or fingerprint masking, IP rotation), and protections that are
missing (rate limiting, robots.txt, backoff, an identifying User-Agent). The advice is for
permitted automation: identify the bot honestly and stay inside the site's rules.

The risk score counts both the signatures found and the protections that are
missing, so a bare script with no delays, retries or robots.txt check cannot
score as low risk. Use it on automation you are authorized to run.

Exit codes: 0 risk score below 50, 1 risk score 50 or more, 2 unreadable input.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional


@dataclass
class DetectionSignature:
    """A detected bot detection signature."""
    category: str
    severity: str  # critical, high, medium, low
    title: str
    description: str
    line_number: int
    code_snippet: str
    fix_suggestion: str


@dataclass
class CheckResult:
    """Overall check result."""
    file_path: str
    total_signatures: int = 0
    risk_score: int = 0  # 0-100
    signatures: List[DetectionSignature] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    missing_protections: List[str] = field(default_factory=list)


SEVERITY_WEIGHTS = {"critical": 25, "high": 15, "medium": 8, "low": 3}

# (pattern, category, severity, title, description, fix)
DETECTION_PATTERNS = [
    (r'navigator\.webdriver\s*=\s*false',
     "concealment", "high",
     "Webdriver flag masked",
     "The script hides that it is automated. Sites use this flag to apply their automation policy.",
     "Remove the override. If the site does not allow automation, ask for access or use its API."),

    (r'(?:headless|headless_mode)\s*[:=]\s*(?:True|true|1)',
     "policy", "low",
     "Headless browser",
     "Fine for permitted automation; some sites block headless browsers as a matter of policy.",
     "If the site blocks it, treat that as its answer: request access or an API rather than masking it."),

    (r'(?:sleep|wait|delay)\s*\(\s*(\d+(?:\.\d+)?)\s*\)',
     "timing", "medium",
     "Fixed delay",
     "A constant delay gives no back-pressure: the script keeps the same pace when the server slows.",
     "Use a rate limiter with jitter and back off on 429/503 (honour Retry-After)."),

    (r'time\.sleep\s*\(\s*(?:0\.\d|0\.0)',
     "timing", "high",
     "Sub-second delay between requests",
     "Requests this close together can overload small sites.",
     "Wait at least 1-3 seconds between requests to a site you do not run, longer if it is slow."),

    (r'["\'](?:User-Agent|user-agent)["\']\s*:\s*["\']Mozilla/',
     "identity", "medium",
     "User-Agent impersonates a browser",
     "The script presents itself as a person's browser, so the site owner cannot tell who is crawling.",
     "Use an identifying User-Agent: 'MyCrawler/1.0 (+https://example.com/bot; ops@example.com)'."),

    (r'\.get\s*\(\s*["\']https?://',
     "request", "low",
     "Request without a session or headers",
     "Bare requests skip connection reuse and send no identification.",
     "Use one session with an identifying User-Agent, timeouts and retry with backoff."),

    (r'(?:cookies|cookie_jar)\s*[:=]\s*(?:\{\}|\[\]|None)',
     "session", "low",
     "Empty cookie jar on every run",
     "Starting a new session each run repeats logins and redirects and adds load.",
     "Reuse the session within a run; persist cookies only where the site's terms allow."),

    (r'(?:proxy|PROXY)\s*[:=]\s*["\'](?:http|socks)',
     "concealment", "medium",
     "Proxy configured",
     "Fine for your own network needs. Rotating IPs to get past a site's rate limits or blocks is evasion.",
     "Do not rotate proxies to dodge limits; slow down or ask the site for higher limits or an API."),

    (r'(?:execute_cdp_cmd|execute_script)\s*\(["\'].*(?:Object\.defineProperty|delete\s+)',
     "concealment", "high",
     "Browser fingerprint spoofing",
     "Rewriting browser properties to avoid detection breaks most sites' terms.",
     "Remove it. Permitted automation does not need to look like a person."),

    (r'\.(?:click|send_keys|submit)\s*\([^)]*\)\s*$',
     "reliability", "low",
     "Action without explicit wait or error handling",
     "Actions without waits fail on slow pages and retry loops then hammer the site.",
     "Use explicit waits before interactions and bounded retries."),
]

# Protections that SHOULD be present, with the risk each one's absence adds
EXPECTED_PROTECTIONS = [
    (r'(?:random|randint|uniform|randrange)', "Randomized timing/delays", 8),
    (r'(?:User-Agent|USER_AGENT|user.agent).*(?:bot|crawler|spider|\+https?://|mailto:|@)', "Identifying User-Agent (bot name + contact)", 8),
    (r'(?:requests\.Session|session\s*=|\.Session\()', "Reused HTTP session", 3),
    (r'(?:retry|backoff|exponential)', "Retry/backoff logic", 8),
    (r'(?:robots\.txt|robotparser)', "robots.txt compliance", 15),
    (r'(?:rate.limit|throttle|semaphore)', "Rate limiting", 15),
]


def check_file(file_path: Path) -> CheckResult:
    """Analyze a file for detection signatures."""
    result = CheckResult(file_path=str(file_path))

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        print(f"Error: cannot read {file_path}: {e}", file=sys.stderr)
        sys.exit(2)

    lines = content.split("\n")

    # Check for detection signatures
    for pattern_str, category, severity, title, desc, fix in DETECTION_PATTERNS:
        try:
            pattern = re.compile(pattern_str, re.IGNORECASE)
        except re.error:
            continue

        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                result.signatures.append(DetectionSignature(
                    category=category,
                    severity=severity,
                    title=title,
                    description=desc,
                    line_number=i,
                    code_snippet=line.strip()[:120],
                    fix_suggestion=fix,
                ))

    result.total_signatures = len(result.signatures)

    # Risk = signatures found + protections missing
    risk = sum(SEVERITY_WEIGHTS.get(sig.severity, 0) for sig in result.signatures)
    for pattern_str, protection_name, weight in EXPECTED_PROTECTIONS:
        if not re.search(pattern_str, content, re.IGNORECASE):
            result.missing_protections.append(protection_name)
            risk += weight
    result.risk_score = min(100, risk)

    # Generate recommendations
    if result.risk_score >= 75:
        result.recommendations.append("HIGH RISK: likely to be blocked or to overload the target. Rework before running.")
    elif result.risk_score >= 40:
        result.recommendations.append("MODERATE RISK: fix critical/high signatures and add the missing protections first.")
    elif result.risk_score > 0:
        result.recommendations.append("LOW RISK: minor issues; review the items below.")
    else:
        result.recommendations.append("MINIMAL RISK: no signatures found and all protections present.")

    if result.missing_protections:
        result.recommendations.append(f"Missing protections: {', '.join(result.missing_protections)}")

    return result


def format_human(result: CheckResult) -> str:
    """Format results for human reading."""
    lines = []
    lines.append("=" * 65)
    lines.append("AUTOMATION RISK REPORT")
    lines.append("=" * 65)
    lines.append(f"File: {result.file_path}")
    lines.append(f"Risky patterns found: {result.total_signatures}")
    lines.append(f"Risk Score: {result.risk_score}/100")
    lines.append("")

    if result.recommendations:
        lines.append("Assessment:")
        for rec in result.recommendations:
            lines.append(f"  > {rec}")
        lines.append("")

    if result.missing_protections:
        lines.append("Missing Protections:")
        for mp in result.missing_protections:
            lines.append(f"  [ ] {mp}")
        lines.append("")

    for i, sig in enumerate(result.signatures, 1):
        lines.append("-" * 50)
        lines.append(f"[{i}] [{sig.severity.upper()}] {sig.title}")
        lines.append(f"    Category: {sig.category}")
        lines.append(f"    Line: {sig.line_number}")
        lines.append(f"    Code: {sig.code_snippet}")
        lines.append(f"    Issue: {sig.description}")
        lines.append(f"    Fix: {sig.fix_suggestion}")
        lines.append("")

    lines.append("=" * 65)
    return "\n".join(lines)


def format_json(result: CheckResult) -> str:
    """Format results as JSON."""
    data = {
        "file_path": result.file_path,
        "total_signatures": result.total_signatures,
        "risk_score": result.risk_score,
        "signatures": [asdict(s) for s in result.signatures],
        "missing_protections": result.missing_protections,
        "recommendations": result.recommendations,
    }
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Automation Risk Checker - audit an automation script for overload, concealment and missing protections"
    )
    parser.add_argument("--file", required=True, help="Path to automation script to check")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    args = parser.parse_args()
    path = Path(args.file)

    if not path.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    result = check_file(path)

    if args.format == "json":
        print(format_json(result))
    else:
        print(format_human(result))

    sys.exit(1 if result.risk_score >= 50 else 0)


if __name__ == "__main__":
    main()
