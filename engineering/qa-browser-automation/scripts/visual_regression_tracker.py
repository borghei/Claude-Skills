#!/usr/bin/env python3
"""Visual Regression Tracker — Manages screenshot baselines and detects regressions.

Tracks visual changes between test runs by maintaining a JSON manifest of
baseline screenshots with file hashes. Computes change metrics per page and
flags significant regressions exceeding a configurable threshold.

Usage:
    python visual_regression_tracker.py --init --baseline-dir ./baselines
    python visual_regression_tracker.py --register ./baselines
    python visual_regression_tracker.py --baseline ./baselines --current ./screenshots
    python visual_regression_tracker.py --baseline ./baselines --current ./screenshots --threshold 3
    python visual_regression_tracker.py --update-baseline --baseline ./baselines --current ./screenshots
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MANIFEST_FILENAME = "visual_baseline_manifest.json"
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
DEFAULT_THRESHOLD = 5.0  # percent


# ---------------------------------------------------------------------------
# File Hashing
# ---------------------------------------------------------------------------

def compute_file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_file_size(filepath: Path) -> int:
    """Get file size in bytes."""
    return filepath.stat().st_size


# ---------------------------------------------------------------------------
# PNG Dimension Reader (standard library only)
# ---------------------------------------------------------------------------

def read_png_dimensions(filepath: Path) -> tuple[int, int] | None:
    """Read width and height from a PNG file header."""
    try:
        with open(filepath, "rb") as f:
            header = f.read(24)
            if len(header) < 24:
                return None
            if header[:8] != b"\x89PNG\r\n\x1a\n":
                return None
            width = struct.unpack(">I", header[16:20])[0]
            height = struct.unpack(">I", header[20:24])[0]
            return (width, height)
    except (OSError, struct.error):
        return None


def get_image_info(filepath: Path) -> dict[str, Any]:
    """Get basic image metadata."""
    info: dict[str, Any] = {
        "size_bytes": get_file_size(filepath),
        "extension": filepath.suffix.lower(),
    }
    if filepath.suffix.lower() == ".png":
        dims = read_png_dimensions(filepath)
        if dims:
            info["width"] = dims[0]
            info["height"] = dims[1]
    return info


# ---------------------------------------------------------------------------
# Manifest Management
# ---------------------------------------------------------------------------

def load_manifest(baseline_dir: Path) -> dict[str, Any]:
    """Load the baseline manifest from disk."""
    manifest_path = baseline_dir / MANIFEST_FILENAME
    if not manifest_path.exists():
        return {"version": 1, "created": "", "updated": "", "baselines": {}}
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(baseline_dir: Path, manifest: dict[str, Any]) -> None:
    """Save the baseline manifest to disk."""
    manifest_path = baseline_dir / MANIFEST_FILENAME
    manifest["updated"] = datetime.now(timezone.utc).isoformat()
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def init_baseline_dir(baseline_dir: Path) -> dict[str, Any]:
    """Initialize a baseline directory with an empty manifest."""
    baseline_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "version": 1,
        "created": datetime.now(timezone.utc).isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "baselines": {},
    }
    save_manifest(baseline_dir, manifest)
    return manifest


def register_baselines(baseline_dir: Path) -> dict[str, Any]:
    """Scan baseline directory and register all image files in the manifest."""
    manifest = load_manifest(baseline_dir)

    registered = 0
    for filepath in sorted(baseline_dir.iterdir()):
        if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if filepath.name == MANIFEST_FILENAME:
            continue

        page_name = filepath.stem
        file_hash = compute_file_hash(filepath)
        image_info = get_image_info(filepath)

        manifest["baselines"][page_name] = {
            "filename": filepath.name,
            "hash": file_hash,
            "registered": datetime.now(timezone.utc).isoformat(),
            **image_info,
        }
        registered += 1

    save_manifest(baseline_dir, manifest)
    return {"registered": registered, "total": len(manifest["baselines"])}


# ---------------------------------------------------------------------------
# Comparison Logic
# ---------------------------------------------------------------------------

def compare_file_bytes(file_a: Path, file_b: Path) -> dict[str, Any]:
    """Compare two files byte-by-byte and compute a change metric.

    Since we use only the standard library (no PIL/OpenCV), we compare:
    1. File hash equality (fast path)
    2. File size difference as a proxy for change magnitude
    3. Byte-level difference ratio for same-size files

    Returns a dict with comparison metrics.
    """
    hash_a = compute_file_hash(file_a)
    hash_b = compute_file_hash(file_b)

    if hash_a == hash_b:
        return {
            "identical": True,
            "change_pct": 0.0,
            "hash_a": hash_a,
            "hash_b": hash_b,
            "size_a": get_file_size(file_a),
            "size_b": get_file_size(file_b),
        }

    size_a = get_file_size(file_a)
    size_b = get_file_size(file_b)

    # If sizes differ significantly, estimate change from size delta
    if size_a > 0 and size_b > 0:
        size_ratio = abs(size_a - size_b) / max(size_a, size_b) * 100

        # For same-ish sizes, do byte comparison on compressed content
        # to estimate structural differences
        if abs(size_a - size_b) / max(size_a, size_b) < 0.5:
            change_pct = _byte_diff_ratio(file_a, file_b)
        else:
            change_pct = min(size_ratio * 2, 100.0)  # Scale up size diff
    else:
        change_pct = 100.0

    return {
        "identical": False,
        "change_pct": round(change_pct, 2),
        "hash_a": hash_a,
        "hash_b": hash_b,
        "size_a": size_a,
        "size_b": size_b,
    }


def _byte_diff_ratio(file_a: Path, file_b: Path) -> float:
    """Compute byte-level difference ratio between two files.

    Reads both files and compares byte-by-byte up to the shorter length,
    plus any extra bytes in the longer file count as differences.
    """
    with open(file_a, "rb") as fa, open(file_b, "rb") as fb:
        data_a = fa.read()
        data_b = fb.read()

    min_len = min(len(data_a), len(data_b))
    max_len = max(len(data_a), len(data_b))

    if max_len == 0:
        return 0.0

    diff_count = abs(len(data_a) - len(data_b))  # Extra bytes
    # Sample comparison for performance (compare every Nth byte for large files)
    step = max(1, min_len // 100000)
    sampled = 0
    sampled_diff = 0
    for i in range(0, min_len, step):
        sampled += 1
        if data_a[i] != data_b[i]:
            sampled_diff += 1

    if sampled > 0:
        byte_diff_ratio = sampled_diff / sampled
        diff_count += int(byte_diff_ratio * min_len)

    return min((diff_count / max_len) * 100, 100.0)


def run_comparison(
    baseline_dir: Path,
    current_dir: Path,
    threshold: float,
) -> dict[str, Any]:
    """Compare current screenshots against baselines.

    Returns a comprehensive comparison report.
    """
    manifest = load_manifest(baseline_dir)
    baselines = manifest.get("baselines", {})

    results: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "threshold": threshold,
        "baseline_dir": str(baseline_dir),
        "current_dir": str(current_dir),
        "pages": {},
        "summary": {
            "total_compared": 0,
            "passed": 0,
            "failed": 0,
            "new_pages": 0,
            "missing_pages": 0,
        },
    }

    # Find current screenshots
    current_files: dict[str, Path] = {}
    if current_dir.exists():
        for filepath in current_dir.iterdir():
            if filepath.suffix.lower() in SUPPORTED_EXTENSIONS:
                current_files[filepath.stem] = filepath

    # Compare each baseline
    for page_name, baseline_info in baselines.items():
        baseline_file = baseline_dir / baseline_info["filename"]
        if not baseline_file.exists():
            results["pages"][page_name] = {
                "status": "baseline_missing",
                "message": f"Baseline file missing: {baseline_info['filename']}",
            }
            results["summary"]["missing_pages"] += 1
            continue

        if page_name not in current_files:
            results["pages"][page_name] = {
                "status": "current_missing",
                "message": "No current screenshot found for this page",
            }
            results["summary"]["missing_pages"] += 1
            continue

        comparison = compare_file_bytes(baseline_file, current_files[page_name])
        passed = comparison["change_pct"] <= threshold

        results["pages"][page_name] = {
            "status": "pass" if passed else "fail",
            "change_pct": comparison["change_pct"],
            "identical": comparison["identical"],
            "baseline_hash": comparison["hash_a"],
            "current_hash": comparison["hash_b"],
            "baseline_size": comparison["size_a"],
            "current_size": comparison["size_b"],
        }

        results["summary"]["total_compared"] += 1
        if passed:
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1

    # Detect new pages (in current but not in baseline)
    for page_name, filepath in current_files.items():
        if page_name not in baselines:
            results["pages"][page_name] = {
                "status": "new",
                "message": "New page not in baseline",
                "current_hash": compute_file_hash(filepath),
                "current_size": get_file_size(filepath),
            }
            results["summary"]["new_pages"] += 1

    return results


def update_baselines(baseline_dir: Path, current_dir: Path) -> dict[str, Any]:
    """Update baseline screenshots with current ones."""
    import shutil

    manifest = load_manifest(baseline_dir)
    updated = 0
    added = 0

    if not current_dir.exists():
        return {"error": f"Current directory not found: {current_dir}"}

    for filepath in sorted(current_dir.iterdir()):
        if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        dest = baseline_dir / filepath.name
        shutil.copy2(filepath, dest)

        page_name = filepath.stem
        file_hash = compute_file_hash(dest)
        image_info = get_image_info(dest)

        if page_name in manifest.get("baselines", {}):
            updated += 1
        else:
            added += 1

        manifest.setdefault("baselines", {})[page_name] = {
            "filename": filepath.name,
            "hash": file_hash,
            "registered": datetime.now(timezone.utc).isoformat(),
            **image_info,
        }

    save_manifest(baseline_dir, manifest)
    return {"updated": updated, "added": added, "total": len(manifest["baselines"])}


# ---------------------------------------------------------------------------
# Output Formatting
# ---------------------------------------------------------------------------

def format_human_readable(results: dict[str, Any]) -> str:
    """Format comparison results as human-readable text."""
    lines: list[str] = []
    summary = results["summary"]

    lines.append("=" * 60)
    lines.append("  VISUAL REGRESSION REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  Timestamp:    {results['timestamp']}")
    lines.append(f"  Threshold:    {results['threshold']}%")
    lines.append(f"  Compared:     {summary['total_compared']} pages")
    lines.append(f"  Passed:       {summary['passed']}")
    lines.append(f"  Failed:       {summary['failed']}")
    lines.append(f"  New pages:    {summary['new_pages']}")
    lines.append(f"  Missing:      {summary['missing_pages']}")
    lines.append("")

    overall = "PASS" if summary["failed"] == 0 else "FAIL"
    lines.append(f"  Result:       {overall}")
    lines.append("")

    # Page details
    lines.append("-" * 60)
    lines.append("  PAGE RESULTS")
    lines.append("-" * 60)

    for page_name, data in sorted(results["pages"].items()):
        status = data["status"].upper()
        if data["status"] == "pass":
            change = data.get("change_pct", 0)
            marker = "  [OK]" if data.get("identical") else f"  [{change}% change]"
            lines.append(f"  {page_name:<30} PASS{marker}")
        elif data["status"] == "fail":
            change = data.get("change_pct", 0)
            lines.append(f"  {page_name:<30} FAIL  [{change}% change] !!!")
        elif data["status"] == "new":
            lines.append(f"  {page_name:<30} NEW   (not in baseline)")
        else:
            msg = data.get("message", "")
            lines.append(f"  {page_name:<30} {status}  {msg}")

    lines.append("")
    lines.append("=" * 60)

    if summary["failed"] > 0:
        lines.append("")
        lines.append("  REGRESSIONS DETECTED — Review failed pages above.")
        lines.append("  To accept changes: --update-baseline")
        lines.append("")

    return "\n".join(lines)


def format_json_output(results: dict[str, Any]) -> str:
    """Format comparison results as JSON."""
    return json.dumps(results, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="visual_regression_tracker",
        description="Track visual regressions between screenshot baselines and current captures.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python visual_regression_tracker.py --init --baseline-dir ./baselines\n"
            "  python visual_regression_tracker.py --register ./baselines\n"
            "  python visual_regression_tracker.py --baseline ./baselines --current ./screenshots\n"
            "  python visual_regression_tracker.py --baseline ./baselines --current ./screenshots --threshold 3\n"
            "  python visual_regression_tracker.py --update-baseline --baseline ./baselines --current ./screenshots\n"
        ),
    )

    # Actions
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize a new baseline directory",
    )
    parser.add_argument(
        "--register",
        metavar="DIR",
        help="Scan directory and register all images as baselines",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Update baselines with current screenshots",
    )

    # Directories
    parser.add_argument(
        "--baseline-dir", "--baseline",
        dest="baseline_dir",
        help="Path to baseline screenshot directory",
    )
    parser.add_argument(
        "--current",
        help="Path to current screenshot directory (for comparison)",
    )

    # Options
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Change percentage threshold for regression (default: {DEFAULT_THRESHOLD}%%)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )

    return parser


def main() -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # --- Init mode ---
    if args.init:
        if not args.baseline_dir:
            print("Error: --baseline-dir required with --init", file=sys.stderr)
            sys.exit(1)
        baseline_dir = Path(args.baseline_dir)
        manifest = init_baseline_dir(baseline_dir)
        if args.json_output:
            print(json.dumps({"action": "init", "directory": str(baseline_dir), "manifest": manifest}, indent=2))
        else:
            print(f"Initialized baseline directory: {baseline_dir}")
            print(f"Manifest created: {baseline_dir / MANIFEST_FILENAME}")
        return

    # --- Register mode ---
    if args.register:
        register_dir = Path(args.register)
        if not register_dir.exists():
            print(f"Error: Directory not found: {args.register}", file=sys.stderr)
            sys.exit(1)
        result = register_baselines(register_dir)
        if args.json_output:
            print(json.dumps({"action": "register", **result}, indent=2))
        else:
            print(f"Registered {result['registered']} baseline(s) ({result['total']} total)")
        return

    # --- Update baseline mode ---
    if args.update_baseline:
        if not args.baseline_dir or not args.current:
            print("Error: --baseline-dir and --current required with --update-baseline", file=sys.stderr)
            sys.exit(1)
        baseline_dir = Path(args.baseline_dir)
        current_dir = Path(args.current)
        result = update_baselines(baseline_dir, current_dir)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        if args.json_output:
            print(json.dumps({"action": "update_baseline", **result}, indent=2))
        else:
            print(f"Updated {result['updated']} baseline(s), added {result['added']} new ({result['total']} total)")
        return

    # --- Comparison mode (default) ---
    if not args.baseline_dir or not args.current:
        print("Error: --baseline-dir and --current required for comparison", file=sys.stderr)
        print("Use --help for usage information", file=sys.stderr)
        sys.exit(1)

    baseline_dir = Path(args.baseline_dir)
    current_dir = Path(args.current)

    if not baseline_dir.exists():
        print(f"Error: Baseline directory not found: {baseline_dir}", file=sys.stderr)
        sys.exit(1)
    if not current_dir.exists():
        print(f"Error: Current directory not found: {current_dir}", file=sys.stderr)
        sys.exit(1)

    results = run_comparison(baseline_dir, current_dir, args.threshold)

    if args.json_output:
        print(format_json_output(results))
    else:
        print(format_human_readable(results))

    # Exit code: non-zero if regressions found
    if results["summary"]["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
