# Assumption Mapping Guide

## Teresa Torres' Four Risk Categories

Teresa Torres identifies four types of risk that every product decision carries. These categories originate from her book *Continuous Discovery Habits* and are the standard framework for assumption mapping in continuous product discovery.

### Value Risk

**Question:** Will customers want this? Will they choose it over alternatives?

**What to look for:**
- Assumptions about the severity or frequency of the problem.
- Assumptions about how customers currently solve the problem.
- Assumptions about willingness to switch from the current solution.
- Assumptions about perceived value relative to price.

**Red flags:**
- "Everyone has this problem" -- usually not true. Define the specific segment.
- "Users told us they want this" -- stated preference does not equal revealed preference.
- "No one else is doing this" -- could mean no demand, not just no competition.

### Usability Risk

**Question:** Can customers figure out how to use this? Will they complete the task successfully?

**What to look for:**
- Assumptions about user mental models and expectations.
- Assumptions about discoverability of features.
- Assumptions about required knowledge or skill level.
- Assumptions about error recovery and edge cases.

**Red flags:**
- "It is intuitive" -- intuitive to the team that built it, maybe not to users.
- "We will add a tutorial" -- tutorials are a band-aid for poor usability.
- "Power users will figure it out" -- even power users have limited patience.

### Viability Risk

**Question:** Can the business sustain this? Does the economics work?

**What to look for:**
- Assumptions about revenue impact or cost savings.
- Assumptions about customer acquisition cost and lifetime value.
- Assumptions about operational cost of maintaining the feature.
- Assumptions about regulatory or legal compliance.

**Red flags:**
- "We will monetize later" -- without a path, later often means never.
- "The marginal cost is zero" -- infrastructure, support, and maintenance are rarely zero.
- "Legal will be fine with it" -- check early, not after building.

### Feasibility Risk

**Question:** Can we build this with our current team, technology, and timeline?

**What to look for:**
- Assumptions about technical complexity and unknowns.
- Assumptions about third-party dependencies (APIs, vendors, partners).
- Assumptions about data availability and quality.
- Assumptions about performance, scalability, and reliability requirements.

**Red flags:**
- "It is just a simple API call" -- integration is rarely simple.
- "We have done something similar before" -- similar is not identical.
- "It will take two weeks" -- engineer estimates are systematically optimistic.

---

## Extended 8-Category Model for New Products

When building something entirely new, four additional risk categories become relevant. These are often overlooked because they fall outside the traditional product development frame.

### Ethics Risk

**Question:** Should we build this? Could it cause harm?

**Assumptions to surface:**
- Data collection will not violate user privacy expectations.
- The product will not create negative externalities for non-users.
- Algorithmic decisions will not exhibit bias against protected groups.
- Users will give informed consent for how their data is used.
- The product will not enable harmful use cases.

**When to prioritize:** Any product involving personal data, AI/ML, health, finance, or vulnerable populations.

### Go-to-Market Risk

**Question:** Can we reach and acquire our target customers?

**Assumptions to surface:**
- The target segment is reachable through specific channels.
- Customer acquisition cost will be below lifetime value.
- The value proposition can be communicated in a headline.
- Word-of-mouth or viral mechanics will contribute to growth.
- Sales cycle length is within our runway tolerance.

**When to prioritize:** Any new product without an existing distribution channel or customer base.

### Strategy and Objectives Risk

**Question:** Does this align with where the company wants to go?

**Assumptions to surface:**
- This product/feature advances a current company objective.
- Leadership will continue to fund this initiative through completion.
- This does not cannibalize or conflict with other products.
- The competitive landscape will remain favorable.
- Market timing is right (not too early, not too late).

**When to prioritize:** New products, pivots, or features that represent a strategic bet.

### Team Risk

**Question:** Do we have the right people and skills to execute?

**Assumptions to surface:**
- The team has the technical skills required.
- Key personnel will remain available throughout the project.
- Cross-functional collaboration will be effective.
- The team can learn new skills within the project timeline.
- We can hire for skill gaps quickly enough.

**When to prioritize:** Projects requiring new technologies, new domains, or stretched teams.

---

## Confidence Calibration Techniques

Confidence levels are subjective. Use these techniques to improve calibration:

### Evidence-Based Confidence

| Confidence Level | Evidence Required |
|-----------------|-------------------|
| **High** | Direct quantitative data (analytics, A/B test results, sales data) from your own product/market |
| **Medium** | Qualitative evidence (5+ user interviews), analogous data from similar products, or industry benchmarks |
| **Low** | Team intuition, anecdotal evidence, or no evidence at all |

### The Five Whys Test

For any assumption rated "High confidence," ask "Why do we believe this?" five times. If you cannot trace the confidence back to concrete evidence by the third "why," downgrade to Medium.

### Pre-Mortem Check

Imagine the assumption turned out to be wrong. How surprised would you be?
- "I would be shocked" = High confidence (but verify you have evidence, not just conviction)
- "I would be disappointed but not shocked" = Medium confidence
- "I honestly do not know" = Low confidence

### Calibration Exercise

Before mapping assumptions, run a quick calibration: have each team member independently rate confidence for 3-4 well-known assumptions (e.g., "Our homepage conversion rate is above 3%"). Compare ratings. If the team diverges significantly, discuss what evidence each person is using. This aligns the team's confidence scale before the real exercise.

---

## Assumption Prioritization Matrix

### The 2x2 Matrix

```
                    HIGH IMPACT
                        |
     PROCEED            |     TEST NOW
     (high confidence,  |     (low confidence,
      high impact)      |      high impact)
                        |
  ──────────────────────┼──────────────────────
                        |
     DEFER              |     INVESTIGATE
     (high confidence,  |     (low confidence,
      low impact)       |      low impact)
                        |
                    LOW IMPACT

     HIGH CONFIDENCE ◄──┼──► LOW CONFIDENCE
```

### Decision Rules

| Quadrant | Action | Timeline |
|----------|--------|----------|
| **Test Now** | Design and run an experiment within the current sprint/cycle | This week |
| **Proceed** | Move forward but set a monitoring tripwire | Ongoing |
| **Investigate** | Gather more information; may promote to Test Now | Next cycle |
| **Defer** | Accept the risk; revisit only if context changes | Backlog |

### Tripwires for "Proceed" Assumptions

Even high-confidence assumptions can be wrong. Set tripwires:
- "If churn exceeds 8% in the first month, revisit the value assumption."
- "If support tickets about this feature exceed 20/week, revisit the usability assumption."

---

## Connection to Experiment Design

Assumption mapping feeds directly into experiment design:

1. **Identify** assumptions (this skill).
2. **Prioritize** to find "Test Now" assumptions.
3. **Design experiments** (use `brainstorm-experiments/` skill) targeting the riskiest assumptions.
4. **Run experiments** and update confidence levels based on results.
5. **Re-prioritize** -- the map is a living document.

### Mapping Assumptions to Experiment Types

| Assumption Category | Best Experiment Types |
|--------------------|-----------------------|
| Value | Customer interviews, fake door tests, landing pages, pre-orders |
| Usability | Usability testing (5 users), prototype walkthroughs, first-click tests |
| Viability | Pricing experiments, unit economics modeling, willingness-to-pay surveys |
| Feasibility | Technical spikes, proof of concept, architecture reviews |
| Ethics | Ethics review, user consent studies, bias audits |
| Go-to-Market | Channel experiments, SEO keyword tests, paid ad campaigns |
| Strategy | Leadership alignment sessions, competitive analysis |
| Team | Skills assessments, trial projects, pair programming sessions |
