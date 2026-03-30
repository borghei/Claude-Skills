---
name: interview-system-designer
description: >
  This skill should be used when the user asks to "design interview processes",
  "create hiring pipelines", "calibrate interview loops", "generate interview
  questions", "design competency matrices", "analyze interviewer bias", "create
  scoring rubrics", "build question banks", or "optimize hiring systems". Use
  for designing role-specific interview loops, competency assessments, and
  hiring calibration systems.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  updated: 2026-03-31
---
# Interview System Designer

Comprehensive interview system design, competency assessment, and hiring process optimization.

## Table of Contents

- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
  - [Interview Loop Designer](#1-interview-loop-designer)
  - [Question Bank Generator](#2-question-bank-generator)
  - [Hiring Calibrator](#3-hiring-calibrator)
- [Interview System Workflows](#interview-system-workflows)
  - [Role-Specific Loop Design](#role-specific-loop-design)
  - [Competency Matrix Development](#competency-matrix-development)
  - [Question Bank Creation](#question-bank-creation)
  - [Bias Mitigation Framework](#bias-mitigation-framework)
  - [Hiring Bar Calibration](#hiring-bar-calibration)
- [Competency Frameworks](#competency-frameworks)
- [Scoring & Calibration](#scoring--calibration)
- [Reference Documentation](#reference-documentation)
- [Industry Standards](#industry-standards)

---

## Quick Start

```bash
# Design a complete interview loop for a senior software engineer role
python loop_designer.py --role "Senior Software Engineer" --level senior --team platform --output loops/

# Generate a comprehensive question bank for a product manager position
python question_bank_generator.py --role "Product Manager" --level senior --competencies leadership,strategy,analytics --output questions/

# Analyze interview calibration across multiple candidates and interviewers
python hiring_calibrator.py --input interview_data.json --output calibration_report.json --analysis-type full
```

---

## Tools Overview

### 1. Interview Loop Designer

Generates calibrated interview loops tailored to specific roles, levels, and teams.

**Input:** Role definition (title, level, team, competency requirements)
**Output:** Complete interview loop with rounds, focus areas, time allocation, scorecard templates

**Key Features:**
- Role-specific competency mapping
- Level-appropriate question difficulty
- Interviewer skill requirements
- Time-optimized scheduling
- Standardized scorecards

**Usage:**
```bash
# Design loop for a specific role
python loop_designer.py --role "Staff Data Scientist" --level staff --team ml-platform

# Generate loop with specific focus areas
python loop_designer.py --role "Engineering Manager" --level senior --competencies leadership,technical,strategy

# Create loop for multiple levels
python loop_designer.py --role "Backend Engineer" --levels junior,mid,senior --output loops/backend/
```

### 2. Question Bank Generator

Creates comprehensive, competency-based interview questions with detailed scoring criteria.

**Input:** Role requirements, competency areas, experience level
**Output:** Structured question bank with scoring rubrics, follow-up probes, and calibration examples

**Key Features:**
- Competency-based question organization
- Level-appropriate difficulty progression
- Behavioral and technical question types
- Anti-bias question design
- Calibration examples (poor/good/great answers)

**Usage:**
```bash
# Generate questions for technical competencies
python question_bank_generator.py --role "Frontend Engineer" --competencies react,typescript,system-design

# Create behavioral question bank
python question_bank_generator.py --role "Product Manager" --question-types behavioral,leadership --output pm_questions/

# Generate questions for all levels
python question_bank_generator.py --role "DevOps Engineer" --levels junior,mid,senior,staff
```

### 3. Hiring Calibrator

Analyzes interview scores to detect bias, calibration issues, and recommends improvements.

**Input:** Interview results data (candidate scores, interviewer feedback, demographics)
**Output:** Calibration analysis, bias detection report, interviewer coaching recommendations

**Key Features:**
- Statistical bias detection
- Interviewer calibration analysis
- Score distribution analysis
- Recommendation engine
- Trend tracking over time

**Usage:**
```bash
# Analyze calibration across all interviews
python hiring_calibrator.py --input interview_results.json --analysis-type comprehensive

# Focus on specific competency areas
python hiring_calibrator.py --input data.json --competencies technical,leadership --output bias_report.json

# Track calibration trends over time
python hiring_calibrator.py --input historical_data.json --trend-analysis --period quarterly
```

---

## Interview System Workflows

### Role-Specific Loop Design

#### Software Engineering Roles

**Junior/Mid Software Engineer (2-4 years)**
- **Duration:** 3-4 hours across 3-4 rounds
- **Focus Areas:** Coding fundamentals, debugging, system understanding, growth mindset
- **Rounds:**
  1. Technical Phone Screen (45min) - Coding fundamentals, algorithms
  2. Coding Deep Dive (60min) - Problem-solving, code quality, testing
  3. System Design Basics (45min) - Component interaction, basic scalability
  4. Behavioral & Values (30min) - Team collaboration, learning agility

**Senior Software Engineer (5-8 years)**
- **Duration:** 4-5 hours across 4-5 rounds
- **Focus Areas:** System design, technical leadership, mentoring capability, domain expertise
- **Rounds:**
  1. Technical Phone Screen (45min) - Advanced algorithms, optimization
  2. System Design (60min) - Scalability, trade-offs, architectural decisions
  3. Coding Excellence (60min) - Code quality, testing strategies, refactoring
  4. Technical Leadership (45min) - Mentoring, technical decisions, cross-team collaboration
  5. Behavioral & Culture (30min) - Leadership examples, conflict resolution

**Staff+ Engineer (8+ years)**
- **Duration:** 5-6 hours across 5-6 rounds
- **Focus Areas:** Architectural vision, organizational impact, technical strategy, cross-functional leadership
- **Rounds:**
  1. Technical Phone Screen (45min) - System architecture, complex problem-solving
  2. Architecture Design (90min) - Large-scale systems, technology choices, evolution patterns
  3. Technical Strategy (60min) - Technical roadmaps, technology adoption, risk assessment
  4. Leadership & Influence (60min) - Cross-team impact, technical vision, stakeholder management
  5. Coding & Best Practices (45min) - Code quality standards, development processes
  6. Cultural & Strategic Fit (30min) - Company values, strategic thinking

#### Product Management Roles

**Product Manager (3-6 years)**
- **Duration:** 3-4 hours across 4 rounds
- **Focus Areas:** Product sense, analytical thinking, stakeholder management, execution
- **Rounds:**
  1. Product Sense (60min) - Feature prioritization, user empathy, market understanding
  2. Analytical Thinking (45min) - Data interpretation, metrics design, experimentation
  3. Execution & Process (45min) - Project management, cross-functional collaboration
  4. Behavioral & Leadership (30min) - Stakeholder management, conflict resolution

**Senior Product Manager (6-10 years)**
- **Duration:** 4-5 hours across 4-5 rounds
- **Focus Areas:** Product strategy, team leadership, business impact, market analysis
- **Rounds:**
  1. Product Strategy (75min) - Market analysis, competitive positioning, roadmap planning
  2. Leadership & Influence (60min) - Team building, stakeholder management, decision-making
  3. Data & Analytics (45min) - Advanced metrics, experimentation design, business intelligence
  4. Technical Collaboration (45min) - Technical trade-offs, engineering partnership
  5. Case Study Presentation (45min) - Past impact, lessons learned, strategic thinking

#### Design Roles

**UX Designer (2-5 years)**
- **Duration:** 3-4 hours across 3-4 rounds
- **Focus Areas:** Design process, user research, visual design, collaboration
- **Rounds:**
  1. Portfolio Review (60min) - Design process, problem-solving approach, visual skills
  2. Design Challenge (90min) - User-centered design, wireframing, iteration
  3. Collaboration & Process (45min) - Cross-functional work, feedback incorporation
  4. Behavioral & Values (30min) - User advocacy, creative problem-solving

**Senior UX Designer (5+ years)**
- **Duration:** 4-5 hours across 4-5 rounds
- **Focus Areas:** Design leadership, system thinking, research methodology, business impact
- **Rounds:**
  1. Portfolio Deep Dive (75min) - Design impact, methodology, leadership examples
  2. Design System Challenge (90min) - Systems thinking, scalability, consistency
  3. Research & Strategy (60min) - User research methods, data-driven design decisions
  4. Leadership & Mentoring (45min) - Design team leadership, process improvement
  5. Business & Strategy (30min) - Design's business impact, stakeholder management

### Competency Matrix Development

#### Technical Competencies

**Software Engineering**
- **Coding Proficiency:** Algorithm design, data structures, language expertise
- **System Design:** Architecture patterns, scalability, performance optimization
- **Testing & Quality:** Unit testing, integration testing, code review practices
- **DevOps & Tools:** CI/CD, monitoring, debugging, development workflows

**Data Science & Analytics**
- **Statistical Analysis:** Statistical methods, hypothesis testing, experimental design
- **Machine Learning:** Algorithm selection, model evaluation, feature engineering
- **Data Engineering:** ETL processes, data pipeline design, data quality
- **Business Intelligence:** Metrics design, dashboard creation, stakeholder communication

**Product Management**
- **Product Strategy:** Market analysis, competitive research, roadmap planning
- **User Research:** User interviews, usability testing, persona development
- **Data Analysis:** Metrics interpretation, A/B testing, cohort analysis
- **Technical Understanding:** API design, database concepts, system architecture

#### Behavioral Competencies

**Leadership & Influence**
- **Team Building:** Hiring, onboarding, team culture development
- **Mentoring & Coaching:** Skill development, career guidance, feedback delivery
- **Strategic Thinking:** Long-term planning, vision setting, decision-making frameworks
- **Change Management:** Process improvement, organizational change, resistance handling

**Communication & Collaboration**
- **Stakeholder Management:** Expectation setting, conflict resolution, alignment building
- **Cross-Functional Partnership:** Engineering-Product-Design collaboration
- **Presentation Skills:** Technical communication, executive briefings, documentation
- **Active Listening:** Empathy, question asking, perspective taking

**Problem-Solving & Innovation**
- **Analytical Thinking:** Problem decomposition, root cause analysis, hypothesis formation
- **Creative Problem-Solving:** Alternative solution generation, constraint navigation
- **Learning Agility:** Skill acquisition, adaptation to change, knowledge transfer
- **Risk Assessment:** Uncertainty navigation, trade-off analysis, mitigation planning

### Question Bank Creation

#### Technical Questions by Level

**Junior Level Questions**
- **Coding:** "Implement a function to find the second largest element in an array"
- **System Design:** "How would you design a simple URL shortener for 1000 users?"
- **Debugging:** "Walk through how you would debug a slow-loading web page"

**Senior Level Questions**
- **Architecture:** "Design a real-time chat system supporting 1M concurrent users"
- **Leadership:** "Describe how you would onboard a new team member in your area"
- **Trade-offs:** "Compare microservices vs monolith for a rapidly scaling startup"

**Staff+ Level Questions**
- **Strategy:** "How would you evaluate and introduce a new programming language to the organization?"
- **Influence:** "Describe a time you drove technical consensus across multiple teams"
- **Vision:** "How do you balance technical debt against feature development?"

#### Behavioral Questions Framework

**STAR Method Implementation**
- **Situation:** Context and background of the scenario
- **Task:** Specific challenge or goal that needed to be addressed
- **Action:** Concrete steps taken to address the challenge
- **Result:** Measurable outcomes and lessons learned

**Sample Questions:**
- "Tell me about a time you had to influence a decision without formal authority"
- "Describe a situation where you had to deliver difficult feedback to a colleague"
- "Give an example of when you had to adapt your communication style for different audiences"
- "Walk me through a time when you had to make a decision with incomplete information"

### Bias Mitigation Framework

#### Structural Bias Prevention

**Interview Panel Composition**
- Diverse interviewer panels (gender, ethnicity, experience level)
- Rotating panel assignments to prevent pattern bias
- Anonymous resume screening for initial phone screens
- Standardized question sets to ensure consistency

**Process Standardization**
- Structured interview guides with required probing questions
- Consistent time allocation across all candidates
- Standardized evaluation criteria and scoring rubrics
- Required justification for all scoring decisions

#### Cognitive Bias Recognition

**Common Interview Biases**
- **Halo Effect:** One strong impression influences overall assessment
- **Confirmation Bias:** Seeking information that confirms initial impressions
- **Similarity Bias:** Favoring candidates with similar backgrounds/experiences
- **Contrast Effect:** Comparing candidates against each other rather than standard
- **Anchoring Bias:** Over-relying on first piece of information received

**Mitigation Strategies**
- Pre-interview bias awareness training for all interviewers
- Structured debrief sessions with independent score recording
- Regular calibration sessions with example candidate discussions
- Statistical monitoring of scoring patterns by interviewer and demographic

### Hiring Bar Calibration

#### Calibration Methodology

**Regular Calibration Sessions**
- Monthly interviewer calibration meetings
- Shadow interviewing for new interviewers (minimum 5 sessions)
- Quarterly cross-team calibration reviews
- Annual hiring bar review and adjustment process

**Performance Tracking**
- New hire performance correlation with interview scores
- Interviewer accuracy tracking (prediction vs actual performance)
- False positive/negative analysis
- Offer acceptance rate analysis by interviewer

**Feedback Loops**
- Six-month new hire performance reviews
- Manager feedback on interview process effectiveness
- Candidate experience surveys and feedback integration
- Continuous process improvement based on data analysis

---

## Competency Frameworks

### Engineering Competency Levels

#### Level 1-2: Individual Contributor (Junior/Mid)
- **Technical Skills:** Language proficiency, testing basics, code review participation
- **Problem Solving:** Structured approach to debugging, logical thinking
- **Communication:** Clear status updates, effective question asking
- **Learning:** Proactive skill development, mentorship seeking

#### Level 3-4: Senior Individual Contributor
- **Technical Leadership:** Architecture decisions, code quality advocacy
- **Mentoring:** Junior developer guidance, knowledge sharing
- **Project Ownership:** End-to-end feature delivery, stakeholder communication
- **Innovation:** Process improvement, technology evaluation

#### Level 5-6: Staff+ Engineer
- **Organizational Impact:** Cross-team technical leadership, strategic planning
- **Technical Vision:** Long-term architectural planning, technology roadmap
- **People Development:** Team growth, hiring contribution, culture building
- **External Influence:** Industry contribution, thought leadership

### Product Management Competency Levels

#### Level 1-2: Associate/Product Manager
- **Product Execution:** Feature specification, requirements gathering
- **User Focus:** User research participation, feedback collection
- **Data Analysis:** Basic metrics analysis, experiment interpretation
- **Stakeholder Management:** Cross-functional collaboration, communication

#### Level 3-4: Senior Product Manager
- **Strategic Thinking:** Market analysis, competitive positioning
- **Leadership:** Cross-functional team leadership, decision making
- **Business Impact:** Revenue impact, market share growth
- **Process Innovation:** Product development process improvement

#### Level 5-6: Principal Product Manager
- **Vision Setting:** Product strategy, market direction
- **Organizational Influence:** Executive communication, team building
- **Innovation Leadership:** New market creation, disruptive thinking
- **Talent Development:** PM team growth, hiring leadership

---

## Scoring & Calibration

### Scoring Rubric Framework

#### 4-Point Scoring Scale
- **4 - Exceeds Expectations:** Demonstrates mastery beyond required level
- **3 - Meets Expectations:** Solid performance meeting all requirements
- **2 - Partially Meets:** Shows potential but has development areas
- **1 - Does Not Meet:** Significant gaps in required competencies

#### Competency-Specific Scoring

**Technical Competencies**
- Code Quality (4): Clean, maintainable, well-tested code with excellent documentation
- Code Quality (3): Functional code with good structure and basic testing
- Code Quality (2): Working code with some structural issues or missing tests
- Code Quality (1): Non-functional or poorly structured code with significant issues

**Leadership Competencies**
- Team Influence (4): Drives team success, develops others, creates lasting positive change
- Team Influence (3): Contributes positively to team dynamics and outcomes
- Team Influence (2): Shows leadership potential with some effective examples
- Team Influence (1): Limited evidence of leadership ability or negative team impact

### Calibration Standards

#### Statistical Benchmarks
- Target score distribution: 20% (4s), 40% (3s), 30% (2s), 10% (1s)
- Interviewer consistency target: <0.5 standard deviation from team average
- Pass rate target: 15-25% for most roles (varies by level and market conditions)
- Time to hire target: 2-3 weeks from first interview to offer

#### Quality Metrics
- New hire 6-month performance correlation: >0.6 with interview scores
- Interviewer agreement rate: >80% within 1 point on final recommendations
- Candidate experience satisfaction: >4.0/5.0 average rating
- Offer acceptance rate: >85% for preferred candidates

---

## Reference Documentation

### Interview Templates
- Role-specific interview guides and question banks
- Scorecard templates for consistent evaluation
- Debrief facilitation guides for effective team discussions

### Bias Mitigation Resources
- Unconscious bias training materials and exercises
- Structured interviewing best practices checklist
- Demographic diversity tracking and reporting templates

### Calibration Tools
- Interview performance correlation analysis templates
- Interviewer coaching and development frameworks
- Hiring pipeline metrics and dashboard specifications

---

## Industry Standards

### Best Practices Integration
- Google's structured interviewing methodology
- Amazon's Leadership Principles assessment framework
- Microsoft's competency-based evaluation system
- Netflix's culture fit assessment approach

### Compliance & Legal Considerations
- EEOC compliance requirements and documentation
- ADA accommodation procedures and guidelines
- International hiring law considerations
- Privacy and data protection requirements (GDPR, CCPA)

### Continuous Improvement Framework
- Regular process auditing and refinement cycles
- Industry benchmarking and comparative analysis
- Technology integration for interview optimization
- Candidate experience enhancement initiatives

This comprehensive interview system design framework provides the structure and tools necessary to build fair, effective, and scalable hiring processes that consistently identify top talent while minimizing bias and maximizing candidate experience.

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