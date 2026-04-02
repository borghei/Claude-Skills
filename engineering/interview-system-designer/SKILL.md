---
name: interview-system-designer
description: >
  Designs calibrated interview loops, competency-based question banks, and
  hiring calibration systems. Use when designing interview processes, creating
  hiring pipelines, generating scoring rubrics, analyzing interviewer bias,
  or building question banks for engineering, product, or design roles.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  updated: 2026-03-31
---
# Interview System Designer

The agent designs role-specific interview loops, generates competency-based question banks with scoring rubrics, and detects interviewer bias through statistical calibration analysis.

## Quick Start

```bash
# Design a complete interview loop for a senior software engineer role
python loop_designer.py --role "Senior Software Engineer" --level senior --team platform --output loops/

# Generate a question bank for a product manager position
python question_bank_generator.py --role "Product Manager" --level senior --competencies leadership,strategy,analytics --output questions/

# Analyze interview calibration across candidates and interviewers
python hiring_calibrator.py --input interview_data.json --output calibration_report.json --analysis-type full
```

---

## Core Workflows

### Workflow 1: Design an Interview Loop

1. Define role requirements (title, level, team, 3-5 critical competencies)
2. Run `loop_designer.py` with role parameters to generate rounds, time allocations, and scorecards
3. Review generated loop for competency coverage -- every required competency maps to at least one round
4. Customize interviewer skill requirements per round
5. **Validation checkpoint:** 100% competency coverage; no round exceeds 90 minutes; total loop under 6 hours

```bash
python loop_designer.py --role "Staff Data Scientist" --level staff \
  --competencies ml,statistics,leadership --format json --output loops/ds-staff.json
```

### Workflow 2: Generate a Question Bank

1. Identify target role and experience level
2. Select competency areas and question types (technical, behavioral, situational)
3. Run `question_bank_generator.py` to produce questions with scoring rubrics
4. Review for duplicate or overlapping questions across competency areas
5. **Validation checkpoint:** <15% duplicate rate; each competency has 3+ questions; calibration examples (poor/good/great) present for every question

```bash
python question_bank_generator.py --role "Frontend Engineer" \
  --competencies react,typescript,system-design --num-questions 30
```

### Workflow 3: Calibrate Hiring Bar

1. Collect interview results data (minimum 10 records for statistical significance)
2. Run `hiring_calibrator.py` with comprehensive analysis
3. Review interviewer deviation metrics -- flag anyone >0.5 standard deviations from team mean
4. Generate coaching recommendations for flagged interviewers
5. **Validation checkpoint:** Bias detection precision >80%; score distribution follows target (20/40/30/10 split)

```bash
python hiring_calibrator.py --input q1_interviews.json \
  --analysis-type comprehensive --trend-analysis --period quarterly
```

---

## Interview Loop Templates

### Software Engineering Loops

| Level | Duration | Rounds | Focus Areas |
|-------|----------|--------|-------------|
| Junior/Mid (2-4 yr) | 3-4 hours | 3-4 | Coding fundamentals, debugging, system basics, growth mindset |
| Senior (5-8 yr) | 4-5 hours | 4-5 | System design, technical leadership, mentoring, code quality |
| Staff+ (8+ yr) | 5-6 hours | 5-6 | Architecture vision, org impact, technical strategy, cross-functional leadership |

**Senior Software Engineer Example:**
1. Technical Phone Screen (45min) -- Advanced algorithms, optimization
2. System Design (60min) -- Scalability, trade-offs, architectural decisions
3. Coding Excellence (60min) -- Code quality, testing strategies, refactoring
4. Technical Leadership (45min) -- Mentoring, technical decisions, cross-team collaboration
5. Behavioral & Culture (30min) -- Leadership examples, conflict resolution

### Sample Questions by Level

**Junior:** "Implement a function to find the second largest element in an array"
**Senior:** "Design a real-time chat system supporting 1M concurrent users"
**Staff+:** "How would you evaluate and introduce a new programming language to the organization?"

**Behavioral (STAR Method):**
- "Tell me about a time you had to influence a decision without formal authority"
- "Walk me through a time when you had to make a decision with incomplete information"

---

## Scoring Rubric

### 4-Point Scale

| Score | Label | Description |
|-------|-------|-------------|
| 4 | Exceeds | Demonstrates mastery beyond required level |
| 3 | Meets | Solid performance meeting all requirements |
| 2 | Partial | Shows potential but has development areas |
| 1 | Does Not Meet | Significant gaps in required competencies |

### Calibration Benchmarks

- **Target distribution:** 20% (4s), 40% (3s), 30% (2s), 10% (1s)
- **Interviewer consistency:** <0.5 std dev from team average
- **Pass rate:** 15-25% for most roles
- **New hire correlation:** >0.6 between interview scores and 6-month performance

---

## Anti-Patterns

- **Unstandardized loops** -- different question sets per candidate prevent fair comparison; always use structured guides
- **Halo effect scoring** -- one strong answer inflates all dimensions; score each competency independently before debrief
- **Similarity bias** -- favoring candidates with similar backgrounds; require diverse panels and rotate assignments
- **Skipping calibration** -- interviewers drift over time without regular calibration sessions (monthly minimum)
- **Over-indexing on algorithms** -- testing LeetCode for a staff role that requires architecture and leadership; match round focus to actual job requirements
- **No debrief structure** -- unstructured debriefs lead to anchoring on the loudest voice; require independent score submission before group discussion

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Loop designer produces generic rounds with no role-specific focus | The `--competencies` flag was omitted, so the tool falls back to default competency mapping for the role family | Re-run with explicit `--competencies` listing the 3-5 most critical skills for the position |
| Question bank output has too many behavioral questions and too few technical ones | The `--question-types` flag was not provided, causing the generator to use a balanced default split | Supply `--question-types technical,system-design` (or whichever mix is needed) to control the ratio |
| Hiring calibrator reports "insufficient data" for bias detection | The input JSON contains fewer than 10 interview records, which is below the statistical minimum | Collect more interview data before running bias analysis; use `--analysis-type scoring` for small datasets |
| Calibrator trend analysis returns empty results | The input data lacks date fields or all records fall within a single period | Ensure each interview record has a valid date field and that the dataset spans multiple periods matching `--period` |
| Loop designer ignores the `--team` flag | The team value does not match any of the predefined team mappings in the tool | Check supported team names in the tool's `TEAM_CONFIGS` dictionary, or omit `--team` and rely on competency overrides |
| Score distribution chart shows all interviewers clustered at the same score | Interviewers are not applying the full 1-4 rubric scale (central tendency bias) | Run `--analysis-type calibration` to identify leniency/severity patterns and use the coaching recommendations |
| Question bank generates duplicate questions across competency areas | Overlapping competency keywords (e.g., "leadership" appears in both behavioral and technical mappings) | Use more specific competency terms or reduce `--num-questions` to avoid exhausting the unique question pool |

---

## Success Criteria

- **Interview loop coverage:** Every generated loop maps 100% of required competencies to at least one round with a dedicated scoring dimension.
- **Question bank diversity:** Generated banks contain no more than 15% duplicate or near-duplicate questions across competency areas.
- **Calibration detection accuracy:** Bias detection flags interviewer score deviation greater than 0.5 standard deviations from the team mean with at least 80% precision.
- **Time-to-design reduction:** Designing a complete interview loop (rounds, scorecards, question sets) takes under 10 minutes compared to the typical 2-4 hours of manual design.
- **Rubric consistency:** Generated scoring rubrics achieve inter-rater reliability (Cohen's kappa) of 0.7 or higher when tested with calibration panels.
- **Candidate experience alignment:** Loops designed with this tool target a candidate experience satisfaction score of 4.0/5.0 or above.
- **Hiring quality signal:** Organizations using the calibrator report a correlation of 0.6 or higher between interview scores and 6-month performance reviews.

---

## Scope & Limitations

**This skill covers:**
- Designing end-to-end interview loops for engineering, product, design, and data roles across all seniority levels (junior through principal)
- Generating competency-based question banks with structured scoring rubrics and calibration examples
- Detecting statistical bias and calibration drift across interviewers and time periods
- Producing scorecard templates, debrief guides, and interviewer assignment recommendations

**This skill does NOT cover:**
- Applicant tracking system (ATS) integration, job posting, or candidate sourcing pipeline management — see `hr-operations/talent-acquisition`
- Compensation benchmarking, offer negotiation strategy, or total rewards analysis — see `hr-operations/hr-business-partner`
- Workforce planning, headcount modeling, or organizational design — see `hr-operations/people-analytics`
- Post-hire onboarding program design or new-hire ramp-up tracking — see `engineering/codebase-onboarding`

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `hr-operations/talent-acquisition` | Feed designed interview loops and scorecards into the talent acquisition pipeline for end-to-end hiring execution | Loop JSON output → talent acquisition workflow input |
| `hr-operations/people-analytics` | Supply calibration reports and interviewer performance data for workforce-level hiring analytics | Calibrator JSON reports → people analytics dashboards |
| `engineering/codebase-onboarding` | Hand off hired candidate profiles and assessed competency gaps to onboarding plan generation | Scorecard results → onboarding skill-gap inputs |
| `hr-operations/hr-business-partner` | Provide interview quality metrics and pass-rate data to support hiring bar discussions with HR leadership | Calibration trend data → HRBP quarterly reviews |
| `product-team` | Align PM interview loop competencies with the product team's competency frameworks and role leveling guides | Competency matrix → PM loop designer `--competencies` input |
| `engineering/pr-review-expert` | Use coding round evaluation criteria to inform code review standards for new hires during their ramp period | Scoring rubric technical criteria → PR review checklist alignment |

---

## Tool Reference

### loop_designer.py

**Purpose:** Generates calibrated interview loops tailored to specific roles, levels, and teams. Produces complete loops with rounds, focus areas, time allocation, interviewer skill requirements, and scorecard templates.

**Usage:**
```bash
python loop_designer.py --role "Senior Software Engineer" --level senior --team platform --output loops/
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
python loop_designer.py --role "Staff Data Scientist" --level staff --competencies ml,statistics,leadership --format json --output loops/ds-staff.json
```

**Output Formats:**
- **JSON:** Structured loop definition with rounds array, competency mappings, time allocations, and scorecard templates suitable for programmatic consumption.
- **Text:** Human-readable interview guide with formatted round descriptions, interviewer requirements, and evaluation criteria.
- **Both (default):** Writes both JSON and text outputs to the specified directory.

---

### question_bank_generator.py

**Purpose:** Generates comprehensive, competency-based interview questions with detailed scoring criteria, follow-up probes, and calibration examples organized by competency area.

**Usage:**
```bash
python question_bank_generator.py --role "Frontend Engineer" --competencies react,typescript,system-design --output questions/
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
python question_bank_generator.py --role "Product Manager" --level mid --question-types behavioral,situational --num-questions 30 --format text
```

**Output Formats:**
- **JSON:** Array of question objects each containing the question text, competency area, difficulty level, scoring rubric (1-4 scale), follow-up probes, and calibration examples (poor/good/great answers).
- **Text:** Formatted question bank grouped by competency with inline scoring guidance and example answers for interviewer reference.
- **Both (default):** Writes both JSON and text outputs to the specified directory.

---

### hiring_calibrator.py

**Purpose:** Analyzes interview scores from multiple candidates and interviewers to detect bias, calibration issues, and inconsistent rubric application. Generates calibration reports with recommendations for interviewer coaching and process improvements.

**Usage:**
```bash
python hiring_calibrator.py --input interview_results.json --analysis-type comprehensive --output report.json
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
python hiring_calibrator.py --input q1_interviews.json --analysis-type bias --competencies technical,leadership --trend-analysis --period quarterly --format json --output calibration/q1_bias.json
```

**Output Formats:**
- **JSON:** Structured calibration report containing score distributions, interviewer deviation metrics, bias indicators, trend data (if enabled), and prioritized coaching recommendations.
- **Text:** Human-readable report with summary statistics, flagged interviewers, bias findings, and actionable improvement recommendations formatted for management review.
- **Both (default):** Writes both JSON and text outputs to the specified path.