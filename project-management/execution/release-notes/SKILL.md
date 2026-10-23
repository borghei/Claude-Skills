---
name: release-notes
description: >
  Structured release notes that translate technical changes (tickets, changelogs,
  git logs, PRDs) into user-benefit communication. Use for product releases, sprint
  demos, changelog maintenance, or customer release announcements.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools:
    - scripts/release_notes_generator.py
  tech-stack: release-management, changelog, semantic-versioning
  tags:
    - release-notes
    - changelog
    - customer-communication
    - product-updates
---
# Release Notes Expert

## Overview

Transform raw technical changes -- tickets, changelogs, git logs, PRDs -- into clear, user-benefit-oriented release notes. This skill ensures every release communicates value to the right audience in the right tone, via a 5-step methodology: gather input, classify each change into one of five categories, rewrite for user benefit, adjust tone for the audience, and assemble.

### When to Use

- **Product Releases** -- Announcing new versions to customers, partners, or internal stakeholders.
- **Sprint Demos** -- Summarizing what shipped for sprint review audiences.
- **Changelog Maintenance** -- Keeping a running log of changes across releases.
- **Customer Communication** -- Preparing release announcements for email, in-app, or documentation.

## Core Capabilities

- **5-category classification** — New Features, Improvements, Bug Fixes, Breaking Changes, Deprecations with explicit assignment rules
- **User-benefit rewriting** — lead with the outcome, plain language, 1-3 sentences; detects developer-perspective phrasing
- **Audience tone guidance** — B2B/enterprise, consumer, developer/API, internal
- **Automated generation** — `release_notes_generator.py` groups entries, formats markdown/JSON, and flags technical language for rewrite

## Clarify First

Before generating the release notes, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Audience:** B2B/enterprise, consumer, developer/API, or internal (sets the entire tone matrix and how much detail to include).
- **Source changes:** the tickets/PRs/changelog to translate, classified into the 5 categories (nothing generates without these).
- **Breaking changes & deprecations:** what changed, the required action, and by when (forces the mandatory breaking-change fields that protect user trust).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
python scripts/release_notes_generator.py --input changes.json --product-name "Acme App" --version "2.5.0"
python scripts/release_notes_generator.py --demo --product-name "Acme App" --version "1.0.0"
```

Include only categories that have entries. Breaking changes must state what changed, what the user must do, and by when. See the references for the full methodology, output template, and flag reference.

## Anti-Patterns

### Notes for features that never shipped
**Mistake:** An item appears because its ticket was marked Done, but the code was reverted before release.
**Why it happens:** The ticket tracker looks like the source of truth, so its Done list goes straight into `changes.json`.
**Instead:** Before running `release_notes_generator.py`, cross-check Done tickets against the shipped commits (for example `git log v4.1..v4.2`). Flag any ticket that is missing from the diff for human review, and remove it if it didn't ship.

### Marketing copy in place of specifics
**Mistake:** "Game-changing AI-powered insights now live across the platform!" with no behavior described.
**Why it happens:** Hype feels like it drives adoption, and describing the exact behavior takes more work.
**Instead:** Search for "revolutionary", "game-changing", "powered by AI" and "next-generation". Replace each with the specific behavior, the plans it is on, and how to turn it off.

### One note for internal and external readers
**Mistake:** The customer email includes "known issue: occasional 502 on Safari, rollback in progress, on-call: @ana".
**Why it happens:** Writing one note is faster, and the internal details feel like useful transparency.
**Instead:** Produce two artifacts from the same source. The internal one carries known issues, on-call and rollback steps. The external one is value-framed with breaking changes first. Check customer copy for "rollback", "on-call" and internal known issues before sending.

Seven more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/methodology-and-tooling.md](references/methodology-and-tooling.md)** — full 5-step methodology, classification tables, rewriting before/after examples, audience tone matrix, output template, troubleshooting, success criteria, and the `release_notes_generator.py` flag + JSON-schema reference. Read when producing notes or running the tool.
- **[references/release-notes-guide.md](references/release-notes-guide.md)** — best-practices guide on category definitions, audience guidance, and worked examples. Read for the deeper rationale.
- **[references/red-flags.md](references/red-flags.md)** — concrete bad-vs-good entry examples and how to fix them. Read before publishing a draft.
- **[assets/release_notes_template.md](assets/release_notes_template.md)** — ready-to-use release notes document template.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `sprint-retrospective/` | Receives from | Sprint commit data and type distribution inform what changes to include |
| `senior-pm/` | Complements | Stakeholder communication plans guide release note audience and tone |
| `execution/create-prd/` | Receives from | PRD feature descriptions (Section 7) become release note entry drafts |
| `scrum-master/` | Receives from | Sprint review outputs identify what shipped and needs documentation |
| `summarize-meeting/` | Receives from | Release planning meeting summaries capture context for release notes |
| `job-stories/` / `wwas/` | Receives from | User story descriptions inform user-benefit framing of entries |

## Scope & Limitations

**In Scope:**
- Structured release note generation from JSON input with 5 entry categories
- Automatic technical language detection with rewriting suggestions
- Markdown and JSON output formatting with category grouping
- Audience tone guidance (B2B, consumer, developer, internal)
- Classification rules for New Features, Improvements, Bug Fixes, Breaking Changes, and Deprecations

**Out of Scope:**
- Automatic extraction of changes from git history (see `sprint-retrospective/` for git analysis)
- Jira/Linear ticket integration for pulling completed stories (manual JSON input required)
- Changelog maintenance across multiple releases (this tool generates per-release notes)
- Distribution to email, in-app, or documentation channels (output is markdown/JSON for further processing)

**Important Caveats:**
- The rewriting suggestions are pattern-based heuristics. They catch common technical language but cannot assess whether a description truly communicates user benefit.
- Semantic versioning alignment is the user's responsibility. The tool does not validate that version numbers follow semver conventions relative to the change types present.
- Breaking changes require special care. Always include: what changed, what the user must do, and by when. Vague breaking change notes erode user trust.
