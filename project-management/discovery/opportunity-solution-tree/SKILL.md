---
name: opportunity-solution-tree
description: >
  Opportunity Solution Tree (Teresa Torres) mapping outcomes →
  opportunities → solutions → assumption tests. Use when prioritizing
  discovery work, mapping solutions to a problem, or checking whether
  a roadmap moves outcomes.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-05-27
  python-tools: ost_validator.py
  tech-stack: opportunity-solution-tree, continuous-discovery, teresa-torres
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

Before building the tree, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The one outcome** — a single, measurable, bounded outcome (the tree root; "ship X" or "make users happy" produces an invalid tree)
- [ ] **Customer evidence source** — interviews / tickets / analytics that populate the opportunity layer (opportunities must come from research, not the team's imagination)
- [ ] **Engagement type** — net-new tree vs auditing an existing roadmap (net-new builds top-down; an audit maps current solutions back onto outcomes)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Pick ONE outcome
A good outcome is:
- Behavioral (something users do) or business (revenue, retention)
- Measurable (specific metric, baseline, target)
- Bounded (this quarter / half)
- Within team's influence

Examples:
- "Increase week-1 activation rate from 28% to 40% by end of Q3"
- "Reduce admin-panel time-on-task by 30%"
- "Lift NRR from 105% to 115% by end of year"

NOT outcomes:
- "Build [feature]" (output, not outcome)
- "Improve user experience" (vague)
- "Hit revenue target" (too high; needs to decompose)

### Step 2 — Generate opportunities (from research)
Opportunities come from **customer evidence**, not the team's imagination:
- Interview transcripts
- Support ticket themes
- Sales objection patterns
- Behavioral analytics
- Survey free-text

Opportunities are **customer problems/needs**, not solutions:
- ✓ "Users abandon during email-verification step"
- ✓ "Admins want to bulk-invite from CSV"
- ✗ "Add a CSV import feature" (that's a solution)

### Step 3 — Cluster + dedupe opportunities
Group similar opportunities. Aim for 3-7 distinct opportunity clusters
per outcome.

### Step 4 — Generate multiple solutions per opportunity
For each opportunity, brainstorm 3-5 solutions. Resist jumping to one.

Multiple solutions matter because:
- It surfaces underlying assumption: which solution best solves this?
- Allows comparison of cost/effort
- Reveals the team has bias toward a specific approach

### Step 5 — Identify assumptions + tests
For each candidate solution, list:
- **Value assumption** — will users want this?
- **Usability assumption** — can users use it?
- **Feasibility assumption** — can we build it?
- **Viability assumption** — is it good for the business?

For each top assumption, design a cheap test (interview, prototype, A/B,
landing page, prefab Wizard-of-Oz).

### Step 6 — Run `ost_validator.py`
Audit for: missing outcome, opportunities written as solutions,
single-solution branches, no assumption tests, tree without recent updates.

```bash
python3 project-management/discovery/opportunity-solution-tree/scripts/ost_validator.py \
  --input ost.json --format markdown
```

### Step 7 — Iterate weekly
OST is a living artifact. Each week:
- Add opportunities from new interviews
- Move opportunities up/down based on evidence
- Add solutions
- Track assumption test results
- Kill solutions that failed tests
- Promote validated solutions to roadmap

## Decision frameworks

### Choosing the outcome

Wrong: "Build the new dashboard" (output)
Wrong: "Make customers happy" (vague)
Wrong: "Hit $20M ARR" (too high; many teams)

Right: One number a team can move. Decompose company OKRs to team-level
outcome. See `project-management/execution/north-star-metric`.

### Opportunity vs solution test

If the statement is a thing to build → solution.
If the statement is a customer pain / desire / need → opportunity.

| Statement | Type |
|-----------|------|
| "Add bulk CSV import" | Solution |
| "Admins want to invite many users at once" | Opportunity |
| "Build SAML SSO" | Solution |
| "Enterprise IT requires SSO to approve purchase" | Opportunity |
| "Replace the onboarding video" | Solution |
| "New users can't find the start button" | Opportunity |

### Sizing opportunities

For each opportunity:
- How many customers experience it (% of base)?
- How severe (workaround cost in time/$)?
- How often (frequency per user)?
- Strategic fit with outcome?

Score = impact × frequency × strategic fit. Prioritize accordingly.

### Multiple solutions discipline

Don't allow single-solution branches. If only one solution comes up:
- Ask: "What if we couldn't build that?"
- Borrow from analogous problems
- Get team brainstorm input
- Look at how competitors solve it

Goal: at least 3 candidate solutions per opportunity worth pursuing.

### Assumption test ladder

For each solution, the cheapest test first:
1. Customer interview / desirability test (~$0)
2. Landing page / smoke test (~hours)
3. Wizard-of-Oz / concierge MVP (~days)
4. Low-fidelity prototype (~1 week)
5. High-fidelity prototype (~2 weeks)
6. A/B test in production (~weeks-months)

Spend the minimum to learn the most.

## Common engagements

### "Help me set up an OST for our team this quarter"
1. Confirm the outcome (1 number).
2. Pull existing discovery evidence; cluster into opportunities.
3. Brainstorm 3-5 solutions per top opportunity.
4. Identify top 3 assumption tests for the quarter.
5. Schedule weekly OST update rhythm.

### "Our roadmap is full of features but outcomes aren't moving"
1. Map current roadmap to OST.
2. Identify orphan solutions (no opportunity → no outcome).
3. Identify gaps (opportunities without solutions in roadmap).
4. Reshape roadmap around outcome-supporting solutions.

### "Audit our discovery practice"
1. Look at the OST: when last updated?
2. How many interviews per week feed it?
3. Are opportunities written as needs (not solutions)?
4. How many solutions per opportunity (1 = under-divergent)?
5. How many assumption tests in progress?

## Anti-patterns to avoid

- **Outcome = output.** "Ship X" is not an outcome.
- **Opportunities = solutions.** Strip solutions out of the opportunity layer.
- **Single solution per opportunity.** Force 3+ alternatives.
- **No assumption tests.** Tree without tests = wishful thinking.
- **Static tree.** Update weekly or it dies.
- **Tree built without customer input.** Designed in vacuum; full of bias.
- **One huge outcome.** Decompose to team-level.
- **All opportunities equally important.** Prioritize explicitly.

## References

- `references/ost-fundamentals.md` — Teresa Torres framework deep
- `references/ost-anti-patterns.md` — common failures + fixes

## Related skills

- `project-management/discovery/identify-assumptions` — assumption surfacing
- `project-management/discovery/brainstorm-experiments` — test design
- `project-management/discovery/customer-interview-script` — interview prep
- `project-management/discovery/interview-synthesis` — turn interviews into opportunities
- `project-management/execution/north-star-metric` — outcome definition
- `project-management/strategy-frameworks/lean-canvas` — strategic context
- `product-team/research-summarizer` — interview synthesis
