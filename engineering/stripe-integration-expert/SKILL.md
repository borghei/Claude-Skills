---
name: stripe-integration-expert
description: >
  Implement Stripe integrations for SaaS billing: subscriptions, checkout, proration, usage-
  based billing, idempotent webhooks, customer portal, dunning, and SCA. Use when building
  billing, handling webhooks, or testing with Stripe CLI.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: payments
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: stripe-subscriptions, webhook-handling, billing-infrastructure
  tags:
    - stripe
    - payments
    - subscriptions
    - webhooks
    - billing
---
# Stripe Integration Expert

The agent builds production-grade Stripe integrations for SaaS billing: subscription lifecycle management with trials and proration, idempotent webhook handlers, usage-based metered billing, Checkout sessions, Customer Portal, dunning recovery, and SCA/3D Secure compliance. Provides patterns for Next.js, Express, and Django with emphasis on real-world edge cases.

## Core Capabilities

- **Checkout & client setup** — pinned-version Stripe client, centralized plan config, Checkout sessions with trials, tax collection, and promo codes
- **Subscription lifecycle** — a state machine covering trialing → active → past_due → canceled, plus upgrades/downgrades with proration previews and reactivation
- **Idempotent webhooks** — signature verification, event dedup, re-fetch-from-API handlers, and retry-safe processing
- **Usage-based billing & gating** — Billing Meters and meter events, feature gating by plan, and grace-period access logic
- **Dunning & SCA** — payment-failure email sequences and PSD2 / 3D Secure authentication flows
- **Local testing** — Stripe CLI webhook forwarding, event triggers, and test card matrix

## When to Use

- Building SaaS subscription billing from scratch on Next.js, Express, or Django
- Adding plan upgrades/downgrades with correct proration behavior
- Hardening or debugging a webhook endpoint for idempotency and retry safety
- Implementing metered/usage-based billing or feature gating by plan
- Adding dunning recovery or European SCA/3D Secure compliance

## Clarify First

Before building the integration, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Framework:** Next.js / Express / Django (the handler and client patterns differ per stack).
- **Billing model:** flat subscription / metered usage-based / trials + proration (shapes the subscription state machine and code).
- **Scope:** which piece: Checkout, idempotent webhooks, dunning, or SCA/3D Secure (selects the reference and code generated).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

Three stdlib CLIs. The two checkers are regex-based: they confirm the common safeguards are
present, not that they are correct, so read the flagged handler before declaring it fixed.

| Tool | Purpose | Example (runs as written) |
|------|---------|---------|
| `scripts/webhook_validator.py` | Webhook handler check: signature verification, event dedup, required billing events, 200-on-error, hardcoded `whsec_` secrets (`--json`, `--strict` fails on warnings) | `python scripts/webhook_validator.py assets/sample_project_flawed` |
| `scripts/integration_auditor.py` | Integration audit: hardcoded keys, unpinned `apiVersion`, missing idempotency keys, hardcoded price IDs, checkout without metadata, `.env` exposure (`--json`, `--severity critical/warning/info`) | `python scripts/integration_auditor.py assets/sample_project_sound` |
| `scripts/checkout_scaffolder.py` | Generate checkout, webhook, subscription, portal and usage (meter events) code for `nextjs`, `express` or `django` (`--features`, `--all`, `--json`, `--list-features`) | `python scripts/checkout_scaffolder.py --framework nextjs --features checkout,webhooks` |

Exit codes: `0` pass; `1` critical findings (validator: also warnings under `--strict`, or
no webhook handler found); `2` bad input (path is not a directory, unknown feature). The
auditor exits `0` with status `NO_STRIPE_CODE` when the target contains no Stripe code, so
check the status rather than the exit code alone.

Samples: `assets/sample_project_flawed/` (unverified payload, no dedup, 5 billing events
missing, unpinned version, no checkout metadata) exits 1 on both checkers;
`assets/sample_project_sound/` exits 0 on both.

Before writing code that names an API version or a newer Stripe feature, check Stripe's API
changelog: pinned versions and billing APIs change yearly, and the references here are a
snapshot.

## Workflow

1. Settle the Clarify First inputs, then generate the pieces you need with `checkout_scaffolder.py` (or adapt the reference code).
2. Run both checkers on the project and fix every critical finding:
   ```bash
   python scripts/webhook_validator.py path/to/project --strict
   python scripts/integration_auditor.py path/to/project --severity warning
   ```
3. Test end to end with the Stripe CLI (`stripe listen --forward-to localhost:3000/api/webhooks/stripe`, then `stripe trigger invoice.payment_failed`) and verify that each handled event changes local state exactly once, including on a replay.
4. Done when both checkers exit 0, replayed events are no-ops, a failed handler returns 5xx and Stripe retries it, and the pinned `apiVersion` is the version your SDK ships with (2026-10-28.endive for stripe-node 23.1.0, as of November 2026).

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/payment-flows.md](references/payment-flows.md)** — Stripe client setup, plan config, Checkout sessions, Customer Portal, and SCA/3D Secure. Read when wiring up the client or building the checkout/portal redirects.
- **[references/subscriptions.md](references/subscriptions.md)** — lifecycle state-machine diagram, upgrade/downgrade/preview/cancel code, usage-based billing, feature gating, and the Prisma schema. Read when modeling subscription state or implementing plan changes.
- **[references/webhooks.md](references/webhooks.md)** — the full idempotent webhook handler with signature verification and every event handler. Read when building or auditing the webhook endpoint.
- **[references/testing-and-troubleshooting.md](references/testing-and-troubleshooting.md)** — Stripe CLI testing, common pitfalls, troubleshooting table, and success criteria. Read when testing locally or diagnosing a billing bug.

## Related Skills

| Skill | Use When |
|-------|----------|
| **ab-test-setup** | Testing pricing page variants and checkout flows |
| **analytics-tracking** | Tracking checkout and subscription conversion events |
| **email-template-builder** | Building dunning and billing notification emails |
| **api-design-reviewer** | Reviewing your billing API endpoints |

## Scope & Limitations

**This skill covers:**
- Stripe Checkout, Subscriptions, and Customer Portal integration for SaaS billing
- Webhook handling with idempotency, signature verification, and retry safety
- Usage-based (metered) billing, proration previews, and plan change workflows
- SCA/3D Secure compliance for European payment regulations (PSD2)

**This skill does NOT cover:**
- Stripe Connect (marketplace payouts, multi-party payments) -- see platform-specific Stripe Connect documentation
- One-time payment flows without subscriptions (e.g., e-commerce product purchases)
- Tax calculation and remittance (Stripe Tax configuration, VAT/GST filing) -- see `ra-qm-team/` compliance skills for regulatory guidance
- Payment fraud detection and dispute management (Stripe Radar rules, chargeback workflows) -- see `skill-security-auditor` for security review patterns

## Anti-Patterns

### Trusting the Event Payload
**Mistake:** Acting on `JSON.parse(body)` without `constructEvent`, or on stale object state in the event.
**Why it happens:** Local testing works without signatures, and the payload already contains the object.
**Instead:** Verify the signature against the raw body, then re-fetch the subscription or invoice from the API before writing state. Events arrive out of order and can be replayed.

### Returning 200 When Processing Fails
**Mistake:** Catching every error in the webhook handler and answering 200.
**Why it happens:** It silences Stripe's retry emails.
**Instead:** Return 5xx on processing failure so Stripe retries, and make the handler idempotent on `event.id` so retries are safe.

### Timestamp Identifiers for Usage
**Mistake:** Keying meter events or idempotency keys on `Date.now()`.
**Why it happens:** It looks unique.
**Instead:** Use a stable business identifier (request ID, job ID). A timestamp changes on retry, so the same usage is billed twice.

## Files

| File | Purpose |
|------|---------|
| `scripts/webhook_validator.py` | Webhook handler safeguards check |
| `scripts/integration_auditor.py` | Integration anti-pattern audit |
| `scripts/checkout_scaffolder.py` | Framework boilerplate generator |
| `assets/sample_project_flawed/stripe_webhook.ts` | Flawed handler and checkout (checkers exit 1) |
| `assets/sample_project_sound/stripe_webhook.ts` | Sound handler and checkout (checkers exit 0) |
| `references/*.md` | Payment flows, subscriptions and meters, webhooks, testing |
