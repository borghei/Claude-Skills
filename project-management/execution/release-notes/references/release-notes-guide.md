# Release Notes Best Practices Guide

## Purpose

Release notes are the bridge between what your team built and what your users understand. They serve three functions: inform users of what changed, build trust through transparency, and drive adoption of new capabilities.

## Category Definitions

### New Features

Something that did not exist before. The user gains a capability they previously lacked.

**Test:** Could the user do this yesterday? If no, it is a new feature.

### Improvements

An existing capability that is now better -- faster, easier, more reliable, more accessible.

**Test:** Could the user already do this, but now it is better? If yes, it is an improvement.

### Bug Fixes

Something was broken and is now fixed. The software was not behaving as intended or documented.

**Test:** Was this a defect report or unexpected behavior? If yes, it is a bug fix.

### Breaking Changes

A change that requires the user to take action. Their existing workflow, integration, or configuration will stop working or behave differently without intervention.

**Test:** Will anything break for the user if they do nothing? If yes, it is a breaking change.

### Deprecations

A feature that still works today but will be removed in a future release. This gives users time to migrate.

**Test:** Does it still work but is scheduled for removal? If yes, it is a deprecation.

## Writing for Different Audiences

### B2B / Enterprise

- **Tone:** Professional, precise, confident
- **Emphasize:** Reliability, security, compliance, productivity gains
- **Avoid:** Casual language, exclamation marks, emojis
- **Include:** Impact on workflows, admin actions required, compliance implications
- **Example:** "Role-based access controls now support custom permission sets, enabling administrators to define granular access policies aligned with organizational security requirements."

### Consumer

- **Tone:** Friendly, conversational, enthusiastic (measured)
- **Emphasize:** Ease of use, delight, time saved, new possibilities
- **Avoid:** Technical jargon, implementation details
- **Include:** Visual descriptions, tips for getting started
- **Example:** "You can now organize your photos into custom albums. Tap the new Albums tab to get started."

### Developer / API

- **Tone:** Technical, direct, specific
- **Emphasize:** Endpoints, parameters, SDK versions, migration steps
- **Avoid:** Marketing language, vague descriptions
- **Include:** Code snippets, request/response examples, version numbers
- **Example:** "The `GET /v2/users` endpoint now accepts an optional `fields` query parameter for sparse fieldsets. See the API reference for supported field names."

### Internal Stakeholders

- **Tone:** Detailed, context-rich
- **Emphasize:** Business impact, metrics, team contributions
- **Avoid:** Over-simplification
- **Include:** Ticket IDs, team names, technical context as needed

## Distribution Channels

| Channel | Best For | Format |
|---------|----------|--------|
| **In-app notification** | All users, high visibility | Short summary with link to full notes |
| **Email** | Active users, subscription-based | Full notes or curated highlights |
| **Blog post** | Major releases, marketing value | Narrative format with screenshots |
| **Changelog page** | Developer audience, reference | Chronological, all versions |
| **Documentation** | API changes, migration guides | Technical, step-by-step |
| **Social media** | Brand awareness, feature highlights | Single feature spotlight |
| **Slack / Teams** | Internal stakeholders | Summary with links |

## Good vs Bad Examples

### Bad: Technical and self-centered

> - Updated React from v17 to v18
> - Refactored UserService to use repository pattern
> - Fixed NPE in ReportExportHandler.java line 234
> - Migrated auth to PKCE flow

### Good: User-benefit-oriented

> - **Smoother interactions** -- Page transitions and form updates are now noticeably faster and more responsive.
> - **Faster report exports** -- Reports that previously timed out now complete reliably, even for large date ranges.
> - **More secure sign-in** -- Your account is now protected by an upgraded authentication standard that works consistently across all browsers.

### Bad: Vague and unhelpful

> - Various bug fixes and improvements
> - Performance enhancements
> - Updated dependencies

### Good: Specific and actionable

> - **Fixed:** CSV exports now include all columns when custom fields are enabled. (BUG-3421)
> - **Faster:** Dashboard widgets load 40% faster on pages with more than 20 widgets.
> - **Updated:** The Python SDK now requires Python 3.9 or later. See the migration guide for upgrade instructions.

## Checklist Before Publishing

- [ ] Every entry leads with user benefit, not technical change
- [ ] No internal jargon, class names, or function references
- [ ] Breaking changes clearly state what the user must do
- [ ] Deprecations include a timeline and recommended alternative
- [ ] Tone matches the target audience
- [ ] Ticket IDs are included for traceability (if appropriate for audience)
- [ ] Empty categories are removed
- [ ] Release date and version number are correct
- [ ] Links to full changelog, support, and migration guides are included
