---
name: saas-scaffolder
description: Generate complete production-ready SaaS boilerplate with authentication, database schemas, billing integration (Stripe), multi-tenancy, API routes, dashboard UI, and deployment configuration. Supports Next.js App Router, TypeScript, Tailwind, shadcn/ui, Drizzle ORM, and multiple auth/payment providers. Use when starting a new SaaS product, subscription app, or multi-tenant platform.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: full-stack
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: nextjs, drizzle, stripe, nextauth, tailwind, shadcn
---

# SaaS Scaffolder

**Tier:** POWERFUL
**Category:** Engineering / Full-Stack
**Maintainer:** Claude Skills Team

## Overview

Generate a complete, production-ready SaaS application boilerplate including authentication (NextAuth, Clerk, or Supabase Auth), database schemas with multi-tenancy, billing integration (Stripe or Lemon Squeezy), API routes with validation, dashboard UI with shadcn/ui, and deployment configuration. Produces a working application from a product specification in under 30 minutes.

## Keywords

SaaS, boilerplate, scaffolding, Next.js, authentication, Stripe, billing, multi-tenancy, subscription, starter template, NextAuth, Drizzle ORM, shadcn/ui

## Input Specification

```
Product: [name]
Description: [1-3 sentences]
Auth: nextauth | clerk | supabase
Database: neondb | supabase | planetscale | turso
Payments: stripe | lemonsqueezy | none
Multi-tenancy: workspace | organization | none
Features: [comma-separated list]
```

## Generated File Tree

```
my-saas/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── forgot-password/page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── dashboard/page.tsx
│   │   ├── settings/
│   │   │   ├── page.tsx              # Profile settings
│   │   │   ├── billing/page.tsx      # Subscription management
│   │   │   └── team/page.tsx         # Team/workspace settings
│   │   └── layout.tsx                # Dashboard shell (sidebar + header)
│   ├── (marketing)/
│   │   ├── page.tsx                  # Landing page
│   │   ├── pricing/page.tsx          # Pricing tiers
│   │   └── layout.tsx
│   ├── api/
│   │   ├── auth/[...nextauth]/route.ts
│   │   ├── webhooks/stripe/route.ts
│   │   ├── billing/
│   │   │   ├── checkout/route.ts
│   │   │   └── portal/route.ts
│   │   └── health/route.ts
│   ├── layout.tsx                    # Root layout
│   └── not-found.tsx
├── components/
│   ├── ui/                           # shadcn/ui components
│   ├── auth/
│   │   ├── login-form.tsx
│   │   └── register-form.tsx
│   ├── dashboard/
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   └── stats-card.tsx
│   ├── marketing/
│   │   ├── hero.tsx
│   │   ├── features.tsx
│   │   ├── pricing-card.tsx
│   │   └── footer.tsx
│   └── billing/
│       ├── plan-card.tsx
│       └── usage-meter.tsx
├── lib/
│   ├── auth.ts                       # Auth configuration
│   ├── db.ts                         # Database client singleton
│   ├── stripe.ts                     # Stripe client
│   ├── validations.ts                # Zod schemas
│   └── utils.ts                      # Shared utilities
├── db/
│   ├── schema.ts                     # Drizzle schema
│   ├── migrations/                   # Generated migrations
│   └── seed.ts                       # Development seed data
├── hooks/
│   ├── use-subscription.ts
│   └── use-current-user.ts
├── types/
│   └── index.ts                      # Shared TypeScript types
├── middleware.ts                      # Auth + rate limiting
├── .env.example
├── drizzle.config.ts
├── tailwind.config.ts
└── next.config.ts
```

## Database Schema (Multi-Tenant)

```typescript
// db/schema.ts
import { pgTable, text, timestamp, integer, boolean, uniqueIndex, index } from 'drizzle-orm/pg-core'
import { createId } from '@paralleldrive/cuid2'

// ──── WORKSPACES (Tenancy boundary) ────
export const workspaces = pgTable('workspaces', {
  id: text('id').primaryKey().$defaultFn(createId),
  name: text('name').notNull(),
  slug: text('slug').notNull(),
  plan: text('plan').notNull().default('free'),  // free | pro | enterprise
  stripeCustomerId: text('stripe_customer_id').unique(),
  stripeSubscriptionId: text('stripe_subscription_id'),
  stripePriceId: text('stripe_price_id'),
  stripeCurrentPeriodEnd: timestamp('stripe_current_period_end'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (t) => [
  uniqueIndex('workspaces_slug_idx').on(t.slug),
])

// ──── USERS ────
export const users = pgTable('users', {
  id: text('id').primaryKey().$defaultFn(createId),
  email: text('email').notNull().unique(),
  name: text('name'),
  avatarUrl: text('avatar_url'),
  emailVerified: timestamp('email_verified', { withTimezone: true }),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
})

// ──── WORKSPACE MEMBERS ────
export const workspaceMembers = pgTable('workspace_members', {
  id: text('id').primaryKey().$defaultFn(createId),
  workspaceId: text('workspace_id').notNull().references(() => workspaces.id, { onDelete: 'cascade' }),
  userId: text('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  role: text('role').notNull().default('member'), // owner | admin | member
  joinedAt: timestamp('joined_at', { withTimezone: true }).defaultNow().notNull(),
}, (t) => [
  uniqueIndex('workspace_members_unique').on(t.workspaceId, t.userId),
  index('workspace_members_workspace_idx').on(t.workspaceId),
])

// ──── ACCOUNTS (OAuth) ────
export const accounts = pgTable('accounts', {
  userId: text('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  type: text('type').notNull(),
  provider: text('provider').notNull(),
  providerAccountId: text('provider_account_id').notNull(),
  refreshToken: text('refresh_token'),
  accessToken: text('access_token'),
  expiresAt: integer('expires_at'),
})

// ──── SESSIONS ────
export const sessions = pgTable('sessions', {
  sessionToken: text('session_token').primaryKey(),
  userId: text('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  expires: timestamp('expires', { withTimezone: true }).notNull(),
})
```

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
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
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
// middleware.ts
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

## Environment Variables

```bash
# .env.example

# ─── App ───
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXTAUTH_SECRET=           # openssl rand -base64 32
NEXTAUTH_URL=http://localhost:3000

# ─── Database ───
DATABASE_URL=              # postgresql://user:pass@host/db?sslmode=require

# ─── OAuth Providers ───
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# ─── Stripe ───
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_YEARLY_PRICE_ID=price_...

# ─── Email ───
RESEND_API_KEY=re_...

# ─── Monitoring (optional) ───
SENTRY_DSN=
```

## Scaffolding Phases

Execute these phases in order. Validate at the end of each phase.

### Phase 1: Foundation
1. Initialize Next.js with TypeScript and App Router
2. Configure Tailwind CSS with custom theme
3. Install and configure shadcn/ui
4. Set up ESLint and Prettier
5. Create `.env.example`

**Validate:** `pnpm build` completes without errors.

### Phase 2: Database
6. Install and configure Drizzle ORM
7. Write schema (users, accounts, sessions, workspaces, members)
8. Generate and apply initial migration
9. Export DB client singleton from `lib/db.ts`
10. Create seed script with test data

**Validate:** `pnpm db:push` succeeds and `pnpm db:seed` creates test data.

### Phase 3: Authentication
11. Install and configure NextAuth v5 with Drizzle adapter
12. Set up OAuth providers (Google, GitHub)
13. Create auth API route
14. Implement middleware for route protection
15. Build login and register pages

**Validate:** OAuth login works, session persists, protected routes redirect.

### Phase 4: Billing
16. Initialize Stripe client
17. Create checkout session API route
18. Create customer portal API route
19. Implement webhook handler with signature verification
20. Build pricing page and billing settings page

**Validate:** Complete a test checkout with card `4242 4242 4242 4242`. Verify subscription data written to DB. Replay webhook event and confirm idempotency.

### Phase 5: UI and Polish
21. Build landing page (hero, features, pricing, footer)
22. Build dashboard layout (sidebar, header, stats)
23. Build settings pages (profile, billing, team)
24. Add loading states, error boundaries, and not-found pages
25. Configure deployment (Vercel/Railway)

**Validate:** `pnpm build` succeeds. All routes render correctly. No hydration errors.

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

## Common Pitfalls

- **Missing `NEXTAUTH_SECRET` in production** — causes session errors; generate with `openssl rand -base64 32`
- **Webhook signature verification skipped** — always verify Stripe webhook signatures; test with `stripe listen`
- **`workspace:*` in session but not refreshed** — stale subscription data; recheck on billing pages
- **Edge Runtime conflicts with Drizzle** — Drizzle needs Node.js runtime; set `export const runtime = 'nodejs'` on API routes
- **No idempotent webhook handling** — Stripe may send duplicate events; use `event.id` for deduplication
- **Hardcoded Stripe price IDs** — store in env vars, not in code; prices change between test and live mode

## Best Practices

1. **Stripe singleton** — create the client once in `lib/stripe.ts`, import everywhere
2. **Server actions for form mutations** — use Next.js Server Actions instead of API routes for forms
3. **Idempotent webhook handlers** — check if the event was already processed before writing to DB
4. **Suspense boundaries for async data** — wrap dashboard data in `<Suspense>` with loading skeletons
5. **Feature gating at the server level** — check `stripeCurrentPeriodEnd` on the server, not the client
6. **Rate limiting on auth routes** — prevent brute force with Upstash Redis + `@upstash/ratelimit`
7. **Workspace context in every query** — never query without scoping to the current workspace
8. **Test with Stripe CLI** — `stripe listen --forward-to localhost:3000/api/webhooks/stripe` for local development
