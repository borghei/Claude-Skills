---
name: opportunity-solution-tree
description: >
  Maps one outcome to customer opportunities, 3+ solutions each and assumption tests,
  then audits the tree. Use when prioritizing discovery work, mapping solutions to a
  problem, or checking whether a roadmap moves outcomes.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-11-08
  python-tools: ost_validator.py
  tech-stack: opportunity-solution-tree, continuous-discovery, teresa-torres
  tags:
    - opportunity-solution-tree
    - continuous-discovery
    - teresa-torres
    - assumption-testing
---

# Opportunity Solution Tree (OST)

Teresa Torres' framework from *Continuous Discovery Habits*. An OST
visualizes the path from a desired outcome to the assumption tests that
will validate or invalidate candidate solutions.

## When to use this skill

- Prioritizing **discovery work** for a quarter
- Structuring **weekly customer touchpoints**
- Mapping **multiple solutions** to one problem (vs jumping to solution)
- Auditing whether **roadmap actually moves outcomes**
- **Coaching** a team into continuous discovery rhythm
- **Pivoting** discovery away from a dead-end branch

## The tree structure

```
                  [Outcome]
                      |
        +-------------+-------------+
        |             |             |
   Opportunity   Opportunity   Opportunity
        |             |             |
     +--+--+      +--+--+      +--+--+
     |     |      |     |      |     |
   Solution Solution ...
        |
   +----+----+
   |         |
 Assumption  Assumption
   Test        Test
```

### Levels
1. **Outcome** — a single, specific, measurable business / product outcome
2. **Opportunities** — customer needs/pains/desires that, if addressed, drive the outcome
3. **Solutions** — candidate ways to address each opportunity
4. **Assumption tests** — experiments validating that the solution will deliver

## Clarify First

Before building the tree, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The one outcome:** a single, measurable, bounded outcome (the tree root; "ship X" or "make users happy" produces an invalid tree).
- **Customer evidence source:** interviews / tickets / analytics that populate the opportunity layer (opportunities must come from research, not the team's imagination).
- **Engagement type:** net-new tree vs auditing an existing roadmap (net-new builds top-down; an audit maps current solutions back onto outcomes).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

Layer definitions, good and bad examples, the weekly rhythm and stuck-tree symptoms are in
`references/ost-fundamentals.md`; this section is the procedure.

1. **One outcome.** Measurable, behavioral or business, bounded to a quarter or half, and within the team's influence ("Lift week-1 activation from 28% to 40% by end of Q3"). "Ship X" is an output; "hit $20M ARR" is too high for one team.
2. **Opportunities from evidence.** Pull them from interviews, tickets, sales objections, analytics and survey text, phrased as the customer's need ("Admins want to invite their whole team at once"), never as a build ("Add CSV import"). Cluster to 3-7 per outcome.
3. **Three or more solutions per opportunity.** A single solution means the team is defending a favourite; ask "what if we couldn't build that?" and look at analogous problems.
4. **Assumption tests.** For each solution, name the riskiest of value, usability, feasibility and viability, and the cheapest test with a time box and a pass criterion. Climb the ladder only as needed: interview, landing page or smoke test, Wizard-of-Oz or concierge, low-fi prototype, high-fi prototype, production A/B. AI-built prototypes make the prototype rungs cheap, not the earlier rungs unnecessary.
5. **Audit the tree** with `ost_validator.py` (below), and fix every fail.
6. **Iterate weekly.** Add opportunities from new interviews, record test results, kill failed solutions, promote validated ones to the roadmap.

To audit an existing roadmap, map each roadmap item to an opportunity and the outcome; items with no opportunity are orphans, and opportunities with no item are gaps.

## Tool

`ost_validator.py` reads a JSON tree (schema in its `--help`; JSON is the default output, `--format markdown` for a table, `--output` to write a file).

```bash
python3 project-management/discovery/opportunity-solution-tree/scripts/ost_validator.py \
  --input project-management/discovery/opportunity-solution-tree/assets/sample_ost.json --format markdown         # exit 0
python3 project-management/discovery/opportunity-solution-tree/scripts/ost_validator.py \
  --input project-management/discovery/opportunity-solution-tree/assets/sample_ost_flawed.json --format markdown  # exit 1
```

It fails a tree with no outcome or opportunities, an outcome not marked measurable or behavioral, or no update in 30+ days (measured from `as_of`, so a fixed file gives a fixed answer). It warns on output language in the outcome, opportunities that start with a build verb (add, build, create, implement and similar, checked against the text whatever the `is_customer_phrased` flag says), missing evidence, fewer than 3 solutions, solutions without tests or pass criteria, and no update in 14+ days. Exit codes: 0 no fail, 1 at least one fail, 2 bad input.

## Anti-Patterns

### Outcome that is an output
**Mistake:** The root reads "Ship the new onboarding".
**Why it happens:** Roadmaps are written in features, and the tree gets copied from the roadmap.
**Instead:** Name the behavior or business number that the onboarding should move, with a baseline and a target. The validator fails an outcome not marked measurable and behavioral.

### Solutions in the opportunity layer
**Mistake:** Opportunities read "Add bulk CSV import", "Build SSO".
**Why it happens:** Teams think in solutions, and a solution feels more concrete than a need.
**Instead:** Ask "why would a customer want that?" and write the answer as the opportunity; the import becomes one of three solutions under it.

### The static tree
**Mistake:** The tree was built in a planning offsite and not touched since.
**Why it happens:** Building it felt like the deliverable.
**Instead:** Update it weekly from new interviews and test results; a tree older than 30 days fails the audit.

More failures and fixes: `references/ost-anti-patterns.md`.

## Scope & Limitations

**In Scope:**
- Building an Opportunity Solution Tree (Teresa Torres) from one outcome through opportunities and solutions to assumption tests
- The opportunity-versus-solution test, opportunity sizing and the rule of 3+ solutions per opportunity
- Value, usability, feasibility and viability assumptions per solution, with an assumption test ladder from interview to production A/B test
- A tree audit for outcome quality, opportunities written as solutions, single-solution branches, missing tests and stale trees (`ost_validator.py`)
- Mapping an existing roadmap onto the tree to find orphan solutions and gaps

**Out of Scope:**
- Running interviews or synthesizing them into opportunities (see `project-management/discovery/customer-interview-script/` and `project-management/discovery/interview-synthesis/`)
- Designing the experiments in detail (see `project-management/discovery/brainstorm-experiments/`)
- Defining the company-level North Star (see `project-management/execution/north-star-metric/`)
- Building prototypes for assumption tests (see `project-management/discovery/ai-prototyping/`)

**Important Caveats:**
- `ost_validator.py` reads a hand-built JSON tree. Flags such as `is_customer_phrased` and `has_evidence` are self-reported, so the tool checks structure, not the quality of the evidence.
- Opportunity scoring (impact, frequency, strategic fit) is an estimate the team makes. The tool does not compute it from data.
- The tree goes stale without weekly updates. The validator warns when `last_updated` is more than 14 days before `as_of` and fails it past 30.

## References

- `references/ost-fundamentals.md` — layers, outcome/opportunity/solution examples, assumption tests, weekly rhythm, stuck trees
- `references/ost-anti-patterns.md` — common failures + fixes

## Related skills

- `project-management/discovery/identify-assumptions` — assumption surfacing
- `project-management/discovery/brainstorm-experiments` — test design
- `project-management/discovery/customer-interview-script` — interview prep
- `project-management/discovery/interview-synthesis` — turn interviews into opportunities
- `project-management/execution/north-star-metric` — outcome definition
- `project-management/strategy-frameworks/lean-canvas` — strategic context
- `product-team/research-summarizer` — interview synthesis

## Files

| File | Purpose |
|------|---------|
| `scripts/ost_validator.py` | Audits a JSON tree for outcome quality, opportunity phrasing, solution diversity, test coverage and freshness |
| `assets/sample_ost.json`, `assets/sample_ost_flawed.json` | Runnable trees: sound (exit 0) and flawed (exit 1) |
| `assets/ost_template.md` | Tree worksheet to fill in |
| `references/ost-fundamentals.md`, `references/ost-anti-patterns.md` | Framework detail; failures and fixes |
