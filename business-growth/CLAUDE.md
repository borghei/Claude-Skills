# Business & Growth Skills - Claude Code Guidance

This guide covers the 21 production-ready business and growth skills, organized into three clusters: **GTM operations** (customer success, sales engineering, revenue ops), **growth tactics** (CRO sub-skills, churn, referral, pricing, contracts, competitive teardown), and **commercial mechanics** (deal-desk, channel-economics, partnerships-architect, commercial-policy — added Apr 2026).

## Business & Growth Skills Overview (21 skills)

### GTM operations
- **customer-success-manager/** - Customer health scoring, churn risk analysis, expansion opportunities (3 Python tools)
- **sales-engineer/** - Technical discovery, RFP analysis, competitive positioning, POC planning (3 Python tools)
- **revenue-operations/** - Pipeline analysis, forecast accuracy, GTM efficiency metrics (3 Python tools)

### Growth tactics
- **churn-prevention** · **competitive-teardown** · **competitor-alternatives** · **contract-and-proposal-writer** · **form-cro** · **free-tool-strategy** · **onboarding-cro** · **page-cro** · **paywall-upgrade-cro** · **popup-cro** · **offer-design** (offer stack, guarantee and urgency scorer; 1 Python tool) · **pricing-strategy** · **referral-program** · **signup-flow-cro**

### Commercial mechanics (Apr 2026 additions)
- **deal-desk/** - Charter, approval matrix, deal-review packets, velocity analysis (3 Python tools)
- **channel-economics/** - 6-channel decision tree, TCO framework, tier economics, mix optimizer (3 Python tools)
- **partnerships-architect/** - Partnership types, deal structures, partner evaluation, ROI modeler (3 Python tools)
- **commercial-policy/** - Policy charter, compliance checker, terms-deviation analyzer, policy generator (3 Python tools)

**Total Tools:** 30+ Python automation tools, 25+ knowledge bases, 19+ templates

## Python Automation Tools

### Customer Success Manager Tools

#### 1. Health Score Calculator (`customer-success-manager/scripts/health_score_calculator.py`)

**Purpose:** Multi-dimensional customer health scoring with trend analysis

**Features:**
- Weighted scoring across 4 dimensions (usage, engagement, support, relationship)
- Red/Yellow/Green classification with configurable thresholds
- Trend analysis comparing current vs previous period
- Segment-aware benchmarking (Enterprise/Mid-Market/SMB)

**Usage:**
```bash
python customer-success-manager/scripts/health_score_calculator.py customer_data.json
python customer-success-manager/scripts/health_score_calculator.py customer_data.json --format json
```

#### 2. Churn Risk Analyzer (`customer-success-manager/scripts/churn_risk_analyzer.py`)

**Purpose:** Identify at-risk accounts with intervention recommendations

**Features:**
- Risk scoring based on behavioral signals
- Warning signal detection and categorization
- Tier-appropriate intervention playbooks
- Urgency-based prioritization

**Usage:**
```bash
python customer-success-manager/scripts/churn_risk_analyzer.py customer_data.json
python customer-success-manager/scripts/churn_risk_analyzer.py customer_data.json --format json
```

#### 3. Expansion Opportunity Scorer (`customer-success-manager/scripts/expansion_opportunity_scorer.py`)

**Purpose:** Identify upsell and cross-sell opportunities

**Features:**
- Adoption depth analysis across product modules
- Whitespace mapping for unused features
- Revenue opportunity estimation
- Priority ranking by effort and impact

**Usage:**
```bash
python customer-success-manager/scripts/expansion_opportunity_scorer.py customer_data.json
python customer-success-manager/scripts/expansion_opportunity_scorer.py customer_data.json --format json
```

### Sales Engineer Tools

#### 4. RFP Response Analyzer (`sales-engineer/scripts/rfp_response_analyzer.py`)

**Purpose:** Score RFP/RFI coverage and identify gaps

**Features:**
- Requirement coverage scoring (Full/Partial/Planned/Gap)
- Effort estimation per requirement
- Gap identification with mitigation strategies
- Overall bid/no-bid recommendation

**Usage:**
```bash
python sales-engineer/scripts/rfp_response_analyzer.py rfp_data.json
python sales-engineer/scripts/rfp_response_analyzer.py rfp_data.json --format json
```

#### 5. Competitive Matrix Builder (`sales-engineer/scripts/competitive_matrix_builder.py`)

**Purpose:** Generate feature comparison matrices and competitive positioning

**Features:**
- Feature-by-feature comparison matrix
- Competitive scoring with weighted categories
- Differentiator identification
- Battlecard-ready output

**Usage:**
```bash
python sales-engineer/scripts/competitive_matrix_builder.py competitive_data.json
python sales-engineer/scripts/competitive_matrix_builder.py competitive_data.json --format json
```

#### 6. POC Planner (`sales-engineer/scripts/poc_planner.py`)

**Purpose:** Plan proof-of-concept engagements

**Features:**
- Timeline estimation based on scope
- Resource allocation planning
- Success criteria definition
- Evaluation scorecard generation

**Usage:**
```bash
python sales-engineer/scripts/poc_planner.py poc_data.json
python sales-engineer/scripts/poc_planner.py poc_data.json --format json
```

### Revenue Operations Tools

#### 7. Pipeline Analyzer (`revenue-operations/scripts/pipeline_analyzer.py`)

**Purpose:** Analyze sales pipeline health and velocity

**Features:**
- Coverage ratio calculation (pipeline/quota)
- Stage conversion rate analysis
- Sales velocity metrics (4-lever model)
- Deal aging analysis

**Usage:**
```bash
python revenue-operations/scripts/pipeline_analyzer.py pipeline_data.json
python revenue-operations/scripts/pipeline_analyzer.py pipeline_data.json --format json
```

#### 8. Forecast Accuracy Tracker (`revenue-operations/scripts/forecast_accuracy_tracker.py`)

**Purpose:** Measure and improve forecast accuracy

**Features:**
- MAPE (Mean Absolute Percentage Error) calculation
- Forecast bias detection (over/under-forecasting)
- Period-over-period trend analysis
- Category-level accuracy breakdown

**Usage:**
```bash
python revenue-operations/scripts/forecast_accuracy_tracker.py forecast_data.json
python revenue-operations/scripts/forecast_accuracy_tracker.py forecast_data.json --format json
```

#### 9. GTM Efficiency Calculator (`revenue-operations/scripts/gtm_efficiency_calculator.py`)

**Purpose:** Calculate go-to-market efficiency metrics

**Features:**
- Magic number calculation
- LTV:CAC ratio analysis
- CAC payback period
- Burn multiple assessment
- Industry benchmarking

**Usage:**
```bash
python revenue-operations/scripts/gtm_efficiency_calculator.py gtm_data.json
python revenue-operations/scripts/gtm_efficiency_calculator.py gtm_data.json --format json
```

## Quality Standards

**All business & growth Python tools must:**
- Use standard library only (no external dependencies)
- Support both JSON and human-readable output via `--format` flag
- Provide clear error messages for invalid input
- Return appropriate exit codes
- Process files locally (no API calls)
- Include argparse CLI with `--help` support

## Related Skills

- **Marketing:** Content creation, demand generation -> `../marketing/`
- **Product Team:** User research, feature prioritization -> `../product-team/`
- **C-Level:** Strategic planning -> `../c-level-advisor/`
- **Engineering:** Technical implementation -> `../engineering/`

---

**Last Updated:** February 2026
**Skills Deployed:** 3/3 business & growth skills production-ready
**Total Tools:** 9 Python automation tools
