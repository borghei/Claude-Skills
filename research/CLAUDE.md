# Research Skills - Claude Code Guidance

This domain covers structured research workflows for academic, R&D,
patent, and market intelligence work. Distinct from `product-team/`
user research (which focuses on customer behavior) and `marketing/`
competitive analysis (which focuses on positioning).

## Research Skills Overview (4 skills)

- **litreview/** — academic/professional literature review: search strategy,
  source assessment, synthesis, citation management. Use when conducting
  systematic literature reviews, building bibliographies, or preparing
  research-grounded reports.

- **grants/** — grant writing and proposal architecture: funder fit,
  proposal structure, budget design, success-factor scoring. Use when
  writing a grant proposal, evaluating funder fit, or auditing a draft
  for competitiveness.

- **patent/** — patent research and IP landscape mapping: prior art
  search, claim mapping, landscape visualization, freedom-to-operate
  assessment. Use when conducting prior-art searches, mapping IP
  landscape, or evaluating patentability of an invention.

- **dossier/** — structured intelligence dossier on a company, person,
  market, or domain: source triangulation, fact / inference separation,
  reliability scoring. Use when building a deal-prep dossier, executive
  briefing, market-entry analysis, or due-diligence overview.

**Total Tools:** 12 Python automation tools (stdlib only)

## Common Patterns

All skills in this domain follow the same structure:

```
research/<skill>/
├── SKILL.md
├── references/
│   ├── *.md (frameworks, methodology, anti-patterns)
└── scripts/
    └── *.py (analysis, scoring, generation — stdlib only)
```

## Related Skills

- `product-team/research-summarizer` — synthesizing user research (different domain)
- `legal/` — formal legal IP work (patent skill here is research, not filing)
- `c-level-advisor/general-counsel-advisor` — strategic legal counsel
- `business-growth/competitive-teardown` — competitive analysis (different lens)
- `business-growth/` — commercial intelligence

## Quality Standard

Each skill must:
- Use stdlib-only Python (no external dependencies)
- Support both JSON and human-readable output (`--format` flag)
- Distinguish facts from inferences clearly
- Include source reliability scoring
- Reject inflation, hallucination, and unsubstantiated claims

---

**Last Updated:** May 2026
**Skills Deployed:** 4/4 research skills (Tier 2)
