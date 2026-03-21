#!/usr/bin/env python3
"""
Prompt Injection Scanner - Detect prompt injection in markdown and text files.

Scans .md, .txt, and .yaml/.yml files for patterns that indicate prompt
injection attempts: system prompt overrides, role hijacking, safety bypasses,
data extraction instructions, hidden zero-width characters, and suspicious
HTML comments containing directives.

Respects fenced code blocks (triple backticks) and skips content inside them
to reduce false positives from documentation examples.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Tuple


@dataclass
class Finding:
    severity: str
    category: str
    file: str
    line: int
    matched_text: str
    risk: str
    fix: str


@dataclass
class ScanReport:
    target: str
    files_scanned: int
    total_findings: int
    critical_count: int
    high_count: int
    info_count: int
    verdict: str
    strict_mode: bool
    findings: List[Dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pattern definitions
# ---------------------------------------------------------------------------

CRITICAL_PATTERNS: Dict[str, List[Dict[str, str]]] = {
    "SYSTEM-OVERRIDE": [
        {
            "regex": r"ignore\s+(all\s+)?previous\s+instructions",
            "risk": "Attempts to override the AI system prompt and prior instructions",
            "fix": "Remove this phrase entirely; legitimate skills never override system prompts",
        },
        {
            "regex": r"ignore\s+(all\s+)?prior\s+instructions",
            "risk": "Attempts to override the AI system prompt and prior instructions",
            "fix": "Remove this phrase entirely; legitimate skills never override system prompts",
        },
        {
            "regex": r"disregard\s+(all\s+)?(previous|prior|above)",
            "risk": "Attempts to make the AI disregard its existing instructions",
            "fix": "Remove this directive; skills should work within existing instructions",
        },
        {
            "regex": r"new\s+system\s+prompt",
            "risk": "Attempts to inject a replacement system prompt",
            "fix": "Remove system prompt override; use standard skill documentation format",
        },
        {
            "regex": r"override\s+(the\s+)?system\s+(prompt|instructions)",
            "risk": "Explicit attempt to override system-level instructions",
            "fix": "Remove system override language; skills extend behavior, not replace it",
        },
    ],
    "ROLE-HIJACK": [
        {
            "regex": r"act\s+as\s+(root|admin|administrator|superuser)",
            "risk": "Attempts to escalate the AI to a privileged role",
            "fix": "Remove privileged role assignment; define skill scope without role escalation",
        },
        {
            "regex": r"pretend\s+you\s+(have\s+no|don'?t\s+have)\s+restrictions",
            "risk": "Attempts to remove the AI's safety restrictions",
            "fix": "Remove restriction-bypass language; work within standard safety boundaries",
        },
        {
            "regex": r"you\s+have\s+no\s+limitations",
            "risk": "Declares the AI has no limitations to bypass safety measures",
            "fix": "Remove this assertion; document realistic capabilities instead",
        },
        {
            "regex": r"unrestricted\s+mode",
            "risk": "Attempts to enable an unrestricted execution mode",
            "fix": "Remove 'unrestricted mode' language; define explicit, scoped permissions",
        },
        {
            "regex": r"developer\s+mode\s+enabled",
            "risk": "Attempts to activate a fake developer mode to bypass safety",
            "fix": "Remove 'developer mode' activation; this is a known jailbreak technique",
        },
        {
            "regex": r"\bjailbreak\b",
            "risk": "References jailbreaking, a technique to bypass AI safety measures",
            "fix": "Remove jailbreak references; legitimate skills do not mention jailbreaking",
        },
    ],
    "DATA-EXTRACT": [
        {
            "regex": r"send\s+(the\s+)?contents?\s+(of|from)\s+",
            "risk": "Instructs the AI to send file contents to an external destination",
            "fix": "Remove data exfiltration instructions; skills should process data locally",
        },
        {
            "regex": r"upload\s+(the\s+)?file\s+to\s+",
            "risk": "Instructs the AI to upload files to an external service",
            "fix": "Remove file upload instructions; skills should not exfiltrate data",
        },
        {
            "regex": r"POST\s+to\s+https?://",
            "risk": "Instructs the AI to send an HTTP POST to an external URL",
            "fix": "Remove HTTP POST instructions targeting external URLs",
        },
        {
            "regex": r"\bexfiltrate\b",
            "risk": "Explicit mention of data exfiltration",
            "fix": "Remove exfiltration language; this indicates malicious intent",
        },
        {
            "regex": r"transmit\s+(all\s+)?data\s+to\s+",
            "risk": "Instructs the AI to transmit data to an external destination",
            "fix": "Remove data transmission instructions targeting external services",
        },
    ],
}

HIGH_PATTERNS: Dict[str, List[Dict[str, str]]] = {
    "SAFETY-BYPASS": [
        {
            "regex": r"skip\s+(all\s+)?safety\s+checks?",
            "risk": "Instructs the AI to skip safety validation checks",
            "fix": "Remove safety-bypass instructions; skills must respect safety checks",
        },
        {
            "regex": r"disable\s+(the\s+)?content\s+filter",
            "risk": "Attempts to disable content filtering mechanisms",
            "fix": "Remove content filter bypass; skills work within content policies",
        },
        {
            "regex": r"bypass\s+(the\s+)?security",
            "risk": "Instructs the AI to bypass security mechanisms",
            "fix": "Remove security bypass language; document legitimate permissions needed",
        },
        {
            "regex": r"remove\s+(all\s+)?guardrails",
            "risk": "Attempts to remove AI safety guardrails",
            "fix": "Remove guardrail-bypass language; work within existing guardrails",
        },
        {
            "regex": r"no\s+restrictions?\s+appl(y|ies)",
            "risk": "Declares that no restrictions apply to bypass safety measures",
            "fix": "Remove restriction-bypass declarations; document specific permissions needed",
        },
    ],
    "EXCESSIVE-PERMS": [
        {
            "regex": r"(run|execute)\s+any\s+command",
            "risk": "Requests unrestricted command execution privileges",
            "fix": "Specify exact commands needed instead of requesting blanket execution",
        },
        {
            "regex": r"full\s+(file\s*system|filesystem)\s+access",
            "risk": "Requests unrestricted filesystem access",
            "fix": "Specify exact directories needed instead of full filesystem access",
        },
        {
            "regex": r"access\s+to\s+all\s+files",
            "risk": "Requests access to all files without scope limitation",
            "fix": "Limit file access to the skill's own directory and documented paths",
        },
        {
            "regex": r"root\s+access\s+required",
            "risk": "Claims root/admin access is required",
            "fix": "Remove root access requirement; skills should run with minimal privileges",
        },
    ],
    "HIDDEN-DIRECTIVE": [
        {
            "regex": r"<!--\s*(system|instruction|command|execute|override|ignore)",
            "risk": "HTML comment contains a hidden directive that may control AI behavior",
            "fix": "Remove hidden directives from HTML comments; all instructions should be visible",
        },
    ],
}

INFO_PATTERNS: Dict[str, List[Dict[str, str]]] = {
    "SUSPICIOUS-LANG": [
        {
            "regex": r"you\s+must\s+(always|never)\s+",
            "risk": "Strong directive language that may constrain AI behavior unexpectedly",
            "fix": "Consider using softer language (e.g., 'should' instead of 'must always')",
        },
        {
            "regex": r"do\s+not\s+(ever|under\s+any\s+circumstances)\s+",
            "risk": "Absolute prohibition that may conflict with the AI's base instructions",
            "fix": "Use scoped guidance instead of absolute prohibitions",
        },
        {
            "regex": r"from\s+now\s+on\s+(you|your)\s+",
            "risk": "Attempts to permanently alter AI behavior beyond the skill's scope",
            "fix": "Scope instructions to the skill's specific tasks, not permanent behavior changes",
        },
        {
            "regex": r"you\s+are\s+now\s+(a|an)\s+",
            "risk": "Attempts to redefine the AI's identity or role",
            "fix": "Use 'when using this skill, act as...' instead of identity reassignment",
        },
    ],
}

# Zero-width characters to detect (checked separately)
ZERO_WIDTH_CHARS: Dict[str, str] = {
    "\u200b": "zero-width space (U+200B)",
    "\u200c": "zero-width non-joiner (U+200C)",
    "\u200d": "zero-width joiner (U+200D)",
    "\ufeff": "byte order mark (U+FEFF)",
    "\u2060": "word joiner (U+2060)",
    "\u2062": "invisible times (U+2062)",
    "\u2063": "invisible separator (U+2063)",
}

SCANNABLE_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".rst", ".adoc"}


def is_in_code_block(lines: List[str], target_line: int) -> bool:
    """Check if a line number is inside a fenced code block (``` ... ```)."""
    in_block = False
    for i in range(target_line):
        stripped = lines[i].strip()
        if stripped.startswith("```"):
            in_block = not in_block
    return in_block


def scan_file(filepath: str) -> List[Finding]:
    """Scan a single file for prompt injection patterns."""
    findings: List[Finding] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
            lines = content.splitlines()
    except OSError:
        return findings

    # Check for zero-width characters across the entire content
    for char, description in ZERO_WIDTH_CHARS.items():
        pos = content.find(char)
        if pos != -1:
            # Find line number
            line_num = content[:pos].count("\n") + 1
            findings.append(Finding(
                severity="HIGH",
                category="HIDDEN-CHARS",
                file=filepath,
                line=line_num,
                matched_text=f"[{description}]",
                risk=f"Hidden {description} detected; may conceal injected instructions",
                fix="Remove all zero-width characters; paste content into a hex editor to verify",
            ))

    # Scan line by line for text patterns
    for line_num, line in enumerate(lines, start=1):
        # Skip lines inside fenced code blocks
        if is_in_code_block(lines, line_num - 1):
            continue

        line_lower = line.lower()

        for category, patterns in CRITICAL_PATTERNS.items():
            for pat in patterns:
                match = re.search(pat["regex"], line_lower)
                if match:
                    findings.append(Finding(
                        severity="CRITICAL",
                        category=category,
                        file=filepath,
                        line=line_num,
                        matched_text=match.group(0),
                        risk=pat["risk"],
                        fix=pat["fix"],
                    ))

        for category, patterns in HIGH_PATTERNS.items():
            for pat in patterns:
                match = re.search(pat["regex"], line_lower)
                if match:
                    findings.append(Finding(
                        severity="HIGH",
                        category=category,
                        file=filepath,
                        line=line_num,
                        matched_text=match.group(0),
                        risk=pat["risk"],
                        fix=pat["fix"],
                    ))

        for category, patterns in INFO_PATTERNS.items():
            for pat in patterns:
                match = re.search(pat["regex"], line_lower)
                if match:
                    findings.append(Finding(
                        severity="INFO",
                        category=category,
                        file=filepath,
                        line=line_num,
                        matched_text=match.group(0),
                        risk=pat["risk"],
                        fix=pat["fix"],
                    ))

    return findings


def collect_files(target: str) -> List[str]:
    """Collect scannable files from the target path."""
    target_path = Path(target)
    if target_path.is_file():
        if target_path.suffix in SCANNABLE_EXTENSIONS:
            return [str(target_path)]
        return []
    if target_path.is_dir():
        results = []
        for p in sorted(target_path.rglob("*")):
            if p.is_file() and p.suffix in SCANNABLE_EXTENSIONS:
                results.append(str(p))
        return results
    return []


def determine_verdict(critical: int, high: int, strict: bool) -> str:
    """Determine PASS/WARN/FAIL verdict."""
    if critical > 0:
        return "FAIL"
    if high > 0:
        return "FAIL" if strict else "WARN"
    return "PASS"


def format_human_readable(report: ScanReport) -> str:
    """Format the report for human-readable terminal output."""
    lines = [
        "",
        "+" + "=" * 55 + "+",
        "|  PROMPT INJECTION SCAN REPORT" + " " * 25 + "|",
        f"|  Target: {report.target[:44]:<44} |",
        f"|  Files scanned: {report.files_scanned:<37} |",
        f"|  Verdict: {report.verdict:<43} |",
        "+" + "=" * 55 + "+",
        f"|  CRITICAL: {report.critical_count}  |  HIGH: {report.high_count}  |  INFO: {report.info_count}",
        "+" + "=" * 55 + "+",
        "",
    ]

    if not report.findings:
        lines.append("  No prompt injection patterns found.")
        lines.append("")
        return "\n".join(lines)

    for f in report.findings:
        lines.append(f"{f['severity']} [{f['category']}] {f['file']}:{f['line']}")
        lines.append(f"  Matched: {f['matched_text'][:70]}")
        lines.append(f"  Risk: {f['risk']}")
        lines.append(f"  Fix: {f['fix']}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan markdown and text files for prompt injection patterns. "
                    "Detects system prompt overrides, role hijacking, safety bypasses, "
                    "data extraction instructions, hidden zero-width characters, "
                    "and suspicious HTML comment directives.",
        epilog="Examples:\n"
               "  %(prog)s SKILL.md\n"
               "  %(prog)s references/\n"
               "  %(prog)s . --strict --json\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        help="File or directory to scan (scans .md, .txt, .yaml, .yml files)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Strict mode: any HIGH finding upgrades verdict to FAIL",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        dest="json_output",
        help="Output results as JSON instead of human-readable text",
    )
    args = parser.parse_args()

    target = os.path.abspath(args.target)
    if not os.path.exists(target):
        print(f"Error: target '{args.target}' does not exist.", file=sys.stderr)
        sys.exit(2)

    files = collect_files(target)
    if not files:
        print(f"No scannable files found in '{args.target}'.", file=sys.stderr)
        sys.exit(0)

    all_findings: List[Finding] = []
    for f in files:
        all_findings.extend(scan_file(f))

    critical = sum(1 for f in all_findings if f.severity == "CRITICAL")
    high = sum(1 for f in all_findings if f.severity == "HIGH")
    info = sum(1 for f in all_findings if f.severity == "INFO")
    verdict = determine_verdict(critical, high, args.strict)

    report = ScanReport(
        target=args.target,
        files_scanned=len(files),
        total_findings=len(all_findings),
        critical_count=critical,
        high_count=high,
        info_count=info,
        verdict=verdict,
        strict_mode=args.strict,
        findings=[asdict(f) for f in all_findings],
    )

    if args.json_output:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(format_human_readable(report))

    sys.exit(1 if verdict == "FAIL" else 0)


if __name__ == "__main__":
    main()
