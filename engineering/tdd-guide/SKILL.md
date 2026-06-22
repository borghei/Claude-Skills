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
  updated: 2026-06-15
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

Before generating tests or analyzing coverage, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Framework & language** — Jest / Vitest / Pytest / JUnit / Mocha (changes the generated stubs and any conversion)
- [ ] **Task** — generate from requirements / analyze coverage / guide a red-green-refactor cycle / convert tests (selects the tool)
- [ ] **Source input** — the user story / acceptance criteria, or the coverage report (LCOV/JSON/XML) to parse (the script's input)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Generate test cases from requirements (Python API)
from test_generator import TestGenerator, TestFramework
gen = TestGenerator(framework=TestFramework.PYTEST, language="python")
cases = gen.generate_from_requirements(requirements)

# Analyze coverage gaps from LCOV report
from coverage_analyzer import CoverageAnalyzer
analyzer = CoverageAnalyzer()
analyzer.parse_coverage_report(content, "lcov")
gaps = analyzer.identify_gaps(threshold=80.0)

# Guide TDD cycle
from tdd_workflow import TDDWorkflow
wf = TDDWorkflow()
wf.start_cycle("User can reset password via email")
```

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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-qa` | Generated test stubs feed into QA review workflows; QA coverage standards inform threshold settings | `test_generator.py` output → QA review → approved test suite |
| `code-reviewer` | Metrics calculator output provides quantitative data for code review checklists | `metrics_calculator.py` quality report → code review scoring |
| `senior-fullstack` | Scaffolded projects include test infrastructure; TDD guide generates tests for scaffolded modules | `project_scaffolder.py` output → `test_generator.py` input |
| `senior-devops` | Coverage reports from CI pipelines are parsed by coverage analyzer; recommendations feed back into pipeline gates | CI coverage artifact → `coverage_analyzer.py` → pass/fail gate |
| `senior-security` | Edge-case fixtures for auth and API scenarios complement security-focused test plans | `fixture_generator.py` auth/API edge cases → security test plan |
| `tech-stack-evaluator` | Framework detection informs stack evaluation; test quality metrics feed into technology assessment | `format_detector.py` analysis → stack evaluation input |
