# Scaffolding Workflow & Quality Bar

Read this when running the phased scaffolding process, debugging common issues, or checking the generated project against the success criteria before shipping.

## Scaffolding Phases

Execute these phases in order. Validate at the end of each phase.

### Phase 1: Foundation
1. Initialize Next.js with TypeScript and App Router
2. Configure Tailwind CSS with custom theme
3. Install and configure shadcn/ui
4. Set up ESLint and Prettier
5. Create `.env.example`

**Validate:** `npm run build` completes without errors.

### Phase 2: Database
6. Install and configure Drizzle ORM
7. Write schema (users, accounts, sessions, workspaces, members)
8. Generate and apply initial migration
9. Export DB client singleton from `lib/db.ts`
10. Create seed script with test data

**Validate:** `npm run db:generate && npm run db:migrate` succeeds and `npm run db:seed` creates test data.

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

**Validate:** `npm run build` succeeds. All routes render correctly. No hydration errors.

## Common Pitfalls

- **Missing `AUTH_SECRET` in production** — causes session errors; generate with `openssl rand -base64 32`
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

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Auth callback URL mismatch in production | `AUTH_URL` (or the host header behind a proxy) still points at localhost | Set `AUTH_URL` to the production origin, or `AUTH_TRUST_HOST=true` behind a trusted proxy |
| Stripe webhook returns 400 on every event | Raw body is consumed before signature verification | Ensure the webhook route uses `req.text()` before any JSON parsing; do not use body-parser middleware on the webhook endpoint |
| Drizzle migrations fail with "relation already exists" | Migration was partially applied or schema drifted from migration history | Run `pnpm drizzle-kit drop` to reset the migration journal, then regenerate with `pnpm drizzle-kit generate` and reapply |
| OAuth callback redirects to wrong URL | Redirect URI registered in provider console does not match `AUTH_URL` | Update the authorized redirect URI in Google/GitHub developer console to match your deployment URL exactly |
| Multi-tenant queries return data from other workspaces | Missing `workspaceId` filter in a database query | Audit all `db.query` and `db.select` calls to ensure every query includes a `where` clause scoped to the current workspace |
| Hydration mismatch on dashboard pages | Server-rendered HTML differs from client due to conditional auth checks | Move auth-dependent rendering into client components or wrap with `<Suspense>`; avoid reading session in server components that also render on the client |
| Stripe test mode charges succeed but live mode fails | Live mode price IDs differ from test mode IDs | Use separate environment variables for test vs. live Stripe keys and price IDs; verify `.env.production` references the correct live values |

## Success Criteria

- Scaffolded project passes `pnpm build` with zero errors and zero TypeScript warnings on first run
- End-to-end authentication flow (register, login, logout, password reset) completes in under 60 seconds of manual testing
- Stripe checkout creates a subscription and webhook handler updates the database within 5 seconds of payment completion
- Multi-tenant data isolation verified: queries scoped to Workspace A return zero rows belonging to Workspace B
- Lighthouse performance score on the landing page is 90+ on mobile with no accessibility violations at the AA level
- Time from `git clone` to running local dev server with seeded data is under 10 minutes following the generated README
- All environment variables are documented in `.env.example` with descriptions, and the app fails fast with clear error messages when required variables are missing
