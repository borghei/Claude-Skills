---
name: confluence-expert
description: >
  Confluence expert for spaces, knowledge bases, documentation, page layouts,
  macros, templates, and Jira-Confluence integration. Use for documentation
  strategy, space architecture, content organization, and collaborative
  knowledge management.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: atlassian
  updated: 2026-06-15
  tags: [confluence, knowledge-management, wiki, documentation]
---
# Atlassian Confluence Expert

Master-level expertise in Confluence space management, documentation architecture, content creation, macros, templates, and collaborative knowledge management.

## Core Capabilities

- **Space architecture** — design space hierarchies, organize knowledge by team/project/topic, implement taxonomies, configure permissions and visibility
- **Content creation** — structured pages with layouts, dynamic macros, reusable templates, version control and change tracking
- **Collaboration & governance** — documentation practices, review/approval workflows, content lifecycle management, documentation standards
- **Integration & automation** — link Confluence with Jira, embed dynamic Jira reports, configure watchers/notifications, content automation

## When to Use

- Standing up or restructuring a space and its page hierarchy
- Designing templates (meeting notes, project overview, decision log, retro)
- Setting content governance: review cycles, archiving, quality standards
- Embedding Jira issues, charts, or reports inside Confluence pages
- Defining or auditing space permission schemes
- Driving documentation strategy and knowledge-base health

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/confluence-playbook.md](references/confluence-playbook.md)** — full detail behind this map: competencies, workflows (space creation, page architecture, documentation strategy, KB management), macro syntax, page layouts, inline template examples, permission schemes, content governance, decision/handoff protocols, analytics, troubleshooting table, and success criteria. Read when executing any Confluence task.
- **[references/templates.md](references/templates.md)** — ready-to-paste Confluence page templates (meeting notes, and more) with full markdown structure. Read when you need a complete template to drop into a space.
- **[references/red-flags.md](references/red-flags.md)** — common ways a space design, IA proposal, page template, or governance policy goes wrong, with bad/good examples. Read before shipping any Confluence artifact.

## Scope & Limitations

**In Scope:** Space creation and architecture, page hierarchy design, template creation and management, content governance (review cycles, archiving, quality standards), macro usage and dynamic content, documentation strategy, knowledge base management, Jira-Confluence integration, content analytics.

**Out of Scope:** Global Atlassian administration (hand off to `atlassian-admin/`), Jira project configuration (hand off to `jira-expert/`), template design and governance (hand off to `atlassian-templates/`), sprint execution artifacts (hand off to `scrum-master/`).

**Limitations:** Confluence Cloud has storage limits per plan tier that affect attachment-heavy spaces. Advanced analytics (page view trends, contributor activity) require Confluence Premium or marketplace apps. Space-level permissions cannot override more restrictive org-wide security policies set by `atlassian-admin/`. Content migration between spaces can break internal links and require manual fixup. Confluence Data Center reaches end of life on 28 Mar 2029 (read-only; no new/expanded DC licenses after 30 Mar 2028) -- plan space restructuring around a Cloud migration rather than on DC ([timeline](https://www.atlassian.com/licensing/data-center-end-of-life); see `atlassian-admin/`).

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `jira-expert/` | Bidirectional | Jira macros in Confluence pages; Confluence page links in Jira issue descriptions |
| `atlassian-admin/` | Admin -> Confluence | Global templates, space permission schemes, blueprint configuration |
| `atlassian-templates/` | Templates -> Confluence | Designed templates deployed to spaces; template usage guidelines |
| `scrum-master/` | SM -> Confluence | Sprint ceremony documentation needs, team working agreement pages |
| `senior-pm/` | PM -> Confluence | Executive report pages, portfolio documentation, stakeholder communication |
| `delivery-manager/` | DM -> Confluence | Post-mortem documentation, runbooks, release notes pages |
