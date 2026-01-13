---
name: product-manager
description: Expert product management covering strategy, roadmapping, user research, prioritization frameworks, and stakeholder management.
version: 1.0.0
author: Claude Skills
category: product-design
tags: [product, strategy, roadmap, prioritization, research]
---

# Product Manager

Expert-level product management for building successful products.

## Core Competencies

- Product strategy and vision
- Roadmap planning
- User research and discovery
- Feature prioritization
- Stakeholder management
- Metrics and analytics
- Go-to-market planning
- Agile product development

## Product Strategy

### Vision Framework

```
VISION STATEMENT
What future do we want to create?
[Aspirational, 3-5 year horizon]

MISSION
How do we create that future?
[Actionable, explains our approach]

STRATEGY
What are our key bets?
[3-5 strategic pillars]

OBJECTIVES
How do we measure success?
[OKRs, quarterly targets]
```

### Strategy Canvas

| Dimension | Current State | Target State | Gap | Priority |
|-----------|---------------|--------------|-----|----------|
| User Experience | | | | |
| Feature Set | | | | |
| Performance | | | | |
| Pricing | | | | |
| Market Position | | | | |

## Prioritization Frameworks

### RICE Framework

```
RICE Score = (Reach × Impact × Confidence) / Effort

Reach: How many users affected per quarter
  - 10000+ users = 10
  - 5000-10000 = 8
  - 1000-5000 = 5
  - 500-1000 = 3
  - <500 = 1

Impact: Effect on users (0.25, 0.5, 1, 2, 3)
  - Massive = 3
  - High = 2
  - Medium = 1
  - Low = 0.5
  - Minimal = 0.25

Confidence: How sure are we (20%, 50%, 80%, 100%)
  - High = 100%
  - Medium = 80%
  - Low = 50%
  - Very Low = 20%

Effort: Person-months
  - 0.5, 1, 2, 3, 4, etc.
```

### ICE Framework

```
ICE Score = Impact × Confidence × Ease

Impact: 1-10 (effect on key metric)
Confidence: 1-10 (certainty of estimate)
Ease: 1-10 (simplicity of implementation)
```

### Priority Matrix

```
                    High Impact
                         |
    Do First        -----+-----    Plan Carefully
    (Quick Wins)         |         (Strategic)
                         |
    Low Effort ----------+---------- High Effort
                         |
    Fill-ins        -----+-----    Don't Do
    (When Available)     |         (Time Sinks)
                         |
                    Low Impact
```

## Roadmap Planning

### Roadmap Template

```markdown
# Product Roadmap - [Year/Quarter]

## Theme: [Strategic Theme]

### Now (Current Quarter)
| Feature | Goal | Metric | Status |
|---------|------|--------|--------|
| [Feature 1] | [Goal] | [KPI] | In Progress |
| [Feature 2] | [Goal] | [KPI] | Planning |

### Next (Next Quarter)
| Feature | Goal | Metric | Confidence |
|---------|------|--------|------------|
| [Feature 3] | [Goal] | [KPI] | High |
| [Feature 4] | [Goal] | [KPI] | Medium |

### Later (Future)
| Feature | Goal | Dependencies |
|---------|------|--------------|
| [Feature 5] | [Goal] | [Deps] |

## Key Assumptions
- [Assumption 1]
- [Assumption 2]

## Risks
- [Risk 1]: [Mitigation]
```

### Roadmap Presentation Structure

**For Executives:**
- Strategic themes
- Business outcomes
- Key milestones
- Resource needs

**For Engineering:**
- Technical requirements
- Dependencies
- Sprint allocation
- Technical debt balance

**For Sales/CS:**
- Customer-facing features
- Release timeline
- Competitive positioning
- Training needs

## User Research

### Research Methods

| Method | When to Use | Sample Size | Duration |
|--------|-------------|-------------|----------|
| User Interviews | Discovery, validation | 5-10 | 1-2 weeks |
| Surveys | Quantitative validation | 100+ | 1 week |
| Usability Testing | Design validation | 5-8 | 1 week |
| A/B Testing | Feature optimization | 1000+ | 2-4 weeks |
| Analytics | Behavioral insights | All users | Ongoing |

### Interview Guide Template

```markdown
# User Interview Guide: [Topic]

## Objectives
- [What we want to learn]

## Participant Criteria
- [Who we're talking to]

## Warm-up (5 min)
- Tell me about your role
- How long have you been using [product/solution]?

## Current Behavior (10 min)
- Walk me through how you currently [task]
- What tools do you use?
- What's most frustrating about this process?

## Problem Exploration (15 min)
- Tell me about a recent time when [problem]
- What did you do to solve it?
- How often does this happen?

## Solution Validation (15 min)
- [Show concept/prototype]
- What do you think this does?
- How would you use this?
- What's missing?

## Wrap-up (5 min)
- Is there anything else you'd like to share?
- Can we follow up with more questions?
```

### Research Synthesis

```
FINDINGS SUMMARY

Key Insights:
1. [Insight with supporting quotes]
2. [Insight with supporting quotes]
3. [Insight with supporting quotes]

User Segments Identified:
- Segment A: [Description, size, needs]
- Segment B: [Description, size, needs]

Opportunities:
- [Opportunity 1]
- [Opportunity 2]

Recommendations:
- [Action item 1]
- [Action item 2]
```

## PRD Template

```markdown
# Product Requirements Document
## [Feature Name]

### Overview
**Problem:** [What problem are we solving?]
**Solution:** [How are we solving it?]
**Success Metric:** [How will we measure success?]

### User Stories
As a [user type], I want to [action], so that [benefit].

### Requirements

#### Must Have (P0)
- [ ] [Requirement 1]
- [ ] [Requirement 2]

#### Should Have (P1)
- [ ] [Requirement 3]
- [ ] [Requirement 4]

#### Nice to Have (P2)
- [ ] [Requirement 5]

### User Flow
[Diagram or description]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

### Out of Scope
- [What we're NOT building]

### Technical Considerations
- [Dependencies]
- [Constraints]

### Open Questions
- [Question 1]
- [Question 2]

### Timeline
- Design: [Date]
- Development: [Date]
- QA: [Date]
- Release: [Date]
```

## Metrics Framework

### North Star Metric

```
NORTH STAR METRIC: [Metric Name]

Why this metric:
- Reflects customer value
- Leads to revenue
- Measurable and actionable

Supporting Metrics:
├── Acquisition: [Metric]
├── Activation: [Metric]
├── Retention: [Metric]
├── Revenue: [Metric]
└── Referral: [Metric]
```

### Product Analytics

**Funnel Metrics:**
```
Visitors → Sign-ups → Activated → Retained → Paying
  100%       10%         40%        60%        20%

Conversion Rates:
- Visit to Sign-up: 10%
- Sign-up to Activated: 40%
- Activated to Retained: 60%
- Retained to Paying: 20%
```

**Engagement Metrics:**
- DAU/MAU ratio
- Session frequency
- Feature adoption
- Time in product

**Business Metrics:**
- MRR/ARR
- ARPU
- LTV
- CAC
- Payback period

## Stakeholder Management

### RACI Matrix

| Decision | Responsible | Accountable | Consulted | Informed |
|----------|-------------|-------------|-----------|----------|
| Roadmap | PM | VP Product | Eng, Sales | All |
| Pricing | PM | CEO | Finance, Sales | All |
| UX | Designer | PM | Eng, Users | Sales |
| Tech Arch | Eng Lead | CTO | PM | All |

### Communication Cadence

| Stakeholder | Frequency | Format | Content |
|-------------|-----------|--------|---------|
| Engineering | Daily | Standup | Blockers, priorities |
| Leadership | Weekly | Sync | Progress, decisions |
| Sales | Bi-weekly | Meeting | Pipeline, feedback |
| Customers | Monthly | Newsletter | Updates, roadmap |

## Reference Materials

- `references/prioritization.md` - Prioritization frameworks
- `references/research_methods.md` - User research guide
- `references/roadmap_templates.md` - Roadmap formats
- `references/metrics_guide.md` - Product analytics

## Scripts

```bash
# RICE score calculator
python scripts/rice_calculator.py --features features.csv

# User research analyzer
python scripts/research_analyzer.py --interviews transcripts/

# Roadmap generator
python scripts/roadmap_gen.py --backlog backlog.csv --quarters 4

# Metrics dashboard
python scripts/metrics_dashboard.py --product myproduct
```
