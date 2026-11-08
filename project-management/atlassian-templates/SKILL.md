---
name: atlassian-templates
description: >
  Builds, validates and retires reusable Jira issue and Confluence page templates. Use
  when creating a team or org-wide template, a template is ignored or half-filled, or a
  template library has sprawled. Space layout is confluence-expert.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: atlassian
  updated: 2026-11-08
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

Before building the template, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target tool & artifact:** Confluence page template, Jira issue template, or multi-page blueprint (sets which macros/fields are available and the structure).
- **Template type:** meeting notes, PRD, charter, bug report, decision log, etc. (selects the base structure and placeholders).
- **Rollout scope:** one team vs org-wide canonical template (drives parameterization, naming, and governance).
- **Dynamic vs static content:** which fields auto-populate via macros/Jira queries vs fixed placeholders (drives build complexity and adoption).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

1. **Discover** stakeholder needs and review existing content patterns
2. **Design** the structure with clear placeholders + inline guidance
3. **Build** with macros (panels, info/note, tasks, status, dynamic Jira queries)
4. **Test** with sample data, then **publish** to the target space/project
5. **Train** users and **monitor** adoption; iterate quarterly

Grab a ready-made starting point from `references/confluence-templates.md` or `references/jira-templates.md`, then follow the full creation/modification workflow in `references/workflows-and-governance.md`. Step 3 is `template_scaffolder.py`; step 4 is `template_validator.py`; step 5 is `template_usage_analyzer.py`.

## Tools

Each tool reads one JSON file and prints a text report (`--json` for machine output).
`--example` prints the input shape; samples ship in `assets/`. Bad input (missing file,
invalid JSON, wrong shape) exits 2 with a one-line error.

```bash
python3 project-management/atlassian-templates/scripts/template_scaffolder.py --spec project-management/atlassian-templates/assets/sample_template_spec.json --format confluence
python3 project-management/atlassian-templates/scripts/template_validator.py --template project-management/atlassian-templates/assets/sample_template.json         # exit 0
python3 project-management/atlassian-templates/scripts/template_validator.py --template project-management/atlassian-templates/assets/sample_template_flawed.json  # exit 1
python3 project-management/atlassian-templates/scripts/template_usage_analyzer.py --usage project-management/atlassian-templates/assets/sample_template_usage.json
```

| Tool | What it does | Exit |
|------|--------------|------|
| `template_scaffolder.py` | Turns a section spec into Confluence wiki markup or a Jira description (`--format confluence\|jira`) | 0 |
| `template_validator.py` | 10 weighted checks: name, owner, description, 3+ sections, inline instructions, example, dynamic content, version, updated within 12 months of `as_of` (default today), labels | 0 all pass, 1 any fail |
| `template_usage_analyzer.py` | Adoption, quality score and freshness per template; flags zero-use, low-quality and ownerless templates. Freshness is measured from the file's `as_of`, else its latest `last_updated` | 0 |

## Anti-Patterns

### A new template for every variation
**Mistake:** The space fills up with "PRD v1", "PRD v2", "PRD - mobile" and copies of copies.
**Why it happens:** Copying a template and tweaking it is quicker than changing the shared one.
**Instead:** Keep a small set of canonical templates with parameterized sections. More than 15 templates in one top-level space is sprawl. Merge the variants and retire the rest.

### Fields nobody fills in
**Mistake:** The template has 40 fields, and 25 of them end up blank, "TBD" or "N/A".
**Why it happens:** Each field looked useful when someone proposed it, and nobody checks how they get used.
**Instead:** Measure fill rate per field across the last 50 uses. Remove or make optional any field below 50%. Make a section required only if 80% or more of authors will have real content for it.

### Macros that render empty
**Mistake:** The template ships a Jira-issues macro with a hardcoded JQL filter, or a page-properties report on a label nobody uses.
**Why it happens:** The macro worked in the space where the template was built.
**Instead:** Render the template into a sample page before you publish it. Every macro must show real content or a clear "configure me" prompt. It must never show a silent blank.

Nine more, each with a bad and a good example: `references/red-flags.md`.

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

## Files

| File | Purpose |
|------|---------|
| `scripts/template_scaffolder.py`, `scripts/template_validator.py`, `scripts/template_usage_analyzer.py` | See Tools |
| `assets/sample_template_spec.json`, `assets/sample_template.json`, `assets/sample_template_flawed.json`, `assets/sample_template_usage.json` | Runnable inputs; the flawed template shows a failing gate |
| `references/*.md` | See References |
