# Research Ops Skills - Claude Code Guidance

This domain covers **applied, operational** research — running research as a
funded, staffed, repeatable function. It is deliberately distinct from the
academic `research/` domain (litreview, grants, patent, dossier), which covers
scholarly synthesis and intelligence work.

Rule of thumb: `research/` answers *what is known*; `research-ops/` answers
*how we run studies to find out, and what they cost*.

## Research Ops Skills Overview (4 skills)

- **market-research/** — market sizing and structure: TAM/SAM/SOM built both
  top-down and bottom-up then reconciled, segmentation, demand-signal
  triangulation, and survey instrument design. Use when sizing a market,
  validating demand, or auditing a survey before it ships.

- **product-research/** — continuous product discovery operations: choosing the
  right method for the question, screener and recruiting design, interview guide
  construction, and evidence-to-insight synthesis with confidence scoring. Use
  when planning a study, screening participants, or judging how much weight an
  insight can carry.

- **clinical-research/** — clinical study operations: protocol structure,
  endpoint selection, inclusion/exclusion design, sample-size and power planning,
  site feasibility, and regulatory documentation readiness. Use when planning a
  study, sizing a trial, or auditing a protocol outline.

- **research-finance/** — research budgeting and funding: study and programme
  budget construction, cost-per-participant and cost-per-insight modelling, burn
  tracking against milestones, and portfolio prioritisation of research spend.
  Use when budgeting a study, forecasting overrun, or ranking a research
  portfolio.

**Total Tools:** 12 Python automation tools (stdlib only)

## Scope Boundary — clinical-research

`clinical-research/` supports **study operations planning**. It does not replace
a qualified biostatistician, medical monitor, or regulatory affairs sign-off, and
its SKILL.md says so explicitly. The sample-size calculator uses documented
normal-approximation formulas and reports its method in every result; it is a
planning aid, not a submission artefact.

For regulatory submission and quality-system work, use `ra-qm-team/`.

## Common Patterns

```
research-ops/<skill>/
├── SKILL.md
├── references/
│   └── *.md (methodology, thresholds, design guidance)
├── scripts/
│   └── *.py (sizing, scoring, budgeting — stdlib only)
└── assets/
    └── *.md templates + sample_*.json inputs
```

Statistical scripts state their method in the output (`method_note`) and warn on
inputs that invite misuse (zero dropout, SD from a small pilot, thin cells).

## Related Skills

- `research/` — academic literature review, grants, patent, intelligence dossiers
- `product-team/research-summarizer` — synthesising user research findings
- `product-team/product-analytics` — behavioural/quantitative product data
- `data-analytics/statistical-analyst` — general applied statistics and test choice
- `ra-qm-team/` — regulatory submission and quality systems
- `marketing/competitive-teardown` — competitive positioning (different lens)

## Quality Standard

Each skill must:
- Use stdlib-only Python (no external dependencies)
- Support both JSON and human-readable output (`--format` flag)
- State the statistical or methodological assumption behind every number
- Warn on inputs that produce misleading results rather than silently computing
- Separate what the evidence supports from what it merely suggests

---

**Last Updated:** July 2026
**Skills Deployed:** 4/4 research ops skills
