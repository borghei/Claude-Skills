---
name: doc-drift-detector
description: >
  Detect documentation drift against code changes, score staleness, validate API docs via AST
  parsing, and audit link integrity. Use when docs fall out of sync with code, preparing
  releases, running CI doc gates, or auditing doc accuracy.
license: MIT + Commons Clause
metadata:
  version: 2.1.0
  author: borghei
  category: engineering
  domain: documentation
  updated: 2026-06-17
  tags: [documentation, staleness, api-docs, drift-analysis]
  python-tools: drift_analyzer.py, doc_staleness_scorer.py, api_doc_validator.py, link_checker.py
  tech-stack: python, git, markdown, documentation
---
# Documentation Drift Detector

The agent detects documentation drift by mapping code directories to their docs, comparing git modification histories, extracting Python function signatures via AST, validating every markdown link and anchor, and scoring freshness on a weighted 0-100 scale. All four CLI tools use the Python standard library only.

## Core Capabilities

- **Full drift analysis** — map docs to code, compare git histories, detect renamed files, version drift, broken references, and structural gaps; classify each issue by category, severity, and fix type.
- **API doc validation** — AST-based extraction of Python signatures/classes compared against markdown API docs (undocumented items, phantom docs, parameter mismatches, deprecations).
- **Staleness scoring** — weighted 0-100 freshness score across five dimensions with CI threshold gates and README-focused mode.
- **Link integrity audit** — validate local files, anchors, cross-document anchors, images, case-sensitivity, and duplicate anchors; optional external URL checks.
- **Drift classification** — structural, factual, referential, temporal, semantic categories, each tagged `[AUTO]`/`[SEMI]`/`[MANUAL]` for fix routing.
- **CI/CD integration** — non-zero exit codes, JSON output, GitHub Actions and pre-commit recipes for ongoing monitoring.

## When to Use

- Docs have fallen out of sync with code — run full drift analysis.
- Preparing a release — gate on aggregate staleness score.
- Running CI doc gates — fail PRs on high/critical drift or broken links.
- Auditing API doc accuracy against Python source.
- Checking README health and link integrity after refactors.

## Clarify First

Before running detection, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which check** — full drift analysis, staleness score, API doc validation, or link audit (selects `drift_analyzer.py` vs `doc_staleness_scorer.py` vs `api_doc_validator.py` vs `link_checker.py`)
- [ ] **Repo & doc/source paths** — the repository and which code and docs directories to compare (the input the tools scan)
- [ ] **Threshold & gate** — minimum severity or staleness threshold for CI failure (sets `--min-severity`/`--threshold` and the exit-code gate)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `drift_analyzer.py` | Full drift analysis between code and docs | `python scripts/drift_analyzer.py <repo> --min-severity high --json` |
| `doc_staleness_scorer.py` | Score documentation freshness 0-100 | `python scripts/doc_staleness_scorer.py <repo> --threshold 60` |
| `api_doc_validator.py` | Validate API docs against Python source (AST) | `python scripts/api_doc_validator.py <src> <docs> --recursive` |
| `link_checker.py` | Audit all markdown links and anchors | `python scripts/link_checker.py <repo> --broken-only` |

All tools: Python 3.8+ stdlib only, `--json` and `--help`, non-zero exit codes for CI, any OS.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-tool-reference.md](references/workflows-and-tool-reference.md)** — quick start, the 5 core workflows (full analysis, API validation, README health, link audit, CI monitoring) with output examples, GitHub Actions + pre-commit recipes, and the complete per-tool parameter/output/exit-code reference. Read when running tools or wiring CI.
- **[references/scoring-categories-and-troubleshooting.md](references/scoring-categories-and-troubleshooting.md)** — the staleness scoring model and weights, the five drift categories, auto-fix vs manual-fix classification, detailed integration points, anti-patterns, troubleshooting table, and success criteria. Read when interpreting results or triaging drift.
- **[references/documentation_standards.md](references/documentation_standards.md)** — README structure, API docs, changelogs, ADRs, docs-as-code standards.
- **[references/drift_prevention_guide.md](references/drift_prevention_guide.md)** — coupling strategies, CI gates, review checklists, and prevention patterns.

## Assets

| Asset | Description |
|-------|-------------|
| [Drift Report Template](assets/drift_report_template.md) | Template for drift analysis reports |
| [Sample Drift Data](assets/sample_drift_data.json) | Sample JSON for testing and demonstration |

## Scope & Limitations

**Covers:**

- Detection of documentation drift against git history for any git repository
- AST-based validation of Python API documentation (function signatures, class definitions, parameters, return types)
- Internal link validation including local files, markdown anchors, cross-document anchors, images, and case-sensitivity checks
- Multi-dimensional staleness scoring with configurable weights and CI/CD threshold enforcement

**Does NOT cover:**

- Non-Python source code API validation -- the AST-based validator only parses Python; for TypeScript, Go, Rust, or Java APIs, use language-specific doc generators and pair with the link checker
- External URL uptime monitoring -- `--check-external` performs one-shot HEAD requests but does not provide continuous monitoring; use the **senior-devops** skill for uptime dashboards
- Automatic documentation rewriting -- tools classify issues as `[AUTO]`, `[SEMI]`, or `[MANUAL]` but do not generate replacement text; use the **code-reviewer** skill for AI-assisted doc suggestions
- Content quality or readability assessment -- staleness scoring measures freshness and structural completeness, not prose quality; see the **standards/communication** library for writing guidelines

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **code-reviewer** | Include drift report in PR review comments | `drift_analyzer.py --json` output feeds into review checklists as a documentation health section |
| **senior-devops** | Add staleness gate to CI/CD pipelines | `doc_staleness_scorer.py --threshold 50` returns exit code 1 on failure, blocking deploys |
| **senior-qa** | Documentation quality as part of QA acceptance | `link_checker.py --json` output merges into QA dashboards alongside test coverage metrics |
| **senior-fullstack** | Validate generated project docs post-scaffold | Run `api_doc_validator.py` against scaffolded `docs/` directory to confirm generated API docs match source |
| **senior-secops** | Audit security documentation currency | `drift_analyzer.py --scope security/` detects when security docs fall behind policy changes |
| **senior-architect** | Architecture decision record (ADR) freshness | `doc_staleness_scorer.py --required-sections "Status,Context,Decision,Consequences"` validates ADR completeness |
