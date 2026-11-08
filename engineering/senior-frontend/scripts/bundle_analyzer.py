#!/usr/bin/env python3
"""
Frontend Bundle Analyzer

Analyzes package.json and project structure for bundle optimization opportunities,
heavy dependencies, and best practice recommendations.

Usage:
    python bundle_analyzer.py . --json
    python bundle_analyzer.py /path/to/project --verbose --format json
    python bundle_analyzer.py /path/to/project --min-score 70   # CI gate

Rule tables live in references/bundle_rules.json.
Exit codes: 0 ok, 1 score below --min-score (only when the flag is given),
2 bad input (missing directory, no valid package.json, unreadable rules).
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


RULES_PATH = Path(__file__).resolve().parent.parent / "references" / "bundle_rules.json"

try:
    with open(RULES_PATH, encoding="utf-8") as _f:
        RULES = json.load(_f)
except (OSError, json.JSONDecodeError) as _exc:
    print(f"Error: cannot load rules from {RULES_PATH}: {_exc}", file=sys.stderr)
    sys.exit(2)

# Known heavy packages and their lighter alternatives
HEAVY_PACKAGES: Dict[str, Dict[str, str]] = RULES["heavy_packages"]
# Recommended optimizations by package
PACKAGE_OPTIMIZATIONS: Dict[str, str] = RULES["package_optimizations"]
# Development dependencies that should not be in dependencies
DEV_ONLY_PACKAGES: List[str] = RULES["dev_only_packages"]
STATE_LIBS: List[str] = RULES["state_libs"]
IMPORT_PATTERNS: List[Tuple[str, str]] = [tuple(p) for p in RULES["import_patterns"]]


def load_package_json(project_dir: Path) -> Optional[Dict]:
    """Load and parse package.json."""
    package_path = project_dir / "package.json"
    if not package_path.exists():
        return None

    try:
        with open(package_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None


def analyze_dependencies(package_json: Dict) -> Dict:
    """Analyze dependencies for issues."""
    deps = package_json.get("dependencies", {})
    dev_deps = package_json.get("devDependencies", {})

    issues = []
    warnings = []
    optimizations = []

    # Check for heavy packages
    for pkg, info in HEAVY_PACKAGES.items():
        if pkg in deps:
            issues.append({"package": pkg, "type": "heavy_dependency", "size": info["size"],
                           "alternative": info["alternative"], "reason": info["reason"]})

    # Check for dev dependencies in production
    for pkg in deps.keys():
        for dev_pattern in DEV_ONLY_PACKAGES:
            if dev_pattern in pkg:
                warnings.append({"package": pkg, "type": "dev_in_production",
                                 "message": f"{pkg} should be in devDependencies, not dependencies"})

    # Check for optimization opportunities
    for pkg in deps.keys():
        for opt_pkg, opt_tip in PACKAGE_OPTIMIZATIONS.items():
            if opt_pkg in pkg:
                optimizations.append({"package": pkg, "tip": opt_tip})

    # Check for outdated React patterns
    if "prop-types" in deps and ("typescript" in dev_deps or "@types/react" in dev_deps):
        warnings.append({"package": "prop-types", "type": "redundant",
                         "message": "prop-types is redundant when using TypeScript"})

    # Check for multiple state management libraries
    found_state_libs = [lib for lib in STATE_LIBS if lib in deps]
    if len(found_state_libs) > 1:
        warnings.append({"packages": found_state_libs, "type": "multiple_state_libs",
                         "message": f"Multiple state management libraries found: {', '.join(found_state_libs)}"})

    return {
        "total_dependencies": len(deps),
        "total_dev_dependencies": len(dev_deps),
        "issues": issues,
        "warnings": warnings,
        "optimizations": optimizations
    }


def detect_framework(package_json: Dict) -> str:
    """Return 'next', 'vite' or 'other' from the declared dependencies."""
    declared = {**package_json.get("devDependencies", {}), **package_json.get("dependencies", {})}
    return "next" if "next" in declared else "vite" if "vite" in declared else "other"


def check_nextjs_config(project_dir: Path) -> Dict:
    """Check Next.js configuration for optimizations."""
    config_paths = [project_dir / f"next.config.{ext}" for ext in ("js", "mjs", "ts")]

    for config_path in config_paths:
        if config_path.exists():
            try:
                content = config_path.read_text()
                suggestions = []
                if "images" not in content:
                    suggestions.append("Configure images.remotePatterns for optimized image loading")
                if "optimizePackageImports" not in content:
                    suggestions.append("Add experimental.optimizePackageImports for lucide-react, @heroicons/react")
                if "transpilePackages" not in content and "swc" not in content:
                    suggestions.append("Consider transpilePackages for monorepo packages")

                return {"found": True, "path": str(config_path), "suggestions": suggestions}
            except Exception:
                pass

    return {"found": False,
            "suggestions": ["Create next.config.js with image and bundle optimizations"]}


def analyze_imports(project_dir: Path) -> Dict:
    """Analyze import patterns in source files."""
    issues = []
    src_dirs = [project_dir / "src", project_dir / "app", project_dir / "pages"]

    files_checked = 0
    for src_dir in src_dirs:
        if not src_dir.exists():
            continue

        for ext in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
            for file_path in src_dir.glob(f"**/{ext}"):
                if "node_modules" in str(file_path):
                    continue

                files_checked += 1
                try:
                    content = file_path.read_text()
                    for pattern, message in IMPORT_PATTERNS:
                        if re.search(pattern, content):
                            issues.append({"file": str(file_path.relative_to(project_dir)),
                                           "issue": message})
                except Exception:
                    continue

    return {"files_checked": files_checked, "issues": issues}


def calculate_score(analysis: Dict) -> Tuple[int, str]:
    """Calculate bundle health score."""
    score = 100

    score -= len(analysis["dependencies"]["issues"]) * 10  # heavy dependencies
    # every warning (dev dep in production, redundant prop-types, overlapping state libs) costs 5
    score -= len(analysis["dependencies"]["warnings"]) * 5
    score -= len(analysis.get("imports", {}).get("issues", [])) * 3
    # Missing next.config (Next projects only; other frameworks carry no "nextjs" key)
    if not analysis.get("nextjs", {}).get("found", True):
        score -= 10

    score = max(0, min(100, score))
    grade = next((g for g, floor in (("A", 90), ("B", 80), ("C", 70), ("D", 60)) if score >= floor), "F")

    return score, grade


WARNING_ADVICE = {"dev_in_production": "Move dev-only packages to devDependencies",
                  "redundant": "Remove prop-types; TypeScript already checks props",
                  "multiple_state_libs": "Consolidate on one state management library"}


def recommendations(analysis: Dict) -> List[str]:
    """One line of advice per kind of finding, in report order."""
    deps = analysis["dependencies"]
    recs = ["Replace heavy dependencies with lighter alternatives"] if deps["issues"] else []
    for kind in dict.fromkeys(w["type"] for w in deps["warnings"]):
        recs.append(WARNING_ADVICE.get(kind, kind))
    if analysis.get("imports", {}).get("issues"):
        recs.append("Fix the flagged import patterns")
    if deps["optimizations"]:
        recs.append("Apply import optimizations for tree-shaking")
    return recs


def print_report(analysis: Dict) -> None:
    """Print human-readable report."""
    score, grade = calculate_score(analysis)

    print("=" * 60)
    print("FRONTEND BUNDLE ANALYSIS REPORT")
    print("=" * 60)
    print(f"\nBundle Health Score: {score}/100 ({grade})")
    print(f"Framework: {analysis.get('framework', 'other')}")

    deps = analysis["dependencies"]
    print(f"\nDependencies: {deps['total_dependencies']} production, {deps['total_dev_dependencies']} dev")

    if deps["issues"]:
        print("\n--- HEAVY DEPENDENCIES ---")
        for issue in deps["issues"]:
            print(f"\n  {issue['package']} ({issue['size']})")
            print(f"    Reason: {issue['reason']}")
            print(f"    Alternative: {issue['alternative']}")

    if deps["warnings"]:
        print("\n--- WARNINGS ---")
        for warning in deps["warnings"]:
            if "package" in warning:
                print(f"  - {warning['package']}: {warning['message']}")
            else:
                print(f"  - {warning['message']}")

    if deps["optimizations"]:
        print("\n--- OPTIMIZATION TIPS ---")
        for opt in deps["optimizations"]:
            print(f"  - {opt['package']}: {opt['tip']}")

    if analysis.get("nextjs", {}).get("suggestions"):
        print("\n--- NEXT.JS CONFIG ---")
        for suggestion in analysis["nextjs"]["suggestions"]:
            print(f"  - {suggestion}")

    if analysis.get("imports", {}).get("issues"):
        print("\n--- IMPORT ISSUES ---")
        for issue in analysis["imports"]["issues"][:10]:  # Limit to 10
            print(f"  - {issue['file']}: {issue['issue']}")

    print("\n--- RECOMMENDATIONS ---")
    for i, rec in enumerate(recommendations(analysis), 1):
        print(f"  {i}. {rec}")
    if not (deps["issues"] or deps["warnings"] or analysis.get("imports", {}).get("issues")):
        print("  Bundle is well-optimized!")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Analyze frontend project for bundle optimization opportunities")
    parser.add_argument("project_dir", nargs="?", default=".",
                        help="Project directory to analyze (default: current directory)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--json", action="store_true", help="Shorthand for --format json")
    parser.add_argument("--min-score", type=int, default=None,
                        help="Exit 1 when the health score is below this value (default: never fail)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Include detailed import analysis")

    args = parser.parse_args()
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"Error: Directory not found: {project_dir}", file=sys.stderr)
        sys.exit(2)

    package_json = load_package_json(project_dir)
    if not package_json:
        print("Error: No valid package.json found", file=sys.stderr)
        sys.exit(2)

    framework = detect_framework(package_json)
    analysis = {"project": str(project_dir), "framework": framework,
                "dependencies": analyze_dependencies(package_json)}
    if framework == "next":  # next.config checks mean nothing to a Vite or other app
        analysis["nextjs"] = check_nextjs_config(project_dir)

    if args.verbose:
        analysis["imports"] = analyze_imports(project_dir)

    analysis["score"], analysis["grade"] = calculate_score(analysis)

    if args.json or args.format == "json":
        print(json.dumps(analysis, indent=2))
    else:
        print_report(analysis)

    if args.min_score is not None and analysis["score"] < args.min_score:
        print(f"Bundle health score {analysis['score']} is below --min-score {args.min_score}",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
