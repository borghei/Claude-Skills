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
  updated: 2026-11-08
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

Before running detection, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Which check:** full drift analysis, staleness score, API doc validation, or link audit (selects `drift_analyzer.py` vs `doc_staleness_scorer.py` vs `api_doc_validator.py` vs `link_checker.py`).
- **Repo & doc/source paths:** the repository and which code and docs directories to compare (the input the tools scan).
- **Threshold & gate:** minimum severity or staleness threshold for CI failure (sets `--min-severity`/`--threshold` and the exit-code gate).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Links first** (fast, no git needed): `link_checker.py <docs-dir> --broken-only`. Fix broken files and anchors.
2. **API docs** (Python): `api_doc_validator.py <src> <docs> --recursive` lists documented-but-missing and undocumented functions and classes, and signature mismatches.
3. **Drift against history**: `drift_analyzer.py <repo>` compares doc and code change history (needs a git checkout; on very large repositories use `--scope` to limit it).
4. **Score freshness**: `doc_staleness_scorer.py <repo> --threshold 60` for a 0-100 score per document and an aggregate gate.
5. **Fix** in order: broken links and wrong API signatures (readers act on them), then stale how-tos, then completeness.
6. **Verify** that all four tools exit 0 at the gates you chose before merging.

## Quick Start

```bash
python3 scripts/link_checker.py . --broken-only                       # this skill's own docs: clean (exit 0)
python3 scripts/api_doc_validator.py scripts references --recursive    # undocumented helpers are reported
python3 scripts/drift_analyzer.py /path/to/repo --min-severity medium --fail-on high
python3 scripts/doc_staleness_scorer.py /path/to/repo --threshold 60 --json
```

## Tools Overview

| Tool | What it does | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `link_checker.py <path>` | Local files, anchors (GitHub slug rules), cross-doc anchors, images, case mismatches, duplicate anchors; ignores fenced and inline code | `--broken-only`, `--check-external`, `--json` | 0 clean, 1 broken links or duplicate anchors, 2 bad path |
| `api_doc_validator.py <src> <docs>` | Python AST vs docs: missing, undocumented and mismatched functions/classes/parameters | `--recursive`, `--include-private`, `--json` | 0 no documented-but-missing items, 1 mismatches, 2 bad path |
| `drift_analyzer.py <repo>` | Structural, factual, referential, temporal and semantic drift from git history | `--min-severity` (what to report), `--fail-on` (what fails, default high), `--scope`, `--doc-patterns`, `--json` | 0, 1 issue at/above `--fail-on`, 2 not a directory or not a git checkout |
| `doc_staleness_scorer.py <repo>` | Weighted 0-100 freshness per doc (age, code alignment, links, completeness, accuracy) | `--threshold`, `--readme-focus`, `--required-sections`, `--weight-*`, `--json` | 0, 1 aggregate below threshold, 2 bad path |

All tools are Python stdlib only; `drift_analyzer.py` and the scorer read git history through the `git` command.

## Anti-Patterns

**Mistake:** Gating CI on every low-severity drift finding.
**Why it happens:** Strict gates look rigorous.
**Instead:** Fail on high (the default) and report the rest; a gate that fails on cosmetic drift gets disabled.

**Mistake:** Treating "recently edited" as "accurate".
**Why it happens:** Age is the easiest signal to compute.
**Instead:** Check alignment with the code that changed (drift analyzer, API validator); a doc edited yesterday can still describe last year's API.

**Mistake:** Writing example links in docs as real links.
**Why it happens:** It is the natural way to show syntax.
**Instead:** Put examples in inline code or fenced blocks; the checker ignores them there and reports only real links.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-tool-reference.md](references/workflows-and-tool-reference.md)** — quick start, the 5 core workflows (full analysis, API validation, README health, link audit, CI monitoring) with output examples, GitHub Actions + pre-commit recipes, and the complete per-tool parameter/output/exit-code reference. Read when running tools or wiring CI.
- **[references/scoring-categories-and-troubleshooting.md](references/scoring-categories-and-troubleshooting.md)** — the staleness scoring model and weights, the five drift categories, auto-fix vs manual-fix classification, detailed integration points, anti-patterns, troubleshooting table, and success criteria. Read when interpreting results or triaging drift.
- **[references/documentation_standards.md](references/documentation_standards.md)** — README structure, API docs, changelogs, ADRs, docs-as-code standards.
- **[references/drift_prevention_guide.md](references/drift_prevention_guide.md)** — coupling strategies, CI gates, review checklists, and prevention patterns.

## Files

- `scripts/link_checker.py`, `scripts/api_doc_validator.py`, `scripts/drift_analyzer.py`, `scripts/doc_staleness_scorer.py` — the tools above.
- [assets/drift_report_template.md](assets/drift_report_template.md) — report template; [assets/sample_drift_data.json](assets/sample_drift_data.json) — example of a combined report's shape (illustrative data, not tool input).

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

Related skills: `engineering/code-reviewer` (attach the drift report to PR review), `engineering/senior-devops` (CI gates).
