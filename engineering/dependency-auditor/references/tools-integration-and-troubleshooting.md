# Tool Reference, Integration & Troubleshooting

Read this when running the three CLI tools, wiring them into CI/CD or scheduled audits, looking up exact flags/output formats, or diagnosing failures against success-criteria targets.

## Quick Start

```bash
# Scan project for vulnerabilities and licenses
python scripts/dep_scanner.py /path/to/project

# Check license compliance
python scripts/license_checker.py /path/to/project --policy strict

# Plan dependency upgrades
python scripts/upgrade_planner.py deps.json --risk-threshold medium
```

For detailed usage instructions, see [../README.md](../README.md).

## Integration Patterns

### CI/CD Pipeline Integration
```bash
# Security gate in CI
python dep_scanner.py /project --format json --fail-on-high
python license_checker.py /project --policy strict --format json
```

### Scheduled Audits
```bash
# Weekly dependency audit
./audit_dependencies.sh > weekly_report.html
python upgrade_planner.py deps.json --timeline 30days
```

### Development Workflow
```bash
# Pre-commit dependency check
python dep_scanner.py . --quick-scan
python license_checker.py . --warn-conflicts
```

## Tool Reference

### `dep_scanner.py`

**Purpose:** Scans a project directory for dependency manifest and lockfile files across 8+ ecosystems, extracts direct and transitive dependencies, matches them against an offline sample table of about eight well-known advisories (newest from 2024) - not a vulnerability database; a clean result proves nothing, so run npm audit / pip-audit / osv-scanner / govulncheck for real data, and produces a report.

**Usage:**
```bash
python scripts/dep_scanner.py <project_path> [options]
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `project_path` | positional | *(required)* | Path to the project directory to scan |
| `--format` | `text` or `json` | `text` | Output format |
| `--output`, `-o` | string | stdout | Output file path |
| `--fail-on-high` | flag | off | Exit with code 1 if any HIGH-severity vulnerabilities are found |
| `--quick-scan` | flag | off | Perform quick scan (skip transitive dependencies) |

**Example:**
```bash
python scripts/dep_scanner.py /app --format json --output scan.json --fail-on-high
```

**Output Formats:**
- **text** -- Human-readable report with summary, vulnerable dependency list, and numbered recommendations.
- **json** -- Machine-readable JSON with `dependencies`, `scan_summary`, `vulnerabilities_found`, severity counts, and `recommendations` arrays.

### `license_checker.py`

**Purpose:** Analyzes dependency licenses from package metadata and LICENSE files, classifies them by risk tier, detects license compatibility conflicts against the project license, and calculates a compliance score.

**Usage:**
```bash
python scripts/license_checker.py <project_path> [options]
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `project_path` | positional | *(required)* | Path to the project directory to analyze |
| `--inventory` | string | none | Path to a dependency inventory JSON file (output from `dep_scanner.py`) |
| `--format` | `text` or `json` | `text` | Output format |
| `--output`, `-o` | string | stdout | Output file path |
| `--policy` | `permissive` or `strict` | `permissive` | License policy strictness level |
| `--warn-conflicts` | flag | off | Show warnings for potential license conflicts |

**Example:**
```bash
python scripts/license_checker.py /app --policy strict --format json --output licenses.json
```

**Output Formats:**
- **text** -- Compliance report with project license, per-dependency license classification, conflict details, compliance score, and recommendations.
- **json** -- Structured JSON with `project_license`, `dependencies` (each with `license_declared`, `license_detected`, `confidence`), `conflicts`, `compliance_score`, and `risk_assessment`.

### `upgrade_planner.py`

**Purpose:** Reads a dependency inventory JSON file, evaluates semantic versioning gaps against a simulated registry, assesses breaking-change risk, and produces a phased upgrade plan with prioritized recommendations, migration checklists, and rollback procedures.

**Usage:**
```bash
python scripts/upgrade_planner.py <inventory_file> [options]
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `inventory_file` | positional | *(required)* | Path to dependency inventory JSON file |
| `--timeline` | integer | `90` | Timeline for the upgrade plan in days |
| `--format` | `text` or `json` | `text` | Output format |
| `--output`, `-o` | string | stdout | Output file path |
| `--risk-threshold` | `safe`, `low`, `medium`, `high`, or `critical` | `high` | Maximum risk level to include in the plan |
| `--security-only` | flag | off | Only plan upgrades that include security fixes |

**Example:**
```bash
python scripts/upgrade_planner.py scan.json --timeline 30 --risk-threshold medium --format json
```

**Output Formats:**
- **text** -- Phased upgrade plan with per-dependency risk assessment, breaking-change notes, estimated time, rollback complexity, and prioritized recommendations.
- **json** -- Structured JSON with `available_upgrades` (each with `update_type`, `risk_level`, `security_updates`, `breaking_changes`, `priority_score`), `upgrade_statistics`, `risk_assessment`, and `upgrade_plans` arrays.

## Troubleshooting Guide

### Common Issues
1. **False Positives**: Tuning vulnerability detection sensitivity
2. **License Ambiguity**: Resolving unclear or multiple licenses
3. **Breaking Changes**: Managing major version upgrades
4. **Performance Impact**: Optimizing scanning for large codebases

### Resolution Strategies
- Whitelist false positives with documentation
- Contact maintainers for license clarification
- Implement feature flags for risky upgrades
- Use incremental scanning for large projects

## Troubleshooting Table

| Problem | Cause | Solution |
|---------|-------|----------|
| Scanner reports zero dependencies | Dependency files are nested in subdirectories or use non-standard names | Ensure manifest files (`package.json`, `requirements.txt`, `go.mod`, etc.) exist in the scanned path; the scanner uses `rglob` so subdirectories are included |
| False-positive vulnerability match | The offline sample table uses simplified version-range matching without pre-release awareness | Verify the flagged version against the NVD entry; whitelist confirmed false positives in your CI pipeline |
| License detected as UNKNOWN | Package metadata lacks a `license` field and no LICENSE file is present in `node_modules` | Supply a dependency inventory JSON with explicit `license` fields, or manually verify and document the license |
| Upgrade planner shows no available upgrades | The package name does not appear in the internal mock version registry | The planner uses a simulated registry; for real results, extend `_get_latest_version()` to query npm/PyPI/crates.io APIs |
| `--fail-on-high` exits 1 unexpectedly | Transitive dependencies inherit vulnerability matches from lockfile parsing | Use `--quick-scan` to limit analysis to direct dependencies, then investigate transitive matches separately |
| Slow scan on large monorepos | `rglob` traverses `node_modules`, `vendor`, and other heavy directories | Restructure scans to target specific sub-project paths rather than the repository root |
| License conflict reported between permissive licenses | Compatibility matrix does not cover every SPDX identifier variant | Check the `_build_compatibility_matrix()` mapping; add missing SPDX IDs as needed |

## Success Criteria

- **Zero critical CVEs in production dependencies** -- all HIGH/CRITICAL vulnerabilities resolved or documented with approved exceptions before release.
- **License compliance at 100%** -- every direct dependency has a known, classified license; zero UNKNOWN licenses ship to production.
- **No unresolved license conflicts** -- all detected conflicts have documented resolutions or approved waivers.
- **Outdated dependency ratio below 15%** -- at least 85% of direct dependencies are within one minor version of the latest release.
- **Mean Time to Patch (MTTP) under 7 days** -- high-severity vulnerability patches applied within one week of disclosure.
- **Upgrade plan coverage above 90%** -- phased upgrade plans exist for all dependencies with available major or security updates.
- **Scan integration in CI/CD** -- `dep_scanner.py --fail-on-high` runs on every pull request with zero unacknowledged failures.
