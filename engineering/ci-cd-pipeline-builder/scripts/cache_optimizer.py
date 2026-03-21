#!/usr/bin/env python3
"""Analyze CI/CD pipeline configs and suggest caching improvements.

Reads GitHub Actions or GitLab CI YAML files and identifies missing
caches, suboptimal cache keys, redundant installs across jobs, and
opportunities to use built-in caching features.

Usage:
    python cache_optimizer.py .github/workflows/ci.yml
    python cache_optimizer.py .gitlab-ci.yml --json
    python cache_optimizer.py --dir .github/workflows/
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Known cache strategies
# ---------------------------------------------------------------------------

GITHUB_CACHE_STRATEGIES = {
    "npm": {
        "preferred": "cache: 'npm' in actions/setup-node",
        "cache_path": "~/.npm",
        "key_pattern": "hashFiles('**/package-lock.json')",
        "lockfile": "package-lock.json",
    },
    "pnpm": {
        "preferred": "cache: 'pnpm' in actions/setup-node (with pnpm/action-setup)",
        "cache_path": "detected by setup-node",
        "key_pattern": "hashFiles('**/pnpm-lock.yaml')",
        "lockfile": "pnpm-lock.yaml",
    },
    "yarn": {
        "preferred": "cache: 'yarn' in actions/setup-node",
        "cache_path": "~/.cache/yarn",
        "key_pattern": "hashFiles('**/yarn.lock')",
        "lockfile": "yarn.lock",
    },
    "pip": {
        "preferred": "cache: 'pip' in actions/setup-python",
        "cache_path": "~/.cache/pip",
        "key_pattern": "hashFiles('**/requirements*.txt')",
        "lockfile": "requirements.txt",
    },
    "uv": {
        "preferred": "Built-in caching via astral-sh/setup-uv",
        "cache_path": "~/.cache/uv",
        "key_pattern": "hashFiles('**/uv.lock')",
        "lockfile": "uv.lock",
    },
    "go": {
        "preferred": "Built-in caching via actions/setup-go (cache: true)",
        "cache_path": "~/go/pkg/mod",
        "key_pattern": "hashFiles('**/go.sum')",
        "lockfile": "go.sum",
    },
    "cargo": {
        "preferred": "actions/cache with Cargo.lock hash key",
        "cache_path": "~/.cargo/registry, ~/.cargo/git, target/",
        "key_pattern": "hashFiles('**/Cargo.lock')",
        "lockfile": "Cargo.lock",
    },
}

# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"


def detect_platform(filepath, text):
    """Determine CI platform from path and content."""
    if ".github" in filepath or "runs-on:" in text:
        return "github-actions"
    if ".gitlab-ci" in os.path.basename(filepath) or ("stages:" in text and "script:" in text):
        return "gitlab-ci"
    return "unknown"


def detect_package_managers(text):
    """Detect which package managers are referenced in the pipeline."""
    found = set()
    indicators = {
        "npm": [r'\bnpm\s+(ci|install)\b', r'package-lock\.json'],
        "pnpm": [r'\bpnpm\s+install\b', r'pnpm-lock\.yaml'],
        "yarn": [r'\byarn\s+install\b', r'yarn\.lock'],
        "pip": [r'\bpip\s+install\b', r'requirements.*\.txt'],
        "uv": [r'\buv\s+(sync|install)\b', r'uv\.lock'],
        "poetry": [r'\bpoetry\s+install\b', r'poetry\.lock'],
        "go": [r'\bgo\s+(build|test|vet)\b', r'go\.sum'],
        "cargo": [r'\bcargo\s+(build|test)\b', r'Cargo\.lock'],
    }
    for pm, patterns in indicators.items():
        for pat in patterns:
            if re.search(pat, text):
                found.add(pm)
                break
    return found


def check_missing_cache(text, platform, package_managers):
    """Identify package managers used without any caching."""
    suggestions = []
    for pm in package_managers:
        strategy = GITHUB_CACHE_STRATEGIES.get(pm)
        if not strategy:
            continue

        has_cache = False
        # Check for setup-node/setup-python cache param
        if pm in ("npm", "pnpm", "yarn") and re.search(r"cache:\s*['\"]?" + pm, text):
            has_cache = True
        if pm == "pip" and re.search(r"cache:\s*['\"]?pip", text):
            has_cache = True
        if pm == "uv" and "setup-uv" in text:
            has_cache = True
        if pm == "go" and "setup-go" in text:
            has_cache = True
        # Check for explicit actions/cache
        if re.search(r"actions/cache", text) and strategy["lockfile"] in text:
            has_cache = True
        # GitLab cache block
        if platform == "gitlab-ci" and "cache:" in text:
            has_cache = True

        if not has_cache:
            suggestions.append({
                "type": "missing-cache",
                "severity": SEVERITY_HIGH,
                "package_manager": pm,
                "message": f"No caching detected for {pm}. Dependencies are re-downloaded on every run.",
                "recommendation": strategy["preferred"],
                "estimated_savings": "30-120 seconds per job",
            })

    return suggestions


def check_cache_key_quality(text, platform):
    """Check for suboptimal cache key patterns."""
    suggestions = []

    if platform == "github-actions":
        # Check for cache keys without hashFiles
        cache_key_lines = re.findall(r'key:\s*(.+)', text)
        for key_expr in cache_key_lines:
            if "hashFiles" not in key_expr and "github.sha" in key_expr:
                suggestions.append({
                    "type": "volatile-cache-key",
                    "severity": SEVERITY_HIGH,
                    "message": "Cache key uses github.sha which changes every commit, causing 0% hit rate.",
                    "recommendation": "Use hashFiles('**/lockfile') for dependency caches.",
                    "estimated_savings": "30-120 seconds per job",
                })
            if "hashFiles" not in key_expr and "${{" not in key_expr and key_expr.strip().strip("'\""):
                # Static string key - always same, never invalidated
                suggestions.append({
                    "type": "static-cache-key",
                    "severity": SEVERITY_MEDIUM,
                    "message": f"Cache key appears static: {key_expr.strip()[:60]}. Cache never invalidates.",
                    "recommendation": "Include hashFiles() of your lockfile so cache refreshes on dependency changes.",
                    "estimated_savings": "Prevents stale dependency bugs",
                })

    if platform == "gitlab-ci":
        cache_key_lines = re.findall(r'key:\s*(.+)', text)
        for key_expr in cache_key_lines:
            if "$CI_COMMIT_SHA" in key_expr:
                suggestions.append({
                    "type": "volatile-cache-key",
                    "severity": SEVERITY_HIGH,
                    "message": "Cache key uses $CI_COMMIT_SHA which changes every commit.",
                    "recommendation": "Use $CI_COMMIT_REF_SLUG or Files(['lockfile']) for dependency caches.",
                    "estimated_savings": "30-120 seconds per job",
                })

    return suggestions


def check_redundant_installs(text, platform):
    """Detect when multiple jobs repeat the same install step without shared cache."""
    suggestions = []

    if platform == "github-actions":
        install_patterns = [
            (r'npm ci', "npm ci"),
            (r'pnpm install', "pnpm install"),
            (r'yarn install', "yarn install"),
            (r'pip install -r', "pip install"),
            (r'uv sync', "uv sync"),
        ]
        for pat, label in install_patterns:
            matches = re.findall(pat, text)
            if len(matches) > 2:
                suggestions.append({
                    "type": "redundant-install",
                    "severity": SEVERITY_MEDIUM,
                    "message": f"'{label}' appears {len(matches)} times across jobs.",
                    "recommendation": (
                        "Ensure caching is enabled so repeated installs are fast. "
                        "Consider a dedicated setup job with artifact passing for large dependency trees."
                    ),
                    "estimated_savings": f"{(len(matches) - 1) * 20}-{(len(matches) - 1) * 60} seconds total",
                })

    return suggestions


def check_docker_cache(text, platform):
    """Check if Docker builds use layer caching."""
    suggestions = []
    if "docker" not in text.lower() and "buildx" not in text.lower():
        return suggestions

    has_docker_build = bool(re.search(r'docker\s+build\b', text))
    has_buildx = "docker/build-push-action" in text or "buildx" in text
    has_cache_from = "cache-from" in text

    if has_docker_build and not has_buildx:
        suggestions.append({
            "type": "no-buildx",
            "severity": SEVERITY_MEDIUM,
            "message": "Using 'docker build' without BuildKit/Buildx. No layer caching between runs.",
            "recommendation": "Switch to docker/build-push-action with cache-from: type=gha, cache-to: type=gha,mode=max",
            "estimated_savings": "1-10 minutes per build depending on image size",
        })
    elif has_buildx and not has_cache_from:
        suggestions.append({
            "type": "buildx-no-cache",
            "severity": SEVERITY_HIGH,
            "message": "Using Buildx but no cache-from/cache-to configured. Docker layers rebuild from scratch.",
            "recommendation": "Add cache-from: type=gha and cache-to: type=gha,mode=max to build-push-action",
            "estimated_savings": "1-10 minutes per build depending on image size",
        })

    return suggestions


def check_missing_restore_keys(text, platform):
    """Suggest restore-keys for graceful cache fallback."""
    suggestions = []
    if platform != "github-actions":
        return suggestions

    if "actions/cache" in text and "restore-keys" not in text:
        suggestions.append({
            "type": "missing-restore-keys",
            "severity": SEVERITY_LOW,
            "message": "actions/cache used without restore-keys. Cache miss when lockfile changes means full re-download.",
            "recommendation": (
                "Add restore-keys with a prefix fallback, e.g.:\n"
                "  restore-keys: |\n"
                "    ${{ runner.os }}-npm-\n"
                "This allows partial cache hits when only some deps change."
            ),
            "estimated_savings": "10-60 seconds on lockfile changes",
        })

    return suggestions


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

ALL_CHECKS = [
    check_missing_cache,
    check_cache_key_quality,
    check_redundant_installs,
    check_docker_cache,
    check_missing_restore_keys,
]


def analyze_file(filepath):
    """Run all cache optimization checks on a single pipeline file."""
    filepath = str(filepath)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as exc:
        return {
            "file": filepath,
            "platform": "unknown",
            "package_managers": [],
            "suggestions": [{
                "type": "file-read-error",
                "severity": SEVERITY_HIGH,
                "message": str(exc),
            }],
        }

    platform = detect_platform(filepath, text)
    package_managers = sorted(detect_package_managers(text))
    suggestions = []

    for check_fn in ALL_CHECKS:
        if check_fn == check_missing_cache:
            suggestions.extend(check_fn(text, platform, package_managers))
        elif check_fn in (check_cache_key_quality, check_redundant_installs,
                          check_docker_cache, check_missing_restore_keys):
            suggestions.extend(check_fn(text, platform))

    # Sort: high first
    severity_order = {SEVERITY_HIGH: 0, SEVERITY_MEDIUM: 1, SEVERITY_LOW: 2}
    suggestions.sort(key=lambda s: severity_order.get(s["severity"], 9))

    return {
        "file": filepath,
        "platform": platform,
        "package_managers": package_managers,
        "suggestions": suggestions,
    }


def collect_files(path):
    """Collect YAML files from a file path or directory."""
    p = Path(path)
    if p.is_file():
        return [p]
    if p.is_dir():
        return sorted(p.glob("**/*.yml")) + sorted(p.glob("**/*.yaml"))
    return []


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

_SEVERITY_BADGE = {
    SEVERITY_HIGH: "HIGH",
    SEVERITY_MEDIUM: "MED ",
    SEVERITY_LOW: "LOW ",
}


def format_human(results):
    """Return human-readable optimization report."""
    lines = []
    total_suggestions = 0

    for result in results:
        lines.append(f"\n=== {result['file']} ===")
        lines.append(f"Platform: {result['platform']}")
        lines.append(f"Package managers detected: {', '.join(result['package_managers']) or 'none'}")

        if not result["suggestions"]:
            lines.append("\n  No optimization suggestions. Caching looks good!")
            continue

        lines.append("")
        for idx, s in enumerate(result["suggestions"], 1):
            badge = _SEVERITY_BADGE.get(s["severity"], "????")
            lines.append(f"  [{badge}] {idx}. {s['type']}")
            lines.append(f"         {s['message']}")
            if "recommendation" in s:
                for rec_line in s["recommendation"].split("\n"):
                    lines.append(f"         -> {rec_line}")
            if "estimated_savings" in s:
                lines.append(f"         Estimated savings: {s['estimated_savings']}")
            lines.append("")
            total_suggestions += 1

    lines.append(f"Total suggestions: {total_suggestions}")
    high_count = sum(
        1 for r in results for s in r["suggestions"] if s["severity"] == SEVERITY_HIGH
    )
    if high_count:
        lines.append(f"High-priority items: {high_count}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Analyze CI/CD pipeline configs and suggest caching improvements.",
        epilog="Examples:\n"
               "  %(prog)s .github/workflows/ci.yml\n"
               "  %(prog)s --dir .github/workflows/ --json\n"
               "  %(prog)s .gitlab-ci.yml --severity high",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("files", nargs="*", help="Pipeline YAML files to analyze")
    parser.add_argument("--dir", help="Directory to scan recursively for YAML files")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")
    parser.add_argument("--severity", choices=["high", "medium", "low"],
                        default="low",
                        help="Minimum severity to report (default: low)")
    args = parser.parse_args()

    files_to_analyze = []
    for f in (args.files or []):
        files_to_analyze.extend(collect_files(f))
    if args.dir:
        files_to_analyze.extend(collect_files(args.dir))

    if not files_to_analyze:
        parser.error("No files provided. Pass YAML files or use --dir.")

    severity_rank = {"high": 3, "medium": 2, "low": 1}
    min_rank = severity_rank[args.severity]

    results = []
    for fpath in files_to_analyze:
        result = analyze_file(fpath)
        result["suggestions"] = [
            s for s in result["suggestions"]
            if severity_rank.get(s["severity"], 0) >= min_rank
        ]
        results.append(result)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    has_high = any(
        s["severity"] == SEVERITY_HIGH
        for r in results for s in r["suggestions"]
    )
    sys.exit(1 if has_high else 0)


if __name__ == "__main__":
    main()
