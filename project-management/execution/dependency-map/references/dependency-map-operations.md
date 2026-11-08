# Dependency Map Operations

> Read this when you need the operational detail: the dependency data model, slack/risk derivation, critical-path computation, the step-by-step weekly workflow, the tool flags, input/output JSON schemas, troubleshooting, and success criteria.

## The Dependency Model

A **dependency** has six attributes:

| Field | Required | Notes |
|-------|:--------:|-------|
| `id` | Yes | Stable identifier (e.g., `DEP-014`) |
| `from_team` | Yes | The team that NEEDS the work (the consumer/blocked party) |
| `to_team` | Yes | The team that OWES the work (the producer/blocker) |
| `description` | Yes | One sentence: what is needed |
| `needed_by` | Yes | ISO date when the consumer needs it |
| `expected_delivery` | Yes | ISO date when the producer expects to deliver |
| `status` | Yes | `not_started` / `in_progress` / `at_risk` / `blocked` / `done` |
| `criticality` | Optional | `critical` / `high` / `medium` / `low` (default `medium`) |
| `notes` | Optional | Free text context, links, decisions |

### Slack and Risk

For each dependency:

- **Slack** = `expected_delivery - needed_by`. Negative slack = the dependency is late or will be.
- **Risk** is derived from `status` and `slack`:
    - `done`: no risk
    - `blocked`: highest risk (work has stopped)
    - `at_risk` or `slack < 0`: high risk
    - `in_progress` with positive slack: medium
    - `not_started` more than 14 days before `needed_by`: low
    - `not_started` within 14 days of `needed_by`: high

### Critical Path

The **critical path** is the longest dependency chain through the program -- the sequence whose total duration determines the earliest possible completion. Any delay on the critical path delays the entire program. Any delay off it does not (until it consumes the slack and becomes critical).

This tool computes the critical path by building a directed graph from dependencies, ordering by `needed_by` dates, and identifying the chain of nodes with zero slack. The output lists the critical chain plus its near-critical sibling chains (slack < 7 days).

## Conway's Law and Recurring Dependencies

Melvin Conway, 1968: "Organizations which design systems are constrained to produce designs which are copies of the communication structures of these organizations."

Practical consequence for dependency mapping: if you find the same two teams generating dependencies every quarter, the org structure is the dependency. Three responses, in order of preference:

1. **Merge the teams** if the volume of dependencies justifies it.
2. **Create a permanent interface** (API contract, service-level agreement, scheduled sync) that reduces ad-hoc coordination.
3. **Add a permanent program manager** for the seam (see `program-manager/`).

## Workflow

1. **Inventory dependencies.** With each team's lead, list every cross-team need for the planning period. One sentence per dependency. Date both `needed_by` and `expected_delivery`.
2. **Populate the JSON.** Use the schema in `assets/dependency-template.json`.
3. **Run the analyzer.** `python scripts/dependency_graph.py --input deps.json --format markdown` for the full report.
4. **Generate the Mermaid graph.** `--format mermaid` -- paste into README, Notion, Confluence.
5. **Identify the critical path.** Review the critical path list. Every item on it gets a named owner and weekly status.
6. **Run the weekly sync.** Use `assets/weekly-sync-agenda.md`. Walk the critical path, then the at-risk items, then anything newly added.
7. **Update the JSON after every sync.** The map is only useful if it reflects current state. Stale maps are worse than no map.
8. **Quarterly review.** Look at recurring dependencies between the same two teams. If volume is high, consider Conway's Law responses.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `dependency_graph.py` | Compute critical path, render dependency graph, list risks | `python scripts/dependency_graph.py --input deps.json --format mermaid` |

Demo mode: `python scripts/dependency_graph.py --demo --format markdown` produces sample output without input.

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| Critical path is empty | All dependencies have generous slack (positive `expected_delivery - needed_by`) | Verify dates are realistic; ask teams whether their `expected_delivery` reflects current capacity |
| Same two teams appear in 60% of dependencies | Org structure is the dependency (Conway's Law) | Quarterly review; consider merging teams, adding a permanent interface, or adding a program manager |
| Map goes stale within 2 weeks | No clear update cadence; map lives in nobody's daily routine | Make the JSON the single source of truth; require update before the weekly sync |
| Dependencies modeled at task level become unmaintainable | Granularity too fine; dozens of items per team per sprint | Aggregate at the epic level; only model cross-team blocks, not within-team sequencing |
| Status field always reads `at_risk` for every dep | Teams use it as a generic "this is hard" signal | Define explicit thresholds for `at_risk`; require dates to back the label |
| Mermaid diagram unreadable with 30+ nodes | Too many dependencies on one diagram | Filter by criticality (`--criticality critical,high`) or by team |
| Critical-path item has no named owner | Owner field optional and skipped | Make the weekly sync require an owner for every critical-path dependency |

## Success Criteria

- Every cross-team dependency is captured in the JSON with all required fields.
- A weekly cross-team sync walks the critical path and at-risk dependencies.
- Mermaid dependency diagram is published in a shared location and updated weekly.
- Every critical-path dependency has a named owner and a weekly status.
- Recurring dependencies are reviewed quarterly for Conway's Law responses.
- The dependency JSON is the single source of truth; spreadsheets and side documents are retired.
- Map is updated before, not after, the weekly sync.

## Tool Reference

### dependency_graph.py

Computes critical path, lists risks, and renders the dependency graph from a JSON file of cross-team dependencies.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--input` | path | (required unless `--demo`) | JSON file with dependencies |
| `--demo` | flag | off | Use built-in demo data |
| `--format` | string | `markdown` | One of `json`, `markdown`, `mermaid`, `confluence`, `notion`, `linear` |
| `--output` | path | stdout | Output file path |
| `--criticality` | string | (all) | Comma-separated filter: `critical,high,medium,low` |
| `--team` | string (repeatable) | (none) | Filter to dependencies involving these team names |
| `--as-of` | ISO date | file `as_of`, else today | Reference date for risk calculations |

### Input JSON schema

```json
{
  "program": "Q3 Mobile Launch",
  "dependencies": [
    {
      "id": "DEP-001",
      "from_team": "Mobile",
      "to_team": "Platform",
      "description": "OAuth refresh token rotation API",
      "needed_by": "2026-06-15",
      "expected_delivery": "2026-06-10",
      "status": "in_progress",
      "criticality": "critical",
      "owner": "Alex Lee",
      "notes": "Blocking iOS auth refactor"
    }
  ]
}
```

### Output JSON schema (envelope per `SHARED_OUTPUT_SCHEMA.md`)

```json
{
  "schema": "pm/dependency-map/v1",
  "generated_at": "2026-05-21T00:00:00Z",
  "data": {
    "program": "Q3 Mobile Launch",
    "as_of": "2026-05-21",
    "summary": {
      "total_dependencies": 12,
      "done": 3, "blocked": 1, "at_risk": 2,
      "critical_path_length": 5
    },
    "critical_path": [ { "id": "DEP-001", "from_team": "...", "to_team": "...", "slack_days": 0 } ],
    "at_risk": [ ... ],
    "by_team_pair": [ { "from_team": "...", "to_team": "...", "count": 4 } ],
    "all_dependencies": [ ... ]
  }
}
```
