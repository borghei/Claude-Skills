# Payment Flows — Client Setup, Checkout, Portal & SCA

Read this when wiring up the Stripe client, building the Checkout redirect, exposing the Customer Portal, or handling European SCA/3D Secure authentication.

## Stripe Client Setup

```typescript
// lib/stripe.ts
import Stripe from "stripe";

if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error("STRIPE_SECRET_KEY is required");
}

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  // Pin to the version your SDK ships with (its types match that version);
  // upgrade deliberately after reading Stripe's API changelog.
  apiVersion: "2026-10-28.endive",  // as of stripe-node 23.1.0
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
