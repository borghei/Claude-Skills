# Outcome Roadmap Guide

A detailed reference for building outcome-driven roadmaps that communicate strategy, not just feature lists.

---

## Output vs Outcome Roadmap

### Side-by-Side Comparison

| Aspect | Output Roadmap | Outcome Roadmap |
|--------|---------------|-----------------|
| **Format** | Feature list with dates | Outcome statements with horizons |
| **Time horizon** | Q1, Q2, Q3, Q4 (fixed dates) | Now, Next, Later (commitment levels) |
| **Success measure** | "Did we ship it?" | "Did it produce the expected result?" |
| **Stakeholder question** | "When will feature X be done?" | "How are we progressing toward outcome Y?" |
| **Risk** | Dates slip, trust erodes | Outcomes are flexible; learning is valued |
| **Team alignment** | Aligned on deliverables | Aligned on impact |
| **Adaptability** | Change requires re-planning | Pivot the solution, keep the outcome |

### Why Outcomes Win

When a roadmap says "Build advanced search in Q2," the team ships advanced search in Q2. Success. But if customers do not use it, or it does not improve conversion, was it actually a success?

When a roadmap says "Enable customers to find products 50% faster," the team might build advanced search. Or they might improve navigation. Or they might add better categorization. The outcome is fixed; the solution is flexible. If advanced search does not work, the team can pivot without declaring failure.

---

## Outcome Statement Formula

```
Enable [customer segment] to [desired customer outcome] so that [business impact]
```

### Breaking It Down

**[Customer segment]:** Who specifically benefits? Be precise. "Users" is too broad. "New users in their first week" or "Enterprise admins managing 50+ seats" is specific enough to design for.

**[Desired customer outcome]:** What changes in the customer's experience? This should be something the customer would recognize and value. "Find products in under 5 seconds" -- a customer understands this. "Improved search indexing" -- a customer does not care about this.

**[Business impact]:** Why does the business care? Connect to a metric: revenue, retention, cost, market share, competitive position.

### Examples

| Output | Outcome |
|--------|---------|
| Build advanced search | Enable power users to find relevant products in under 5 seconds so that browse-to-purchase conversion increases by 20% |
| Launch mobile app | Enable field teams to access critical data on-site so that deal cycle time decreases by 30% |
| Add SSO integration | Enable enterprise IT admins to onboard teams in minutes instead of days so that enterprise deal close rate improves by 25% |
| Redesign dashboard | Enable managers to identify at-risk accounts in one glance so that proactive retention outreach increases by 40% |
| Migrate to new database | Enable the platform to handle 10x current load without degradation so that we can support enterprise-tier SLAs |

---

## The "So What?" Technique

The most powerful tool for finding outcomes. Start with the feature and keep asking "so what?" until you reach something a customer or executive would care about.

### Example 1

```
"Add CSV export"
  -> So what?
"Users can get their data out of the system"
  -> So what?
"They can share reports with stakeholders who don't have accounts"
  -> So what?
"Decision-makers see the data, which accelerates deal approvals"

Outcome: "Enable users to share insights with external stakeholders
          so that deal approval cycles shorten by 2 weeks"
```

### Example 2

```
"Implement caching layer"
  -> So what?
"Pages load faster"
  -> So what?
"Users experience less friction during peak hours"
  -> So what?
"Abandonment rate during high-traffic periods decreases"

Outcome: "Enable users to complete transactions without slowdowns during
          peak traffic so that peak-hour abandonment drops below 5%"
```

### When to Stop

Stop when you reach a statement that satisfies both:
1. A customer would nod and say "yes, that matters to me"
2. A business leader would say "yes, that moves a metric I care about"

If only one is satisfied, keep asking.

---

## Time Horizon Recommendations

### Now / Next / Later

This framework replaces calendar quarters with commitment levels.

**Now (0-6 weeks)**
- Team is actively working on this or will start within 2 weeks.
- Scope is defined. Solution is chosen. Dependencies are identified.
- Detail level: Full outcome statement, specific metrics, assigned team.
- Commitment: "We are doing this."

**Next (6 weeks - 3 months)**
- Direction is clear. Solution may still be flexible.
- The problem is validated, but the approach may change based on learnings from "Now" items.
- Detail level: Outcome statement with draft metrics. Team identified but not fully assigned.
- Commitment: "We intend to do this, subject to learning."

**Later (3-6 months)**
- Strategic opportunity or problem area identified.
- No solution chosen. May be reframed based on what we learn.
- Detail level: Problem statement or opportunity description. No solution details.
- Commitment: "We are thinking about this."

### Why Not Quarters?

Calendar quarters create two problems:

1. **False precision:** "Q3" implies a specific 3-month window. But 6 months out, you cannot predict scope, dependencies, or team availability with any reliability. The date becomes a promise you cannot keep.

2. **Rigidity:** When a Q2 item slips to Q3, the entire roadmap shifts. With Now/Next/Later, items move between horizons based on strategic priority, not calendar math.

---

## Success Metrics for Outcome Roadmaps

Every outcome needs 2-3 metrics that tell you whether the outcome was achieved.

### Metric Types

**Leading indicators:** Predict future success. Measurable quickly. Examples: sign-up rate, feature adoption in first week, NPS after onboarding.

**Lagging indicators:** Confirm actual impact. Take longer to materialize. Examples: revenue change, churn rate, market share.

**Counter-metrics:** Ensure you are not achieving the outcome at the expense of something else. Examples: if you increase sign-ups, track activation rate to make sure quality is not dropping.

### Metric Selection Checklist

- [ ] Is this metric directly influenced by the initiative?
- [ ] Can we measure it within the quarter?
- [ ] Do we have a reliable baseline (current value)?
- [ ] Would improving this metric genuinely indicate success?
- [ ] Is there a counter-metric to catch unintended consequences?

---

## Stakeholder Communication Strategies

### For Executives

Executives want to know: "Are we making progress toward our strategic goals?"

- Lead with outcomes, not features.
- Show metrics: baseline, target, current progress.
- Use Now/Next/Later to show strategic sequencing.
- Highlight dependencies and risks, not task-level status.

### For Sales Teams

Sales wants to know: "What can I tell customers is coming?"

- Share "Now" items as commitments. Be specific about what customers will experience.
- Share "Next" items as direction. Use language like "We are investing in [outcome area]."
- Do not share "Later" items. They change too frequently.

### For Engineering Teams

Engineers want to know: "What problem am I solving and how will I know I succeeded?"

- Lead with the outcome statement and success metrics.
- Share the "so what?" chain so engineers understand the full context.
- Let engineers propose solutions. The outcome is fixed; the approach is theirs.

### For Customers

Customers want to know: "Will this product keep solving my problems?"

- Share themes, not features. "We are investing in making collaboration faster" is better than "We are building real-time editing."
- Use outcome language: "You will be able to [desired outcome]."
- Never share dates unless you are confident. Missed dates destroy trust faster than vague timelines.

---

## Roadmap Review Cadence

| Activity | Frequency | Participants | Purpose |
|----------|-----------|-------------|---------|
| Outcome check-in | Weekly | Product + Engineering leads | Are "Now" items progressing toward metrics? |
| Horizon review | Monthly | Product team + stakeholders | Should anything move between Now/Next/Later? |
| Strategic review | Quarterly | Leadership + Product | Are our outcomes still aligned to company strategy? |
| Customer validation | Ongoing | Product + Customer-facing teams | Are our outcome assumptions correct? |
