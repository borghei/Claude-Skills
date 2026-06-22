---
name: tech-stack-evaluator
description: >
  Evaluate and compare technology stacks with TCO analysis, security assessment, and ecosystem
  health scoring. Use when comparing frameworks, calculating total cost of ownership,
  assessing migration paths, or analyzing ecosystem viability.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: technology-evaluation
  updated: 2026-06-17
  tags: [framework-comparison, tco-analysis, technology-evaluation]
---
# Technology Stack Evaluator

Evaluate and compare technologies, frameworks, and cloud providers with data-driven, weighted analysis and actionable recommendations.

## Core Capabilities

- **Technology comparison** — weighted multi-criteria scoring of frameworks and libraries across 8 categories.
- **TCO analysis** — 5-year total cost of ownership including hidden costs (technical debt, vendor lock-in, turnover).
- **Ecosystem health** — viability scoring from GitHub, npm, community, and corporate-backing metrics.
- **Security assessment** — vulnerability/patch scoring and compliance readiness for GDPR, SOC2, HIPAA, PCI-DSS.
- **Migration analysis** — complexity, effort, risk, and recommended approach (direct/phased/strangler).
- **Cloud comparison** — compare AWS, Azure, GCP for specific workloads.

## When to Use

- Comparing frontend/backend frameworks for new projects
- Evaluating cloud providers for specific workloads
- Planning technology migrations with risk assessment
- Calculating build vs. buy decisions with TCO
- Assessing open-source library viability

**When NOT to use:** trivial decisions between similar tools (use team preference), mandated technology choices (decision already made), emergency production issues (use monitoring tools).

## Clarify First

Before the evaluation, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Candidates** — the specific frameworks / libraries / cloud providers to compare (the subject of the analysis)
- [ ] **Analysis type** — comparison / TCO / ecosystem health / security / migration (selects which module runs)
- [ ] **Decision criteria & weights** — which of the 8 categories matter most for this context (drives the weighted scoring and recommendation)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

All scripts are Python library modules — import the class and call its methods. See `references/tool-reference.md` for full parameters and outputs.

| Tool | Purpose | Entry point |
|------|---------|-------------|
| `stack_comparator.py` | Weighted comparison across 8 categories | `from stack_comparator import StackComparator` |
| `tco_calculator.py` | Multi-year TCO incl. hidden costs | `from tco_calculator import TCOCalculator` |
| `ecosystem_analyzer.py` | Ecosystem health & viability scoring | `from ecosystem_analyzer import EcosystemAnalyzer` |
| `security_assessor.py` | Security posture & compliance readiness | `from security_assessor import SecurityAssessor` |
| `migration_analyzer.py` | Migration complexity, effort, risks | `from migration_analyzer import MigrationAnalyzer` |
| `report_generator.py` | Context-aware report rendering | `from report_generator import ReportGenerator` |
| `format_detector.py` | Detect/parse JSON, YAML, URL, or text input | `from format_detector import FormatDetector` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tool-reference.md](references/tool-reference.md)** — full constructor parameters, methods, scoring weights, and output formats for all 7 scripts. Read when wiring up or debugging any tool.
- **[references/usage-and-criteria.md](references/usage-and-criteria.md)** — example prompts, input formats (text/YAML/JSON), analysis depth tiers, confidence levels, troubleshooting table, and success criteria. Read before invoking the evaluator.
- **[references/metrics.md](references/metrics.md)** — detailed scoring algorithms and calculation formulas.
- **[references/examples.md](references/examples.md)** — input/output examples for all analysis types.
- **[references/workflows.md](references/workflows.md)** — step-by-step evaluation workflows for common scenarios.

## Scope & Limitations

**Covers:**
- Weighted multi-criteria comparison of frameworks, libraries, and cloud providers
- Multi-year TCO projections including hidden costs (technical debt, vendor lock-in, turnover)
- Ecosystem viability assessment using GitHub, npm, and community metrics
- Security posture scoring and compliance readiness for GDPR, SOC2, HIPAA, PCI-DSS

**Does NOT cover:**
- Live data fetching from GitHub API, npm registry, or vulnerability databases (all data must be provided as input dictionaries)
- Performance benchmarking or load testing (use `engineering/senior-qa` for test execution)
- Licensing legal review or contract negotiation (use `ra-qm-team` compliance skills for regulatory guidance)
- Team hiring or organizational design decisions (use `hr-operations/talent-acquisition` for staffing analysis)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/senior-security` | Feed security assessor output into deeper vulnerability analysis | `SecurityAssessor` results → security review input |
| `engineering/senior-devops` | Use TCO hosting projections to inform infrastructure planning | `TCOCalculator` hosting/scaling data → DevOps capacity models |
| `engineering/senior-qa` | Migration test coverage scores inform QA test planning | `MigrationAnalyzer` testing_requirements → QA test strategy |
| `ra-qm-team/compliance-auditor` | Compliance readiness gaps feed into formal audit preparation | `SecurityAssessor.assess_compliance()` missing features → audit checklist |
| `c-level-advisor/cto-advisor` | Executive summaries and TCO reports support CTO decision-making | `ReportGenerator` executive summary → strategic technology decisions |
| `product-team/product-manager` | Ecosystem viability and migration timelines inform product roadmaps | `EcosystemAnalyzer` + `MigrationAnalyzer` → roadmap planning |
