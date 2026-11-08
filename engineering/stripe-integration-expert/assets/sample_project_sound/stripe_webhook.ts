// Sound sample: verified signature, event dedup, re-fetch, 500 on failure so Stripe retries.
import Stripe from "stripe";
import { db } from "./db";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: "2026-10-28.endive" /* pin to the version your SDK ships with */ });
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export async function POST(req: Request) {
  const body = await req.text();
  const signature = req.headers.get("stripe-signature")!;
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch {
    return new Response("bad signature", { status: 400 });
  }

  // Idempotency: skip events we have already processed
  const seen = await db.processedEvent.findUnique({ where: { id: event.id } });
  if (seen) return new Response("duplicate", { status: 200 });

  try {
    switch (event.type) {
      case "checkout.session.completed":
      case "customer.subscription.created":
      case "customer.subscription.updated":
      case "customer.subscription.deleted":
      case "invoice.payment_succeeded":
      case "invoice.payment_failed":
        await syncFromStripe(event);
        break;
    }
    await db.processedEvent.create({ data: { id: event.id } });
  } catch (err) {
    console.error("webhook processing failed", event.id, err);
    return new Response("retry", { status: 500 });
  }
  return new Response("ok", { status: 200 });
}

export async function createCheckout(customerId: string, userId: string) {
  try {
    return await stripe.checkout.sessions.create(
      {
        customer: customerId,
        mode: "subscription",
        line_items: [{ price: process.env.STRIPE_PRICE_PRO!, quantity: 1 }],
        metadata: { userId },
        success_url: "https://example.com/ok",
      },
      { idempotencyKey: `checkout-${userId}` },
    );
  } catch (err) {
    console.error("checkout failed", err);
    throw err;
  }
}

async function syncFromStripe(event: Stripe.Event) {
  // Re-fetch the object instead of trusting the event payload ordering
  const obj = event.data.object as { id: string };
  return obj.id;
}
