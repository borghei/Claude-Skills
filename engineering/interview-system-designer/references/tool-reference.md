# Tool Reference, Troubleshooting & Success Criteria

Read this when invoking the three tools (full flags, examples, output formats), debugging
unexpected output, or checking results against the quality bar.

## Tool Reference

### loop_designer.py

**Purpose:** Generates calibrated interview loops tailored to specific roles, levels, and teams. Produces complete loops with rounds, focus areas, time allocation, interviewer skill requirements, and scorecard templates.

**Usage:**
```bash
python3 scripts/loop_designer.py --role "Senior Software Engineer" --level senior --team platform --output loops/
```

**Flags/Parameters:**

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--role` | `str` | No | — | Job role title (e.g., "Senior Software Engineer") |
| `--level` | `str` | No | — | Experience level: `junior`, `mid`, `senior`, `staff`, `principal` |
| `--team` | `str` | No | — | Team or department name (optional context for loop customization) |
| `--competencies` | `str` | No | — | Comma-separated list of specific competencies to focus on |
| `--input` | `str` | No | — | Input JSON file with role definition |
| `--output` | `str` | No | — | Output directory or file path |
| `--format` | `str` | No | `both` | Output format: `json`, `text`, or `both` |

**Example:**
```bash
python3 scripts/loop_designer.py --role "Staff Data Scientist" --level staff --competencies ml,statistics,leadership --format json --output loops/ds-staff.json
```

**Output Formats:**
- **JSON:** Structured loop definition with rounds array, competency mappings, time allocations, and scorecard templates suitable for programmatic consumption.
- **Text:** Human-readable interview guide with formatted round descriptions, interviewer requirements, and evaluation criteria.
- **Both (default):** With `--output`, writes JSON and text files there; without `--output`, prints the text report to stdout and writes nothing.

### question_bank_generator.py

**Purpose:** Generates comprehensive, competency-based interview questions with detailed scoring criteria, follow-up probes, and calibration examples organized by competency area.

**Usage:**
```bash
python3 scripts/question_bank_generator.py --role "Frontend Engineer" --competencies react,typescript,system-design --output questions/
```

**Flags/Parameters:**

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--role` | `str` | No | — | Job role title (e.g., "Frontend Engineer") |
| `--level` | `str` | No | `senior` | Experience level: `junior`, `mid`, `senior`, `staff`, `principal` |
| `--competencies` | `str` | No | — | Comma-separated list of competencies to focus on |
| `--question-types` | `str` | No | — | Comma-separated list of question types: `technical`, `behavioral`, `situational` |
| `--num-questions` | `int` | No | `20` | Number of questions to generate |
| `--input` | `str` | No | — | Input JSON file with role requirements |
| `--output` | `str` | No | — | Output directory or file path |
| `--format` | `str` | No | `both` | Output format: `json`, `text`, or `both` |

**Example:**
```bash
python3 scripts/question_bank_generator.py --role "Product Manager" --level mid --question-types behavioral,situational --num-questions 30 --format text
```

**Output Formats:**
- **JSON:** Array of question objects each containing the question text, competency area, difficulty level, scoring rubric (1-4 scale), follow-up probes, and calibration examples (poor/good/great answers).
- **Text:** Formatted question bank grouped by competency with inline scoring guidance and example answers for interviewer reference.
- **Both (default):** With `--output`, writes JSON and text files there; without `--output`, prints the text report to stdout and writes nothing.

### hiring_calibrator.py

**Purpose:** Analyzes interview scores from multiple candidates and interviewers to detect bias, calibration issues, and inconsistent rubric application. Generates calibration reports with recommendations for interviewer coaching and process improvements.

**Usage:**
```bash
python3 scripts/hiring_calibrator.py --input interview_results.json --analysis-type comprehensive --output report.json
```

**Flags/Parameters:**

| Flag | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `--input` | `str` | **Yes** | — | Input JSON file with interview results data |
| `--analysis-type` | `str` | No | `comprehensive` | Analysis type: `comprehensive`, `bias`, `calibration`, `interviewer`, `scoring` |
| `--competencies` | `str` | No | — | Comma-separated list of competencies to focus on |
| `--trend-analysis` | flag | No | `false` | Enable trend analysis over time |
| `--period` | `str` | No | `monthly` | Trend period: `daily`, `weekly`, `monthly`, `quarterly` |
| `--output` | `str` | No | — | Output file path |
| `--format` | `str` | No | `both` | Output format: `json`, `text`, or `both` |

**Example:**
```bash
python3 scripts/hiring_calibrator.py --input q1_interviews.json --analysis-type bias --competencies technical,leadership --trend-analysis --period quarterly --format json --output calibration/q1_bias.json
```

**Output Formats:**
- **JSON:** Structured calibration report containing score distributions, interviewer deviation metrics, bias indicators, trend data (if enabled), and prioritized coaching recommendations.
- **Text:** Human-readable report with summary statistics, flagged interviewers, bias findings, and actionable improvement recommendations formatted for management review.
- **Both (default):** With `--output`, writes JSON and text files there; without `--output`, prints the text report to stdout and writes nothing.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Loop designer produces generic rounds with no role-specific focus | The `--competencies` flag was omitted, so the tool falls back to default competency mapping for the role family | Re-run with explicit `--competencies` listing the 3-5 most critical skills for the position |
| Question bank output has too many behavioral questions and too few technical ones | The `--question-types` flag was not provided, causing the generator to use a balanced default split | Supply `--question-types technical,situational` (or whichever mix is needed) to control the ratio |
| Hiring calibrator reports "insufficient data" for bias detection | The input JSON contains fewer than 10 interview records, which is below the statistical minimum | Collect more interview data before running bias analysis; use `--analysis-type scoring` for small datasets |
| Calibrator trend analysis returns empty results | The input data lacks date fields or all records fall within a single period | Ensure each interview record has a valid date field and that the dataset spans multiple periods matching `--period` |
| Loop designer ignores the `--team` flag | The team value does not match any of the predefined team mappings in the tool | Check supported team names in the tool's `TEAM_CONFIGS` dictionary, or omit `--team` and rely on competency overrides |
| Score distribution chart shows all interviewers clustered at the same score | Interviewers are not applying the full 1-4 rubric scale (central tendency bias) | Run `--analysis-type calibration` to identify leniency/severity patterns and use the coaching recommendations |
| Question bank generates duplicate questions across competency areas | Overlapping competency keywords (e.g., "leadership" appears in both behavioral and technical mappings) | Use more specific competency terms or reduce `--num-questions` to avoid exhausting the unique question pool |

## Success Criteria

- **Interview loop coverage:** Every generated loop maps 100% of required competencies to at least one round with a dedicated scoring dimension.
- **Question bank diversity:** Generated banks contain no more than 15% duplicate or near-duplicate questions across competency areas.
- **Calibration detection accuracy:** Bias detection flags interviewer score deviation greater than 0.5 standard deviations from the team mean with at least 80% precision.
- **Time-to-design reduction:** Designing a complete interview loop (rounds, scorecards, question sets) takes under 10 minutes compared to the typical 2-4 hours of manual design.
- **Rubric consistency:** Generated scoring rubrics achieve inter-rater reliability (Cohen's kappa) of 0.7 or higher when tested with calibration panels.
- **Candidate experience alignment:** Loops designed with this tool target a candidate experience satisfaction score of 4.0/5.0 or above.
- **Hiring quality signal:** Organizations using the calibrator report a correlation of 0.6 or higher between interview scores and 6-month performance reviews.
