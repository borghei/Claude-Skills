---
name: porters-five-forces
description: >
  Porter's Five Forces — analyze the competitive intensity and
  attractiveness of an industry. Use when evaluating a new market entry,
  diagnosing margin pressure, designing a defensive strategy, or auditing
  industry-level positioning.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: strategy-frameworks
  updated: 2026-05-27
  python-tools: five_forces_scorer.py
  tech-stack: porters-five-forces, industry-analysis, competitive-strategy
---

# Porter's Five Forces

Michael Porter's framework for analyzing the structural attractiveness
of an industry. Reveals where profit pools form, why some markets are
chronically unprofitable, and where strategic positioning has leverage.

## When to use this skill

- **Market entry** decision (which industry to play in)
- Diagnosing **chronic margin pressure** (why are we squeezed?)
- **Strategic positioning** (where to invest, where to defend)
- **Competitive response** planning
- **M&A target evaluation** (industry attractiveness)
- **Pre-fundraise** industry framing

## The 5 forces

1. **Threat of new entrants** — how easily can newcomers join?
2. **Bargaining power of suppliers** — how concentrated/critical are inputs?
3. **Bargaining power of buyers** — how concentrated/price-sensitive are customers?
4. **Threat of substitute products** — what alternatives could replace the category?
5. **Competitive rivalry** — how intense is competition between existing players?

Plus (Porter's later addition):
6. **Complementors** (the "sixth force") — do partners increase total industry value?

## Scoring rubric

Each force is rated **low / medium / high** based on specific factors:

### 1. Threat of new entrants — high when:
- Low capital requirements
- No regulatory barriers
- No proprietary tech / patents
- Low switching costs
- No economies of scale
- No brand loyalty
- Access to distribution is easy
- Network effects absent

### 2. Supplier power — high when:
- Few suppliers / concentrated supply base
- Suppliers are critical / cannot be substituted
- Switching cost is high
- Suppliers can forward-integrate
- Industry is not a large customer for supplier

### 3. Buyer power — high when:
- Few buyers / concentrated demand
- Buyers purchase in large volumes
- Product is undifferentiated
- Switching cost is low
- Buyers can backward-integrate
- Buyers have full information
- Buyers face thin margins (price pressure)

### 4. Threat of substitutes — high when:
- Many substitutes exist
- Substitutes have favorable price-performance
- Switching cost to substitute is low
- Buyer propensity to substitute is high
- Substitute industry is growing fast

### 5. Competitive rivalry — high when:
- Many similar-sized competitors
- Low growth industry (zero-sum)
- High fixed costs (drive volume)
- Low differentiation
- High exit barriers
- Strategic stakes high

## Clarify First

Before scoring the forces, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Precise industry definition** — narrow enough to be specific, broad enough to catch substitutes (too broad/narrow is the #1 error and sets the entire analysis scope)
- [ ] **Evidence per force** — the data/facts behind each low/medium/high rating (a score without evidence is just opinion)
- [ ] **Purpose** — market entry / margin-pressure diagnosis / positioning audit (frames which dominant force matters and the strategy translation; margin diagnosis also needs a then-vs-now comparison)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Define the industry
Industry definition is the most-frequent source of error.
- "Software" is too broad
- "B2B SaaS" is too broad
- "Mid-market HR analytics SaaS" is workable
- "Enterprise revenue intelligence tools (Gong, Outreach, Salesloft-tier)" is precise

### Step 2 — Score each force
Use the rubric. Each force gets low / medium / high + evidence.

### Step 3 — Identify the dominant force(s)
Usually 1-2 forces dominate. They drive the industry's profit pool.

### Step 4 — Translate to strategy
Each force suggests strategic moves:

| Force | High = unfavorable | Strategy implications |
|-------|---------------------|------------------------|
| New entrants | Easy entry | Build barriers (brand, scale, network, switching cost) |
| Supplier power | Concentrated | Diversify, integrate backward, build alternative supply |
| Buyer power | Concentrated | Diversify customer base, differentiate, integrate forward |
| Substitutes | Strong substitutes | Differentiate, raise switching cost, defend value prop |
| Rivalry | Intense | Differentiate, niche down, exit, consolidate |

### Step 5 — Run `five_forces_scorer.py`
Audit for: missing evidence, generic factors, missed sub-factors, no
strategy implications drawn.

```bash
python3 project-management/strategy-frameworks/porters-five-forces/scripts/five_forces_scorer.py \
  --input forces.json --format markdown
```

## Common engagements

### "Should we enter market X?"
1. Define X precisely.
2. Score each force.
3. Identify dominant force.
4. Assess: can we differentiate against the dominant force?
5. If yes, structure entry to counter that force; if no, don't enter.

### "Why are our margins under pressure?"
1. Score industry today vs 3-5 years ago.
2. Identify the force(s) that shifted (usually buyer power or rivalry).
3. Identify which factor specifically caused the shift.
4. Address: product differentiation, switching cost, customer concentration, etc.

### "Audit our strategic position"
1. Score industry forces.
2. For each high force, identify how we currently counter it.
3. Identify weak counters; recommend reinforcement.

## Anti-patterns to avoid

- **Industry defined too broadly.** Yields generic analysis.
- **Industry defined too narrowly.** Misses substitute threats.
- **Each force = "medium".** No analysis happened.
- **No evidence cited.** Just opinion.
- **No strategy implications.** Just a score; not actionable.
- **Static analysis.** Industries evolve; refresh every 12-18 months.
- **Mixing internal capabilities with industry analysis.** Five Forces is industry-level; capabilities are firm-level (see SWOT).

## References

- `references/five-forces-deep.md` — each force, factors, examples
- `references/five-forces-and-strategy.md` — translating to strategic moves

## Related skills

- `project-management/strategy-frameworks/swot-analysis` — firm-level positioning
- `project-management/strategy-frameworks/ansoff-matrix` — growth options
- `project-management/strategy-frameworks/business-model-canvas` — operational view
- `marketing/competitive-teardown` — competitor-specific analysis
- `c-level-advisor/ceo-advisor` — strategic context
