# Workflows, Loop Templates & Scoring

Read this when running the design workflows, building an interview loop, or applying the
scoring rubric, calibration benchmarks, and anti-pattern guardrails.

## Quick Start

```bash
# Design a complete interview loop for a senior software engineer role
python3 scripts/loop_designer.py --role "Senior Software Engineer" --level senior --team platform --output loops/

# Generate a question bank for a product manager position
python3 scripts/question_bank_generator.py --role "Product Manager" --level senior --competencies leadership,strategy,analytics --output questions/

# Analyze interview calibration across candidates and interviewers
python3 scripts/hiring_calibrator.py --input interview_data.json --output calibration_report.json --analysis-type comprehensive
```

## Core Workflows

### Workflow 1: Design an Interview Loop

1. Define role requirements (title, level, team, 3-5 critical competencies)
2. Run `loop_designer.py` with role parameters to generate rounds, time allocations, and scorecards
3. Review generated loop for competency coverage -- every required competency maps to at least one round
4. Customize interviewer skill requirements per round
5. **Validation checkpoint:** 100% competency coverage; no round exceeds 90 minutes; total loop under 6 hours

```bash
python3 scripts/loop_designer.py --role "Staff Data Scientist" --level staff \
  --competencies ml,statistics,leadership --format json --output loops/ds-staff.json
```

### Workflow 2: Generate a Question Bank

1. Identify target role and experience level
2. Select competency areas and question types (technical, behavioral, situational)
3. Run `question_bank_generator.py` to produce questions with scoring rubrics
4. Review for duplicate or overlapping questions across competency areas
5. **Validation checkpoint:** <15% duplicate rate; each competency has 3+ questions; calibration examples (poor/good/great) present for every question

```bash
python3 scripts/question_bank_generator.py --role "Frontend Engineer" \
  --competencies react,typescript,system-design --num-questions 30
```

### Workflow 3: Calibrate Hiring Bar

1. Collect interview results data (minimum 10 records for statistical significance)
2. Run `hiring_calibrator.py` with comprehensive analysis
3. Review interviewer deviation metrics -- flag anyone >0.5 standard deviations from team mean
4. Generate coaching recommendations for flagged interviewers
5. **Validation checkpoint:** Bias detection precision >80%; score distribution follows target (20/40/30/10 split)

```bash
python3 scripts/hiring_calibrator.py --input q1_interviews.json \
  --analysis-type comprehensive --trend-analysis --period quarterly
```

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

## Anti-Patterns

- **Unstandardized loops** -- different question sets per candidate prevent fair comparison; always use structured guides
- **Halo effect scoring** -- one strong answer inflates all dimensions; score each competency independently before debrief
- **Similarity bias** -- favoring candidates with similar backgrounds; require diverse panels and rotate assignments
- **Skipping calibration** -- interviewers drift over time without regular calibration sessions (monthly minimum)
- **Over-indexing on algorithms** -- testing LeetCode for a staff role that requires architecture and leadership; match round focus to actual job requirements
- **No debrief structure** -- unstructured debriefs lead to anchoring on the loudest voice; require independent score submission before group discussion
