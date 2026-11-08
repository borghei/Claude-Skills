# Tool Reference

From a shell, use `python scripts/tdd.py coverage|generate|quality` (see SKILL.md). The Python examples below need `PYTHONPATH=scripts` (or run from `scripts/`).

Complete API reference for the eight TDD Guide scripts. Read this when you need exact module names, constructor parameters, method signatures, or worked usage examples for any script.

## Tools Summary

| Tool | Purpose |
|------|---------|
| `test_generator.py` | Generate test cases from requirements/specs |
| `coverage_analyzer.py` | Parse LCOV/JSON/XML reports, find gaps |
| `tdd_workflow.py` | Guide red-green-refactor cycles |
| `framework_adapter.py` | Convert tests between frameworks |
| `fixture_generator.py` | Generate test data and mocks with seeds |
| `metrics_calculator.py` | Calculate complexity and test quality |
| `format_detector.py` | Auto-detect language and framework |
| `output_formatter.py` | Format output for CLI/desktop/CI |

---

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
