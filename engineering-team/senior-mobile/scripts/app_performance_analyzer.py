#!/usr/bin/env python3
"""
Mobile App Performance Analyzer
================================

CLI tool that analyzes a mobile project for common performance issues.

Checks performed:
  - Large image assets (unoptimized PNGs/JPGs)
  - Unnecessary re-render patterns (React Native)
  - Memory leak patterns (missing cleanup, uncancelled subscriptions)
  - Bundle size estimation
  - Platform-specific anti-patterns

Supported platforms: react-native, flutter, ios-native, android-native

Usage:
  python app_performance_analyzer.py /path/to/project
  python app_performance_analyzer.py /path/to/project --platform react-native
  python app_performance_analyzer.py /path/to/project --json

Dependencies: Python 3.8+ standard library only.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Severity levels
# ---------------------------------------------------------------------------

SEVERITY_CRITICAL = "critical"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

SEVERITY_WEIGHT = {
    SEVERITY_CRITICAL: 3,
    SEVERITY_WARNING: 2,
    SEVERITY_INFO: 1,
}

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

def detect_platform(project_dir: Path) -> str:
    """Auto-detect the mobile platform based on project files."""
    if (project_dir / "pubspec.yaml").exists():
        return "flutter"
    if (project_dir / "package.json").exists():
        pkg_file = project_dir / "package.json"
        try:
            content = pkg_file.read_text()
            if "react-native" in content or "expo" in content:
                return "react-native"
        except Exception:
            pass
    if (project_dir / "app" / "build.gradle").exists() or (project_dir / "app" / "build.gradle.kts").exists():
        return "android-native"
    # Look for .xcodeproj or Swift files
    for child in project_dir.iterdir():
        if child.suffix == ".xcodeproj" or child.suffix == ".xcworkspace":
            return "ios-native"
    swift_files = list(project_dir.rglob("*.swift"))
    if swift_files:
        return "ios-native"
    return "unknown"

# ---------------------------------------------------------------------------
# Image asset analysis
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif", ".webp"}
# Thresholds in bytes
IMAGE_SIZE_WARNING = 500 * 1024   # 500 KB
IMAGE_SIZE_CRITICAL = 1024 * 1024  # 1 MB


def analyze_images(project_dir: Path) -> list:
    """Find oversized image assets."""
    issues = []
    total_image_bytes = 0
    image_count = 0

    for root, dirs, files in os.walk(project_dir):
        # Skip build and dependency directories
        dirs[:] = [d for d in dirs if d not in {
            "node_modules", ".gradle", "build", "Pods",
            "DerivedData", ".dart_tool", ".expo", ".git",
            "__pycache__", ".next",
        }]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in IMAGE_EXTENSIONS:
                continue
            fpath = Path(root) / fname
            try:
                size = fpath.stat().st_size
            except OSError:
                continue

            image_count += 1
            total_image_bytes += size
            rel = fpath.relative_to(project_dir)

            if size >= IMAGE_SIZE_CRITICAL:
                issues.append({
                    "category": "image_assets",
                    "severity": SEVERITY_CRITICAL,
                    "file": str(rel),
                    "message": f"Very large image ({_fmt_bytes(size)}). Consider compressing or converting to WebP.",
                    "size_bytes": size,
                })
            elif size >= IMAGE_SIZE_WARNING:
                issues.append({
                    "category": "image_assets",
                    "severity": SEVERITY_WARNING,
                    "file": str(rel),
                    "message": f"Large image ({_fmt_bytes(size)}). Consider optimizing.",
                    "size_bytes": size,
                })

    # Summary
    if total_image_bytes > 5 * 1024 * 1024:
        issues.append({
            "category": "image_assets",
            "severity": SEVERITY_WARNING,
            "file": None,
            "message": f"Total image assets: {_fmt_bytes(total_image_bytes)} across {image_count} files. Consider using a CDN or lazy loading.",
            "size_bytes": total_image_bytes,
        })

    return issues


def _fmt_bytes(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    elif size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"

# ---------------------------------------------------------------------------
# React Native specific checks
# ---------------------------------------------------------------------------

# Patterns that suggest re-render issues
RN_RERENDER_PATTERNS = [
    (r"<FlatList[^>]*(?!keyExtractor)", "FlatList without keyExtractor causes full re-renders"),
    (r"style=\{\{", "Inline style objects create new references each render - use StyleSheet.create"),
    (r"onPress=\{\(\)\s*=>", "Inline arrow function in onPress creates new reference each render - use useCallback"),
    (r"\.map\(.*=>\s*<", "Using .map() to render lists instead of FlatList/SectionList may cause perf issues with large data"),
]

RN_MEMORY_PATTERNS = [
    (r"addEventListener\(", "Event listener added - ensure it is removed in cleanup/useEffect return"),
    (r"setInterval\(", "setInterval detected - ensure clearInterval on unmount"),
    (r"setTimeout\(", "setTimeout detected - ensure clearTimeout on unmount"),
    (r"new WebSocket\(", "WebSocket created - ensure close() on component unmount"),
    (r"Animated\.loop\(", "Animated.loop detected - ensure animation is stopped on unmount"),
]

RN_PERF_PATTERNS = [
    (r"console\.(log|warn|error|info|debug)\(", "console.log statements left in code - remove for production"),
    (r"import\s+\{[^}]+\}\s+from\s+['\"]lodash['\"]", "Full lodash import - use lodash/specific-function for smaller bundles"),
    (r"import\s+moment\s+from", "moment.js is large (300KB+) - consider date-fns or dayjs"),
    (r"JSON\.parse\(JSON\.stringify\(", "Deep clone via JSON - consider structuredClone or specific copy"),
]


def analyze_react_native(project_dir: Path) -> list:
    """React Native specific performance analysis."""
    issues = []

    source_extensions = {".js", ".jsx", ".ts", ".tsx"}
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".expo", ".git", "build", "__tests__"}]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in source_extensions:
                continue
            fpath = Path(root) / fname
            rel = str(fpath.relative_to(project_dir))
            try:
                content = fpath.read_text(errors="replace")
            except OSError:
                continue

            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                for pattern, msg in RN_RERENDER_PATTERNS:
                    if re.search(pattern, line):
                        issues.append({
                            "category": "re_renders",
                            "severity": SEVERITY_WARNING,
                            "file": rel,
                            "line": line_num,
                            "message": msg,
                        })

                for pattern, msg in RN_MEMORY_PATTERNS:
                    if re.search(pattern, line):
                        issues.append({
                            "category": "memory_leaks",
                            "severity": SEVERITY_WARNING,
                            "file": rel,
                            "line": line_num,
                            "message": msg,
                        })

                for pattern, msg in RN_PERF_PATTERNS:
                    if re.search(pattern, line):
                        issues.append({
                            "category": "performance",
                            "severity": SEVERITY_INFO if "console" in pattern else SEVERITY_WARNING,
                            "file": rel,
                            "line": line_num,
                            "message": msg,
                        })

    # FlatList optimization analysis (multi-line: check full component props)
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".expo", ".git", "build", "__tests__"}]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in source_extensions:
                continue
            fpath = Path(root) / fname
            rel = str(fpath.relative_to(project_dir))
            try:
                content = fpath.read_text(errors="replace")
            except OSError:
                continue

            # Find FlatList usages and check for optimization props
            flatlist_matches = list(re.finditer(r"<FlatList\b", content))
            for match in flatlist_matches:
                start = match.start()
                # Extract a reasonable chunk after <FlatList to capture its props
                chunk_end = min(start + 1500, len(content))
                chunk = content[start:chunk_end]
                # Find closing > or /> to scope the props
                close = re.search(r"/?>", chunk)
                if close:
                    chunk = chunk[: close.end()]
                line_num = content[:start].count("\n") + 1

                if "getItemLayout" not in chunk:
                    issues.append({
                        "category": "flatlist_optimization",
                        "severity": SEVERITY_WARNING,
                        "file": rel,
                        "line": line_num,
                        "message": "FlatList missing getItemLayout - add it for fixed-height items to skip measurement.",
                    })
                if "windowSize" not in chunk:
                    issues.append({
                        "category": "flatlist_optimization",
                        "severity": SEVERITY_INFO,
                        "file": rel,
                        "line": line_num,
                        "message": "FlatList missing windowSize prop - set windowSize={5} to reduce off-screen rendering.",
                    })
                if "keyExtractor" not in chunk:
                    issues.append({
                        "category": "flatlist_optimization",
                        "severity": SEVERITY_WARNING,
                        "file": rel,
                        "line": line_num,
                        "message": "FlatList missing keyExtractor - required for efficient re-rendering.",
                    })

    # Check for missing useCallback/useMemo in components with FlatList
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".expo", ".git", "build", "__tests__"}]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in source_extensions:
                continue
            fpath = Path(root) / fname
            rel = str(fpath.relative_to(project_dir))
            try:
                content = fpath.read_text(errors="replace")
            except OSError:
                continue

            # If file contains FlatList but no useCallback, flag it
            if "<FlatList" in content:
                if "useCallback" not in content:
                    issues.append({
                        "category": "re_renders",
                        "severity": SEVERITY_WARNING,
                        "file": rel,
                        "message": "File uses FlatList but does not import useCallback - wrap renderItem and handlers in useCallback.",
                    })
                if "useMemo" not in content and "React.memo" not in content:
                    issues.append({
                        "category": "re_renders",
                        "severity": SEVERITY_INFO,
                        "file": rel,
                        "message": "File uses FlatList but does not use useMemo or React.memo - consider memoizing list items.",
                    })

    # Check package.json for heavy dependencies
    pkg_path = project_dir / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text())
            deps = {}
            deps.update(pkg.get("dependencies", {}))
            deps.update(pkg.get("devDependencies", {}))

            heavy_deps = {
                "moment": "moment is ~300KB. Use date-fns or dayjs instead.",
                "lodash": "Full lodash is ~70KB. Use lodash-es or specific imports.",
                "axios": "axios is ~13KB. fetch() is built-in for React Native.",
                "react-native-elements": "Heavy UI lib. Consider react-native-paper or custom components.",
            }
            for dep, msg in heavy_deps.items():
                if dep in deps:
                    issues.append({
                        "category": "bundle_size",
                        "severity": SEVERITY_INFO,
                        "file": "package.json",
                        "message": msg,
                    })
        except (json.JSONDecodeError, OSError):
            pass

    return issues

# ---------------------------------------------------------------------------
# Flutter specific checks
# ---------------------------------------------------------------------------

FLUTTER_PERF_PATTERNS = [
    (r"setState\(\s*\(\)\s*\{", "setState can cause full widget rebuild - consider using ValueNotifier or Riverpod for granular updates"),
    (r"print\(", "print() statements left in code - remove for production or use debugPrint"),
    (r"Column\(\s*children:\s*\[.*ListView", "ListView inside Column without Expanded/shrinkWrap causes layout issues"),
    (r"Image\.network\(", "Image.network without caching - consider cached_network_image package"),
]

FLUTTER_MEMORY_PATTERNS = [
    (r"StreamSubscription", "StreamSubscription detected - ensure cancel() in dispose()"),
    (r"AnimationController", "AnimationController detected - ensure dispose() is called"),
    (r"TextEditingController", "TextEditingController detected - ensure dispose() is called"),
    (r"ScrollController", "ScrollController detected - ensure dispose() is called"),
    (r"FocusNode", "FocusNode detected - ensure dispose() is called"),
]


def analyze_flutter(project_dir: Path) -> list:
    """Flutter specific performance analysis."""
    issues = []

    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in {".dart_tool", "build", ".git", ".idea"}]
        for fname in files:
            if not fname.endswith(".dart"):
                continue
            fpath = Path(root) / fname
            rel = str(fpath.relative_to(project_dir))
            try:
                content = fpath.read_text(errors="replace")
            except OSError:
                continue

            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                for pattern, msg in FLUTTER_PERF_PATTERNS:
                    if re.search(pattern, line):
                        issues.append({
                            "category": "performance",
                            "severity": SEVERITY_WARNING,
                            "file": rel,
                            "line": line_num,
                            "message": msg,
                        })

                for pattern, msg in FLUTTER_MEMORY_PATTERNS:
                    if re.search(pattern, line):
                        issues.append({
                            "category": "memory_leaks",
                            "severity": SEVERITY_WARNING,
                            "file": rel,
                            "line": line_num,
                            "message": msg,
                        })

    # Check pubspec for heavy packages
    pubspec = project_dir / "pubspec.yaml"
    if pubspec.exists():
        try:
            content = pubspec.read_text()
            if "flutter_svg" not in content and re.search(r"\.svg", content):
                issues.append({
                    "category": "performance",
                    "severity": SEVERITY_INFO,
                    "file": "pubspec.yaml",
                    "message": "SVG files detected but flutter_svg not in dependencies.",
                })
        except OSError:
            pass

    return issues

# ---------------------------------------------------------------------------
# iOS Native checks
# ---------------------------------------------------------------------------

IOS_PATTERNS = [
    (r"DispatchQueue\.main\.async", "Check that heavy work is not dispatched to main queue"),
    (r"UIImage\(named:", "UIImage(named:) caches images in memory - use UIImage(contentsOfFile:) for large images"),
    (r"NotificationCenter\.default\.addObserver", "Observer added - ensure removeObserver in deinit"),
    (r"Timer\.scheduledTimer", "Timer created - ensure invalidate() in deinit/disappear"),
    (r"print\(", "print() statements left in code - remove for production"),
    (r"force\s+try", "Force try detected - handle errors gracefully"),
    (r"as!", "Force cast detected - use optional binding (as?) instead"),
]


def analyze_ios(project_dir: Path) -> list:
    """iOS native performance analysis."""
    issues = []

    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in {"Pods", "DerivedData", ".git", "build", "xcuserdata"}]
        for fname in files:
            if not fname.endswith(".swift"):
                continue
            fpath = Path(root) / fname
            rel = str(fpath.relative_to(project_dir))
            try:
                content = fpath.read_text(errors="replace")
            except OSError:
                continue

            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                for pattern, msg in IOS_PATTERNS:
                    if re.search(pattern, line):
                        issues.append({
                            "category": "performance",
                            "severity": SEVERITY_WARNING,
                            "file": rel,
                            "line": line_num,
                            "message": msg,
                        })

    return issues

# ---------------------------------------------------------------------------
# Android Native checks
# ---------------------------------------------------------------------------

ANDROID_PATTERNS = [
    (r"runOnUiThread", "Heavy work on UI thread detected - use coroutines or background thread"),
    (r"Log\.(d|v|i|w|e)\(", "Log statements left in code - remove for production builds or use Timber"),
    (r"GlobalScope\.launch", "GlobalScope causes potential leaks - use viewModelScope or lifecycleScope"),
    (r"Thread\(\)", "Raw Thread usage - prefer Coroutines for structured concurrency"),
    (r"BitmapFactory\.decodeFile", "BitmapFactory without inSampleSize may cause OOM - use Coil or Glide"),
    (r"registerReceiver\(", "BroadcastReceiver registered - ensure unregisterReceiver in onDestroy/onPause"),
]


def analyze_android(project_dir: Path) -> list:
    """Android native performance analysis."""
    issues = []
    kt_extensions = {".kt", ".java"}

    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in {".gradle", "build", ".git", ".idea"}]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in kt_extensions:
                continue
            fpath = Path(root) / fname
            rel = str(fpath.relative_to(project_dir))
            try:
                content = fpath.read_text(errors="replace")
            except OSError:
                continue

            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                for pattern, msg in ANDROID_PATTERNS:
                    if re.search(pattern, line):
                        issues.append({
                            "category": "performance",
                            "severity": SEVERITY_WARNING,
                            "file": rel,
                            "line": line_num,
                            "message": msg,
                        })

    return issues

# ---------------------------------------------------------------------------
# Bundle size estimation
# ---------------------------------------------------------------------------

SKIP_DIRS = {
    "node_modules", ".gradle", "build", "Pods", "DerivedData",
    ".dart_tool", ".expo", ".git", "__pycache__", ".next", ".idea",
    "xcuserdata",
}

CODE_EXTENSIONS = {
    ".js", ".jsx", ".ts", ".tsx", ".dart", ".swift", ".kt", ".java",
    ".m", ".mm", ".h", ".c", ".cpp",
}


def estimate_bundle_size(project_dir: Path) -> dict:
    """Estimate the source code size (not final bundle, but a rough indicator)."""
    total_code_bytes = 0
    total_asset_bytes = 0
    total_other_bytes = 0
    code_files = 0
    asset_files = 0

    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            fpath = Path(root) / fname
            try:
                size = fpath.stat().st_size
            except OSError:
                continue

            ext = os.path.splitext(fname)[1].lower()
            if ext in CODE_EXTENSIONS:
                total_code_bytes += size
                code_files += 1
            elif ext in IMAGE_EXTENSIONS or ext in {".mp4", ".mp3", ".wav", ".ttf", ".otf", ".json"}:
                total_asset_bytes += size
                asset_files += 1
            else:
                total_other_bytes += size

    return {
        "source_code_size": _fmt_bytes(total_code_bytes),
        "source_code_bytes": total_code_bytes,
        "source_code_files": code_files,
        "asset_size": _fmt_bytes(total_asset_bytes),
        "asset_bytes": total_asset_bytes,
        "asset_files": asset_files,
        "other_size": _fmt_bytes(total_other_bytes),
        "other_bytes": total_other_bytes,
        "total_size": _fmt_bytes(total_code_bytes + total_asset_bytes + total_other_bytes),
        "total_bytes": total_code_bytes + total_asset_bytes + total_other_bytes,
    }

# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def compute_score(issues: list) -> int:
    """Compute a performance score from 0-100."""
    base = 100
    for issue in issues:
        weight = SEVERITY_WEIGHT.get(issue.get("severity", SEVERITY_INFO), 1)
        base -= weight
    return max(0, min(100, base))


def generate_report(project_dir: Path, platform: str, json_output: bool):
    """Run all analyses and produce a report."""
    all_issues = []

    # Image analysis (all platforms)
    all_issues.extend(analyze_images(project_dir))

    # Platform-specific analysis
    if platform == "react-native":
        all_issues.extend(analyze_react_native(project_dir))
    elif platform == "flutter":
        all_issues.extend(analyze_flutter(project_dir))
    elif platform == "ios-native":
        all_issues.extend(analyze_ios(project_dir))
    elif platform == "android-native":
        all_issues.extend(analyze_android(project_dir))

    # Bundle size estimation
    bundle_info = estimate_bundle_size(project_dir)

    # Categorize
    by_category = defaultdict(list)
    by_severity = defaultdict(int)
    for issue in all_issues:
        by_category[issue["category"]].append(issue)
        by_severity[issue["severity"]] += 1

    score = compute_score(all_issues)

    result = {
        "project": str(project_dir),
        "platform": platform,
        "analyzed_at": datetime.utcnow().isoformat() + "Z",
        "performance_score": score,
        "summary": {
            "total_issues": len(all_issues),
            "critical": by_severity.get(SEVERITY_CRITICAL, 0),
            "warnings": by_severity.get(SEVERITY_WARNING, 0),
            "info": by_severity.get(SEVERITY_INFO, 0),
        },
        "bundle_estimate": bundle_info,
        "issues_by_category": {k: v for k, v in sorted(by_category.items())},
        "issues": all_issues,
    }

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        _print_human_report(result)


def _print_human_report(result: dict):
    """Pretty-print the analysis report."""
    print("=" * 70)
    print("  MOBILE APP PERFORMANCE ANALYSIS")
    print("=" * 70)
    print(f"  Project:   {result['project']}")
    print(f"  Platform:  {result['platform']}")
    print(f"  Analyzed:  {result['analyzed_at']}")
    print()

    score = result["performance_score"]
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"
    print(f"  Performance Score: {score}/100 (Grade: {grade})")
    print()

    s = result["summary"]
    print(f"  Issues Found: {s['total_issues']}")
    if s["critical"]:
        print(f"    Critical: {s['critical']}")
    if s["warnings"]:
        print(f"    Warnings: {s['warnings']}")
    if s["info"]:
        print(f"    Info:     {s['info']}")
    print()

    b = result["bundle_estimate"]
    print("  Bundle Size Estimate:")
    print(f"    Source code:  {b['source_code_size']} ({b['source_code_files']} files)")
    print(f"    Assets:       {b['asset_size']} ({b['asset_files']} files)")
    print(f"    Total:        {b['total_size']}")
    print()

    if result["issues"]:
        print("-" * 70)
        print("  DETAILED ISSUES")
        print("-" * 70)

        for category, issues in result["issues_by_category"].items():
            cat_label = category.replace("_", " ").title()
            print(f"\n  [{cat_label}] ({len(issues)} issues)")
            for issue in issues:
                sev = issue["severity"].upper()
                loc = issue.get("file", "project")
                line = issue.get("line")
                loc_str = f"{loc}:{line}" if line else loc
                print(f"    [{sev:8s}] {loc_str}")
                print(f"              {issue['message']}")
    else:
        print("  No performance issues detected. Great job!")

    print()
    print("=" * 70)
    print("  RECOMMENDATIONS")
    print("=" * 70)

    if result["summary"]["critical"] > 0:
        print("  1. Address all CRITICAL issues immediately")
    if result["bundle_estimate"]["asset_bytes"] > 5 * 1024 * 1024:
        print("  2. Optimize image assets - total asset size exceeds 5 MB")
    if result["summary"]["warnings"] > 10:
        print("  3. Review WARNING issues - many potential performance regressions")
    if result["platform"] == "react-native":
        print("  - Use React.memo() for expensive components")
        print("  - Use useCallback/useMemo for reference stability")
        print("  - Use FlatList with keyExtractor for all lists")
        print("  - Remove console.log statements before production")
    elif result["platform"] == "flutter":
        print("  - Use const constructors where possible")
        print("  - Prefer ValueNotifier/Riverpod over setState for granular rebuilds")
        print("  - Dispose all controllers in dispose()")
        print("  - Use cached_network_image for network images")
    elif result["platform"] == "ios-native":
        print("  - Profile with Instruments (Time Profiler, Allocations)")
        print("  - Remove all print() statements for release")
        print("  - Avoid force unwrapping and force casting")
    elif result["platform"] == "android-native":
        print("  - Use viewModelScope/lifecycleScope instead of GlobalScope")
        print("  - Profile with Android Studio Profiler")
        print("  - Use Coil/Glide for image loading")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="app_performance_analyzer",
        description="Analyze a mobile app project for performance issues.",
        epilog="Example: python app_performance_analyzer.py ./my-app --platform react-native",
    )
    parser.add_argument(
        "project_dir",
        help="Path to the mobile project directory",
    )
    parser.add_argument(
        "--platform", "-p",
        choices=["react-native", "flutter", "ios-native", "android-native"],
        default=None,
        help="Target platform (auto-detected if omitted)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output results as JSON",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    project_dir = Path(args.project_dir).resolve()

    if not project_dir.is_dir():
        sys.stderr.write(f"Error: '{project_dir}' is not a directory.\n")
        sys.exit(1)

    platform = args.platform
    if platform is None:
        platform = detect_platform(project_dir)
        if platform == "unknown":
            sys.stderr.write(
                "Error: Could not auto-detect platform. "
                "Use --platform to specify.\n"
            )
            sys.exit(1)
        if not args.json:
            sys.stderr.write(f"Auto-detected platform: {platform}\n")

    generate_report(project_dir, platform, args.json)


if __name__ == "__main__":
    main()
