---
name: pre-mortem
description: Pre-mortem risk analysis expert that classifies risks as Tigers, Paper Tigers, and Elephants to surface launch-blocking issues before they happen.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-03-04
  python-tools: risk_categorizer.py
  tech-stack: pre-mortem, risk-analysis, gary-klein, prospective-hindsight
---

# Pre-Mortem Risk Analysis Expert

## Overview

A pre-mortem is a prospective hindsight exercise: imagine that your product has launched and failed, then work backward to identify why. This skill uses the Tiger / Paper Tiger / Elephant classification to categorize risks by type and urgency, ensuring launch-blocking issues are addressed before launch while avoiding wasted effort on unlikely risks.

### When to Use

- Before committing significant resources to build (post-ideation, post-validation).
- Before a major launch, migration, or architectural change.
- When the team has "a bad feeling" they cannot articulate.
- When stakeholder confidence is high and you need to stress-test it.

## Core Concept

### The Thought Experiment

> "It is 14 days after launch. The product has failed. What went wrong?"

This framing exploits a cognitive bias: people are better at explaining past events than predicting future ones. By placing the failure in the "past" (even fictitiously), participants generate more specific and honest risk assessments.

## Risk Classification

### Tigers (Real Risks)

Tigers are real, evidence-backed risks that could cause serious harm if not addressed.

**Characteristics:**
- Supported by data, past experience, or observable trends.
- The team can describe a plausible failure scenario in concrete terms.
- Ignoring them would be negligent.

**Examples:**
- "Our authentication service went down 3 times last month. A launch-day outage is plausible."
- "We have zero customers in the enterprise segment. Our sales team has no enterprise relationships."
- "The EU regulation takes effect in 60 days. We have not started compliance work."

### Paper Tigers (Look Scary but Unlikely)

Paper Tigers are risks that sound alarming but, on closer inspection, are unlikely or have minimal real impact.

**Characteristics:**
- Based on hypothetical scenarios without supporting evidence.
- The probability is very low, or the impact would be manageable.
- Often raised because of general anxiety rather than specific knowledge.

**Examples:**
- "A competitor might copy our feature" -- possible, but their execution timeline is 6-12 months.
- "The server might not handle 100x traffic" -- but our realistic projection is 5x, with auto-scaling.
- "Users might hate the new UI" -- but usability testing with 8 users showed high satisfaction.

### Elephants (Unspoken Concerns)

Elephants are the risks everyone knows about but nobody talks about. They are the "elephant in the room."

**Characteristics:**
- The team avoids discussing them due to politics, hierarchy, or discomfort.
- Often involve people, process, or organizational issues rather than technical ones.
- Frequently the actual cause of failure when projects fail.

**Examples:**
- "The tech lead does not believe in this project and has been disengaged for weeks."
- "The CEO's pet feature is driving the roadmap, but customers have not asked for it."
- "We do not have a plan for what happens when the contractor's contract ends next month."

## Tiger Urgency Classification

Once a risk is classified as a Tiger, assign an urgency level:

| Urgency | Definition | Action Required |
|---------|-----------|----------------|
| **Launch-Blocking** | If unresolved, the launch should not proceed. | Concrete mitigation plan, assigned owner, decision date before launch. |
| **Fast-Follow** | Must be addressed within 2 weeks after launch. | Documented plan, assigned owner, scheduled for first post-launch sprint. |
| **Track** | Should be monitored and addressed if it escalates. | Added to risk register, reviewed at regular cadence. |

## Methodology

### Phase 1: Set the Scene (5 minutes)

The facilitator reads this prompt to the group:

> "Imagine it is 14 days after our launch. The product has failed. Users are not adopting it, key metrics are down, and leadership is asking what went wrong. Take 10 minutes to write down every reason you can think of for why we failed. Be specific. Be honest. Nothing is off limits."

**Ground rules:**
- Anonymous contributions (sticky notes or digital equivalent).
- No attribution, no blame, no judgment.
- Quantity over quality in the first round.

### Phase 2: Generate Risks (10 minutes)

Each participant independently writes down failure scenarios. One risk per sticky note. Aim for 5-10 per person.

**Prompts to stimulate thinking:**
- What technical system is most likely to break?
- What customer objection have we not addressed?
- What team dynamic could derail us?
- What external event could change our assumptions?
- What are we pretending is not a problem?
- What decision are we avoiding?

### Phase 3: Share and Cluster (15 minutes)

1. Read each risk aloud (without attribution).
2. Place on the board.
3. Group similar risks together.
4. Merge duplicates.

### Phase 4: Classify (15 minutes)

For each cluster, the group decides:

| Classification | Criteria |
|---------------|----------|
| **Tiger** | Supported by evidence. Plausible failure scenario. |
| **Paper Tiger** | Sounds scary but unlikely or low-impact on inspection. |
| **Elephant** | The room got quiet when this was read. People exchanged glances. |

For each Tiger, assign urgency: Launch-Blocking, Fast-Follow, or Track.

### Phase 5: Mitigation Plans (15 minutes)

For each **Launch-Blocking Tiger**, complete:

| Field | Description |
|-------|-------------|
| **Risk** | Clear description of the risk |
| **Evidence** | What data or experience supports this being a real risk? |
| **Mitigation** | Specific, concrete action to reduce the risk |
| **Owner** | Single person accountable |
| **Decision Date** | Date by which the mitigation must be complete or the launch decision revisited |

### Phase 6: Address Elephants (10 minutes)

Elephants require a different approach than Tigers:

1. **Acknowledge** -- Name the elephant explicitly. "The team is concerned that..."
2. **Assess** -- Is this actually a Tiger in disguise? If so, reclassify.
3. **Decide** -- Either address it (assign an owner) or consciously accept it (document the acceptance and rationale).

## Python Tool: risk_categorizer.py

Categorize and analyze risks using the CLI tool:

```bash
# Run with demo data
python3 scripts/risk_categorizer.py --demo

# Run with custom input
python3 scripts/risk_categorizer.py input.json

# Output as JSON
python3 scripts/risk_categorizer.py input.json --format json
```

### Input Format

```json
{
  "risks": [
    {
      "description": "Authentication service has had 3 outages in the last month",
      "category": "tiger",
      "evidence": "Incident reports from last 30 days",
      "urgency": "launch_blocking"
    }
  ]
}
```

### Output

Risk distribution summary, action plans for launch-blocking tigers, and flags for elephants that may need investigation.

See `scripts/risk_categorizer.py` for full documentation.

## Output Format

### Pre-Mortem Summary

```
Pre-Mortem Analysis: [Product/Feature Name]
Date: YYYY-MM-DD
Participants: [list]
Total risks identified: N
  - Tigers: X (Launch-Blocking: A, Fast-Follow: B, Track: C)
  - Paper Tigers: Y
  - Elephants: Z
```

### Risk Registry

| # | Risk | Category | Urgency | Evidence | Mitigation | Owner | Decision Date |
|---|------|----------|---------|----------|-----------|-------|--------------|
| 1 | ... | Tiger | Launch-Blocking | ... | ... | ... | ... |
| 2 | ... | Tiger | Fast-Follow | ... | ... | ... | ... |
| 3 | ... | Paper Tiger | -- | ... | -- | -- | -- |
| 4 | ... | Elephant | TBD | ... | ... | ... | ... |

Use `assets/pre_mortem_template.md` for the full document template.

## Integration with Other Discovery Skills

- Use after `brainstorm-ideas/` and `brainstorm-experiments/` -- pre-mortem is the final check before committing to build.
- Feed launch-blocking Tiger mitigations back into `identify-assumptions/` if they surface new assumptions.
- Elephants often reveal assumptions that the team has been avoiding.

## References

- Gary Klein, "Performing a Project Pre-Mortem," *Harvard Business Review* (2007)
- Daniel Kahneman, *Thinking, Fast and Slow* (2011) -- prospective hindsight
- Chip Heath & Dan Heath, *Decisive* (2013) -- decision-making under uncertainty
- Amy Edmondson, *The Fearless Organization* (2018) -- psychological safety for surfacing elephants
