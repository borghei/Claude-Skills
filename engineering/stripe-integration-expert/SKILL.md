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
  updated: 2026-06-15
  frameworks: stripe-subscriptions, webhook-handling, billing-infrastructure
---
# Stripe Integration Expert

The agent builds production-grade Stripe integrations for SaaS billing: subscription lifecycle management with trials and proration, idempotent webhook handlers, usage-based metered billing, Checkout sessions, Customer Portal, dunning recovery, and SCA/3D Secure compliance. Provides patterns for Next.js, Express, and Django with emphasis on real-world edge cases.

## Core Capabilities

- **Checkout & client setup** — pinned-version Stripe client, centralized plan config, Checkout sessions with trials, tax collection, and promo codes
- **Subscription lifecycle** — a state machine covering trialing → active → past_due → canceled, plus upgrades/downgrades with proration previews and reactivation
- **Idempotent webhooks** — signature verification, event dedup, re-fetch-from-API handlers, and retry-safe processing
- **Usage-based billing & gating** — metered usage records, feature gating by plan, and grace-period access logic
- **Dunning & SCA** — payment-failure email sequences and PSD2 / 3D Secure authentication flows
- **Local testing** — Stripe CLI webhook forwarding, event triggers, and test card matrix

## When to Use

- Building SaaS subscription billing from scratch on Next.js, Express, or Django
- Adding plan upgrades/downgrades with correct proration behavior
- Hardening or debugging a webhook endpoint for idempotency and retry safety
- Implementing metered/usage-based billing or feature gating by plan
- Adding dunning recovery or European SCA/3D Secure compliance

## Clarify First

Before building the integration, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Framework** — Next.js / Express / Django (the handler and client patterns differ per stack)
- [ ] **Billing model** — flat subscription / metered usage-based / trials + proration (shapes the subscription state machine and code)
- [ ] **Scope** — which piece: Checkout, idempotent webhooks, dunning, or SCA/3D Secure (selects the reference and code generated)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **api-design-reviewer** | Review billing API endpoints for REST conventions, error handling, and rate limiting | Billing route definitions --> API review checklist --> validated endpoint contracts |
| **database-schema-designer** | Design and validate the Prisma schema for Stripe customer, subscription, and event tracking tables | Schema requirements --> normalized table design --> migration files |
| **observability-designer** | Instrument webhook handlers and checkout flows with structured logging, metrics, and alerting | Webhook events --> OpenTelemetry traces --> dashboard alerts on failure spikes |
| **env-secrets-manager** | Manage Stripe API keys, webhook secrets, and price IDs across dev/staging/production | Secret definitions --> encrypted vault storage --> runtime injection via env vars |
| **ci-cd-pipeline-builder** | Automate Stripe CLI webhook testing in CI and validate integration before deployment | Test triggers --> `stripe listen` in CI --> webhook handler assertions |
| **runbook-generator** | Create operational runbooks for billing incidents: failed webhooks, mass payment failures, subscription reconciliation | Incident scenarios --> step-by-step remediation --> escalation paths |
