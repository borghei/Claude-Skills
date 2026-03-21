#!/usr/bin/env python3
"""
Code Scanner - Static security analysis for Python scripts.

Scans Python files for dangerous patterns including subprocess calls,
eval/exec usage, file operations outside skill boundaries, network calls,
unsafe imports, obfuscation, and credential harvesting.

Produces PASS/WARN/FAIL verdicts with severity-categorized findings.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Optional


@dataclass
class Finding:
    severity: str          # CRITICAL, HIGH, INFO
    category: str          # CODE-EXEC, NET-EXFIL, FS-BOUNDARY, etc.
    file: str
    line: int
    pattern: str
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
    "CODE-EXEC": [
        {
            "regex": r"\beval\s*\(",
            "risk": "Arbitrary code execution via eval()",
            "fix": "Replace eval() with ast.literal_eval() or explicit parsing",
        },
        {
            "regex": r"\bexec\s*\(",
            "risk": "Arbitrary code execution via exec()",
            "fix": "Remove exec() and use explicit function calls instead",
        },
        {
            "regex": r"\bcompile\s*\(",
            "risk": "Dynamic code compilation may execute untrusted input",
            "fix": "Remove compile() or ensure input is fully trusted and validated",
        },
        {
            "regex": r"__import__\s*\(",
            "risk": "Dynamic import can load arbitrary modules at runtime",
            "fix": "Use static imports at the top of the file",
        },
        {
            "regex": r"importlib\.import_module\s*\(",
            "risk": "Dynamic import can load arbitrary modules at runtime",
            "fix": "Use static imports at the top of the file",
        },
    ],
    "CMD-INJECT": [
        {
            "regex": r"os\.system\s*\(",
            "risk": "Shell command injection via os.system()",
            "fix": "Use subprocess.run() with a list of arguments and shell=False",
        },
        {
            "regex": r"os\.popen\s*\(",
            "risk": "Shell command injection via os.popen()",
            "fix": "Use subprocess.run() with a list of arguments and shell=False",
        },
        {
            "regex": r"subprocess\.\w+\(.*shell\s*=\s*True",
            "risk": "Shell=True enables command injection via string interpolation",
            "fix": "Remove shell=True and pass command as a list of arguments",
        },
    ],
    "NET-EXFIL": [
        {
            "regex": r"requests\.(post|put)\s*\(",
            "risk": "Outbound HTTP request may exfiltrate local data",
            "fix": "Remove outbound network calls or document the destination explicitly",
        },
        {
            "regex": r"urllib\.request\.urlopen\s*\(",
            "risk": "Outbound HTTP request may exfiltrate data",
            "fix": "Remove outbound network calls or document the destination explicitly",
        },
        {
            "regex": r"httpx\.(post|put)\s*\(",
            "risk": "Outbound HTTP request via httpx may exfiltrate data",
            "fix": "Remove outbound network calls or document the destination explicitly",
        },
        {
            "regex": r"socket\.connect\s*\(",
            "risk": "Raw socket connection may exfiltrate data to external server",
            "fix": "Remove socket connections or document the destination explicitly",
        },
        {
            "regex": r"aiohttp\.ClientSession\s*\(",
            "risk": "Async HTTP session may exfiltrate data",
            "fix": "Remove async HTTP clients or document the destination explicitly",
        },
    ],
    "CRED-HARVEST": [
        {
            "regex": r"['\"]~/\.ssh",
            "risk": "Reads SSH keys from user home directory",
            "fix": "Remove filesystem access to ~/.ssh entirely",
        },
        {
            "regex": r"['\"]~/\.aws",
            "risk": "Reads AWS credentials from user home directory",
            "fix": "Remove filesystem access to ~/.aws entirely",
        },
        {
            "regex": r"['\"]~/\.gnupg",
            "risk": "Reads GPG keys from user home directory",
            "fix": "Remove filesystem access to ~/.gnupg entirely",
        },
        {
            "regex": r"open\s*\(.*\.(pem|key|p12)",
            "risk": "Opens a private key or certificate file",
            "fix": "Remove access to private key files",
        },
    ],
}

HIGH_PATTERNS: Dict[str, List[Dict[str, str]]] = {
    "OBFUSCATION": [
        {
            "regex": r"base64\.b64decode\s*\(",
            "risk": "Base64 decoding may hide malicious payloads",
            "fix": "Verify the decoded content is safe or remove the decode call",
        },
        {
            "regex": r"codecs\.decode\s*\(",
            "risk": "Codecs decode may obscure malicious strings",
            "fix": "Use explicit string literals instead of encoded content",
        },
        {
            "regex": r"bytes\.fromhex\s*\(",
            "risk": "Hex decoding may hide malicious payloads",
            "fix": "Use explicit string literals instead of hex-encoded content",
        },
        {
            "regex": r"chr\s*\(\s*\d+\s*\)\s*\+\s*chr\s*\(",
            "risk": "Character-by-character string construction hides intent",
            "fix": "Use plain string literals instead of chr() chains",
        },
    ],
    "UNSAFE-DESER": [
        {
            "regex": r"pickle\.loads?\s*\(",
            "risk": "Pickle deserialization can execute arbitrary code",
            "fix": "Use json.loads() or a safe serialization format instead",
        },
        {
            "regex": r"yaml\.load\s*\([^)]*\)",
            "risk": "yaml.load() without SafeLoader executes arbitrary Python",
            "fix": "Use yaml.safe_load() or pass Loader=yaml.SafeLoader",
        },
        {
            "regex": r"marshal\.loads?\s*\(",
            "risk": "Marshal deserialization can execute arbitrary code",
            "fix": "Use json.loads() or a safe serialization format instead",
        },
    ],
    "FS-BOUNDARY": [
        {
            "regex": r"open\s*\(.*(/etc/|/usr/|/var/|/tmp/)",
            "risk": "File access outside the skill directory boundary",
            "fix": "Restrict file access to the skill's own directory",
        },
        {
            "regex": r"open\s*\(.*~/\.(bashrc|profile|zshrc)",
            "risk": "Modifies user shell configuration files",
            "fix": "Remove access to shell config files",
        },
        {
            "regex": r"os\.symlink\s*\(",
            "risk": "Symbolic links can redirect operations to sensitive locations",
            "fix": "Remove symlink creation or validate destination paths",
        },
        {
            "regex": r"shutil\.(rmtree|move)\s*\(",
            "risk": "Destructive file operation may affect files outside skill scope",
            "fix": "Validate paths are within the skill directory before operations",
        },
    ],
    "PRIV-ESC": [
        {
            "regex": r"\bsudo\b",
            "risk": "Privilege escalation via sudo",
            "fix": "Remove sudo usage; skills should not require elevated privileges",
        },
        {
            "regex": r"chmod\s+777",
            "risk": "World-writable permissions create security vulnerabilities",
            "fix": "Use restrictive permissions (e.g., 0o644 for files, 0o755 for dirs)",
        },
        {
            "regex": r"\bcrontab\b",
            "risk": "Cron manipulation can install persistent backdoors",
            "fix": "Remove crontab access; skills should not modify system schedules",
        },
    ],
}

INFO_PATTERNS: Dict[str, List[Dict[str, str]]] = {
    "SUBPROCESS": [
        {
            "regex": r"subprocess\.(run|call|check_output|check_call|Popen)\s*\(",
            "risk": "Subprocess call detected (verify shell=False and list args)",
            "fix": "Ensure command is passed as a list and shell=True is not used",
        },
    ],
    "ENV-ACCESS": [
        {
            "regex": r"os\.environ\s*[\[\.]",
            "risk": "Reads environment variables which may contain secrets",
            "fix": "Document which env vars are read and why they are needed",
        },
    ],
    "FILE-OPS": [
        {
            "regex": r"os\.path\.expanduser\s*\(",
            "risk": "Expands ~ to home directory; verify target is within skill scope",
            "fix": "Use paths relative to the skill directory instead",
        },
    ],
}


def is_inside_comment_or_string(line: str, match_start: int) -> bool:
    """Heuristic: check if match is inside a comment."""
    stripped = line[:match_start].lstrip()
    if stripped.startswith("#"):
        return True
    return False


def scan_file(filepath: str) -> List[Finding]:
    """Scan a single Python file for security patterns."""
    findings: List[Finding] = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        return findings

    rel_path = filepath

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Skip pure comment lines
        if stripped.startswith("#"):
            continue

        for category, patterns in CRITICAL_PATTERNS.items():
            for pat in patterns:
                if re.search(pat["regex"], line):
                    findings.append(Finding(
                        severity="CRITICAL",
                        category=category,
                        file=rel_path,
                        line=line_num,
                        pattern=stripped,
                        risk=pat["risk"],
                        fix=pat["fix"],
                    ))

        for category, patterns in HIGH_PATTERNS.items():
            for pat in patterns:
                if re.search(pat["regex"], line):
                    # Downgrade subprocess without shell=True to INFO
                    if category == "SUBPROCESS" and "shell" not in line:
                        continue
                    findings.append(Finding(
                        severity="HIGH",
                        category=category,
                        file=rel_path,
                        line=line_num,
                        pattern=stripped,
                        risk=pat["risk"],
                        fix=pat["fix"],
                    ))

        for category, patterns in INFO_PATTERNS.items():
            for pat in patterns:
                if re.search(pat["regex"], line):
                    findings.append(Finding(
                        severity="INFO",
                        category=category,
                        file=rel_path,
                        line=line_num,
                        pattern=stripped,
                        risk=pat["risk"],
                        fix=pat["fix"],
                    ))

    return findings


def determine_verdict(critical: int, high: int, strict: bool) -> str:
    """Determine PASS/WARN/FAIL verdict based on finding counts."""
    if critical > 0:
        return "FAIL"
    if high > 0:
        return "FAIL" if strict else "WARN"
    return "PASS"


def collect_python_files(target: str) -> List[str]:
    """Collect all .py files from the target path."""
    target_path = Path(target)
    if target_path.is_file() and target_path.suffix == ".py":
        return [str(target_path)]
    if target_path.is_dir():
        return sorted(str(p) for p in target_path.rglob("*.py"))
    return []


def format_human_readable(report: ScanReport) -> str:
    """Format the report for human-readable terminal output."""
    lines = [
        "",
        "+" + "=" * 55 + "+",
        "|  CODE SECURITY SCAN REPORT" + " " * 28 + "|",
        f"|  Target: {report.target[:44]:<44} |",
        f"|  Files scanned: {report.files_scanned:<37} |",
        f"|  Verdict: {report.verdict:<43} |",
        "+" + "=" * 55 + "+",
        f"|  CRITICAL: {report.critical_count}  |  HIGH: {report.high_count}  |  INFO: {report.info_count}",
        "+" + "=" * 55 + "+",
        "",
    ]

    if not report.findings:
        lines.append("  No security issues found.")
        lines.append("")
        return "\n".join(lines)

    for f in report.findings:
        lines.append(f"{f['severity']} [{f['category']}] {f['file']}:{f['line']}")
        lines.append(f"  Pattern: {f['pattern'][:80]}")
        lines.append(f"  Risk: {f['risk']}")
        lines.append(f"  Fix: {f['fix']}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan Python scripts for security issues. Detects eval/exec, "
                    "subprocess calls, network exfiltration, credential harvesting, "
                    "obfuscation, and unsafe imports.",
        epilog="Examples:\n"
               "  %(prog)s scripts/\n"
               "  %(prog)s helper.py --strict\n"
               "  %(prog)s . --json\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        help="File or directory to scan (scans .py files recursively)",
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

    py_files = collect_python_files(target)
    if not py_files:
        print(f"No Python files found in '{args.target}'.", file=sys.stderr)
        sys.exit(0)

    all_findings: List[Finding] = []
    for pf in py_files:
        all_findings.extend(scan_file(pf))

    critical = sum(1 for f in all_findings if f.severity == "CRITICAL")
    high = sum(1 for f in all_findings if f.severity == "HIGH")
    info = sum(1 for f in all_findings if f.severity == "INFO")
    verdict = determine_verdict(critical, high, args.strict)

    report = ScanReport(
        target=args.target,
        files_scanned=len(py_files),
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

    # Exit code: 1 for FAIL, 0 for PASS/WARN
    sys.exit(1 if verdict == "FAIL" else 0)


if __name__ == "__main__":
    main()
