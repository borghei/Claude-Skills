---
name: codebase-onboarding
description: Analyze a codebase and generate comprehensive onboarding documentation including architecture overviews, key file maps, local setup guides, task runbooks, debugging guides, and contribution guidelines. Audience-aware output for junior, senior, or contractor developers. Use when onboarding new team members, open-sourcing, or documenting after a major refactor.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: developer-experience
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: markdown, notion, confluence
---

# Codebase Onboarding

**Tier:** POWERFUL
**Category:** Engineering / Developer Experience
**Maintainer:** Claude Skills Team

## Overview

Analyze any codebase and generate production-quality onboarding documentation tailored to the audience. Produces architecture overviews with system diagrams, annotated key file maps, step-by-step local setup guides, common developer task runbooks, debugging guides with real error solutions, and contribution guidelines. Supports Markdown, Notion, and Confluence output formats.

## Keywords

codebase onboarding, developer experience, documentation, architecture overview, setup guide, debugging guide, contribution guidelines, code walkthrough, new hire onboarding

## Core Capabilities

### 1. Architecture Analysis
- Tech stack identification from manifests and lockfiles
- System boundary mapping (services, databases, external APIs)
- Data flow diagramming with Mermaid
- Dependency graph visualization
- Module ownership mapping

### 2. Key File Annotation
- Identify the 20 most important files and explain why they matter
- Mark entry points, configuration hubs, and shared utilities
- Flag files that are dangerous to modify without coordination
- Link files to the architectural concepts they implement

### 3. Setup Guide Generation
- Prerequisites with exact versions and install commands
- Step-by-step from `git clone` to running tests
- Environment variable documentation with example values
- Infrastructure setup (Docker, databases, caches)
- Verification checklist (what "success" looks like)

### 4. Task Runbooks
- How to add a new API endpoint (full lifecycle)
- How to run and write tests
- How to create and apply database migrations
- How to deploy to staging and production
- How to add a new dependency safely

### 5. Debugging Guide
- Common errors with exact error messages and solutions
- Log locations by environment
- Useful SQL/CLI diagnostic queries
- How to reproduce production issues locally

## When to Use

- Onboarding a new team member (junior, senior, or contractor)
- After a major refactor that made existing docs stale
- Before open-sourcing a project
- Creating a team wiki page for a service you own
- Self-documenting before a long vacation or team transition
- Preparing for a compliance audit that requires documentation

## Codebase Analysis Process

### Phase 1: Gather Facts

Run these analysis commands to collect data before generating any documentation.

```bash
# 1. Package manifest and scripts
cat package.json 2>/dev/null | python3 -c "
import json, sys
pkg = json.load(sys.stdin)
print(f\"Name: {pkg.get('name')}\")
print(f\"Scripts: {list(pkg.get('scripts', {}).keys())}\")
print(f\"Deps: {len(pkg.get('dependencies', {}))}\")
print(f\"DevDeps: {len(pkg.get('devDependencies', {}))}\")
" || echo "No package.json found"

# 2. Directory structure (top 3 levels, excluding noise)
find . -maxdepth 3 \
  -not -path '*/node_modules/*' \
  -not -path '*/.git/*' \
  -not -path '*/.next/*' \
  -not -path '*/__pycache__/*' \
  -not -path '*/dist/*' \
  -not -path '*/.venv/*' | \
  sort | head -80

# 3. Largest source files (complexity indicators)
find src/ app/ lib/ -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.go" 2>/dev/null | \
  xargs wc -l 2>/dev/null | sort -rn | head -20

# 4. API routes
find . -name "route.ts" -path "*/api/*" 2>/dev/null | sort  # Next.js
grep -rn "router\.\(get\|post\|put\|delete\)" src/ --include="*.ts" 2>/dev/null | head -30  # Express

# 5. Database schema location
find . -name "schema.ts" -o -name "schema.prisma" -o -name "models.py" 2>/dev/null | head -10

# 6. Test infrastructure
find . -name "*.test.ts" -o -name "*.spec.ts" -o -name "test_*.py" 2>/dev/null | wc -l

# 7. Recent significant changes (last 90 days)
git log --oneline --since="90 days ago" | grep -iE "feat|refactor|breaking|migrate" | head -20

# 8. CI/CD configuration
ls .github/workflows/ 2>/dev/null || ls .gitlab-ci.yml 2>/dev/null || echo "No CI config found"

# 9. Environment variables referenced in code
grep -rh "process\.env\.\|os\.environ\.\|os\.getenv" src/ app/ lib/ --include="*.ts" --include="*.py" 2>/dev/null | \
  grep -oE "[A-Z_]{3,}" | sort -u | head -30
```

### Phase 2: Identify Architecture Patterns

Based on gathered facts, classify the project:

| Signal | Architecture Pattern |
|--------|---------------------|
| `app/` directory with `page.tsx` | Next.js App Router (file-based routing) |
| `src/routes/` with Express imports | Express REST API |
| FastAPI decorators | Python REST/async API |
| `docker-compose.yml` with multiple services | Microservices |
| Single `main.go` with handlers | Go monolith |
| `packages/` or `apps/` at root | Monorepo |
| Prisma/Drizzle schema file | ORM-managed database |
| `k8s/` or `terraform/` directories | Infrastructure as Code |

### Phase 3: Generate Documentation

## Architecture Overview Template

```markdown
## Architecture

### System Diagram

[Use the ASCII diagram pattern below — it renders in any markdown viewer]

```
Browser / Mobile App
    │
    v
[API Gateway / Load Balancer]
    │
    ├──> [Web Server: Next.js / Express / FastAPI]
    │       ├── Authentication (JWT / OAuth)
    │       ├── Business Logic
    │       └── Background Jobs
    │
    ├──> [Primary Database: PostgreSQL]
    │       └── Migrations managed by [ORM]
    │
    ├──> [Cache: Redis]
    │       └── Sessions, rate limits, job queue
    │
    └──> [Object Storage: S3 / R2]
            └── File uploads, static assets

External Integrations:
    ├── [Stripe] — Payments
    ├── [SendGrid / Resend] — Transactional email
    └── [Sentry] — Error tracking
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | [framework] | [why chosen] |
| API | [framework] | [routing, middleware] |
| Database | [database + ORM] | [data storage, migrations] |
| Auth | [provider] | [authentication method] |
| Queue | [system] | [background processing] |
| Deployment | [platform] | [hosting, CI/CD] |
| Monitoring | [tool] | [errors, performance] |
```

## Key File Map Template

```markdown
## Key Files

Priority files — read these first to understand the system:

| Priority | Path | What It Does | When to Read |
|----------|------|-------------|-------------|
| 1 | `src/db/schema.ts` | Database schema — single source of truth for data model | First day |
| 2 | `src/lib/auth.ts` | Authentication configuration and session handling | First day |
| 3 | `app/api/` | All API route handlers | First week |
| 4 | `middleware.ts` | Request middleware (auth, logging, rate limiting) | First week |
| 5 | `.env.example` | All environment variables with descriptions | Setup day |

Dangerous files — coordinate before modifying:

| Path | Risk | Coordination Required |
|------|------|----------------------|
| `src/db/schema.ts` | Schema changes affect all services | PR review from DB owner |
| `middleware.ts` | Affects every request | Load test after changes |
| `lib/stripe.ts` | Payment processing | Finance team notification |
```

## Local Setup Guide Template

```markdown
## Local Setup (Target: under 10 minutes)

### Prerequisites

| Tool | Required Version | Install Command |
|------|-----------------|----------------|
| Node.js | 20+ | `nvm install 20` |
| pnpm | 9+ | `corepack enable && corepack prepare pnpm@latest` |
| Docker | 24+ | [docker.com/get-docker](https://docker.com/get-docker) |
| PostgreSQL | 16+ | Via Docker (see step 3) |

### Steps

**Step 1: Clone and install** (2 min)
```bash
git clone [repo-url]
cd [repo-name]
pnpm install
```

**Step 2: Configure environment** (1 min)
```bash
cp .env.example .env
# Edit .env — minimum required values:
#   DATABASE_URL=postgresql://dev:dev@localhost:5432/myapp
#   APP_SECRET=$(openssl rand -base64 32)
```

**Step 3: Start infrastructure** (1 min)
```bash
docker compose up -d
# Starts: PostgreSQL, Redis
# Verify: docker compose ps (all should show "running")
```

**Step 4: Set up database** (1 min)
```bash
pnpm db:migrate
pnpm db:seed    # Optional: loads test data
```

**Step 5: Start dev server** (30 sec)
```bash
pnpm dev
# App runs at http://localhost:3000
```

### Verify Everything Works

- [ ] http://localhost:3000 loads the app
- [ ] http://localhost:3000/api/health returns `{"status": "ok"}`
- [ ] `pnpm test` passes with no failures
- [ ] You can log in with the seeded test user (see .env.example for credentials)
```

## Debugging Guide Template

```markdown
## Debugging Guide

### Common Errors and Fixes

**`Error: connect ECONNREFUSED 127.0.0.1:5432`**
```
Cause: PostgreSQL is not running
Fix: docker compose up -d postgres
Verify: docker compose ps postgres (should show "running")
```

**`Error: relation "users" does not exist`**
```
Cause: Migrations have not been applied
Fix: pnpm db:migrate
Verify: pnpm db:migrate status (should show all applied)
```

**`TypeError: Cannot read property 'id' of null`**
```
Cause: Session is null — usually a missing or expired auth token
Fix: Check that the request includes a valid Authorization header
Debug: Add console.log(session) in the route handler to inspect
```

### Where to Find Logs

| Environment | Location | Command |
|-------------|----------|---------|
| Local dev | Terminal running `pnpm dev` | Scroll up in terminal |
| Local DB | Docker logs | `docker compose logs postgres` |
| Staging | [Platform dashboard] | [Link to staging logs] |
| Production | [Platform dashboard] | [Link to production logs] |

### Useful Diagnostic Commands

```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT 1"

# View active database connections
psql $DATABASE_URL -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state"

# Check if a specific migration was applied
pnpm db:migrate status

# Clear local caches
redis-cli FLUSHDB

# Verify environment variables are loaded
node -e "console.log(process.env.DATABASE_URL ? 'Set' : 'MISSING')"
```
```

## Audience-Specific Customization

### Junior Developer Additions
- Explain acronyms on first use (ORM, RLS, JWT, etc.)
- Add "read this first" ordered reading list of 5 files
- Include screenshots for UI-related flows
- Link to external learning resources for key technologies
- Add a "glossary" section for domain-specific terms

### Senior Engineer Additions
- Link to Architecture Decision Records (ADRs)
- Include performance benchmark baselines
- Document known technical debt and planned improvements
- Provide security model overview with threat boundaries
- Share scaling limits and planned capacity changes

### Contractor Additions
- Define scope boundaries ("only modify files in src/features/your-feature/")
- Specify communication channels and response expectations
- Document access request process for required systems
- Include time logging requirements and reporting cadence
- List prohibited actions (direct push to main, schema changes, etc.)

## Quality Verification

After generating onboarding docs, validate with this checklist:

1. **Fresh machine test** — can a new developer follow the setup guide verbatim on a clean machine?
2. **10-minute target** — does local setup complete in under 10 minutes?
3. **Error coverage** — do the documented errors match what developers actually encounter?
4. **Link validity** — do all links to external resources and internal docs resolve?
5. **Currency** — are all version numbers, commands, and screenshots current?

## Common Pitfalls

- **Docs written once, never updated** — add doc update checks to the PR template
- **Missing "why" for architecture decisions** — document why, not just what
- **Untested setup instructions** — test the docs on a fresh machine quarterly
- **No debugging section** — the debugging guide is the most valuable section for new hires
- **Too much detail for the wrong audience** — contractors need task-specific docs, not deep architecture
- **Stale screenshots** — UI screenshots go stale fast; link to running instances when possible

## Best Practices

1. **Keep setup under 10 minutes** — if it takes longer, fix the setup process, not the docs
2. **Test the docs** — have a new hire follow them literally and fix every gap they hit
3. **Link, do not repeat** — reference ADRs, issues, and external docs instead of duplicating
4. **Update docs in the same PR as code changes** — documentation drift is the number one failure mode
5. **Version-specific notes** — call out what changed in recent versions so returning developers catch up
6. **Runbooks over theory** — "run this command" is more useful than "the system uses Redis for caching"
7. **Key file map is mandatory** — every project should have an annotated list of the 10-20 most important files
