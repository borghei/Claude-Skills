---
name: doc-drift-detector
description: Automated documentation drift detection and synchronization with code change analysis, staleness scoring, and intelligent update recommendations
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: engineering
  domain: documentation
  updated: 2026-03-18
  python-tools: drift_analyzer.py, doc_staleness_scorer.py, api_doc_validator.py, link_checker.py
  tech-stack: python, git, markdown, documentation
---

# Documentation Drift Detector

Automated documentation drift detection and synchronization for codebases of any size. Identifies when documentation falls out of sync with code, scores staleness, validates API docs against source, and audits link integrity -- all with zero external dependencies.

---

## Table of Contents

- [Overview](#overview)
- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
  - [1. Full Drift Analysis](#workflow-1-full-drift-analysis)
  - [2. API Documentation Validation](#workflow-2-api-documentation-validation)
  - [3. README Health Check](#workflow-3-readme-health-check)
  - [4. Link Integrity Audit](#workflow-4-link-integrity-audit)
  - [5. Continuous Doc Monitoring](#workflow-5-continuous-doc-monitoring)
- [Tools](#tools)
- [Staleness Scoring](#staleness-scoring)
- [Drift Categories](#drift-categories)
- [Auto-Fix vs Manual-Fix Classification](#auto-fix-vs-manual-fix-classification)
- [Integration Points](#integration-points)
- [Reference Guides](#reference-guides)
- [Assets](#assets)

---

## Overview

Documentation drift is the silent killer of developer productivity. When docs say one thing and code does another, teams waste hours debugging misunderstandings, onboarding slows to a crawl, and API consumers hit walls that should never exist.

This skill provides four Python CLI tools that work together to detect, measure, classify, and report documentation drift. Unlike basic file-date comparisons, these tools perform semantic analysis: mapping code directories to their documentation, extracting function signatures to compare against API docs, validating every link and anchor, and scoring freshness on a weighted 0-100 scale.

**What sets this apart:**

- **Code-to-doc mapping** -- automatically discovers which docs describe which code directories
- **AST-based API validation** -- parses Python source with the `ast` module to compare real signatures against documented ones
- **Weighted staleness scoring** -- five dimensions scored independently, then combined with configurable weights
- **Drift classification** -- categorizes every issue as structural, factual, referential, temporal, or semantic
- **Auto-fix triage** -- tells you which issues can be fixed automatically vs. which need human judgment
- **CI/CD ready** -- exit codes, JSON output, and threshold flags for pipeline integration

**Standard library only.** No pip installs. No ML calls. No network requests (except optional URL validation). Drop the scripts into any Python 3.8+ environment and run.

---

## Keywords

documentation drift, doc sync, staleness detection, API documentation validation, link checker, markdown analysis, documentation quality, code-doc alignment, README health, changelog validation, documentation CI/CD, documentation gates, broken links, anchor validation, documentation scoring, freshness metrics

---

## Quick Start

```bash
# 1. Run full drift analysis on a repository
python scripts/drift_analyzer.py /path/to/repo

# 2. Score documentation freshness
python scripts/doc_staleness_scorer.py /path/to/repo

# 3. Validate API docs against Python source
python scripts/api_doc_validator.py /path/to/repo/src /path/to/repo/docs/api.md

# 4. Check all markdown links
python scripts/link_checker.py /path/to/repo

# JSON output for any tool
python scripts/drift_analyzer.py /path/to/repo --json

# Set failure threshold for CI
python scripts/doc_staleness_scorer.py /path/to/repo --threshold 60
```

All tools support `--help` for full usage details.

---

## Core Workflows

### Workflow 1: Full Drift Analysis

Scan all documentation against code changes since each doc was last updated. This is the primary entry point for understanding the overall drift state of a repository.

```bash
# Basic analysis
python scripts/drift_analyzer.py /path/to/repo

# Analyze with custom doc patterns
python scripts/drift_analyzer.py /path/to/repo --doc-patterns "*.md,*.rst,*.txt"

# JSON output for tooling
python scripts/drift_analyzer.py /path/to/repo --json

# Only show high-severity drift
python scripts/drift_analyzer.py /path/to/repo --min-severity high

# Analyze specific directory
python scripts/drift_analyzer.py /path/to/repo --scope src/
```

**What it does:**

1. Discovers all documentation files in the repo
2. For each doc, identifies the code directories it describes (via path proximity and content references)
3. Compares the doc's last-modified date against the git history of its associated code
4. Identifies specific changes (renamed files, moved directories, changed function signatures)
5. Classifies each drift instance by category and severity
6. Generates an actionable report with specific file:line references

**Output example:**

```
Documentation Drift Report
==========================
Repository: /path/to/repo
Scan date:  2026-03-18
Docs found: 12
Drifted:    5

HIGH SEVERITY:
  docs/api.md (last updated: 2026-01-15)
    - 23 code files changed since doc update
    - 4 functions renamed in src/handlers/
    - 2 new modules undocumented
    Category: Factual + Structural
    Recommendation: Manual update required

MEDIUM SEVERITY:
  README.md (last updated: 2026-02-28)
    - Installation section references removed dependency
    - Version string outdated (says 1.8.0, current 2.0.0)
    Category: Factual + Temporal
    Recommendation: Auto-fixable (version), Manual (installation)
```

### Workflow 2: API Documentation Validation

Check that API documentation accurately reflects the actual function signatures, class definitions, and module structure in your Python source code.

```bash
# Validate API docs against source
python scripts/api_doc_validator.py /path/to/src /path/to/docs/api.md

# Scan entire docs directory
python scripts/api_doc_validator.py /path/to/src /path/to/docs/ --recursive

# JSON output
python scripts/api_doc_validator.py /path/to/src /path/to/docs/api.md --json

# Include private methods in validation
python scripts/api_doc_validator.py /path/to/src /path/to/docs/ --include-private
```

**What it detects:**

- Functions/classes present in code but missing from docs
- Functions/classes documented but no longer in code (removed or renamed)
- Parameter mismatches (missing params, wrong types, wrong defaults)
- Deprecated items still documented as current
- Return type mismatches
- Module-level docstring drift

**How it works:**

The tool uses Python's `ast` module to parse source files and extract function signatures, class definitions, decorators, and docstrings. It then parses the markdown documentation looking for function/class references, parameter lists, and code blocks. Mismatches are reported with exact locations in both source and documentation.

### Workflow 3: README Health Check

Validate README sections against the actual project state. This combines drift analysis, link checking, and completeness scoring into a single README-focused report.

```bash
# Check README health
python scripts/doc_staleness_scorer.py /path/to/repo --readme-focus

# Check with custom sections
python scripts/doc_staleness_scorer.py /path/to/repo --required-sections "Installation,Usage,API,Contributing,License"
```

**Validates:**

- Required sections are present (Installation, Usage, API Reference, Contributing, License)
- Version strings match package version (package.json, setup.py, pyproject.toml)
- File references in README actually exist
- Badge URLs are well-formed
- Code examples reference existing files/functions
- Table of contents matches actual headings

### Workflow 4: Link Integrity Audit

Check every link in every markdown file -- local file references, anchors, cross-document links, and optionally external URLs.

```bash
# Check all markdown links
python scripts/link_checker.py /path/to/repo

# Include external URL checks (slower, makes HTTP requests)
python scripts/link_checker.py /path/to/repo --check-external

# Check specific file
python scripts/link_checker.py /path/to/repo/README.md

# JSON output
python scripts/link_checker.py /path/to/repo --json

# Only show broken links
python scripts/link_checker.py /path/to/repo --broken-only
```

**What it checks:**

- Local file references (`[link](path/to/file.md)`) -- does the file exist?
- Anchor references (`[link](#section-name)`) -- does the heading exist?
- Cross-document anchors (`[link](other.md#section)`) -- does the file and heading exist?
- Relative path correctness (catches `../` errors)
- Case sensitivity issues (common on Linux but silent on macOS)
- Image references -- do referenced images exist?
- Duplicate anchors that would cause ambiguous links

### Workflow 5: Continuous Doc Monitoring

Integrate documentation drift detection into your CI/CD pipeline for ongoing monitoring.

**GitHub Actions example:**

```yaml
name: Documentation Drift Check
on:
  pull_request:
    branches: [main, dev]
  push:
    branches: [main]

jobs:
  doc-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git log analysis

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run drift analysis
        run: python engineering/doc-drift-detector/scripts/drift_analyzer.py . --json > drift-report.json

      - name: Check staleness score
        run: python engineering/doc-drift-detector/scripts/doc_staleness_scorer.py . --threshold 50

      - name: Validate API docs
        run: python engineering/doc-drift-detector/scripts/api_doc_validator.py src/ docs/api.md

      - name: Check links
        run: python engineering/doc-drift-detector/scripts/link_checker.py .

      - name: Upload drift report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: drift-report
          path: drift-report.json
```

**Pre-commit hook:**

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Fail commit if docs are severely stale
python engineering/doc-drift-detector/scripts/doc_staleness_scorer.py . --threshold 30 --quiet
if [ $? -ne 0 ]; then
    echo "Documentation is critically stale. Update docs before committing."
    exit 1
fi
```

---

## Tools

| Tool | Purpose | Lines | Key Feature |
|------|---------|-------|-------------|
| `drift_analyzer.py` | Full drift analysis between code and docs | ~550 | Git history comparison with code-to-doc mapping |
| `doc_staleness_scorer.py` | Score documentation freshness 0-100 | ~450 | Weighted multi-dimensional scoring |
| `api_doc_validator.py` | Validate API docs against Python source | ~400 | AST-based signature extraction and comparison |
| `link_checker.py` | Audit all markdown links and anchors | ~400 | Local file, anchor, and cross-document validation |

All tools:
- Python 3.8+ standard library only
- Support `--json` for machine-readable output
- Support `--help` for usage details
- Use non-zero exit codes on failure (CI/CD compatible)
- Work on any OS (Windows, macOS, Linux)

---

## Staleness Scoring

Documentation freshness is scored on a **0-100 scale** where **100 = perfectly current**. The score is a weighted combination of five dimensions:

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **Last Updated** | 20% | How recently the doc file was modified relative to its associated code |
| **Code-Doc Alignment** | 30% | Whether documented items (functions, classes, files) still exist and match |
| **Link Health** | 15% | Percentage of links that resolve correctly |
| **Completeness** | 20% | Whether expected sections are present and non-empty |
| **Accuracy** | 15% | Whether version strings, file paths, and other verifiable facts are correct |

**Score interpretation:**

| Score | Label | Action |
|-------|-------|--------|
| 90-100 | Excellent | No action needed |
| 70-89 | Good | Minor updates recommended |
| 50-69 | Stale | Updates needed before next release |
| 30-49 | Critical | Immediate attention required |
| 0-29 | Abandoned | Full rewrite likely needed |

**Customization:**

```bash
# Override default weights
python scripts/doc_staleness_scorer.py /path/to/repo \
  --weight-updated 0.25 \
  --weight-alignment 0.25 \
  --weight-links 0.15 \
  --weight-completeness 0.20 \
  --weight-accuracy 0.15

# Set staleness thresholds
python scripts/doc_staleness_scorer.py /path/to/repo --threshold 60
```

---

## Drift Categories

Every detected drift instance is classified into one or more categories:

### Structural Drift
Missing or misorganized sections. A README lacks an Installation section. An API doc is missing an entire module. A CHANGELOG has no entries for the latest version.

**Detection:** Compare actual document headings against expected headings for that document type.

### Factual Drift
Incorrect information. A function signature in the docs has the wrong parameters. An installation command references a removed package. A configuration example uses deprecated options.

**Detection:** Cross-reference documented facts against code analysis (AST parsing, file existence, git tags).

### Referential Drift
Broken references. A link points to a file that was moved. An anchor references a heading that was renamed. An image path is wrong.

**Detection:** Link checker validates every reference against the filesystem and document structure.

### Temporal Drift
Outdated time-sensitive content. Version strings are old. "Last updated" dates are stale. "Coming soon" items that shipped months ago. Roadmap items past their target date.

**Detection:** Extract version strings and dates, compare against git tags, package manifests, and current date.

### Semantic Drift
Technically accurate but misleading. A description says "simple REST API" when the project now has GraphQL, gRPC, and WebSocket endpoints. The architecture overview omits a major new subsystem.

**Detection:** Compare document topic coverage against code directory structure and file counts. Flag when code complexity has grown significantly but documentation scope has not.

---

## Auto-Fix vs Manual-Fix Classification

Not all drift can be fixed programmatically. The tools classify each issue:

### Auto-Fixable (safe to automate)

- **Version string updates** -- replace old version with current from package manifest
- **Date updates** -- update "last modified" timestamps
- **Broken local links** -- suggest correct path when file was moved (git log tracks renames)
- **Missing table of contents entries** -- generate from actual headings
- **Removed file references** -- flag for deletion or suggest replacement

### Manual-Fix Required (needs human judgment)

- **Architectural description changes** -- requires understanding intent
- **API usage examples** -- new examples need domain context
- **Migration guides** -- require understanding of breaking changes
- **Getting started rewrites** -- narrative flow needs human touch
- **Security documentation updates** -- compliance implications require review

### Semi-Automated (template + human review)

- **New function documentation** -- generate skeleton from AST, human fills description
- **Changelog entries** -- generate from git commits, human edits for clarity
- **README section additions** -- provide template, human adds content

The drift report marks each issue with `[AUTO]`, `[MANUAL]`, or `[SEMI]` tags.

---

## Integration Points

### With CI/CD Pipelines

All tools return non-zero exit codes when issues are found:
- Exit 0: No issues (or all within threshold)
- Exit 1: Issues found exceeding threshold
- Exit 2: Tool error (invalid arguments, missing files)

### With Code Review

Add drift analysis to PR checks. When a PR modifies code in `src/`, automatically check whether docs in `docs/` need updates. The drift analyzer can scope its analysis to only changed directories.

### With Documentation Generators

Pair with tools like Sphinx, MkDocs, or mdBook. Run API validation after doc generation to ensure the generated docs match source. Run link checker on the built output.

### With Release Processes

Add staleness scoring to release checklists. Block releases if documentation score falls below threshold. Generate drift reports as release artifacts.

### With Other Skills

- **code-reviewer** -- include doc drift in PR review reports
- **senior-devops** -- integrate into deployment pipelines
- **senior-qa** -- documentation quality as part of QA checklist

---

## Reference Guides

| Guide | Description |
|-------|-------------|
| [Documentation Standards](references/documentation_standards.md) | README structure, API docs, changelogs, ADRs, docs-as-code |
| [Drift Prevention Guide](references/drift_prevention_guide.md) | Coupling strategies, CI gates, review checklists, prevention patterns |

---

## Assets

| Asset | Description |
|-------|-------------|
| [Drift Report Template](assets/drift_report_template.md) | Template for drift analysis reports |
| [Sample Drift Data](assets/sample_drift_data.json) | Sample JSON for testing and demonstration |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `drift_analyzer.py` reports zero docs found | Repository has non-standard doc extensions or docs are in ignored directories (e.g., `node_modules`, `dist`) | Use `--doc-patterns "*.md,*.rst,*.txt"` to explicitly specify extensions |
| Staleness scores are unexpectedly low | Docs reference files that were reorganized or moved to new directories | Run `link_checker.py` first to identify broken references, fix them, then re-score |
| API validator finds no source signatures | Source path points to a non-Python directory or all functions are `_`-prefixed private | Verify `source_path` contains `.py` files; add `--include-private` if the API surface uses private names |
| Link checker flags valid anchors as broken | Heading text contains special characters, inline code, or emoji that alter the slug | Compare the expected slug (lowercase, special chars stripped, spaces to hyphens) against the actual heading text |
| Git history comparison shows no changes | Shallow clone lacks full commit history (common in CI) | Clone with `fetch-depth: 0` or pass `--scope` to narrow the analysis window |
| External URL checks hang or time out | Target servers are slow or block automated HEAD requests | Omit `--check-external` for local-only validation, or run external checks in a separate non-blocking job |
| Drift report marks everything as `[MANUAL]` | Most detected drift is semantic or architectural, not auto-fixable | This is expected for large refactors; focus on `[AUTO]` and `[SEMI]` items first, then triage `[MANUAL]` items by severity |

---

## Success Criteria

- **Zero stale docs older than 90 days** -- every documentation file has been updated within the last 90 days relative to its associated code changes
- **Aggregate staleness score above 80/100** -- the repository-wide freshness score stays in the "Good" or "Excellent" range
- **Link integrity above 99%** -- fewer than 1% of internal links (file references, anchors, cross-document links) are broken
- **API doc coverage above 95%** -- at least 95% of public functions and classes have corresponding entries in API documentation
- **Zero high-severity drift issues in CI** -- pull requests with high or critical drift are blocked before merge
- **Version string accuracy at 100%** -- every version reference in documentation matches the current release tag or package manifest
- **Drift report turnaround under 60 seconds** -- full drift analysis completes in under one minute for repositories with up to 500 documentation files

---

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

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **code-reviewer** | Include drift report in PR review comments | `drift_analyzer.py --json` output feeds into review checklists as a documentation health section |
| **senior-devops** | Add staleness gate to CI/CD pipelines | `doc_staleness_scorer.py --threshold 50` returns exit code 1 on failure, blocking deploys |
| **senior-qa** | Documentation quality as part of QA acceptance | `link_checker.py --json` output merges into QA dashboards alongside test coverage metrics |
| **senior-fullstack** | Validate generated project docs post-scaffold | Run `api_doc_validator.py` against scaffolded `docs/` directory to confirm generated API docs match source |
| **senior-secops** | Audit security documentation currency | `drift_analyzer.py --scope security/` detects when security docs fall behind policy changes |
| **senior-architect** | Architecture decision record (ADR) freshness | `doc_staleness_scorer.py --required-sections "Status,Context,Decision,Consequences"` validates ADR completeness |

---

## Tool Reference

### drift_analyzer.py

**Purpose:** Scan a git repository for documentation that has fallen out of sync with code. Maps documentation files to their associated code directories, compares git modification dates, detects renamed files, version string drift, broken references, and structural gaps. Classifies every issue by category, severity, and fix type.

**Usage:**

```bash
python scripts/drift_analyzer.py <repo_path> [options]
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `repo_path` | positional | *(required)* | Path to the git repository to analyze |
| `--json` | flag | off | Output the full drift report as JSON |
| `--min-severity` | choice | `low` | Minimum severity to include in report. Choices: `critical`, `high`, `medium`, `low`, `info` |
| `--scope` | string | `""` (all) | Limit code analysis to a subdirectory (e.g., `src/`) |
| `--doc-patterns` | string | `*.md,*.rst,*.txt,*.adoc` | Comma-separated file patterns for documentation discovery |

**Example:**

```bash
python scripts/drift_analyzer.py /path/to/repo --min-severity medium --scope src/ --json
```

**Output Formats:**

- **Human-readable** (default): Grouped by severity with `[AUTO]`/`[SEMI]`/`[MANUAL]` fix-type tags, category labels, and a fix-type summary
- **JSON** (`--json`): Structured object with `repository`, `scan_date`, `summary` (counts by severity, category, fix type), and `issues` array

**Exit Codes:** 0 = no high/critical issues, 1 = high or critical issues found, 2 = tool error (invalid path, not a git repo)

---

### doc_staleness_scorer.py

**Purpose:** Score documentation freshness on a weighted 0-100 scale across five dimensions: last updated, code-doc alignment, link health, completeness, and accuracy. Supports CI/CD threshold gates and README-focused analysis.

**Usage:**

```bash
python scripts/doc_staleness_scorer.py <repo_path> [options]
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `repo_path` | positional | *(required)* | Path to the git repository to score |
| `--json` | flag | off | Output the full scoring report as JSON |
| `--threshold` | float | *(none)* | Fail with exit code 1 if aggregate score falls below this value |
| `--readme-focus` | flag | off | Only score README files (filenames starting with `readme`) |
| `--required-sections` | string | `Installation,Usage,API,Contributing,License` | Comma-separated section names for completeness scoring |
| `--quiet` | flag | off | Only print the aggregate score number (no report) |
| `--weight-updated` | float | `0.20` | Weight for the "last updated" dimension |
| `--weight-alignment` | float | `0.30` | Weight for the "code-doc alignment" dimension |
| `--weight-links` | float | `0.15` | Weight for the "link health" dimension |
| `--weight-completeness` | float | `0.20` | Weight for the "completeness" dimension |
| `--weight-accuracy` | float | `0.15` | Weight for the "accuracy" dimension |

**Example:**

```bash
python scripts/doc_staleness_scorer.py /path/to/repo --threshold 60 --readme-focus --quiet
```

**Output Formats:**

- **Human-readable** (default): Aggregate score with label, per-file score table sorted worst-first, and dimension breakdown with ASCII bars for the bottom 5 files
- **JSON** (`--json`): Structured object with `aggregate_score`, `aggregate_label`, `total_documents`, and `documents` array (each with `total_score`, `label`, and per-dimension scores/details)
- **Quiet** (`--quiet`): Single line with the aggregate score (e.g., `72.3`)

**Exit Codes:** 0 = score above threshold (or no threshold set), 1 = score below threshold, 2 = tool error

---

### api_doc_validator.py

**Purpose:** Extract function and class signatures from Python source files using the `ast` module and compare them against API documentation in markdown files. Detects undocumented items, phantom documentation for removed code, parameter mismatches, and deprecated items.

**Usage:**

```bash
python scripts/api_doc_validator.py <source_path> <doc_path> [options]
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `source_path` | positional | *(required)* | Path to a Python source file or directory |
| `doc_path` | positional | *(required)* | Path to API documentation file (`.md`) or directory |
| `--json` | flag | off | Output the validation report as JSON |
| `--recursive` | flag | off | Recursively scan the doc directory for markdown files |
| `--include-private` | flag | off | Include `_`-prefixed private functions and classes in validation |

**Example:**

```bash
python scripts/api_doc_validator.py /path/to/src /path/to/docs/ --recursive --include-private --json
```

**Output Formats:**

- **Human-readable** (default): Summary counts (source signatures, documented items, issues), then issues grouped by severity with type tags, source/doc file locations, and a summary-by-type table
- **JSON** (`--json`): Structured object with `summary` (counts by type and severity) and `issues` array (each with `type`, `severity`, `name`, file/line references, and `description`)

**Exit Codes:** 0 = no high-severity issues, 1 = high-severity issues found (e.g., documented items missing from source), 2 = tool error

---

### link_checker.py

**Purpose:** Scan markdown files for every link type (local files, anchors, cross-document anchors, images, HTML links, reference-style links) and validate them against the filesystem and document headings. Optionally validates external URLs via HTTP HEAD requests. Also detects duplicate heading anchors.

**Usage:**

```bash
python scripts/link_checker.py <path> [options]
```

**Parameters:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `path` | positional | *(required)* | File or directory to check (single `.md` file or directory for recursive scan) |
| `--json` | flag | off | Output the link check report as JSON |
| `--broken-only` | flag | off | Only show broken links in the report (omit valid links from output) |
| `--check-external` | flag | off | Also validate external URLs via HTTP HEAD requests (slower, makes network requests) |

**Example:**

```bash
python scripts/link_checker.py /path/to/repo --broken-only --json
```

**Output Formats:**

- **Human-readable** (default): Summary counts (total, valid, broken, skipped, duplicate anchors), broken links grouped by source file with line numbers and error messages, duplicate anchor list, and link-type breakdown table
- **JSON** (`--json`): Structured object with `summary` (counts), `broken_links` array (each with source file, line, text, target, type, error), `duplicate_anchors` map, and optionally `all_links` (when `--broken-only` is not set)

**Exit Codes:** 0 = no broken links and no duplicate anchors, 1 = broken links or duplicate anchors found, 2 = tool error

---

**Last Updated:** 2026-03-18
**Version:** 2.0.0
**Tools:** 4 Python CLI tools, 0 external dependencies
**Compatibility:** Python 3.8+, any OS, any git repository
