# Subscriptions — Lifecycle, Plan Changes, Usage & Gating

Read this when modeling subscription state, implementing upgrades/downgrades with proration, reporting metered usage, gating features by plan, or designing the persistence schema. Every billing edge case maps to a state transition below.

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

## Usage-Based Billing

Current Stripe API versions bill usage through **Billing Meters**: you define a meter
(event name, aggregation such as sum or count), attach a metered price to it, and send
**meter events** keyed by customer. The legacy `subscriptionItems.createUsageRecord` /
usage-record API was removed from current API versions; do not generate it. Check the
Stripe docs for the exact meter options your account's API version supports.

```typescript
// One-time setup (Dashboard or API): a meter that sums "value" per customer
// await stripe.billing.meters.create({
//   display_name: "API requests",
//   event_name: "api_requests",
//   default_aggregation: { formula: "sum" },
// });
// Then create a recurring price with recurring.usage_type = "metered" and recurring.meter = meter.id.

// Report usage per request
export async function reportUsage(stripeCustomerId: string, value: number, identifier: string) {
  return stripe.billing.meterEvents.create({
    event_name: "api_requests",
    payload: { stripe_customer_id: stripeCustomerId, value: String(value) },
    identifier, // unique per event; Stripe dedupes repeats, so retries do not double-count
  });
}

export async function trackApiUsage(userId: string, requestId: string) {
  const user = await db.user.findUnique({ where: { id: userId } });
  if (!user?.stripeCustomerId) return;
  await reportUsage(user.stripeCustomerId, 1, `${userId}-${requestId}`);
}
```

Use a stable identifier (the request or job ID), not `Date.now()`: a timestamp changes on
retry and defeats deduplication. For high volume, aggregate locally and send one event per
customer per interval rather than one per request.

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
