# Pre-Mortem Guide

## Origin: Gary Klein's Prospective Hindsight

The pre-mortem technique was developed by psychologist Gary Klein and published in the *Harvard Business Review* in 2007. It is based on research into "prospective hindsight" -- the finding that imagining an event has already occurred increases the ability to identify reasons for that event by 30%.

### Why Pre-Mortems Work

Traditional risk assessment asks: "What could go wrong?" This question triggers optimism bias -- people tend to minimize risks because they are invested in the plan's success.

A pre-mortem flips the frame: "The project has failed. Why?" This framing:
1. **Legitimizes dissent.** Team members have permission to voice concerns.
2. **Activates different cognitive processes.** Explaining a "past" event is easier than predicting a future one.
3. **Reduces groupthink.** The exercise explicitly asks for failure scenarios, breaking the social pressure to be positive.
4. **Surfaces elephants.** Anonymous contributions lower the barrier to raising sensitive issues.

### When to Run a Pre-Mortem

- **Before major commits.** Before allocating a full team to a multi-month effort.
- **Before launches.** 2-4 weeks before go-live, when there is still time to act on findings.
- **Before migrations or architectural changes.** High-risk, low-reversibility decisions.
- **Periodically during long projects.** Every 6-8 weeks for projects lasting more than a quarter.

### When NOT to Run a Pre-Mortem

- When the decision is already made and irreversible. A pre-mortem on a shipped feature wastes energy; run a retrospective instead.
- When the team lacks psychological safety. If people cannot speak honestly, the exercise will produce sanitized results.

---

## Tiger / Paper Tiger / Elephant Classification

### Tigers: Real Risks

**Definition:** Risks supported by evidence that could credibly cause the project to fail.

**How to identify:**
- Can the person describe a specific, plausible failure scenario?
- Is there data, past experience, or observable signals supporting this risk?
- Would a reasonable outside observer agree this is a real concern?

**Examples across domains:**

| Domain | Tiger Example |
|--------|--------------|
| Technical | "Our database query P99 latency is already 800ms. Adding the new feature will push it over SLA." |
| Market | "Three of our five pilot customers have gone silent after the demo. No follow-up despite outreach." |
| Operational | "The only person who knows the deployment process is on parental leave starting next week." |
| Financial | "Our burn rate at current headcount gives us 4 months of runway. The feature needs 5 months." |

### Paper Tigers: Perceived but Unlikely Risks

**Definition:** Risks that sound alarming but are unlikely to materialize or would have manageable impact.

**How to identify:**
- Is the scenario based on speculation rather than evidence?
- Is the probability very low (< 5%)?
- If it happened, could we recover quickly?
- Is this a general anxiety rather than a specific concern?

**Examples:**

| Perceived Risk | Why It Is a Paper Tiger |
|---------------|------------------------|
| "AWS might have a global outage on launch day" | Probability < 0.1%. Multi-AZ setup provides resilience. |
| "A major competitor might launch the same feature" | Their last release was 8 months ago. Even if they started now, we would have a 6-month head start. |
| "Users might abuse the API" | Rate limiting is in place. Abuse is detectable and reversible. |

**Caution:** Sometimes a Paper Tiger is actually a Tiger that the team is underestimating. If there is disagreement, investigate further before dismissing.

### Elephants: Unspoken Concerns

**Definition:** Risks that the team is aware of but avoids discussing, typically because they involve interpersonal dynamics, organizational politics, or uncomfortable truths.

**How to identify:**
- The room goes quiet when the topic is raised.
- People speak in euphemisms or generalities.
- The risk involves a person, a relationship, or a power dynamic.
- Multiple people have mentioned it privately but not in group settings.

**Examples:**

| Elephant | Why It Is Unspoken |
|----------|--------------------|
| "The project sponsor does not actually use the product and is making requirements based on assumptions" | Challenging the sponsor feels politically risky |
| "Two key engineers have been interviewing elsewhere" | Retention concerns feel disloyal to raise publicly |
| "The deadline was set by a sales commitment, not engineering estimation" | Nobody wants to push back on the VP of Sales |
| "We are building this because the CEO saw a competitor demo, not because of customer demand" | Questioning the CEO's judgment feels career-limiting |

**How to surface elephants:**
1. Anonymous contributions (sticky notes, digital forms).
2. Direct prompts: "What are we pretending is not a problem?"
3. One-on-one conversations before the session to prime participation.
4. Explicit psychological safety: "There will be no consequences for anything raised in this exercise."

---

## Urgency Classification Guide

Once a risk is classified as a Tiger, assign one of three urgency levels:

### Launch-Blocking

**Definition:** If this risk is not mitigated before launch, the launch should not proceed.

**Criteria (any one is sufficient):**
- The risk could cause data loss, security breach, or legal liability.
- The risk could cause >50% of target users to have a broken experience.
- The risk would make the core value proposition non-functional.
- The risk would cause immediate, public reputational damage.

**Required action:**
- Concrete mitigation plan with specific steps.
- Single accountable owner.
- Decision date: a specific date by which the mitigation is complete or the launch is postponed.

### Fast-Follow

**Definition:** This risk is real but manageable at launch. It must be addressed within 2 weeks post-launch.

**Criteria:**
- The risk affects a subset of users or a secondary flow.
- A temporary workaround exists (manual process, reduced functionality).
- The risk grows over time but is acceptable for a short window.

**Required action:**
- Documented plan.
- Assigned owner.
- Scheduled in the first post-launch sprint.

### Track

**Definition:** This risk should be monitored but does not require immediate action.

**Criteria:**
- The risk is real but low probability in the near term.
- The impact is manageable if it materializes.
- Early warning signals exist that would give time to respond.

**Required action:**
- Added to risk register.
- Monitoring metric or tripwire defined.
- Reviewed at regular cadence (weekly or bi-weekly).

---

## Facilitation Guide for Pre-Mortem Sessions

### Before the Session

1. **Invite the right people.** Include PM, Design, Engineering, QA, and at least one person outside the core team (fresh perspective).
2. **Set expectations.** Send a pre-read explaining the exercise and ground rules.
3. **Prepare materials.** Sticky notes (physical or digital), timer, board for clustering.
4. **Create safety.** Ensure anonymous contribution is possible.

### During the Session (60 minutes total)

| Phase | Duration | Facilitator Action |
|-------|----------|--------------------|
| Set the scene | 5 min | Read the failure prompt. Establish ground rules. |
| Silent generation | 10 min | Everyone writes risks independently. No talking. |
| Share and cluster | 15 min | Read aloud, group on board, merge duplicates. |
| Classify | 15 min | Vote or discuss: Tiger, Paper Tiger, or Elephant for each cluster. |
| Mitigation planning | 15 min | Assign owner, mitigation, and decision date for Launch-Blocking Tigers. |

### Facilitator Tips

- **Protect anonymity.** If reading sticky notes aloud, shuffle them first. Do not ask "whose is this?"
- **Probe Paper Tigers.** "What evidence would change this from a Paper Tiger to a Tiger?" This prevents premature dismissal.
- **Name Elephants explicitly.** "I notice the room got quiet. Let us talk about this one."
- **Keep the energy up.** This exercise can feel heavy. Remind participants that identifying risks is empowering, not demoralizing.
- **Time-box strictly.** The mitigation phase tends to expand. Keep it focused on Launch-Blocking items only.

### After the Session

1. Document all risks in the pre-mortem template.
2. Distribute to all participants and stakeholders.
3. Track Launch-Blocking mitigations in your project management tool.
4. Schedule a follow-up review 1 week before the decision date.

---

## Example Pre-Mortem: SaaS Feature Launch

**Product:** Analytics dashboard for a B2B SaaS product
**Launch date:** 3 weeks from pre-mortem
**Participants:** PM, 2 Engineers, Designer, QA Lead

### Tigers Identified

| # | Risk | Urgency | Evidence |
|---|------|---------|----------|
| T1 | Dashboard query timeout on accounts with >100K events | Launch-Blocking | Load testing showed P95 latency of 12s on large accounts (SLA is 3s) |
| T2 | Export-to-CSV does not handle special characters in data | Fast-Follow | Bug found in QA but not yet fixed. Affects ~15% of accounts. |
| T3 | No monitoring alerts for the new data pipeline | Track | Pipeline is new. We have logs but no automated alerting. |

### Paper Tigers Identified

| # | Risk | Why Paper Tiger |
|---|------|----------------|
| P1 | Competitor X might launch similar feature | Their last release was 9 months ago. We have a 6-month head start. |
| P2 | Users might not find the new dashboard | It is the default landing page. Discovery is not a concern. |

### Elephants Identified

| # | Risk | Resolution |
|---|------|-----------|
| E1 | The PM who requested this feature left the company. Nobody has validated the requirements with current customers. | Reclassified as Tiger (Fast-Follow). PM will run 5 customer interviews this week. |
| E2 | The team is burned out from the previous sprint. Quality may suffer. | Acknowledged. Reduced scope for launch: defer 2 non-critical features to Fast-Follow. |

### Action Plan (Launch-Blocking)

| Tiger | Mitigation | Owner | Decision Date |
|-------|-----------|-------|--------------|
| T1: Query timeout | Add query optimization + caching layer for large accounts. If not resolved by decision date, launch with a feature flag limiting to accounts <50K events. | Senior Engineer | 10 days before launch |
