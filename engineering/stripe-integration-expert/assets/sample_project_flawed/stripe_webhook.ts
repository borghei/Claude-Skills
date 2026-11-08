// Deliberately flawed sample: unverified payload, replays handled twice, errors swallowed with 200.
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(req: Request) {
  try {
    const event = JSON.parse(await req.text());
    if (event.type === "checkout.session.completed") {
      await activate(event.data.object);
    }
  } catch (err) {
    return new Response("ok", { status: 200 });
  }
  return new Response("ok", { status: 200 });
}

export async function createCheckout(customerId: string) {
  return stripe.checkout.sessions.create({
    customer: customerId,
    mode: "subscription",
    line_items: [{ price: "price_1PbasicMonthly", quantity: 1 }],
    success_url: "https://example.com/ok",
  });
}

async function activate(_session: unknown) {}
