---
name: dependency-auditor
description: >
  Scans project dependencies for vulnerabilities, license compliance issues, and
  upgrade opportunities across Python, Node.js, Go, and Rust. Use when auditing
  dependencies, checking licenses, planning upgrades, or assessing supply chain
  security.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: security
  tier: POWERFUL
  updated: 2026-03-31
---
# Dependency Auditor

> **Skill Type:** POWERFUL
> **Category:** Engineering
> **Domain:** Dependency Management & Security

## Overview

The **Dependency Auditor** is a comprehensive toolkit for analyzing, auditing, and managing dependencies across multi-language software projects. This skill provides deep visibility into your project's dependency ecosystem, enabling teams to identify vulnerabilities, ensure license compliance, optimize dependency trees, and plan safe upgrades.

In modern software development, dependencies form complex webs that can introduce significant security, legal, and maintenance risks. A single project might have hundreds of direct and transitive dependencies, each potentially introducing vulnerabilities, license conflicts, or maintenance burden. This skill addresses these challenges through automated analysis and actionable recommendations.

## Core Capabilities

### 1. Vulnerability Scanning & CVE Matching

**Comprehensive Security Analysis**
- Scans dependencies against built-in vulnerability databases
- Matches Common Vulnerabilities and Exposures (CVE) patterns
- Identifies known security issues across multiple ecosystems
- Analyzes transitive dependency vulnerabilities
- Provides CVSS scores and exploit assessments
- Tracks vulnerability disclosure timelines
- Maps vulnerabilities to dependency paths

**Multi-Language Support**
- **JavaScript/Node.js**: package.json, package-lock.json, yarn.lock
- **Python**: requirements.txt, pyproject.toml, Pipfile.lock, poetry.lock
- **Go**: go.mod, go.sum
- **Rust**: Cargo.toml, Cargo.lock
- **Ruby**: Gemfile, Gemfile.lock
- **Java/Maven**: pom.xml, gradle.lockfile
- **PHP**: composer.json, composer.lock
- **C#/.NET**: packages.config, project.assets.json

### 2. License Compliance & Legal Risk Assessment

**License Classification System**
- **Permissive Licenses**: MIT, Apache 2.0, BSD (2-clause, 3-clause), ISC
- **Copyleft (Strong)**: GPL (v2, v3), AGPL (v3)
- **Copyleft (Weak)**: LGPL (v2.1, v3), MPL (v2.0)
- **Proprietary**: Commercial, custom, or restrictive licenses
- **Dual Licensed**: Multi-license scenarios and compatibility
- **Unknown/Ambiguous**: Missing or unclear licensing

**Conflict Detection**
- Identifies incompatible license combinations
- Warns about GPL contamination in permissive projects
- Analyzes license inheritance through dependency chains
- Provides compliance recommendations for distribution
- Generates legal risk matrices for decision-making

### 3. Outdated Dependency Detection

**Version Analysis**
- Identifies dependencies with available updates
- Categorizes updates by severity (patch, minor, major)
- Detects pinned versions that may be outdated
- Analyzes semantic versioning patterns
- Identifies floating version specifiers
- Tracks release frequencies and maintenance status

**Maintenance Status Assessment**
- Identifies abandoned or unmaintained packages
- Analyzes commit frequency and contributor activity
- Tracks last release dates and security patch availability
- Identifies packages with known end-of-life dates
- Assesses upstream maintenance quality

### 4. Dependency Bloat Analysis

**Unused Dependency Detection**
- Identifies dependencies that aren't actually imported/used
- Analyzes import statements and usage patterns
- Detects redundant dependencies with overlapping functionality
- Identifies oversized packages for simple use cases
- Maps actual vs. declared dependency usage

**Redundancy Analysis**
- Identifies multiple packages providing similar functionality
- Detects version conflicts in transitive dependencies
- Analyzes bundle size impact of dependencies
- Identifies opportunities for dependency consolidation
- Maps dependency overlap and duplication

### 5. Upgrade Path Planning & Breaking Change Risk

**Semantic Versioning Analysis**
- Analyzes semver patterns to predict breaking changes
- Identifies safe upgrade paths (patch/minor versions)
- Flags major version updates requiring attention
- Tracks breaking changes across dependency updates
- Provides rollback strategies for failed upgrades

**Risk Assessment Matrix**
- Low Risk: Patch updates, security fixes
- Medium Risk: Minor updates with new features
- High Risk: Major version updates, API changes
- Critical Risk: Dependencies with known breaking changes

**Upgrade Prioritization**
- Security patches: Highest priority
- Bug fixes: High priority
- Feature updates: Medium priority
- Major rewrites: Planned priority
- Deprecated features: Immediate attention

### 6. Supply Chain Security

**Dependency Provenance**
- Verifies package signatures and checksums
- Analyzes package download sources and mirrors
- Identifies suspicious or compromised packages
- Tracks package ownership changes and maintainer shifts
- Detects typosquatting and malicious packages

**Transitive Risk Analysis**
- Maps complete dependency trees
- Identifies high-risk transitive dependencies
- Analyzes dependency depth and complexity
- Tracks influence of indirect dependencies
- Provides supply chain risk scoring

### 7. Lockfile Analysis & Deterministic Builds

**Lockfile Validation**
- Ensures lockfiles are up-to-date with manifests
- Validates integrity hashes and version consistency
- Identifies drift between environments
- Analyzes lockfile conflicts and resolution strategies
- Ensures deterministic, reproducible builds

**Environment Consistency**
- Compares dependencies across environments (dev/staging/prod)
- Identifies version mismatches between team members
- Validates CI/CD environment consistency
- Tracks dependency resolution differences

## Technical Architecture

### Scanner Engine (`dep_scanner.py`)
- Multi-format parser supporting 8+ package ecosystems
- Built-in vulnerability database with 500+ CVE patterns
- Transitive dependency resolution from lockfiles
- JSON and human-readable output formats
- Configurable scanning depth and exclusion patterns

### License Analyzer (`license_checker.py`)
- License detection from package metadata and files
- Compatibility matrix with 20+ license types
- Conflict detection engine with remediation suggestions
- Risk scoring based on distribution and usage context
- Export capabilities for legal review

### Upgrade Planner (`upgrade_planner.py`)
- Semantic version analysis with breaking change prediction
- Dependency ordering based on risk and interdependence
- Migration checklists with testing recommendations
- Rollback procedures for failed upgrades
- Timeline estimation for upgrade cycles

## Use Cases & Applications

### Security Teams
- **Vulnerability Management**: Continuous scanning for security issues
- **Incident Response**: Rapid assessment of vulnerable dependencies
- **Supply Chain Monitoring**: Tracking third-party security posture
- **Compliance Reporting**: Automated security compliance documentation

### Legal & Compliance Teams
- **License Auditing**: Comprehensive license compliance verification
- **Risk Assessment**: Legal risk analysis for software distribution
- **Due Diligence**: Dependency licensing for M&A activities
- **Policy Enforcement**: Automated license policy compliance

### Development Teams
- **Dependency Hygiene**: Regular cleanup of unused dependencies
- **Upgrade Planning**: Strategic dependency update scheduling
- **Performance Optimization**: Bundle size optimization through dep analysis
- **Technical Debt**: Identifying and prioritizing dependency technical debt

### DevOps & Platform Teams
- **Build Optimization**: Faster builds through dependency optimization
- **Security Automation**: Automated vulnerability scanning in CI/CD
- **Environment Consistency**: Ensuring consistent dependencies across environments
- **Release Management**: Dependency-aware release planning

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

## Advanced Features

### Custom Vulnerability Databases
- Support for internal/proprietary vulnerability feeds
- Custom CVE pattern definitions
- Organization-specific risk scoring
- Integration with enterprise security tools

### Policy-Based Scanning
- Configurable license policies by project type
- Custom risk thresholds and escalation rules
- Automated policy enforcement and notifications
- Exception management for approved violations

### Reporting & Dashboards
- Executive summaries for management
- Technical reports for development teams
- Trend analysis and dependency health metrics
- Integration with project management tools

### Multi-Project Analysis
- Portfolio-level dependency analysis
- Shared dependency impact analysis
- Organization-wide license compliance
- Cross-project vulnerability propagation

## Best Practices

### Scanning Frequency
- **Security Scans**: Daily or on every commit
- **License Audits**: Weekly or monthly
- **Upgrade Planning**: Monthly or quarterly
- **Full Dependency Audit**: Quarterly

### Risk Management
1. **Prioritize Security**: Address high/critical CVEs immediately
2. **License First**: Ensure compliance before functionality
3. **Gradual Updates**: Incremental dependency updates
4. **Test Thoroughly**: Comprehensive testing after updates
5. **Monitor Continuously**: Automated monitoring and alerting

### Team Workflows
1. **Security Champions**: Designate dependency security owners
2. **Review Process**: Mandatory review for new dependencies
3. **Update Cycles**: Regular, scheduled dependency updates
4. **Documentation**: Maintain dependency rationale and decisions
5. **Training**: Regular team education on dependency security

## Metrics & KPIs

### Security Metrics
- Mean Time to Patch (MTTP) for vulnerabilities
- Number of high/critical vulnerabilities
- Percentage of dependencies with known vulnerabilities
- Security debt accumulation rate

### Compliance Metrics
- License compliance percentage
- Number of license conflicts
- Time to resolve compliance issues
- Policy violation frequency

### Maintenance Metrics
- Percentage of up-to-date dependencies
- Average dependency age
- Number of abandoned dependencies
- Upgrade success rate

### Efficiency Metrics
- Bundle size reduction percentage
- Unused dependency elimination rate
- Build time improvement
- Developer productivity impact

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

## Future Enhancements

### Planned Features
- Machine learning for vulnerability prediction
- Automated dependency update pull requests
- Integration with container image scanning
- Real-time dependency monitoring dashboards
- Natural language policy definition

### Ecosystem Expansion
- Additional language support (Swift, Kotlin, Dart)
- Container and infrastructure dependencies
- Development tool and build system dependencies
- Cloud service and SaaS dependency tracking

---

## Quick Start

```bash
# Scan project for vulnerabilities and licenses
python scripts/dep_scanner.py /path/to/project

# Check license compliance
python scripts/license_checker.py /path/to/project --policy strict

# Plan dependency upgrades
python scripts/upgrade_planner.py deps.json --risk-threshold medium
```

For detailed usage instructions, see [README.md](README.md).

---

*This skill provides comprehensive dependency management capabilities essential for maintaining secure, compliant, and efficient software projects. Regular use helps teams stay ahead of security threats, maintain legal compliance, and optimize their dependency ecosystems.*

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Scanner reports zero dependencies | Dependency files are nested in subdirectories or use non-standard names | Ensure manifest files (`package.json`, `requirements.txt`, `go.mod`, etc.) exist in the scanned path; the scanner uses `rglob` so subdirectories are included |
| False-positive vulnerability match | Built-in CVE database uses simplified version-range matching without pre-release awareness | Verify the flagged version against the NVD entry; whitelist confirmed false positives in your CI pipeline |
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

## Scope & Limitations

**This skill covers:**
- Parsing dependency manifests and lockfiles for JavaScript/Node.js, Python, Go, Rust, Ruby, Java, PHP, and C#/.NET ecosystems.
- Matching dependencies against a built-in vulnerability database of common CVE patterns with severity scoring.
- Classifying licenses into risk tiers (permissive, weak copyleft, strong copyleft, proprietary, unknown) and detecting conflicts.
- Generating prioritized, phased upgrade plans with breaking-change analysis, rollback procedures, and time estimates.

**This skill does NOT cover:**
- Real-time querying of live vulnerability databases (NVD, OSV, GitHub Advisory); the built-in database is a representative subset. For continuous monitoring, see **skill-security-auditor**.
- Container image or OS-level package scanning. For infrastructure-layer auditing, see **ci-cd-pipeline-builder** or **observability-designer**.
- Automated pull request creation for dependency updates (e.g., Dependabot/Renovate-style). The skill produces plans and reports, not automated code changes.
- Runtime dependency analysis or dynamic import tracing; detection relies on static manifest and lockfile parsing only.

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **skill-security-auditor** | Feed vulnerability scan results into broader security audit workflows | `dep_scanner.py --format json` output consumed as evidence artifacts |
| **ci-cd-pipeline-builder** | Embed dependency gates in CI/CD pipelines | `dep_scanner.py --fail-on-high` and `license_checker.py --policy strict` as pipeline steps |
| **release-manager** | Attach dependency audit reports to release checklists | JSON reports from all three tools included in release documentation |
| **pr-review-expert** | Flag dependency changes during pull request review | Scanner diff between base and head branch dependency files |
| **env-secrets-manager** | Ensure dependency tooling credentials (registry tokens) are securely managed | Registry authentication tokens stored and rotated via secrets manager |
| **observability-designer** | Monitor dependency health metrics over time | Scan summary statistics exported to monitoring dashboards |

## Tool Reference

### `dep_scanner.py`

**Purpose:** Scans a project directory for dependency manifest and lockfile files across 8+ ecosystems, extracts direct and transitive dependencies, matches them against a built-in vulnerability database, and produces a security report.

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

---

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

---

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