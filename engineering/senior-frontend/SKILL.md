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
  updated: 2026-11-08
  tags: [react, typescript, accessibility, performance, state-management]
---
# Senior Frontend

Frontend development patterns, performance optimization, and automation tools for React/Next.js applications. Scaffold projects, generate components and hooks, analyze bundle sizes, and apply React/Next.js patterns with accessibility and testing built in.

## Core Capabilities

- **Project scaffolding** — generate Next.js 16 (App Router) or React+Vite projects with TypeScript, Tailwind, and optional auth/api/forms/testing/storybook features.
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

Before scaffolding or generating, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Template:** Next.js (App Router) vs React+Vite (`--template`; produces a different project structure).
- **Features:** auth / api / forms / testing / storybook (`--features`; decides what gets generated).
- **Generation target:** a new project vs a component/hook in an existing app (selects `frontend_scaffolder` vs `component_generator`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

| Tool | Purpose | Example (runs as written) |
|------|---------|---------|
| `frontend_scaffolder.py` | Scaffold Next.js 16 (App Router) or React + Vite 8 with React 19, TypeScript and Tailwind CSS v4 (`--template`, `--features auth,api,forms,testing,storybook`, `--dir`, `--dry-run`, `--json`) | `python scripts/frontend_scaffolder.py my-app --dir /tmp/web --template nextjs --features auth,api` |
| `component_generator.py` | Component or hook with optional test and Storybook story (`--type`, `--with-test`, `--with-story`, `--dir`) | `python scripts/component_generator.py ProductCard --type client --with-test --with-story --dir /tmp/web/components` |
| `bundle_analyzer.py` | Flag heavy or duplicate dependencies from `package.json` and imports, with a health score (`--verbose`, `--json`) | `python scripts/bundle_analyzer.py /tmp/web/my-app --verbose` |

Exit codes: `0` ok; `2` bad input (target folder exists, unwritable path, unknown feature,
missing project or `package.json`). The bundle score never fails the run.

`bundle_analyzer.py` works from dependency names and import statements; it cannot see real
bundle sizes, tree-shaking or code splitting. For ground truth run the framework's analyzer
(`@next/bundle-analyzer`, `vite-bundle-visualizer`) on a production build. Scaffold versions
target Next.js 16, React 19, Tailwind v4 and Vite 8 (as of November 2026: Next 16.4, React 19.3, Tailwind 4.3, Vite 8.3); the `auth` feature writes `proxy.ts`, which replaced `middleware.ts` in Next 16, and linting uses ESLint 9 flat config because `next lint` was removed; check each project's release notes before
bumping a major, and run the build once after `npm install`.

## Workflow

1. Scaffold or open the project, then generate components with tests next to them.
2. Build each component against the accessibility basics: semantic elements, labels, keyboard focus, visible focus states.
3. Run `npm run build` and the framework bundle analyzer; use `bundle_analyzer.py` to spot heavy dependencies worth replacing.
4. Done when the build passes, tests pass, Lighthouse or Web Vitals meet the agreed budget (for example LCP under 2.5 s on a mid-range phone), and no client bundle carries an avoidable heavy dependency.

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

## Anti-Patterns

### Client Components by Default
**Mistake:** Marking whole pages `'use client'` in the App Router.
**Why it happens:** It makes hooks and event handlers work immediately.
**Instead:** Keep pages and layouts as Server Components and push `'use client'` down to the smallest interactive leaf; that keeps data fetching on the server and JavaScript out of the bundle.

### Judging Bundle Size From package.json
**Mistake:** Reporting the static analyzer's score as the bundle size.
**Why it happens:** It is quick and gives a number.
**Instead:** Measure a production build with the framework's analyzer; tree-shaking and dynamic imports change the picture.

### Accessibility as a Final Pass
**Mistake:** Adding labels and keyboard support after the UI is done.
**Why it happens:** It is invisible in a mouse-driven demo.
**Instead:** Build with semantic elements from the start and check keyboard and screen-reader paths per component; retrofitting means rewriting.

## Files

| File | Purpose |
|------|---------|
| `scripts/frontend_scaffolder.py` | Next.js / React + Vite project scaffolder |
| `scripts/component_generator.py` | Component, hook, test and story generator |
| `scripts/bundle_analyzer.py` | Static dependency and import analysis |
| `references/*.md` | Code patterns, best practices, Next.js optimisation, React patterns, tooling |
