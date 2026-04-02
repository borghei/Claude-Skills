#!/usr/bin/env python3
"""
Anti-Detection Checker - Audit browser automation scripts for bot detection signatures.

Analyzes automation code for patterns that trigger bot detection systems including
fingerprinting tells, timing issues, and missing evasion techniques.

Author: Claude Skills Engineering Team
License: MIT
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
    # Webdriver detection
    (r'navigator\.webdriver\s*=\s*false',
     "fingerprint", "high",
     "Naive webdriver override",
     "Setting navigator.webdriver=false is easily detected by advanced bot systems that check the property descriptor.",
     "Use CDP commands to remove webdriver property before page load, or use undetected-chromedriver."),

    (r'(?:headless|headless_mode)\s*[:=]\s*(?:True|true|1)',
     "fingerprint", "critical",
     "Headless mode enabled without evasion",
     "Running in headless mode without anti-fingerprinting is the most common detection trigger.",
     "Use --headless=new (Chrome 112+) or apply comprehensive anti-fingerprinting patches."),

    # Fixed timing
    (r'(?:sleep|wait|delay)\s*\(\s*(\d+(?:\.\d+)?)\s*\)',
     "timing", "medium",
     "Fixed delay detected",
     "Constant delays create predictable timing patterns that bot detectors recognize.",
     "Use randomized delays: random.uniform(min_delay, max_delay)."),

    (r'time\.sleep\s*\(\s*(?:0\.\d|0\.0)',
     "timing", "high",
     "Very short fixed delay",
     "Sub-second fixed delays are a strong bot indicator.",
     "Use randomized delays of at least 1-3 seconds between actions."),

    # User-Agent issues
    (r'["\'](?:User-Agent|user-agent)["\']\s*:\s*["\'][^"\']+["\']',
     "headers", "medium",
     "Hardcoded User-Agent string",
     "A single hardcoded User-Agent is easily fingerprinted and blocked.",
     "Rotate User-Agent strings from a realistic pool matching the browser being automated."),

    (r'(?:HeadlessChrome|PhantomJS|Selenium|puppeteer)',
     "fingerprint", "critical",
     "Bot identifier in User-Agent or code",
     "Bot-identifying strings in the User-Agent or runtime environment are trivially detected.",
     "Remove all bot-identifying strings. Use realistic User-Agent rotation."),

    # Missing protections
    (r'\.get\s*\(\s*["\']https?://',
     "request", "low",
     "HTTP request without explicit headers",
     "Requests without custom headers may use default library headers that identify automation.",
     "Set realistic Accept, Accept-Language, Accept-Encoding, and Connection headers."),

    # Cookie handling
    (r'(?:cookies|cookie_jar)\s*[:=]\s*(?:\{\}|\[\]|None)',
     "session", "medium",
     "Empty cookie initialization",
     "Starting with empty cookies on a site you've 'visited' before is suspicious.",
     "Persist and reuse cookies across sessions. Pre-load common cookies."),

    # Viewport/resolution
    (r'(?:window_size|viewport|set_window_size)\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)',
     "fingerprint", "low",
     "Fixed viewport size",
     "Using a fixed viewport without variation can be a fingerprinting signal.",
     "Randomize viewport dimensions slightly around common resolutions."),

    # Proxy patterns
    (r'(?:proxy|PROXY)\s*[:=]\s*["\'](?:http|socks)',
     "network", "low",
     "Single proxy configuration",
     "Using a single proxy IP is easily blocked. Detected as automation if IP is in known ranges.",
     "Use rotating residential proxies or a proxy pool with automatic rotation."),

    # Selenium-specific
    (r'(?:execute_cdp_cmd|execute_script)\s*\(["\'].*(?:Object\.defineProperty|delete\s+)',
     "fingerprint", "medium",
     "JavaScript property manipulation for evasion",
     "Manual JS property overrides can be detected by checking property descriptors and prototype chains.",
     "Use comprehensive stealth plugins (e.g., selenium-stealth, puppeteer-extra-plugin-stealth)."),

    # No error handling
    (r'\.(?:click|send_keys|submit)\s*\([^)]*\)\s*$',
     "reliability", "low",
     "Action without explicit wait or error handling",
     "Actions without waits may fail on slow pages, causing detectable error patterns.",
     "Use explicit waits (WebDriverWait) before interactions. Add try/except for retries."),

    # Referrer issues
    (r'(?:Referer|referrer)\s*[:=]\s*(?:None|""|\'\')',
     "headers", "medium",
     "Missing or empty Referer header",
     "Navigation without a Referer header is suspicious for internal page transitions.",
     "Set appropriate Referer headers matching natural navigation flow."),
]

# Protections that SHOULD be present
EXPECTED_PROTECTIONS = [
    (r'(?:random|randint|uniform|randrange)', "Randomized timing/delays"),
    (r'(?:User-Agent|user.agent).*(?:random|choice|rotate|pool|list)', "User-Agent rotation"),
    (r'(?:cookie|session).*(?:save|persist|load|store)', "Cookie persistence"),
    (r'(?:retry|backoff|exponential)', "Retry/backoff logic"),
    (r'(?:robots\.txt|robotparser)', "robots.txt compliance"),
    (r'(?:rate.limit|throttle|semaphore)', "Rate limiting"),
]


def check_file(file_path: Path) -> CheckResult:
    """Analyze a file for detection signatures."""
    result = CheckResult(file_path=str(file_path))

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError) as e:
        result.recommendations.append(f"Could not read file: {e}")
        return result

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

    # Calculate risk score
    risk = 0
    for sig in result.signatures:
        risk += SEVERITY_WEIGHTS.get(sig.severity, 0)
    result.risk_score = min(100, risk)

    # Check for missing protections
    for pattern_str, protection_name in EXPECTED_PROTECTIONS:
        if not re.search(pattern_str, content, re.IGNORECASE):
            result.missing_protections.append(protection_name)

    # Generate recommendations
    if result.risk_score >= 75:
        result.recommendations.append("HIGH RISK: This script is very likely to be detected. Major refactoring needed.")
    elif result.risk_score >= 40:
        result.recommendations.append("MODERATE RISK: Several detection signatures found. Address high/critical items first.")
    elif result.risk_score > 0:
        result.recommendations.append("LOW RISK: Minor signatures found. Script is reasonably stealthy.")
    else:
        result.recommendations.append("MINIMAL RISK: No obvious detection signatures found.")

    if result.missing_protections:
        result.recommendations.append(f"Missing protections: {', '.join(result.missing_protections)}")

    return result


def format_human(result: CheckResult) -> str:
    """Format results for human reading."""
    lines = []
    lines.append("=" * 65)
    lines.append("ANTI-DETECTION CHECK REPORT")
    lines.append("=" * 65)
    lines.append(f"File: {result.file_path}")
    lines.append(f"Detection Signatures Found: {result.total_signatures}")
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
        description="Anti-Detection Checker - Audit browser automation scripts for bot detection signatures"
    )
    parser.add_argument("--file", required=True, help="Path to automation script to check")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    args = parser.parse_args()
    path = Path(args.file)

    if not path.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = check_file(path)

    if args.format == "json":
        print(format_json(result))
    else:
        print(format_human(result))

    sys.exit(1 if result.risk_score >= 50 else 0)


if __name__ == "__main__":
    main()
