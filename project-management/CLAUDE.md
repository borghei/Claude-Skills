# Project Management Skills - Claude Code Guidance

This guide covers the 25 production-ready project management skills organized across role-based, discovery, and execution domains.

## PM Skills Overview

**Available Skills (25 total):**

### Role-Based Skills (10)
1. **senior-pm/** - Portfolio management, stakeholder mapping, risk analysis, executive reporting
2. **scrum-master/** - Sprint analytics, team health, velocity forecasting, capacity planning
3. **delivery-manager/** - Release management, deployment coordination, incident response
4. **jira-expert/** - Jira administration, workflows, JQL, automation
5. **confluence-expert/** - Documentation, knowledge management, collaboration
6. **atlassian-admin/** - Atlassian suite administration and configuration
7. **atlassian-templates/** - Ready-to-use templates for Jira and Confluence
8. **agile-coach/** - Agile transformation, team coaching, maturity assessment
9. **program-manager/** - Multi-project coordination, dependency management
10. **packaged-skills/** - Bundled skill packages for quick deployment

### Discovery Skills (4) — `discovery/`
11. **brainstorm-ideas/** - Product Trio ideation, Opportunity Solution Trees
12. **brainstorm-experiments/** - Lean experiment design, XYZ hypotheses, pretotyping
13. **identify-assumptions/** - Assumption mapping across 4-8 risk categories
14. **pre-mortem/** - Tiger/Paper Tiger/Elephant risk classification

### Execution Skills (11) — `execution/`
15. **create-prd/** - 8-section PRD scaffolding with problem framing canvas and working backwards PR
16. **brainstorm-okrs/** - OKR brainstorming and validation (Wodtke framework)
17. **outcome-roadmap/** - Output→outcome roadmap transformation
18. **prioritization-frameworks/** - 9-framework reference with multi-scorer
19. **release-notes/** - Release notes generation from tickets/changelogs
20. **summarize-meeting/** - Structured meeting summaries with action items
21. **job-stories/** - JTBD discovery canvas and When/Want/So backlog format
22. **wwas/** - Why-What-Acceptance structured backlog items
23. **daci-framework/** - DACI decision facilitation and governance
24. **eol-communication/** - End-of-life product messaging and sunset communication
25. **story-mapping/** - Jeff Patton user story mapping for release planning

**Key Features:**
- Atlassian MCP Server integration for direct Jira/Confluence operations
- 10 Python CLI tools across role-based, discovery, and execution skills
- Integration between discovery → execution → delivery workflows

## Atlassian MCP Integration

**Purpose:** Direct integration with Jira and Confluence via Model Context Protocol (MCP)

**Capabilities:**
- Create, read, update Jira issues
- Manage Confluence pages and spaces
- Automate workflows and transitions
- Generate reports and dashboards
- Bulk operations on issues

**Setup:** Atlassian MCP server configured in Claude Code settings

**Usage Pattern:**
```bash
# Jira operations via MCP
mcp__atlassian__create_issue project="PROJ" summary="New feature" type="Story"

# Confluence operations via MCP
mcp__atlassian__create_page space="TEAM" title="Sprint Retrospective"
```

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

**Focus:** Product discovery workflows — ideation, experimentation, assumption mapping, risk analysis

**Python Tools:** `experiment_designer.py`, `assumption_tracker.py`, `risk_categorizer.py`

**Key Workflows:**
- Product Trio ideation (PM + Designer + Engineer perspectives)
- Lean experiment design with XYZ hypothesis format
- Assumption mapping with Impact × Risk prioritization
- Pre-mortem with Tiger/Paper Tiger/Elephant classification

### Execution Skills (`execution/`)

**Focus:** PM execution artifacts — PRDs, OKRs, roadmaps, prioritization, release notes, backlog formats

**Python Tools:** `prd_scaffolder.py`, `okr_validator.py`, `roadmap_transformer.py`, `prioritization_scorer.py`, `release_notes_generator.py`

**Key Workflows:**
- PRD generation with 8-section structure
- OKR validation against SMART criteria
- Output→outcome roadmap transformation
- Multi-framework prioritization (RICE, ICE, Opportunity Score, MoSCoW, Weighted)
- Release notes from tickets/changelogs
- Meeting summaries, job stories, WWAS backlog items

### Jira Expert (`jira-expert/`)

**Focus:** Jira configuration, custom workflows, automation rules

### Confluence Expert (`confluence-expert/`)

**Focus:** Documentation strategy, templates, knowledge management

### Atlassian Admin (`atlassian-admin/`)

**Focus:** Suite administration, user management, integrations

### Atlassian Templates (`atlassian-templates/`)

**Focus:** Ready-to-use templates for common PM tasks

## Integration Patterns

### Pattern 1: Discovery → Execution Flow

```
brainstorm-ideas/ → identify-assumptions/ → brainstorm-experiments/ → pre-mortem/
     ↓                                                                      ↓
create-prd/ → brainstorm-okrs/ → outcome-roadmap/ → prioritization-frameworks/
     ↓
release-notes/ (post-delivery)
```

### Pattern 2: Sprint Planning (Data-Driven)

```bash
# 1. Calculate team capacity
python scrum-master/scripts/sprint_capacity_calculator.py team.json

# 2. Analyze velocity trends
python scrum-master/scripts/velocity_analyzer.py sprints.json

# 3. Score backlog items
python execution/prioritization-frameworks/scripts/prioritization_scorer.py backlog.json --framework rice

# 4. Create sprint in Jira (via MCP)
mcp__atlassian__create_sprint board="TEAM-board" name="Sprint 23"
```

### Pattern 3: Stakeholder-Aligned Release

```bash
# 1. Map stakeholders
python senior-pm/scripts/stakeholder_mapper.py stakeholders.json

# 2. Run pre-mortem on release plan
python discovery/pre-mortem/scripts/risk_categorizer.py risks.json

# 3. Generate release notes
python execution/release-notes/scripts/release_notes_generator.py entries.json
```

## Additional Resources

- **Installation Guide:** `INSTALLATION_GUIDE.txt`
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`
- **Real-World Scenario:** `REAL_WORLD_SCENARIO.md`
- **PM Overview:** `README.md`
- **Main Documentation:** `../CLAUDE.md`

---

**Last Updated:** March 2026
**Skills Deployed:** 22/22 PM skills production-ready
**Python Tools:** 10 CLI tools
**Integration:** Atlassian MCP Server for Jira/Confluence automation
