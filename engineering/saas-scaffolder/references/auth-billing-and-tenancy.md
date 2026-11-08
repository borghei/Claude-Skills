# Auth, Stripe Billing, Middleware & Multi-Tenancy

Read this when wiring up NextAuth, building the Stripe checkout/webhook/portal flow, protecting routes with middleware, or implementing workspace-scoped queries and plan-based feature gating.

## Authentication Configuration

```typescript
// lib/auth.ts
import { DrizzleAdapter } from '@auth/drizzle-adapter'
import NextAuth from 'next-auth'
import Google from 'next-auth/providers/google'
import GitHub from 'next-auth/providers/github'
import Resend from 'next-auth/providers/resend'
import { db } from './db'

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: DrizzleAdapter(db),
  providers: [
    Google,   // reads AUTH_GOOGLE_ID / AUTH_GOOGLE_SECRET
    GitHub,   // reads AUTH_GITHUB_ID / AUTH_GITHUB_SECRET
    Resend({
      from: 'noreply@myapp.com',
    }),
  ],
  callbacks: {
    session: async ({ session, user }) => ({
      ...session,
      user: {
        ...session.user,
        id: user.id,
      },
    }),
  },
  pages: {
    signIn: '/login',
    error: '/login',
  },
})
```

## Stripe Billing Integration

### Checkout Session

```typescript
// app/api/billing/checkout/route.ts
import { NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { stripe } from '@/lib/stripe'
import { db } from '@/lib/db'
import { workspaces } from '@/db/schema'
import { eq } from 'drizzle-orm'

export async function POST(req: Request) {
  const session = await auth()
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { priceId, workspaceId } = await req.json()

  // Get or create Stripe customer
  const [workspace] = await db.select().from(workspaces).where(eq(workspaces.id, workspaceId))
  if (!workspace) {
    return NextResponse.json({ error: 'Workspace not found' }, { status: 404 })
  }

  let customerId = workspace.stripeCustomerId
  if (!customerId) {
    const customer = await stripe.customers.create({
      email: session.user.email!,
      metadata: { workspaceId },
    })
    customerId = customer.id
    await db.update(workspaces)
      .set({ stripeCustomerId: customerId })
      .where(eq(workspaces.id, workspaceId))
  }

  const checkoutSession = await stripe.checkout.sessions.create({
    customer: customerId,
    mode: 'subscription',
    payment_method_types: ['card'],
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/settings/billing?success=true`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
    subscription_data: { trial_period_days: 14 },
    metadata: { workspaceId },
  })

  return NextResponse.json({ url: checkoutSession.url })
}
```

### Webhook Handler

```typescript
// app/api/webhooks/stripe/route.ts
import { headers } from 'next/headers'
import { stripe } from '@/lib/stripe'
import { db } from '@/lib/db'
import { workspaces } from '@/db/schema'
import { eq } from 'drizzle-orm'

export async function POST(req: Request) {
  const body = await req.text()
  const signature = (await headers()).get('Stripe-Signature')!

  let event
  try {
    event = stripe.webhooks.constructEvent(body, signature, process.env.STRIPE_WEBHOOK_SECRET!)
  } catch (err) {
    return new Response(`Webhook Error: ${err.message}`, { status: 400 })
  }

  // Stripe API 2025-03-31 ("basil") and later moved current_period_end onto subscription
  // items (subscription.items.data[0].current_period_end). Match the API version your SDK pins.
  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object
      const subscription = await stripe.subscriptions.retrieve(session.subscription as string)
      await db.update(workspaces).set({
        stripeSubscriptionId: subscription.id,
        stripePriceId: subscription.items.data[0].price.id,
        stripeCurrentPeriodEnd: new Date(subscription.current_period_end * 1000),
      }).where(eq(workspaces.stripeCustomerId, session.customer as string))
      break
    }

    case 'invoice.payment_succeeded': {
      const invoice = event.data.object
      const subscription = await stripe.subscriptions.retrieve(invoice.subscription as string)
      await db.update(workspaces).set({
        stripeCurrentPeriodEnd: new Date(subscription.current_period_end * 1000),
      }).where(eq(workspaces.stripeCustomerId, invoice.customer as string))
      break
    }

    case 'customer.subscription.deleted': {
      const subscription = event.data.object
      await db.update(workspaces).set({
        plan: 'free',
        stripeSubscriptionId: null,
        stripePriceId: null,
        stripeCurrentPeriodEnd: null,
      }).where(eq(workspaces.stripeCustomerId, subscription.customer as string))
      break
    }
  }

  return new Response('OK', { status: 200 })
}
```

## Middleware (Auth + Rate Limiting)

```typescript
// proxy.ts (Next.js 16+; named middleware.ts with a `middleware` export before 16)
import { auth } from '@/lib/auth'
import { NextResponse } from 'next/server'

export default auth((req) => {
  const { pathname } = req.nextUrl
  const isAuthenticated = !!req.auth

  // Protected routes
  if (pathname.startsWith('/dashboard') || pathname.startsWith('/settings')) {
    if (!isAuthenticated) {
      return NextResponse.redirect(new URL('/login', req.url))
    }
  }

  // Redirect logged-in users away from auth pages
  if ((pathname === '/login' || pathname === '/register') && isAuthenticated) {
    return NextResponse.redirect(new URL('/dashboard', req.url))
  }

  return NextResponse.next()
})

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*', '/login', '/register'],
}
```

## Multi-Tenancy Patterns

### Workspace-Scoped Queries

```typescript
// Every data query must be scoped to the current workspace
export async function getProjects(workspaceId: string) {
  return db.query.projects.findMany({
    where: eq(projects.workspaceId, workspaceId),
    orderBy: [desc(projects.updatedAt)],
  })
}

// Middleware: resolve workspace from URL or session
export function getCurrentWorkspace(req: Request) {
  // Option A: workspace slug in URL (/workspace/acme/dashboard)
  // Option B: workspace ID in session/cookie
  // Option C: header (X-Workspace-Id) for API calls
}
```

### Plan-Based Feature Gating

```typescript
export function canAccessFeature(workspace: Workspace, feature: string): boolean {
  const PLAN_FEATURES: Record<string, string[]> = {
    free: ['basic_dashboard', 'up_to_3_members'],
    pro: ['advanced_analytics', 'up_to_20_members', 'custom_domain', 'api_access'],
    enterprise: ['sso', 'unlimited_members', 'audit_log', 'sla'],
  }

  const isActive = workspace.stripeCurrentPeriodEnd
    ? workspace.stripeCurrentPeriodEnd > new Date()
    : workspace.plan === 'free'

  if (!isActive) return PLAN_FEATURES.free.includes(feature)
  return PLAN_FEATURES[workspace.plan]?.includes(feature) ?? false
}
```
