---
name: status-update-generator
description: >
  Generate weekly executive status updates from Jira/Linear data exports.
  Produces a structured "highlights / blockers / risks / asks / what's next"
  briefing in markdown, Confluence, Notion, Linear, JSON, or Mermaid.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: status_generator.py
  tech-stack: jira, linear, weekly-status, executive-reporting, sbnr, r-y-g
---
# Status Update Generator

## Overview

Weekly status updates eat 30-90 minutes of every PM's Friday afternoon and they almost always say the same thing in subtly different ways. This skill standardizes the artifact: pull tickets from Jira or Linear (or any JSON dump), and emit a structured update with five named sections -- Highlights, Blockers, Risks, Asks, What's Next -- plus a traffic-light status (Red / Yellow / Green) for the period. The structure follows **SBNR** (Status / Blockers / Next / Risks) and a condensed Amazon **6-pager** narrative for Highlights; the stoplight verdict follows classic R/Y/G reporting.

## Core Capabilities

- **Six-section template** — Header, Highlights, Blockers, Risks, Asks, What's Next, in a fixed order so exec readers scan in under 5 seconds (full section definitions in `references/status-structure-and-workflow.md`).
- **Traffic-light discipline** — Green / Yellow / Red rules plus anti-patterns (watermelon status, always-yellow, color creep).
- **Multi-format rendering** — `status_generator.py` emits all six SHARED_OUTPUT_SCHEMA formats: `markdown`, `confluence`, `notion`, `linear`, `json`, `mermaid`.
- **SBNR mapping** — compressed async-standup variant mapped to the weekly sections.

## When to Use

- **Weekly exec status update** -- the standard Friday/Monday cadence brief sent to a sponsor, VP, or steering committee.
- **Monthly board / leadership packet** -- aggregate four weekly updates into a monthly view.
- **Sprint review summary** -- end-of-sprint communication that travels outside the team.
- **Cross-team async standup** -- distributed teams where a written async update replaces a sync meeting.
- **Project kickoff status baseline** -- the first status update establishes the template and traffic-light baseline.

**When NOT to use:** real-time incident response (use `delivery-manager/` incident skills), deep retrospectives (use `sprint-retrospective/`), or one-to-one stakeholder reporting needing custom framing (use `roadmap-communication/`).

## Clarify First

Before generating the update, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Traffic-light verdict (R/Y/G)** — the human judgment the tool will not infer; sets the whole frame and must be defensible (prevents watermelon status)
- [ ] **Audience** — sponsor, VP, or steering committee (sets altitude and what belongs in Highlights vs Asks)
- [ ] **This period's wins + blockers with real numbers** — quantitative claims must come from telemetry, not ticket titles (fills Highlights and Blockers)
- [ ] **The asks** — the specific decisions or help you need from the reader this week (drives the Asks section)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

| Tool | Purpose | Command |
|------|---------|---------|
| `status_generator.py` | Generate a structured weekly status update | `python scripts/status_generator.py --input data.json --format markdown` |
| `status_generator.py --demo` | Inspect demo input and output formats | `python scripts/status_generator.py --demo --format markdown` |

The traffic-light status is a human judgment, not a calculation — set it and document the rationale. See `references/tool-and-troubleshooting.md` for flags and the input JSON shape.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/status-structure-and-workflow.md](references/status-structure-and-workflow.md)** — full definition of each of the six sections, R/Y/G rules and anti-patterns, SBNR shorthand mapping, and the 6-step authoring workflow. Read when writing or standardizing an update.
- **[references/status-update-style-guide.md](references/status-update-style-guide.md)** — voice, structural rules, traffic-light discipline, and 5 worked examples (Green / Yellow / Red across team types). Read when coaching writing quality or seeing full examples.
- **[references/red-flags.md](references/red-flags.md)** — warning signs and failure modes in status reporting practice. Read when an update process feels performative or untrusted.
- **[references/tool-and-troubleshooting.md](references/tool-and-troubleshooting.md)** — `status_generator.py` flags, input JSON shape, Mermaid output, troubleshooting table, and success criteria. Read when running the tool or diagnosing a problem.
- **[assets/weekly_status_template.md](assets/weekly_status_template.md)** — fill-in template matching the tool's input JSON structure. Use to draft an update by hand.

## Scope & Limitations

**In Scope:**
- Generating weekly executive status updates from structured input
- Five-section template (Highlights / Blockers / Risks / Asks / What's Next) with R/Y/G traffic light
- Output in all six SHARED_OUTPUT_SCHEMA formats (json, markdown, mermaid, confluence, notion, linear)
- Aggregating ticket data from Jira-shaped or Linear-shaped JSON dumps
- SBNR shorthand mapping for async standup variants

**Out of Scope:**
- Pulling data directly from Jira or Linear APIs (use the Atlassian MCP, Linear MCP, or `linear-expert/`/`jira-expert/` skills to export the JSON first)
- Sprint analytics or velocity calculation (use `../scrum-master/`)
- Incident communication or postmortems (use `delivery-manager/`)
- Long-form retrospective output (use `sprint-retrospective/`)
- Tailoring updates to multiple audiences in different framings (use `roadmap-communication/`)

**Important Caveats:**
- The traffic-light status is a human judgment. The tool will not infer it from ticket counts. Forcing automation here produces watermelon updates.
- Quantitative claims in Highlights ("latency down to 210ms") must come from real telemetry, not from the ticket title. The tool will not verify these.
- Status updates are most effective on a predictable cadence. A high-quality irregular update is worse than a mediocre regular one.

## Integration Points

| Integration | Direction | Description |
|-------------|-----------|-------------|
| `../jira-expert/` | Receives from | Jira JQL exports or MCP pulls feed the input JSON |
| `linear-expert/` | Receives from | Linear GraphQL exports feed the input JSON |
| `../senior-pm/` | Feeds into | Weekly updates aggregate into monthly portfolio reports; risks lift into the portfolio risk register |
| `../scrum-master/` | Pairs with | Sprint health scores supply the Highlights/Risks context |
| `roadmap-communication/` | Pairs with | Weekly status feeds the executive-variant roadmap narrative |
| `sprint-retrospective/` | Feeds into | Four weeks of status archives become retrospective input |
| `../program-manager/` | Feeds into | Cross-team status aggregation rolls up multiple team updates |
| `../delivery-manager/` | Pairs with | Release windows and incident references show up in Highlights and Risks |
