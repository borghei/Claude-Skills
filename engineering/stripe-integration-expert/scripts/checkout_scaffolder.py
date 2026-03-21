#!/usr/bin/env python3
"""Stripe Checkout & Subscription Boilerplate Generator.

Generates production-ready Stripe Checkout integration code for different
frameworks. Includes checkout session creation, webhook handler, subscription
management, and customer portal setup.

Usage:
    python checkout_scaffolder.py --framework nextjs --features subscriptions,portal
    python checkout_scaffolder.py --framework express --features checkout,webhooks --json
    python checkout_scaffolder.py --list-frameworks
    python checkout_scaffolder.py --list-features
"""

import argparse
import json
import sys
import textwrap
from datetime import datetime

FRAMEWORKS = {
    "nextjs": "Next.js App Router (TypeScript)",
    "express": "Express.js (TypeScript)",
    "django": "Django (Python)",
}

FEATURES = {
    "checkout": "Checkout session creation endpoint",
    "webhooks": "Idempotent webhook handler with signature verification",
    "subscriptions": "Subscription management (upgrade, downgrade, cancel)",
    "portal": "Customer portal session endpoint",
    "usage": "Usage-based (metered) billing helpers",
}

# ---------------------------------------------------------------------------
# Code templates per framework per feature
# ---------------------------------------------------------------------------

TEMPLATES = {}

# ── Next.js ────────────────────────────────────────────────────────────────

TEMPLATES[("nextjs", "checkout")] = textwrap.dedent('''\
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
          metadata: { userId: user.id },
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
''')

TEMPLATES[("nextjs", "webhooks")] = textwrap.dedent('''\
    // app/api/webhooks/stripe/route.ts
    import { NextResponse } from "next/server";
    import { headers } from "next/headers";
    import { stripe } from "@/lib/stripe";
    import { db } from "@/lib/db";
    import type Stripe from "stripe";

    async function isProcessed(eventId: string): Promise<boolean> {
      return !!(await db.stripeEvent.findUnique({ where: { id: eventId } }));
    }

    async function markProcessed(eventId: string, type: string) {
      await db.stripeEvent.create({ data: { id: eventId, type, processedAt: new Date() } });
    }

    export async function POST(req: Request) {
      const body = await req.text();
      const signature = headers().get("stripe-signature");
      if (!signature) return NextResponse.json({ error: "Missing signature" }, { status: 400 });

      let event: Stripe.Event;
      try {
        event = stripe.webhooks.constructEvent(body, signature, process.env.STRIPE_WEBHOOK_SECRET!);
      } catch (err) {
        console.error("Webhook signature verification failed:", err);
        return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
      }

      if (await isProcessed(event.id)) {
        return NextResponse.json({ received: true, deduplicated: true });
      }

      try {
        switch (event.type) {
          case "checkout.session.completed":
            await handleCheckoutCompleted(event.data.object as Stripe.Checkout.Session);
            break;
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
          default:
            console.log(`Unhandled webhook: ${event.type}`);
        }

        await markProcessed(event.id, event.type);
        return NextResponse.json({ received: true });
      } catch (err) {
        console.error(`Webhook error [${event.type}]:`, err);
        return NextResponse.json({ error: "Processing failed" }, { status: 500 });
      }
    }

    // TODO: Implement handler functions (handleCheckoutCompleted, etc.)
    // See SKILL.md for full handler implementations.
''')

TEMPLATES[("nextjs", "subscriptions")] = textwrap.dedent('''\
    // lib/subscriptions.ts
    import { stripe } from "@/lib/stripe";

    export async function upgradeSubscription(subscriptionId: string, newPriceId: string) {
      const subscription = await stripe.subscriptions.retrieve(subscriptionId);
      return stripe.subscriptions.update(subscriptionId, {
        items: [{ id: subscription.items.data[0].id, price: newPriceId }],
        proration_behavior: "always_invoice",
        billing_cycle_anchor: "unchanged",
      });
    }

    export async function downgradeSubscription(subscriptionId: string, newPriceId: string) {
      const subscription = await stripe.subscriptions.retrieve(subscriptionId);
      return stripe.subscriptions.update(subscriptionId, {
        items: [{ id: subscription.items.data[0].id, price: newPriceId }],
        proration_behavior: "none",
        billing_cycle_anchor: "unchanged",
      });
    }

    export async function cancelSubscription(subscriptionId: string) {
      return stripe.subscriptions.update(subscriptionId, {
        cancel_at_period_end: true,
      });
    }

    export async function reactivateSubscription(subscriptionId: string) {
      return stripe.subscriptions.update(subscriptionId, {
        cancel_at_period_end: false,
      });
    }

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
        amountDue: invoice.amount_due,
        credit: invoice.total < 0 ? Math.abs(invoice.total) : 0,
        lineItems: invoice.lines.data.map((l) => ({ description: l.description, amount: l.amount })),
      };
    }
''')

TEMPLATES[("nextjs", "portal")] = textwrap.dedent('''\
    // app/api/billing/portal/route.ts
    import { NextResponse } from "next/server";
    import { stripe } from "@/lib/stripe";
    import { getAuthUser } from "@/lib/auth";

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
''')

TEMPLATES[("nextjs", "usage")] = textwrap.dedent('''\
    // lib/usage-billing.ts
    import { stripe } from "@/lib/stripe";
    import { db } from "@/lib/db";

    export async function reportUsage(subscriptionItemId: string, quantity: number, idempotencyKey?: string) {
      return stripe.subscriptionItems.createUsageRecord(
        subscriptionItemId,
        { quantity, timestamp: Math.floor(Date.now() / 1000), action: "increment" },
        { idempotencyKey },
      );
    }

    export async function trackApiUsage(userId: string) {
      const user = await db.user.findUnique({ where: { id: userId } });
      if (!user?.stripeSubscriptionId) return;

      const subscription = await stripe.subscriptions.retrieve(user.stripeSubscriptionId);
      const meteredItem = subscription.items.data.find(
        (item) => item.price.recurring?.usage_type === "metered",
      );

      if (meteredItem) {
        await reportUsage(meteredItem.id, 1, `${userId}-${Date.now()}`);
      }
    }
''')

# ── Express ────────────────────────────────────────────────────────────────

TEMPLATES[("express", "checkout")] = textwrap.dedent('''\
    // routes/billing.ts
    import { Router, Request, Response } from "express";
    import { stripe, PLANS } from "../lib/stripe";
    import { requireAuth } from "../middleware/auth";
    import { db } from "../lib/db";

    const router = Router();

    router.post("/checkout", requireAuth, async (req: Request, res: Response) => {
      const { plan, interval = "monthly" } = req.body;
      const user = req.user!;

      if (!PLANS[plan]) return res.status(400).json({ error: "Invalid plan" });

      let customerId = user.stripeCustomerId;
      if (!customerId) {
        const customer = await stripe.customers.create({
          email: user.email,
          metadata: { userId: user.id },
        });
        customerId = customer.id;
        await db.user.update({ where: { id: user.id }, data: { stripeCustomerId: customerId } });
      }

      const session = await stripe.checkout.sessions.create({
        customer: customerId,
        mode: "subscription",
        line_items: [{ price: PLANS[plan][interval], quantity: 1 }],
        subscription_data: { metadata: { userId: user.id, plan } },
        success_url: `${process.env.APP_URL}/dashboard?checkout=success`,
        cancel_url: `${process.env.APP_URL}/pricing`,
        metadata: { userId: user.id },
      });

      res.json({ url: session.url });
    });

    export default router;
''')

TEMPLATES[("express", "webhooks")] = textwrap.dedent('''\
    // routes/webhooks.ts
    import { Router, Request, Response } from "express";
    import { stripe } from "../lib/stripe";
    import { db } from "../lib/db";
    import type Stripe from "stripe";

    const router = Router();

    // IMPORTANT: Use express.raw() middleware for this route, not express.json()
    router.post(
      "/stripe",
      async (req: Request, res: Response) => {
        const sig = req.headers["stripe-signature"] as string;
        if (!sig) return res.status(400).json({ error: "Missing signature" });

        let event: Stripe.Event;
        try {
          event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
        } catch (err) {
          console.error("Webhook signature failed:", err);
          return res.status(400).json({ error: "Invalid signature" });
        }

        // Idempotency check
        const existing = await db.stripeEvent.findUnique({ where: { id: event.id } });
        if (existing) return res.json({ received: true, deduplicated: true });

        try {
          // Handle event types here (see SKILL.md for full handlers)
          switch (event.type) {
            case "checkout.session.completed":
            case "customer.subscription.updated":
            case "customer.subscription.deleted":
            case "invoice.payment_succeeded":
            case "invoice.payment_failed":
              console.log(`Processing: ${event.type}`);
              // TODO: Implement handlers
              break;
            default:
              console.log(`Unhandled: ${event.type}`);
          }

          await db.stripeEvent.create({ data: { id: event.id, type: event.type } });
          res.json({ received: true });
        } catch (err) {
          console.error(`Webhook error [${event.type}]:`, err);
          res.status(500).json({ error: "Processing failed" });
        }
      },
    );

    export default router;
''')

TEMPLATES[("express", "subscriptions")] = TEMPLATES[("nextjs", "subscriptions")]
TEMPLATES[("express", "portal")] = textwrap.dedent('''\
    // routes/portal.ts (add to billing router)
    import { Router, Request, Response } from "express";
    import { stripe } from "../lib/stripe";
    import { requireAuth } from "../middleware/auth";

    const router = Router();

    router.post("/portal", requireAuth, async (req: Request, res: Response) => {
      const user = req.user!;
      if (!user.stripeCustomerId) return res.status(400).json({ error: "No billing account" });

      const session = await stripe.billingPortal.sessions.create({
        customer: user.stripeCustomerId,
        return_url: `${process.env.APP_URL}/settings/billing`,
      });

      res.json({ url: session.url });
    });

    export default router;
''')

TEMPLATES[("express", "usage")] = TEMPLATES[("nextjs", "usage")]

# ── Django ─────────────────────────────────────────────────────────────────

TEMPLATES[("django", "checkout")] = textwrap.dedent('''\
    # billing/views.py
    import json
    import stripe
    from django.conf import settings
    from django.http import JsonResponse
    from django.views.decorators.http import require_POST
    from django.contrib.auth.decorators import login_required
    from .models import UserProfile

    stripe.api_key = settings.STRIPE_SECRET_KEY

    PLANS = {
        "starter": {"monthly": settings.STRIPE_STARTER_MONTHLY, "yearly": settings.STRIPE_STARTER_YEARLY},
        "pro": {"monthly": settings.STRIPE_PRO_MONTHLY, "yearly": settings.STRIPE_PRO_YEARLY},
    }

    @require_POST
    @login_required
    def create_checkout(request):
        data = json.loads(request.body)
        plan = data.get("plan")
        interval = data.get("interval", "monthly")

        if plan not in PLANS:
            return JsonResponse({"error": "Invalid plan"}, status=400)

        profile = request.user.profile
        if not profile.stripe_customer_id:
            customer = stripe.Customer.create(
                email=request.user.email,
                metadata={"userId": str(request.user.id)},
            )
            profile.stripe_customer_id = customer.id
            profile.save()

        session = stripe.checkout.Session.create(
            customer=profile.stripe_customer_id,
            mode="subscription",
            line_items=[{"price": PLANS[plan][interval], "quantity": 1}],
            subscription_data={"metadata": {"userId": str(request.user.id), "plan": plan}},
            success_url=f"{settings.APP_URL}/dashboard/?checkout=success&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.APP_URL}/pricing/",
            metadata={"userId": str(request.user.id)},
        )

        return JsonResponse({"url": session.url})
''')

TEMPLATES[("django", "webhooks")] = textwrap.dedent('''\
    # billing/webhooks.py
    import stripe
    from django.conf import settings
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    from django.views.decorators.http import require_POST
    from .models import StripeEvent, UserProfile

    stripe.api_key = settings.STRIPE_SECRET_KEY

    @csrf_exempt
    @require_POST
    def stripe_webhook(request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        if not sig_header:
            return JsonResponse({"error": "Missing signature"}, status=400)

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return JsonResponse({"error": "Invalid signature"}, status=400)

        # Idempotency check
        if StripeEvent.objects.filter(event_id=event["id"]).exists():
            return JsonResponse({"received": True, "deduplicated": True})

        try:
            event_type = event["type"]
            # TODO: Implement handlers for each event type
            if event_type == "checkout.session.completed":
                pass  # handle checkout
            elif event_type == "customer.subscription.updated":
                pass  # handle subscription change
            elif event_type == "customer.subscription.deleted":
                pass  # handle cancellation
            elif event_type == "invoice.payment_failed":
                pass  # handle payment failure

            StripeEvent.objects.create(event_id=event["id"], event_type=event_type)
            return JsonResponse({"received": True})
        except Exception as e:
            return JsonResponse({"error": "Processing failed"}, status=500)
''')

TEMPLATES[("django", "subscriptions")] = textwrap.dedent('''\
    # billing/subscriptions.py
    import stripe
    from django.conf import settings

    stripe.api_key = settings.STRIPE_SECRET_KEY

    def upgrade_subscription(subscription_id: str, new_price_id: str):
        subscription = stripe.Subscription.retrieve(subscription_id)
        return stripe.Subscription.modify(
            subscription_id,
            items=[{"id": subscription["items"]["data"][0]["id"], "price": new_price_id}],
            proration_behavior="always_invoice",
            billing_cycle_anchor="unchanged",
        )

    def downgrade_subscription(subscription_id: str, new_price_id: str):
        subscription = stripe.Subscription.retrieve(subscription_id)
        return stripe.Subscription.modify(
            subscription_id,
            items=[{"id": subscription["items"]["data"][0]["id"], "price": new_price_id}],
            proration_behavior="none",
        )

    def cancel_subscription(subscription_id: str):
        return stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)

    def reactivate_subscription(subscription_id: str):
        return stripe.Subscription.modify(subscription_id, cancel_at_period_end=False)
''')

TEMPLATES[("django", "portal")] = textwrap.dedent('''\
    # billing/views.py (add to existing views)
    @require_POST
    @login_required
    def customer_portal(request):
        profile = request.user.profile
        if not profile.stripe_customer_id:
            return JsonResponse({"error": "No billing account"}, status=400)

        session = stripe.billing_portal.Session.create(
            customer=profile.stripe_customer_id,
            return_url=f"{settings.APP_URL}/settings/billing/",
        )

        return JsonResponse({"url": session.url})
''')

TEMPLATES[("django", "usage")] = textwrap.dedent('''\
    # billing/usage.py
    import time
    import stripe
    from django.conf import settings

    stripe.api_key = settings.STRIPE_SECRET_KEY

    def report_usage(subscription_item_id: str, quantity: int, idempotency_key: str = None):
        return stripe.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=quantity,
            timestamp=int(time.time()),
            action="increment",
            idempotency_key=idempotency_key,
        )
''')


def generate_scaffold(framework, features):
    """Generate code scaffold for the given framework and features."""
    output = {
        "framework": framework,
        "framework_name": FRAMEWORKS[framework],
        "features": features,
        "generated_at": datetime.now().isoformat(),
        "files": [],
    }

    for feature in features:
        key = (framework, feature)
        if key not in TEMPLATES:
            output["files"].append({
                "feature": feature,
                "error": f"No template available for {framework}/{feature}",
            })
            continue

        code = TEMPLATES[key]
        # Extract filename from first comment line
        first_line = code.strip().splitlines()[0]
        filename = first_line.strip("/ #").strip()

        output["files"].append({
            "feature": feature,
            "filename": filename,
            "code": code,
        })

    return output


def format_human(output):
    """Format scaffold output for human-readable display."""
    lines = []
    lines.append("=" * 64)
    lines.append(f"  Stripe Checkout Scaffolder - {output['framework_name']}")
    lines.append("=" * 64)
    lines.append(f"\nFeatures: {', '.join(output['features'])}")
    lines.append(f"Generated: {output['generated_at']}")

    for file_info in output["files"]:
        lines.append(f"\n{'─' * 64}")
        if "error" in file_info:
            lines.append(f"[ERROR] {file_info['feature']}: {file_info['error']}")
            continue

        lines.append(f"Feature: {file_info['feature']}")
        lines.append(f"File: {file_info['filename']}")
        lines.append(f"{'─' * 64}")
        lines.append(file_info["code"])

    lines.append("=" * 64)
    lines.append("\nNext steps:")
    lines.append("  1. Copy generated files into your project")
    lines.append("  2. Set environment variables: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, APP_URL")
    lines.append("  3. Configure price IDs in environment for each plan")
    lines.append("  4. Set up webhook endpoint in Stripe Dashboard")
    lines.append("  5. Test with: stripe listen --forward-to localhost:3000/api/webhooks/stripe")
    lines.append("=" * 64)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Stripe Checkout and subscription boilerplate code for different frameworks.",
        epilog="Example: %(prog)s --framework nextjs --features checkout,webhooks,subscriptions",
    )
    parser.add_argument(
        "--framework", "-f",
        choices=list(FRAMEWORKS.keys()),
        help="Target framework for code generation",
    )
    parser.add_argument(
        "--features",
        help="Comma-separated list of features to generate (checkout,webhooks,subscriptions,portal,usage)",
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    parser.add_argument("--list-frameworks", action="store_true", help="List available frameworks")
    parser.add_argument("--list-features", action="store_true", help="List available features")
    parser.add_argument("--all", action="store_true", help="Generate all features for the selected framework")

    args = parser.parse_args()

    if args.list_frameworks:
        if args.json_output:
            print(json.dumps(FRAMEWORKS, indent=2))
        else:
            print("Available frameworks:")
            for key, name in FRAMEWORKS.items():
                print(f"  {key:12s} - {name}")
        sys.exit(0)

    if args.list_features:
        if args.json_output:
            print(json.dumps(FEATURES, indent=2))
        else:
            print("Available features:")
            for key, desc in FEATURES.items():
                print(f"  {key:16s} - {desc}")
        sys.exit(0)

    if not args.framework:
        parser.error("--framework is required (use --list-frameworks to see options)")

    if args.all:
        features = list(FEATURES.keys())
    elif not args.features:
        parser.error("--features is required (use --list-features to see options, or --all for everything)")
    else:
        features = [f.strip() for f in args.features.split(",")]
        invalid = [f for f in features if f not in FEATURES]
        if invalid:
            parser.error(f"Unknown feature(s): {', '.join(invalid)}. Use --list-features to see options.")

    output = generate_scaffold(args.framework, features)

    if args.json_output:
        print(json.dumps(output, indent=2))
    else:
        print(format_human(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
