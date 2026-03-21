#!/usr/bin/env python3
"""
Pre-Flight Checker for Release Orchestration.

Validates repository state before release:
- Branch sync with remote base
- Merge conflict detection (dry-run)
- Secret scanning across staged/committed files
- Gitignore validation for sensitive files
- Uncommitted changes detection
- Conventional commit format validation
- Dependency lock file consistency

Usage:
    python preflight_checker.py --repo /path/to/repo --base main
    python preflight_checker.py --repo . --base main --verbose
    python preflight_checker.py --repo . --base main --json
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Secret patterns
# ---------------------------------------------------------------------------

SECRET_PATTERNS: List[Tuple[str, str]] = [
    # AWS
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"(?i)aws[_\-]?secret[_\-]?access[_\-]?key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}", "AWS Secret Access Key"),
    # GitHub
    (r"ghp_[A-Za-z0-9_]{36}", "GitHub Personal Access Token"),
    (r"gho_[A-Za-z0-9_]{36}", "GitHub OAuth Token"),
    (r"ghs_[A-Za-z0-9_]{36}", "GitHub Server Token"),
    (r"github_pat_[A-Za-z0-9_]{22,}", "GitHub Fine-Grained PAT"),
    # Generic tokens / keys
    (r"(?i)(api[_\-]?key|apikey)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{20,}", "Generic API Key"),
    (r"(?i)(secret|token|password|passwd|pwd)\s*[=:]\s*['\"]?[^\s'\"]{8,}", "Generic Secret/Token"),
    # Stripe
    (r"sk_live_[A-Za-z0-9]{24,}", "Stripe Live Secret Key"),
    (r"rk_live_[A-Za-z0-9]{24,}", "Stripe Restricted Key"),
    # Slack
    (r"xoxb-[0-9A-Za-z\-]{50,}", "Slack Bot Token"),
    (r"xoxp-[0-9A-Za-z\-]{50,}", "Slack User Token"),
    (r"xoxs-[0-9A-Za-z\-]{50,}", "Slack Session Token"),
    # JWT
    (r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}", "JSON Web Token"),
    # Private keys
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private Key"),
    # GCP
    (r"(?i)\"type\"\s*:\s*\"service_account\"", "GCP Service Account JSON"),
    # Connection strings
    (r"(?i)(mongodb|postgres|mysql|redis|amqp)://[^\s'\"]{10,}", "Database Connection String"),
    # Heroku
    (r"(?i)heroku[_\-]?api[_\-]?key\s*[=:]\s*['\"]?[A-Fa-f0-9\-]{36}", "Heroku API Key"),
    # Twilio
    (r"SK[0-9a-fA-F]{32}", "Twilio API Key"),
    # SendGrid
    (r"SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}", "SendGrid API Key"),
    # npm
    (r"npm_[A-Za-z0-9]{36}", "npm Access Token"),
]

COMPILED_SECRET_PATTERNS = [(re.compile(p), name) for p, name in SECRET_PATTERNS]

# Conventional commit pattern
CONVENTIONAL_COMMIT_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\(.+\))?!?:\s.+"
)

# Sensitive files that should be in .gitignore
SENSITIVE_FILES = [
    ".env",
    ".env.local",
    ".env.production",
    ".env.staging",
    ".env.development",
    "credentials.json",
    "service-account.json",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "id_rsa",
    "id_ed25519",
    ".npmrc",
    ".pypirc",
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """Result of a single pre-flight check."""
    name: str
    passed: bool
    message: str
    details: List[str] = field(default_factory=list)
    severity: str = "error"  # error, warning, info


@dataclass
class PreFlightReport:
    """Aggregate pre-flight report."""
    repo_path: str
    base_branch: str
    timestamp: str
    checks: List[CheckResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks if c.severity == "error")

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed and c.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed and c.severity == "warning")

    def to_dict(self) -> Dict:
        return {
            "repo_path": self.repo_path,
            "base_branch": self.base_branch,
            "timestamp": self.timestamp,
            "all_passed": self.all_passed,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "warnings": self.warning_count,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "message": c.message,
                    "severity": c.severity,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def run_git(args: List[str], cwd: str, check: bool = False) -> subprocess.CompletedProcess:
    """Run a git command and return the result."""
    cmd = ["git"] + args
    try:
        return subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, check=check, timeout=30
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="Command timed out")


def get_current_branch(repo: str) -> Optional[str]:
    """Return the current branch name or None if detached."""
    result = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo)
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return None if branch == "HEAD" else branch


def get_tracked_files(repo: str) -> List[str]:
    """Return list of tracked files in the repo."""
    result = run_git(["ls-files"], cwd=repo)
    if result.returncode != 0:
        return []
    return [f for f in result.stdout.strip().split("\n") if f]


def get_recent_commits(repo: str, count: int = 20) -> List[Tuple[str, str]]:
    """Return recent (hash, subject) tuples."""
    result = run_git(
        ["log", f"-{count}", "--pretty=format:%h|%s"],
        cwd=repo,
    )
    if result.returncode != 0:
        return []
    commits = []
    for line in result.stdout.strip().split("\n"):
        if "|" in line:
            hash_, subject = line.split("|", 1)
            commits.append((hash_.strip(), subject.strip()))
    return commits


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_branch_sync(repo: str, base: str) -> CheckResult:
    """Check if the current branch is up to date with the remote base."""
    # Fetch latest
    run_git(["fetch", "origin", base], cwd=repo)

    current = get_current_branch(repo)
    if current is None:
        return CheckResult(
            name="Branch Sync",
            passed=False,
            message="HEAD is detached; cannot determine branch sync status",
            severity="error",
        )

    # Count commits behind and ahead
    result = run_git(
        ["rev-list", "--left-right", "--count", f"origin/{base}...HEAD"],
        cwd=repo,
    )
    if result.returncode != 0:
        return CheckResult(
            name="Branch Sync",
            passed=False,
            message=f"Could not compare with origin/{base}: {result.stderr.strip()}",
            severity="error",
        )

    parts = result.stdout.strip().split()
    behind = int(parts[0]) if len(parts) >= 1 else 0
    ahead = int(parts[1]) if len(parts) >= 2 else 0

    details = [f"Current branch: {current}", f"Behind origin/{base}: {behind}", f"Ahead of origin/{base}: {ahead}"]

    if behind > 0:
        return CheckResult(
            name="Branch Sync",
            passed=False,
            message=f"Branch is {behind} commit(s) behind origin/{base}. Pull or rebase before release.",
            details=details,
            severity="error",
        )

    return CheckResult(
        name="Branch Sync",
        passed=True,
        message=f"Branch is up to date with origin/{base} ({ahead} commit(s) ahead)",
        details=details,
    )


def check_merge_conflicts(repo: str, base: str) -> CheckResult:
    """Dry-run merge to detect conflicts."""
    # Get the merge base
    result = run_git(["merge-base", "HEAD", f"origin/{base}"], cwd=repo)
    if result.returncode != 0:
        return CheckResult(
            name="Merge Conflicts",
            passed=False,
            message=f"Could not find merge base with origin/{base}",
            severity="error",
        )

    # Try merge with --no-commit --no-ff
    result = run_git(
        ["merge", "--no-commit", "--no-ff", f"origin/{base}"],
        cwd=repo,
    )

    # Abort the merge regardless of outcome
    run_git(["merge", "--abort"], cwd=repo)

    if result.returncode != 0:
        conflict_files = []
        for line in result.stdout.split("\n"):
            if "CONFLICT" in line:
                conflict_files.append(line.strip())
        return CheckResult(
            name="Merge Conflicts",
            passed=False,
            message=f"Merge conflicts detected with origin/{base}",
            details=conflict_files or [result.stderr.strip()],
            severity="error",
        )

    return CheckResult(
        name="Merge Conflicts",
        passed=True,
        message=f"No merge conflicts with origin/{base}",
    )


def check_uncommitted_changes(repo: str) -> CheckResult:
    """Check for uncommitted staged or unstaged changes."""
    result = run_git(["status", "--porcelain"], cwd=repo)
    if result.returncode != 0:
        return CheckResult(
            name="Uncommitted Changes",
            passed=False,
            message="Could not determine working tree status",
            severity="error",
        )

    changes = [line for line in result.stdout.strip().split("\n") if line.strip()]
    if changes:
        staged = [l for l in changes if l[0] in "MADRC"]
        unstaged = [l for l in changes if len(l) > 1 and l[1] in "MADRC"]
        untracked = [l for l in changes if l.startswith("??")]

        details = []
        if staged:
            details.append(f"Staged changes: {len(staged)}")
        if unstaged:
            details.append(f"Unstaged changes: {len(unstaged)}")
        if untracked:
            details.append(f"Untracked files: {len(untracked)}")
        details.extend(changes[:10])
        if len(changes) > 10:
            details.append(f"... and {len(changes) - 10} more")

        return CheckResult(
            name="Uncommitted Changes",
            passed=False,
            message=f"Working tree has {len(changes)} uncommitted change(s)",
            details=details,
            severity="error",
        )

    return CheckResult(
        name="Uncommitted Changes",
        passed=True,
        message="Working tree is clean",
    )


def check_secrets(repo: str) -> CheckResult:
    """Scan tracked files for secrets."""
    tracked = get_tracked_files(repo)
    findings: List[str] = []

    # Only scan text-like files
    text_extensions = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
        ".rb", ".php", ".sh", ".bash", ".zsh", ".yml", ".yaml",
        ".json", ".toml", ".ini", ".cfg", ".conf", ".env", ".md",
        ".txt", ".xml", ".html", ".css", ".scss", ".sql", ".tf",
        ".hcl", ".dockerfile", "", ".gitignore", ".env.example",
    }

    for filepath in tracked:
        ext = Path(filepath).suffix.lower()
        name = Path(filepath).name.lower()

        # Skip binary-like and large files
        if ext not in text_extensions and name not in {".env", ".env.example", "dockerfile", "makefile"}:
            continue

        full_path = os.path.join(repo, filepath)
        if not os.path.isfile(full_path):
            continue

        try:
            with open(full_path, "r", errors="ignore") as f:
                for line_no, line in enumerate(f, 1):
                    # Skip comments that are clearly examples/docs
                    stripped = line.strip()
                    if stripped.startswith("#") and ("example" in stripped.lower() or "placeholder" in stripped.lower()):
                        continue
                    for pattern, secret_name in COMPILED_SECRET_PATTERNS:
                        if pattern.search(line):
                            finding = f"{filepath}:{line_no} - {secret_name}"
                            findings.append(finding)
                            break  # One finding per line is enough
        except (OSError, UnicodeDecodeError):
            continue

    if findings:
        return CheckResult(
            name="Secret Scanning",
            passed=False,
            message=f"Found {len(findings)} potential secret(s) in tracked files",
            details=findings[:20] + ([f"... and {len(findings) - 20} more"] if len(findings) > 20 else []),
            severity="error",
        )

    return CheckResult(
        name="Secret Scanning",
        passed=True,
        message="No secrets detected in tracked files",
    )


def check_gitignore(repo: str) -> CheckResult:
    """Validate that .gitignore covers sensitive file patterns."""
    gitignore_path = os.path.join(repo, ".gitignore")
    missing: List[str] = []

    if not os.path.isfile(gitignore_path):
        return CheckResult(
            name="Gitignore Validation",
            passed=False,
            message="No .gitignore file found",
            details=["Create a .gitignore file to protect sensitive files"],
            severity="warning",
        )

    with open(gitignore_path, "r") as f:
        gitignore_content = f.read()

    gitignore_lines = set()
    for line in gitignore_content.split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            gitignore_lines.add(line)

    for sensitive in SENSITIVE_FILES:
        # Check if the pattern or a broader version is covered
        covered = False
        for gi_line in gitignore_lines:
            if sensitive == gi_line:
                covered = True
                break
            # Check if a wildcard covers it: e.g., *.pem covers id_rsa.pem
            if gi_line.startswith("*") and sensitive.endswith(gi_line[1:]):
                covered = True
                break
            # Check if .env* covers .env.local etc.
            if gi_line.endswith("*") and sensitive.startswith(gi_line[:-1]):
                covered = True
                break
            # Check broader patterns like .env*
            if sensitive.startswith(".env") and ".env" in gi_line:
                covered = True
                break
        if not covered:
            # Only flag if the file actually exists
            full = os.path.join(repo, sensitive.replace("*", ""))
            if "*" in sensitive:
                # For glob patterns, just flag as advisory
                missing.append(f"{sensitive} (recommended)")
            elif os.path.exists(full):
                missing.append(f"{sensitive} (exists in repo!)")
            else:
                missing.append(f"{sensitive} (not present, but recommended)")

    if any("exists in repo" in m for m in missing):
        return CheckResult(
            name="Gitignore Validation",
            passed=False,
            message="Sensitive files exist in repo without gitignore coverage",
            details=missing,
            severity="error",
        )

    if missing:
        return CheckResult(
            name="Gitignore Validation",
            passed=True,
            message="Gitignore exists but could cover more patterns",
            details=missing,
            severity="warning",
        )

    return CheckResult(
        name="Gitignore Validation",
        passed=True,
        message=".gitignore covers all recommended sensitive file patterns",
    )


def check_conventional_commits(repo: str, count: int = 20) -> CheckResult:
    """Validate that recent commits follow conventional commit format."""
    commits = get_recent_commits(repo, count)
    if not commits:
        return CheckResult(
            name="Conventional Commits",
            passed=True,
            message="No commits to validate",
            severity="info",
        )

    non_conforming: List[str] = []
    merge_skipped = 0

    for hash_, subject in commits:
        # Skip merge commits
        if subject.startswith("Merge "):
            merge_skipped += 1
            continue
        if not CONVENTIONAL_COMMIT_RE.match(subject):
            non_conforming.append(f"{hash_} {subject}")

    total_checked = len(commits) - merge_skipped
    conforming = total_checked - len(non_conforming)

    if non_conforming:
        pct = (conforming / total_checked * 100) if total_checked > 0 else 0
        severity = "error" if pct < 50 else "warning"
        return CheckResult(
            name="Conventional Commits",
            passed=False,
            message=f"{len(non_conforming)}/{total_checked} recent commits do not follow conventional format ({pct:.0f}% compliant)",
            details=non_conforming[:10],
            severity=severity,
        )

    return CheckResult(
        name="Conventional Commits",
        passed=True,
        message=f"All {total_checked} recent commits follow conventional commit format",
    )


def check_dependency_locks(repo: str) -> CheckResult:
    """Check for dependency lock file consistency."""
    issues: List[str] = []
    found_any = False

    # Node.js
    pkg_json = os.path.join(repo, "package.json")
    pkg_lock = os.path.join(repo, "package-lock.json")
    yarn_lock = os.path.join(repo, "yarn.lock")
    pnpm_lock = os.path.join(repo, "pnpm-lock.yaml")

    if os.path.isfile(pkg_json):
        found_any = True
        has_lock = any(os.path.isfile(f) for f in [pkg_lock, yarn_lock, pnpm_lock])
        if not has_lock:
            issues.append("package.json exists but no lock file found (package-lock.json, yarn.lock, or pnpm-lock.yaml)")

    # Python - pyproject.toml
    pyproject = os.path.join(repo, "pyproject.toml")
    poetry_lock = os.path.join(repo, "poetry.lock")
    if os.path.isfile(pyproject):
        found_any = True
        # Check if it uses poetry
        try:
            with open(pyproject, "r") as f:
                content = f.read()
            if "[tool.poetry]" in content and not os.path.isfile(poetry_lock):
                issues.append("pyproject.toml uses Poetry but poetry.lock is missing")
        except OSError:
            pass

    # Python - requirements.txt
    req_txt = os.path.join(repo, "requirements.txt")
    if os.path.isfile(req_txt):
        found_any = True
        try:
            with open(req_txt, "r") as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("-"):
                        # Check if version is pinned
                        if "==" not in line and ">=" not in line and "<=" not in line and "~=" not in line:
                            if "@" not in line:  # Skip URL-based requirements
                                issues.append(f"requirements.txt:{line_no} - unpinned dependency: {line}")
        except OSError:
            pass

    # Rust
    cargo_toml = os.path.join(repo, "Cargo.toml")
    cargo_lock = os.path.join(repo, "Cargo.lock")
    if os.path.isfile(cargo_toml):
        found_any = True
        if not os.path.isfile(cargo_lock):
            issues.append("Cargo.toml exists but Cargo.lock is missing (required for binaries)")

    # Go
    go_mod = os.path.join(repo, "go.mod")
    go_sum = os.path.join(repo, "go.sum")
    if os.path.isfile(go_mod):
        found_any = True
        if not os.path.isfile(go_sum):
            issues.append("go.mod exists but go.sum is missing")

    if not found_any:
        return CheckResult(
            name="Dependency Locks",
            passed=True,
            message="No dependency manifests detected",
            severity="info",
        )

    if issues:
        return CheckResult(
            name="Dependency Locks",
            passed=False,
            message=f"Found {len(issues)} dependency lock issue(s)",
            details=issues[:15],
            severity="warning",
        )

    return CheckResult(
        name="Dependency Locks",
        passed=True,
        message="All dependency lock files are present and consistent",
    )


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_text_report(report: PreFlightReport, verbose: bool = False) -> str:
    """Render the report as a human-readable text."""
    lines: List[str] = []
    lines.append("=" * 60)
    lines.append("  RELEASE PRE-FLIGHT CHECK")
    lines.append("=" * 60)
    lines.append(f"  Repository: {report.repo_path}")
    lines.append(f"  Base Branch: {report.base_branch}")
    lines.append(f"  Timestamp: {report.timestamp}")
    lines.append("-" * 60)
    lines.append("")

    for check in report.checks:
        icon = "PASS" if check.passed else ("WARN" if check.severity == "warning" else "FAIL")
        marker = f"[{icon}]"
        lines.append(f"  {marker:8s} {check.name}")
        lines.append(f"           {check.message}")
        if verbose and check.details:
            for detail in check.details:
                lines.append(f"             - {detail}")
        lines.append("")

    lines.append("-" * 60)
    status = "ALL CHECKS PASSED" if report.all_passed else "CHECKS FAILED"
    lines.append(f"  Result: {status}")
    lines.append(f"  Passed: {report.passed_count}  Failed: {report.failed_count}  Warnings: {report.warning_count}")
    lines.append("=" * 60)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_preflight(repo: str, base: str) -> PreFlightReport:
    """Run all pre-flight checks and return a report."""
    report = PreFlightReport(
        repo_path=os.path.abspath(repo),
        base_branch=base,
        timestamp=datetime.now().isoformat(),
    )

    # Verify this is a git repo
    result = run_git(["rev-parse", "--is-inside-work-tree"], cwd=repo)
    if result.returncode != 0:
        report.checks.append(CheckResult(
            name="Git Repository",
            passed=False,
            message=f"{repo} is not a git repository",
            severity="error",
        ))
        return report

    report.checks.append(CheckResult(
        name="Git Repository",
        passed=True,
        message="Valid git repository",
    ))

    report.checks.append(check_uncommitted_changes(repo))
    report.checks.append(check_branch_sync(repo, base))
    report.checks.append(check_merge_conflicts(repo, base))
    report.checks.append(check_secrets(repo))
    report.checks.append(check_gitignore(repo))
    report.checks.append(check_conventional_commits(repo))
    report.checks.append(check_dependency_locks(repo))

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-flight checker for release orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --repo . --base main
  %(prog)s --repo /path/to/repo --base develop --verbose
  %(prog)s --repo . --base main --json
        """,
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the git repository (default: current directory)",
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch to check against (default: main)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for each check",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--commits",
        type=int,
        default=20,
        help="Number of recent commits to validate (default: 20)",
    )

    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    if not os.path.isdir(repo):
        print(f"Error: {repo} is not a directory", file=sys.stderr)
        sys.exit(2)

    # Verify git is available
    try:
        subprocess.run(["git", "--version"], capture_output=True, timeout=5)
    except FileNotFoundError:
        print("Error: git is not installed or not in PATH", file=sys.stderr)
        sys.exit(2)
    except subprocess.TimeoutExpired:
        print("Error: git command timed out", file=sys.stderr)
        sys.exit(2)

    if not os.path.isdir(os.path.join(repo, ".git")):
        print(f"Error: {repo} is not a git repository", file=sys.stderr)
        sys.exit(2)

    report = run_preflight(repo, args.base)

    if args.json_output:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(render_text_report(report, verbose=args.verbose))

    sys.exit(0 if report.all_passed else 1)


if __name__ == "__main__":
    main()
