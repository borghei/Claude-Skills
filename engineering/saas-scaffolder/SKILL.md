---
name: saas-scaffolder
description: >
  Lays down a Next.js SaaS skeleton (provider-specific deps, env, Drizzle tenancy schema,
  middleware) and guides auth, billing and tenant isolation. Use when starting a SaaS,
  subscription app or multi-tenant platform.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: full-stack
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: nextjs, drizzle, stripe, authjs, clerk, tailwind
  tags:
    - saas
    - boilerplate
    - nextjs
    - stripe
    - multi-tenancy
---
# SaaS Scaffolder

The agent stands up a Next.js App Router + TypeScript + Tailwind + Drizzle SaaS for the chosen auth, billing and tenancy providers, then implements auth, billing and tenant isolation from the reference code and checks isolation before anything ships.

**What the tool writes, and what it does not.** `saas_scaffolder.py` writes the file tree, a `package.json` whose dependencies follow `--auth`, `--db` and `--payments`, a provider-filtered `.env.example`, a Drizzle schema shaped by `--tenancy`, `drizzle.config.ts`, `tsconfig.json`, `next.config.ts`, Tailwind v4 PostCSS config, route protection (`proxy.ts` for Next.js 16+, which replaces `middleware.ts`; `--next-major 15` writes `middleware.ts`) and a health route. Every other file is a `// STUB` that names the reference section to implement it from. It does not write application logic, so the result does not build until the stubs are filled.

## When to Use

- Starting a new SaaS product, subscription app or multi-tenant platform.
- Standing up auth, billing and tenancy before building product features.
- Adding workspace or organization tenancy with roles and plan gating.
- Auditing an existing app's tenant config or source for isolation leaks (`tenant_config_validator.py`).

## Clarify First

Before scaffolding, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Auth provider:** NextAuth (Auth.js v5) / Clerk / Supabase Auth (`--auth`; changes dependencies, env and middleware).
- **Payments provider:** Stripe / Lemon Squeezy / none (`--payments`; adds or removes billing routes, deps and schema columns).
- **Tenancy model:** workspace / organization / none (`--tenancy`; shapes the schema and every query).
- **Database host:** Neon / Supabase / other Postgres (`--db`; picks the driver). Only Postgres is supported: the schema uses `drizzle-orm/pg-core`.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Scaffold** into an empty directory: `saas_scaffolder.py --name <pkg> --auth ... --payments ... --tenancy ... --output <dir>`. It refuses a non-empty `--output` so it cannot overwrite work. Use `--dry-run` first to show the plan.
2. **Install once and commit the lockfile.** `next`, `react` and Tailwind get `^` ranges for majors known to be current (Next.js 16, React 19, Tailwind 4); every other dependency uses an npm tag (`latest`, or `beta` for `next-auth`, whose v5 API the references use), because invented version numbers go stale. The lockfile from that first install is what makes later installs reproducible, so review it and commit it.
   Auth.js notes it is now part of Better Auth; read its upgrade guide (authjs.dev) before choosing it for a new project. With Auth.js v5, `AUTH_URL` is optional and `AUTH_TRUST_HOST=true` is needed behind a reverse proxy.
3. **Fill the stubs** in phase order (foundation, database, auth, billing, UI) from [references/workflow-and-quality.md](references/workflow-and-quality.md). `grep -rl "STUB generated" .` lists what remains.
4. **Validate isolation:** run `tenant_config_validator.py --src <app dir>`. Fix every critical finding; unscoped queries are cross-tenant data leaks.
5. Done when: `npm run build` passes, no `STUB generated` files remain, a test checkout updates the subscription row, a replayed webhook is a no-op, and the validator reports no critical findings.

## Quick Start

```bash
# from engineering/saas-scaffolder/; scaffold outside the repo
OUT=$(mktemp -d)
python3 scripts/saas_scaffolder.py --name acme --auth clerk --payments none --tenancy none --output "$OUT/acme"
python3 scripts/saas_scaffolder.py --name acme --dry-run --format json      # plan only, nothing written
```

```bash
python3 scripts/tenant_config_validator.py --config assets/sample_tenant_config.json                      # exit 0
python3 scripts/tenant_config_validator.py --config assets/flawed_tenant_config.json --src assets/flawed_src  # exit 1, 5 critical
python3 scripts/feature_flag_manager.py --store "$OUT/flags.json" create --key sso --enabled --allowed-plans pro enterprise
python3 scripts/feature_flag_manager.py --store "$OUT/flags.json" evaluate --key sso --plan free           # INACTIVE
```

## Tools Overview

| Tool | Purpose | Key flags | Exit codes |
|------|---------|-----------|------------|
| `scripts/saas_scaffolder.py` | Tree, provider-specific `package.json`, `.env.example`, schema, configs, `proxy.ts` (or `middleware.ts`); stubs for the rest | `--name`, `--auth nextauth\|clerk\|supabase`, `--db neondb\|supabase\|postgres`, `--payments stripe\|lemonsqueezy\|none`, `--tenancy workspace\|organization\|none`, `--features a,b`, `--next-major 16`, `--output`, `--dry-run`, `--format json` | 0 done; 2 invalid name or non-empty output |
| `scripts/tenant_config_validator.py` | Tenant config (duplicate ids, slugs, domains; isolation settings; plans) and source scan (unscoped `db.*` queries, global tenant state, route handlers without `auth()`) | `--config FILE`, `--src DIR` (repeatable), `--severity`, `--json` | 0 no critical; 1 critical findings; 2 unreadable config, bad JSON or missing `--src` |
| `scripts/feature_flag_manager.py` | Create, update, list and evaluate plan- and environment-gated flags in a JSON store | `--store FILE`, `create\|get\|update\|delete\|list\|evaluate` | 0 ok; 2 unreadable or malformed store |

The source scan is line-based regex: it catches the common leaks, not every one. A clean result is not proof of isolation; review data access in code review too.

## Anti-Patterns

**Mistake:** Querying tenant-owned tables without the tenant id.
**Why it matters:** One missing `where(eq(t.workspaceId, ...))` returns every customer's rows; it is the most common multi-tenant breach.
**Instead:** Route all reads and writes through a workspace-scoped helper (see Multi-Tenancy Patterns in the auth reference) and run the validator on every PR.

**Mistake:** Trusting the client for plan or subscription state.
**Why it matters:** Feature gates checked only in the browser are bypassed by calling the API directly.
**Instead:** Check the plan and current period end on the server, from the webhook-maintained row.

**Mistake:** A webhook handler without signature verification or idempotency.
**Why it matters:** Unsigned events can be forged, and providers retry, so duplicates double-apply changes.
**Instead:** Verify the signature first, record `event.id`, and make each handler safe to replay.

## Reference Documentation

- **[references/project-structure-and-schema.md](references/project-structure-and-schema.md)**: input spec, full file tree, multi-tenant Drizzle schema and env variables. Read when laying out files or writing the schema.
- **[references/auth-billing-and-tenancy.md](references/auth-billing-and-tenancy.md)**: Auth.js v5 config, Stripe checkout and webhook handlers, middleware, workspace-scoped queries and plan gating. Read when filling auth, billing or tenancy stubs.
- **[references/workflow-and-quality.md](references/workflow-and-quality.md)**: the five phases with a validation step each, pitfalls, troubleshooting and success criteria. Read before scaffolding and before shipping.

## Files

| File | Purpose |
|------|---------|
| `scripts/saas_scaffolder.py` | Skeleton generator (stdlib only) |
| `scripts/tenant_config_validator.py` | Tenant config and source isolation checks |
| `scripts/feature_flag_manager.py` | JSON-store feature flags with plan and environment gating |
| `assets/sample_tenant_config.json` | Sound three-tenant config; validator exits 0 |
| `assets/flawed_tenant_config.json` | Duplicate slug and domain, missing dedicated DB, unknown plan; exits 1 |
| `assets/flawed_src/projects-route.ts` | Unscoped query and global tenant state; critical findings |

## Scope & Limitations

**Covers:** Next.js SaaS skeletons for three auth providers, two billing providers and three tenancy models on Postgres; reference implementations for auth, billing and tenancy; tenant isolation checks; plan-gated feature flags.

**Does not cover:**
- Metered or usage-based billing and invoicing (see `engineering/stripe-integration-expert`).
- Domain schema design beyond the tenancy core (see `engineering/database-schema-designer`).
- CI/CD and deployment (see `engineering/ci-cd-pipeline-builder`).
- API standards review (see `engineering/api-design-reviewer`) and secrets management (see `engineering/env-secrets-manager`).
- Non-Postgres databases.
