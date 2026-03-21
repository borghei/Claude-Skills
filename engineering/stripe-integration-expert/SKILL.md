---
name: stripe-integration-expert
description: Implement production-grade Stripe integrations for SaaS billing. Covers subscription lifecycle management, checkout sessions, plan upgrades/downgrades with proration, usage-based billing, idempotent webhook handlers, customer portal, dunning, SCA compliance, and local testing with Stripe CLI. Provides patterns for Next.js, Express, and Django.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: payments
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: stripe-subscriptions, webhook-handling, billing-infrastructure
---

# Stripe Integration Expert

**Tier:** POWERFUL
**Category:** Engineering
**Tags:** Stripe, payments, subscriptions, billing, webhooks, SCA, usage-based billing

## Overview

Build production-grade Stripe integrations for SaaS products: subscriptions with trials and proration, one-time payments, usage-based billing, Checkout sessions, idempotent webhook handlers, Customer Portal, invoicing, and dunning. Covers Next.js App Router, Express, and Django patterns with emphasis on real-world edge cases that documentation does not warn you about.

---

## Subscription Lifecycle State Machine

Understand this before writing any code. Every billing edge case maps to a state transition.

```
                    ┌────────────────────────────────────────┐
                    │                                        │
 ┌──────────┐   paid    ┌────────┐   cancel    ┌──────────────┐   period_end   ┌──────────┐
 │ TRIALING │──────────▶│ ACTIVE │────────────▶│ CANCEL_PENDING│──────────────▶│ CANCELED │
 └──────────┘           └────────┘             └──────────────┘               └──────────┘
      │                     │                                                      ▲
      │                     │  upgrade                                             │
      │                     ▼                                                  reactivate
      │                ┌──────────┐  period_end  ┌────────┐                        │
      │                │UPGRADING │─────────────▶│ ACTIVE │                        │
      │                └──────────┘  (new plan)  └────────┘                        │
      │                                                                            │
      │  trial_end      ┌──────────┐  3x fail   ┌──────────┐                      │
      └─(no payment)───▶│ PAST_DUE │───────────▶│ CANCELED │──────────────────────┘
                        └──────────┘             └──────────┘
                             │
                        payment_success
                             │
                             ▼
                        ┌────────┐
                        │ ACTIVE │
                        └────────┘
```

**DB status values:** `trialing | active | past_due | canceled | cancel_pending | paused | unpaid`

---

## Stripe Client Setup

```typescript
// lib/stripe.ts
import Stripe from "stripe";

if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error("STRIPE_SECRET_KEY is required");
}

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: "2024-12-18.acacia",  // Pin to specific version
  typescript: true,
  appInfo: {
    name: "your-app-name",
    version: "1.0.0",
    url: "https://yourapp.com",
  },
});

// Centralized plan configuration
export const PLANS = {
  starter: {
    monthly: process.env.STRIPE_STARTER_MONTHLY_PRICE!,
    yearly: process.env.STRIPE_STARTER_YEARLY_PRICE!,
    limits: { projects: 5, events: 10_000 },
  },
  pro: {
    monthly: process.env.STRIPE_PRO_MONTHLY_PRICE!,
    yearly: process.env.STRIPE_PRO_YEARLY_PRICE!,
    limits: { projects: -1, events: 1_000_000 },  // -1 = unlimited
  },
  enterprise: {
    monthly: process.env.STRIPE_ENTERPRISE_MONTHLY_PRICE!,
    yearly: process.env.STRIPE_ENTERPRISE_YEARLY_PRICE!,
    limits: { projects: -1, events: -1 },
  },
} as const;

export type PlanName = keyof typeof PLANS;
export type BillingInterval = "monthly" | "yearly";
```

---

## Checkout Session

```typescript
// app/api/billing/checkout/route.ts
import { NextResponse } from "next/server";
import { stripe, PLANS, type PlanName, type BillingInterval } from "@/lib/stripe";
import { getAuthUser } from "@/lib/auth";
import { db } from "@/lib/db";

export async function POST(req: Request) {
  const user = await getAuthUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { plan, interval = "monthly" } = (await req.json()) as {
    plan: PlanName;
    interval: BillingInterval;
  };

  if (!PLANS[plan]) {
    return NextResponse.json({ error: "Invalid plan" }, { status: 400 });
  }

  const priceId = PLANS[plan][interval];

  // Get or create Stripe customer (idempotent)
  let customerId = user.stripeCustomerId;
  if (!customerId) {
    const customer = await stripe.customers.create({
      email: user.email,
      name: user.name || undefined,
      metadata: { userId: user.id, source: "checkout" },
    });
    customerId = customer.id;
    await db.user.update({
      where: { id: user.id },
      data: { stripeCustomerId: customerId },
    });
  }

  const session = await stripe.checkout.sessions.create({
    customer: customerId,
    mode: "subscription",
    payment_method_types: ["card"],
    line_items: [{ price: priceId, quantity: 1 }],
    allow_promotion_codes: true,
    tax_id_collection: { enabled: true },
    subscription_data: {
      trial_period_days: user.hasHadTrial ? undefined : 14,
      metadata: { userId: user.id, plan },
    },
    success_url: `${process.env.APP_URL}/dashboard?checkout=success&session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.APP_URL}/pricing`,
    metadata: { userId: user.id },
  });

  return NextResponse.json({ url: session.url });
}
```

---

## Subscription Management

### Upgrade (Immediate, Prorated)

```typescript
export async function upgradeSubscription(subscriptionId: string, newPriceId: string) {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);
  const currentItem = subscription.items.data[0];

  return stripe.subscriptions.update(subscriptionId, {
    items: [{ id: currentItem.id, price: newPriceId }],
    proration_behavior: "always_invoice",  // Charge difference immediately
    billing_cycle_anchor: "unchanged",      // Keep same billing date
  });
}
```

### Downgrade (End of Period, No Proration)

```typescript
export async function downgradeSubscription(subscriptionId: string, newPriceId: string) {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);
  const currentItem = subscription.items.data[0];

  // Schedule change for end of current period
  return stripe.subscriptions.update(subscriptionId, {
    items: [{ id: currentItem.id, price: newPriceId }],
    proration_behavior: "none",            // No refund
    billing_cycle_anchor: "unchanged",
  });
}
```

### Preview Proration (Show Before Confirming)

```typescript
export async function previewProration(subscriptionId: string, newPriceId: string) {
  const subscription = await stripe.subscriptions.retrieve(subscriptionId);

  const invoice = await stripe.invoices.createPreview({
    customer: subscription.customer as string,
    subscription: subscriptionId,
    subscription_details: {
      items: [{ id: subscription.items.data[0].id, price: newPriceId }],
      proration_date: Math.floor(Date.now() / 1000),
    },
  });

  return {
    amountDue: invoice.amount_due,            // In cents
    credit: invoice.total < 0 ? Math.abs(invoice.total) : 0,
    lineItems: invoice.lines.data.map(line => ({
      description: line.description,
      amount: line.amount,
    })),
  };
}
```

### Cancel (At Period End)

```typescript
export async function cancelSubscription(subscriptionId: string) {
  // Cancel at period end -- user keeps access until their paid period expires
  return stripe.subscriptions.update(subscriptionId, {
    cancel_at_period_end: true,
  });
}

export async function reactivateSubscription(subscriptionId: string) {
  // Undo pending cancellation
  return stripe.subscriptions.update(subscriptionId, {
    cancel_at_period_end: false,
  });
}
```

---

## Webhook Handler (Idempotent)

This is the most critical code in your billing system. Get this right.

```typescript
// app/api/webhooks/stripe/route.ts
import { NextResponse } from "next/server";
import { headers } from "next/headers";
import { stripe } from "@/lib/stripe";
import { db } from "@/lib/db";
import type Stripe from "stripe";

// Idempotency: track processed events to handle Stripe retries
async function isProcessed(eventId: string): Promise<boolean> {
  return !!(await db.stripeEvent.findUnique({ where: { id: eventId } }));
}

async function markProcessed(eventId: string, type: string) {
  await db.stripeEvent.create({
    data: { id: eventId, type, processedAt: new Date() },
  });
}

export async function POST(req: Request) {
  const body = await req.text();
  const signature = headers().get("stripe-signature");

  if (!signature) {
    return NextResponse.json({ error: "Missing signature" }, { status: 400 });
  }

  // Step 1: Verify webhook signature
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(
      body, signature, process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err) {
    console.error("Webhook signature verification failed:", err);
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  // Step 2: Idempotency check
  if (await isProcessed(event.id)) {
    return NextResponse.json({ received: true, deduplicated: true });
  }

  // Step 3: Handle events
  try {
    switch (event.type) {
      case "checkout.session.completed":
        await handleCheckoutCompleted(event.data.object as Stripe.Checkout.Session);
        break;
      case "customer.subscription.created":
      case "customer.subscription.updated":
        await handleSubscriptionChange(event.data.object as Stripe.Subscription);
        break;
      case "customer.subscription.deleted":
        await handleSubscriptionDeleted(event.data.object as Stripe.Subscription);
        break;
      case "invoice.payment_succeeded":
        await handlePaymentSucceeded(event.data.object as Stripe.Invoice);
        break;
      case "invoice.payment_failed":
        await handlePaymentFailed(event.data.object as Stripe.Invoice);
        break;
      case "customer.subscription.trial_will_end":
        await handleTrialEnding(event.data.object as Stripe.Subscription);
        break;
      default:
        // Log unhandled events for monitoring
        console.log(`Unhandled webhook: ${event.type}`);
    }

    await markProcessed(event.id, event.type);
    return NextResponse.json({ received: true });
  } catch (err) {
    console.error(`Webhook processing failed [${event.type}]:`, err);
    // Return 500 so Stripe retries. Do NOT mark as processed.
    return NextResponse.json({ error: "Processing failed" }, { status: 500 });
  }
}

// --- Handler implementations ---

async function handleCheckoutCompleted(session: Stripe.Checkout.Session) {
  if (session.mode !== "subscription") return;

  const userId = session.metadata?.userId;
  if (!userId) throw new Error("Missing userId in checkout metadata");

  // Always re-fetch from Stripe API -- event data may be stale
  const subscription = await stripe.subscriptions.retrieve(
    session.subscription as string
  );

  await db.user.update({
    where: { id: userId },
    data: {
      stripeCustomerId: session.customer as string,
      stripeSubscriptionId: subscription.id,
      stripePriceId: subscription.items.data[0].price.id,
      stripeCurrentPeriodEnd: new Date(subscription.current_period_end * 1000),
      subscriptionStatus: subscription.status,
      hasHadTrial: true,
    },
  });
}

async function handleSubscriptionChange(subscription: Stripe.Subscription) {
  // Find user by subscription ID first, fall back to customer ID
  const user = await db.user.findFirst({
    where: {
      OR: [
        { stripeSubscriptionId: subscription.id },
        { stripeCustomerId: subscription.customer as string },
      ],
    },
  });
  if (!user) {
    console.warn(`No user for subscription ${subscription.id}`);
    return;  // Don't throw -- this may be a subscription we don't manage
  }

  await db.user.update({
    where: { id: user.id },
    data: {
      stripeSubscriptionId: subscription.id,
      stripePriceId: subscription.items.data[0].price.id,
      stripeCurrentPeriodEnd: new Date(subscription.current_period_end * 1000),
      subscriptionStatus: subscription.status,
      cancelAtPeriodEnd: subscription.cancel_at_period_end,
    },
  });
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  await db.user.updateMany({
    where: { stripeSubscriptionId: subscription.id },
    data: {
      subscriptionStatus: "canceled",
      stripePriceId: null,
      stripeCurrentPeriodEnd: null,
      cancelAtPeriodEnd: false,
    },
  });
}

async function handlePaymentSucceeded(invoice: Stripe.Invoice) {
  if (!invoice.subscription) return;

  await db.user.updateMany({
    where: { stripeSubscriptionId: invoice.subscription as string },
    data: {
      subscriptionStatus: "active",
      stripeCurrentPeriodEnd: new Date(invoice.period_end * 1000),
    },
  });
}

async function handlePaymentFailed(invoice: Stripe.Invoice) {
  if (!invoice.subscription) return;

  await db.user.updateMany({
    where: { stripeSubscriptionId: invoice.subscription as string },
    data: { subscriptionStatus: "past_due" },
  });

  // Dunning: send appropriate email based on attempt count
  const attemptCount = invoice.attempt_count || 1;
  if (attemptCount === 1) {
    // First failure: gentle reminder
    await sendDunningEmail(invoice.customer_email!, "first_failure");
  } else if (attemptCount === 2) {
    // Second failure: more urgent
    await sendDunningEmail(invoice.customer_email!, "second_failure");
  } else if (attemptCount >= 3) {
    // Final failure: last chance before cancellation
    await sendDunningEmail(invoice.customer_email!, "final_notice");
  }
}

async function handleTrialEnding(subscription: Stripe.Subscription) {
  // Stripe sends this 3 days before trial ends
  const user = await db.user.findFirst({
    where: { stripeSubscriptionId: subscription.id },
  });
  if (user?.email) {
    await sendTrialEndingEmail(user.email, subscription.trial_end!);
  }
}
```

---

## Usage-Based Billing

```typescript
// Report metered usage
export async function reportUsage(
  subscriptionItemId: string,
  quantity: number,
  idempotencyKey?: string,
) {
  return stripe.subscriptionItems.createUsageRecord(
    subscriptionItemId,
    {
      quantity,
      timestamp: Math.floor(Date.now() / 1000),
      action: "increment",  // or "set" for absolute values
    },
    {
      idempotencyKey,  // Prevent double-counting on retries
    }
  );
}

// Middleware: track API usage per request
export async function trackApiUsage(userId: string) {
  const user = await db.user.findUnique({ where: { id: userId } });
  if (!user?.stripeSubscriptionId) return;

  const subscription = await stripe.subscriptions.retrieve(user.stripeSubscriptionId);
  const meteredItem = subscription.items.data.find(
    (item) => item.price.recurring?.usage_type === "metered"
  );

  if (meteredItem) {
    await reportUsage(meteredItem.id, 1, `${userId}-${Date.now()}`);
  }
}
```

---

## Customer Portal

```typescript
// app/api/billing/portal/route.ts
export async function POST() {
  const user = await getAuthUser();
  if (!user?.stripeCustomerId) {
    return NextResponse.json({ error: "No billing account" }, { status: 400 });
  }

  const session = await stripe.billingPortal.sessions.create({
    customer: user.stripeCustomerId,
    return_url: `${process.env.APP_URL}/settings/billing`,
  });

  return NextResponse.json({ url: session.url });
}
```

**Portal configuration** (must be done in Stripe Dashboard > Billing > Customer Portal):
- Enable: Update subscription, cancel subscription, update payment method
- Set cancellation flow: show pause option, require reason
- Configure plan change options: which plans can switch to which

---

## Feature Gating

```typescript
// lib/subscription.ts
import { PLANS, type PlanName } from "./stripe";

export function isSubscriptionActive(user: {
  subscriptionStatus: string | null;
  stripeCurrentPeriodEnd: Date | null;
}): boolean {
  if (!user.subscriptionStatus) return false;

  // Active or trialing = full access
  if (["active", "trialing"].includes(user.subscriptionStatus)) return true;

  // Past due: grace period until period end
  if (user.subscriptionStatus === "past_due" && user.stripeCurrentPeriodEnd) {
    return user.stripeCurrentPeriodEnd > new Date();
  }

  // Cancel pending: access until period end
  if (user.subscriptionStatus === "cancel_pending" && user.stripeCurrentPeriodEnd) {
    return user.stripeCurrentPeriodEnd > new Date();
  }

  return false;
}

export function getUserPlan(stripePriceId: string | null): PlanName | "free" {
  if (!stripePriceId) return "free";

  for (const [plan, config] of Object.entries(PLANS)) {
    if (config.monthly === stripePriceId || config.yearly === stripePriceId) {
      return plan as PlanName;
    }
  }

  return "free";
}

export function canAccess(user: { stripePriceId: string | null }, feature: string): boolean {
  const plan = getUserPlan(user.stripePriceId);
  const limits = plan === "free" ? { projects: 1, events: 1000 } : PLANS[plan].limits;

  // Feature-specific checks
  switch (feature) {
    case "unlimited_projects": return limits.projects === -1;
    case "api_access": return plan !== "free" && plan !== "starter";
    default: return plan !== "free";
  }
}
```

---

## SCA (Strong Customer Authentication) Compliance

Required for European customers under PSD2.

```typescript
// Checkout Sessions handle SCA automatically (3D Secure)
// For existing subscriptions, handle authentication_required:

async function handlePaymentRequiresAction(invoice: Stripe.Invoice) {
  if (invoice.payment_intent) {
    const pi = await stripe.paymentIntents.retrieve(invoice.payment_intent as string);
    if (pi.status === "requires_action") {
      // Send email with link to complete authentication
      await sendAuthenticationEmail(
        invoice.customer_email!,
        pi.next_action?.redirect_to_url?.url || `${process.env.APP_URL}/billing/authenticate`
      );
    }
  }
}
```

---

## Testing with Stripe CLI

```bash
# Install and authenticate
brew install stripe/stripe-cli/stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:3000/api/webhooks/stripe

# Trigger specific events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.updated
stripe trigger invoice.payment_failed
stripe trigger customer.subscription.trial_will_end

# Test card numbers
# Success:               4242 4242 4242 4242
# Requires 3D Secure:    4000 0025 0000 3155
# Declined:              4000 0000 0000 0002
# Insufficient funds:    4000 0000 0000 9995
# Expired card:          4000 0000 0000 0069

# View recent events
stripe events list --limit 10

# Inspect a specific event
stripe events retrieve evt_xxx
```

---

## Database Schema (Prisma)

```prisma
model User {
  id                      String    @id @default(cuid())
  email                   String    @unique
  name                    String?

  // Stripe fields
  stripeCustomerId        String?   @unique
  stripeSubscriptionId    String?   @unique
  stripePriceId           String?
  stripeCurrentPeriodEnd  DateTime?
  subscriptionStatus      String?   // trialing, active, past_due, canceled, cancel_pending
  cancelAtPeriodEnd       Boolean   @default(false)
  hasHadTrial             Boolean   @default(false)
}

model StripeEvent {
  id          String   @id          // Stripe event ID (evt_xxx)
  type        String                // Event type
  processedAt DateTime @default(now())

  @@index([type])
}
```

---

## Common Pitfalls

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| Trusting webhook event data | Stale data, race conditions | Always re-fetch from Stripe API in handlers |
| No idempotency on webhooks | Double-charges, duplicate records | Track processed event IDs in database |
| Missing metadata on checkout | Cannot link subscription to user | Always pass `userId` in metadata |
| Proration surprises | Users charged unexpected amounts | Always preview proration before upgrade |
| Not handling `past_due` | Users lose access without warning | Implement dunning emails on payment failure |
| Skipping trial abuse prevention | Users create multiple accounts for free trials | Store `hasHadTrial: true`, check on checkout |
| Customer Portal not configured | Portal returns blank page | Enable features in Stripe Dashboard first |
| Webhook endpoint not idempotent | Stripe retries cause duplicate processing | Idempotency table with event ID dedup |
| Not pinning API version | Breaking changes on Stripe updates | Pin `apiVersion` in client constructor |
| Ignoring `trial_will_end` event | Users surprised when trial ends | Send reminder email 3 days before |

---

## Related Skills

| Skill | Use When |
|-------|----------|
| **ab-test-setup** | Testing pricing page variants and checkout flows |
| **analytics-tracking** | Tracking checkout and subscription conversion events |
| **email-template-builder** | Building dunning and billing notification emails |
| **api-design-reviewer** | Reviewing your billing API endpoints |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Webhook returns 400 on all events | Webhook signing secret mismatch between environments | Verify `STRIPE_WEBHOOK_SECRET` matches the endpoint in Stripe Dashboard; use `stripe listen` output secret for local dev |
| Checkout session redirects to blank page | `success_url` or `cancel_url` missing `{CHECKOUT_SESSION_ID}` template or pointing to wrong domain | Ensure URLs use `APP_URL` env var and include the session ID template literal for retrieval |
| Subscription shows `incomplete` status | First payment requires 3D Secure but was never completed | Handle `checkout.session.async_payment_failed` and send the customer a link to complete authentication |
| Proration invoice charges full price instead of difference | Using `create_prorations` instead of `always_invoice` or not passing existing subscription item ID | Use `always_invoice` proration behavior and update the existing `items[0].id` rather than adding a new line item |
| Usage records return "Cannot create usage record" | Reporting usage on a non-metered price or after subscription cancellation | Confirm the price uses `recurring.usage_type: "metered"` and the subscription is active before reporting |
| Customer Portal shows no options | Portal configuration not enabled in Stripe Dashboard | Navigate to Stripe Dashboard > Settings > Billing > Customer Portal and enable subscription management features |
| Duplicate webhook processing despite idempotency table | `markProcessed` called before handler completes, then handler throws on retry | Move `markProcessed` to after the handler succeeds (as shown in the webhook handler pattern above) |

---

## Success Criteria

- **Webhook reliability:** 99.9%+ webhook processing success rate with zero duplicate side effects over a 30-day window
- **Checkout conversion:** End-to-end checkout flow completes in under 3 seconds (redirect to Stripe and back)
- **Idempotency coverage:** 100% of webhook handlers are idempotent, verified by replaying the same event ID twice with no state change on the second pass
- **Subscription state accuracy:** Database subscription status matches Stripe source of truth within 60 seconds of any state change
- **SCA compliance:** All European payment flows pass 3D Secure challenges without manual intervention or dropped transactions
- **Dunning recovery:** Automated dunning emails recover at least 30% of failed payments within the retry window (typically 7-21 days)
- **Zero hardcoded price IDs:** All Stripe price IDs are sourced from environment variables, enabling test/production parity without code changes

---

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

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **api-design-reviewer** | Review billing API endpoints for REST conventions, error handling, and rate limiting | Billing route definitions --> API review checklist --> validated endpoint contracts |
| **database-schema-designer** | Design and validate the Prisma schema for Stripe customer, subscription, and event tracking tables | Schema requirements --> normalized table design --> migration files |
| **observability-designer** | Instrument webhook handlers and checkout flows with structured logging, metrics, and alerting | Webhook events --> OpenTelemetry traces --> dashboard alerts on failure spikes |
| **env-secrets-manager** | Manage Stripe API keys, webhook secrets, and price IDs across dev/staging/production | Secret definitions --> encrypted vault storage --> runtime injection via env vars |
| **ci-cd-pipeline-builder** | Automate Stripe CLI webhook testing in CI and validate integration before deployment | Test triggers --> `stripe listen` in CI --> webhook handler assertions |
| **runbook-generator** | Create operational runbooks for billing incidents: failed webhooks, mass payment failures, subscription reconciliation | Incident scenarios --> step-by-step remediation --> escalation paths |
