# Sales Success Skills - Claude Code Guidance

This guide covers the 5 sales success skills and planned Python automation tools for the domain.

## Sales Success Skills Overview

**Available Skills:**
1. **account-executive/** - Pipeline management, discovery and qualification, solution selling, negotiation, deal closing, and forecasting
2. **sales-engineer/** - Technical discovery, solution design, demo delivery, RFP responses, and proof-of-concept management
3. **customer-success-manager/** - Onboarding, health scoring, churn prevention, expansion revenue, and executive business reviews
4. **sales-operations/** - CRM administration, territory design, quota setting, pipeline reporting, and sales process optimization
5. **solutions-architect/** - Technical requirements analysis, solution design, integration architecture, enterprise alignment, and stakeholder management

**Current Status:** 5 SKILL.md knowledge bases deployed. Python automation tools planned for next phase.

## Skill Selection Guide

| Need | Use This Skill |
|------|---------------|
| Closing deals and managing sales cycles | account-executive |
| Technical selling and product demonstrations | sales-engineer |
| Post-sale retention and account growth | customer-success-manager |
| Sales process design and reporting infrastructure | sales-operations |
| Complex enterprise solution design and integration | solutions-architect |

**Overlap Guidance:**
- account-executive vs sales-engineer: Use account-executive for commercial deal strategy and negotiation; use sales-engineer for technical validation and demo execution within the same deal cycle.
- sales-engineer vs solutions-architect: Use sales-engineer for pre-sales technical engagement on individual deals; use solutions-architect for cross-deal enterprise architecture and long-term integration planning.
- customer-success-manager handles post-close; account-executive handles pre-close. Handoff criteria and shared account plans bridge the two.
- sales-operations supports all other skills by providing the data infrastructure, territory definitions, and process guardrails they operate within.

## Recommended Python Tools (Planned)

### Pipeline and Deal Management
- **Pipeline Analyzer** (`sales-operations/scripts/pipeline_analyzer.py`) - Coverage ratio calculation, stage conversion rates, deal aging analysis, and velocity metrics
- **Win-Rate Calculator** (`sales-operations/scripts/win_rate_calculator.py`) - Historical win rates by segment, deal size, sales cycle length, and competitive presence
- **Deal Scoring Engine** (`account-executive/scripts/deal_scoring_engine.py`) - Score deal health based on MEDDPICC or BANT qualification criteria

### Territory and Quota Planning
- **Territory Planner** (`sales-operations/scripts/territory_planner.py`) - Balance territories by account count, revenue potential, and geographic distribution
- **Quota Attainment Tracker** (`sales-operations/scripts/quota_attainment_tracker.py`) - Track individual and team quota attainment with pacing indicators

### Customer Success
- **Customer Health Scorer** (`customer-success-manager/scripts/customer_health_scorer.py`) - Multi-dimensional health scoring across usage, engagement, support, and relationship signals
- **Renewal Forecaster** (`customer-success-manager/scripts/renewal_forecaster.py`) - Predict renewal likelihood based on health score trends, contract terms, and engagement history

### Technical Sales
- **RFP Coverage Analyzer** (`sales-engineer/scripts/rfp_coverage_analyzer.py`) - Score requirement coverage, identify gaps, and generate response prioritization
- **POC Success Tracker** (`solutions-architect/scripts/poc_success_tracker.py`) - Track proof-of-concept milestones, success criteria completion, and evaluation scores

## Integration with Other Domains

### Business & Growth Integration
| Sales Success Skill | Business & Growth Skill | Integration Pattern |
|--------------------|------------------------|-------------------|
| account-executive | revenue-operations | Pipeline data feeds into revenue forecasting and GTM efficiency metrics |
| customer-success-manager | customer-success-manager (business-growth) | Complementary perspectives; sales-success focuses on execution, business-growth on strategy |
| sales-operations | revenue-operations | Shared pipeline and forecast infrastructure; sales-ops handles CRM, rev-ops handles cross-functional metrics |

### Marketing Integration
| Sales Success Skill | Marketing Skill | Integration Pattern |
|--------------------|----------------|-------------------|
| account-executive | marketing-demand-acquisition | Marketing-sourced leads feed into AE pipeline; shared MQL-to-SQL conversion metrics |
| sales-engineer | content-creator | Technical content (whitepapers, solution briefs) supports SE demo and discovery workflows |
| sales-operations | campaign-analytics | Attribution data connects marketing spend to closed-won revenue |

**Cross-Domain Workflow:**
```bash
# 1. Analyze pipeline health
python sales-operations/scripts/pipeline_analyzer.py pipeline_data.json

# 2. Calculate win rates by segment
python sales-operations/scripts/win_rate_calculator.py deal_history.json

# 3. Score customer health for expansion opportunities
python customer-success-manager/scripts/customer_health_scorer.py customer_data.json

# 4. Plan balanced territories for next quarter
python sales-operations/scripts/territory_planner.py account_data.json
```

## Quality Standards

**All sales success Python tools must:**
- Use standard library only (no external dependencies)
- Support both JSON and human-readable output via `--format` flag
- Provide clear error messages for invalid input
- Return appropriate exit codes (0 success, 1 error)
- Process files locally with no API calls or network access
- Include argparse CLI with `--help` support
- Accept standard CRM export formats (CSV and JSON)

**Skill documentation must:**
- Reference established sales methodologies (MEDDPICC, Challenger, SPIN, Sandler)
- Include realistic deal scenarios with sample data structures
- Provide stage-appropriate templates (discovery scripts, demo outlines, proposal frameworks)
- Address multi-stakeholder selling and enterprise complexity

## Related Skills

- **Business & Growth:** Revenue operations, customer success strategy -> `../business-growth/`
- **Marketing:** Demand generation, campaign analytics -> `../marketing-skill/`
- **Product Team:** Product positioning, competitive analysis -> `../product-team/`
- **C-Level:** GTM strategy, revenue planning -> `../c-level-advisor/`
- **Engineering:** Technical integration, solution architecture -> `../engineering-team/`

## Additional Resources

- **Main Documentation:** `../CLAUDE.md`
- **Standards Library:** `../standards/`

---

**Last Updated:** February 2026
**Skills Deployed:** 5/5 sales success skills (SKILL.md knowledge bases)
**Python Tools:** Planned for next development phase
