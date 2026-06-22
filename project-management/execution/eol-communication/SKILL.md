---
name: eol-communication
description: >
  End-of-life product messaging and sunset communication framework for clear,
  empathetic EOL announcements that preserve customer trust. Use when sunsetting
  a product, feature, service, API version, or pricing tier.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: eol, product-lifecycle, change-communication
---
# EOL Communication Expert

## Overview

Create clear, empathetic End-of-Life (EOL) communications that preserve customer trust and facilitate smooth transitions. Sunsetting a product is a high-stakes communication challenge -- done poorly, it damages brand trust and accelerates churn across your entire portfolio. Done well, it strengthens customer relationships and drives migration to replacement solutions.

The work runs in four phases: **(1) Pre-announcement planning** (what, why, who, when, what support, what risks), **(2) Craft the message** (transition narrative, customer impact, transition solution, timeline, one CTA), **(3) Segment and distribute** (different message and channel per segment), **(4) Support and monitor** (support FAQ, migration tracking, churn watch). See the playbook reference for the full framework, templates, and timeline guidance.

## Clarify First

Before crafting the EOL communication, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **What is being sunset and why** — drives the transition narrative and Phase 1 planning; a vague "why" reads as abandonment
- [ ] **Replacement / migration path** — drives the transition solution and the single CTA; if it is broken or absent, do not announce yet
- [ ] **Timeline and key dates** — drives the timeline section and varies sharply by product type (API vs paid product vs free feature)
- [ ] **Customer segments affected** — drives the Phase 3 segment/channel matrix; high-value accounts need different message and outreach than self-serve

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## When to Use

- **Product sunset** -- Discontinuing an entire product or product line.
- **Feature deprecation** -- Removing a significant feature from an existing product.
- **Service migration** -- Moving customers from one platform or infrastructure to another.
- **API retirement** -- Deprecating API versions or endpoints.
- **Pricing model change** -- Major pricing restructure that effectively ends old tiers.

### When NOT to Use

- Minor feature changes that don't require customer notification.
- Internal tooling changes with no customer impact.
- Bug fixes or patches (use release notes instead).

## References

- **[references/playbook.md](references/playbook.md)** — read this when crafting a sunset announcement: the 4-phase EOL framework, the messaging template and writing rules, the segment/channel matrix, the internal support FAQ, the monitoring checklist, timeline best practices by product type, troubleshooting, and success criteria.
- **[references/red-flags.md](references/red-flags.md)** — read this before sending the message to Legal and Support for review: common ways an EOL message, timeline, or migration plan goes wrong with bad/good examples anchored to the 4-phase framework.

## Scope & Limitations

**In Scope:** EOL message creation, timeline planning, segment-specific messaging, internal FAQ preparation, migration monitoring framework, customer objection handling, support team preparation.

**Out of Scope:** Replacement product development, data migration tooling implementation, legal contract review, refund processing, technical infrastructure decommissioning.

**Important Caveats:** EOL communication is only as good as the transition path behind it. If the replacement product isn't ready or the migration path is broken, the best-written message won't prevent customer frustration. Ensure migration tooling is tested before announcing.

## Integration Points

| Integration | Direction | What Flows |
|---|---|---|
| `create-prd/` | Complements | Replacement product PRD informs EOL transition narrative |
| `release-notes/` | Feeds into | Final product updates communicated alongside EOL timeline |
| `summarize-meeting/` | Receives from | EOL decision meeting notes inform communication content |
| `senior-pm/` | Receives from | Stakeholder map identifies high-risk accounts for personal outreach |
| `daci-framework/` | Complements | DACI chart clarifies who Drives the EOL decision and communication |
