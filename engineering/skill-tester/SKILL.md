---
name: skill-tester
description: >
  Validates and scores Claude Code skill packages for quality, completeness, and
  best practices compliance. Tests Python scripts, checks YAML frontmatter, and
  generates quality reports. Use when creating new skills, validating skill
  packages, or auditing skill quality.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: meta-skills
  tier: POWERFUL
  updated: 2026-03-31
---
# Skill Tester

The agent validates skill packages for structure compliance, tests Python scripts for syntax and stdlib-only imports, and scores quality across four dimensions (documentation, code quality, completeness, usability) with letter grades and improvement recommendations. It supports BASIC, STANDARD, and POWERFUL tier classification.

## Quick Start

```bash
# Validate skill structure and documentation
python skill_validator.py engineering/my-skill --tier POWERFUL --json

# Test all Python scripts in a skill
python script_tester.py engineering/my-skill --timeout 30

# Score quality with improvement roadmap
python quality_scorer.py engineering/my-skill --detailed --minimum-score 75
```

---

## Core Workflows

### Workflow 1: Validate a New Skill

1. Run `skill_validator.py` with target tier to check structure, frontmatter, required sections, and scripts
2. Review errors (blocking) and warnings (non-blocking) in the report
3. Fix all errors -- missing SKILL.md, invalid frontmatter, external imports
4. **Validation checkpoint:** Score >= 60; zero errors; all scripts pass `ast.parse()`

```bash
python skill_validator.py engineering/my-skill --tier STANDARD --json
```

### Workflow 2: Test Skill Scripts

1. Run `script_tester.py` to execute syntax validation, import analysis, and runtime tests
2. Review per-script results: argparse detection, `--help` output, sample data execution
3. Fix failures: add `if __name__ == "__main__"` guards, replace external imports with stdlib
4. **Validation checkpoint:** All scripts pass syntax; zero external imports; `--help` exits cleanly

```bash
python script_tester.py engineering/my-skill --timeout 60 --json
```

### Workflow 3: Score and Improve Quality

1. Run `quality_scorer.py` with `--detailed` for component-level breakdowns
2. Review the prioritized improvement roadmap (up to 5 items)
3. Address HIGH-priority items first (documentation gaps, missing error handling)
4. Re-run to verify score improvement
5. **Validation checkpoint:** Overall score >= 75; no dimension below 50%

```bash
python quality_scorer.py engineering/my-skill --detailed --minimum-score 75 --json
```

---

## Tier Requirements

| Requirement | BASIC | STANDARD | POWERFUL |
|-------------|-------|----------|----------|
| SKILL.md lines | 100+ | 200+ | 300+ |
| Python scripts | 1 (100-300 LOC) | 1-2 (300-500 LOC) | 2-3 (500-800 LOC) |
| Argparse | Basic | Subcommands | Multiple modes |
| Output formats | Single | JSON + text | JSON + text + validation |
| Error handling | Essential | Comprehensive | Advanced recovery |

---

## Quality Scoring Dimensions

| Dimension | Weight | Measures |
|-----------|--------|----------|
| Documentation | 25% | SKILL.md depth, README clarity, reference quality |
| Code Quality | 25% | Complexity, error handling, output consistency |
| Completeness | 25% | Required files, sample data, expected outputs |
| Usability | 25% | Argparse help text, example clarity, ease of setup |

**Grades:** A+ (97+) through F (<40). Exit code 0 for A+ through C-, exit code 2 for D, exit code 1 for F.

---

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Validate Changed Skills
  run: |
    for skill in $(git diff --name-only | grep -E '^engineering/[^/]+/' | cut -d'/' -f1-2 | sort -u); do
      python engineering/skill-tester/scripts/skill_validator.py $skill --json
      python engineering/skill-tester/scripts/script_tester.py $skill
      python engineering/skill-tester/scripts/quality_scorer.py $skill --minimum-score 75
    done
```

---

## Anti-Patterns

- **Padding SKILL.md with filler** -- line count thresholds measure substantive content; blank lines and boilerplate do not count
- **External imports disguised as stdlib** -- the import allowlist is manually maintained; if a legit stdlib module is flagged, add it to `stdlib_modules`
- **Missing argparse help strings** -- usability scoring requires `help=` parameters on every argument; empty help strings score zero
- **No `__main__` guard** -- scripts without `if __name__ == "__main__"` fail runtime tests when imported
- **Relying on SKILL.md for usability** -- usability is scored from scripts and README independently; a detailed SKILL.md does not compensate for missing `--help` output

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `SKILL.md too short` error despite sufficient content | Validator counts only non-blank lines; blank lines inflate raw line count but are excluded from the tally | Remove excessive blank lines or add more substantive content sections to meet the tier threshold |
| YAML frontmatter parse failure | Frontmatter contains invalid YAML syntax (unquoted colons, tabs instead of spaces, missing closing `---`) | Validate frontmatter through `yaml.safe_load()` locally; ensure the closing `---` marker is present on its own line |
| External import false positive | The stdlib module allowlist in `skill_validator.py` and `script_tester.py` is manually maintained and may not include every standard library module | Add the missing module name to the `stdlib_modules` set in the relevant script, or restructure the import |
| Script execution timeout during testing | Script requires interactive input, enters an infinite loop, or performs long-running computation | Increase `--timeout` value, add early-exit logic for missing arguments, or ensure scripts exit cleanly when no input is provided |
| Tier compliance check fails despite passing individual checks | `_validate_tier_compliance` only examines `skill_md_exists`, `min_scripts_count`, and `skill_md_length`; other failures (e.g., missing directories) are reported separately | Fix the specific critical checks listed in the error message; review the `TIER_REQUIREMENTS` dictionary for the target tier |
| Quality scorer reports low usability despite good documentation | Usability dimension scores help text inside scripts, `README.md` usage sections, and practical example files independently of SKILL.md content | Add `argparse` help strings with `help=` parameters, include a `Usage` section in README.md, and place sample/example files in the `assets/` directory |
| `--json` flag produces no output | Script raised an unhandled exception before reaching the output formatter; errors are written to stderr | Run with `--verbose` to see the full traceback on stderr, then address the underlying exception |

## Success Criteria

- **Structure pass rate above 95%**: Validated skills pass all required-file and directory-structure checks on first run in at least 95% of cases.
- **Script syntax zero-defect**: Every Python script in a validated skill compiles without `SyntaxError` via `ast.parse()`.
- **Standard library compliance 100%**: No external (non-stdlib) imports detected across all validated scripts.
- **Quality score consistency within 5 points**: Re-running `quality_scorer.py` on an unchanged skill produces scores that vary by no more than 5 points across runs.
- **Execution time under 10 seconds per skill**: Full validation, testing, and scoring pipeline completes in under 10 seconds for a single skill with up to 3 scripts.
- **Actionable recommendation density**: Every skill scoring below 75/100 receives at least 3 prioritized improvement suggestions in the roadmap.
- **CI/CD gate reliability**: When integrated as a GitHub Actions step, the tool exits with non-zero status for every skill that fails critical checks, blocking the merge.

## Scope & Limitations

**Covers:**
- Structural validation of skill directories against tier-specific requirements (BASIC, STANDARD, POWERFUL)
- Static analysis of Python scripts including syntax checking, import validation, argparse detection, and main guard verification
- Multi-dimensional quality scoring across documentation, code quality, completeness, and usability
- Dual output formatting (JSON for CI/CD pipelines, human-readable for developer consumption)

**Does NOT cover:**
- Functional correctness of script logic or algorithm accuracy — the tester verifies structure and conventions, not business logic
- Performance benchmarking or memory profiling of scripts — see `engineering/performance-profiler` for runtime analysis
- Security vulnerability scanning of script code — see `engineering/skill-security-auditor` for dependency and code security audits
- Cross-skill dependency resolution or integration testing — skills are validated in isolation without verifying inter-skill compatibility

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/skill-security-auditor` | Run security audit after validation passes | `skill_validator.py` confirms structure compliance, then `skill-security-auditor` scans for vulnerabilities in the same skill path |
| `engineering/ci-cd-pipeline-builder` | Embed skill-tester as a quality gate stage | Pipeline builder generates workflow YAML that invokes `skill_validator.py`, `script_tester.py`, and `quality_scorer.py` sequentially |
| `engineering/changelog-generator` | Feed quality score deltas into changelog entries | Compare `quality_scorer.py` JSON output between releases to surface quality improvements or regressions |
| `engineering/pr-review-expert` | Attach validation report to pull request reviews | `skill_validator.py --json` output is posted as a PR comment for reviewer context |
| `engineering/performance-profiler` | Complement structural testing with runtime profiling | After `script_tester.py` confirms execution succeeds, `performance-profiler` measures execution time and resource usage |
| `engineering/tech-debt-tracker` | Track quality score trends over time | Periodic `quality_scorer.py --json` output is ingested to detect score degradation and flag technical debt |

## Tool Reference

### skill_validator.py

**Purpose:** Validates a skill directory's structure, documentation, and Python scripts against the claude-skills ecosystem standards. Checks required files, YAML frontmatter, required SKILL.md sections, directory layout, script syntax, import compliance, and tier-specific requirements.

**Usage:**
```bash
python skill_validator.py <skill_path> [--tier TIER] [--json] [--verbose]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skill_path` | positional | Yes | — | Path to the skill directory to validate |
| `--tier` | option | No | None | Target tier for validation: `BASIC`, `STANDARD`, or `POWERFUL` |
| `--json` | flag | No | Off | Output results in JSON format instead of human-readable text |
| `--verbose` | flag | No | Off | Enable verbose logging to stderr |

**Example:**
```bash
python skill_validator.py engineering/my-skill --tier POWERFUL --json
```

**Output Formats:**
- **Human-readable (default):** Grouped report with STRUCTURE VALIDATION, SCRIPT VALIDATION, ERRORS, WARNINGS, and SUGGESTIONS sections. Displays overall score out of 100 with compliance level (EXCELLENT, GOOD, ACCEPTABLE, NEEDS_IMPROVEMENT, POOR).
- **JSON (`--json`):** Object with keys `skill_path`, `timestamp`, `overall_score`, `compliance_level`, `checks` (dict of check name to pass/message/score), `warnings`, `errors`, `suggestions`.

**Exit codes:** `0` on success (score >= 60 and no errors), `1` on failure.

---

### script_tester.py

**Purpose:** Tests all Python scripts within a skill's `scripts/` directory. Performs syntax validation via AST parsing, import analysis for stdlib compliance, argparse implementation verification, main guard detection, runtime execution with timeout protection, `--help` functionality testing, sample data processing against files in `assets/`, and output format compliance checks.

**Usage:**
```bash
python script_tester.py <skill_path> [--timeout SECONDS] [--json] [--verbose]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skill_path` | positional | Yes | — | Path to the skill directory containing scripts to test |
| `--timeout` | option | No | `30` | Timeout in seconds for each script execution test |
| `--json` | flag | No | Off | Output results in JSON format instead of human-readable text |
| `--verbose` | flag | No | Off | Enable verbose logging to stderr |

**Example:**
```bash
python script_tester.py engineering/my-skill --timeout 60 --json
```

**Output Formats:**
- **Human-readable (default):** Report with SUMMARY (total/passed/partial/failed counts), GLOBAL ERRORS, and per-script sections showing status, execution time, individual test results, errors, and warnings.
- **JSON (`--json`):** Object with keys `skill_path`, `timestamp`, `summary` (counts and overall status), `global_errors`, `script_results` (dict per script with `overall_status`, `execution_time`, `tests`, `errors`, `warnings`).

**Exit codes:** `0` on full success, `1` on failure or global errors, `2` on partial success.

---

### quality_scorer.py

**Purpose:** Provides a comprehensive multi-dimensional quality assessment for a skill. Evaluates four equally weighted dimensions — Documentation (25%), Code Quality (25%), Completeness (25%), and Usability (25%) — and produces an overall score, letter grade (A+ through F), tier recommendation, and a prioritized improvement roadmap.

**Usage:**
```bash
python quality_scorer.py <skill_path> [--detailed] [--minimum-score SCORE] [--json] [--verbose]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skill_path` | positional | Yes | — | Path to the skill directory to assess |
| `--detailed` | flag | No | Off | Show detailed component scores within each dimension |
| `--minimum-score` | option | No | `0` | Minimum acceptable overall score; exits with error code `1` if the score falls below this threshold |
| `--json` | flag | No | Off | Output results in JSON format instead of human-readable text |
| `--verbose` | flag | No | Off | Enable verbose logging to stderr |

**Example:**
```bash
python quality_scorer.py engineering/my-skill --detailed --minimum-score 75 --json
```

**Output Formats:**
- **Human-readable (default):** Report with overall score and letter grade, per-dimension scores with weights, summary statistics (highest/lowest dimension, dimensions above 70%, dimensions below 50%), and a prioritized improvement roadmap (up to 5 items with HIGH/MEDIUM/LOW priority). When `--detailed` is used, component-level breakdowns appear under each dimension.
- **JSON (`--json`):** Object with keys `skill_path`, `timestamp`, `overall_score`, `letter_grade`, `tier_recommendation`, `summary_stats`, `dimensions` (per-dimension name/weight/score/details/suggestions), `improvement_roadmap` (list of priority/dimension/suggestion/current_score objects).

**Exit codes:** `0` for grades A+ through C-, `1` for grade F or when score is below `--minimum-score`, `2` for grade D.