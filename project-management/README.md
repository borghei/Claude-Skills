# Project Management Skills Collection

**22 production-ready PM skills** spanning role-based expertise, product discovery, and execution frameworks — with 10 Python CLI tools and Atlassian MCP integration.

---

## Table of Contents

- [Installation](#installation)
- [Skills Catalog](#skills-catalog)
  - [Role-Based Skills (10)](#role-based-skills-10)
  - [Discovery Skills (4)](#discovery-skills-4)
  - [Execution Skills (8)](#execution-skills-8)
- [Python Tools](#python-tools)
- [Atlassian MCP Integration](#atlassian-mcp-integration)
- [Workflows](#workflows)
- [Success Metrics](#success-metrics)

---

## Installation

### Quick Install (Recommended)

```bash
# Install all PM skills
npx ai-agent-skills install borghei/Claude-Skills/project-management

# Install to Claude Code only
npx ai-agent-skills install borghei/Claude-Skills/project-management --agent claude

# Install to Cursor only
npx ai-agent-skills install borghei/Claude-Skills/project-management --agent cursor
```

### Install Individual Skills

```bash
# Role-based skills
npx ai-agent-skills install borghei/Claude-Skills/project-management/senior-pm
npx ai-agent-skills install borghei/Claude-Skills/project-management/scrum-master
npx ai-agent-skills install borghei/Claude-Skills/project-management/delivery-manager

# Discovery skills
npx ai-agent-skills install borghei/Claude-Skills/project-management/discovery/brainstorm-ideas
npx ai-agent-skills install borghei/Claude-Skills/project-management/discovery/pre-mortem

# Execution skills
npx ai-agent-skills install borghei/Claude-Skills/project-management/execution/create-prd
npx ai-agent-skills install borghei/Claude-Skills/project-management/execution/prioritization-frameworks
```

**Supported Agents:** Claude Code, Cursor, VS Code, Copilot, Goose, Amp, Codex

---

## Skills Catalog

### Role-Based Skills (10)

| Skill | Focus | Python Tools | Status |
|-------|-------|-------------|--------|
| **senior-pm** | Portfolio management, stakeholder mapping, risk analysis | 4 scripts | v2.0 |
| **scrum-master** | Sprint analytics, velocity forecasting, team health | 4 scripts | v2.0 |
| **delivery-manager** | Release management, deployment, incident response | — | v1.0 |
| **jira-expert** | Jira configuration, JQL, automation | — | v1.0 |
| **confluence-expert** | Documentation, knowledge management | — | v1.0 |
| **atlassian-admin** | Suite administration, user management | — | v1.0 |
| **atlassian-templates** | Ready-to-use Jira/Confluence templates | — | v1.0 |
| **agile-coach** | Agile transformation, team coaching | — | v1.0 |
| **program-manager** | Multi-project coordination, dependencies | — | v1.0 |
| **packaged-skills** | Bundled skill packages | — | v1.0 |

### Discovery Skills (4)

| Skill | Focus | Python Tool | Key Framework |
|-------|-------|-------------|---------------|
| **brainstorm-ideas** | Product ideation for new and existing products | — | Product Trio + Opportunity Solution Tree |
| **brainstorm-experiments** | Lean experiment design and validation | `experiment_designer.py` | XYZ Hypothesis (Savoia) |
| **identify-assumptions** | Assumption mapping and prioritization | `assumption_tracker.py` | Teresa Torres 4-8 risk categories |
| **pre-mortem** | Pre-launch risk analysis | `risk_categorizer.py` | Tiger/Paper Tiger/Elephant (Klein) |

**Discovery Flow:** Ideas → Assumptions → Experiments → Pre-Mortem → Build Decision

### Execution Skills (8)

| Skill | Focus | Python Tool | Key Framework |
|-------|-------|-------------|---------------|
| **create-prd** | PRD scaffolding and documentation | `prd_scaffolder.py` | 8-section PRD template |
| **brainstorm-okrs** | OKR brainstorming and validation | `okr_validator.py` | Wodtke "Radical Focus" |
| **outcome-roadmap** | Output→outcome roadmap transformation | `roadmap_transformer.py` | Now/Next/Later horizons |
| **prioritization-frameworks** | Multi-framework prioritization scoring | `prioritization_scorer.py` | RICE, ICE, Opportunity Score, MoSCoW, Weighted |
| **release-notes** | Release notes from tickets/changelogs | `release_notes_generator.py` | Category-based (features, fixes, breaking) |
| **summarize-meeting** | Structured meeting summaries | — | Action items + decisions + open questions |
| **job-stories** | JTBD backlog format | — | When/Want/So (Klement) |
| **wwas** | Why-What-Acceptance backlog format | — | Strategic context + observable outcomes |

---

## Python Tools

All 10 tools are CLI-first, standard library only, with `--help`, `--demo`, and `--format json|text` support.

```bash
# Stakeholder mapping
python senior-pm/scripts/stakeholder_mapper.py --demo

# Sprint capacity
python scrum-master/scripts/sprint_capacity_calculator.py --demo

# Experiment design
python discovery/brainstorm-experiments/scripts/experiment_designer.py --demo

# Assumption tracking
python discovery/identify-assumptions/scripts/assumption_tracker.py --demo

# Risk categorization
python discovery/pre-mortem/scripts/risk_categorizer.py --demo

# PRD generation
python execution/create-prd/scripts/prd_scaffolder.py --product-name "MyProduct" --objective "Improve onboarding"

# OKR validation
python execution/brainstorm-okrs/scripts/okr_validator.py --demo

# Roadmap transformation
python execution/outcome-roadmap/scripts/roadmap_transformer.py --demo

# Prioritization scoring
python execution/prioritization-frameworks/scripts/prioritization_scorer.py --demo --framework rice

# Release notes
python execution/release-notes/scripts/release_notes_generator.py --demo --product-name "MyProduct" --version "2.0"
```

---

## Atlassian MCP Integration

Direct integration with Jira and Confluence via Model Context Protocol:

```bash
# Create Jira issue
mcp__atlassian__create_issue project="PROJ" summary="New feature" type="Story"

# Transition issue
mcp__atlassian__transition_issue key="PROJ-123" status="In Progress"

# Create Confluence page
mcp__atlassian__create_page space="TEAM" title="Sprint Retrospective"

# Run JQL query
mcp__atlassian__search_issues jql="project = PROJ AND status = 'In Progress'"
```

---

## Workflows

### Discovery → Execution → Delivery

```
1. brainstorm-ideas     → Generate 15 ideas across PM/Design/Eng perspectives
2. identify-assumptions → Map and prioritize assumptions (Value/Usability/Viability/Feasibility)
3. brainstorm-experiments → Design lean experiments for riskiest assumptions
4. pre-mortem           → Tiger/Paper Tiger/Elephant risk analysis before build
5. create-prd           → Scaffold PRD with objectives, segments, value props
6. brainstorm-okrs      → Set quarterly OKRs aligned with product strategy
7. outcome-roadmap      → Transform feature list into outcome-driven roadmap
8. prioritization-frameworks → Score and rank with RICE/ICE/Opportunity Score
9. release-notes        → Generate user-facing release communication
```

### Sprint Execution (Data-Driven)

```
1. sprint_capacity_calculator.py → Calculate team capacity with ceremony overhead
2. velocity_analyzer.py          → Analyze velocity trends, Monte Carlo forecast
3. prioritization_scorer.py      → Score backlog items for sprint selection
4. sprint_health_scorer.py       → Assess sprint health across 6 dimensions
5. retrospective_analyzer.py     → Analyze retro patterns and action items
```

### Stakeholder-Aligned Delivery

```
1. stakeholder_mapper.py         → Map power/interest grid, generate comm plan
2. risk_categorizer.py           → Pre-mortem risk analysis for launch
3. release_notes_generator.py    → Draft release notes by category
4. delivery-manager/SKILL.md     → Release communication workflow
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Sprint Predictability | +40% improvement |
| Project On-Time Delivery | +25% improvement |
| Atlassian Operations Efficiency | +70% time savings |
| Documentation Findability | +60% improvement |
| Meeting Summary Quality | +50% consistency |
| Stakeholder Communication Coverage | 100% mapped |

---

**Last Updated:** March 2026
**Skills Deployed:** 22/22 PM skills production-ready
**Python Tools:** 10 CLI tools (standard library only)
**Integration:** Atlassian MCP Server for Jira/Confluence automation
