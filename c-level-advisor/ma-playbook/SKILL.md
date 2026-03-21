---
name: ma-playbook
description: >
  M&A strategy for acquiring companies or being acquired. Covers strategic rationale
  assessment, target screening, due diligence frameworks, valuation methodologies,
  deal structure, negotiation strategy, integration planning, and post-acquisition
  execution. Use when evaluating acquisitions, preparing to be acquired, conducting
  due diligence, planning integration, negotiating deal terms, or when user mentions
  M&A, acquisition, merger, acqui-hire, due diligence, valuation, LOI, earnout,
  integration, or deal structure.
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: c-level
  domain: ma-strategy
  updated: 2026-03-09
  frameworks:
    - acquisition-playbook
    - due-diligence-framework
    - valuation-methods
    - integration-100-day
    - being-acquired-playbook
    - deal-structure
  triggers:
    - M&A
    - merger
    - acquisition
    - acquire
    - acqui-hire
    - due diligence
    - valuation
    - LOI
    - letter of intent
    - term sheet
    - earnout
    - integration
    - deal structure
    - buy a company
    - being acquired
    - selling the company
    - exit strategy
    - data room
  cross-references:
    - c-level-advisor/ceo-advisor
    - c-level-advisor/cfo-advisor
    - c-level-advisor/cto-advisor
    - c-level-advisor/chro-advisor
    - c-level-advisor/coo-advisor
    - c-level-advisor/cpo-advisor
    - c-level-advisor/ciso-advisor
    - c-level-advisor/culture-architect
---

# M&A Playbook

Frameworks for both sides of M&A: acquiring companies and being acquired. Every M&A decision starts with strategic rationale -- without it, you are buying problems.

## Keywords

M&A, mergers and acquisitions, due diligence, acquisition, acqui-hire, integration, deal structure, valuation, LOI, term sheet, earnout, data room, strategic rationale, post-merger integration, buyer, seller, exit

---

## Acquiring: Decision Framework

### Strategic Rationale Decision Tree

```
START: Acquisition opportunity identified
  |
  v
[What are you really buying?]
  |
  +-- TALENT (acqui-hire)
  |     Cost: $1-3M per key engineer
  |     Timeline: 1-3 months
  |     Risk: Key people leave after lockup
  |
  +-- TECHNOLOGY (product/IP)
  |     Cost: Revenue multiple or technology valuation
  |     Timeline: 3-6 months
  |     Risk: Technology doesn't integrate, team leaves
  |
  +-- CUSTOMERS (market share)
  |     Cost: Revenue multiple (higher for sticky customers)
  |     Timeline: 3-6 months
  |     Risk: Customers churn during transition
  |
  +-- MARKET ACCESS (geographic or vertical)
        Cost: Strategic premium
        Timeline: 6-12 months
        Risk: Market assumptions wrong, cultural clash

For ALL types, ask:
  "Can we build this faster and cheaper?" If YES --> Don't acquire.
  "Is integration complexity worth the shortcut?" If NO --> Don't acquire.
```

### Buy vs. Build Analysis

| Factor | Buy | Build |
|--------|-----|-------|
| Time to market | Fast (months) | Slow (years) |
| Cost | Higher upfront, uncertain total | Lower upfront, predictable |
| Risk | Integration risk, culture clash, key person departure | Execution risk, market timing |
| Control | Lower (inheriting systems and culture) | Higher (building from scratch) |
| Team | Get experienced team immediately | Build team to your culture |

**Decision rule**: Buy when time-to-market matters more than cost. Build when control and culture matter more than speed.

---

## Due Diligence Framework

### Due Diligence by Domain

| Domain | Key Questions | Red Flags | Owner |
|--------|--------------|-----------|-------|
| **Financial** | Revenue quality? Customer concentration? Burn rate? Deferred revenue? | > 30% from 1 customer; declining margins; hidden liabilities | CFO |
| **Technical** | Code quality? Tech debt? Architecture fit? Security posture? | Monolith with no tests; no CI/CD; critical security gaps | CTO |
| **Legal** | IP ownership? Pending litigation? Contract assignability? | Key IP owned by individuals; active lawsuits; non-assignable contracts | Legal counsel |
| **People** | Key person risk? Culture fit? Retention likelihood? | Founders with no lockup; team wants to leave; culture mismatch | CHRO |
| **Market** | Market position? Competitive threats? Customer satisfaction? | Declining market share; commoditizing market; low NPS | CEO/CPO |
| **Customers** | Churn rate? NPS? Contract terms? Expansion potential? | High churn; short contracts; declining usage | CRO/CPO |
| **Product** | PMF evidence? Roadmap alignment? Technical overlap? | No retention data; divergent roadmap; redundant technology | CPO |
| **Security** | Compliance status? Incident history? Data practices? | No SOC 2; history of breaches; poor data handling | CISO |

### Due Diligence Priority Matrix

| Priority | Items | Timeline |
|----------|-------|----------|
| 1 (Deal-breaker) | Financial accuracy, IP ownership, litigation, key person risk | Week 1-2 |
| 2 (Valuation impact) | Revenue quality, churn, tech debt, customer concentration | Week 2-4 |
| 3 (Integration planning) | Culture assessment, technical architecture, process overlap | Week 3-6 |
| 4 (Post-close optimization) | Operational efficiency, vendor contracts, tool consolidation | Week 4-8 |

### Financial Due Diligence Deep Dive

| Metric | What to Verify | Red Flag |
|--------|---------------|----------|
| Revenue recognition | Is revenue recognized properly? Deferred revenue accurate? | Aggressive recognition inflating ARR |
| Customer quality | Weighted average contract length and renewal rate | Short contracts, declining renewals |
| Cohort retention | Do older cohorts retain better or worse? | Worsening retention in newer cohorts |
| Burn rate | All-in cost including one-time items | Hidden costs, one-time items excluded |
| Cash position | Verified bank statements | Discrepancy between reported and actual |
| Liability inventory | All known and contingent liabilities | Undisclosed or underestimated liabilities |

---

## Valuation Methods

### Method Selection

| Method | When to Use | Pros | Cons |
|--------|------------|------|------|
| Revenue multiple | SaaS with growth | Simple, comparable | Ignores profitability |
| ARR multiple | Subscription businesses | Recurring revenue focus | Varies by growth rate |
| DCF | Profitable businesses | Theoretically sound | Highly sensitive to assumptions |
| Comparable transactions | Active M&A market | Market-validated | Finding true comparables is hard |
| Acqui-hire | Talent acquisition | Simple calculation | Ignores IP and customer value |
| Replacement cost | Technology acquisition | Practical baseline | Ignores market position |

### SaaS Revenue Multiple Ranges

| Growth Rate | NRR > 110% | NRR 100-110% | NRR < 100% |
|------------|-----------|-------------|-----------|
| > 100% YoY | 15-25x ARR | 10-18x ARR | 8-12x ARR |
| 50-100% YoY | 8-15x ARR | 6-10x ARR | 4-7x ARR |
| 25-50% YoY | 5-10x ARR | 4-7x ARR | 3-5x ARR |
| < 25% YoY | 3-6x ARR | 2-4x ARR | 1-3x ARR |

**Note**: Multiples vary significantly by market, vertical, and broader market conditions. These are indicative ranges.

### Valuation Adjustment Factors

| Factor | Premium (+) | Discount (-) |
|--------|-----------|-------------|
| Strategic fit | + 10-30% for high synergy | - 10-20% for low synergy |
| Competitive process | + 10-20% for multiple bidders | Baseline for single bidder |
| Key person dependency | -- | - 15-25% if founders critical and reluctant |
| Technical debt | -- | - 10-30% based on remediation cost |
| Customer concentration | -- | - 10-20% if > 25% from one customer |
| IP strength | + 10-20% for strong patents/moat | -- |

---

## Deal Structure

### Key Terms to Negotiate

| Term | Buyer Wants | Seller Wants | Typical Compromise |
|------|-----------|-------------|-------------------|
| Purchase price | Lower, more earnout | Higher, more cash | 60-80% cash, 20-40% earnout |
| Earnout | Long period, hard targets | Short period, easy targets | 12-24 months, achievable with effort |
| Lockup period | Long (24-36 months) | Short (6-12 months) | 18-24 months with milestones |
| Escrow/holdback | Large (15-20%) | Small (5-10%) | 10-15% for 12-18 months |
| Representations | Broad, long survival | Narrow, short survival | 12-18 month survival, materiality thresholds |
| Non-compete | Long (3-5 years), broad | Short (1-2 years), narrow | 2-3 years, reasonable scope |
| Employee treatment | Discretion on offers | Guarantees for team | Offers for key people, best efforts for team |

### Earnout Design Principles

| Principle | Why |
|-----------|-----|
| Metrics must be measurable and auditable | Disputes destroy the relationship |
| Seller must have meaningful control | Unachievable earnouts are disguised price cuts |
| Milestones should be achievable with effort | Too easy = buyer overpaid. Too hard = seller disengages. |
| Payment schedule aligned with milestones | Quarterly or semi-annual, not all at end |
| Dispute resolution mechanism defined upfront | How disagreements are resolved must be in the agreement |

---

## Integration: 100-Day Plan

### Integration Decision: Absorb, Preserve, or Hybrid

| Mode | Description | When | Risk |
|------|------------|------|------|
| Absorb | Fully integrate into acquirer | Product overlap, same ICP | Loss of acquired team culture |
| Preserve | Operate independently | Different market/product, brand value | Missed synergies |
| Hybrid | Shared backend, independent frontend | Complementary products | Complexity in execution |

### 100-Day Integration Timeline

| Phase | Days | Focus | Key Activities |
|-------|------|-------|---------------|
| 1: Stabilize | 0-30 | Retain people, retain customers | Welcome communications, 1:1 with key people, customer outreach |
| 2: Integrate | 30-60 | Systems and process alignment | IT integration, tool consolidation, process mapping |
| 3: Optimize | 60-90 | Synergy realization | Cross-sell, combined roadmap, team optimization |
| 4: Accelerate | 90-100 | Scale combined capabilities | Joint GTM, combined product features, growth investment |

### Day 1 Checklist (Non-Negotiable)

| Item | Owner | Purpose |
|------|-------|---------|
| CEO welcome communication to acquired team | CEO | Set tone, reduce anxiety |
| Customer communication (if public) | CMO + CRO | Retain customer confidence |
| Key person 1:1 meetings scheduled | CHRO + CEO | Retention of critical talent |
| Systems access granted | CTO | Operational continuity |
| Reporting structure clarified | COO | Remove ambiguity immediately |
| Compensation/benefits confirmed | CHRO | Address primary employee concern |

### Integration Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| "We'll figure out integration later" | Creates chaos and attrition | Plan integration before close |
| Imposing acquirer culture immediately | Alienates acquired team | Gradual cultural integration |
| Ignoring acquired team's input | Best people leave feeling unvalued | Include them in integration decisions |
| Rushing product integration | Quality drops, customers impacted | Phase integration with clear milestones |
| No integration owner | Nobody accountable = nothing happens | Named integration lead from day 1 |

---

## Being Acquired: Preparation

### Readiness Assessment

| Signal | Readiness Level |
|--------|----------------|
| Inbound interest from strategic buyers | High -- leverage the interest |
| Market consolidation happening | Medium -- prepare while you have options |
| Fundraising harder than operating | Medium -- acquisition may be better path |
| Founder ready for transition | Personal -- ensure this is genuine |
| Growth stalling despite effort | Consider -- but don't sell from weakness |

### Preparation Timeline (6-12 Months Before)

| Month | Activity | Owner |
|-------|----------|-------|
| 1-2 | Clean financials, resolve outstanding legal issues | CFO + Legal |
| 2-3 | Document all IP, ensure ownership is clean | CTO + Legal |
| 3-4 | Reduce customer concentration below 20% | CRO |
| 4-5 | Retention agreements for key employees | CHRO |
| 5-6 | Build data room with all required documents | CFO |
| 6-8 | Engage M&A advisor, begin outreach | CEO |
| 8-12 | Process management, negotiate, close | CEO + Advisor |

### Data Room Contents

| Category | Required Documents |
|----------|-------------------|
| Corporate | Certificate of incorporation, bylaws, cap table, board minutes |
| Financial | 3 years of financials, tax returns, projections, bank statements |
| Revenue | Customer list, contracts, MRR/ARR breakdown, cohort data |
| Legal | All contracts, IP assignments, employee agreements, litigation |
| People | Org chart, comp data, key person profiles, benefits summary |
| Product | Architecture overview, tech stack, roadmap, key metrics |
| IP | Patents, trademarks, proprietary technology documentation |
| Compliance | Certifications, audit reports, data handling documentation |

---

## Red Flags (Both Sides)

### Acquiring Red Flags

- No clear strategic rationale beyond "it's a good deal"
- Due diligence reveals culture mismatch and it is dismissed
- Key people not committed before close
- Integration plan does not exist or is "we'll figure it out"
- Valuation based on projections, not actuals
- Revenue concentration > 30% in one customer
- Founder has no lockup or earnout incentive

### Being Acquired Red Flags

- Only one buyer interested (no competitive dynamic)
- Earnout targets seem unreachable after integration
- Buyer has history of post-acquisition layoffs
- No written commitment for team retention
- Valuation feels low but "speed" is used as pressure
- Buyer rushing timeline without clear reason

---

## Integration with C-Suite

| Role | Contribution to M&A |
|------|-------------------|
| CEO (`ceo-advisor`) | Strategic rationale, negotiation lead, integration vision |
| CFO (`cfo-advisor`) | Valuation, deal structure, financing, financial DD |
| CTO (`cto-advisor`) | Technical due diligence, architecture assessment, integration plan |
| CHRO (`chro-advisor`) | People DD, retention planning, culture assessment |
| COO (`coo-advisor`) | Integration execution, process merge, operational DD |
| CPO (`cpo-advisor`) | Product roadmap impact, customer overlap analysis |
| CISO (`ciso-advisor`) | Security posture assessment, compliance DD |
| Culture Architect (`culture-architect`) | Culture clash detection, integration culture plan |

---

## Output Artifacts

| Request | Deliverable |
|---------|-------------|
| "Should we acquire [company]?" | Strategic rationale assessment with buy vs. build analysis |
| "Run due diligence on [target]" | Due diligence checklist by domain with priority matrix |
| "Value this acquisition" | Valuation analysis using multiple methods |
| "Structure this deal" | Deal term recommendations with negotiation strategy |
| "Plan the integration" | 100-day integration plan with owners and milestones |
| "Prepare to be acquired" | Readiness assessment + 6-month preparation plan |
| "Build the data room" | Complete data room checklist with document list |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Due diligence keeps surfacing new issues after expected completion | DD scope not defined upfront; no priority matrix followed | Use the Priority Matrix strictly: deal-breakers in Week 1-2, valuation impact in Week 2-4; new findings after Week 4 go to post-close optimization |
| Key employees leaving within 6 months of acquisition | Retention agreements insufficient or culture integration failed | Structure retention bonuses with 24-month cliff; conduct Day 1 welcome meetings; include acquired team in integration decisions |
| Synergy targets missed at 100-day mark | Synergies were aspirational projections, not auditable targets | Require each synergy to have a specific metric, owner, and measurement method before deal close; track quarterly |
| Integration stalls with no clear ownership | No Integration Management Office (IMO) or named integration lead | Appoint dedicated integration lead from Day 0; establish IMO with cross-functional representatives and weekly cadence |
| Earnout disputes destroying the relationship | Metrics not clearly defined or seller lacks control over outcomes | Define earnout metrics that are measurable, auditable, and within seller's meaningful control; include dispute resolution mechanism |
| Valuation gap between buyer and seller too large to bridge | Different methodologies or growth assumptions | Use multiple valuation methods and present range; bridge with earnout structure tied to the gap assumptions |
| Post-acquisition customer churn spike | Customer communication delayed or inadequate; service disruption during integration | Execute customer communication on Day 1; maintain service continuity as Phase 1 priority; assign dedicated CS contact |

---

## Success Criteria

- Strategic rationale articulated in one paragraph before any DD begins; "buy vs. build" analysis completed with clear justification
- Due diligence completed within 8-week timeline with all Priority 1 items cleared by Week 2
- Integration plan documented before deal close, not after, with named owners for every workstream
- Day 1 checklist 100% executed: CEO welcome, customer communication, key person meetings, systems access, reporting structure
- 100-day integration milestones met: 90%+ key person retention, zero customer churn attributable to integration, systems integrated per plan
- Synergy targets tracked quarterly with variance < 15% from projections
- Data room (if selling) complete and organized 30 days before process begins

---

## Scope & Limitations

- **In scope:** Strategic rationale assessment, buy vs. build analysis, due diligence frameworks (financial, technical, legal, people, market, product, security), valuation methodologies, deal structure negotiation, integration planning and execution, preparation for being acquired, data room construction
- **Out of scope:** Legal document drafting (use M&A legal counsel); tax structure optimization (use tax advisors); regulatory antitrust filings (use specialized counsel); investment banking services (engage M&A advisor for process management)
- **Limitation:** Valuation multiples are market-dependent and change with conditions; ranges provided are indicative benchmarks, not appraisals
- **Limitation:** Framework optimized for technology company M&A (SaaS, software); manufacturing, retail, and regulated industry M&A have additional complexities
- **Limitation:** Integration success depends heavily on cultural compatibility, which is difficult to assess fully during DD

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `ceo-advisor` | M&A is a CEO strategic decision requiring board alignment | CEO strategy → M&A strategic rationale |
| `cfo-advisor` | Valuation, deal structure, financial DD, and financing | M&A financials → CFO valuation model |
| `cto-advisor` | Technical DD, architecture assessment, integration plan | M&A tech assessment → CTO integration roadmap |
| `chro-advisor` | People DD, retention planning, culture assessment | M&A people risks → CHRO retention strategy |
| `coo-advisor` | Integration execution, process merge, operational DD | M&A integration plan → COO execution |
| `culture-architect` | Culture clash detection and integration culture plan | M&A culture assessment → Culture integration strategy |
| `ciso-advisor` | Security posture assessment and compliance DD | M&A security audit → CISO remediation plan |

---

## Python Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `scripts/due_diligence_tracker.py` | Track due diligence items across 8 domains with priority, status, and red flag detection | `python scripts/due_diligence_tracker.py add --domain financial --item "Revenue recognition audit" --priority 1 --json` |
| `scripts/synergy_calculator.py` | Calculate and track revenue and cost synergies with confidence-weighted projections | `python scripts/synergy_calculator.py --revenue-synergies 500000 --cost-synergies 200000 --confidence 0.7 --timeline-months 24 --json` |
| `scripts/integration_planner.py` | Generate a 100-day integration plan with phases, milestones, owners, and status tracking | `python scripts/integration_planner.py --mode absorb --target-name "AcquiredCo" --headcount 25 --json` |
