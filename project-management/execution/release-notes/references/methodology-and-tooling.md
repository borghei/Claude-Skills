# Release Notes Methodology, Template & Tooling

> Read this when you need the full 5-step methodology (gather, classify, rewrite, tone, assemble), the output template, the `release_notes_generator.py` command/flag reference, troubleshooting, or success criteria.

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

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Tool flags too many entries as "technical language" | TECHNICAL_PATTERNS is a keyword heuristic (jargon verbs like "refactor", acronyms such as API or SSO, code identifiers) | Review the flagged entries; the tool provides suggestions, not mandates -- ignore false positives for user-facing descriptions |
| All entries classified as same type | Input JSON uses wrong type values or inconsistent casing | Use exact lowercase types: `feature`, `improvement`, `bugfix`, `breaking`, `deprecation` |
| Empty sections appear in output | No entries of that type exist but template still renders the section | The tool only renders sections with entries; empty sections indicate a data issue in input |
| Breaking changes not highlighted prominently | Entries marked as `improvement` instead of `breaking` | Review classification rules: if users must change behavior, config, or integration, it is `breaking`, not `improvement` |
| Release notes sound like commit messages | Descriptions written from developer perspective, not user perspective | Apply the rewriting principles: lead with outcome, use plain language, 1-3 sentences per entry |
| `--demo` flag requires `--product-name` and `--version` | These are required arguments regardless of input source | Always provide both: `--demo --product-name "App" --version "1.0.0"` |
| JSON output missing rewriting suggestions | No entries triggered technical language detection patterns | This is expected behavior; suggestions only appear when TECHNICAL_PATTERNS match entry descriptions |

## Success Criteria

- Every release has structured notes published within 24 hours of deployment
- All entries lead with user benefit, not technical implementation details
- Breaking changes include explicit migration instructions with deadlines
- Deprecations include removal timeline and recommended alternatives
- Technical language flags reviewed and addressed before publication
- Release notes tone matches the target audience (B2B/consumer/developer/internal)
- Entries traceable to tickets via ticket_id for audit and context

## Tool Reference

### release_notes_generator.py

Generates formatted release notes from structured JSON input. Groups entries by category, formats into markdown or JSON, and flags entries that may need user-benefit rewriting.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--input` | string | (optional) | Path to JSON file containing release entries |
| `--demo` | flag | off | Run with built-in demo data (8 entries across all types) |
| `--product-name` | string | (required) | Product name for the release notes header |
| `--version` | string | (required) | Version string (e.g., `2.5.0`) |
| `--format` | choice | `text` | Output format: `text` (markdown) or `json` |
| `--date` | string | today | Release date in YYYY-MM-DD format |

**Input JSON schema:**
```json
{
  "entries": [
    {
      "title": "Feature Name",
      "description": "User-benefit description (1-3 sentences)",
      "type": "feature|improvement|bugfix|breaking|deprecation",
      "ticket_id": "PROJ-123 (optional)"
    }
  ]
}
```
