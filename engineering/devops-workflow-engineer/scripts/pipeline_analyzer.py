#!/usr/bin/env python3
"""
GitHub Actions Pipeline Analyzer

Analyzes existing GitHub Actions workflow files for optimization opportunities
including parallel job detection, caching gaps, unnecessary steps, and cost
estimation.

Usage:
    python pipeline_analyzer.py path/to/.github/workflows/
    python pipeline_analyzer.py path/to/workflow.yml
    python pipeline_analyzer.py path/to/.github/workflows/ --format json
"""

import argparse
import json
import os
import re
import sys
import textwrap
from pathlib import Path


# ---------------------------------------------------------------------------
# Cost constants (GitHub-hosted runners, per-minute, Linux)
# ---------------------------------------------------------------------------

RUNNER_COSTS = {
    "ubuntu-latest": 0.008,
    "ubuntu-22.04": 0.008,
    "ubuntu-24.04": 0.008,
    "ubuntu-20.04": 0.008,
    "macos-latest": 0.08,
    "macos-14": 0.08,
    "macos-13": 0.08,
    "macos-15": 0.08,
    "windows-latest": 0.016,
    "windows-2022": 0.016,
    "windows-2019": 0.016,
}

# Default cost for unknown runners
DEFAULT_COST_PER_MIN = 0.008


# ---------------------------------------------------------------------------
# YAML minimal parser (standard library only, no PyYAML dependency)
# ---------------------------------------------------------------------------

def _minimal_yaml_parse(text):
    """
    Minimal YAML-like parser that extracts enough structure for analysis.
    This is NOT a full YAML parser -- it handles the subset used in
    GitHub Actions workflow files. Returns a dict.
    """
    result = {}
    current_path = []
    indent_stack = [-1]

    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        i += 1

        # Skip comments and blank lines
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(stripped)

        # Pop stack for dedents
        while len(indent_stack) > 1 and indent <= indent_stack[-1]:
            indent_stack.pop()
            if current_path:
                current_path.pop()

        # Handle list items
        if stripped.startswith("- "):
            continue

        # Handle key: value
        if ":" in stripped:
            colon_idx = stripped.index(":")
            key = stripped[:colon_idx].strip().strip("'\"")
            value = stripped[colon_idx + 1:].strip().strip("'\"")

            if value:
                # Simple key: value
                _set_nested(result, current_path + [key], value)
            else:
                # Key with nested content
                current_path.append(key)
                indent_stack.append(indent)
                _set_nested(result, current_path, {})

    return result


def _set_nested(d, path, value):
    """Set a value in a nested dict by path."""
    for key in path[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]
    if path:
        if isinstance(d.get(path[-1]), dict) and isinstance(value, dict):
            d[path[-1]].update(value)
        else:
            d[path[-1]] = value


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------


class Finding:
    """Represents an optimization finding."""

    SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}

    def __init__(self, severity, category, title, description, recommendation, estimated_savings=None):
        self.severity = severity
        self.category = category
        self.title = title
        self.description = description
        self.recommendation = recommendation
        self.estimated_savings = estimated_savings

    def to_dict(self):
        d = {
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
        }
        if self.estimated_savings:
            d["estimated_savings"] = self.estimated_savings
        return d


def analyze_workflow_file(filepath):
    """Analyze a single workflow file and return findings."""
    findings = []
    file_info = {"path": str(filepath), "name": filepath.name}

    try:
        content = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        findings.append(Finding(
            "critical", "file", "Cannot read file",
            f"Error reading {filepath}: {e}",
            "Check file permissions and encoding."
        ))
        return file_info, findings

    lines = content.split("\n")
    file_info["line_count"] = len(lines)

    parsed = _minimal_yaml_parse(content)

    # --- Check: Missing concurrency group ---
    if "concurrency" not in content:
        findings.append(Finding(
            "warning", "cost",
            "No concurrency group",
            "Workflow does not define a concurrency group. Multiple runs for the same branch will execute in parallel, wasting resources.",
            "Add:\nconcurrency:\n  group: ${{ github.workflow }}-${{ github.ref }}\n  cancel-in-progress: true",
            estimated_savings="10-30% fewer redundant runs",
        ))

    # --- Check: Missing timeout ---
    jobs_in_file = _extract_jobs(content)
    for job_name, job_content in jobs_in_file.items():
        if "timeout-minutes" not in job_content:
            findings.append(Finding(
                "warning", "cost",
                f"No timeout on job '{job_name}'",
                f"Job '{job_name}' has no timeout-minutes set. A stuck job will run until the default 6-hour limit.",
                f"Add 'timeout-minutes: 15' (or appropriate limit) to the '{job_name}' job.",
                estimated_savings="Prevents runaway jobs (up to 360 min wasted)",
            ))

    # --- Check: Missing caching ---
    has_setup_action = False
    has_cache = "actions/cache@" in content or "cache:" in content

    for action in ["actions/setup-python@", "actions/setup-node@", "actions/setup-go@", "actions/setup-java@"]:
        if action in content:
            has_setup_action = True
            break

    if has_setup_action and not has_cache:
        findings.append(Finding(
            "warning", "performance",
            "No dependency caching detected",
            "A setup action is used but no caching is configured. Dependencies are re-downloaded every run.",
            "Add 'cache: pip' (or npm/yarn) to the setup action, or use actions/cache@v4 with appropriate key.",
            estimated_savings="30-60% faster dependency installation",
        ))

    # --- Check: Checkout without fetch-depth ---
    checkout_count = content.count("actions/checkout@")
    shallow_checkout_count = len(re.findall(r"fetch-depth:\s*[01]", content))
    if checkout_count > 0 and shallow_checkout_count == 0 and "fetch-depth" not in content:
        # Only flag if there is no git history dependency
        if "git log" not in content and "git diff" not in content and "git blame" not in content:
            findings.append(Finding(
                "info", "performance",
                "Consider shallow checkout",
                "Full git history is fetched but may not be needed.",
                "Add 'fetch-depth: 1' to actions/checkout if full history is not required.",
                estimated_savings="5-15 seconds per checkout",
            ))

    # --- Check: Sequential jobs that could be parallel ---
    needs_map = {}
    for job_name, job_content in jobs_in_file.items():
        needs_match = re.search(r"needs:\s*\[?([^\]\n]+)", job_content)
        if needs_match:
            deps = [d.strip().strip("'\"") for d in needs_match.group(1).split(",")]
            needs_map[job_name] = deps
        else:
            # Check for single value needs
            needs_match2 = re.search(r"needs:\s+(\S+)", job_content)
            if needs_match2:
                needs_map[job_name] = [needs_match2.group(1).strip()]
            else:
                needs_map[job_name] = []

    # Detect linear chains that could be parallel
    chain_jobs = [j for j, deps in needs_map.items() if len(deps) == 1]
    if len(chain_jobs) > 2:
        # Check if multiple jobs depend on the same single parent
        parent_counts = {}
        for j, deps in needs_map.items():
            if len(deps) == 1:
                parent_counts.setdefault(deps[0], []).append(j)
        for parent, children in parent_counts.items():
            if len(children) > 1:
                # These are already parallel -- skip
                pass

        # Check for a long sequential chain
        visited = set()
        for job_name in needs_map:
            chain = _trace_chain(job_name, needs_map, visited)
            if len(chain) >= 4:
                findings.append(Finding(
                    "info", "performance",
                    f"Long sequential chain detected ({len(chain)} jobs)",
                    f"Jobs form a linear chain: {' -> '.join(chain)}. Some may be parallelizable.",
                    "Review if any jobs in the chain are independent and can run in parallel by removing unnecessary 'needs' dependencies.",
                    estimated_savings="Potential 20-40% pipeline time reduction",
                ))
                break

    # --- Check: No path filters ---
    on_section = _extract_section(content, "on:")
    if on_section and "paths" not in on_section and "paths-ignore" not in on_section:
        if "push" in on_section or "pull_request" in on_section:
            findings.append(Finding(
                "info", "cost",
                "No path filters on triggers",
                "Workflow runs on all file changes. Documentation-only changes trigger the full pipeline.",
                "Add paths or paths-ignore filters to skip runs for non-code changes (e.g., docs/, *.md).",
                estimated_savings="5-20% fewer unnecessary runs",
            ))

    # --- Check: Deprecated actions ---
    deprecated_patterns = [
        (r"actions/checkout@v[12]\b", "actions/checkout@v4"),
        (r"actions/setup-python@v[1-3]\b", "actions/setup-python@v5"),
        (r"actions/setup-node@v[1-3]\b", "actions/setup-node@v4"),
        (r"actions/cache@v[1-3]\b", "actions/cache@v4"),
        (r"actions/upload-artifact@v[1-3]\b", "actions/upload-artifact@v4"),
        (r"actions/download-artifact@v[1-3]\b", "actions/download-artifact@v4"),
    ]
    for pattern, replacement in deprecated_patterns:
        matches = re.findall(pattern, content)
        if matches:
            findings.append(Finding(
                "warning", "maintenance",
                f"Outdated action: {matches[0]}",
                f"Using an older version of a GitHub action. Older versions may lack features, performance improvements, and security patches.",
                f"Upgrade to {replacement}.",
            ))

    # --- Check: Hardcoded secrets in env ---
    # Look for patterns that might be hardcoded credentials
    suspicious_patterns = [
        (r'(?:password|token|secret|key|api_key)\s*[:=]\s*["\'][^$\{][^"\']{8,}', "Possible hardcoded secret"),
    ]
    for pattern, msg in suspicious_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            findings.append(Finding(
                "critical", "security",
                "Possible hardcoded secret",
                f"Found what appears to be a hardcoded credential in the workflow file.",
                "Use GitHub Secrets (${{ secrets.SECRET_NAME }}) instead of hardcoded values.",
            ))

    # --- Check: Missing permissions block ---
    if "permissions:" not in content:
        findings.append(Finding(
            "warning", "security",
            "No permissions block",
            "Workflow does not restrict permissions. It runs with the default token permissions, which may be overly broad.",
            "Add a top-level 'permissions:' block with least-privilege access (e.g., contents: read).",
        ))

    # --- Check: Using ubuntu-latest without pinning ---
    if "runs-on: ubuntu-latest" in content:
        findings.append(Finding(
            "info", "maintenance",
            "Using ubuntu-latest (unpinned)",
            "ubuntu-latest will change over time as GitHub updates it. This could cause unexpected breakage.",
            "Consider pinning to a specific version (e.g., ubuntu-24.04) for reproducibility, or accept the trade-off for automatic updates.",
        ))

    # --- Cost estimation ---
    cost_estimate = _estimate_cost(content, jobs_in_file)
    file_info["cost_estimate"] = cost_estimate

    # Sort findings by severity
    findings.sort(key=lambda f: Finding.SEVERITY_ORDER.get(f.severity, 99))

    return file_info, findings


def _extract_jobs(content):
    """Extract job names and their content blocks from workflow YAML."""
    jobs = {}
    lines = content.split("\n")
    in_jobs = False
    current_job = None
    current_lines = []
    job_indent = None

    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if stripped.startswith("jobs:"):
            in_jobs = True
            job_indent = indent + 2
            continue

        if not in_jobs:
            continue

        if indent == job_indent and stripped.endswith(":") and not stripped.startswith("-") and not stripped.startswith("#"):
            # Save previous job
            if current_job:
                jobs[current_job] = "\n".join(current_lines)
            current_job = stripped.rstrip(":")
            current_lines = []
        elif current_job is not None:
            if indent < job_indent and stripped and not stripped.startswith("#"):
                # We've left the jobs section
                break
            current_lines.append(line)

    # Save last job
    if current_job:
        jobs[current_job] = "\n".join(current_lines)

    return jobs


def _extract_section(content, section_key):
    """Extract a top-level section from the YAML content."""
    lines = content.split("\n")
    in_section = False
    section_lines = []
    section_indent = None

    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if stripped.startswith(section_key):
            in_section = True
            section_indent = indent
            section_lines.append(line)
            continue

        if in_section:
            if indent <= section_indent and stripped and not stripped.startswith("#"):
                break
            section_lines.append(line)

    return "\n".join(section_lines) if section_lines else ""


def _trace_chain(start_job, needs_map, visited):
    """Trace a dependency chain backwards."""
    chain = [start_job]
    current = start_job
    while current in needs_map and len(needs_map[current]) == 1:
        parent = needs_map[current][0]
        if parent in visited or parent == current:
            break
        visited.add(parent)
        chain.insert(0, parent)
        current = parent
    return chain


def _estimate_cost(content, jobs):
    """Estimate the cost of a single workflow run."""
    total_minutes = 0.0
    total_cost = 0.0
    job_estimates = {}

    for job_name, job_content in jobs.items():
        # Determine runner
        runner_match = re.search(r"runs-on:\s*(\S+)", job_content)
        runner = runner_match.group(1).strip("'\"") if runner_match else "ubuntu-latest"
        # Handle expression syntax
        if "${{" in runner:
            runner = "ubuntu-latest"  # Default assumption

        cost_per_min = RUNNER_COSTS.get(runner, DEFAULT_COST_PER_MIN)

        # Estimate duration from timeout or default
        timeout_match = re.search(r"timeout-minutes:\s*(\d+)", job_content)
        if timeout_match:
            estimated_minutes = int(timeout_match.group(1)) * 0.5  # Assume 50% of timeout
        else:
            # Estimate based on step count
            step_count = job_content.count("- name:") + job_content.count("- uses:")
            estimated_minutes = max(2, step_count * 1.5)

        # Account for matrix
        matrix_match = re.search(r"matrix:", job_content)
        matrix_multiplier = 1
        if matrix_match:
            # Count matrix dimensions
            version_matches = re.findall(r"-\s*'[^']+'\s*$", job_content, re.MULTILINE)
            if version_matches:
                matrix_multiplier = max(1, len(version_matches))

        job_minutes = estimated_minutes * matrix_multiplier
        job_cost = job_minutes * cost_per_min

        job_estimates[job_name] = {
            "runner": runner,
            "estimated_minutes": round(job_minutes, 1),
            "cost_per_run": round(job_cost, 4),
            "matrix_multiplier": matrix_multiplier,
        }

        total_minutes += job_minutes
        total_cost += job_cost

    return {
        "total_estimated_minutes": round(total_minutes, 1),
        "cost_per_run": round(total_cost, 4),
        "monthly_estimate_50_runs": round(total_cost * 50, 2),
        "monthly_estimate_200_runs": round(total_cost * 200, 2),
        "jobs": job_estimates,
    }


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------


def format_report(workflow_results, output_format):
    """Format the analysis report."""
    if output_format == "json":
        output = []
        for file_info, findings in workflow_results:
            output.append({
                "file": file_info,
                "findings": [f.to_dict() for f in findings],
                "summary": {
                    "critical": sum(1 for f in findings if f.severity == "critical"),
                    "warning": sum(1 for f in findings if f.severity == "warning"),
                    "info": sum(1 for f in findings if f.severity == "info"),
                    "total": len(findings),
                },
            })
        return json.dumps(output, indent=2)

    # Human-readable format
    lines = []
    lines.append("=" * 72)
    lines.append("  GitHub Actions Pipeline Analysis Report")
    lines.append("=" * 72)
    lines.append("")

    total_findings = {"critical": 0, "warning": 0, "info": 0}

    for file_info, findings in workflow_results:
        lines.append(f"File: {file_info['name']}")
        lines.append(f"  Path: {file_info['path']}")
        if "line_count" in file_info:
            lines.append(f"  Lines: {file_info['line_count']}")
        lines.append("-" * 50)

        if not findings:
            lines.append("  No issues found. Workflow looks well-optimized!")
            lines.append("")
            continue

        for f in findings:
            severity_icon = {"critical": "[CRITICAL]", "warning": "[WARNING]", "info": "[INFO]"}.get(f.severity, "[?]")
            total_findings[f.severity] = total_findings.get(f.severity, 0) + 1

            lines.append(f"  {severity_icon} {f.title}")
            lines.append(f"    Category: {f.category}")
            lines.append(f"    {f.description}")
            lines.append(f"    Recommendation: {f.recommendation}")
            if f.estimated_savings:
                lines.append(f"    Estimated savings: {f.estimated_savings}")
            lines.append("")

        # Cost estimate
        if "cost_estimate" in file_info:
            ce = file_info["cost_estimate"]
            lines.append("  Cost Estimate:")
            lines.append(f"    Per run: ~{ce['total_estimated_minutes']} min, ~${ce['cost_per_run']:.4f}")
            lines.append(f"    Monthly (50 runs/mo):  ~${ce['monthly_estimate_50_runs']:.2f}")
            lines.append(f"    Monthly (200 runs/mo): ~${ce['monthly_estimate_200_runs']:.2f}")
            if ce.get("jobs"):
                lines.append("    Breakdown by job:")
                for job_name, je in ce["jobs"].items():
                    mult = f" (x{je['matrix_multiplier']} matrix)" if je["matrix_multiplier"] > 1 else ""
                    lines.append(f"      {job_name}: ~{je['estimated_minutes']} min on {je['runner']}{mult}")
            lines.append("")

        lines.append("")

    # Summary
    total = sum(total_findings.values())
    lines.append("=" * 72)
    lines.append("  Summary")
    lines.append("=" * 72)
    lines.append(f"  Files analyzed: {len(workflow_results)}")
    lines.append(f"  Total findings: {total}")
    lines.append(f"    Critical: {total_findings['critical']}")
    lines.append(f"    Warning:  {total_findings['warning']}")
    lines.append(f"    Info:     {total_findings['info']}")
    lines.append("")

    if total_findings["critical"] > 0:
        lines.append("  ACTION REQUIRED: Critical issues found. Address these immediately.")
    elif total_findings["warning"] > 0:
        lines.append("  RECOMMENDED: Warning-level issues found. Address these to improve efficiency.")
    else:
        lines.append("  GOOD: Only informational suggestions found.")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Analyze GitHub Actions workflows for optimization opportunities.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              %(prog)s .github/workflows/
              %(prog)s .github/workflows/ci.yml
              %(prog)s .github/workflows/ --format json
        """),
    )

    parser.add_argument(
        "path",
        help="Path to a workflow file (.yml/.yaml) or a directory containing workflow files.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output", "-o",
        help="Write report to file instead of stdout.",
    )

    args = parser.parse_args()

    target = Path(args.path)

    if not target.exists():
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)

    # Collect workflow files
    workflow_files = []
    if target.is_file():
        if target.suffix in (".yml", ".yaml"):
            workflow_files.append(target)
        else:
            print(f"Error: File is not a YAML file: {target}", file=sys.stderr)
            sys.exit(1)
    elif target.is_dir():
        for ext in ("*.yml", "*.yaml"):
            workflow_files.extend(sorted(target.glob(ext)))
        if not workflow_files:
            print(f"Error: No .yml or .yaml files found in {target}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Error: Path is not a file or directory: {target}", file=sys.stderr)
        sys.exit(1)

    # Analyze
    results = []
    for wf in workflow_files:
        file_info, findings = analyze_workflow_file(wf)
        results.append((file_info, findings))

    # Format output
    report = format_report(results, args.format)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
