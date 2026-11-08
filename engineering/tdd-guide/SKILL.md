---
name: tdd-guide
description: >
  Guide red-green-refactor TDD with test generation, coverage-gap analysis, and multi-
  framework support. Use when writing tests first, analyzing coverage, generating test stubs,
  or converting tests between Jest, Pytest, JUnit, and Vitest.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: testing
  updated: 2026-11-08
  tags: [tdd, test-driven-development, testing, red-green-refactor]
---
# TDD Guide

The agent guides red-green-refactor TDD workflows, generates framework-specific test stubs from requirements, parses coverage reports to identify prioritized gaps, and calculates test quality metrics including smell detection and assertion density. Supports Jest, Pytest, JUnit, Vitest, and Mocha.

## Core Capabilities

- **Red-green-refactor guidance** — phase validation (RED/GREEN/REFACTOR), cycle tracking, refactoring suggestions
- **Test generation** — produce test cases and framework-specific stubs from user stories, acceptance criteria, and API specs
- **Coverage gap analysis** — parse LCOV/JSON/XML reports, identify files below threshold, prioritize P0/P1/P2
- **Test quality metrics** — cyclomatic/cognitive complexity, assertion density, isolation, naming, and test smell detection
- **Multi-framework support** — convert tests and generate fixtures/mocks across Jest, Vitest, Pytest, JUnit, TestNG, Mocha, Jasmine

## When to Use

- Writing a failing test first for a new feature (test-driven development)
- Analyzing coverage reports to find and prioritize gaps
- Generating test stubs from requirements or API specs
- Converting tests between frameworks or scaffolding fixtures/mocks
- Assessing test quality and detecting smells before merge

## Clarify First

Before generating tests or analyzing coverage, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Framework & language:** Jest / Vitest / Pytest / JUnit / Mocha (changes the generated stubs and any conversion).
- **Task:** generate from requirements / analyze coverage / guide a red-green-refactor cycle / convert tests (selects the tool).
- **Source input:** the user story / acceptance criteria, or the coverage report (LCOV/JSON/XML) to parse (the script's input).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

`scripts/tdd.py` is the command-line entry point. Its most useful job is the coverage gate:
it parses LCOV, Istanbul JSON or Cobertura XML, lists every file below the threshold with
its uncovered lines, and exits 1 while any gap remains.

```bash
python scripts/tdd.py coverage assets/sample_coverage_gaps.lcov --threshold 80     # exit 1, lists gaps
python scripts/tdd.py coverage assets/sample_coverage_report.lcov --threshold 80   # exit 0
python scripts/tdd.py generate assets/sample_input_python.json --module discount  # pytest stubs
python scripts/tdd.py quality tests/test_discount.py --format json               # assertion density, smells
```

## Tools Overview

| Subcommand | What it does | Key flags |
|------------|--------------|-----------|
| `coverage <report>` | Per-file line/branch gaps, uncovered lines, prioritised P0-P2 recommendations | `--threshold` (default 80), `--format text/json` |
| `generate <input.json>` | Test stubs from user stories, acceptance criteria, error and edge cases (Jest, Vitest, Pytest, JUnit, Mocha) | `--framework`, `--module`, `-o`, `--format` |
| `quality <test file>` | Test count, assertions per test, isolation, naming, smells, quality score | `--format` |

Generated stubs raise or throw until you write the real assertion, so they start RED by
design; a stub that passes before the code exists proves nothing.

Exit codes: `0` ok (coverage: every file meets the threshold); `1` coverage gaps found;
`2` bad input (missing or empty file, unknown report format, invalid JSON, unknown framework).

The other modules (`tdd_workflow.py` phase validation, `fixture_generator.py`
boundary values and mocks, `framework_adapter.py` cross-framework conversion,
`output_formatter.py`) are libraries; import them with `PYTHONPATH=scripts` as shown in
`references/tool-reference.md`.

## Workflow

1. RED: write or generate a failing test for the next behaviour; run it and confirm it fails for the expected reason.
2. GREEN: write the least code that passes; run the suite.
3. REFACTOR: clean up with the suite green; run it again.
4. Validate coverage with the project's own test runner producing a report, then `tdd.py coverage` on it. Done when it exits 0 at the agreed threshold and every new branch has a test that failed before the code existed.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows.md](references/workflows.md)** — step-by-step procedures for TDD-ing a feature, analyzing coverage gaps, and generating tests from requirements, each with validation checkpoints. Read when starting any of the three core workflows.
- **[references/tool-reference.md](references/tool-reference.md)** — complete API for all eight scripts (constructors, methods, parameters, worked examples) plus the tools summary table. Read when you need exact module names or method signatures.
- **[references/tdd-best-practices.md](references/tdd-best-practices.md)** — red-green-refactor discipline, naming/structure guidelines, test quality principles, and coverage goals. Read when deciding how to write or evaluate tests.
- **[references/framework-guide.md](references/framework-guide.md)** — framework selection matrix, configuration, and test patterns for TypeScript/JS, Python, and Java, with version requirements. Read when setting up or choosing a test framework.
- **[references/ci-integration.md](references/ci-integration.md)** — coverage report flow, GitHub Actions examples (Jest/Pytest/JaCoCo), quality gates, and trend tracking. Read when wiring coverage and quality gates into CI.
- **[references/troubleshooting-and-quality.md](references/troubleshooting-and-quality.md)** — anti-patterns, troubleshooting table, and success criteria. Read when tests behave unexpectedly or when defining the test-quality bar.

## Scope & Limitations

**This skill covers:**
- Unit test generation, scaffolding, and stub creation for Jest, Pytest, JUnit, Vitest, and Mocha
- Static coverage report parsing (LCOV, JSON/Istanbul, XML/Cobertura) with gap identification and prioritized recommendations
- Red-green-refactor workflow guidance with phase validation and cycle tracking
- Test quality assessment including complexity analysis, isolation scoring, naming quality, and test smell detection

**This skill does NOT cover:**
- Integration, end-to-end, or performance test generation -- see `senior-qa` for E2E patterns and `senior-devops` for load testing
- Runtime test execution or live coverage measurement -- scripts perform static analysis only; you must run your test suite externally
- Visual/snapshot testing or browser-based test workflows -- use Playwright, Cypress, or Storybook for UI-level testing
- Security-focused test generation (fuzz testing, penetration testing) -- see `senior-security` and `senior-secops` skills

## Anti-Patterns

### Tests Written After the Code
**Mistake:** Writing the implementation first, then adding tests that mirror it.
**Why it happens:** It feels faster, and the tests pass on the first run.
**Instead:** Watch each test fail before the code exists. A test that never failed may not be able to fail.

### Chasing the Coverage Number
**Mistake:** Adding assertion-free tests to push a file over the threshold.
**Why it happens:** The gate checks lines executed, not behaviour verified.
**Instead:** Run `tdd.py quality` alongside `coverage`; low assertions per test with high coverage is the signature of this mistake.

### Committing Generated Stubs Unfilled
**Mistake:** Leaving generated stubs in the suite with placeholder bodies.
**Why it happens:** They look like progress.
**Instead:** The stubs fail until filled in, on purpose. Fill each one or delete it before merging.

## Files

| File | Purpose |
|------|---------|
| `scripts/tdd.py` | CLI: `coverage`, `generate`, `quality` |
| `scripts/coverage_analyzer.py`, `test_generator.py`, `metrics_calculator.py`, `format_detector.py` | Libraries behind the CLI |
| `scripts/tdd_workflow.py`, `fixture_generator.py`, `framework_adapter.py`, `output_formatter.py` | Import-only libraries |
| `assets/sample_coverage_report.lcov` | Fully covered report (coverage exits 0) |
| `assets/sample_coverage_gaps.lcov` | Report with an untested function and branches (exits 1) |
| `assets/sample_input_python.json`, `sample_input_typescript.json` | Requirements inputs for `generate` |
| `assets/expected_output.json` | Example combined output |
| `references/*.md` | Workflows, API reference, practices, frameworks, CI, troubleshooting |
