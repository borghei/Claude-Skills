# Project Management Skills - Claude Code Guidance

This guide covers the **66 production-ready project management skills** organized across role-based, discovery, execution, career, integration, strategy-frameworks (Tier 3), and GTM (Tier 3) domains. PM is the most-used domain in this library.

## PM Skills Overview

**Available Skills (70 total):**

**Tier 3 additions (May 2026, 12 new skills):**

### Strategy frameworks — `strategy-frameworks/` (5 NEW)
- **business-model-canvas/** - Osterwalder 9-block canvas + validator (1 tool)
- **lean-canvas/** - Ash Maurya startup canvas + validator (1 tool)
- **swot-analysis/** - SWOT + TOWS matrix + scoring (1 tool)
- **porters-five-forces/** - Industry analysis + strategy translation (1 tool)
- **ansoff-matrix/** - Growth quadrants + investment mix (1 tool)

### Go-to-market — `gtm/` (2 NEW)
- **gtm-strategy/** - Full GTM: ICP, motion, channels, messaging, sequence (1 tool)
- **ideal-customer-profile/** - 8-dimension ICP + qualification rubric (1 tool)

### Discovery additions (2 NEW)
- **discovery/opportunity-solution-tree/** - Teresa Torres OST + validator (1 tool)
- **discovery/metrics-dashboard/** - Dashboard architect + audit (1 tool)

### Execution additions (3 NEW)
- **execution/stakeholder-map/** - Power × Interest + engagement plan (1 tool)
- **execution/test-scenarios/** - 7-category coverage generator (1 tool)
- **execution/sprint-plan/** - Capacity math + commit discipline (1 tool)

**AI-era delivery additions (September 2026, 2 new skills):**

### AI prototyping and agent delivery (2 NEW)
- **discovery/ai-prototyping/** - Idea → AI-generated prototype → user validation → engineering handoff; prototype-vs-spec by uncertainty type, F0-F4 fidelity ladder, handoff gate (2 tools: `prototype_plan.py`, `prototype_handoff_checker.py`)
- **execution/agents-in-the-team/** - Delivery when AI coding/ops agents take tickets; delegation bands + hard blocks, agent-ready tickets, human accountability, review-capacity gate, DORA + agent metrics by author type, security, rollout (2 tools: `agent_delegation_scorer.py`, `agent_delivery_metrics.py`)


### Role-Based Skills (10)
1. **senior-pm/** - Portfolio management, stakeholder mapping, EMV risk analysis, executive reporting
2. **scrum-master/** - Sprint analytics, team health, velocity forecasting, capacity planning
3. **delivery-manager/** - Release management, deployment coordination, incident response
4. **program-manager/** - Multi-project coordination, dependency management
5. **agile-coach/** - Agile transformation, team coaching, maturity assessment
6. **jira-expert/** - Jira administration, workflows, JQL, automation
7. **confluence-expert/** - Documentation, knowledge management, collaboration
8. **atlassian-admin/** - Atlassian suite administration and configuration
9. **atlassian-templates/** - Ready-to-use templates for Jira and Confluence
10. **sprint-retrospective/** - Data-driven sprint retrospectives

### Integration Skills (3)
11. **linear-expert/** - Linear administration, GraphQL queries, Jira → Linear migration
12. **notion-pm/** - Notion DBs for PRDs/OKRs/Roadmap/Decisions, REST API patterns
13. **productboard-expert/** ★ NEW - Productboard administration, Insight inbox triage, Driver scoring, REST API

### Discovery Skills (8) — `discovery/`
14. **brainstorm-ideas/** - Product Trio ideation, Opportunity Solution Trees
15. **brainstorm-experiments/** - Lean experiment design, XYZ hypotheses, pretotyping
16. **identify-assumptions/** - Assumption mapping across 4-8 risk categories
17. **pre-mortem/** - Tiger/Paper Tiger/Elephant risk classification
18. **interview-synthesis/** - Customer interview → opportunity solution tree (Torres)
19. **customer-interview-script/** ★ NEW - How to RUN a discovery interview (Portigal, Fitzpatrick)
20. **value-proposition-canvas/** ★ NEW - Strategyzer VPC (Customer Profile + Value Map)
21. **jtbd-workshop/** ★ NEW - Full Jobs-To-Be-Done workshop (Christensen, Ulwick, Moesta)

### Execution Skills (29) — `execution/`
22. **create-prd/** - 8-section PRD scaffolding with problem framing canvas and working backwards PR
23. **prfaq/** - Amazon Working Backwards PR/FAQ as standalone skill
24. **ai-feature-prd/** ★ NEW - PRDs for AI/ML features (eval, guardrails, model selection, cost)
25. **pricing-prd/** ★ NEW - Pricing experiments and pricing-page PRDs (tactical)
26. **product-vision/** ★ NEW - Vision document (Pichler, Moore, Raskin, Cagan, Amazon WB)
27. **brainstorm-okrs/** - OKR brainstorming and validation (Wodtke framework)
28. **north-star-metric/** - NSM + input metric tree definition
29. **quarterly-planning/** ★ NEW - Full Q1 cycle (kickoff → mid-Q → close) above OKRs
30. **outcome-roadmap/** - Output → outcome roadmap transformation
31. **roadmap-communication/** - Exec/customer/internal roadmap variants
32. **prioritization-frameworks/** - 9-framework reference with multi-scorer
33. **backlog-refinement/** - INVEST + DoR/DoD + splitting playbook
34. **story-splitting/** - 9 vertical slicing patterns (Lawrence)
35. **story-mapping/** - Jeff Patton user story mapping for release planning
36. **job-stories/** - JTBD discovery canvas and When/Want/So backlog format
37. **wwas/** - Why-What-Acceptance structured backlog items
38. **customer-feedback-triage/** ★ NEW - Inbound feedback → categorize → score → backlog (Kano + RICE)
39. **activation-funnel/** ★ NEW - AARRR funnel design + analyzer (12 real activation events)
40. **feature-flag-strategy/** ★ NEW - Phased rollouts, kill-switches, flag debt (Fowler taxonomy)
41. **cycle-time-analyzer/** - Flow metrics (lead time, cycle time, CFD, Little's Law)
42. **dependency-map/** - Cross-team dependency tracking + critical path
43. **status-update-generator/** - Weekly exec update from Jira/Linear data
44. **summarize-meeting/** - Structured meeting summaries with action items
45. **daci-framework/** - DACI decision facilitation and governance
46. **beta-program/** - Closed beta playbook
47. **launch-playbook/** - Internal + external launch coordination
48. **post-mortem/** ★ NEW - Blameless incident RCA (Google SRE, Allspaw, Dekker)
49. **release-notes/** - Release notes generation from tickets/changelogs
50. **eol-communication/** - End-of-life product messaging and sunset communication

### Career Skills (4) — `career/`
51. **pm-interview-prep/** - APM/PM/Sr PM/Group PM interview rubrics + frameworks
52. **pm-career-ladder/** - Rubrics, growth plans, promo packets
53. **pm-onboarding/** - 30-60-90 day plan for new PMs
54. **pm-1on1s/** - 1:1 templates by partner type (EM, designer, IC, manager)

**Key Features:**
- **Atlassian MCP Server** integration for direct Jira/Confluence operations
- **Linear + Notion** integration patterns (GraphQL + REST)
- **15+ Python CLI tools** across role-based, discovery, execution, career
- **Shared output schema** (`--format json|markdown|mermaid|confluence|notion|linear`) — see `SHARED_OUTPUT_SCHEMA.md`
- **Worked examples** in `examples/` showing end-to-end flows
- **Role-based Quick Start** in `README.md` from APM → CPO

## Shared Output Format Schema

All PM Python tools follow `SHARED_OUTPUT_SCHEMA.md`:

```bash
python <tool>.py --format <json|markdown|mermaid|confluence|notion|linear> [--output file]
```

When generating outputs for a PM artifact, always consider which format the consumer expects:
- **json** for machine pipelines (CI, MCP servers, agents)
- **markdown** for GitHub PRs/READMEs (default)
- **mermaid** for visual diagrams (story maps, roadmaps, dependency graphs, opportunity trees)
- **confluence** for Confluence pages via Atlassian MCP
- **notion** for Notion pages via API
- **linear** for Linear issues via API

## Atlassian MCP Integration

**Purpose:** Direct integration with Jira and Confluence via Model Context Protocol (MCP)

**Capabilities:**
- Create, read, update Jira issues
- Manage Confluence pages and spaces
- Automate workflows and transitions
- Generate reports and dashboards
- Bulk operations on issues

**Setup:** Atlassian's official **Rovo MCP Server** (Cloud only) -- remote endpoint `https://mcp.atlassian.com/v2/mcp`, OAuth 2.1 by default (API token if your org admin allows it). In Claude Code: `claude mcp add --transport http atlassian https://mcp.atlassian.com/v2/mcp`, then `/mcp` to authenticate. See [Get started](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/).

**Usage Pattern:** tools are called by the agent, not from a shell. Names are from Atlassian's [supported tools](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/supported-tools/) list as of September 2026 (your client may prefix them with the server name, e.g. `mcp__atlassian__createJiraIssue`):

| Task | Rovo MCP tool |
|------|---------------|
| Create / edit an issue | `createJiraIssue`, `editJiraIssue` |
| JQL search | `searchJiraIssuesUsingJql` |
| Transition an issue | `transitionJiraIssue` |
| Create / start / close a sprint | `manageJiraSprint` |
| Create / update a Confluence page | `createConfluenceContent`, `updateConfluenceContent` |
| CQL search | `searchConfluence` |

## Linear Integration (linear-expert/)

Linear's API is GraphQL-first. Common patterns:

```graphql
# List issues
query { issues(first: 50, filter: { state: { type: { eq: "started" } } }) {
  nodes { id identifier title priority assignee { name } }
}}

# Create issue
mutation { issueCreate(input: {
  teamId: "...", title: "...", description: "...", priorityLabel: "High"
}) { issue { id identifier url } } }
```

See `linear-expert/references/linear-graphql-patterns.md` for full library.

## Notion Integration (notion-pm/)

Notion API is REST. PM workflows center on DB-driven artifacts:

```bash
# Create a PRD page in the PRDs database
curl -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": { "type": "data_source_id", "data_source_id": "<prd-data-source-id>" },
    "properties": { ... },
    "children": [ <blocks from prd_scaffolder.py --format notion> ]
  }'
```

Resolve `<prd-data-source-id>` via `GET /v1/databases/<prd-db-id>` → `data_sources[].id` (Notion-Version 2025-09-03, as of September 2026).

See `notion-pm/references/notion-api-patterns.md` for full library.

## Skill-Specific Guidance

### Senior PM (`senior-pm/`)

**Focus:** Portfolio management, stakeholder mapping, risk analysis, executive reporting

**Python Tools:** `project_health_dashboard.py`, `risk_matrix_analyzer.py`, `resource_capacity_planner.py`, `stakeholder_mapper.py`

**Key Workflows:**
- Portfolio health assessment (three-tier analysis)
- Stakeholder mapping with Mendelow's Matrix
- Risk quantification with EMV analysis
- Executive report generation

### Scrum Master (`scrum-master/`)

**Focus:** Data-driven sprint analytics, team health, velocity forecasting, capacity planning

**Python Tools:** `velocity_analyzer.py`, `sprint_health_scorer.py`, `retrospective_analyzer.py`, `sprint_capacity_calculator.py`

**Key Workflows:**
- Sprint capacity calculation with ceremony overhead
- Velocity analysis with Monte Carlo forecasting
- Sprint health scoring across 6 dimensions
- Retrospective pattern analysis

### Discovery Skills (`discovery/`)

**Focus:** Product discovery workflows — ideation, experimentation, assumption mapping, risk analysis, interview synthesis

**Python Tools:** `experiment_designer.py`, `assumption_tracker.py`, `risk_categorizer.py`, `interview_synthesizer.py`, `prototype_plan.py`, `prototype_handoff_checker.py`

**Key Workflows:**
- Product Trio ideation (PM + Designer + Engineer perspectives)
- Lean experiment design with XYZ hypothesis format
- Assumption mapping with Impact × Risk prioritization
- Pre-mortem with Tiger/Paper Tiger/Elephant classification
- Customer interview → opportunity solution tree
- AI prototyping: prototype-vs-spec decision, fidelity plan with kill criteria, handoff gate (`ai-prototyping/`)

### Execution Skills (`execution/`)

**Focus:** PM execution artifacts — PRDs, OKRs, roadmaps, prioritization, refinement, flow metrics, status, launch, release

**Python Tools:** `prd_scaffolder.py`, `okr_validator.py`, `roadmap_transformer.py`, `prioritization_scorer.py`, `release_notes_generator.py`, `refinement_scorer.py`, `status_generator.py`, `metric_tree_builder.py`, `flow_metrics.py`, `dependency_graph.py`, `agent_delegation_scorer.py`, `agent_delivery_metrics.py`

**Key Workflows:**
- PRD generation with 8-section structure
- PR/FAQ Working Backwards
- OKR validation against SMART criteria
- Output→outcome roadmap transformation
- Multi-framework prioritization (RICE, ICE, Opportunity Score, MoSCoW, Weighted)
- Backlog refinement (INVEST, DoR/DoD, splitting)
- Flow metrics (Little's Law, CFD, aging WIP)
- Cross-team dependency mapping with critical path
- Weekly exec status update from issue data
- Beta + launch playbooks
- Release notes from tickets/changelogs
- Agents in the team: agent-eligibility scoring, review-capacity gate, human vs agent delivery metrics (`agents-in-the-team/`)

### Career Skills (`career/`) ★ NEW

**Focus:** PM career growth — interview prep, ladder rubrics, onboarding, 1:1s

**Key Workflows:**
- Interview prep across product sense, execution, strategy, behavioral (CIRCLES, AARM, STAR, Decode and Conquer)
- Career ladder rubrics from APM → CPO with gap analysis
- 30-60-90 day onboarding plan (Watkins, STARS)
- 1:1 templates per partner type (manager, EM, designer, IC)

### Integration Skills

**linear-expert/** - GraphQL-first, cycle/project/initiative hierarchy, Jira → Linear migration patterns
**notion-pm/** - DB-driven PM artifacts (PRDs DB, OKRs DB, Roadmap DB, Decisions DB), Notion API REST patterns

## Integration Patterns

### Pattern 1: Discovery → Execution → Delivery

```
brainstorm-ideas → identify-assumptions → brainstorm-experiments → pre-mortem
      ↓                                                                    ↓
create-prd → brainstorm-okrs → outcome-roadmap → prioritization-frameworks
      ↓
backlog-refinement → story-splitting → (build) → release-notes
      ↓
status-update-generator → (weekly exec comms)
```

### Pattern 2: Sprint Planning (Data-Driven)

```bash
python scrum-master/scripts/sprint_capacity_calculator.py team.json
python scrum-master/scripts/velocity_analyzer.py sprints.json
python execution/prioritization-frameworks/scripts/prioritization_scorer.py backlog.json --framework rice
python execution/cycle-time-analyzer/scripts/flow_metrics.py issues.json
# then, via the Atlassian Rovo MCP Server: manageJiraSprint (create "Sprint 23" on the team board)
```

### Pattern 3: Cross-Team Coordination

```bash
python execution/dependency-map/scripts/dependency_graph.py deps.json --format mermaid
python execution/daci-framework/...  # Document decision rights
python execution/status-update-generator/scripts/status_generator.py --format confluence
# then, via the Atlassian Rovo MCP Server: createConfluenceContent (space PROG, title "Weekly status")
```

### Pattern 4: Customer Discovery → Roadmap

```bash
python discovery/interview-synthesis/scripts/interview_synthesizer.py interviews.json --format mermaid
python discovery/identify-assumptions/scripts/assumption_tracker.py opportunities.json
python execution/north-star-metric/scripts/metric_tree_builder.py --nsm "QBR engagement"
python execution/outcome-roadmap/scripts/roadmap_transformer.py outputs.json
```

### Pattern 5: Push to Linear (instead of Jira)

```bash
python execution/prioritization-frameworks/scripts/prioritization_scorer.py backlog.json \
  --framework rice --format linear | linear-cli issues create-batch --team PROD
python execution/status-update-generator/scripts/status_generator.py issues.json \
  --format linear --output status.md
```

### Pattern 6: Push to Notion DB

```bash
python execution/create-prd/scripts/prd_scaffolder.py \
  --product-name "Shared Dashboards" --format notion --output prd.md
# Then post to Notion API via notion-pm/ patterns
```

## Career Track Usage Patterns

### Pattern: Interview Prep
```
career/pm-interview-prep/ → frame question type → use CIRCLES/AARM/STAR → practice with mocks
```

### Pattern: Promo Cycle
```
career/pm-career-ladder/ → assess against rubric → identify gaps → 90-day growth plan → promo packet
```

### Pattern: New PM Onboarding
```
career/pm-onboarding/ → 30-60-90 day plan → stakeholder mapping (senior-pm/) → first PRD (create-prd/)
```

## Additional Resources

- **Shared Output Schema:** `SHARED_OUTPUT_SCHEMA.md` (critical for consistent tool integration)
- **Worked Examples:** `examples/` (end-to-end scenarios)
- **Installation Guide:** `INSTALLATION_GUIDE.txt`
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`
- **Real-World Scenario:** `REAL_WORLD_SCENARIO.md`
- **PM Overview:** `README.md`
- **Main Documentation:** `../CLAUDE.md`

---

**Last Updated:** 2026-05-21
**Skills Deployed:** 54/54 PM skills production-ready
**Python Tools:** 15+ CLI tools
**Integrations:** Jira, Linear, Notion, Confluence, GitHub Projects, Atlassian MCP
**Career Track:** 4 skills (unique to this library — no competitor covers PM career growth)
