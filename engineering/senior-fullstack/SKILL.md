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
  updated: 2026-06-17
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

Use this skill when you hear:
- "scaffold a new project" / "set up a fullstack project" / "generate project boilerplate"
- "create a Next.js app" / "set up FastAPI with React"
- "analyze code quality" / "check for security issues in codebase"
- "what stack should I use"

## Clarify First

Before scaffolding, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Stack** — Next.js / FastAPI+React / MERN / Django+React (selects the scaffold template and entire file tree)
- [ ] **App name & output path** — where the project is written (`project_scaffolder` positional args)
- [ ] **Task** — scaffold a new project vs analyze an existing codebase's quality (selects `project_scaffolder` vs `code_quality_analyzer`)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `project_scaffolder.py` | Scaffold a fullstack project structure with boilerplate, Docker, and env config | `python scripts/project_scaffolder.py nextjs my-app --output ./projects` |
| `code_quality_analyzer.py` | Static-analyze a codebase for security, complexity, deps, coverage, and docs | `python scripts/code_quality_analyzer.py . --verbose --json --output audit.json` |

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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-devops` | CI/CD pipeline setup for scaffolded projects | Scaffolder output directory feeds into DevOps pipeline configuration and Docker deployment workflows |
| `senior-secops` | Deep security audit after initial quality scan | Code quality analyzer P0/P1 security findings hand off to SecOps for remediation tracking and penetration testing |
| `senior-qa` | Test strategy for scaffolded projects | Test coverage estimation from the analyzer informs QA test plan gaps; scaffolded test infrastructure provides the harness |
| `code-reviewer` | Automated review of generated and existing code | Quality analyzer JSON report provides structured input for code review checklists and PR approval criteria |
| `senior-architect` | Architecture validation of stack choices | Tech stack guide recommendations feed into architecture decision records; complexity metrics validate design compliance |
| `aws-solution-architect` | Cloud deployment of scaffolded applications | Docker Compose configurations from the scaffolder translate into ECS/EKS task definitions and infrastructure blueprints |
