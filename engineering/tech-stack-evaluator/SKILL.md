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
  updated: 2026-11-08
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

Before the evaluation, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Candidates:** the specific frameworks / libraries / cloud providers to compare (the subject of the analysis).
- **Analysis type:** comparison / TCO / ecosystem health / security / migration (selects which module runs).
- **Decision criteria & weights:** which of the 8 categories matter most for this context (drives the weighted scoring and recommendation).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

`scripts/evaluate.py` is the command-line entry point; the other scripts are the library
modules it calls. Nothing fetches live data: every number comes from the input file, so the
output is only as good as the inputs.

```bash
python scripts/evaluate.py compare assets/sample_compare_evidenced.json   # exit 0, CLEAR winner
python scripts/evaluate.py compare assets/sample_input_structured.json    # exit 1, UNSUPPORTED
python scripts/evaluate.py tco assets/sample_input_tco.json
python scripts/evaluate.py ecosystem assets/sample_input_ecosystem.json
python scripts/evaluate.py security assets/sample_input_security.json --format json
python scripts/evaluate.py migration assets/sample_input_migration.json
python scripts/evaluate.py parse assets/sample_input_text.json            # free text -> structured request
```

| Subcommand | Library module | Input section |
|------|---------|-------------|
| `compare` | `stack_comparator.py` | `comparison`: candidates with a 0-100 `score` and an `evidence` note per category, plus `weights` and `use_case` |
| `tco` | `tco_calculator.py` | `tco_analysis`: initial, operational, scaling and productivity costs |
| `ecosystem` | `ecosystem_analyzer.py` | `ecosystem`: repository, registry, community and backing metrics |
| `security` | `security_assessor.py` | `security`: CVE counts, patch times, security features, compliance targets |
| `migration` | `migration_analyzer.py` | `migration`: codebase stats, constraints, team |

`parse` uses `format_detector.py` to turn a free-text request into candidates, use case and
priorities. `report_generator.py` renders a combined report from those results; import it with
`PYTHONPATH=scripts` when you need a formatted document.

Flags: `--format text|json`; `compare` also takes `--margin` (default 5 points). Exit codes:
`0` ran (for `compare`: every score has evidence and the winner leads by at least the margin);
`1` `compare` verdict is `UNSUPPORTED` (scores without evidence) or `TOO_CLOSE`; `2` bad input
(missing file, invalid JSON, missing section).

## Workflow

1. Settle candidates, constraints and weights with the user (Clarify First). Weights come from the decision context, not from defaults.
2. Research each score before writing it down: release cadence, open CVEs and patch times, registry downloads, the team's measured experience, a prototype benchmark. Put the source in `evidence`.
3. Run `evaluate.py compare` and the analyses the decision needs (`tco`, `security`, `migration`).
4. Validate before recommending: the compare verdict must be `CLEAR`. On `TOO_CLOSE`, present the trade-offs and the deciding constraint instead of a winner; on `UNSUPPORTED`, return to step 2.
5. Report the recommendation with the evidence table, the assumptions behind any cost figure, and what would change the decision.

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
- Live data fetching from GitHub API, npm registry, or vulnerability databases (all data must be provided in the input file; research it first)
- Performance benchmarking or load testing (use `engineering/senior-qa` for test execution)
- Licensing legal review or contract negotiation (use `ra-qm-team` compliance skills for regulatory guidance)
- Team hiring or organizational design decisions (use `hr-operations/talent-acquisition` for staffing analysis)

## Anti-Patterns

### Scoring From Memory
**Mistake:** Filling the 0-100 category scores from general impressions and presenting the weighted total as an objective result.
**Why it happens:** The tool accepts any number and returns a precise-looking total.
**Instead:** Attach evidence to every score (that is why `compare` exits 1 without it). If a fact cannot be found, say the score is a judgement and lower its weight.

### Declaring a Winner on a Small Gap
**Mistake:** Recommending the top scorer when it leads by two or three points.
**Why it happens:** A ranked list always has a first place.
**Instead:** Treat gaps under the margin as a tie and decide on the constraint the scores do not capture (team skills, existing contracts, migration cost).

### Reusing Reference Cost Figures
**Mistake:** Quoting hosting prices or salaries from the references as current.
**Why it happens:** They sit next to the formulas and look authoritative.
**Instead:** They are illustrative. Price from the provider's calculator and the user's own payroll data, with an as-of date.

## Files

| File | Purpose |
|------|---------|
| `scripts/evaluate.py` | CLI entry point with evidence and margin checks |
| `scripts/stack_comparator.py`, `tco_calculator.py`, `ecosystem_analyzer.py`, `security_assessor.py`, `migration_analyzer.py` | Analysis libraries |
| `scripts/format_detector.py` | Free-text request parser (`evaluate.py parse`) |
| `scripts/report_generator.py` | Report rendering library (import only) |
| `assets/sample_compare_evidenced.json` | Comparison with evidence on every score (exit 0) |
| `assets/sample_input_structured.json` | Comparison without evidence (exit 1, `UNSUPPORTED`) |
| `assets/expected_output_comparison.json` | JSON output of the unsupported comparison |
| `assets/sample_input_tco.json`, `sample_input_ecosystem.json`, `sample_input_security.json`, `sample_input_migration.json` | Inputs for the other subcommands |
| `assets/sample_input_text.json` | Free-text request example for `evaluate.py parse` |
| `references/*.md` | Tool reference, criteria, metrics (illustrative figures), examples, workflows |
