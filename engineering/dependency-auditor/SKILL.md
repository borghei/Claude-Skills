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
  updated: 2026-11-08
  tags:
    - dependencies
    - vulnerabilities
    - licenses
    - supply-chain
    - upgrades
---
# Dependency Auditor

Audit a project's dependencies for known vulnerabilities, license risk and upgrade work, and turn the result into a prioritised, phased plan. The real vulnerability data comes from the ecosystem's own auditor; the bundled scripts parse manifests offline, classify licenses from an inventory, and sequence upgrades.

## When to Use

- Auditing a project's dependencies for vulnerabilities or supply-chain risk.
- Checking license compliance before distribution or M&A due diligence.
- Planning safe, phased dependency upgrades.
- Adding a dependency gate to CI/CD, or cleaning up unused dependencies.

## Clarify First

Before running the audit, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Project & ecosystem:** the project path and which manifests/lockfiles exist.
- **Audit focus:** vulnerabilities, license compliance, or upgrade planning.
- **Policy & gate:** the project's license, how strict the license policy is, and which severity fails the build.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Get real vulnerability data first.** The bundled CVE table is a small offline sample (about eight well-known advisories, newest from 2024), so a clean `dep_scanner.py` run proves nothing. Run the ecosystem tool and treat its output as the source of truth:
   `npm audit --json` / `pnpm audit`, `pip-audit -f json`, `govulncheck ./...`, `cargo audit`, `bundle audit`, or `osv-scanner -r .` for any mix. If none can run (no network, no install), say so in the report and label the result "offline heuristic only".
2. **Inventory and offline scan.** `dep_scanner.py` parses manifests and lockfiles (package.json, package-lock.json, yarn.lock, requirements.txt, pyproject.toml, Pipfile.lock, poetry.lock, go.mod, Cargo.toml/lock, Gemfile/lock) and lists direct and transitive dependencies. Use it for the inventory and as a cross-check.
3. **Licenses.** Manifests do not carry each dependency's license, so build an inventory (`npm view <pkg> license`, `pip show`, `go-licenses report`, or a lockfile-aware tool) and pass it with `--inventory`. Dependencies with no license data are listed as **unresolved**, not as conflicts.
4. **Upgrade plan.** Put each dependency's current `version` and registry `latest` in the inventory; `upgrade_planner.py` classifies patch/minor/major, flags known breaking changes and security fixes, and phases the work. Without a `latest` field it falls back to a tiny built-in sample table and skips packages it does not know.
5. **Report.** Lead with exploitable, reachable high-severity issues and license conflicts that block distribution; then the phased upgrades. Say which data was live and which was offline.

```bash
# Offline demo from the skill folder
python3 scripts/dep_scanner.py assets/sample_package.json                 # 3 sample advisories (exit 0)
python3 scripts/dep_scanner.py assets/sample_requirements.txt --fail-on-high  # 2 HIGH -> exit 1
python3 scripts/license_checker.py assets/sample_package.json --inventory assets/sample_inventory.json --warn-conflicts  # GPL-3.0 in an MIT project -> exit 1
python3 scripts/upgrade_planner.py assets/sample_inventory.json --timeline 60   # phased plan, 2 major upgrades
```

Done means: every HIGH/CRITICAL advisory from the live tool has a fix version or an accepted-risk note, no unresolved or conflicting license blocks distribution, and the upgrade phases have owners.

## Tools

| Tool | What it does | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `dep_scanner.py <dir-or-manifest>` | Parse manifests/lockfiles; match against the offline sample CVE table | `--format json`, `--fail-on-high`, `--output` | 0 ok, 1 HIGH found with `--fail-on-high`, 2 path missing or no manifest found |
| `license_checker.py <dir-or-package.json>` | Classify licenses (permissive / weak / strong copyleft / proprietary / unknown), detect conflicts with the project license, score compliance | `--inventory`, `--project-license`, `--policy strict`, `--warn-conflicts` | 0 ok, 1 strict score < 80 or conflicts with `--warn-conflicts`, 2 bad path/inventory |
| `upgrade_planner.py <inventory.json>` | Semver gap, risk, security-fix and breaking-change notes, phased plan | `--timeline`, `--risk-threshold`, `--security-only`, `--format json` | 0 ok, 2 bad inventory |

**Inventory format** (shared by `--inventory` and the planner): a list, or `{"dependencies": [...]}`, of objects with `name` and `version`, plus optional `latest`, `license` (SPDX id), `ecosystem`, `direct`. See `assets/sample_inventory.json`.

## Anti-Patterns

**Mistake:** Reporting "no vulnerabilities" from the offline scanner.
**Why it happens:** The script prints a tidy report either way.
**Instead:** Run the ecosystem auditor or osv-scanner. The bundled table knows about eight advisories, so silence from it means nothing.

**Mistake:** Treating every unknown license as a conflict.
**Why it happens:** Manifests do not carry license data, so everything looks unknown.
**Instead:** Report unresolved licenses as missing data, fetch them, then rerun with `--inventory`.

**Mistake:** Upgrading every outdated package at once.
**Why it happens:** One big PR feels efficient.
**Instead:** Ship security fixes and patch updates first, then minors, then each major on its own with its migration notes and a rollback path.

## Files

- `scripts/dep_scanner.py`, `scripts/license_checker.py`, `scripts/upgrade_planner.py` — the three tools.
- `assets/sample_package.json`, `assets/sample_requirements.txt`, `assets/sample_go.mod` — manifests for the scanner; `assets/sample_inventory.json` — inventory with licenses and latest versions.
- `expected_outputs/` — reference outputs; `test-project/` — a minimal project folder for directory scans.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/capabilities-and-best-practices.md](references/capabilities-and-best-practices.md)** — full breakdown of every analysis capability, the scanner/analyzer/planner internals, use cases by team, advanced/enterprise features, recommended scan cadences, and metrics/KPIs. Read when you need the deep capability or architecture detail.
- **[references/tools-integration-and-troubleshooting.md](references/tools-integration-and-troubleshooting.md)** — quick-start and CI/CD/scheduled-audit integration commands, complete per-tool flag/output reference, the troubleshooting table, and success-criteria targets. Read when running the tools, wiring them into pipelines, or diagnosing failures.
- **[references/vulnerability_assessment_guide.md](references/vulnerability_assessment_guide.md)** — how to assess, prioritize, and remediate dependency vulnerabilities (CVSS, exploitability, disclosure timelines). Read when triaging or responding to security findings.
- **[references/license_compatibility_matrix.md](references/license_compatibility_matrix.md)** — comprehensive license-type reference and compatibility matrix for combining open-source dependencies. Read when resolving license conflicts or making distribution decisions.
- **[references/dependency_management_best_practices.md](references/dependency_management_best_practices.md)** — strategic, governance, security, and operational best practices across the dependency lifecycle. Read when establishing dependency policy or team workflows.

## Scope & Limitations

**This skill covers:** manifest/lockfile parsing for Node.js, Python, Go, Rust and Ruby; license classification and conflict detection from an inventory; phased upgrade planning.

**This skill does NOT cover:**
- Live vulnerability data: use the ecosystem auditor or osv-scanner (step 1). For a broader code audit, see `engineering/security-audit`.
- Container image or OS package scanning (use Trivy, Grype or your registry's scanner).
- Automated update PRs (Dependabot/Renovate); this skill produces plans, not code changes.
- Runtime reachability: detection is static. Reachability-aware tools (govulncheck) give better priority signals.

## Related skills

`engineering/security-audit` (code-level audit), `engineering/ci-cd-pipeline-builder` (wire the gate into CI), `engineering/release-manager` (attach reports to releases).
