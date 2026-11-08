# Outcome Roadmap Workflow

> Read this when you are actually transforming a roadmap: the 6-step workflow with validation checkpoints, the "so what?" technique, the Now/Next/Later detail levels, a full worked example, why output roadmaps fail, the output structure, the tool flags, troubleshooting, and success criteria.

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

**Input (output-based roadmap):** "Build advanced search" (Q2), "Launch mobile app" (Q3),
"Add Slack integration" (Q3), "Redesign dashboard" (Q4).

**After the "so what?" pass (written by the PM; `roadmap_transformer.py` then checks it):**

```text

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

## Tool Reference

### roadmap_transformer.py

Places initiatives in Now/Next/Later and checks each is outcome-ready. It does not write outcomes.

| Flag | Default | Description |
|------|---------|-------------|
| `--input` / `--demo` | one required | JSON file with `initiatives`, or the built-in output-style roadmap (exits 1) |
| `--as-of` | earliest quarter in the file | Current quarter, e.g. `Q4 2026`; pass it for a live roadmap |
| `--format` | `text` | `text`, `json` or `markdown` |
| `--output` | stdout | Write to a file |

Per initiative: `title`, `description`, `quarter` ("Q3 2026"), `type` (`feature`, `improvement`, `infrastructure`), plus `outcome`, `metric {name, baseline, target}` and `counter_metric`.

Errors: more than 3 Now items; Now/Next item with no outcome, an outcome that starts with an output verb, no metric, or a metric missing baseline or target; unparseable quarter. Warnings: no "so that", Now item without counter-metric, quarter before `--as-of`.

Exit codes: 0 no errors, 1 errors found, 2 bad input.
