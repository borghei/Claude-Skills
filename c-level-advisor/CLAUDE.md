# C-Level Advisory Skills - Claude Code Guidance

This guide covers the 31 production-ready C-level advisory skills for strategic decision-making.

## C-Level Skills Overview

**Core executive advisors (26):**
- **ceo-advisor/** — strategic planning, business operations, organizational design
- **cto-advisor/** — technical leadership, architecture, engineering strategy
- **cfo-advisor/** — financial planning, fundraising, investor reporting
- **cmo-advisor/** — marketing strategy, brand, demand
- **cpo-advisor/** — product strategy, roadmap, prioritization
- **cro-advisor/** — revenue, sales, GTM
- **coo-advisor/** — operations, scaling, process
- **chro-advisor/** — talent, culture, comp
- **ciso-advisor/** — security strategy, risk, compliance
- Plus: board-deck-builder, board-meeting, change-management, chief-of-staff,
  company-os, competitive-intel, cs-onboard, culture-architect, decision-logger,
  executive-mentor, founder-coach, internal-narrative, intl-expansion,
  ma-playbook, org-health-diagnostic, scenario-war-room, strategic-alignment

**Tier 2 additions (May 2026, 5 new C-suite advisors):**
- **chief-ai-officer-advisor/** — AI strategy, governance, risk, investment, AI org design (3 tools)
- **chief-data-officer-advisor/** — data strategy, governance, quality, platform evaluation (3 tools)
- **chief-customer-officer-advisor/** — CX strategy, churn intervention, VoC program design (3 tools)
- **general-counsel-advisor/** — legal strategy, risk register, contract portfolio, regulatory calendar (3 tools)
- **vpe-advisor/** — engineering org health, productivity dashboard, capacity planning (3 tools)

**Focus:** Strategic decision-making, cross-functional alignment, long-term planning

## CEO Advisor

**Skill Location:** `ceo-advisor/`

### Strategic Planning Tools

**Purpose:** Support CEOs in strategic planning, business operations, and organizational design

**Key Areas:**
- Strategic planning frameworks (SWOT, Porter's Five Forces, Blue Ocean)
- Business model canvas and validation
- Organizational structure design
- Change management strategies
- Board reporting and investor relations

**Python Tools:**
- Strategic analysis frameworks
- Business metrics calculator
- Organizational design templates

**Usage:**
```bash
python ceo-advisor/scripts/strategy_analyzer.py
```

### Decision-Making Frameworks

**When to Use:**
- Annual strategic planning
- Major business pivots
- M&A evaluation
- Market expansion decisions
- Organizational restructuring

## CTO Advisor

**Skill Location:** `cto-advisor/`

### Technical Leadership Tools

**Purpose:** Support CTOs in technical leadership, architecture decisions, and engineering strategy

**Key Areas:**
- Technology stack selection and evaluation
- Engineering team scaling strategies
- Technical debt management
- Architecture decision records (ADRs)
- Build vs buy analysis
- Engineering culture and practices

**Python Tools:**
- Technology evaluation framework
- Team capacity planning
- Technical debt calculator

**Usage:**
```bash
python cto-advisor/scripts/tech_debt_analyzer.py
```

### Technical Decision Frameworks

**When to Use:**
- Technology stack decisions
- Architecture pattern selection
- Engineering team organization
- Technical hiring strategies
- Infrastructure planning

## Strategic Workflows

### Workflow 1: Annual Strategic Planning (CEO)

```bash
# 1. Market analysis
python competitive-intel/scripts/market_landscape_mapper.py --input market-data.json

# 2. SWOT analysis
python competitive-intel/scripts/swot_analyzer.py --input swot-data.json

# 3. Strategy formulation
python ceo-advisor/scripts/strategy_analyzer.py

# 4. OKR cascade (link to product-strategist)
python ../product-team/product-strategist/scripts/okr_cascade_generator.py growth
```

### Workflow 2: Technical Strategy (CTO)

```bash
# 1. Evaluate technology options against weighted criteria (performance, scalability, ecosystem, TCO)

# 2. Architecture decision: record it as an ADR (format: cto-advisor/references/architecture_decision_records.md)

# 3. Team capacity planning
python vpe-advisor/scripts/eng_capacity_planner.py --input team-data.json

# 4. Engineering roadmap: sequence priorities against the capacity projection from step 3
```

## Integration with Other Skills

### CEO ↔ Product Team
- Strategic OKRs cascade to product OKRs
- Market insights inform product strategy
- Business metrics align with product metrics

### CTO ↔ Engineering Team
- Architecture decisions guide engineering work
- Technical strategy informs team structure
- Engineering metrics roll up to CTO dashboard

### CEO ↔ CTO Alignment
- Strategic business goals inform technical priorities
- Technical capabilities enable business strategies
- Joint decision-making on build vs buy

## Additional Resources

- **CEO Advisor Skill:** `ceo-advisor/SKILL.md`
- **CTO Advisor Skill:** `cto-advisor/SKILL.md`
- **Main Documentation:** `../CLAUDE.md`

---

**Last Updated:** November 5, 2025
**Skills Deployed:** 2/2 C-level skills production-ready
**Focus:** Strategic decision-making and executive leadership
