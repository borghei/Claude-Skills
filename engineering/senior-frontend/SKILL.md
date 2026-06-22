---
name: senior-frontend
description: >
  Frontend development for React, Next.js, TypeScript, and Tailwind CSS. Use when building
  React components, optimizing Next.js performance, analyzing bundle sizes, scaffolding
  projects, implementing accessibility, or reviewing frontend code.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: frontend
  updated: 2026-06-17
  tags: [react, typescript, accessibility, performance, state-management]
---
# Senior Frontend

Frontend development patterns, performance optimization, and automation tools for React/Next.js applications. Scaffold projects, generate components and hooks, analyze bundle sizes, and apply React/Next.js patterns with accessibility and testing built in.

## Core Capabilities

- **Project scaffolding** — generate Next.js 14+ (App Router) or React+Vite projects with TypeScript, Tailwind, and optional auth/api/forms/testing/storybook features.
- **Component generation** — client/server components, custom hooks, with test and Storybook story files following established patterns.
- **Bundle analysis** — static `package.json` + import scanning that scores bundle health and flags heavy dependencies with lighter alternatives.
- **React patterns** — compound components, custom hooks, render props, and reusable state-sharing patterns.
- **Next.js optimization** — Server vs Client Components, image optimization, parallel/streaming data fetching with Suspense.
- **Accessibility & testing** — semantic HTML, ARIA, keyboard nav, focus, and React Testing Library component/a11y tests.

## When to Use

- Starting a new React/Next.js project that needs a best-practice baseline.
- Adding components, hooks, or test/story scaffolding to an existing app.
- Optimizing bundle size or diagnosing heavy dependencies.
- Implementing accessible, performant Server/Client Component architecture.
- Reviewing frontend code against React/TypeScript/a11y best practices.

## Clarify First

Before scaffolding or generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Template** — Next.js (App Router) vs React+Vite (`--template`; produces a different project structure)
- [ ] **Features** — auth / api / forms / testing / storybook (`--features`; decides what gets generated)
- [ ] **Generation target** — a new project vs a component/hook in an existing app (selects `frontend_scaffolder` vs `component_generator`)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `frontend_scaffolder.py` | Scaffold a Next.js or React project with TypeScript + Tailwind + optional features | `python scripts/frontend_scaffolder.py my-app --template nextjs --features auth,api` |
| `component_generator.py` | Generate a component/hook with optional test and Storybook story | `python scripts/component_generator.py ProductCard --type client --with-test --with-story` |
| `bundle_analyzer.py` | Score bundle health and flag heavy dependencies from `package.json` + imports | `python scripts/bundle_analyzer.py /path/to/project --verbose` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tooling-guide.md](references/tooling-guide.md)** — full scaffolding / component-generation / bundle-analysis workflows, option tables, generated structure, the per-script flag reference, troubleshooting table, and success criteria. Read when running a tool or wiring up CLI flags.
- **[references/code-patterns.md](references/code-patterns.md)** — inline React patterns (compound components, hooks, render props), Next.js optimization (Server/Client, image, data fetching), accessibility + testing snippets, and the Next.js config / Tailwind / TypeScript quick reference. Read when writing components or optimizing pages.
- **[references/react_patterns.md](references/react_patterns.md)** — deep React patterns library. Read when designing component/state architecture.
- **[references/nextjs_optimization_guide.md](references/nextjs_optimization_guide.md)** — deep Next.js performance and rendering guide. Read when tuning Next.js apps.
- **[references/frontend_best_practices.md](references/frontend_best_practices.md)** — accessibility, testing, and general frontend best-practice guide. Read before shipping a component.

## Scope & Limitations

**What this skill covers:**
- React and Next.js project scaffolding with TypeScript and Tailwind CSS
- Component, hook, test, and Storybook story generation following established patterns
- Static bundle analysis based on `package.json` dependency inspection and import pattern scanning
- Frontend-specific best practices for Server Components, image optimization, data fetching, and accessibility

**What this skill does NOT cover:**
- Backend API development, database schema design, or server infrastructure -- see **senior-backend** and **senior-fullstack**
- End-to-end testing with Cypress or Playwright -- see **senior-qa**
- CI/CD pipeline configuration and Docker deployment -- see **senior-devops**
- Security vulnerability scanning and penetration testing -- see **senior-secops** and **senior-security**

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **senior-fullstack** | Scaffolded frontend projects connect to fullstack project scaffolder for API layer setup | Frontend project structure feeds into `project_scaffolder.py` which adds backend, Docker, and CI/CD layers |
| **senior-backend** | Components consuming API data follow patterns defined by backend skill's REST/GraphQL conventions | Backend API response types imported into frontend `types/` directory generated by this skill |
| **senior-qa** | Generated test files (`--with-test`) use the same Testing Library conventions that the QA skill's test strategies build upon | Component test files hand off to QA skill for integration and E2E test coverage expansion |
| **senior-devops** | Bundle analyzer output informs build pipeline optimization decisions | Bundle health score and dependency warnings feed into CI quality gates configured by DevOps skill |
| **senior-secops** | Dependency analysis identifies packages that need security audit | Heavy/outdated dependency warnings from `bundle_analyzer.py` trigger security review workflows |
| **code-reviewer** | Generated components follow patterns that the code reviewer skill validates | Code reviewer checks generated components against React/TypeScript best practices defined in this skill's references |
