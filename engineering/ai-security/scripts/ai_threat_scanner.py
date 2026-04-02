#!/usr/bin/env python3
"""
AI Threat Scanner - Detect AI-specific security vulnerabilities in source code.

Scans codebases for prompt injection risks, data poisoning vectors, model extraction
vulnerabilities, adversarial input handling gaps, and insecure model serving patterns.

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
from typing import List, Dict, Optional, Tuple


@dataclass
class Finding:
    """Represents a single security finding."""
    category: str
    severity: str
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    recommendation: str
    cwe_id: Optional[str] = None


@dataclass
class ScanResult:
    """Aggregated scan results."""
    total_files_scanned: int = 0
    total_findings: int = 0
    findings_by_severity: Dict[str, int] = field(default_factory=lambda: {
        "critical": 0, "high": 0, "medium": 0, "low": 0
    })
    findings_by_category: Dict[str, int] = field(default_factory=dict)
    findings: List[Finding] = field(default_factory=list)


# Pattern definitions: (regex, severity, title, description, recommendation, cwe_id)
PROMPT_INJECTION_PATTERNS = [
    (
        r'f["\'].*\{.*user.*(?:input|query|message|text|prompt).*\}',
        "high",
        "Unsanitized user input in prompt template",
        "User-controlled input is directly interpolated into a prompt string via f-string. "
        "An attacker can inject instructions that override system behavior.",
        "Sanitize user input before prompt assembly. Use delimiters to separate instructions from user content.",
        "CWE-77"
    ),
    (
        r'(?:prompt|system_prompt|instruction)\s*(?:\+|\.format|%)\s*.*(?:user|input|query|request)',
        "high",
        "String concatenation of user input into prompt",
        "User input is concatenated or formatted into prompt strings without sanitization.",
        "Use parameterized prompt templates with explicit input boundaries.",
        "CWE-77"
    ),
    (
        r'\.format\(.*(?:user_input|user_message|query|request_body)',
        "medium",
        "Format string with user input in prompt context",
        "User-controlled values used in .format() calls that may construct prompts.",
        "Validate and sanitize all user inputs before including in prompt templates.",
        "CWE-134"
    ),
    (
        r'(?:messages|chat).*(?:append|extend|insert).*(?:user|input|content)',
        "medium",
        "Dynamic message list manipulation with user content",
        "Chat message arrays are modified with user-controlled content without validation.",
        "Validate message structure and content before adding to conversation history.",
        "CWE-20"
    ),
    (
        r'(?:jinja|template|render).*(?:user|input|query)',
        "high",
        "Template engine used with user input for prompt generation",
        "Template engines (Jinja2, etc.) used to render prompts with user input can enable injection.",
        "Escape user input and restrict template capabilities. Avoid user-controlled template strings.",
        "CWE-94"
    ),
]

DATA_POISONING_PATTERNS = [
    (
        r'(?:read_csv|load_data|read_json|read_parquet).*(?:http|ftp|s3://|gs://)',
        "high",
        "Training data loaded from remote source without integrity check",
        "Data is loaded from a remote URL without checksum verification or signature validation.",
        "Verify data integrity with checksums. Pin data versions. Use signed URLs.",
        "CWE-494"
    ),
    (
        r'(?:train|fit|fine.?tune).*(?:DataFrame|dataset|data_loader)',
        "low",
        "Training pipeline detected - verify data validation",
        "A training pipeline was detected. Ensure data validation is in place.",
        "Add data validation, schema checks, and anomaly detection before training.",
        "CWE-20"
    ),
    (
        r'(?:pickle|joblib|torch)\.load\s*\(',
        "critical",
        "Unsafe deserialization used for data/model loading",
        "pickle/joblib/torch.load can execute arbitrary code during deserialization. "
        "If the source is untrusted, this is a remote code execution vector.",
        "Use safe serialization formats (JSON, SafeTensors). Verify file checksums before loading.",
        "CWE-502"
    ),
    (
        r'(?:crawl|scrape|fetch).*(?:train|dataset|corpus)',
        "medium",
        "Web-scraped data used in training pipeline",
        "Data scraped from the web is used in training without apparent sanitization.",
        "Sanitize and validate scraped data. Check for adversarial content injection.",
        "CWE-829"
    ),
]

MODEL_EXTRACTION_PATTERNS = [
    (
        r'(?:predict|inference|generate|embed)\s*\(.*\).*(?:return|response).*(?:logits|probabilities|scores|confidence)',
        "high",
        "Model confidence scores exposed in API response",
        "Returning raw logits or probability distributions enables model extraction attacks.",
        "Return only top-k predictions without confidence scores. Implement rate limiting.",
        "CWE-200"
    ),
    (
        r'@(?:app|router)\.(?:get|post|put)\s*\(\s*["\'].*(?:predict|infer|generate|embed)',
        "medium",
        "Model inference endpoint detected - verify rate limiting",
        "A model inference endpoint was found. Verify rate limiting and authentication are in place.",
        "Add rate limiting, authentication, and query logging to inference endpoints.",
        "CWE-770"
    ),
    (
        r'(?:model|weights|checkpoint).*(?:download|export|save|serialize).*(?:response|send|return)',
        "critical",
        "Model weights potentially exposed via API",
        "Model weights or checkpoints appear to be accessible through an API endpoint.",
        "Never expose model weights through public APIs. Use access controls and audit logging.",
        "CWE-200"
    ),
    (
        r'(?:traceback|stack_trace|exception).*(?:model|layer|weight|architecture)',
        "medium",
        "Error responses may leak model architecture details",
        "Verbose error handling could expose model architecture information to attackers.",
        "Use generic error messages in production. Log detailed errors server-side only.",
        "CWE-209"
    ),
]

ADVERSARIAL_INPUT_PATTERNS = [
    (
        r'(?:predict|classify|detect)\s*\((?!.*(?:validate|check|sanitize|clip|clamp)).*\)',
        "medium",
        "Model inference without input validation",
        "Model prediction is called without apparent input validation or bounds checking.",
        "Validate input shape, type, and value ranges before model inference.",
        "CWE-20"
    ),
    (
        r'(?:numpy|np|torch|tf)\.(?:array|tensor)\s*\(\s*(?:request|input|data|body)',
        "medium",
        "Direct conversion of user input to tensor without validation",
        "User input is converted directly to numpy/torch tensors without type or range validation.",
        "Validate input dtype, shape, and value ranges before tensor conversion.",
        "CWE-20"
    ),
    (
        r'(?:Image|PIL|cv2)\.(?:open|imread|load)\s*\(.*(?:user|upload|request|input)',
        "medium",
        "User-uploaded image processed without validation",
        "Images from untrusted sources are loaded without format or size validation.",
        "Validate image format, dimensions, and file size. Re-encode images before processing.",
        "CWE-434"
    ),
]

INSECURE_SERVING_PATTERNS = [
    (
        r'pickle\.loads?\s*\(\s*(?:open|read|request|data|body|content)',
        "critical",
        "Pickle deserialization of untrusted data",
        "pickle.load/loads is used on potentially untrusted data, enabling arbitrary code execution.",
        "Never unpickle untrusted data. Use SafeTensors, JSON, or other safe formats.",
        "CWE-502"
    ),
    (
        r'(?:CORS|cors).*(?:\*|allow_all|any)',
        "medium",
        "Overly permissive CORS on model API",
        "CORS is configured to allow all origins, increasing the attack surface of model APIs.",
        "Restrict CORS to specific trusted origins.",
        "CWE-942"
    ),
    (
        r'(?:debug|DEBUG)\s*=\s*(?:True|1|true)',
        "high",
        "Debug mode enabled in model serving configuration",
        "Debug mode is enabled, which may expose model internals, stack traces, and configuration.",
        "Disable debug mode in production. Use environment-based configuration.",
        "CWE-489"
    ),
    (
        r'(?:eval|exec)\s*\(.*(?:user|input|request|query)',
        "critical",
        "Code execution with user-controlled input",
        "eval() or exec() is called with user-controlled data, enabling remote code execution.",
        "Never use eval/exec with untrusted input. Use safe alternatives.",
        "CWE-94"
    ),
]

CATEGORY_MAP = {
    "prompt-injection": PROMPT_INJECTION_PATTERNS,
    "data-poisoning": DATA_POISONING_PATTERNS,
    "model-extraction": MODEL_EXTRACTION_PATTERNS,
    "adversarial-input": ADVERSARIAL_INPUT_PATTERNS,
    "insecure-serving": INSECURE_SERVING_PATTERNS,
}

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

SCAN_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".rb", ".yaml", ".yml", ".toml", ".json", ".cfg", ".ini"}


def scan_file(file_path: Path, categories: List[str]) -> List[Finding]:
    """Scan a single file for AI security patterns."""
    findings = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError):
        return findings

    lines = content.split("\n")

    for category_name in categories:
        patterns = CATEGORY_MAP.get(category_name, [])
        for pattern_str, severity, title, desc, rec, cwe in patterns:
            try:
                pattern = re.compile(pattern_str, re.IGNORECASE)
            except re.error:
                continue

            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
                    continue
                if pattern.search(line):
                    snippet = line.strip()[:120]
                    findings.append(Finding(
                        category=category_name,
                        severity=severity,
                        title=title,
                        description=desc,
                        file_path=str(file_path),
                        line_number=i,
                        code_snippet=snippet,
                        recommendation=rec,
                        cwe_id=cwe,
                    ))
    return findings


def collect_files(path: Path) -> List[Path]:
    """Collect all scannable files under the given path."""
    files = []
    if path.is_file():
        if path.suffix in SCAN_EXTENSIONS:
            files.append(path)
    elif path.is_dir():
        for root, dirs, filenames in os.walk(path):
            dirs[:] = [d for d in dirs if d not in {
                ".git", "node_modules", "__pycache__", ".venv", "venv",
                ".tox", ".mypy_cache", "dist", "build", ".eggs"
            }]
            for fname in filenames:
                fp = Path(root) / fname
                if fp.suffix in SCAN_EXTENSIONS:
                    files.append(fp)
    return files


def run_scan(path: Path, categories: List[str], min_severity: str) -> ScanResult:
    """Run the full scan and aggregate results."""
    result = ScanResult()
    files = collect_files(path)
    result.total_files_scanned = len(files)
    min_sev_val = SEVERITY_ORDER.get(min_severity, 3)

    for fp in files:
        file_findings = scan_file(fp, categories)
        for f in file_findings:
            if SEVERITY_ORDER.get(f.severity, 3) <= min_sev_val:
                result.findings.append(f)
                result.total_findings += 1
                result.findings_by_severity[f.severity] = result.findings_by_severity.get(f.severity, 0) + 1
                result.findings_by_category[f.category] = result.findings_by_category.get(f.category, 0) + 1

    result.findings.sort(key=lambda x: SEVERITY_ORDER.get(x.severity, 3))
    return result


def format_human(result: ScanResult) -> str:
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("AI THREAT SCANNER REPORT")
    lines.append("=" * 70)
    lines.append(f"Files scanned: {result.total_files_scanned}")
    lines.append(f"Total findings: {result.total_findings}")
    lines.append("")
    lines.append("Findings by Severity:")
    for sev in ["critical", "high", "medium", "low"]:
        count = result.findings_by_severity.get(sev, 0)
        if count > 0:
            marker = "!!!" if sev == "critical" else "! " if sev == "high" else "- " if sev == "medium" else "  "
            lines.append(f"  {marker} {sev.upper()}: {count}")
    lines.append("")
    if result.findings_by_category:
        lines.append("Findings by Category:")
        for cat, count in sorted(result.findings_by_category.items()):
            lines.append(f"  {cat}: {count}")
        lines.append("")

    for i, f in enumerate(result.findings, 1):
        lines.append("-" * 60)
        lines.append(f"[{i}] [{f.severity.upper()}] {f.title}")
        lines.append(f"    Category: {f.category}")
        lines.append(f"    File: {f.file_path}:{f.line_number}")
        if f.cwe_id:
            lines.append(f"    CWE: {f.cwe_id}")
        lines.append(f"    Code: {f.code_snippet}")
        lines.append(f"    Description: {f.description}")
        lines.append(f"    Recommendation: {f.recommendation}")
        lines.append("")

    if result.total_findings == 0:
        lines.append("No AI security findings detected. Good job!")

    lines.append("=" * 70)
    return "\n".join(lines)


def format_json(result: ScanResult) -> str:
    """Format results as JSON."""
    data = {
        "total_files_scanned": result.total_files_scanned,
        "total_findings": result.total_findings,
        "findings_by_severity": result.findings_by_severity,
        "findings_by_category": result.findings_by_category,
        "findings": [asdict(f) for f in result.findings],
    }
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="AI Threat Scanner - Detect AI-specific security vulnerabilities in source code"
    )
    parser.add_argument("--path", required=True, help="Path to scan (file or directory)")
    parser.add_argument("--category", choices=list(CATEGORY_MAP.keys()),
                        help="Scan only a specific threat category")
    parser.add_argument("--min-severity", choices=["critical", "high", "medium", "low"],
                        default="low", help="Minimum severity to report (default: low)")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    args = parser.parse_args()
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    categories = [args.category] if args.category else list(CATEGORY_MAP.keys())
    result = run_scan(path, categories, args.min_severity)

    if args.format == "json":
        print(format_json(result))
    else:
        print(format_human(result))

    if result.findings_by_severity.get("critical", 0) > 0:
        sys.exit(2)
    elif result.findings_by_severity.get("high", 0) > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
