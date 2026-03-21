---
name: scenario-war-room
description: Cross-functional what-if modeling for compound adversity scenarios. Models cascading multi-variable risks across all business functions simultaneously. Unlike single-assumption stress tests, this shows how one problem creates the next. Use when facing complex risk scenarios, strategic decisions with major downside, multi-variable threats, or when someone asks "what if X AND Y both happen?"
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: c-level
  domain: strategic-planning
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: cascade-modeling, scenario-planning, pre-mortem, contingency-design
---

# Scenario War Room

**Tier:** POWERFUL
**Category:** C-Level Advisory
**Tags:** scenario planning, war room, risk modeling, cascade effects, contingency planning, pre-mortem, crisis simulation

## Overview

The Scenario War Room models cascading what-if scenarios across all business functions. Not single-assumption stress tests -- compound adversity that shows how one problem creates the next, and where the cascade can be interrupted. Every scenario produces concrete hedges with costs, owners, and deadlines.

---

## When to Use

- A major risk has probability above 15% and impact above 20% of ARR
- Two or more threats could plausibly co-occur
- A strategic decision has significant downside if wrong
- Board or investors are asking "what's the worst case?"
- Pre-mortem before a major commitment (fundraise, acquisition, market entry)
- Quarterly risk review for leadership team

## When NOT to Use

- Single-variable financial sensitivity analysis (use CFO Advisor stress testing)
- Routine project risk assessment (use project management risk frameworks)
- Technical failure mode analysis (use engineering incident planning)

---

## The 6-Step Cascade Model

### Step 1: Define Scenario Variables (Maximum 3)

More than 3 variables creates analysis paralysis, not insight. Choose the 3 that actually keep leadership awake at night.

For each variable, specify:

| Field | Description | Example |
|-------|-----------|---------|
| **What changes** | Specific, quantified | "Top customer (28% of ARR) gives 60-day termination notice" |
| **Probability** | Your best estimate | 15% |
| **Timeline** | When it could hit | Within 90 days |
| **Detection signal** | How you would know it is happening | Sponsor goes dark, usage drops 25% MoM |

**Variable Template:**
```
Variable A: [Specific change]
  Probability: [X]%  |  Timeline: [When]
  Detection: [Early warning signal]
  First-order impact: [Immediate consequence]

Variable B: [Specific change]
  Probability: [X]%  |  Timeline: [When]
  Detection: [Early warning signal]
  First-order impact: [Immediate consequence]

Variable C: [Specific change]
  Probability: [X]%  |  Timeline: [When]
  Detection: [Early warning signal]
  First-order impact: [Immediate consequence]
```

### Step 2: Domain Impact Mapping

For each variable, assess impact across every business function:

| Domain | Key Questions | Typical Impact Areas |
|--------|-------------|---------------------|
| **Finance (CFO)** | Burn impact? Runway change? Bridge options? | Cash, runway, covenant triggers |
| **Revenue (CRO)** | ARR gap? Churn cascade? Pipeline affected? | NRR, expansion, new logo risk |
| **Product (CPO)** | Roadmap derailed? PMF at risk? Customer need shift? | Delivery timeline, feature priority |
| **Engineering (CTO)** | Velocity hit? Key person risk? Technical debt impact? | Capacity, architecture, hiring |
| **People (CHRO)** | Attrition cascade? Hiring freeze? Morale impact? | Retention, culture, bench strength |
| **Operations (COO)** | Capacity affected? Process breaks? OKR impact? | SLAs, efficiency, scale |
| **Market (CMO)** | CAC affected? Competitive exposure? Brand risk? | Pipeline generation, positioning |
| **Legal/Compliance** | Regulatory timeline risk? Contract exposure? | Obligations, deadlines, penalties |

### Step 3: Cascade Mapping (The Core)

This is the most valuable step. Map how Variable A triggers consequences that amplify Variable B.

**Cascade Diagram:**
```
TRIGGER: Customer churn ($560K ARR)
  │
  ├──▶ CFO: Runway drops 14 → 8 months
  │     │
  │     └──▶ CHRO: Hiring freeze imposed
  │           │
  │           └──▶ CTO: 3 open engineering reqs frozen, roadmap slips 2 months
  │                 │
  │                 └──▶ CPO: Q4 feature launch delayed → 2 more customers at risk
  │                       │
  │                       └──▶ CRO: NRR drops → additional churn risk (DEATH SPIRAL ENTRY)
  │
  └──▶ CRO: Revenue concentration increases (next largest = 22%)
        │
        └──▶ Investors: Concentration risk flagged → Series A terms worsen
```

**Name the cascades explicitly.** Common cascade patterns:

| Cascade Pattern | Description | Interruption Point |
|----------------|-------------|-------------------|
| Revenue-to-Runway Death Spiral | Customer churn → lower runway → hiring freeze → slower product → more churn | Emergency revenue diversification |
| Key Person Cascade | Star leaves → team morale drops → followers leave → velocity collapses | Retention bonuses before departure |
| Market Squeeze | Competitor raises → price war → margins compress → can't invest in product | Differentiation, not price matching |
| Trust Cascade | Incident → customer concern → churn → press → more churn | Swift, transparent communication |
| Fundraise-Burn Spiral | Miss target → raise delayed → bridge at bad terms → burn cuts → team loss | Parallel fundraise tracks |

### Step 4: Severity Matrix

Model three scenarios with increasing severity:

| Scenario | Variables Hit | Definition | Recovery Difficulty |
|----------|-------------|-----------|-------------------|
| **Base** | 1 of 3 | Single shock, others don't materialize | Manageable with prepared response |
| **Stress** | 2 of 3 | Compound shock, cascade begins | Requires significant pivot, board involvement |
| **Severe** | All 3 | Full cascade, existential territory | Requires emergency action, may need board intervention |

For each severity level, quantify:

```
BASE SCENARIO (Variable A only):
  Runway impact: [X] months → [Y] months
  ARR impact: -$[X] ([Y]% of total)
  Headcount impact: [freeze / reduction / none]
  Timeline to critical: [X] months
  Recovery plan: [specific actions]

STRESS SCENARIO (Variables A + B):
  Runway impact: [X] months → [Y] months
  ARR impact: -$[X] ([Y]% of total)
  Headcount impact: [specifics]
  Timeline to critical: [X] months
  Recovery plan: [specific actions]

SEVERE SCENARIO (All three):
  Runway impact: [X] months → [Y] months
  ARR impact: -$[X] ([Y]% of total)
  Headcount impact: [specifics]
  Timeline to critical: [X] months
  Existential: [yes/no]
  Emergency plan: [specific actions requiring board approval]
```

### Step 5: Early Warning Signals (Trigger Points)

Define measurable signals that tell you a scenario is unfolding BEFORE it is confirmed. The value of this exercise is acting early, not reacting late.

**Signal Design Criteria:**
- Observable (you can actually measure it)
- Leading (appears before the full impact)
- Specific (not just "things feel off")
- Actionable (triggers a specific response)

| Variable | Signal | Threshold | Response |
|----------|--------|-----------|----------|
| Customer churn | Sponsor stops responding | > 3 weeks silence | Exec escalation, QBR request |
| Customer churn | Usage drops | > 25% MoM decline | CS outreach, value review |
| Fundraise delay | Term sheets | < 3 after 60 days in process | Parallel bridge conversations |
| Fundraise delay | Investor requests | > 30 day DD extension | Reduce burn, extend runway |
| Key person departure | Market compensation | Counter-offer required in last 90 days | Retention package, succession plan |
| Key person departure | External engagement | Engineer presenting at conferences for competitors | Direct conversation, role expansion |

### Step 6: Hedging Strategies

For each scenario: actions to take NOW (before the scenario materializes) that reduce impact if it does. Hedges have costs -- the goal is cheap insurance, not paranoia.

**Hedge Evaluation Criteria:**

| Criterion | Question |
|-----------|----------|
| Cost | What does this hedge cost to implement? |
| Reversibility | Can we undo it if the scenario doesn't happen? |
| Lead time | How long to implement? (Must be shorter than detection-to-impact window) |
| Coverage | Which scenarios does this hedge protect against? |
| Side effects | Does this hedge cause other problems? |

**Hedge Table Template:**

| Hedge | Cost | Protects Against | Owner | Deadline | Status |
|-------|------|-----------------|-------|----------|--------|
| Establish $500K credit line | $5K/year | Runway shortfall (Base + Stress) | CFO | 60 days | Not started |
| 12-month retention bonus for 3 key engineers | $90K | Key person departure (all scenarios) | CHRO | 30 days | In progress |
| Diversify to <20% revenue per customer | Sales effort (6 months) | Single-customer dependency | CRO | 2 quarters | Planning |
| Start parallel fundraise track | CEO time (10 hrs/week) | Fundraise delay (Stress + Severe) | CEO | Immediate | Not started |
| Pre-negotiate bridge terms with existing investors | 2 board conversations | Runway crisis (Severe) | CFO + CEO | 45 days | Not started |
| Document architecture for bus factor reduction | 2 engineering weeks | Key person departure | CTO | 30 days | Not started |

---

## Output Format

Every war room session produces this structured output:

```
SCENARIO: [Name]
DATE: [Date of analysis]
PARTICIPANTS: [Who was involved]

VARIABLES:
  A: [Description] — Probability: [X]%, Timeline: [When]
  B: [Description] — Probability: [X]%, Timeline: [When]
  C: [Description] — Probability: [X]%, Timeline: [When]

MOST LIKELY PATH: [Which combination actually plays out, with reasoning]

SEVERITY LEVELS:
  Base (A only):  Runway [X]→[Y]mo, ARR impact -$[X]
    Recovery: [2-3 specific actions]
  Stress (A+B):   Runway [X]→[Y]mo, ARR impact -$[X]
    Recovery: [3-4 specific actions]
  Severe (A+B+C): Runway [X]→[Y]mo, ARR impact -$[X]
    Existential: [yes/no]
    Emergency: [actions requiring board approval]

CASCADE MAP:
  [A] → [domain impact] → [triggers B amplification] → [domain impact] → [end state]
  Interruption points: [where cascade can be broken]

EARLY WARNING SIGNALS:
  1. [Signal] → indicates [scenario], threshold: [specific]
  2. [Signal] → indicates [scenario], threshold: [specific]
  3. [Signal] → indicates [scenario], threshold: [specific]

HEDGES (implement now):
  1. [Action] — cost: $[X] — protects: [scenarios] — owner: [role] — deadline: [date]
  2. [Action] — cost: $[X] — protects: [scenarios] — owner: [role] — deadline: [date]
  3. [Action] — cost: $[X] — protects: [scenarios] — owner: [role] — deadline: [date]

RECOMMENDED DECISION:
  [One paragraph: what to do, in what order, and why]

REVIEW DATE: [When to re-run this analysis — typically 90 days or after any variable shifts]
```

---

## Common Scenarios by Company Stage

### Seed Stage
- Co-founder departure + product misses launch deadline
- Runway runs out + bridge terms are predatory
- Key technical hire falls through + competitor ships first

### Series A
- Miss ARR target + fundraise delayed
- Top customer churns + competitor raises large round
- Key engineer leaves + critical feature deadline

### Series B+
- Market contraction + burn multiple spikes above 3x
- Lead investor wants strategic pivot + team resists
- Regulatory change + product requires rearchitecture

---

## War Room Ground Rules

1. **Maximum 3 variables per scenario.** More is noise. Model the ones that actually matter.
2. **Quantify or estimate.** "Revenue drops" is not useful. "$420K ARR at risk over 60 days" is. Use ranges if uncertain.
3. **Don't stop at first-order effects.** The real damage is always in the cascade.
4. **Model recovery, not just impact.** Every scenario must have a "what we do" path.
5. **Separate base case from sensitivity.** Don't conflate "what probably happens" with "what could happen."
6. **3-4 scenarios per planning cycle.** More creates analysis paralysis.
7. **Review every 90 days.** Probabilities and variables change. Stale scenarios give false comfort.
8. **No judgment-free zone.** People must feel safe naming ugly scenarios.

---

## Related Skills

| Skill | Use When |
|-------|----------|
| **ceo-advisor** | Strategic decisions that scenarios inform |
| **cfo-advisor** | Financial modeling for scenario impacts |
| **coo-advisor** | Operational contingency planning |
| **internal-narrative** | Communicating scenario outcomes to stakeholders |
| **cs-onboard** | Company context that feeds scenario variables |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Scenarios feel too abstract to act on | Variables not specific or quantified enough | Require dollar amounts, percentages, and timelines for every variable; "revenue drops" is not actionable, "$420K ARR at risk over 60 days" is |
| Team generates only obvious, low-probability scenarios | Conformity bias; not applying Shell scenario planning method of challenging mental models | Use inversion technique: "What would guarantee our failure?"; bring in external perspective; reference industry-specific historical precedents |
| Cascade mapping stops at first-order effects | Facilitator not pushing past immediate consequences | Require minimum 3 levels of cascade for each variable; use "and then what?" prompting for each domain impact |
| Hedges identified but never implemented | No ownership, deadline, or cost attached | Every hedge must have: cost estimate, owner name, deadline, and status tracking; review in weekly leadership meeting |
| War room sessions take too long (> 4 hours) | Too many variables or trying to model every scenario | Enforce maximum 3 variables and 3-4 scenarios per session; use severity matrix to focus on highest-impact combinations |
| Early warning signals not being monitored | Signals assigned but not integrated into existing reporting | Add signals to existing dashboards and weekly scorecards; assign specific person to monitor each signal |
| Participants reluctant to name worst-case scenarios | Fear of being seen as negative or alarmist | Establish ground rules explicitly; cite Shell's experience: "the value is in surfacing what others won't say"; reward naming hard truths |

---

## Success Criteria

- Each scenario session produces exactly 3 variables, 3 severity levels, and a cascade map with interruption points identified
- Early warning signals are specific enough to be monitored: observable, leading, and actionable with defined thresholds
- Hedges are costed, owned, and have deadlines within 7 days of the war room session
- At least one hedge per scenario is implemented (not just planned) within 30 days
- Scenario review conducted every 90 days with probability updates based on new information
- When an early warning signal fires, the pre-planned response is executed within the defined timeline
- War room output is concise enough for board consumption: one-page summary per scenario

---

## Scope & Limitations

- **In scope:** Multi-variable scenario construction, cascade modeling across all business functions, severity matrix analysis, early warning signal design, hedge strategy with cost-benefit analysis, scenario review cadence
- **Out of scope:** Single-variable financial sensitivity analysis (use CFO Advisor stress testing); technical failure mode analysis (use engineering incident planning); routine project risk assessment (use project management frameworks); insurance and risk transfer (use specialized broker)
- **Limitation:** Scenario probabilities are subjective estimates, not actuarial calculations; value is in preparedness, not prediction accuracy
- **Limitation:** Framework assumes scenarios are independent or correlated; black swan events by definition are not modelable
- **Limitation:** Cascade mapping is based on common organizational patterns; unique company structures may have different cascade paths
- **Limitation:** Maximum 3 variables per scenario is a deliberate constraint; more variables create analysis paralysis, not better insight

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `ceo-advisor` | Strategic decisions informed by scenario analysis | War room scenarios → CEO decision inputs |
| `cfo-advisor` | Financial modeling for scenario impacts and hedge costs | War room financial impacts → CFO stress test models |
| `coo-advisor` | Operational contingency planning and cascade interruption | War room cascade map → COO contingency plans |
| `executive-mentor` | Pre-mortem failure modes feed into scenario variables | Mentor failure modes → War room variables |
| `internal-narrative` | Crisis scenarios require pre-built communication plans | War room crisis scenarios → Narrative crisis templates |
| `org-health-diagnostic` | Health dimension scores surface scenario variables | Health red flags → War room variable candidates |
| `strategic-alignment` | Scenario outcomes may require strategic realignment | War room outcomes → Alignment reassessment |

---

## Python Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `scripts/scenario_builder.py` | Build structured scenarios with variables, probabilities, detection signals, and severity levels | `python scripts/scenario_builder.py --name "Customer Concentration Risk" --variable "Top customer churns" --probability 20 --impact 500000 --timeline 90 --json` |
| `scripts/impact_matrix_calculator.py` | Calculate compound impact across multiple variables with severity matrix and cascade risk scoring | `python scripts/impact_matrix_calculator.py --variables "churn:500000:0.2" "fundraise_delay:0:0.3" "key_departure:0:0.15" --arr 2000000 --runway-months 14 --json` |
| `scripts/decision_tree_analyzer.py` | Build and evaluate decision trees with expected value calculations for strategic options | `python scripts/decision_tree_analyzer.py --decision "Enter Japan market" --option "Direct:0.6:2000000:-500000" --option "Partnership:0.75:1000000:-200000" --option "Wait:1.0:0:0" --json` |
