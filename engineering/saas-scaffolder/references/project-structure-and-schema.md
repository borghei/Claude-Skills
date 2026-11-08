# Project Structure, Schema & Environment

Read this when defining the product spec, laying out the file tree, writing the multi-tenant database schema, or configuring environment variables.

## Input Specification

```
Product: [name]
Description: [1-3 sentences]
Auth: nextauth | clerk | supabase
Database: neondb | supabase | postgres   (Postgres only: the schema uses drizzle-orm/pg-core)
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
├── postcss.config.mjs        # Tailwind v4: @tailwindcss/postcss, no tailwind.config.ts needed
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

## Environment Variables

```bash
# .env.example

# ─── App ───
NEXT_PUBLIC_APP_URL=http://localhost:3000
AUTH_SECRET=               # Auth.js v5 name; openssl rand -base64 32

# ─── Database ───
DATABASE_URL=              # postgresql://user:pass@host/db?sslmode=require

# ─── OAuth Providers ───
AUTH_GOOGLE_ID=
AUTH_GOOGLE_SECRET=
AUTH_GITHUB_ID=
AUTH_GITHUB_SECRET=

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
