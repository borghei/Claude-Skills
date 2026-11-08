---
name: senior-fullstack
description: >
  Fullstack development toolkit with project scaffolding for
  Next.js/FastAPI/MERN/Django stacks and code quality analysis. Use when
  scaffolding new projects, analyzing codebase quality, or implementing
  fullstack architecture patterns.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: fullstack
  updated: 2026-11-08
  tags: [react, nodejs, databases, api-design, system-architecture]
---
# Senior Fullstack

Fullstack development skill that scaffolds production-ready project structures (Next.js, FastAPI+React, MERN, Django+React) and runs static code quality analysis across security, complexity, dependency health, test coverage, and documentation — paired with reference guides for architecture patterns, development workflows, and stack selection.

## Core Capabilities

- **Project scaffolding** — generate complete Next.js, FastAPI+React, MERN, or Django+React structures with TypeScript, Docker/docker-compose, env templates, and package configs.
- **Code quality analysis** — static scan for security issues, cyclomatic complexity, dependency CVEs, test coverage estimate, and documentation scoring, with an overall score/grade and prioritized P0/P1/P2 recommendations.
- **Stack selection** — decision matrix and trade-off guides for frameworks, databases, ORMs, auth, and deployment platforms by use case (MVP, SaaS, Enterprise).
- **Architecture patterns** — frontend component design, backend clean architecture, API design (REST/GraphQL), caching, and authentication.
- **Lifecycle workflows** — local setup, git, CI/CD, testing, code review, deployment, and observability.

## When to Use

- Starting a new web app that needs both a frontend and an API (Next.js alone, FastAPI or Django + React, MERN).
- A quick quality pass over an existing codebase before a review or handover.
- Choosing a fullstack stack for an MVP, SaaS or internal tool.

Boundaries: frontend-only work (components, Next.js performance, bundle size) belongs to
`senior-frontend`; a weighted, evidence-backed comparison of technologies belongs to
`tech-stack-evaluator`; system-level architecture decisions belong to `senior-architect`.

## Clarify First

Before scaffolding, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Stack:** Next.js / FastAPI+React / MERN / Django+React (selects the scaffold template and entire file tree).
- **App name & output path:** where the project is written (`project_scaffolder` positional args).
- **Task:** scaffold a new project vs analyze an existing codebase's quality (selects `project_scaffolder` vs `code_quality_analyzer`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

| Tool | Purpose | Example (runs as written) |
|------|---------|---------|
| `project_scaffolder.py` | Scaffold `nextjs`, `fastapi-react`, `mern` or `django-react` with Docker, env templates and per-service package configs (`--output`, `--list-templates`, `--json`) | `python scripts/project_scaffolder.py fastapi-react my-app --output /tmp/projects` |
| `code_quality_analyzer.py` | Static scan for security patterns, complexity, dependency hygiene, test-file ratio and docs, with a grade and P0-P2 actions (`--verbose`, `--json`, `--output`) | `python scripts/code_quality_analyzer.py /tmp/projects/my-app --json` |

Exit codes: `0` ok; `2` bad input (unknown template, target folder exists, unwritable path,
missing analysis path). The analyzer's grade never fails the run.

The scaffolds target Next.js 16, React 19, Tailwind CSS v4, Vite 8, Express 5, Node 22,
Python 3.12 and PostgreSQL 17 / MongoDB 7. Most generated files are working starting points;
some (database clients, auth) are stubs to fill in. Run `npm install && npm run build` (and
the backend's install and migrations) once before handing a scaffold over. The analyzer's
"coverage" is a test-file ratio, not measured coverage; use the test runner's coverage report
for real numbers.

## Workflow

1. Pick the template from the Clarify First answers and scaffold into the target folder.
2. Install and build every service once; fix anything the build reports before writing features.
3. Run `code_quality_analyzer.py` on the result and on each later milestone; act on P0 items first.
4. Done when every service builds and starts with `docker compose up`, the health endpoint answers, and the analyzer reports no P0 findings.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tooling-workflows-and-quality.md](references/tooling-workflows-and-quality.md)** — full tool docs (templates, flags, sample output, output formats), the three end-to-end workflows, the stack decision matrix / common issues, the troubleshooting table, and the success-criteria bar. Read when running the tools in depth or checking generated work before shipping.
- **[references/architecture_patterns.md](references/architecture_patterns.md)** — frontend component architecture, backend clean architecture / repository pattern, REST & GraphQL API design, database patterns, caching strategies, and authentication architecture. Read when designing or reviewing system structure.
- **[references/development_workflows.md](references/development_workflows.md)** — local dev setup, git workflows, CI/CD pipelines, testing strategies, code review process, deployment strategies, and observability. Read when standing up the development lifecycle.
- **[references/tech_stack_guide.md](references/tech_stack_guide.md)** — frontend/backend framework comparisons, database selection, ORMs, auth solutions, deployment platforms, and stack recommendations by use case. Read when choosing a stack.

## Scope & Limitations

**What this skill covers:**
- Project scaffolding for Next.js, FastAPI+React, MERN, and Django+React stacks with Docker, TypeScript, and environment configuration
- Static code quality analysis including complexity metrics, security pattern detection, dependency vulnerability checks, test coverage estimation, and documentation scoring
- Stack selection guidance via the tech stack decision matrix and reference guides
- Fullstack architecture patterns (frontend component design, backend clean architecture, API design, caching, auth)

**What this skill does NOT cover:**
- Runtime performance profiling, load testing, or APM instrumentation -- see `senior-devops` for observability tooling
- Infrastructure provisioning, Terraform/Pulumi, or cloud deployment automation -- see `aws-solution-architect` and `senior-devops`
- Comprehensive CVE scanning against live vulnerability databases -- use `npm audit`, `pip-audit`, or `senior-secops` for deep security analysis
- Mobile or native desktop application scaffolding -- this skill targets web-based fullstack architectures only

## Anti-Patterns

### Shipping the Scaffold's Defaults
**Mistake:** Deploying with the generated `.env.example` secrets, the dev-server Docker command and open CORS.
**Why it happens:** The scaffold runs, so it feels production-ready.
**Instead:** Treat it as a dev setup. Replace secrets, switch containers to production commands, lock CORS to known origins, and add health checks before deploying.

### One Database Model Shared Across Layers
**Mistake:** Returning ORM models straight from API handlers.
**Why it happens:** It saves a mapping layer.
**Instead:** Keep request/response schemas (Pydantic, Zod, DRF serializers) separate from persistence models, so a column change does not silently change the public API or leak fields like password hashes.

### Grading Quality by the Analyzer Alone
**Mistake:** Reporting an A grade as "the codebase is healthy".
**Why it happens:** The grade is a single, quotable number.
**Instead:** The analyzer reads code statically. Pair it with the real test suite's coverage, `npm audit` / `pip-audit`, and a human review of the riskiest modules.

## Files

| File | Purpose |
|------|---------|
| `scripts/project_scaffolder.py` | Fullstack project scaffolder for four stacks |
| `scripts/code_quality_analyzer.py` | Static code quality scan and grade |
| `references/*.md` | Tooling and quality workflows, architecture patterns, development workflows, stack guide |
