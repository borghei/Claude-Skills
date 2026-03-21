#!/usr/bin/env python3
"""
Release Readiness Scorer for Release Orchestration.

Computes a weighted readiness score (0-100) from release checklist data
with 7 categories. Provides detailed breakdown, recommendations, and
trend tracking across releases.

Gate Logic:
  80-100 = GO (proceed with deployment)
  60-79  = CONDITIONAL (proceed with documented mitigations)
  0-59   = NO-GO (address blockers before release)

Usage:
    python release_readiness_scorer.py --input release_data.json
    python release_readiness_scorer.py --input release_data.json --history history.json
    python release_readiness_scorer.py --input release_data.json --json
    python release_readiness_scorer.py --input release_data.json --format summary
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Scoring configuration
# ---------------------------------------------------------------------------

CATEGORY_WEIGHTS: Dict[str, float] = {
    "tests": 0.25,
    "code_quality": 0.20,
    "documentation": 0.15,
    "security": 0.15,
    "breaking_changes": 0.10,
    "dependencies": 0.10,
    "rollback_plan": 0.05,
}

CATEGORY_DISPLAY_NAMES: Dict[str, str] = {
    "tests": "Tests",
    "code_quality": "Code Quality",
    "documentation": "Documentation",
    "security": "Security",
    "breaking_changes": "Breaking Changes",
    "dependencies": "Dependencies",
    "rollback_plan": "Rollback Plan",
}

DECISION_THRESHOLDS = {
    "go": 80,
    "conditional": 60,
}

CATEGORY_BLOCKER_THRESHOLD = 40


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CategoryScore:
    """Score for a single category."""
    name: str
    display_name: str
    score: float  # 0-100
    weight: float
    weighted_score: float
    checks: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    is_blocker: bool = False

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "score": round(self.score, 1),
            "weight": self.weight,
            "weighted_score": round(self.weighted_score, 1),
            "checks": self.checks,
            "recommendations": self.recommendations,
            "is_blocker": self.is_blocker,
        }


@dataclass
class ReadinessReport:
    """Complete readiness assessment."""
    version: Optional[str]
    timestamp: str
    overall_score: float
    decision: str  # GO, CONDITIONAL, NO-GO
    categories: List[CategoryScore]
    blockers: List[str]
    recommendations: List[str]
    has_category_blocker: bool

    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "overall_score": round(self.overall_score, 1),
            "decision": self.decision,
            "has_category_blocker": self.has_category_blocker,
            "blockers": self.blockers,
            "recommendations": self.recommendations,
            "categories": [c.to_dict() for c in self.categories],
        }


@dataclass
class TrendEntry:
    """Historical release score entry."""
    version: str
    date: str
    score: float
    decision: str


# ---------------------------------------------------------------------------
# Scoring functions per category
# ---------------------------------------------------------------------------

def score_tests(data: Dict) -> CategoryScore:
    """Score the Tests category (25% weight)."""
    checks: Dict[str, Any] = {}
    recommendations: List[str] = []
    score = 100.0

    # Test pass rate
    total_tests = data.get("total_tests", 0)
    passed_tests = data.get("passed_tests", 0)
    if total_tests > 0:
        pass_rate = (passed_tests / total_tests) * 100
        checks["pass_rate"] = f"{pass_rate:.1f}%"
        if pass_rate < 100:
            score -= (100 - pass_rate) * 2  # Heavy penalty for failures
            recommendations.append(f"Fix {total_tests - passed_tests} failing test(s)")
    else:
        checks["pass_rate"] = "No tests found"
        score -= 50
        recommendations.append("Add test suite to the project")

    # Coverage
    coverage = data.get("coverage_percent", None)
    if coverage is not None:
        checks["coverage"] = f"{coverage}%"
        if coverage < 80:
            score -= (80 - coverage) * 0.5
            recommendations.append(f"Increase test coverage from {coverage}% to 80%+")
    else:
        checks["coverage"] = "Not measured"
        score -= 15
        recommendations.append("Configure code coverage reporting")

    # Flaky tests
    flaky_count = data.get("flaky_tests", 0)
    checks["flaky_tests"] = flaky_count
    if flaky_count > 0:
        score -= flaky_count * 5
        recommendations.append(f"Investigate {flaky_count} flaky test(s)")

    # Coverage delta
    coverage_delta = data.get("coverage_delta", None)
    if coverage_delta is not None:
        checks["coverage_delta"] = f"{coverage_delta:+.1f}%"
        if coverage_delta < -2:
            score -= abs(coverage_delta) * 2
            recommendations.append(f"Coverage dropped by {abs(coverage_delta):.1f}% since last release")

    score = max(0, min(100, score))
    weight = CATEGORY_WEIGHTS["tests"]

    return CategoryScore(
        name="tests",
        display_name="Tests",
        score=score,
        weight=weight,
        weighted_score=score * weight,
        checks=checks,
        recommendations=recommendations,
        is_blocker=score < CATEGORY_BLOCKER_THRESHOLD,
    )


def score_code_quality(data: Dict) -> CategoryScore:
    """Score the Code Quality category (20% weight)."""
    checks: Dict[str, Any] = {}
    recommendations: List[str] = []
    score = 100.0

    # Lint errors
    lint_errors = data.get("lint_errors", 0)
    checks["lint_errors"] = lint_errors
    if lint_errors > 0:
        score -= min(lint_errors * 3, 40)
        recommendations.append(f"Fix {lint_errors} lint error(s)")

    # Type errors
    type_errors = data.get("type_errors", 0)
    checks["type_errors"] = type_errors
    if type_errors > 0:
        score -= min(type_errors * 5, 30)
        recommendations.append(f"Fix {type_errors} type error(s)")

    # Complexity violations
    complexity_violations = data.get("complexity_violations", 0)
    checks["complexity_violations"] = complexity_violations
    if complexity_violations > 0:
        score -= min(complexity_violations * 4, 25)
        recommendations.append(f"Refactor {complexity_violations} function(s) with high cyclomatic complexity")

    # Code duplication
    duplication_percent = data.get("duplication_percent", 0)
    checks["duplication"] = f"{duplication_percent}%"
    if duplication_percent > 5:
        score -= min((duplication_percent - 5) * 2, 20)
        recommendations.append(f"Reduce code duplication from {duplication_percent}% to under 5%")

    # Dead code
    dead_code_count = data.get("dead_code_count", 0)
    checks["dead_code"] = dead_code_count
    if dead_code_count > 0:
        score -= min(dead_code_count * 2, 15)
        recommendations.append(f"Remove {dead_code_count} dead code instance(s)")

    score = max(0, min(100, score))
    weight = CATEGORY_WEIGHTS["code_quality"]

    return CategoryScore(
        name="code_quality",
        display_name="Code Quality",
        score=score,
        weight=weight,
        weighted_score=score * weight,
        checks=checks,
        recommendations=recommendations,
        is_blocker=score < CATEGORY_BLOCKER_THRESHOLD,
    )


def score_documentation(data: Dict) -> CategoryScore:
    """Score the Documentation category (15% weight)."""
    checks: Dict[str, Any] = {}
    recommendations: List[str] = []
    score = 100.0

    checklist = {
        "readme_updated": ("README updated", 20),
        "api_docs_current": ("API docs current", 25),
        "changelog_generated": ("Changelog generated", 30),
        "migration_guide": ("Migration guide present", 25),
    }

    for key, (label, penalty) in checklist.items():
        value = data.get(key, False)
        checks[key] = value
        if not value:
            score -= penalty
            recommendations.append(f"{label}")

    score = max(0, min(100, score))
    weight = CATEGORY_WEIGHTS["documentation"]

    return CategoryScore(
        name="documentation",
        display_name="Documentation",
        score=score,
        weight=weight,
        weighted_score=score * weight,
        checks=checks,
        recommendations=recommendations,
        is_blocker=score < CATEGORY_BLOCKER_THRESHOLD,
    )


def score_security(data: Dict) -> CategoryScore:
    """Score the Security category (15% weight)."""
    checks: Dict[str, Any] = {}
    recommendations: List[str] = []
    score = 100.0

    # Secrets in code
    secrets_found = data.get("secrets_found", 0)
    checks["secrets_found"] = secrets_found
    if secrets_found > 0:
        score -= 50  # Hard penalty
        recommendations.append(f"Remove {secrets_found} secret(s) from codebase immediately")

    # Dependency CVEs
    critical_cves = data.get("critical_cves", 0)
    high_cves = data.get("high_cves", 0)
    medium_cves = data.get("medium_cves", 0)
    checks["critical_cves"] = critical_cves
    checks["high_cves"] = high_cves
    checks["medium_cves"] = medium_cves

    if critical_cves > 0:
        score -= critical_cves * 25
        recommendations.append(f"Resolve {critical_cves} critical CVE(s) before release")
    if high_cves > 0:
        score -= high_cves * 10
        recommendations.append(f"Resolve {high_cves} high-severity CVE(s)")
    if medium_cves > 0:
        score -= medium_cves * 3
        if medium_cves > 3:
            recommendations.append(f"Review {medium_cves} medium-severity CVE(s)")

    # SAST clean
    sast_clean = data.get("sast_clean", True)
    checks["sast_clean"] = sast_clean
    if not sast_clean:
        score -= 20
        recommendations.append("Address SAST findings before release")

    score = max(0, min(100, score))
    weight = CATEGORY_WEIGHTS["security"]

    return CategoryScore(
        name="security",
        display_name="Security",
        score=score,
        weight=weight,
        weighted_score=score * weight,
        checks=checks,
        recommendations=recommendations,
        is_blocker=score < CATEGORY_BLOCKER_THRESHOLD,
    )


def score_breaking_changes(data: Dict) -> CategoryScore:
    """Score the Breaking Changes category (10% weight)."""
    checks: Dict[str, Any] = {}
    recommendations: List[str] = []
    score = 100.0

    breaking_count = data.get("breaking_changes_count", 0)
    checks["breaking_changes"] = breaking_count

    if breaking_count > 0:
        # Breaking changes need documentation
        documented = data.get("breaking_changes_documented", False)
        checks["documented"] = documented
        if not documented:
            score -= 40
            recommendations.append("Document all breaking changes in release notes")

        migration_provided = data.get("migration_path_provided", False)
        checks["migration_path"] = migration_provided
        if not migration_provided:
            score -= 30
            recommendations.append("Provide migration path for breaking changes")

        deprecation_notice = data.get("deprecation_notice_given", False)
        checks["deprecation_notice"] = deprecation_notice
        if not deprecation_notice:
            score -= 20
            recommendations.append("Issue deprecation notices before breaking changes")

        # Penalty scales with number of breaking changes
        if breaking_count > 3:
            score -= 10
            recommendations.append(f"Consider splitting {breaking_count} breaking changes across releases")

    score = max(0, min(100, score))
    weight = CATEGORY_WEIGHTS["breaking_changes"]

    return CategoryScore(
        name="breaking_changes",
        display_name="Breaking Changes",
        score=score,
        weight=weight,
        weighted_score=score * weight,
        checks=checks,
        recommendations=recommendations,
        is_blocker=score < CATEGORY_BLOCKER_THRESHOLD,
    )


def score_dependencies(data: Dict) -> CategoryScore:
    """Score the Dependencies category (10% weight)."""
    checks: Dict[str, Any] = {}
    recommendations: List[str] = []
    score = 100.0

    # Lock file consistency
    lock_consistent = data.get("lock_files_consistent", True)
    checks["lock_consistent"] = lock_consistent
    if not lock_consistent:
        score -= 30
        recommendations.append("Regenerate lock files to ensure consistency")

    # Yanked packages
    yanked_packages = data.get("yanked_packages", 0)
    checks["yanked_packages"] = yanked_packages
    if yanked_packages > 0:
        score -= yanked_packages * 15
        recommendations.append(f"Replace {yanked_packages} yanked package(s)")

    # Major upgrades reviewed
    major_upgrades = data.get("major_upgrades_pending", 0)
    major_reviewed = data.get("major_upgrades_reviewed", True)
    checks["major_upgrades_pending"] = major_upgrades
    checks["major_upgrades_reviewed"] = major_reviewed
    if major_upgrades > 0 and not major_reviewed:
        score -= 20
        recommendations.append(f"Review {major_upgrades} pending major dependency upgrade(s)")

    # Outdated dependencies
    outdated_count = data.get("outdated_dependencies", 0)
    checks["outdated"] = outdated_count
    if outdated_count > 10:
        score -= 10
        recommendations.append(f"Update {outdated_count} outdated dependencies")

    score = max(0, min(100, score))
    weight = CATEGORY_WEIGHTS["dependencies"]

    return CategoryScore(
        name="dependencies",
        display_name="Dependencies",
        score=score,
        weight=weight,
        weighted_score=score * weight,
        checks=checks,
        recommendations=recommendations,
        is_blocker=score < CATEGORY_BLOCKER_THRESHOLD,
    )


def score_rollback_plan(data: Dict) -> CategoryScore:
    """Score the Rollback Plan category (5% weight)."""
    checks: Dict[str, Any] = {}
    recommendations: List[str] = []
    score = 100.0

    checklist = {
        "rollback_documented": ("Rollback procedure documented", 35),
        "db_migration_reversible": ("Database migrations reversible", 30),
        "feature_flags_in_place": ("Feature flags in place for new features", 20),
        "monitoring_configured": ("Monitoring and alerting configured", 15),
    }

    for key, (label, penalty) in checklist.items():
        value = data.get(key, False)
        checks[key] = value
        if not value:
            score -= penalty
            recommendations.append(label)

    score = max(0, min(100, score))
    weight = CATEGORY_WEIGHTS["rollback_plan"]

    return CategoryScore(
        name="rollback_plan",
        display_name="Rollback Plan",
        score=score,
        weight=weight,
        weighted_score=score * weight,
        checks=checks,
        recommendations=recommendations,
        is_blocker=score < CATEGORY_BLOCKER_THRESHOLD,
    )


# ---------------------------------------------------------------------------
# Scoring engine
# ---------------------------------------------------------------------------

SCORERS = {
    "tests": score_tests,
    "code_quality": score_code_quality,
    "documentation": score_documentation,
    "security": score_security,
    "breaking_changes": score_breaking_changes,
    "dependencies": score_dependencies,
    "rollback_plan": score_rollback_plan,
}


def compute_readiness(data: Dict) -> ReadinessReport:
    """Compute the full readiness report from input data."""
    version = data.get("version", None)
    categories: List[CategoryScore] = []
    all_recommendations: List[str] = []
    blockers: List[str] = []

    for cat_name, scorer in SCORERS.items():
        cat_data = data.get(cat_name, {})
        cat_score = scorer(cat_data)
        categories.append(cat_score)

        if cat_score.is_blocker:
            blockers.append(
                f"{cat_score.display_name} scored {cat_score.score:.0f}/100 "
                f"(below {CATEGORY_BLOCKER_THRESHOLD} threshold)"
            )

        all_recommendations.extend(
            f"{cat_score.display_name}: {r}" for r in cat_score.recommendations
        )

    overall = sum(c.weighted_score for c in categories)

    has_category_blocker = any(c.is_blocker for c in categories)

    if has_category_blocker:
        decision = "NO-GO"
    elif overall >= DECISION_THRESHOLDS["go"]:
        decision = "GO"
    elif overall >= DECISION_THRESHOLDS["conditional"]:
        decision = "CONDITIONAL"
    else:
        decision = "NO-GO"

    return ReadinessReport(
        version=version,
        timestamp=datetime.now().isoformat(),
        overall_score=overall,
        decision=decision,
        categories=categories,
        blockers=blockers,
        recommendations=all_recommendations,
        has_category_blocker=has_category_blocker,
    )


# ---------------------------------------------------------------------------
# Trend tracking
# ---------------------------------------------------------------------------

def load_history(filepath: str) -> List[TrendEntry]:
    """Load release score history from file."""
    if not os.path.isfile(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return [
            TrendEntry(
                version=e["version"],
                date=e["date"],
                score=e["score"],
                decision=e["decision"],
            )
            for e in data.get("releases", [])
        ]
    except (json.JSONDecodeError, KeyError, OSError):
        return []


def save_history(filepath: str, history: List[TrendEntry], report: ReadinessReport) -> None:
    """Append current release to history file."""
    entries = [
        {"version": e.version, "date": e.date, "score": e.score, "decision": e.decision}
        for e in history
    ]
    entries.append({
        "version": report.version or "unreleased",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "score": round(report.overall_score, 1),
        "decision": report.decision,
    })
    with open(filepath, "w") as f:
        json.dump({"releases": entries}, f, indent=2)


def render_trend(history: List[TrendEntry]) -> str:
    """Render a trend summary."""
    if not history:
        return "  No release history available."

    lines: List[str] = []
    lines.append("  Release Score Trend:")
    lines.append("  " + "-" * 50)

    for entry in history[-10:]:  # Last 10 releases
        bar_len = int(entry.score / 2)
        bar = "#" * bar_len
        lines.append(
            f"    {entry.version:12s} {entry.date}  {entry.score:5.1f}  [{entry.decision:11s}]  {bar}"
        )

    if len(history) >= 2:
        delta = history[-1].score - history[-2].score
        direction = "UP" if delta > 0 else "DOWN" if delta < 0 else "FLAT"
        lines.append(f"\n  Trend: {direction} ({delta:+.1f} from previous release)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_text_report(report: ReadinessReport, history: Optional[List[TrendEntry]] = None) -> str:
    """Render the report as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 60)
    lines.append("  RELEASE READINESS REPORT")
    lines.append("=" * 60)

    if report.version:
        lines.append(f"  Version: {report.version}")
    lines.append(f"  Timestamp: {report.timestamp}")
    lines.append(f"  Overall Score: {report.overall_score:.0f}/100 - {report.decision}")
    lines.append("")

    # Category breakdown
    lines.append("  Category Breakdown:")
    lines.append("  " + "-" * 50)
    for cat in report.categories:
        blocker_mark = " [BLOCKER]" if cat.is_blocker else ""
        lines.append(
            f"    {cat.display_name:20s} {cat.score:5.0f}/100 ({cat.weight * 100:.0f}%) "
            f"-> {cat.weighted_score:5.1f}{blocker_mark}"
        )
    lines.append("")

    # Blockers
    if report.blockers:
        lines.append("  BLOCKERS:")
        for b in report.blockers:
            lines.append(f"    [!] {b}")
        lines.append("")

    # Recommendations
    if report.recommendations:
        lines.append("  Recommendations:")
        for i, r in enumerate(report.recommendations, 1):
            lines.append(f"    {i:2d}. {r}")
        lines.append("")

    # Trend
    if history:
        lines.append(render_trend(history))
        lines.append("")

    # Decision box
    lines.append("-" * 60)
    if report.decision == "GO":
        lines.append("  DECISION: GO - Proceed with deployment")
    elif report.decision == "CONDITIONAL":
        lines.append("  DECISION: CONDITIONAL - Proceed with documented mitigations")
    else:
        lines.append("  DECISION: NO-GO - Address blockers before release")
    lines.append("=" * 60)

    return "\n".join(lines)


def render_summary(report: ReadinessReport) -> str:
    """Render a one-line summary suitable for notifications."""
    version = report.version or "unreleased"
    rec_count = len(report.recommendations)
    rec_text = f" - {rec_count} recommendation(s)" if rec_count > 0 else ""
    return f"Release {version} scored {report.overall_score:.0f}/100 ({report.decision}){rec_text}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Release readiness scorer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input release_data.json
  %(prog)s --input release_data.json --history history.json
  %(prog)s --input release_data.json --json
  %(prog)s --input release_data.json --format summary
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to release data JSON file")
    parser.add_argument("--history", help="Path to release history JSON file for trend tracking")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    parser.add_argument("--format", choices=["full", "summary"], default="full", dest="fmt", help="Output format")

    args = parser.parse_args()

    # Load input data
    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(2)

    try:
        with open(input_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_path}: {e}", file=sys.stderr)
        sys.exit(2)

    # Compute readiness
    report = compute_readiness(data)

    # Load history
    history: Optional[List[TrendEntry]] = None
    if args.history:
        history = load_history(args.history)
        save_history(args.history, history, report)

    # Output
    if args.json_output:
        output = report.to_dict()
        if history:
            output["trend"] = [
                {"version": e.version, "date": e.date, "score": e.score, "decision": e.decision}
                for e in history
            ]
        print(json.dumps(output, indent=2))
    elif args.fmt == "summary":
        print(render_summary(report))
    else:
        print(render_text_report(report, history))

    # Exit code based on decision
    if report.decision == "GO":
        sys.exit(0)
    elif report.decision == "CONDITIONAL":
        sys.exit(0)  # Conditional is still a pass
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
