#!/usr/bin/env python3
"""
Change Scope Analyzer - Identify minimal files to change for a bugfix.

Analyzes a bug description against a codebase to find the most relevant files,
estimate change scope, and recommend a focused fix approach.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import math


@dataclass
class FileRelevance:
    """A file's relevance to the bug description."""
    file_path: str
    relevance_score: float
    matching_keywords: List[str]
    matching_lines: List[Tuple[int, str]]  # (line_num, line_text)
    estimated_change_lines: int
    confidence: str  # high, medium, low
    reason: str


@dataclass
class ScopeAnalysis:
    """Complete scope analysis result."""
    bug_description: str
    extracted_keywords: List[str]
    total_files_scanned: int
    relevant_files: List[FileRelevance] = field(default_factory=list)
    scope_category: str = ""  # micro, small, medium, large
    estimated_total_files: int = 0
    estimated_total_lines: int = 0
    risk_level: str = ""
    recommended_approach: str = ""
    warnings: List[str] = field(default_factory=list)


# Keyword categories that map bug descriptions to code areas
KEYWORD_DOMAINS = {
    "authentication": ["login", "auth", "password", "credential", "session", "token", "jwt",
                       "oauth", "sso", "signin", "signup", "logout", "2fa", "mfa"],
    "authorization": ["permission", "access", "denied", "forbidden", "role", "acl", "rbac",
                      "policy", "scope", "privilege"],
    "api": ["api", "endpoint", "request", "response", "rest", "graphql", "route", "handler",
            "middleware", "controller", "status code", "http", "404", "500", "401", "403"],
    "database": ["query", "database", "sql", "table", "column", "migration", "orm",
                 "transaction", "index", "foreign key", "constraint", "join"],
    "frontend": ["display", "render", "layout", "css", "style", "component", "template",
                 "ui", "ux", "button", "form", "input", "modal", "responsive", "mobile"],
    "data_validation": ["validation", "null", "undefined", "empty", "missing", "format",
                        "parse", "convert", "type", "schema", "regex", "pattern"],
    "performance": ["slow", "timeout", "performance", "latency", "cache", "memory", "leak",
                    "cpu", "load", "optimize", "n+1", "batch"],
    "error_handling": ["crash", "exception", "error", "bug", "fail", "broken", "traceback",
                       "stack trace", "panic", "unhandled"],
    "email": ["email", "mail", "notification", "send", "smtp", "template", "newsletter"],
    "file_handling": ["file", "upload", "download", "path", "directory", "permission",
                      "read", "write", "stream", "encoding", "utf"],
    "integration": ["webhook", "callback", "integration", "third-party", "external",
                    "service", "sdk", "client"],
    "configuration": ["config", "environment", "env", "setting", "flag", "feature",
                      "toggle", "variable"],
}

# File path patterns that correlate with keyword domains
PATH_DOMAIN_PATTERNS = {
    "authentication": [r'auth', r'login', r'session', r'identity'],
    "authorization": [r'perm', r'role', r'policy', r'guard'],
    "api": [r'api', r'route', r'controller', r'handler', r'endpoint', r'middleware'],
    "database": [r'model', r'schema', r'migration', r'repository', r'dao', r'query'],
    "frontend": [r'component', r'view', r'template', r'page', r'layout', r'style'],
    "data_validation": [r'valid', r'schema', r'form', r'sanitiz', r'filter'],
    "performance": [r'cache', r'queue', r'worker', r'task', r'job'],
    "error_handling": [r'error', r'exception', r'handler', r'middleware'],
    "email": [r'mail', r'email', r'notification', r'message'],
    "file_handling": [r'upload', r'storage', r'file', r'media', r'asset'],
    "integration": [r'client', r'service', r'integration', r'webhook', r'external'],
    "configuration": [r'config', r'setting', r'env'],
}

SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".rb",
    ".php", ".cs", ".swift", ".kt", ".scala", ".css", ".scss", ".html",
    ".vue", ".svelte", ".sql", ".yaml", ".yml", ".toml", ".json", ".xml",
}

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".tox", ".mypy_cache", ".eggs", "vendor", ".next", ".nuxt",
}


def extract_keywords(bug_description: str) -> Tuple[List[str], Dict[str, float]]:
    """Extract keywords from bug description and score by domain relevance."""
    words = re.findall(r'\b[a-zA-Z_]{2,}\b', bug_description.lower())
    # Remove common stop words
    stop_words = {"the", "is", "at", "in", "on", "to", "of", "and", "or", "for",
                  "it", "an", "as", "by", "be", "was", "are", "been", "has", "have",
                  "had", "do", "does", "did", "will", "would", "could", "should",
                  "when", "where", "what", "how", "why", "with", "from", "not", "but",
                  "this", "that", "they", "them", "their", "there", "than", "then",
                  "also", "just", "only", "very", "can", "into", "some", "other"}
    keywords = [w for w in words if w not in stop_words]

    # Score domains
    domain_scores: Dict[str, float] = defaultdict(float)
    for word in keywords:
        for domain, domain_keywords in KEYWORD_DOMAINS.items():
            for dk in domain_keywords:
                if dk in word or word in dk:
                    domain_scores[domain] += 1.0
                elif _fuzzy_match(word, dk):
                    domain_scores[domain] += 0.5

    return keywords, dict(domain_scores)


def _fuzzy_match(a: str, b: str) -> bool:
    """Simple fuzzy matching - checks if strings share significant overlap."""
    if len(a) < 3 or len(b) < 3:
        return False
    shorter = min(a, b, key=len)
    longer = max(a, b, key=len)
    return shorter in longer


def collect_files(path: Path, extensions: Optional[Set[str]] = None) -> List[Path]:
    """Collect source files from the codebase."""
    exts = extensions or SCAN_EXTENSIONS
    files = []
    if path.is_file():
        if path.suffix in exts:
            files.append(path)
    else:
        for root, dirs, filenames in os.walk(path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fname in filenames:
                fp = Path(root) / fname
                if fp.suffix in exts:
                    files.append(fp)
    return files


def score_file(file_path: Path, keywords: List[str], domain_scores: Dict[str, float],
               base_path: Path) -> Optional[FileRelevance]:
    """Score a file's relevance to the bug."""
    score = 0.0
    matching_keywords = []
    matching_lines = []
    reasons = []

    rel_path = str(file_path.relative_to(base_path)).lower()

    # Score based on path matching domain patterns
    for domain, patterns in PATH_DOMAIN_PATTERNS.items():
        domain_weight = domain_scores.get(domain, 0)
        if domain_weight > 0:
            for pat in patterns:
                if re.search(pat, rel_path, re.IGNORECASE):
                    score += domain_weight * 2
                    reasons.append(f"Path matches {domain} domain")
                    break

    # Score based on file content keyword matching
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError):
        return None

    lines = content.split("\n")
    content_lower = content.lower()

    for keyword in keywords:
        if keyword in content_lower:
            matching_keywords.append(keyword)
            # Find specific matching lines (up to 3 per keyword)
            count = 0
            for i, line in enumerate(lines, 1):
                if keyword in line.lower() and count < 3:
                    matching_lines.append((i, line.strip()[:100]))
                    count += 1
            score += 1.0

    # Bonus for filename matching keywords
    fname = file_path.stem.lower()
    for keyword in keywords:
        if keyword in fname:
            score += 3.0
            reasons.append(f"Filename contains '{keyword}'")

    if score < 0.5:
        return None

    # Estimate change scope based on matching density
    match_density = len(matching_keywords) / max(len(keywords), 1)
    estimated_lines = max(1, int(match_density * 10))

    # Determine confidence
    if score >= 8:
        confidence = "high"
    elif score >= 4:
        confidence = "medium"
    else:
        confidence = "low"

    reason = "; ".join(reasons) if reasons else f"Content matches: {', '.join(matching_keywords[:5])}"

    return FileRelevance(
        file_path=str(file_path.relative_to(base_path)),
        relevance_score=round(score, 2),
        matching_keywords=matching_keywords,
        matching_lines=matching_lines[:5],
        estimated_change_lines=estimated_lines,
        confidence=confidence,
        reason=reason,
    )


def analyze_scope(bug_description: str, path: Path,
                  extensions: Optional[Set[str]] = None) -> ScopeAnalysis:
    """Perform full scope analysis."""
    keywords, domain_scores = extract_keywords(bug_description)
    files = collect_files(path, extensions)

    analysis = ScopeAnalysis(
        bug_description=bug_description,
        extracted_keywords=keywords,
        total_files_scanned=len(files),
    )

    # Score all files
    scored = []
    for fp in files:
        relevance = score_file(fp, keywords, domain_scores, path)
        if relevance:
            scored.append(relevance)

    # Sort by relevance score descending
    scored.sort(key=lambda x: x.relevance_score, reverse=True)

    # Keep top results (max 15)
    analysis.relevant_files = scored[:15]
    analysis.estimated_total_files = min(len(scored), 15)
    analysis.estimated_total_lines = sum(f.estimated_change_lines for f in analysis.relevant_files[:5])

    # Classify scope
    high_confidence = [f for f in analysis.relevant_files if f.confidence == "high"]
    if len(high_confidence) <= 1 and analysis.estimated_total_lines <= 5:
        analysis.scope_category = "micro"
        analysis.risk_level = "very low"
    elif len(high_confidence) <= 2 and analysis.estimated_total_lines <= 20:
        analysis.scope_category = "small"
        analysis.risk_level = "low"
    elif len(high_confidence) <= 4 and analysis.estimated_total_lines <= 50:
        analysis.scope_category = "medium"
        analysis.risk_level = "medium"
    else:
        analysis.scope_category = "large"
        analysis.risk_level = "high"
        analysis.warnings.append("Large scope detected. Consider breaking into smaller fixes.")

    # Generate approach recommendation
    if analysis.scope_category in ("micro", "small"):
        analysis.recommended_approach = (
            "Direct fix: Change the identified file(s) with minimal modifications. "
            "Add a regression test targeting the specific bug scenario."
        )
    elif analysis.scope_category == "medium":
        analysis.recommended_approach = (
            "Targeted fix: Focus on the top 2-3 high-confidence files first. "
            "Verify the fix resolves the issue before touching additional files. "
            "Consider if all changes are truly necessary for this fix."
        )
    else:
        analysis.recommended_approach = (
            "Structural fix needed: This bug may require changes across multiple layers. "
            "Consider splitting into multiple PRs. Start with the core fix, "
            "then address cascading changes in follow-up PRs."
        )

    if not analysis.relevant_files:
        analysis.warnings.append("No relevant files found. Try refining the bug description with more specific terms.")

    return analysis


def format_human(analysis: ScopeAnalysis) -> str:
    """Format results for human reading."""
    lines = []
    lines.append("=" * 65)
    lines.append("CHANGE SCOPE ANALYSIS")
    lines.append("=" * 65)
    lines.append(f"Bug: {analysis.bug_description}")
    lines.append(f"Keywords: {', '.join(analysis.extracted_keywords[:10])}")
    lines.append(f"Files scanned: {analysis.total_files_scanned}")
    lines.append("")
    lines.append(f"Scope: {analysis.scope_category.upper()}")
    lines.append(f"Risk: {analysis.risk_level}")
    lines.append(f"Estimated files to change: {analysis.estimated_total_files}")
    lines.append(f"Estimated lines to change: {analysis.estimated_total_lines}")
    lines.append("")
    lines.append(f"Recommended approach:")
    lines.append(f"  {analysis.recommended_approach}")
    lines.append("")

    if analysis.warnings:
        lines.append("Warnings:")
        for w in analysis.warnings:
            lines.append(f"  ! {w}")
        lines.append("")

    if analysis.relevant_files:
        lines.append("Relevant Files (by relevance):")
        lines.append("-" * 55)
        for i, f in enumerate(analysis.relevant_files, 1):
            lines.append(f"  {i}. [{f.confidence.upper():6s}] {f.file_path} (score: {f.relevance_score})")
            lines.append(f"     Keywords: {', '.join(f.matching_keywords[:5])}")
            lines.append(f"     Est. changes: ~{f.estimated_change_lines} lines")
            lines.append(f"     Reason: {f.reason}")
            if f.matching_lines:
                for ln, text in f.matching_lines[:2]:
                    lines.append(f"     L{ln}: {text}")
            lines.append("")

    lines.append("=" * 65)
    return "\n".join(lines)


def format_json(analysis: ScopeAnalysis) -> str:
    """Format results as JSON."""
    data = {
        "bug_description": analysis.bug_description,
        "extracted_keywords": analysis.extracted_keywords,
        "total_files_scanned": analysis.total_files_scanned,
        "scope_category": analysis.scope_category,
        "risk_level": analysis.risk_level,
        "estimated_total_files": analysis.estimated_total_files,
        "estimated_total_lines": analysis.estimated_total_lines,
        "recommended_approach": analysis.recommended_approach,
        "warnings": analysis.warnings,
        "relevant_files": [
            {
                "file_path": f.file_path,
                "relevance_score": f.relevance_score,
                "matching_keywords": f.matching_keywords,
                "estimated_change_lines": f.estimated_change_lines,
                "confidence": f.confidence,
                "reason": f.reason,
            }
            for f in analysis.relevant_files
        ],
    }
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Change Scope Analyzer - Identify minimal files to change for a bugfix"
    )
    parser.add_argument("--bug", required=True, help="Bug description text")
    parser.add_argument("--path", required=True, help="Path to codebase to analyze")
    parser.add_argument("--extensions", nargs="+",
                        help="File extensions to scan (e.g., .py .js .ts)")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    args = parser.parse_args()
    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    extensions = None
    if args.extensions:
        extensions = {ext if ext.startswith(".") else f".{ext}" for ext in args.extensions}

    analysis = analyze_scope(args.bug, path, extensions)

    if args.format == "json":
        print(format_json(analysis))
    else:
        print(format_human(analysis))


if __name__ == "__main__":
    main()
