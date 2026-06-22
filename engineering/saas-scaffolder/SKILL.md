---
name: saas-scaffolder
description: >
  Generate SaaS boilerplate with auth, database schemas, Stripe billing, multi-tenancy, API
  routes, and dashboard UI on a Next.js/TypeScript/Tailwind stack. Use when starting a new
  SaaS product, subscription app, or multi-tenant platform.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: full-stack
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: nextjs, drizzle, stripe, nextauth, tailwind, shadcn
---
# SaaS Scaffolder

Generate a complete, production-ready SaaS application boilerplate including authentication (NextAuth, Clerk, or Supabase Auth), database schemas with multi-tenancy, billing integration (Stripe or Lemon Squeezy), API routes with validation, dashboard UI with shadcn/ui, and deployment configuration. Produces a working application from a product specification in under 30 minutes.

## Core Capabilities

- **Spec-driven scaffolding** — produce a full Next.js App Router + TypeScript + Tailwind + shadcn/ui file tree from a short product spec (auth/db/payments/tenancy/features).
- **Multi-tenant database schema** — Drizzle ORM schema with workspaces (tenancy boundary), users, members, OAuth accounts, and sessions, with proper indexes and cascade rules.
- **Authentication** — NextAuth v5 with Drizzle adapter, OAuth (Google/GitHub) and magic-link (Resend) providers, route-protection middleware.
- **Stripe billing** — checkout session, customer portal, and signature-verified webhook handler keeping subscription state in sync.
- **Multi-tenancy patterns** — workspace-scoped queries and plan-based feature gating (free/pro/enterprise).
- **Phased build + quality bar** — 5 ordered scaffolding phases with per-phase validation, pitfalls, best practices, troubleshooting, and success criteria.

**Keywords:** SaaS, boilerplate, scaffolding, Next.js, authentication, Stripe, billing, multi-tenancy, subscription, starter template, NextAuth, Drizzle ORM, shadcn/ui

## When to Use

- Starting a new SaaS product, subscription app, or multi-tenant platform.
- Standing up auth + billing + tenancy boilerplate quickly before building product features.
- Adding workspace/organization tenancy with role-based access and plan gating.
- Generating a baseline `.env.example`, schema, and API routes for a Next.js stack.

## Clarify First

Before scaffolding, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Auth provider** — NextAuth / Clerk / Supabase Auth (`--auth`; changes the auth config and middleware generated)
- [ ] **Payments provider** — Stripe / Lemon Squeezy / none (`--payments`; determines the billing + webhook handler)
- [ ] **Tenancy model** — workspace / organization / single-tenant (`--tenancy`; shapes the entire database schema and scoped queries)
- [ ] **Database** — Neon / Supabase / other Postgres (`--db`; sets the Drizzle adapter and connection config)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `saas_scaffolder.py` | Generate a production-ready SaaS project structure (auth, billing, tenancy) | `python scripts/saas_scaffolder.py --name my-saas --auth nextauth --db neondb --payments stripe --tenancy workspace` |
| `feature_flag_manager.py` | CRUD + evaluate feature flags on a JSON store | `python scripts/feature_flag_manager.py evaluate --key dark-mode --environment production --plan pro` |
| `tenant_config_validator.py` | Validate multi-tenant config and scan source for missing tenant scoping / isolation issues | `python scripts/tenant_config_validator.py --config tenant_config.json --src ./app` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/project-structure-and-schema.md](references/project-structure-and-schema.md)** — input spec format, the full generated file tree, the multi-tenant Drizzle schema, and the `.env.example` variables. Read when defining the spec, laying out files, or writing the schema/env config.
- **[references/auth-billing-and-tenancy.md](references/auth-billing-and-tenancy.md)** — complete NextAuth config, Stripe checkout + webhook handlers, route-protection middleware, and workspace-scoped query / plan-gating code. Read when wiring auth, billing, or tenancy.
- **[references/workflow-and-quality.md](references/workflow-and-quality.md)** — the 5 ordered scaffolding phases with per-phase validation, common pitfalls, best practices, the troubleshooting table, and success criteria. Read before scaffolding and before shipping.

## Scope & Limitations

**This skill covers:**
- Full-stack SaaS scaffolding with Next.js App Router, TypeScript, Tailwind, and shadcn/ui
- Authentication setup with NextAuth v5, Clerk, or Supabase Auth including OAuth and magic link providers
- Stripe and Lemon Squeezy billing integration with checkout, webhooks, and customer portal
- Multi-tenancy patterns (workspace/organization) with role-based access and plan-based feature gating

**This skill does NOT cover:**
- Ongoing Stripe billing logic beyond initial integration (metered billing, usage-based pricing, invoicing customization) — see `stripe-integration-expert`
- Database schema design decisions beyond the core tenancy model (complex relational modeling, indexing strategies) — see `database-schema-designer`
- CI/CD pipeline configuration, deployment automation, or infrastructure provisioning — see `ci-cd-pipeline-builder`
- API design standards, versioning, or OpenAPI specification generation — see `api-design-reviewer`

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `stripe-integration-expert` | Extends the scaffolded Stripe setup with advanced billing patterns (metered, tiered, usage-based) | Scaffolder outputs base Stripe config and webhook handler; Stripe expert refines pricing models and adds invoice customization |
| `database-schema-designer` | Designs extended schemas beyond the core tenancy tables | Scaffolder provides baseline users/workspaces/members schema; schema designer adds domain-specific entities and optimizes indexes |
| `api-design-reviewer` | Reviews and improves the generated API routes for consistency and standards compliance | Scaffolder generates initial API routes; reviewer audits naming, error handling, and response formats |
| `ci-cd-pipeline-builder` | Creates deployment pipelines for the scaffolded project | Scaffolder outputs the application code; pipeline builder adds GitHub Actions, preview deployments, and production release workflows |
| `env-secrets-manager` | Audits and secures the environment variable configuration | Scaffolder generates `.env.example`; secrets manager validates no secrets are hardcoded and recommends vault integration |
| `observability-designer` | Adds logging, tracing, and monitoring to the scaffolded application | Scaffolder provides the application structure; observability designer instruments API routes, webhooks, and auth flows |
