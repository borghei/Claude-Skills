---
name: release-notes
description: Structured release notes creation that translates technical changes into user-benefit-oriented communication.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-03-04
  tech-stack: release-management, changelog, semantic-versioning
  python-tools:
    - scripts/release_notes_generator.py
---

# Release Notes Expert

## Overview

Transform raw technical changes -- tickets, changelogs, git logs, PRDs -- into clear, user-benefit-oriented release notes. This skill ensures every release communicates value to the right audience in the right tone.

### When to Use

- **Product Releases** -- Announcing new versions to customers, partners, or internal stakeholders.
- **Sprint Demos** -- Summarizing what shipped for sprint review audiences.
- **Changelog Maintenance** -- Keeping a running log of changes across releases.
- **Customer Communication** -- Preparing release announcements for email, in-app, or documentation.

## Methodology

### Step 1: Gather Raw Input

Collect all changes from the release cycle:

- **Jira/Linear tickets** -- Completed stories, bugs, and tasks
- **Git log** -- Merge commits since last release tag
- **PRD references** -- Feature specs that shipped
- **Hotfix records** -- Emergency fixes deployed between releases

### Step 2: Classify Each Change

Assign every change to exactly one category:

| Category | Definition | Example |
|----------|-----------|---------|
| **New Features** | Net-new capabilities that did not exist before | New export-to-PDF option |
| **Improvements** | Enhancements to existing functionality | Faster dashboard loading |
| **Bug Fixes** | Corrections to broken or incorrect behavior | Fixed login redirect loop |
| **Breaking Changes** | Changes that require user action to adapt | API v2 replaces v1 endpoints |
| **Deprecations** | Features scheduled for future removal | Legacy CSV import will be removed in v4.0 |

**Classification rules:**

- If a change adds something entirely new, it is a **New Feature**.
- If it makes something existing better (faster, easier, more reliable), it is an **Improvement**.
- If it fixes something that was wrong, it is a **Bug Fix**.
- If users must change their behavior, configuration, or integration, it is a **Breaking Change**.
- If a feature still works but will be removed later, it is a **Deprecation**.

### Step 3: Rewrite for User Benefit

The most critical step. Every entry must lead with the benefit to the user, not the technical change.

**Rewriting principles:**

1. **Lead with the outcome.** What can the user do now that they could not before, or what is better for them?
2. **Use plain language.** Avoid internal jargon, code references, or implementation details.
3. **Keep it to 1-3 sentences.** One sentence for minor items, up to three for significant features.
4. **Include context when needed.** If users need to take action, tell them exactly what to do.

**Before and after examples:**

| Technical (Bad) | User-Benefit (Good) |
|----------------|-------------------|
| Implemented Redis caching layer for dashboard queries | Dashboards now load up to 3x faster |
| Refactored authentication module to use OAuth 2.0 PKCE flow | Sign-in is now more secure and works reliably across all browsers |
| Fixed null pointer exception in report export handler | Report exports no longer fail when date ranges include empty days |
| Migrated user preferences API from v1 to v2 schema | **Action required:** Update your API calls to use the new `/v2/preferences` endpoint by April 30. See migration guide. |
| Added feature flag for beta dashboard | You can now opt into the redesigned dashboard from Settings > Beta Features |

**Red flags that an entry needs rewriting:**

- Mentions a class name, function, or library
- Starts with "Refactored," "Migrated," or "Updated" without stating impact
- Uses acronyms the target audience would not know
- Describes what the team did instead of what the user gains

### Step 4: Adjust Tone for Audience

| Audience | Tone | Style Notes |
|----------|------|-------------|
| **B2B / Enterprise** | Professional, precise | Emphasize reliability, security, compliance. Avoid casual language. |
| **Consumer** | Friendly, conversational | Use "you" and "your." Celebrate new features. Keep it light. |
| **Developer / API** | Technical, direct | Include endpoint names, SDK versions, code snippets. Be specific. |
| **Internal** | Detailed, context-rich | Include ticket IDs, team names, technical details as needed. |

### Step 5: Assemble the Release Notes

Use the output template below. Include only categories that have entries -- do not show empty sections.

## Output Template

```markdown
# [Product Name] v[X.Y.Z] Release Notes

**Release Date:** [YYYY-MM-DD]

---

## New Features

- **[Feature Name]** -- [1-3 sentence description of user benefit]. ([TICKET-ID])

## Improvements

- **[Improvement Name]** -- [1-2 sentence description of what is better]. ([TICKET-ID])

## Bug Fixes

- **[Bug Fix Name]** -- [1 sentence describing what was broken and that it is now fixed]. ([TICKET-ID])

## Breaking Changes

> **Action Required:** The following changes require updates on your end.

- **[Change Name]** -- [Description of what changed and exactly what the user must do]. ([TICKET-ID])

## Deprecations

> **Planned Removal:** The following features will be removed in a future release.

- **[Feature Name]** -- [What is being deprecated and when it will be removed. Recommend alternative if available]. ([TICKET-ID])

---

**Full changelog:** [link]
**Questions?** [support link or contact]
```

## Python Tool

Use `scripts/release_notes_generator.py` to generate formatted release notes from structured input.

```bash
# Generate from JSON input
python scripts/release_notes_generator.py --input changes.json --product-name "Acme App" --version "2.5.0"

# Run with demo data
python scripts/release_notes_generator.py --demo --product-name "Acme App" --version "1.0.0"

# Output as JSON instead of markdown
python scripts/release_notes_generator.py --input changes.json --format json --product-name "Acme App" --version "2.5.0"
```

See `scripts/release_notes_generator.py --help` for full usage.

## Integration with Other Skills

- Use `summarize-meeting/` to capture release planning discussions.
- Use `job-stories/` or `wwas/` to trace features back to their original motivation.
- Pair with `../senior-pm/` for stakeholder communication planning around major releases.

## References

- See `references/release-notes-guide.md` for best practices, audience guidance, and examples.
- See `assets/release_notes_template.md` for a ready-to-use document template.
