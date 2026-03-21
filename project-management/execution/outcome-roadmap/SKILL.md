---
name: outcome-roadmap
description: >
  Transforms output-based feature lists into outcome-driven roadmaps with measurable impact
  using Now/Next/Later framing and the "so what?" technique.
  Use when converting a feature-list roadmap into outcome-driven format, communicating product
  strategy to executives or customers, running quarterly planning, or aligning teams around
  impact rather than deliverables.
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

The agent transforms output-based roadmaps ("build feature X") into outcome-driven roadmaps ("enable customers to achieve Y") using the "so what?" technique and Now/Next/Later framing. It produces roadmaps that communicate strategy and measurable impact, not just feature lists and dates.

## Workflow

### 1. Gather Current Roadmap Items

The agent collects the existing roadmap -- features, projects, or initiatives -- in any format (list, spreadsheet, JSON, or prose).

**Validation checkpoint:** Each item must have at least a name and a brief description. If items are just feature names with no context, the agent asks for the problem each feature is meant to solve.

### 2. Transform Each Item

The agent applies the transformation formula:

```
"Enable [customer segment] to [desired customer outcome] so that [business impact]"
```

For each feature, the agent uses the "so what?" chain to find the real outcome:

```
"Build advanced search"
  -> So what? "Users can find products faster"
  -> So what? "They spend less time browsing and more time buying"
  -> So what? "Conversion rate increases, reducing acquisition cost per sale"
```

The last answer is the outcome. The agent works backward to write the outcome statement:

**Output:** "Enable power users to find relevant products in under 5 seconds so that conversion rates increase by 20%"

**Validation checkpoint:** Every transformed item must answer Who benefits, What changes for them, and Why it matters to the business.

### 3. Categorize into Now / Next / Later

| Horizon | Meaning | Commitment | Detail Level |
|---------|---------|-----------|--------------|
| **Now** | In progress or starting within 2 weeks | High -- team assigned, scope defined | Full outcome statements, success metrics, dependencies |
| **Next** | Planned for 1-3 months | Medium -- direction set, scope flexible | Outcome statements with draft metrics |
| **Later** | On the radar, 3-6 months | Low -- strategic intent only | Problem statements or opportunity areas |

**Validation checkpoint:** "Later" items should NOT have detailed metrics or specific solutions. Forcing detail on uncertain items creates false precision.

### 4. Add Success Metrics

For each Now and Next item, the agent defines 2-3 measurable indicators:

- **Primary metric:** Directly measures the desired outcome
- **Secondary metric:** Captures a different dimension of success
- **Counter-metric:** Prevents perverse optimization (optional for Next items)

### 5. Identify Dependencies

For each item, the agent documents:
- Technical prerequisites (APIs, infrastructure, data)
- Organizational prerequisites (team capacity, stakeholder buy-in)
- Market prerequisites (customer demand signal, competitive timing)

### 6. Review with Stakeholders

The agent produces a stakeholder-ready roadmap document for alignment review.

**Validation checkpoint:** Walk stakeholders through the outcome roadmap. If anyone asks "but when exactly will this ship?", redirect to commitment levels -- Now items have dates, Later items do not.

## Example: Roadmap Transformation

**Input (output-based roadmap):**
```json
{
  "initiatives": [
    {"name": "Build advanced search", "quarter": "Q2"},
    {"name": "Launch mobile app", "quarter": "Q3"},
    {"name": "Add Slack integration", "quarter": "Q3"},
    {"name": "Redesign dashboard", "quarter": "Q4"}
  ]
}
```

```bash
$ python scripts/roadmap_transformer.py --input roadmap.json

Outcome Roadmap Transformation
==============================

NOW (In Progress):
  Original: "Build advanced search"
  Outcome: "Enable power users to find relevant products in under 5 seconds
            so that conversion rates increase by 20%"
  Metrics:
    - Search-to-purchase conversion: 12% -> 15%
    - Avg search time: 18s -> 5s
    - Counter: Maintain search result relevance score above 0.8
  Dependencies: Elasticsearch cluster upgrade, product taxonomy cleanup

NEXT (1-3 Months):
  Original: "Launch mobile app"
  Outcome: "Enable field sales reps to close deals on-site so that
            average deal cycle shortens by 30%"
  Metrics:
    - Mobile-originated deals: 0% -> 15% of total
    - Avg deal close time: 14 days -> 10 days
  Dependencies: API v2 completion, mobile auth infrastructure

  Original: "Add Slack integration"
  Outcome: "Enable teams to act on alerts without context-switching
            so that mean response time drops by 40%"
  Metrics:
    - Alert-to-action time: 25min -> 15min
    - Alerts resolved in Slack: 0% -> 60%
  Dependencies: Webhook infrastructure, Slack app approval

LATER (3-6 Months):
  Original: "Redesign dashboard"
  Problem area: Users report dashboard is overwhelming and they
                can't find the metrics that matter to their role.
  Strategic intent: Role-based views that surface relevant data,
                    reducing time-to-insight.
  Dependencies: User research (not yet started)
```

## Why Output Roadmaps Fail

Output roadmaps create three problems:

1. **False precision** -- Dates promise certainty that does not exist. When dates slip, trust erodes.
2. **Misaligned teams** -- Engineers optimize for shipping features. Product optimizes for impact. An output roadmap makes these goals invisible to each other.
3. **Lost context** -- Six months later, nobody remembers why "advanced search" was important. The feature ships, but the problem it solved may have changed.

The outcome roadmap solves these by anchoring every item to customer value and business impact, with commitment levels that match certainty.

## Output Structure

For each initiative, the transformed roadmap includes:

1. **Original Initiative** -- What was on the old roadmap
2. **Outcome Statement** -- "Enable [segment] to [outcome] so that [impact]"
3. **Success Metrics** -- 2-3 measurable indicators
4. **Dependencies** -- Technical, organizational, or market prerequisites
5. **Strategic Context** -- Connection to company objectives or OKRs

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `roadmap_transformer.py` | Transform output initiatives to outcomes | `python scripts/roadmap_transformer.py --input roadmap.json` |
| `roadmap_transformer.py` | Run demo transformation | `python scripts/roadmap_transformer.py --demo` |

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| All initiatives classified as "Later" | Quarter strings do not match expected format (e.g., "Q2 2026") or dates are far future | Verify `quarter` field uses "Q[1-4] YYYY" format; the tool uses current date to compute Now/Next/Later horizons |
| "So what?" chain produces vague outcomes | Team stopped the chain too early or did not reach business impact | Push through at least 3 "So what?" levels; the last answer should reference a business metric (revenue, retention, cost) |
| Stakeholders keep asking "when exactly will this ship?" | Commitment levels not communicated clearly, or stakeholders trained to expect dates | Redirect to Now/Next/Later commitment framework; Now items have dates, Next has direction, Later has intent only |
| Outcome statements all sound the same | Using the template formula mechanically without domain-specific context | Customize the "[customer segment]", "[desired outcome]", and "[business impact]" placeholders with real data |
| Roadmap has too many "Now" items | Team not making hard prioritization choices, or everything feels urgent | Enforce a cap: maximum 2-3 Now items at any time; use `prioritization-frameworks/` to rank competing priorities |
| Demo mode works but custom input fails | JSON schema mismatch: missing `initiatives` key or missing required fields per item | Each initiative needs `title`, `description`, `quarter`, and `type` (feature/improvement/infrastructure) |

## Success Criteria

- Every roadmap initiative has an outcome statement answering Who benefits, What changes, and Why it matters
- Now items have full outcome statements with 2-3 measurable success metrics and dependencies documented
- Next items have outcome statements with draft metrics (no counter-metrics required)
- Later items have problem statements and strategic intent only (no false-precision metrics or solutions)
- Stakeholders understand and accept the commitment level framework (Now = high, Next = medium, Later = low)
- Roadmap is reviewed quarterly with stakeholders to validate horizon placement
- Output-to-outcome transformation reduces "when will it ship?" questions by 50%+

## Scope & Limitations

**In Scope:**
- Transforming output-based feature lists into outcome-driven roadmap items
- Now/Next/Later horizon classification based on quarter-to-current-date distance
- "So what?" chain generation for each initiative
- Strategic question prompts and metric suggestions by initiative type (feature, improvement, infrastructure)
- Markdown and text report output with grouped-by-horizon formatting

**Out of Scope:**
- Feature prioritization or scoring (see `execution/prioritization-frameworks/`)
- Detailed sprint-level planning or capacity allocation (see `scrum-master/`)
- Product strategy or vision definition (outcome roadmaps communicate strategy, they do not create it)
- Dependency management across teams (see `program-manager/`)

**Important Caveats:**
- Outcome roadmaps require a cultural shift. Teams accustomed to date-driven feature lists need coaching on commitment levels.
- The tool generates outcome statement templates, not finished outcomes. The templates must be filled in with real customer and business data.
- Later items intentionally lack detailed metrics. Adding false precision to uncertain items undermines the roadmap's credibility.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `execution/brainstorm-okrs/` | Receives from | OKR key results become success metrics for Now/Next roadmap items |
| `execution/prioritization-frameworks/` | Receives from | RICE/ICE scores inform which initiatives move to Now vs. Next vs. Later |
| `execution/create-prd/` | Feeds into | Now items with validated outcomes become PRD candidates |
| `discovery/brainstorm-experiments/` | Receives from | Experiment results validate demand for Next/Later items, promoting them to Now |
| `senior-pm/` | Receives from | Portfolio strategic priorities influence roadmap horizon placement |
| `scrum-master/` | Receives from | Sprint capacity data determines how many Now items the team can support |

## Tool Reference

### roadmap_transformer.py

Transforms output-based roadmap initiatives into outcome-driven format with horizon classification, strategic questions, and metric suggestions.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--input` | string | (required, mutually exclusive with --demo) | Path to JSON file containing roadmap initiatives |
| `--demo` | flag | off | Run transformation on built-in demo data (5 initiatives) |
| `--format` | choice | `text` | Output format: `text`, `json`, or `markdown` |
| `--output` | string | stdout | Output file path; if omitted, prints to stdout |

**Supported initiative types:** `feature`, `improvement`, `infrastructure`

## References

- `references/outcome-roadmap-guide.md` -- Detailed guide with comparison, formulas, and stakeholder strategies
- `assets/outcome_roadmap_template.md` -- Roadmap document template with Now/Next/Later sections
