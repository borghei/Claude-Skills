---
name: eol-communication
description: >
  Plan and write end-of-life announcements with dated milestones, a working
  migration path and per-segment messages. Use when sunsetting a product,
  feature, API version or pricing tier.
license: MIT + Commons Clause
metadata:
  version: 1.0.2
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  tech-stack: eol, product-lifecycle, change-communication
  tags:
    - end-of-life
    - sunset
    - deprecation
    - customer-communication
---
# EOL Communication Expert

## Overview

Create clear, empathetic End-of-Life (EOL) communications that preserve customer trust and facilitate smooth transitions. Sunsetting a product is a high-stakes communication challenge -- done poorly, it damages brand trust and accelerates churn across your entire portfolio. Done well, it strengthens customer relationships and drives migration to replacement solutions.

The work runs in four phases: **(1) Pre-announcement planning** (what, why, who, when, what support, what risks), **(2) Craft the message** (transition narrative, customer impact, transition solution, timeline, one CTA), **(3) Segment and distribute** (different message and channel per segment), **(4) Support and monitor** (support FAQ, migration tracking, churn watch). See the playbook reference for the full framework, templates, and timeline guidance.

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

## Clarify First

Before crafting the EOL communication, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **What is being sunset and why:** drives the transition narrative and Phase 1 planning; a vague "why" reads as abandonment.
- **Replacement / migration path:** drives the transition solution and the single CTA; if it is broken or absent, do not announce yet.
- **Timeline and key dates:** drives the timeline section and varies sharply by product type (API vs paid product vs free feature).
- **Customer segments affected:** drives the Phase 3 segment/channel matrix; high-value accounts need different message and outreach than self-serve.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Plan** (phase 1): what ends, why, who is affected, the replacement, the dated milestones, and the support plan.
2. **Prove the migration path** before announcing: real customers have moved on the path you will recommend.
3. **Write the message** (phase 2): transition narrative, customer impact, the migration path, the dated timeline, one call to action.
4. **Segment** (phase 3): a different message and channel for high-value accounts, self-serve users and API consumers.
5. **Brief customer-facing staff first**, then announce, then monitor migration and churn weekly (phase 4).

**Verify** before sending: every milestone has a date; the draft has no "coming months" or "soon"; support, sales and CS have the internal FAQ; the CTA links to a path that works today. Templates and timelines by product type: `references/playbook.md`.

## Anti-Patterns

### Announcing before the migration path works
**Mistake:** The EOL email goes out while the migration tool is still "coming soon". Customers try it at launch, it breaks, and the support queue floods.
**Why it happens:** The shutdown date is set and the announcement feels urgent, so the tooling is assumed to catch up.
**Instead:** Treat a working migration path as a gate. A default [RECOMMENDED]: announce once about 10 real customers have migrated in production on the path you will recommend. Ten is enough to surface the common failure modes; for a product with a handful of enterprise accounts, use most of them instead.

### Vague timeline
**Mistake:** The message says "in the coming months" or "later this year" with no dates.
**Why it happens:** Some dates are not locked yet, and soft wording feels safer than committing.
**Instead:** Search the draft for "coming", "later", "in due course" and "soon", and replace each with a date. Give every milestone a date: announcement, new signups closed, feature freeze, data export deadline, shutdown.

### Customer-facing staff learn from customers
**Mistake:** Internal Slack hears about the EOL a minute after the public post, and a sales rep first hears of it from a customer on a call.
**Why it happens:** Internal comms feel like a formality next to the external message.
**Instead:** Brief sales, CS and support before the external announcement, with the internal FAQ in hand. 7-10 business days is a common default: long enough to rehearse answers and line up key-account calls, short enough not to leak. Before T-0, ask 3 customer-facing employees what the EOL message is. If they hesitate, hold the announcement.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## Files

| File | Purpose |
|---|---|
| `references/playbook.md` | Four-phase framework, message template, segment matrix, internal FAQ, timelines |
| `references/red-flags.md` | Bad/good announcements with fixes |
| `examples/sunsetting-classic-reports.md` | Worked sunset |

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
