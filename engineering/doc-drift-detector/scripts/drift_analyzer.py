#!/usr/bin/env python3
"""
Documentation Drift Analyzer

Compares git log of code changes against documentation file modification dates
to identify documentation that has fallen out of sync with the codebase.

Features:
- Maps code directories to their documentation files
- Detects renamed functions/files, moved directories, changed APIs
- Classifies drift by category and severity
- Outputs actionable drift reports with specific mismatches

Usage:
    python drift_analyzer.py /path/to/repo
    python drift_analyzer.py /path/to/repo --json
    python drift_analyzer.py /path/to/repo --min-severity high
    python drift_analyzer.py /path/to/repo --scope src/
    python drift_analyzer.py /path/to/repo --doc-patterns "*.md,*.rst"
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# --- Constants ---

DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc"}
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".hpp", ".rb", ".php", ".swift", ".kt",
    ".scala", ".sh", ".bash", ".zsh", ".yaml", ".yml", ".toml",
    ".json", ".xml", ".css", ".scss", ".html",
}
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
DRIFT_CATEGORIES = {"structural", "factual", "referential", "temporal", "semantic"}


# --- Git Helpers ---

def run_git(repo_path: str, args: List[str], default: str = "") -> str:
    """Run a git command and return stdout. Returns default on failure."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + args,
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return default
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return default


def get_file_last_modified(repo_path: str, file_path: str) -> Optional[datetime]:
    """Get the last git commit date for a file."""
    output = run_git(repo_path, [
        "log", "-1", "--format=%aI", "--", file_path
    ])
    if output:
        try:
            return datetime.fromisoformat(output)
        except ValueError:
            pass
    return None


def get_files_changed_since(repo_path: str, since_date: str, scope: str = "") -> List[Dict[str, str]]:
    """Get files changed since a given date, optionally scoped to a directory."""
    args = ["log", "--since", since_date, "--name-status", "--pretty=format:", "--diff-filter=ACDMRT"]
    if scope:
        args += ["--", scope]
    output = run_git(repo_path, args)
    changes = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0][0]  # First char: A, C, D, M, R, T
            filepath = parts[-1]
            changes.append({"status": status, "file": filepath})
    return changes


def get_renamed_files(repo_path: str, since_date: str) -> List[Tuple[str, str]]:
    """Get files that were renamed since a given date."""
    output = run_git(repo_path, [
        "log", "--since", since_date, "--name-status", "--pretty=format:",
        "--diff-filter=R", "-M"
    ])
    renames = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0].startswith("R"):
            renames.append((parts[1], parts[2]))
    return renames


def get_current_version_from_git(repo_path: str) -> Optional[str]:
    """Get the latest git tag as a version string."""
    output = run_git(repo_path, ["describe", "--tags", "--abbrev=0"])
    if output:
        return output.lstrip("v")
    return None


# --- File Discovery ---

def find_doc_files(repo_path: str, patterns: Optional[List[str]] = None) -> List[str]:
    """Find all documentation files in the repository."""
    doc_files = []
    repo = Path(repo_path)
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox", "dist", "build"}

    if patterns:
        extensions = set()
        for p in patterns:
            if p.startswith("*."):
                extensions.add(p[1:])
            elif p.startswith("."):
                extensions.add(p)
            else:
                extensions.add("." + p)
    else:
        extensions = DOC_EXTENSIONS

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if Path(f).suffix.lower() in extensions:
                rel_path = os.path.relpath(os.path.join(root, f), repo_path)
                doc_files.append(rel_path)
    return sorted(doc_files)


def find_code_files(repo_path: str, scope: str = "") -> List[str]:
    """Find all code files in the repository."""
    code_files = []
    search_path = os.path.join(repo_path, scope) if scope else repo_path
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox", "dist", "build"}

    if not os.path.isdir(search_path):
        return code_files

    for root, dirs, files in os.walk(search_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if Path(f).suffix.lower() in CODE_EXTENSIONS:
                rel_path = os.path.relpath(os.path.join(root, f), repo_path)
                code_files.append(rel_path)
    return sorted(code_files)


# --- Code-to-Doc Mapping ---

def map_docs_to_code(repo_path: str, doc_files: List[str], code_files: List[str]) -> Dict[str, List[str]]:
    """Map documentation files to the code directories they likely describe."""
    mapping = defaultdict(list)

    # Strategy 1: Directory proximity -- docs describe code in same or parent directory
    doc_dirs = {}
    for doc in doc_files:
        doc_dir = os.path.dirname(doc)
        doc_dirs[doc] = doc_dir

    code_dirs = set()
    for code in code_files:
        code_dirs.add(os.path.dirname(code))

    for doc, doc_dir in doc_dirs.items():
        # Check if there are code files in the same directory
        if doc_dir in code_dirs:
            mapping[doc].append(doc_dir)
        # Check parent directory
        parent = os.path.dirname(doc_dir)
        if parent in code_dirs:
            mapping[doc].append(parent)

    # Strategy 2: Content references -- docs that reference code file paths
    for doc in doc_files:
        doc_full = os.path.join(repo_path, doc)
        try:
            with open(doc_full, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except (OSError, IOError):
            continue

        for code in code_files:
            # Check if the code file path is mentioned in the doc
            code_basename = os.path.basename(code)
            if code_basename in content:
                code_dir = os.path.dirname(code)
                if code_dir and code_dir not in mapping[doc]:
                    mapping[doc].append(code_dir)

    # Strategy 3: Naming convention -- README in src/auth/ describes src/auth/
    for doc in doc_files:
        doc_lower = os.path.basename(doc).lower()
        if doc_lower in ("readme.md", "readme.rst", "readme.txt", "index.md"):
            doc_dir = os.path.dirname(doc)
            if doc_dir not in mapping[doc]:
                mapping[doc].append(doc_dir)

    return dict(mapping)


# --- Drift Detection ---

def extract_references_from_doc(repo_path: str, doc_path: str) -> Dict[str, Set[str]]:
    """Extract file references, function names, and version strings from a doc."""
    full_path = os.path.join(repo_path, doc_path)
    refs: Dict[str, Set[str]] = {
        "files": set(),
        "functions": set(),
        "versions": set(),
        "links": set(),
    }
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return refs

    # File references in markdown links
    link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
    for match in link_pattern.finditer(content):
        target = match.group(2)
        if not target.startswith(("http://", "https://", "mailto:", "#")):
            refs["files"].add(target.split("#")[0])
        refs["links"].add(target)

    # Function/method references in backticks
    func_pattern = re.compile(r'`(\w+(?:\.\w+)*)\(`')
    for match in func_pattern.finditer(content):
        refs["functions"].add(match.group(1))

    # Version strings
    version_pattern = re.compile(r'(?:v|version[:\s]*)(\d+\.\d+(?:\.\d+)?)', re.IGNORECASE)
    for match in version_pattern.finditer(content):
        refs["versions"].add(match.group(1))

    # Code block file references
    code_ref_pattern = re.compile(r'`([^\s`]+\.\w{1,5})`')
    for match in code_ref_pattern.finditer(content):
        candidate = match.group(1)
        if Path(candidate).suffix.lower() in CODE_EXTENSIONS:
            refs["files"].add(candidate)

    return refs


def detect_drift_for_doc(
    repo_path: str,
    doc_path: str,
    associated_code_dirs: List[str],
    renames: List[Tuple[str, str]],
    current_version: Optional[str],
) -> List[Dict[str, Any]]:
    """Detect drift issues for a single documentation file."""
    issues = []

    doc_modified = get_file_last_modified(repo_path, doc_path)
    if not doc_modified:
        issues.append({
            "file": doc_path,
            "severity": "info",
            "category": "temporal",
            "description": "Documentation file has no git history (untracked or new)",
            "fix_type": "manual",
        })
        return issues

    since_date = doc_modified.strftime("%Y-%m-%d")

    # Check code changes since doc was last updated
    total_code_changes = 0
    changed_dirs = set()
    for code_dir in associated_code_dirs:
        changes = get_files_changed_since(repo_path, since_date, code_dir)
        code_changes = [c for c in changes if Path(c["file"]).suffix.lower() in CODE_EXTENSIONS]
        total_code_changes += len(code_changes)
        if code_changes:
            changed_dirs.add(code_dir)

    if total_code_changes > 20:
        issues.append({
            "file": doc_path,
            "severity": "high",
            "category": "factual",
            "description": f"{total_code_changes} code files changed in associated directories since doc was last updated",
            "fix_type": "manual",
            "details": {"changed_dirs": list(changed_dirs), "change_count": total_code_changes},
        })
    elif total_code_changes > 5:
        issues.append({
            "file": doc_path,
            "severity": "medium",
            "category": "factual",
            "description": f"{total_code_changes} code files changed since doc update",
            "fix_type": "semi",
            "details": {"changed_dirs": list(changed_dirs), "change_count": total_code_changes},
        })
    elif total_code_changes > 0:
        issues.append({
            "file": doc_path,
            "severity": "low",
            "category": "factual",
            "description": f"{total_code_changes} code files changed since doc update",
            "fix_type": "semi",
            "details": {"changed_dirs": list(changed_dirs), "change_count": total_code_changes},
        })

    # Check for renamed files referenced in the doc
    refs = extract_references_from_doc(repo_path, doc_path)
    for old_name, new_name in renames:
        old_base = os.path.basename(old_name)
        if old_base in {os.path.basename(r) for r in refs["files"]}:
            issues.append({
                "file": doc_path,
                "severity": "high",
                "category": "referential",
                "description": f"References '{old_base}' which was renamed to '{os.path.basename(new_name)}'",
                "fix_type": "auto",
                "details": {"old_path": old_name, "new_path": new_name},
            })

    # Check for broken file references
    for ref_file in refs["files"]:
        # Resolve relative to doc's directory
        doc_dir = os.path.dirname(doc_path)
        resolved = os.path.normpath(os.path.join(repo_path, doc_dir, ref_file))
        if not os.path.exists(resolved):
            # Also try from repo root
            resolved_root = os.path.normpath(os.path.join(repo_path, ref_file))
            if not os.path.exists(resolved_root):
                issues.append({
                    "file": doc_path,
                    "severity": "medium",
                    "category": "referential",
                    "description": f"References non-existent file: {ref_file}",
                    "fix_type": "auto",
                })

    # Check version string drift
    if current_version and refs["versions"]:
        for doc_version in refs["versions"]:
            if doc_version != current_version and _version_is_older(doc_version, current_version):
                issues.append({
                    "file": doc_path,
                    "severity": "medium",
                    "category": "temporal",
                    "description": f"References version {doc_version}, current is {current_version}",
                    "fix_type": "auto",
                    "details": {"doc_version": doc_version, "current_version": current_version},
                })

    # Check temporal staleness (days since update)
    now = datetime.now(timezone.utc)
    # Normalize both datetimes to UTC-aware for safe comparison
    if doc_modified.tzinfo is None:
        doc_modified_utc = doc_modified.replace(tzinfo=timezone.utc)
    else:
        doc_modified_utc = doc_modified.astimezone(timezone.utc)
    days_since = (now - doc_modified_utc).days
    if days_since > 180:
        issues.append({
            "file": doc_path,
            "severity": "medium",
            "category": "temporal",
            "description": f"Documentation not updated in {days_since} days",
            "fix_type": "manual",
            "details": {"days_since_update": days_since, "last_updated": since_date},
        })
    elif days_since > 365:
        issues.append({
            "file": doc_path,
            "severity": "high",
            "category": "temporal",
            "description": f"Documentation not updated in {days_since} days",
            "fix_type": "manual",
            "details": {"days_since_update": days_since, "last_updated": since_date},
        })

    # Check structural completeness for README files
    if os.path.basename(doc_path).lower().startswith("readme"):
        structural_issues = check_readme_structure(repo_path, doc_path)
        issues.extend(structural_issues)

    return issues


def check_readme_structure(repo_path: str, doc_path: str) -> List[Dict[str, Any]]:
    """Check if a README has expected sections."""
    issues = []
    full_path = os.path.join(repo_path, doc_path)
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return issues

    headings = set()
    for line in content.splitlines():
        match = re.match(r'^#{1,3}\s+(.+)', line)
        if match:
            headings.add(match.group(1).strip().lower())

    expected = {"installation", "usage", "license"}
    heading_words = set()
    for h in headings:
        heading_words.update(h.split())

    for section in expected:
        if section not in heading_words and section not in headings:
            # Check partial matches
            found = any(section in h for h in headings)
            if not found:
                issues.append({
                    "file": doc_path,
                    "severity": "low",
                    "category": "structural",
                    "description": f"README missing recommended section: {section.title()}",
                    "fix_type": "manual",
                })

    return issues


def _parse_version_part(part: str) -> int:
    """Extract numeric value from a version part, stripping pre-release tags."""
    # Strip pre-release suffixes like alpha, beta, rc
    cleaned = re.sub(r'[^0-9].*$', '', part)
    try:
        return int(cleaned) if cleaned else 0
    except ValueError:
        return 0


def _version_is_older(v1: str, v2: str) -> bool:
    """Check if v1 is older than v2 using semantic version comparison.

    Handles versions like '1.10.0', '2.0.0-alpha', '1.2.3-rc.1'.
    """
    try:
        parts1 = [_parse_version_part(x) for x in v1.split(".")]
        parts2 = [_parse_version_part(x) for x in v2.split(".")]
        # Pad to same length
        max_len = max(len(parts1), len(parts2))
        while len(parts1) < max_len:
            parts1.append(0)
        while len(parts2) < max_len:
            parts2.append(0)
        return tuple(parts1) < tuple(parts2)
    except (ValueError, AttributeError, TypeError):
        return False


# --- Semantic Drift Detection ---

def detect_semantic_drift(repo_path: str, doc_path: str, associated_code_dirs: List[str]) -> List[Dict[str, Any]]:
    """Detect when documentation scope hasn't kept up with code growth."""
    issues = []

    full_path = os.path.join(repo_path, doc_path)
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            doc_content = f.read()
    except (OSError, IOError):
        return issues

    doc_lines = len(doc_content.splitlines())

    # Count code files and directories in associated dirs
    total_code_files = 0
    code_subdirs = set()
    for code_dir in associated_code_dirs:
        full_code_dir = os.path.join(repo_path, code_dir) if code_dir else repo_path
        if not os.path.isdir(full_code_dir):
            continue
        for root, dirs, files in os.walk(full_code_dir):
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".venv"}]
            for f in files:
                if Path(f).suffix.lower() in CODE_EXTENSIONS:
                    total_code_files += 1
            for d in dirs:
                code_subdirs.add(os.path.relpath(os.path.join(root, d), repo_path))

    # Heuristic: if code has many subdirectories but doc is small, flag semantic drift
    if len(code_subdirs) > 10 and doc_lines < 50:
        issues.append({
            "file": doc_path,
            "severity": "medium",
            "category": "semantic",
            "description": (
                f"Documentation is {doc_lines} lines but describes code with "
                f"{len(code_subdirs)} subdirectories and {total_code_files} files"
            ),
            "fix_type": "manual",
            "details": {
                "doc_lines": doc_lines,
                "code_subdirs": len(code_subdirs),
                "code_files": total_code_files,
            },
        })

    # Check if major code directories are mentioned in the doc
    for subdir in code_subdirs:
        dirname = os.path.basename(subdir)
        if len(dirname) > 2 and dirname not in doc_content:
            # Only flag top-level subdirectories of the associated code dir
            parts = subdir.split(os.sep)
            if len(parts) <= 2:
                issues.append({
                    "file": doc_path,
                    "severity": "low",
                    "category": "semantic",
                    "description": f"Code directory '{subdir}' not mentioned in documentation",
                    "fix_type": "manual",
                })

    return issues


# --- Report Generation ---

def generate_report(
    repo_path: str,
    all_issues: List[Dict[str, Any]],
    doc_files: List[str],
    as_json: bool = False,
) -> str:
    """Generate a drift report."""
    # Sort by severity
    all_issues.sort(key=lambda x: SEVERITY_ORDER.get(x.get("severity", "info"), 99))

    drifted_files = set(i["file"] for i in all_issues if i["severity"] != "info")

    report_data = {
        "repository": os.path.abspath(repo_path),
        "scan_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "total_docs": len(doc_files),
            "drifted_docs": len(drifted_files),
            "total_issues": len(all_issues),
            "by_severity": {},
            "by_category": {},
            "by_fix_type": {},
        },
        "issues": all_issues,
    }

    for issue in all_issues:
        sev = issue.get("severity", "info")
        cat = issue.get("category", "unknown")
        fix = issue.get("fix_type", "manual")
        report_data["summary"]["by_severity"][sev] = report_data["summary"]["by_severity"].get(sev, 0) + 1
        report_data["summary"]["by_category"][cat] = report_data["summary"]["by_category"].get(cat, 0) + 1
        report_data["summary"]["by_fix_type"][fix] = report_data["summary"]["by_fix_type"].get(fix, 0) + 1

    if as_json:
        return json.dumps(report_data, indent=2, default=str)

    # Human-readable report
    lines = []
    lines.append("Documentation Drift Report")
    lines.append("=" * 60)
    lines.append(f"Repository: {os.path.abspath(repo_path)}")
    lines.append(f"Scan date:  {report_data['scan_date']}")
    lines.append(f"Docs found: {len(doc_files)}")
    lines.append(f"Drifted:    {len(drifted_files)}")
    lines.append(f"Issues:     {len(all_issues)}")
    lines.append("")

    severity_groups = defaultdict(list)
    for issue in all_issues:
        severity_groups[issue["severity"]].append(issue)

    for severity in ["critical", "high", "medium", "low", "info"]:
        group = severity_groups.get(severity, [])
        if not group:
            continue
        lines.append(f"{severity.upper()} SEVERITY ({len(group)} issues):")
        lines.append("-" * 40)
        for issue in group:
            fix_tag = {"auto": "[AUTO]", "semi": "[SEMI]", "manual": "[MANUAL]"}.get(
                issue.get("fix_type", "manual"), "[MANUAL]"
            )
            lines.append(f"  {issue['file']}")
            lines.append(f"    {fix_tag} {issue['description']}")
            lines.append(f"    Category: {issue.get('category', 'unknown')}")
            lines.append("")
        lines.append("")

    # Summary
    lines.append("FIX TYPE SUMMARY:")
    lines.append("-" * 40)
    for fix_type, count in sorted(report_data["summary"]["by_fix_type"].items()):
        label = {"auto": "Auto-fixable", "semi": "Semi-automated", "manual": "Manual review"}.get(fix_type, fix_type)
        lines.append(f"  {label}: {count}")
    lines.append("")

    if not all_issues:
        lines.append("No documentation drift detected. All docs appear current.")

    return "\n".join(lines)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Analyze documentation drift in a git repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/repo
  %(prog)s /path/to/repo --json
  %(prog)s /path/to/repo --min-severity high
  %(prog)s /path/to/repo --scope src/
  %(prog)s /path/to/repo --doc-patterns "*.md,*.rst"
        """,
    )
    parser.add_argument("repo_path", help="Path to the git repository")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--min-severity",
        choices=["critical", "high", "medium", "low", "info"],
        default="low",
        help="Minimum severity to report (default: low)",
    )
    parser.add_argument("--scope", default="", help="Limit code analysis to a subdirectory")
    parser.add_argument(
        "--doc-patterns",
        default=None,
        help="Comma-separated doc file patterns (default: *.md,*.rst,*.txt,*.adoc)",
    )

    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo_path)
    if not os.path.isdir(repo_path):
        print(f"Error: {repo_path} is not a directory", file=sys.stderr)
        sys.exit(2)

    # Verify it's a git repo
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        print(f"Error: {repo_path} is not a git repository", file=sys.stderr)
        sys.exit(2)

    # Parse doc patterns
    patterns = None
    if args.doc_patterns:
        patterns = [p.strip() for p in args.doc_patterns.split(",")]

    # Discovery
    doc_files = find_doc_files(repo_path, patterns)
    code_files = find_code_files(repo_path, args.scope)

    if not doc_files:
        if args.json:
            print(json.dumps({"error": "No documentation files found"}, indent=2))
        else:
            print("No documentation files found in the repository.")
        sys.exit(0)

    # Map docs to code
    doc_code_map = map_docs_to_code(repo_path, doc_files, code_files)

    # Get renames from last 90 days
    renames = get_renamed_files(repo_path, "90 days ago")

    # Get current version
    current_version = get_current_version_from_git(repo_path)

    # Detect drift for each doc
    all_issues = []
    for doc in doc_files:
        associated_dirs = doc_code_map.get(doc, [])
        if not associated_dirs:
            # Default: associate with repo root
            associated_dirs = [""]

        issues = detect_drift_for_doc(repo_path, doc, associated_dirs, renames, current_version)
        semantic_issues = detect_semantic_drift(repo_path, doc, associated_dirs)
        issues.extend(semantic_issues)
        all_issues.extend(issues)

    # Filter by severity
    min_sev = SEVERITY_ORDER.get(args.min_severity, 3)
    filtered = [i for i in all_issues if SEVERITY_ORDER.get(i.get("severity", "info"), 99) <= min_sev]

    # Report
    report = generate_report(repo_path, filtered, doc_files, as_json=args.json)
    print(report)

    # Exit code: 1 if high/critical issues found, 0 otherwise
    has_serious = any(
        i["severity"] in ("critical", "high") for i in filtered
    )
    sys.exit(1 if has_serious else 0)


if __name__ == "__main__":
    main()
