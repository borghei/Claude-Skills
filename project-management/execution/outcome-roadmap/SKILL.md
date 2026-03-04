---
name: outcome-roadmap
description: Outcome roadmap expert that transforms output-based feature lists into outcome-driven roadmaps with measurable impact.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-03-04
  python-tools: roadmap_transformer.py
  tech-stack: outcome-roadmap, product-strategy, now-next-later
---

# Outcome Roadmap Expert

## Overview

Transform output-based roadmaps ("build feature X") into outcome-driven roadmaps ("enable customers to achieve Y") that align teams around impact rather than deliverables. This skill uses the "so what?" technique and Now/Next/Later framing to create roadmaps that communicate strategy, not just plans.

### When to Use

- **Roadmap Refresh** -- Existing roadmap is a feature list and stakeholders keep asking "why are we building this?"
- **Strategic Planning** -- Translating company objectives into team-level roadmap items.
- **Stakeholder Communication** -- Need to explain product direction to executives, sales, or customers in outcome terms.
- **Quarterly Planning** -- Converting backlog items into outcome-driven initiatives.

## The Problem with Output Roadmaps

Output roadmaps list features and dates: "Q2: Build advanced search. Q3: Launch mobile app. Q4: Add integrations."

They create three problems:

1. **False precision** -- Dates promise certainty that does not exist. When dates slip, trust erodes.
2. **Misaligned teams** -- Engineers optimize for shipping features. Product optimizes for impact. An output roadmap makes these goals invisible to each other.
3. **Lost strategic context** -- Six months later, nobody remembers why "advanced search" was important. The feature ships, but the problem it was meant to solve may have changed.

## The Outcome Roadmap Framework

### Transformation Formula

Every initiative transforms from output to outcome using this format:

```
"Enable [customer segment] to [desired customer outcome] so that [business impact]"
```

**Example:**
- Output: "Build advanced search"
- Outcome: "Enable power users to find relevant products in under 5 seconds so that conversion rates increase by 20%"

The outcome version tells everyone:
- **Who** benefits (power users)
- **What** changes for them (find products faster)
- **Why** it matters to the business (conversion)

### The "So What?" Test

When you have a feature and need to find the outcome, keep asking "so what?" until you reach real customer or business value.

```
"Build advanced search"
  -> So what?
"Users can find products faster"
  -> So what?
"They spend less time browsing and more time buying"
  -> So what?
"Conversion rate increases, reducing acquisition cost per sale"
```

The last answer is the outcome. Work backward to write the outcome statement.

### Time Horizons: Now / Next / Later

Replace quarterly dates with commitment levels:

| Horizon | Meaning | Commitment Level | Detail Level |
|---------|---------|-----------------|--------------|
| **Now** | Currently in progress or starting within 2 weeks | High -- team is assigned, scope is defined | Detailed outcome statements, success metrics, dependencies |
| **Next** | Planned for the near future (1-3 months) | Medium -- direction is set, scope is flexible | Outcome statements with draft metrics |
| **Later** | On the radar but not yet committed (3-6 months) | Low -- strategic intent only | Problem statements or opportunity areas |

**Why this works:** "Now" items have enough certainty for detail. "Later" items do not. Forcing detail on uncertain items creates false precision and wastes planning effort.

## Workflow

1. **Gather** -- Collect current roadmap items (features, projects, initiatives).
2. **Transform** -- Run each through `scripts/roadmap_transformer.py` or apply the "so what?" test manually.
3. **Categorize** -- Place items in Now/Next/Later based on commitment level, not calendar dates.
4. **Add Metrics** -- Define how you will measure success for each outcome.
5. **Identify Dependencies** -- What must be true for each outcome to be achievable?
6. **Review** -- Walk stakeholders through the outcome roadmap and get alignment.

## Output Structure

For each initiative, the transformed roadmap includes:

1. **Original Initiative** -- What was on the old roadmap.
2. **Outcome Statement** -- "Enable [segment] to [outcome] so that [impact]."
3. **Success Metrics** -- 2-3 measurable indicators of progress.
4. **Dependencies** -- Technical, organizational, or market prerequisites.
5. **Strategic Context** -- How this connects to company objectives or OKRs.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `roadmap_transformer.py` | Transform output initiatives to outcomes | `python scripts/roadmap_transformer.py --input roadmap.json` |
| `roadmap_transformer.py` | Run demo transformation | `python scripts/roadmap_transformer.py --demo` |

## References

- `references/outcome-roadmap-guide.md` -- Detailed guide with comparison, formulas, and stakeholder strategies
- `assets/outcome_roadmap_template.md` -- Roadmap document template with Now/Next/Later sections
