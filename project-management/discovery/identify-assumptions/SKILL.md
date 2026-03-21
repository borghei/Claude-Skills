---
name: identify-assumptions
description: Assumption mapping expert that identifies, categorizes, and prioritizes product assumptions across 4-8 risk categories using devil's advocate analysis.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-03-04
  python-tools: assumption_tracker.py
  tech-stack: assumption-mapping, risk-matrix, teresa-torres, continuous-discovery
---

# Assumption Mapping Expert

## Overview

Systematically identify, categorize, and prioritize the assumptions underlying your product decisions. This skill extends Teresa Torres' four risk categories with four additional categories for new products, and uses a devil's advocate approach from PM, Designer, and Engineer perspectives to surface hidden assumptions.

### When to Use

- After ideation, before committing to build.
- When a product decision "feels right" but has not been validated.
- When the team disagrees on risk or priority -- assumptions make disagreements explicit.
- Before designing experiments -- test the riskiest assumptions first.

## Risk Categories

### Core 4 Categories (Existing Products)

These four categories come from Teresa Torres' *Continuous Discovery Habits* and cover the primary risks for features within an established product:

| Category | Question It Answers | Example Assumption |
|----------|--------------------|--------------------|
| **Value** | Will customers want this? | "Users will prefer AI-generated summaries over manual note-taking." |
| **Usability** | Can customers figure out how to use it? | "Users will understand the drag-and-drop interface without a tutorial." |
| **Viability** | Can the business sustain this? | "The feature will generate enough upgrades to justify the engineering cost." |
| **Feasibility** | Can we build this? | "Our current infrastructure can handle real-time processing at scale." |

### Extended 8 Categories (New Products)

For new products, four additional risk categories become critical:

| Category | Question It Answers | Example Assumption |
|----------|--------------------|--------------------|
| **Ethics** | Should we build this? Are there unintended harms? | "Collecting location data will not create privacy concerns for our target segment." |
| **Go-to-Market** | Can we reach and acquire customers? | "Our target segment actively searches for solutions on Google, making SEO viable." |
| **Strategy & Objectives** | Does this align with where we want to go? | "Entering the SMB market will not dilute our enterprise positioning." |
| **Team** | Do we have the right people and skills? | "Our team can learn the required ML skills within the project timeline." |

## Methodology

### Phase 1: Devil's Advocate Assumption Surfacing

For each product idea or decision, adopt three adversarial perspectives:

**PM Devil's Advocate**
"I challenge whether this is worth building."
- Is there real demand, or are we projecting our own preferences?
- Will this move the metric we care about?
- Can we sustain this economically?
- Does this align with strategy, or is it a distraction?

**Designer Devil's Advocate**
"I challenge whether users will actually use this."
- Will users discover this feature?
- Can they complete the task without help?
- Does this add complexity that hurts the overall experience?
- Are we designing for edge cases and assuming they are common?

**Engineer Devil's Advocate**
"I challenge whether we can build and maintain this."
- Do we have the technical skills and infrastructure?
- What are the hidden dependencies and integration risks?
- Can this scale if it succeeds?
- What is the ongoing maintenance burden?

### Phase 2: Categorize Each Assumption

For each assumption surfaced, assign:

| Field | Options |
|-------|---------|
| **Description** | Clear, specific statement of what must be true |
| **Risk Category** | Value / Usability / Viability / Feasibility / Ethics / Go-to-Market / Strategy / Team |
| **Confidence** | High (we have strong evidence) / Medium (some evidence, not conclusive) / Low (gut feeling or no evidence) |
| **Impact** | 1-10 scale (if this assumption is wrong, how bad is it?) |

### Phase 3: Prioritize Using Impact x Risk Matrix

Calculate a risk score for each assumption:

```
Risk Score = Impact x (1 - Confidence)
```

Where confidence maps to: High = 0.8, Medium = 0.5, Low = 0.2

| Impact | Confidence | Risk Score | Meaning |
|--------|-----------|------------|---------|
| 9 | Low (0.2) | 7.2 | Critical -- test immediately |
| 9 | High (0.8) | 1.8 | Important but well-understood |
| 3 | Low (0.2) | 2.4 | Low priority |
| 3 | High (0.8) | 0.6 | Ignore |

### Phase 4: Classify into Quadrants

Place each assumption on a 2x2 matrix:

```
                    HIGH IMPACT
                        |
     Proceed with       |     Test Now
     Confidence         |     (highest priority)
                        |
  ──────────────────────┼──────────────────────
                        |
     Defer              |     Investigate
     (low priority)     |     (may be important)
                        |
                    LOW IMPACT

         LOW RISK ◄─────┼─────► HIGH RISK
```

| Quadrant | Impact | Risk | Action |
|----------|--------|------|--------|
| **Test Now** | High | High | Design an experiment immediately |
| **Proceed** | High | Low | Move forward with monitoring |
| **Investigate** | Low | High | Gather more data, may upgrade to Test Now |
| **Defer** | Low | Low | Accept the risk, revisit if context changes |

### Phase 5: Suggest Tests

For each "Test Now" assumption, recommend a validation approach:

| Assumption Type | Suggested Test Methods |
|----------------|----------------------|
| Value assumptions | Customer interviews, fake door test, landing page test |
| Usability assumptions | Usability test (5 users), prototype walkthrough |
| Viability assumptions | Financial modeling, pricing experiment, unit economics analysis |
| Feasibility assumptions | Technical spike, proof of concept, architecture review |
| Ethics assumptions | Ethics review board, user consent study, regulatory consultation |
| Go-to-Market assumptions | Channel experiment, SEO keyword test, paid ad test |
| Strategy assumptions | Strategy review with leadership, competitive analysis |
| Team assumptions | Skills assessment, hiring timeline analysis, training feasibility |

## Python Tool: assumption_tracker.py

Track and prioritize assumptions using the CLI tool:

```bash
# Run with demo data
python3 scripts/assumption_tracker.py --demo

# Run with custom input
python3 scripts/assumption_tracker.py input.json

# Output as JSON
python3 scripts/assumption_tracker.py input.json --format json
```

### Input Format

```json
{
  "assumptions": [
    {
      "description": "Users will prefer AI summaries over manual notes",
      "category": "value",
      "confidence": "low",
      "impact": 9
    }
  ]
}
```

### Output

Sorted by risk priority with quadrant classification and suggested actions.

See `scripts/assumption_tracker.py` for full documentation.

## Output Format

### Assumption Registry

| # | Assumption | Category | Confidence | Impact | Risk Score | Quadrant |
|---|-----------|----------|-----------|--------|-----------|----------|
| 1 | ... | Value | Low | 9 | 7.2 | Test Now |
| 2 | ... | Feasibility | Medium | 8 | 4.0 | Test Now |
| 3 | ... | Usability | High | 7 | 1.4 | Proceed |
| 4 | ... | GTM | Low | 3 | 2.4 | Investigate |

### Action Plan for "Test Now" Assumptions

For each assumption in the Test Now quadrant, document:
- Assumption description
- Why it is high risk
- Suggested validation method
- Owner and timeline

Use `assets/assumption_map_template.md` for the full template.

## Integration with Other Discovery Skills

- Use `brainstorm-ideas/` to generate ideas whose assumptions you will map.
- Feed "Test Now" assumptions into `brainstorm-experiments/` for experiment design.
- Run `pre-mortem/` to catch risks that assumption mapping might miss (especially elephants).

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| All assumptions classified as "Test Now" | Impact scores inflated or confidence levels consistently set to "low" | Calibrate impact scoring with team; use relative ranking (force distribution across quadrants) |
| Validation fails with category error | Category string does not match valid set exactly | Use lowercase: `value`, `usability`, `viability`, `feasibility`, `ethics`, `gtm`, `strategy`, `team` |
| Risk scores cluster around the same value | Impact and confidence values lack variance across assumptions | Use the full 1-10 impact scale; challenge the team to differentiate high vs. medium vs. low confidence with evidence |
| Team generates fewer than 10 assumptions | Devil's Advocate perspectives not applied systematically | Run all three perspectives (PM, Designer, Engineer) independently before combining; use the prompts in Phase 1 |
| "Defer" quadrant is empty | All assumptions scored as high impact, or low-impact assumptions not captured | Include operational and edge-case assumptions; not every assumption is existential |
| Suggested tests are too generic | Tool uses category-level test suggestions, not assumption-specific ones | Use the category suggestion as a starting point; tailor the test method using `brainstorm-experiments/` skill |
| Assumptions not updated after experiments | No feedback loop from experiment results back to assumption tracker | Re-run `assumption_tracker.py` with updated confidence levels after each experiment completes |

## Success Criteria

- All product decisions have at least 8-15 explicit assumptions documented before build commitment
- Every "Test Now" assumption has an assigned owner, validation method, and timeline
- Risk scores are calculated consistently using the Impact x (1 - Confidence) formula
- Assumptions are re-scored after each validation experiment (confidence levels update)
- At least 80% of "Test Now" assumptions are validated or invalidated before major build decisions
- Assumption map is reviewed and updated at every product discovery cycle (weekly or bi-weekly)
- The team can articulate the top 3 riskiest assumptions for any active initiative

## Scope & Limitations

**In Scope:**
- Systematic assumption identification using PM/Designer/Engineer devil's advocate perspectives
- 8-category risk classification (Value, Usability, Viability, Feasibility, Ethics, Go-to-Market, Strategy, Team)
- Quantitative risk scoring using Impact x (1 - Confidence) formula
- Quadrant classification (Test Now, Proceed, Investigate, Defer) with suggested validation methods
- Assumption registry with priority sorting and action plan generation

**Out of Scope:**
- Running validation experiments (see `brainstorm-experiments/` skill)
- Product strategy or roadmap decisions (see `execution/outcome-roadmap/`)
- Technical feasibility deep-dives or architecture reviews (see `engineering/` skills)
- Financial modeling for viability assumptions (see `finance/` domain skills)

**Important Caveats:**
- Confidence levels (high/medium/low) map to fixed numeric values (0.8/0.5/0.2). This is a simplification; real confidence is continuous.
- The quadrant threshold for "high impact" is set at 7/10. Adjust this threshold for your risk tolerance.
- Assumption mapping is most effective when done collaboratively (Product Trio), not by a single person.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `brainstorm-ideas/` | Receives from | Ideas generated become the subjects whose assumptions are mapped |
| `brainstorm-experiments/` | Feeds into | "Test Now" assumptions become hypotheses for experiment design |
| `pre-mortem/` | Complements | Pre-mortem catches risks that assumption mapping may miss (especially elephants) |
| `execution/create-prd/` | Feeds into | Validated assumptions populate the PRD Assumptions section (Section 7) |
| `execution/brainstorm-okrs/` | Feeds into | Viability assumptions inform OKR key result selection and confidence levels |
| `senior-pm/` | Feeds into | High-impact assumptions feed into portfolio risk registers |

## Tool Reference

### assumption_tracker.py

Tracks, scores, and prioritizes product assumptions using an Impact x Risk matrix with quadrant classification.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `input_file` | positional | (optional) | Path to JSON file with assumptions array |
| `--demo` | flag | off | Run with built-in sample data (8 assumptions across all categories) |
| `--format` | choice | `text` | Output format: `text` or `json` |

**Input fields per assumption:**
- `description` (required): Clear statement of what must be true
- `category` (required): One of `value`, `usability`, `viability`, `feasibility`, `ethics`, `gtm`, `strategy`, `team`
- `confidence` (required): One of `high`, `medium`, `low`
- `impact` (required): Integer 1-10

## References

- Teresa Torres, *Continuous Discovery Habits* (2021)
- David J. Bland & Alexander Osterwalder, *Testing Business Ideas* (2019)
- Ash Maurya, *Running Lean* (2012)
- Marty Cagan, *Inspired* (2018)
