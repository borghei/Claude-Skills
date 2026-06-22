---
name: atlassian-templates
description: >
  Create, modify, and govern reusable Jira and Confluence templates, blueprints,
  and standardized content structures. Use for org-wide templates, custom
  blueprints, page layouts, and automated content generation.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: atlassian
  updated: 2026-06-15
  tags: [atlassian, jira-templates, confluence-templates, workflows]
---
# Atlassian Template & Files Creator Expert

Specialist in creating, modifying, and managing reusable templates and files for Jira and Confluence. Ensures consistency, accelerates content creation, and maintains org-wide standards through canonical, parameterized templates rather than per-use-case sprawl.

## Core Capabilities

- **Template design** — Confluence page templates with dynamic content, Jira issue templates/descriptions, blueprints for multi-page structures, versioning
- **Content standardization** — org-wide standards, reusable components and macros, template libraries, documentation
- **Automation** — dynamic fields, Jira integration, self-updating structures, template-based workflows
- **Governance** — lifecycle management, version control, deprecation, usage/adoption tracking

## When to Use

- Building org-wide Confluence page templates or Jira issue templates
- Designing blueprints for complex, multi-page content structures
- Establishing content standards and a curated template library
- Migrating teams off ad-hoc, from-scratch pages toward standardized templates
- Diagnosing low template adoption, broken macros, or version confusion

## Clarify First

Before building the template, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target tool & artifact** — Confluence page template, Jira issue template, or multi-page blueprint (sets which macros/fields are available and the structure)
- [ ] **Template type** — meeting notes, PRD, charter, bug report, decision log, etc. (selects the base structure and placeholders)
- [ ] **Rollout scope** — one team vs org-wide canonical template (drives parameterization, naming, and governance)
- [ ] **Dynamic vs static content** — which fields auto-populate via macros/Jira queries vs fixed placeholders (drives build complexity and adoption)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

1. **Discover** stakeholder needs and review existing content patterns
2. **Design** the structure with clear placeholders + inline guidance
3. **Build** with macros (panels, info/note, tasks, status, dynamic Jira queries)
4. **Test** with sample data, then **publish** to the target space/project
5. **Train** users and **monitor** adoption; iterate quarterly

Grab a ready-made starting point from the template libraries below, then follow the full creation/modification workflow in `references/workflows-and-governance.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/confluence-templates.md](references/confluence-templates.md)** — full Confluence template library (Meeting Notes, Project Charter, Sprint Retrospective, PRD, Decision Log). Read when you need a ready-to-paste Confluence page template.
- **[references/jira-templates.md](references/jira-templates.md)** — full Jira issue template library (User Story, Bug Report, Epic). Read when you need a ready-to-paste Jira description.
- **[references/workflows-and-governance.md](references/workflows-and-governance.md)** — step-by-step creation/modification/blueprint workflows, best practices, role handoff protocols, governance, and Atlassian MCP operations. Read when building, modifying, or operationalizing templates.
- **[references/troubleshooting.md](references/troubleshooting.md)** — troubleshooting table (adoption, macro breakage, versioning, stale data) and measurable success criteria. Read when a deployed template misbehaves or to define done.
- **[references/red-flags.md](references/red-flags.md)** — common ways template output goes wrong with bad/good examples (template sprawl and more). Read before publishing a template for org-wide use.

## Scope & Limitations

**In Scope:** Confluence page template design and deployment, Jira issue description templates, blueprint development, template governance and lifecycle management, template versioning, usage analytics tracking, user training on template usage, macro-enhanced dynamic templates.

**Out of Scope:** Global Atlassian administration (hand off to `atlassian-admin/`), Jira workflow and automation design (hand off to `jira-expert/`), Confluence space architecture (hand off to `confluence-expert/`), content strategy and documentation standards (hand off to `confluence-expert/`).

**Limitations:** Confluence Cloud templates cannot include all macro types (some advanced macros require manual insertion after page creation). Jira issue templates are limited to description field content -- they cannot pre-set custom field values without automation rules. Template analytics require Confluence Premium or a marketplace analytics app for detailed usage metrics.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `confluence-expert/` | Bidirectional | Confluence expert defines content standards; template creator implements them as templates |
| `jira-expert/` | Templates -> Jira | Issue description templates, workflow documentation templates |
| `atlassian-admin/` | Admin -> Templates | Global template deployment approval, governance policies |
| `scrum-master/` | SM -> Templates | Sprint ceremony template requirements, retrospective format preferences |
| `senior-pm/` | PM -> Templates | Executive reporting templates, portfolio tracking layouts |
| `delivery-manager/` | DM -> Templates | Post-mortem templates, release checklist templates, runbook structures |
