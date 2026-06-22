---
name: dependency-auditor
description: >
  Scan project dependencies for vulnerabilities, license issues, and upgrade opportunities
  across Python, Node.js, Go, and Rust. Use when auditing dependencies, checking licenses,
  planning upgrades, or assessing supply chain security.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: security
  tier: POWERFUL
  updated: 2026-06-17
---
# Dependency Auditor

A multi-language toolkit for analyzing, auditing, and managing dependencies. It scans manifests and lockfiles across 8+ ecosystems to surface vulnerabilities, classify licenses, detect bloat, and produce safe, phased upgrade plans — giving teams visibility into security, legal, and maintenance risk hidden in their dependency trees.

## Core Capabilities

- **Vulnerability scanning & CVE matching** — match direct/transitive deps against a built-in CVE database with CVSS scoring across Node, Python, Go, Rust, Ruby, Java, PHP, .NET.
- **License compliance** — classify into permissive / weak-copyleft / strong-copyleft / proprietary / unknown tiers and detect incompatible combinations (e.g. GPL contamination).
- **Outdated & maintenance detection** — categorize updates by patch/minor/major severity; flag abandoned or end-of-life packages.
- **Dependency bloat analysis** — find unused, redundant, or oversized packages and consolidation opportunities.
- **Upgrade path planning** — semver breaking-change prediction, risk matrix, prioritization, rollback strategies.
- **Supply chain security** — provenance checks, typosquatting/malicious-package detection, transitive risk scoring.
- **Lockfile analysis** — validate freshness, integrity hashes, and cross-environment consistency for deterministic builds.

## When to Use

- Auditing a project's dependencies for vulnerabilities or supply-chain risk.
- Checking license compliance before distribution or M&A due diligence.
- Planning safe, phased dependency upgrades.
- Adding a dependency security gate to CI/CD.
- Cleaning up unused or redundant dependencies.

## Clarify First

Before running the audit, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Project & ecosystem** — the project path and which manifests/lockfiles (the input the scanner parses)
- [ ] **Audit focus** — vulnerabilities, license compliance, or upgrade planning (selects `dep_scanner.py` vs `license_checker.py` vs `upgrade_planner.py`)
- [ ] **Policy & gate** — license policy strictness and fail-on-severity threshold (sets `--policy`, `--fail-on-high`, and the CI verdict)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `dep_scanner.py` | Scan manifests/lockfiles across 8+ ecosystems, match CVEs, produce a security report | `python scripts/dep_scanner.py /path/to/project --format json --fail-on-high` |
| `license_checker.py` | Classify dependency licenses by risk tier and detect conflicts vs the project license | `python scripts/license_checker.py /path/to/project --policy strict --warn-conflicts` |
| `upgrade_planner.py` | Evaluate semver gaps, assess breaking-change risk, output a phased upgrade plan | `python scripts/upgrade_planner.py deps.json --risk-threshold medium --timeline 30` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/capabilities-and-best-practices.md](references/capabilities-and-best-practices.md)** — full breakdown of every analysis capability, the scanner/analyzer/planner internals, use cases by team, advanced/enterprise features, recommended scan cadences, and metrics/KPIs. Read when you need the deep capability or architecture detail.
- **[references/tools-integration-and-troubleshooting.md](references/tools-integration-and-troubleshooting.md)** — quick-start and CI/CD/scheduled-audit integration commands, complete per-tool flag/output reference, the troubleshooting table, and success-criteria targets. Read when running the tools, wiring them into pipelines, or diagnosing failures.
- **[references/vulnerability_assessment_guide.md](references/vulnerability_assessment_guide.md)** — how to assess, prioritize, and remediate dependency vulnerabilities (CVSS, exploitability, disclosure timelines). Read when triaging or responding to security findings.
- **[references/license_compatibility_matrix.md](references/license_compatibility_matrix.md)** — comprehensive license-type reference and compatibility matrix for combining open-source dependencies. Read when resolving license conflicts or making distribution decisions.
- **[references/dependency_management_best_practices.md](references/dependency_management_best_practices.md)** — strategic, governance, security, and operational best practices across the dependency lifecycle. Read when establishing dependency policy or team workflows.

## Scope & Limitations

**This skill covers:**
- Parsing dependency manifests and lockfiles for JavaScript/Node.js, Python, Go, Rust, Ruby, Java, PHP, and C#/.NET ecosystems.
- Matching dependencies against a built-in vulnerability database of common CVE patterns with severity scoring.
- Classifying licenses into risk tiers (permissive, weak copyleft, strong copyleft, proprietary, unknown) and detecting conflicts.
- Generating prioritized, phased upgrade plans with breaking-change analysis, rollback procedures, and time estimates.

**This skill does NOT cover:**
- Real-time querying of live vulnerability databases (NVD, OSV, GitHub Advisory); the built-in DB is a representative subset. For continuous monitoring, see **skill-security-auditor**.
- Container image or OS-level package scanning. For infrastructure auditing, see **ci-cd-pipeline-builder** or **observability-designer**.
- Automated PR creation for dependency updates (Dependabot/Renovate-style); the skill produces plans and reports, not code changes.
- Runtime dependency analysis or dynamic import tracing; detection is static manifest/lockfile parsing only.

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **skill-security-auditor** | Feed vulnerability scan results into broader security audit workflows | `dep_scanner.py --format json` output consumed as evidence artifacts |
| **ci-cd-pipeline-builder** | Embed dependency gates in CI/CD pipelines | `dep_scanner.py --fail-on-high` and `license_checker.py --policy strict` as pipeline steps |
| **release-manager** | Attach dependency audit reports to release checklists | JSON reports from all three tools included in release documentation |
| **pr-review-expert** | Flag dependency changes during pull request review | Scanner diff between base and head branch dependency files |
| **env-secrets-manager** | Ensure dependency tooling credentials (registry tokens) are securely managed | Registry authentication tokens stored and rotated via secrets manager |
| **observability-designer** | Monitor dependency health metrics over time | Scan summary statistics exported to monitoring dashboards |
