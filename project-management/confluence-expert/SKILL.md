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

## Clarify First

Confluence advice depends most on which Confluence the user runs and how much of it they can change. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Cloud or Data Center, and plan tier:** Cloud plan tiers set storage limits that matter for attachment-heavy spaces, and page-view and contributor analytics need Premium or a marketplace app. Data Center reaches end of life on 28 Mar 2029, so a restructure there should be planned around the Cloud migration.
- **Permission level:** A space admin can change the page tree, space templates and space permissions. Org-wide templates, blueprints, global automation and cross-space permissions belong to `atlassian-admin/`, and space settings cannot override stricter org-wide security policies. The user's rights decide whether you deliver a change they can make or a request for their admin.
- **New space or existing one:** A new space can get the right page tree from the start. An existing space needs its current tree or a page export first, because moving pages between spaces can break internal links, and `space_structure_analyzer.py`, `content_health_auditor.py` and `label_taxonomy_analyzer.py` all work from such an export.
- **What the space is for:** A team workspace, an operational space of runbooks and a published knowledge base need different hierarchies, permissions and review cadences. Operational pages need a named owner and a review date; a scratch team space can be looser.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Anti-Patterns

### Flat space with no hierarchy
**Mistake:** Hundreds of pages sit at the root of one space, and nobody knows where new content goes.
**Why it happens:** Creating a page at the top level is the default, and nobody owns the structure.
**Instead:** Design the page tree before content piles up. If the space root has more than about 15 pages, regroup them under parent pages by team, project or topic.

### Pages with no owner or review date
**Mistake:** Pages carry no owner and no "last reviewed" date, so stale content stays live.
**Why it happens:** Writing the page feels like the end of the job.
**Instead:** Give every page in an operational space a named owner and a review date, and set a review cadence. A runbook that pages someone who left two years ago is an outage waiting to happen.

### "Source of truth" with four versions
**Mistake:** The team calls Confluence its source of truth, but one topic has four pages that disagree.
**Why it happens:** Writing a new page is easier than finding and fixing the old one.
**Instead:** For your top 10 most-searched topics, keep exactly one canonical page. Merge or archive the duplicates and link them to the canonical page.

Nine more, each with a bad and a good example: `references/red-flags.md`.

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
