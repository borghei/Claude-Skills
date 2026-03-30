---
name: tdd-guide
description: >
  Test-driven development workflow with test generation, coverage analysis, and
  multi-framework support
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: testing
  updated: 2026-03-31
  tags: [tdd, test-driven-development, testing, red-green-refactor]
---
# TDD Guide

Test-driven development skill for generating tests, analyzing coverage, and guiding red-green-refactor workflows across Jest, Pytest, JUnit, and Vitest.

## Table of Contents

- [Capabilities](#capabilities)
- [Workflows](#workflows)
- [Tools](#tools)
- [Input Requirements](#input-requirements)
- [Limitations](#limitations)

---

## Capabilities

| Capability | Description |
|------------|-------------|
| Test Generation | Convert requirements or code into test cases with proper structure |
| Coverage Analysis | Parse LCOV/JSON/XML reports, identify gaps, prioritize fixes |
| TDD Workflow | Guide red-green-refactor cycles with validation |
| Framework Adapters | Generate tests for Jest, Pytest, JUnit, Vitest, Mocha |
| Quality Scoring | Assess test isolation, assertions, naming, detect test smells |
| Fixture Generation | Create realistic test data, mocks, and factories |

---

## Workflows

### Generate Tests from Code

1. Provide source code (TypeScript, JavaScript, Python, Java)
2. Specify target framework (Jest, Pytest, JUnit, Vitest)
3. Run `test_generator.py` with requirements
4. Review generated test stubs
5. **Validation:** Tests compile and cover happy path, error cases, edge cases

### Analyze Coverage Gaps

1. Generate coverage report from test runner (`npm test -- --coverage`)
2. Run `coverage_analyzer.py` on LCOV/JSON/XML report
3. Review prioritized gaps (P0/P1/P2)
4. Generate missing tests for uncovered paths
5. **Validation:** Coverage meets target threshold (typically 80%+)

### TDD New Feature

1. Write failing test first (RED)
2. Run `tdd_workflow.py --phase red` to validate
3. Implement minimal code to pass (GREEN)
4. Run `tdd_workflow.py --phase green` to validate
5. Refactor while keeping tests green (REFACTOR)
6. **Validation:** All tests pass after each cycle

---

## Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `test_generator.py` | Generate test cases from code/requirements | `python scripts/test_generator.py --input source.py --framework pytest` |
| `coverage_analyzer.py` | Parse and analyze coverage reports | `python scripts/coverage_analyzer.py --report lcov.info --threshold 80` |
| `tdd_workflow.py` | Guide red-green-refactor cycles | `python scripts/tdd_workflow.py --phase red --test test_auth.py` |
| `framework_adapter.py` | Convert tests between frameworks | `python scripts/framework_adapter.py --from jest --to pytest` |
| `fixture_generator.py` | Generate test data and mocks | `python scripts/fixture_generator.py --entity User --count 5` |
| `metrics_calculator.py` | Calculate test quality metrics | `python scripts/metrics_calculator.py --tests tests/` |
| `format_detector.py` | Detect language and framework | `python scripts/format_detector.py --file source.ts` |
| `output_formatter.py` | Format output for CLI/desktop/CI | `python scripts/output_formatter.py --format markdown` |

---

## Input Requirements

**For Test Generation:**
- Source code (file path or pasted content)
- Target framework (Jest, Pytest, JUnit, Vitest)
- Coverage scope (unit, integration, edge cases)

**For Coverage Analysis:**
- Coverage report file (LCOV, JSON, or XML format)
- Optional: Source code for context
- Optional: Target threshold percentage

**For TDD Workflow:**
- Feature requirements or user story
- Current phase (RED, GREEN, REFACTOR)
- Test code and implementation status

---

## Limitations

| Scope | Details |
|-------|---------|
| Unit test focus | Integration and E2E tests require different patterns |
| Static analysis | Cannot execute tests or measure runtime behavior |
| Language support | Best for TypeScript, JavaScript, Python, Java |
| Report formats | LCOV, JSON, XML only; other formats need conversion |
| Generated tests | Provide scaffolding; require human review for complex logic |

**When to use other tools:**
- E2E testing: Playwright, Cypress, Selenium
- Performance testing: k6, JMeter, Locust
- Security testing: OWASP ZAP, Burp Suite

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Generated tests pass immediately (no RED phase) | Test has no real assertion or asserts a trivially true value | Ensure every test contains an assertion against the actual unit under test; remove placeholder `assert True` stubs before running |
| Coverage report fails to parse | Report format does not match the expected LCOV, JSON, or XML structure | Run `format_detector.py` first to verify the detected format; convert non-standard reports (e.g., Clover) to Cobertura XML |
| Framework adapter produces wrong import style | Source and target framework were swapped, or language/framework mismatch | Verify the `framework` and `language` arguments match your project; use `detect_framework()` on existing test code to auto-detect |
| Fixture generator produces non-deterministic data | No random seed was supplied, so each run yields different values | Pass `seed=<int>` to `FixtureGenerator()` for reproducible fixtures across CI runs |
| Metrics calculator reports 0 test functions | Test code uses an unsupported naming convention (e.g., `spec_` prefix) | Rename tests to follow `test_*` / `it()` / `@Test` conventions, or extend the regex patterns in `_count_test_functions()` |
| TDD workflow validates GREEN phase but tests still fail locally | Test result dict passed to `validate_green_phase()` has `status` not set to `"passed"` | Ensure your test runner output is normalized to `{"status": "passed"}` or `{"status": "failed"}` before passing it in |
| Coverage gaps list is empty despite low overall coverage | All individual files meet the threshold even though the aggregate does not | Lower the `threshold` argument in `identify_gaps()` or inspect per-file coverage with `get_file_coverage()` |

---

## Success Criteria

- **Test-first ratio above 80%** -- at least 4 out of every 5 features begin with a failing test before any implementation code is written.
- **Red-green-refactor cycle under 10 minutes** -- each TDD micro-cycle (write failing test, make it pass, refactor) completes within a single focused interval.
- **Line coverage at or above 80%** -- measured by `coverage_analyzer.py` against LCOV/JSON/XML reports, with branch coverage at or above 70%.
- **Test quality score at or above 75/100** -- as reported by `metrics_calculator.py`, combining assertion density, isolation, naming quality, and absence of test smells.
- **Zero P0 coverage gaps in critical paths** -- business-critical modules (auth, payments, data persistence) have no files flagged P0 by `identify_gaps()`.
- **Test smell count of zero for high-severity items** -- no `missing_assertions`, `sleepy_test`, or `conditional_test_logic` smells detected at high severity.
- **Fixture reproducibility across CI** -- all generated fixtures use a fixed seed and produce identical output on every pipeline run.

---

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

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-qa` | Generated test stubs feed into QA review workflows; QA coverage standards inform threshold settings | `test_generator.py` output → QA review → approved test suite |
| `code-reviewer` | Metrics calculator output provides quantitative data for code review checklists | `metrics_calculator.py` quality report → code review scoring |
| `senior-fullstack` | Scaffolded projects include test infrastructure; TDD guide generates tests for scaffolded modules | `project_scaffolder.py` output → `test_generator.py` input |
| `senior-devops` | Coverage reports from CI pipelines are parsed by coverage analyzer; recommendations feed back into pipeline gates | CI coverage artifact → `coverage_analyzer.py` → pass/fail gate |
| `senior-security` | Edge-case fixtures for auth and API scenarios complement security-focused test plans | `fixture_generator.py` auth/API edge cases → security test plan |
| `tech-stack-evaluator` | Framework detection informs stack evaluation; test quality metrics feed into technology assessment | `format_detector.py` analysis → stack evaluation input |

---

## Tool Reference

### 1. `test_generator.py`

**Purpose:** Generate test cases from requirements, user stories, and API specs, then produce framework-specific test stubs and complete test files.

**Module:** `TestGenerator` class

**Usage:**
```python
from test_generator import TestGenerator, TestFramework, TestType

gen = TestGenerator(framework=TestFramework.PYTEST, language="python")
cases = gen.generate_from_requirements(requirements, test_type=TestType.UNIT)
stub = gen.generate_test_stub(cases[0])
file_content = gen.generate_test_file("my_module", cases)
suggestions = gen.suggest_missing_scenarios(existing_tests, code_analysis)
```

**Constructor Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `framework` | `TestFramework` | Yes | Target framework: `JEST`, `VITEST`, `PYTEST`, `JUNIT`, `MOCHA` |
| `language` | `str` | Yes | Programming language: `typescript`, `javascript`, `python`, `java` |

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `generate_from_requirements(requirements, test_type)` | `requirements`: dict with `user_stories`, `acceptance_criteria`, `api_specs`; `test_type`: `TestType` enum (default `UNIT`) | `List[Dict]` of test case specs |
| `generate_test_stub(test_case)` | `test_case`: single test case dict | `str` -- framework-specific test stub code |
| `generate_test_file(module_name, test_cases)` | `module_name`: str; `test_cases`: optional list (uses stored cases if omitted) | `str` -- complete test file with imports |
| `suggest_missing_scenarios(existing_tests, code_analysis)` | `existing_tests`: list of test name strings; `code_analysis`: dict with `error_handlers`, `conditional_branches`, `input_validation` | `List[Dict]` of suggested test scenarios |

**Output Formats:** Python dict/list (test case specifications), string (generated code).

**Example:**
```python
requirements = {
    "user_stories": [{"action": "login", "given": ["valid credentials"], "when": "submit form", "then": "redirect to dashboard"}],
    "api_specs": [{"method": "POST", "path": "/auth/login", "requires_auth": False, "required_params": ["email", "password"]}]
}
gen = TestGenerator(framework=TestFramework.JEST, language="typescript")
cases = gen.generate_from_requirements(requirements)
print(gen.generate_test_file("auth_service", cases))
```

---

### 2. `coverage_analyzer.py`

**Purpose:** Parse coverage reports in LCOV, JSON (Istanbul/nyc), and XML (Cobertura) formats. Calculate summary metrics, identify files below threshold, and generate prioritized recommendations.

**Module:** `CoverageAnalyzer` class

**Usage:**
```python
from coverage_analyzer import CoverageAnalyzer

analyzer = CoverageAnalyzer()
data = analyzer.parse_coverage_report(report_content, format_type="lcov")
summary = analyzer.calculate_summary()
gaps = analyzer.identify_gaps(threshold=80.0)
recs = analyzer.generate_recommendations()
file_detail = analyzer.get_file_coverage("src/auth.ts")
detected = analyzer.detect_format(raw_content)
```

**Constructor Parameters:** None.

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `parse_coverage_report(report_content, format_type)` | `report_content`: str; `format_type`: `"lcov"`, `"json"`, `"xml"`, `"cobertura"` | `Dict` of per-file coverage data |
| `calculate_summary()` | None | `Dict` with `line_coverage`, `branch_coverage`, `function_coverage`, totals |
| `identify_gaps(threshold)` | `threshold`: float (default `80.0`) | `List[Dict]` of files below threshold with priority P0/P1/P2 |
| `generate_recommendations()` | None | `List[Dict]` of prioritized recommendations |
| `get_file_coverage(file_path)` | `file_path`: str | `Dict` with per-file line/branch/function coverage |
| `detect_format(content)` | `content`: str | `str` -- `"lcov"`, `"json"`, or `"xml"` |

**Output Formats:** Python dict/list. Use `output_formatter.py` for terminal/markdown/JSON rendering.

**Example:**
```python
with open("coverage/lcov.info") as f:
    content = f.read()
analyzer = CoverageAnalyzer()
fmt = analyzer.detect_format(content)
analyzer.parse_coverage_report(content, fmt)
summary = analyzer.calculate_summary()
# {'line_coverage': 76.5, 'branch_coverage': 62.3, ...}
gaps = analyzer.identify_gaps(threshold=80.0)
# [{'file': 'src/auth.ts', 'line_coverage': 45.0, 'priority': 'P0', ...}]
```

---

### 3. `tdd_workflow.py`

**Purpose:** Guide users through red-green-refactor TDD cycles with phase validation, workflow state tracking, and refactoring suggestions.

**Module:** `TDDWorkflow` class

**Usage:**
```python
from tdd_workflow import TDDWorkflow

wf = TDDWorkflow()
guidance = wf.start_cycle("User can reset password via email")
red_result = wf.validate_red_phase(test_code, test_result={"status": "failed"})
green_result = wf.validate_green_phase(impl_code, {"status": "passed"})
refactor_result = wf.validate_refactor_phase(original, refactored, {"status": "passed"})
phase_guide = wf.get_phase_guidance()
summary = wf.generate_workflow_summary()
```

**Constructor Parameters:** None.

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `start_cycle(requirement)` | `requirement`: str -- user story or feature description | `Dict` with phase, instruction, checklist, tips |
| `validate_red_phase(test_code, test_result)` | `test_code`: str; `test_result`: optional dict with `status` key | `Dict` with `phase_complete`, validations, next instruction |
| `validate_green_phase(implementation_code, test_result)` | `implementation_code`: str; `test_result`: dict with `status` key | `Dict` with `phase_complete`, validations, `refactoring_suggestions` |
| `validate_refactor_phase(original_code, refactored_code, test_result)` | `original_code`: str; `refactored_code`: str; `test_result`: dict with `status` key | `Dict` with `phase_complete`, `cycle_complete`, next steps |
| `get_phase_guidance(phase)` | `phase`: optional `TDDPhase` enum (uses current phase if omitted) | `Dict` with goal, steps, common mistakes, tips |
| `generate_workflow_summary()` | None | `str` -- markdown summary of current state and completed cycles |

**Output Formats:** Python dict (validation results), string (summary).

**Example:**
```python
wf = TDDWorkflow()
wf.start_cycle("Add email validation to signup form")
result = wf.validate_red_phase("def test_invalid_email():\n    assert validate('bad') == False", {"status": "failed"})
# {'phase_complete': True, 'next_phase': 'GREEN', ...}
```

---

### 4. `framework_adapter.py`

**Purpose:** Provide multi-framework support with adapters for Jest, Vitest, Pytest, unittest, JUnit, TestNG, Mocha, and Jasmine. Generate framework-specific imports, test suites, test functions, assertions, and setup/teardown hooks.

**Module:** `FrameworkAdapter` class

**Usage:**
```python
from framework_adapter import FrameworkAdapter, Framework, Language

adapter = FrameworkAdapter(framework=Framework.JEST, language=Language.TYPESCRIPT)
imports = adapter.generate_imports()
suite = adapter.generate_test_suite_wrapper("AuthService", test_content)
test_fn = adapter.generate_test_function("should reject invalid email", body, "Validates email format")
assertion = adapter.generate_assertion("result", "true", "true")
hooks = adapter.generate_setup_teardown(setup_code="db = create_test_db()", teardown_code="db.close()")
detected = adapter.detect_framework(existing_code)
```

**Constructor Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `framework` | `Framework` | Yes | `JEST`, `VITEST`, `PYTEST`, `UNITTEST`, `JUNIT`, `TESTNG`, `MOCHA`, `JASMINE` |
| `language` | `Language` | Yes | `TYPESCRIPT`, `JAVASCRIPT`, `PYTHON`, `JAVA` |

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `generate_imports()` | None | `str` -- framework-specific import statements |
| `generate_test_suite_wrapper(suite_name, test_content)` | `suite_name`: str; `test_content`: str | `str` -- complete test suite wrapping content |
| `generate_test_function(test_name, test_body, description)` | `test_name`: str; `test_body`: str; `description`: str (default `""`) | `str` -- complete test function |
| `generate_assertion(actual, expected, assertion_type)` | `actual`: str; `expected`: str; `assertion_type`: `"equals"`, `"not_equals"`, `"true"`, `"false"`, `"throws"` (default `"equals"`) | `str` -- assertion statement |
| `generate_setup_teardown(setup_code, teardown_code)` | `setup_code`: str (default `""`); `teardown_code`: str (default `""`) | `str` -- setup/teardown hooks |
| `detect_framework(code)` | `code`: str | `Framework` enum or `None` |

**Output Formats:** String (generated code).

**Example:**
```python
adapter = FrameworkAdapter(Framework.PYTEST, Language.PYTHON)
print(adapter.generate_imports())
# import pytest
print(adapter.generate_assertion("calculate_total(items)", "150.0", "equals"))
# assert calculate_total(items) == 150.0
```

---

### 5. `fixture_generator.py`

**Purpose:** Generate realistic test data, boundary values, edge-case scenarios, and mock objects for various domains (auth, payment, form, API, file upload).

**Module:** `FixtureGenerator` class

**Usage:**
```python
from fixture_generator import FixtureGenerator

gen = FixtureGenerator(seed=42)
boundaries = gen.generate_boundary_values("int", {"min": 0, "max": 255})
edge_cases = gen.generate_edge_cases("auth")
mocks = gen.generate_mock_data(schema, count=5)
fixture_content = gen.generate_fixture_file("users", mocks, format="json")
```

**Constructor Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `seed` | `int` or `None` | No | Random seed for reproducible output (default `None`) |

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `generate_boundary_values(data_type, constraints)` | `data_type`: `"int"`, `"string"`, `"array"`, `"date"`, `"email"`, `"url"`; `constraints`: optional dict (`min`, `max`, `min_length`, `max_length`, `min_size`, `max_size`) | `List` of boundary values |
| `generate_edge_cases(scenario, context)` | `scenario`: `"auth"`, `"payment"`, `"form"`, `"api"`, `"file_upload"`; `context`: optional dict (required for `"form"` with `fields` key) | `List[Dict]` of edge case scenarios |
| `generate_mock_data(schema, count)` | `schema`: dict mapping field names to `{"type": ...}` defs; `count`: int (default `1`) | `List[Dict]` of mock objects |
| `generate_fixture_file(fixture_name, data, format)` | `fixture_name`: str; `data`: any; `format`: `"json"`, `"python"`, `"yaml"` (default `"json"`) | `str` -- fixture file content |

**Supported Schema Field Types:** `string`, `int`, `float`, `bool`, `email`, `date`, `array`.

**Output Formats:** Python list/dict (data), string (file content in JSON/Python/YAML).

**Example:**
```python
gen = FixtureGenerator(seed=123)
schema = {
    "id": {"type": "int", "min": 1, "max": 9999},
    "email": {"type": "email"},
    "active": {"type": "bool"}
}
users = gen.generate_mock_data(schema, count=3)
print(gen.generate_fixture_file("test_users", users, format="json"))
```

---

### 6. `metrics_calculator.py`

**Purpose:** Calculate comprehensive test and code quality metrics including cyclomatic/cognitive complexity, testability scoring, test quality assessment (assertions, isolation, naming, smells), and execution analysis.

**Module:** `MetricsCalculator` class

**Usage:**
```python
from metrics_calculator import MetricsCalculator

calc = MetricsCalculator()
all_metrics = calc.calculate_all_metrics(source_code, test_code, coverage_data, execution_data)
complexity = calc.calculate_complexity(source_code)
test_quality = calc.calculate_test_quality(test_code)
execution = calc.analyze_execution_metrics(execution_data)
summary = calc.generate_metrics_summary()
```

**Constructor Parameters:** None.

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `calculate_all_metrics(source_code, test_code, coverage_data, execution_data)` | `source_code`: str; `test_code`: str; `coverage_data`: optional dict; `execution_data`: optional dict | `Dict` with `complexity`, `test_quality`, `coverage`, `execution` |
| `calculate_complexity(code)` | `code`: str | `Dict` with `cyclomatic_complexity`, `cognitive_complexity`, `testability_score`, `assessment` |
| `calculate_test_quality(test_code)` | `test_code`: str | `Dict` with `total_tests`, `total_assertions`, `avg_assertions_per_test`, `isolation_score`, `naming_quality`, `test_smells`, `quality_score` |
| `analyze_execution_metrics(execution_data)` | `execution_data`: dict with `tests` list (each having `duration`, `status`, optional `failure_rate`) | `Dict` with `total_tests`, timing stats, `slow_tests`, `flaky_tests`, `pass_rate` |
| `generate_metrics_summary()` | None | `str` -- human-readable markdown summary |

**Output Formats:** Python dict (metrics data), string (markdown summary).

**Example:**
```python
calc = MetricsCalculator()
complexity = calc.calculate_complexity(open("src/auth.py").read())
# {'cyclomatic_complexity': 8, 'cognitive_complexity': 12, 'testability_score': 82.0, 'assessment': 'Medium complexity - moderately testable'}
quality = calc.calculate_test_quality(open("tests/test_auth.py").read())
# {'quality_score': 78.5, 'test_smells': [], ...}
```

---

### 7. `format_detector.py`

**Purpose:** Automatically detect programming language, testing framework, coverage report format, and project structure from code content or file paths.

**Module:** `FormatDetector` class

**Usage:**
```python
from format_detector import FormatDetector

detector = FormatDetector()
language = detector.detect_language(code)
framework = detector.detect_test_framework(test_code)
cov_format = detector.detect_coverage_format(report_content)
input_info = detector.detect_input_format(raw_input)
file_info = detector.extract_file_info("/src/auth.service.ts")
test_name = detector.suggest_test_file_name("auth.service.ts", "jest")
patterns = detector.identify_test_patterns(test_code)
project = detector.analyze_project_structure(file_path_list)
env = detector.detect_environment()
```

**Constructor Parameters:** None.

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `detect_language(code)` | `code`: str | `str` -- `"typescript"`, `"javascript"`, `"python"`, `"java"`, `"unknown"` |
| `detect_test_framework(code)` | `code`: str | `str` -- `"jest"`, `"vitest"`, `"pytest"`, `"unittest"`, `"junit"`, `"mocha"`, `"unknown"` |
| `detect_coverage_format(content)` | `content`: str | `str` -- `"lcov"`, `"json"`, `"xml"`, `"unknown"` |
| `detect_input_format(input_data)` | `input_data`: str | `Dict` with `format`, `language`, `framework`, `content_type` |
| `extract_file_info(file_path)` | `file_path`: str | `Dict` with `file_name`, `extension`, `language`, `is_test`, `purpose` |
| `suggest_test_file_name(source_file, framework)` | `source_file`: str; `framework`: str | `str` -- suggested test file name |
| `identify_test_patterns(code)` | `code`: str | `List[str]` of detected patterns (AAA, Given-When-Then, etc.) |
| `analyze_project_structure(file_paths)` | `file_paths`: list of str | `Dict` with `primary_language`, `test_ratio`, `suggested_framework` |
| `detect_environment()` | None | `Dict` with `environment`, `output_preference` |

**Output Formats:** String (detection result), Python dict (detailed analysis).

**Example:**
```python
detector = FormatDetector()
print(detector.detect_language("const add = (a: number, b: number): number => a + b;"))
# "typescript"
print(detector.suggest_test_file_name("UserService.java", "junit"))
# "UserserviceTest.java"
print(detector.identify_test_patterns("// Arrange\nsetup()\n// Act\nresult = run()\n// Assert\nassert result"))
# ['AAA (Arrange-Act-Assert)']
```

---

### 8. `output_formatter.py`

**Purpose:** Context-aware output formatting for different environments (Desktop/markdown, CLI/terminal, API/JSON). Supports progressive disclosure, token-efficient summary reports, and output truncation.

**Module:** `OutputFormatter` class

**Usage:**
```python
from output_formatter import OutputFormatter

fmt = OutputFormatter(environment="cli", verbose=False)
cov_output = fmt.format_coverage_summary(summary, detailed=True)
rec_output = fmt.format_recommendations(recommendations, max_items=5)
test_output = fmt.format_test_results(results, show_details=True)
report = fmt.create_summary_report(coverage, metrics, recommendations)
should_detail = fmt.should_show_detailed(data_size=50)
truncated = fmt.truncate_output(long_text, max_lines=30)
```

**Constructor Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `environment` | `str` | No | Target environment: `"desktop"`, `"cli"`, `"api"` (default `"cli"`) |
| `verbose` | `bool` | No | Include detailed output (default `False`) |

**Key Methods:**

| Method | Parameters | Returns |
|--------|-----------|---------|
| `format_coverage_summary(summary, detailed)` | `summary`: dict; `detailed`: bool (default `False`) | `str` -- formatted coverage (markdown/terminal/JSON based on environment) |
| `format_recommendations(recommendations, max_items)` | `recommendations`: list of dicts; `max_items`: optional int | `str` -- formatted recommendations grouped by priority |
| `format_test_results(results, show_details)` | `results`: dict with `total_tests`, `passed`, `failed`, `skipped`, `failed_tests`; `show_details`: bool (default `False`) | `str` -- formatted test results |
| `create_summary_report(coverage, metrics, recommendations)` | `coverage`: dict; `metrics`: dict; `recommendations`: list | `str` -- token-efficient summary (<200 tokens) |
| `should_show_detailed(data_size)` | `data_size`: int | `bool` -- whether to show detailed output |
| `truncate_output(text, max_lines)` | `text`: str; `max_lines`: int (default `50`) | `str` -- truncated text with remaining-lines indicator |

**Output Formats:** String in markdown (desktop), plain text (CLI), or JSON (API) depending on `environment` setting.

**Example:**
```python
fmt = OutputFormatter(environment="desktop", verbose=True)
print(fmt.format_coverage_summary({"line_coverage": 82.5, "branch_coverage": 71.0, "function_coverage": 90.0}))
# ## Test Coverage Summary
# ### Overall Metrics
# - **Line Coverage**: 82.5%
# ...
```
