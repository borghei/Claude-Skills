#!/usr/bin/env python3
"""
Documentation Staleness Scorer

Scores documentation freshness on a 0-100 scale using five weighted dimensions:
- Last Updated (20%): How recently the doc was modified
- Code-Doc Alignment (30%): Whether documented items still match code
- Link Health (15%): Percentage of links that resolve
- Completeness (20%): Whether expected sections exist
- Accuracy (15%): Version strings, file paths, verifiable facts

Usage:
    python doc_staleness_scorer.py /path/to/repo
    python doc_staleness_scorer.py /path/to/repo --json
    python doc_staleness_scorer.py /path/to/repo --threshold 60
    python doc_staleness_scorer.py /path/to/repo --readme-focus
    python doc_staleness_scorer.py /path/to/repo --required-sections "Installation,Usage,API"
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# --- Constants ---

DOC_EXTENSIONS = {".md", ".rst", ".txt", ".adoc"}
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".hpp", ".rb", ".php",
}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox", "dist", "build"}

DEFAULT_WEIGHTS = {
    "last_updated": 0.20,
    "code_doc_alignment": 0.30,
    "link_health": 0.15,
    "completeness": 0.20,
    "accuracy": 0.15,
}

DEFAULT_README_SECTIONS = [
    "installation", "usage", "api", "contributing", "license",
]

SCORE_LABELS = {
    (90, 101): "excellent",
    (70, 90): "good",
    (50, 70): "stale",
    (30, 50): "critical",
    (0, 30): "abandoned",
}


def get_label(score: float) -> str:
    for (low, high), label in SCORE_LABELS.items():
        if low <= score < high:
            return label
    return "unknown"


# --- Git Helpers ---

def run_git(repo_path: str, args: List[str], default: str = "") -> str:
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + args,
            capture_output=True, text=True, timeout=30,
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return default


def get_file_last_commit_date(repo_path: str, file_path: str) -> Optional[datetime]:
    output = run_git(repo_path, ["log", "-1", "--format=%aI", "--", file_path])
    if output:
        try:
            return datetime.fromisoformat(output)
        except ValueError:
            pass
    return None


def get_code_changes_since(repo_path: str, since_date: str, directory: str = "") -> int:
    args = ["log", "--since", since_date, "--oneline", "--", directory or "."]
    output = run_git(repo_path, args)
    return len([l for l in output.splitlines() if l.strip()]) if output else 0


def get_latest_tag(repo_path: str) -> Optional[str]:
    output = run_git(repo_path, ["describe", "--tags", "--abbrev=0"])
    return output.lstrip("v") if output else None


# --- File Discovery ---

def find_doc_files(repo_path: str) -> List[str]:
    doc_files = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if Path(f).suffix.lower() in DOC_EXTENSIONS:
                doc_files.append(os.path.relpath(os.path.join(root, f), repo_path))
    return sorted(doc_files)


# --- Scoring Dimensions ---

def score_last_updated(repo_path: str, doc_path: str) -> Tuple[float, Dict[str, Any]]:
    """Score based on how recently the doc was modified. 0-100."""
    last_modified = get_file_last_commit_date(repo_path, doc_path)
    details = {}

    if not last_modified:
        details["reason"] = "No git history found"
        return 50.0, details

    now = datetime.now(timezone.utc)
    if last_modified.tzinfo is None:
        last_modified = last_modified.replace(tzinfo=timezone.utc)

    days_ago = (now - last_modified).days
    details["last_modified"] = last_modified.strftime("%Y-%m-%d")
    details["days_ago"] = days_ago

    # Score: 100 if updated today, decays over time
    if days_ago <= 7:
        score = 100.0
    elif days_ago <= 30:
        score = 90.0 - (days_ago - 7) * 0.4
    elif days_ago <= 90:
        score = 80.0 - (days_ago - 30) * 0.5
    elif days_ago <= 180:
        score = 50.0 - (days_ago - 90) * 0.3
    elif days_ago <= 365:
        score = 25.0 - (days_ago - 180) * 0.1
    else:
        score = max(0.0, 10.0 - (days_ago - 365) * 0.02)

    return max(0.0, min(100.0, score)), details


def score_code_doc_alignment(repo_path: str, doc_path: str) -> Tuple[float, Dict[str, Any]]:
    """Score based on whether documented items still exist in code. 0-100."""
    full_path = os.path.join(repo_path, doc_path)
    details = {"referenced_files": 0, "existing_files": 0, "referenced_functions": 0}

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return 50.0, details

    # Extract file references
    file_refs = set()
    # Markdown links
    for match in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', content):
        target = match.group(2).split("#")[0]
        if not target.startswith(("http://", "https://", "mailto:")) and target:
            file_refs.add(target)
    # Backtick file references
    for match in re.finditer(r'`([^\s`]+\.\w{1,5})`', content):
        candidate = match.group(1)
        if Path(candidate).suffix.lower() in CODE_EXTENSIONS | DOC_EXTENSIONS:
            file_refs.add(candidate)

    if not file_refs:
        # No explicit references; check if associated code dir has changed
        doc_dir = os.path.dirname(doc_path)
        last_mod = get_file_last_commit_date(repo_path, doc_path)
        if last_mod:
            since = last_mod.strftime("%Y-%m-%d")
            changes = get_code_changes_since(repo_path, since, doc_dir)
            details["code_changes_since_update"] = changes
            if changes == 0:
                return 100.0, details
            elif changes < 5:
                return 80.0, details
            elif changes < 20:
                return 60.0, details
            else:
                return 40.0, details
        return 70.0, details

    # Check which referenced files exist
    doc_dir = os.path.dirname(doc_path)
    existing = 0
    for ref in file_refs:
        # Try relative to doc location
        resolved = os.path.normpath(os.path.join(repo_path, doc_dir, ref))
        if os.path.exists(resolved):
            existing += 1
            continue
        # Try relative to repo root
        resolved_root = os.path.normpath(os.path.join(repo_path, ref))
        if os.path.exists(resolved_root):
            existing += 1

    details["referenced_files"] = len(file_refs)
    details["existing_files"] = existing

    if len(file_refs) == 0:
        return 70.0, details

    ratio = existing / len(file_refs)
    return ratio * 100.0, details


def score_link_health(repo_path: str, doc_path: str) -> Tuple[float, Dict[str, Any]]:
    """Score based on percentage of valid internal links. 0-100."""
    full_path = os.path.join(repo_path, doc_path)
    details = {"total_links": 0, "valid_links": 0, "broken_links": []}

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return 100.0, details

    doc_dir = os.path.dirname(doc_path)

    # Extract markdown links
    links = []
    for match in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', content):
        target = match.group(2)
        if not target.startswith(("http://", "https://", "mailto:")):
            links.append(target)

    if not links:
        return 100.0, details

    details["total_links"] = len(links)
    valid = 0

    for link in links:
        anchor = None
        if "#" in link:
            file_part, anchor = link.split("#", 1)
        else:
            file_part = link

        if not file_part:
            # Anchor-only link within same doc
            if anchor:
                headings = _extract_headings(content)
                slug = _slugify(anchor)
                if slug in headings:
                    valid += 1
                else:
                    details["broken_links"].append(f"#{anchor}")
            else:
                valid += 1
            continue

        # Check file existence
        resolved = os.path.normpath(os.path.join(repo_path, doc_dir, file_part))
        if not os.path.exists(resolved):
            resolved = os.path.normpath(os.path.join(repo_path, file_part))

        if os.path.exists(resolved):
            if anchor and resolved.endswith((".md", ".rst")):
                # Validate anchor in target file
                try:
                    with open(resolved, "r", encoding="utf-8", errors="ignore") as f:
                        target_content = f.read()
                    headings = _extract_headings(target_content)
                    if _slugify(anchor) in headings:
                        valid += 1
                    else:
                        details["broken_links"].append(link)
                except (OSError, IOError):
                    valid += 1  # Give benefit of doubt
            else:
                valid += 1
        else:
            details["broken_links"].append(link)

    details["valid_links"] = valid
    if len(links) == 0:
        return 100.0, details
    return (valid / len(links)) * 100.0, details


def score_completeness(repo_path: str, doc_path: str, required_sections: List[str]) -> Tuple[float, Dict[str, Any]]:
    """Score based on whether expected sections are present. 0-100."""
    full_path = os.path.join(repo_path, doc_path)
    details = {"expected_sections": required_sections, "found_sections": [], "missing_sections": []}

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return 0.0, details

    # Extract headings
    headings_lower = set()
    for line in content.splitlines():
        match = re.match(r'^#{1,4}\s+(.+)', line)
        if match:
            headings_lower.add(match.group(1).strip().lower())

    # Also check heading words
    heading_words = set()
    for h in headings_lower:
        heading_words.update(h.split())

    found = []
    missing = []
    for section in required_sections:
        section_lower = section.lower()
        if section_lower in headings_lower or section_lower in heading_words:
            found.append(section)
        elif any(section_lower in h for h in headings_lower):
            found.append(section)
        else:
            missing.append(section)

    details["found_sections"] = found
    details["missing_sections"] = missing

    if not required_sections:
        return 100.0, details

    # Also score based on content length (very short docs are incomplete)
    content_lines = len([l for l in content.splitlines() if l.strip()])
    length_penalty = 0
    if content_lines < 10:
        length_penalty = 30
    elif content_lines < 30:
        length_penalty = 15

    section_score = (len(found) / len(required_sections)) * 100.0
    return max(0.0, section_score - length_penalty), details


def score_accuracy(repo_path: str, doc_path: str) -> Tuple[float, Dict[str, Any]]:
    """Score based on accuracy of verifiable facts (versions, dates, paths). 0-100."""
    full_path = os.path.join(repo_path, doc_path)
    details = {"checks": [], "issues": []}

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return 50.0, details

    checks_passed = 0
    checks_total = 0

    # Check 1: Version strings match latest tag
    git_version = get_latest_tag(repo_path)
    if git_version:
        version_refs = re.findall(r'(?:v|version[:\s]*)(\d+\.\d+(?:\.\d+)?)', content, re.IGNORECASE)
        if version_refs:
            checks_total += 1
            if any(v == git_version for v in version_refs):
                checks_passed += 1
                details["checks"].append("version_match: PASS")
            else:
                details["checks"].append(f"version_match: FAIL (doc has {version_refs}, git has {git_version})")
                details["issues"].append(f"Version mismatch: doc={version_refs}, git={git_version}")

    # Check 2: Package version from manifests
    for manifest in ["package.json", "pyproject.toml", "setup.py", "Cargo.toml"]:
        manifest_path = os.path.join(repo_path, manifest)
        if os.path.exists(manifest_path):
            manifest_version = _extract_version_from_manifest(manifest_path, manifest)
            if manifest_version:
                version_refs = re.findall(r'(?:v|version[:\s]*)(\d+\.\d+(?:\.\d+)?)', content, re.IGNORECASE)
                if version_refs:
                    checks_total += 1
                    if manifest_version in version_refs:
                        checks_passed += 1
                        details["checks"].append(f"manifest_version ({manifest}): PASS")
                    else:
                        details["checks"].append(
                            f"manifest_version ({manifest}): FAIL "
                            f"(doc={version_refs}, manifest={manifest_version})"
                        )
                        details["issues"].append(
                            f"Manifest version mismatch: {manifest} has {manifest_version}"
                        )

    # Check 3: Referenced file paths exist
    file_refs = re.findall(r'`([^\s`]+/[^\s`]+\.\w{1,5})`', content)
    if file_refs:
        doc_dir = os.path.dirname(doc_path)
        existing_count = 0
        for ref in file_refs:
            resolved = os.path.normpath(os.path.join(repo_path, doc_dir, ref))
            if os.path.exists(resolved):
                existing_count += 1
            else:
                resolved_root = os.path.normpath(os.path.join(repo_path, ref))
                if os.path.exists(resolved_root):
                    existing_count += 1
        checks_total += 1
        if len(file_refs) > 0 and existing_count == len(file_refs):
            checks_passed += 1
            details["checks"].append(f"file_paths: PASS ({existing_count}/{len(file_refs)})")
        else:
            ratio = existing_count / len(file_refs) if file_refs else 0
            # Partial credit
            checks_passed += ratio
            details["checks"].append(f"file_paths: PARTIAL ({existing_count}/{len(file_refs)})")
            details["issues"].append(f"{len(file_refs) - existing_count} referenced file paths not found")

    # Check 4: Dates are not in the future and not suspiciously old
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    dates_found = date_pattern.findall(content)
    if dates_found:
        checks_total += 1
        now = datetime.now(timezone.utc)
        all_ok = True
        for date_str in dates_found:
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if d > now:
                    details["issues"].append(f"Future date found: {date_str}")
                    all_ok = False
            except ValueError:
                pass
        if all_ok:
            checks_passed += 1
            details["checks"].append("dates: PASS")
        else:
            details["checks"].append("dates: FAIL")

    if checks_total == 0:
        return 75.0, details  # No verifiable facts found, assume reasonable

    return (checks_passed / checks_total) * 100.0, details


# --- Helpers ---

def _extract_headings(content: str) -> set:
    """Extract heading slugs from markdown content."""
    slugs = set()
    for line in content.splitlines():
        match = re.match(r'^#{1,6}\s+(.+)', line)
        if match:
            slugs.add(_slugify(match.group(1).strip()))
    return slugs


def _slugify(text: str) -> str:
    """Convert heading text to anchor slug (GitHub-style)."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    text = text.strip('-')
    return text


def _extract_version_from_manifest(path: str, filename: str) -> Optional[str]:
    """Extract version string from a package manifest."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return None

    if filename == "package.json":
        match = re.search(r'"version"\s*:\s*"([^"]+)"', content)
        return match.group(1) if match else None
    elif filename == "pyproject.toml":
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        return match.group(1) if match else None
    elif filename == "setup.py":
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        return match.group(1) if match else None
    elif filename == "Cargo.toml":
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        return match.group(1) if match else None
    return None


# --- Scoring Engine ---

def score_document(
    repo_path: str,
    doc_path: str,
    weights: Dict[str, float],
    required_sections: List[str],
) -> Dict[str, Any]:
    """Score a single documentation file across all dimensions."""
    updated_score, updated_details = score_last_updated(repo_path, doc_path)
    alignment_score, alignment_details = score_code_doc_alignment(repo_path, doc_path)
    link_score, link_details = score_link_health(repo_path, doc_path)
    completeness_score, completeness_details = score_completeness(repo_path, doc_path, required_sections)
    accuracy_score, accuracy_details = score_accuracy(repo_path, doc_path)

    weighted_total = (
        updated_score * weights["last_updated"]
        + alignment_score * weights["code_doc_alignment"]
        + link_score * weights["link_health"]
        + completeness_score * weights["completeness"]
        + accuracy_score * weights["accuracy"]
    )

    return {
        "file": doc_path,
        "total_score": round(weighted_total, 1),
        "label": get_label(weighted_total),
        "dimensions": {
            "last_updated": {
                "score": round(updated_score, 1),
                "weight": weights["last_updated"],
                "weighted": round(updated_score * weights["last_updated"], 1),
                "details": updated_details,
            },
            "code_doc_alignment": {
                "score": round(alignment_score, 1),
                "weight": weights["code_doc_alignment"],
                "weighted": round(alignment_score * weights["code_doc_alignment"], 1),
                "details": alignment_details,
            },
            "link_health": {
                "score": round(link_score, 1),
                "weight": weights["link_health"],
                "weighted": round(link_score * weights["link_health"], 1),
                "details": link_details,
            },
            "completeness": {
                "score": round(completeness_score, 1),
                "weight": weights["completeness"],
                "weighted": round(completeness_score * weights["completeness"], 1),
                "details": completeness_details,
            },
            "accuracy": {
                "score": round(accuracy_score, 1),
                "weight": weights["accuracy"],
                "weighted": round(accuracy_score * weights["accuracy"], 1),
                "details": accuracy_details,
            },
        },
    }


# --- Report ---

def generate_report(scores: List[Dict[str, Any]], as_json: bool = False) -> str:
    """Generate a staleness report from scored documents."""
    if not scores:
        if as_json:
            return json.dumps({"documents": [], "aggregate_score": 0}, indent=2)
        return "No documentation files found to score."

    aggregate = sum(s["total_score"] for s in scores) / len(scores)

    report_data = {
        "aggregate_score": round(aggregate, 1),
        "aggregate_label": get_label(aggregate),
        "total_documents": len(scores),
        "documents": scores,
    }

    if as_json:
        return json.dumps(report_data, indent=2, default=str)

    # Human-readable
    lines = []
    lines.append("Documentation Staleness Report")
    lines.append("=" * 60)
    lines.append(f"Aggregate Score: {aggregate:.1f}/100 ({get_label(aggregate)})")
    lines.append(f"Documents Scored: {len(scores)}")
    lines.append("")

    # Sort by score ascending (worst first)
    sorted_scores = sorted(scores, key=lambda s: s["total_score"])

    lines.append(f"{'File':<45} {'Score':>6} {'Label':>12}")
    lines.append("-" * 65)
    for s in sorted_scores:
        lines.append(f"{s['file']:<45} {s['total_score']:>5.1f} {s['label']:>12}")

    lines.append("")
    lines.append("DIMENSION BREAKDOWN (worst scoring files):")
    lines.append("-" * 60)

    # Show detailed breakdown for bottom 5
    for s in sorted_scores[:5]:
        lines.append(f"\n  {s['file']} (score: {s['total_score']:.1f})")
        for dim_name, dim_data in s["dimensions"].items():
            bar = _score_bar(dim_data["score"])
            lines.append(
                f"    {dim_name:<25} {dim_data['score']:>5.1f} "
                f"(x{dim_data['weight']:.2f} = {dim_data['weighted']:>5.1f}) {bar}"
            )

    lines.append("")
    return "\n".join(lines)


def _score_bar(score: float, width: int = 20) -> str:
    """Generate a simple ASCII bar for a score."""
    filled = int(score / 100 * width)
    return "[" + "#" * filled + "." * (width - filled) + "]"


# --- Main ---

def main():
    parser = argparse.ArgumentParser(
        description="Score documentation freshness on a 0-100 scale",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("repo_path", help="Path to the git repository")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--threshold", type=float, default=None,
        help="Fail (exit 1) if aggregate score is below this value",
    )
    parser.add_argument("--readme-focus", action="store_true", help="Only score README files")
    parser.add_argument(
        "--required-sections", default=None,
        help="Comma-separated required sections for completeness scoring",
    )
    parser.add_argument("--quiet", action="store_true", help="Only output score number")
    parser.add_argument("--weight-updated", type=float, default=None)
    parser.add_argument("--weight-alignment", type=float, default=None)
    parser.add_argument("--weight-links", type=float, default=None)
    parser.add_argument("--weight-completeness", type=float, default=None)
    parser.add_argument("--weight-accuracy", type=float, default=None)

    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo_path)
    if not os.path.isdir(repo_path):
        print(f"Error: {repo_path} is not a directory", file=sys.stderr)
        sys.exit(2)

    # Build weights
    weights = dict(DEFAULT_WEIGHTS)
    if args.weight_updated is not None:
        weights["last_updated"] = args.weight_updated
    if args.weight_alignment is not None:
        weights["code_doc_alignment"] = args.weight_alignment
    if args.weight_links is not None:
        weights["link_health"] = args.weight_links
    if args.weight_completeness is not None:
        weights["completeness"] = args.weight_completeness
    if args.weight_accuracy is not None:
        weights["accuracy"] = args.weight_accuracy

    # Normalize weights to sum to 1.0
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}

    # Required sections
    required_sections = DEFAULT_README_SECTIONS
    if args.required_sections:
        required_sections = [s.strip() for s in args.required_sections.split(",")]

    # Find docs
    doc_files = find_doc_files(repo_path)
    if args.readme_focus:
        doc_files = [d for d in doc_files if os.path.basename(d).lower().startswith("readme")]

    if not doc_files:
        if args.quiet:
            print("0")
        elif args.json:
            print(json.dumps({"error": "No documentation files found"}, indent=2))
        else:
            print("No documentation files found.")
        sys.exit(0)

    # Score each document
    scores = []
    for doc in doc_files:
        score = score_document(repo_path, doc, weights, required_sections)
        scores.append(score)

    aggregate = sum(s["total_score"] for s in scores) / len(scores) if scores else 0

    if args.quiet:
        print(f"{aggregate:.1f}")
    else:
        report = generate_report(scores, as_json=args.json)
        print(report)

    # Threshold check
    if args.threshold is not None and aggregate < args.threshold:
        if not args.quiet:
            print(
                f"\nFAILED: Aggregate score {aggregate:.1f} is below threshold {args.threshold}",
                file=sys.stderr,
            )
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
