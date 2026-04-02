#!/usr/bin/env python3
"""
Prompt Auditor - Audit prompts for injection vulnerabilities, bias, and safety issues.

Performs static analysis of prompt text to detect security vulnerabilities,
biased language, safety concerns, and quality issues.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional, Set


@dataclass
class AuditFinding:
    """A single audit finding."""
    category: str  # injection, bias, safety, quality
    severity: str  # critical, high, medium, low, info
    title: str
    description: str
    matched_text: str
    recommendation: str
    line_number: Optional[int] = None


@dataclass
class AuditReport:
    """Complete audit report."""
    prompt_length: int
    estimated_tokens: int
    total_findings: int = 0
    findings_by_severity: Dict[str, int] = field(default_factory=lambda: {
        "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0
    })
    findings_by_category: Dict[str, int] = field(default_factory=dict)
    findings: List[AuditFinding] = field(default_factory=list)
    overall_risk: str = "low"
    pass_audit: bool = True


# Injection vulnerability patterns
INJECTION_PATTERNS = [
    (r'\{.*user.*\}', "critical",
     "User input interpolation in prompt",
     "Direct user input interpolation enables prompt injection attacks.",
     "Use parameterized templates with input sanitization and delimiters."),
    (r'\{.*input.*\}', "critical",
     "Input variable in prompt template",
     "Input variables without sanitization can carry injection payloads.",
     "Sanitize all inputs. Use XML/delimiter tags to separate instructions from data."),
    (r'(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|above|prior)\s+(?:instructions|rules)',
     "high",
     "Anti-jailbreak instruction detected",
     "The prompt contains defensive language against jailbreaks, suggesting it may be vulnerable.",
     "Instead of defensive text, use structural defenses: delimiters, output validation, and layered prompts."),
    (r'(?:you\s+(?:must|should)\s+)?never\s+reveal\s+(?:this|your|the)\s+(?:system\s+)?prompt',
     "medium",
     "System prompt concealment instruction",
     "Instructing the model to hide the system prompt is a weak defense that can be bypassed.",
     "Accept that system prompts may leak. Don't put secrets in prompts. Use API-level controls."),
    (r'{{.*}}',
     "medium",
     "Double-brace template syntax",
     "Template syntax could be exploited if user input is processed through the same template engine.",
     "Ensure user input never passes through the template engine."),
]

# Bias detection patterns
BIAS_PATTERNS = [
    (r'\b(?:he|his|him)\b(?!(?:\s+or\s+(?:she|her)))', "medium",
     "Gendered language (male default)",
     "Prompt uses male pronouns without inclusive alternatives.",
     "Use 'they/them' or 'he/she' for inclusive language."),
    (r'\b(?:chairman|businessman|fireman|policeman|mailman)\b', "medium",
     "Gendered job title",
     "Prompt uses gendered job titles that may introduce bias.",
     "Use gender-neutral alternatives: chairperson, businessperson, firefighter, etc."),
    (r'\b(?:blacklist|whitelist|master|slave)\b', "low",
     "Potentially exclusionary terminology",
     "Terms like blacklist/whitelist and master/slave have inclusivity concerns.",
     "Use alternatives: blocklist/allowlist, primary/replica, main/secondary."),
    (r'\b(?:normal|abnormal|crazy|insane|lame|dumb)\b', "low",
     "Potentially ableist language",
     "These terms may reinforce ableist assumptions.",
     "Use specific, descriptive language instead of these colloquial terms."),
    (r'\b(?:always|never|all|none|every)\b.*\b(?:people|users|customers|employees)\b', "low",
     "Absolute generalization about people",
     "Absolute statements about groups can reinforce stereotypes.",
     "Use qualified language: 'many', 'some', 'typically' instead of absolutes."),
]

# Safety patterns
SAFETY_PATTERNS = [
    (r'(?:generate|create|write|produce)\s+(?:any|all)\s+(?:content|text|output)', "high",
     "Unrestricted content generation scope",
     "Prompt allows unrestricted content generation without safety boundaries.",
     "Add explicit content restrictions: 'Do not generate violent, sexual, or illegal content.'"),
    (r'(?:no\s+(?:restrictions|limits|boundaries|constraints))', "critical",
     "Explicit removal of safety restrictions",
     "Prompt explicitly removes safety constraints, enabling harmful output.",
     "Always maintain safety boundaries. Define allowed content scope positively."),
    (r'(?:personal|private|sensitive)\s+(?:data|information|details)', "medium",
     "PII handling reference without explicit policy",
     "Prompt references personal data but may lack explicit handling instructions.",
     "Add clear PII handling instructions: minimize collection, mask in output, don't store."),
    (r'(?:medical|legal|financial)\s+advice', "high",
     "Professional advice generation without disclaimers",
     "Prompt may generate professional advice without appropriate disclaimers.",
     "Add disclaimers: 'This is informational only. Consult a professional for advice.'"),
    (r'(?:password|secret|api.?key|token|credential)', "medium",
     "Credentials referenced in prompt",
     "Prompt contains or references sensitive credentials.",
     "Never include credentials in prompts. Use environment variables and reference by name only."),
    (r'(?:execute|run|eval)\s+(?:code|command|script)', "high",
     "Code execution instruction without sandboxing",
     "Prompt instructs code execution without apparent sandboxing.",
     "If code execution is needed, specify sandboxed environments and allowed operations."),
]

# Quality patterns
QUALITY_PATTERNS = [
    (r'^.{0,50}$', "info",
     "Very short prompt",
     "Prompt is very short and may lack sufficient context for consistent results.",
     "Consider adding context, examples, or output format specifications."),
    (r'(?:etc|\.\.\.)', "info",
     "Vague continuation marker",
     "Using 'etc.' or '...' leaves ambiguity about expected behavior.",
     "Be explicit about all expected behaviors and outputs."),
    (r'(?:be\s+creative|use\s+your\s+(?:judgment|discretion))', "low",
     "Subjective instruction",
     "Subjective instructions lead to inconsistent outputs.",
     "Provide specific criteria, examples, or constraints instead of subjective directives."),
]

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def estimate_tokens(text: str) -> int:
    """Quick token estimation."""
    return max(1, int(len(text) / 4.0 * 0.5 + len(text.split()) / 0.75 * 0.5))


def run_audit(text: str, checks: Optional[Set[str]] = None) -> AuditReport:
    """Run full prompt audit."""
    all_checks = checks or {"injection", "bias", "safety", "quality"}
    report = AuditReport(
        prompt_length=len(text),
        estimated_tokens=estimate_tokens(text),
    )

    lines = text.split("\n")
    pattern_groups = []

    if "injection" in all_checks:
        pattern_groups.append(("injection", INJECTION_PATTERNS))
    if "bias" in all_checks:
        pattern_groups.append(("bias", BIAS_PATTERNS))
    if "safety" in all_checks:
        pattern_groups.append(("safety", SAFETY_PATTERNS))
    if "quality" in all_checks:
        pattern_groups.append(("quality", QUALITY_PATTERNS))

    for category, patterns in pattern_groups:
        for pattern_str, severity, title, desc, rec in patterns:
            try:
                pattern = re.compile(pattern_str, re.IGNORECASE)
            except re.error:
                continue

            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    match = pattern.search(line)
                    matched_text = match.group()[:80] if match else line.strip()[:80]
                    report.findings.append(AuditFinding(
                        category=category,
                        severity=severity,
                        title=title,
                        description=desc,
                        matched_text=matched_text,
                        recommendation=rec,
                        line_number=i,
                    ))

    # Check for missing safety elements
    if "safety" in all_checks:
        full_lower = text.lower()
        if "do not" not in full_lower and "don't" not in full_lower and "must not" not in full_lower:
            report.findings.append(AuditFinding(
                category="safety",
                severity="info",
                title="No negative constraints found",
                description="Prompt lacks explicit 'do not' constraints. Consider adding boundaries.",
                matched_text="[entire prompt]",
                recommendation="Add explicit restrictions on what the model should NOT do.",
            ))

        if "format" not in full_lower and "json" not in full_lower and "structure" not in full_lower:
            report.findings.append(AuditFinding(
                category="quality",
                severity="info",
                title="No output format specification",
                description="Prompt doesn't specify an output format, leading to inconsistent responses.",
                matched_text="[entire prompt]",
                recommendation="Add output format instructions (e.g., JSON schema, markdown template).",
            ))

    # Aggregate
    report.total_findings = len(report.findings)
    for f in report.findings:
        report.findings_by_severity[f.severity] = report.findings_by_severity.get(f.severity, 0) + 1
        report.findings_by_category[f.category] = report.findings_by_category.get(f.category, 0) + 1

    report.findings.sort(key=lambda x: SEVERITY_ORDER.get(x.severity, 4))

    # Determine overall risk and pass/fail
    if report.findings_by_severity.get("critical", 0) > 0:
        report.overall_risk = "critical"
        report.pass_audit = False
    elif report.findings_by_severity.get("high", 0) > 0:
        report.overall_risk = "high"
        report.pass_audit = False
    elif report.findings_by_severity.get("medium", 0) > 0:
        report.overall_risk = "medium"
        report.pass_audit = True
    else:
        report.overall_risk = "low"
        report.pass_audit = True

    return report


def format_human(report: AuditReport) -> str:
    """Format for human reading."""
    lines = []
    lines.append("=" * 65)
    lines.append("PROMPT AUDIT REPORT")
    lines.append("=" * 65)
    lines.append(f"Prompt length: {report.prompt_length} chars, ~{report.estimated_tokens} tokens")
    lines.append(f"Total findings: {report.total_findings}")
    verdict = "PASS" if report.pass_audit else "FAIL"
    lines.append(f"Overall risk: {report.overall_risk.upper()}")
    lines.append(f"Audit result: {verdict}")
    lines.append("")

    lines.append("Findings by Severity:")
    for sev in ["critical", "high", "medium", "low", "info"]:
        count = report.findings_by_severity.get(sev, 0)
        if count > 0:
            lines.append(f"  {sev.upper()}: {count}")
    lines.append("")

    if report.findings_by_category:
        lines.append("Findings by Category:")
        for cat, count in sorted(report.findings_by_category.items()):
            lines.append(f"  {cat}: {count}")
        lines.append("")

    for i, f in enumerate(report.findings, 1):
        lines.append("-" * 50)
        ln = f" (line {f.line_number})" if f.line_number else ""
        lines.append(f"[{i}] [{f.severity.upper()}] [{f.category.upper()}] {f.title}{ln}")
        lines.append(f"    Match: {f.matched_text}")
        lines.append(f"    Issue: {f.description}")
        lines.append(f"    Fix: {f.recommendation}")
        lines.append("")

    if report.total_findings == 0:
        lines.append("No issues found. Prompt passes audit.")

    lines.append("=" * 65)
    return "\n".join(lines)


def format_json(report: AuditReport) -> str:
    """Format as JSON."""
    data = {
        "prompt_length": report.prompt_length,
        "estimated_tokens": report.estimated_tokens,
        "total_findings": report.total_findings,
        "overall_risk": report.overall_risk,
        "pass_audit": report.pass_audit,
        "findings_by_severity": report.findings_by_severity,
        "findings_by_category": report.findings_by_category,
        "findings": [asdict(f) for f in report.findings],
    }
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Prompt Auditor - Audit prompts for injection, bias, and safety issues"
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--file", help="Path to prompt file")
    input_group.add_argument("--text", help="Prompt text to audit")
    input_group.add_argument("--stdin", action="store_true", help="Read from stdin")

    parser.add_argument("--checks", help="Comma-separated checks to run: injection,bias,safety,quality (default: all)")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    args = parser.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        text = path.read_text(encoding="utf-8", errors="ignore")
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    checks = None
    if args.checks:
        checks = set(args.checks.split(","))

    report = run_audit(text, checks)

    if args.format == "json":
        print(format_json(report))
    else:
        print(format_human(report))

    sys.exit(0 if report.pass_audit else 1)


if __name__ == "__main__":
    main()
