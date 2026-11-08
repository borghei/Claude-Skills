---
name: senior-frontend
description: >
  Scaffold Next.js 16 or React + Vite 8 apps, generate components with tests and
  stories, and flag heavy bundle dependencies. Use when starting a React project,
  adding components or hooks, or reviewing frontend code or performance.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: frontend
  updated: 2026-11-08
  tags: [react, nextjs, typescript, tailwind, accessibility, performance, scaffolding]
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

## Quick Start

```bash
# Scaffold a Next.js 16 app with auth (writes proxy.ts) and the API client feature
python3 engineering/senior-frontend/scripts/frontend_scaffolder.py my-app \
  --dir /tmp/web --template nextjs --features auth,api

# Add a client component with a test and a Storybook story
python3 engineering/senior-frontend/scripts/component_generator.py ProductCard \
  --type client --with-test --with-story --framework next --dir /tmp/web/my-app/components

# Bundle check on the bundled samples: sound passes, flawed fails the gate (exit 1)
python3 engineering/senior-frontend/scripts/bundle_analyzer.py \
  engineering/senior-frontend/assets/sample-project-sound --verbose --min-score 80
python3 engineering/senior-frontend/scripts/bundle_analyzer.py \
  engineering/senior-frontend/assets/sample-project-flawed --verbose --min-score 80 --format json
```

## Tools Overview

| Tool | Purpose | Key flags |
|------|---------|-----------|
| `frontend_scaffolder.py` | Scaffold Next.js 16 (App Router) or React + Vite 8 with React 19, TypeScript and Tailwind CSS v4 | `--template`, `--features auth,api,forms,testing,storybook`, `--dir`, `--dry-run`, `--list-templates`, `--list-features` (no name needed) |
| `component_generator.py` | Component or hook with optional Vitest test and Storybook 10 story | `--type client\|server\|hook`, `--with-test`, `--with-story`, `--framework next\|vite`, `--no-index`, `--flat`, `--force`, `--dry-run` |
| `bundle_analyzer.py` | Flag heavy or misplaced dependencies from `package.json` and imports, with a health score; detects Next vs Vite and runs `next.config` checks only on Next | `--verbose` (import scan), `--min-score N` (gate) |

- **Output:** all three take `--format text|json`; `--json` still works on the scaffolder and the analyzer.
- **Exit codes:** `0` ok; `1` bundle score below `--min-score` (only with that flag); `2` bad input: target folder exists, a project name that is not a lowercase npm package name or escapes `--dir`, a component file that already exists (without `--force`), unknown feature or type, missing project or `package.json`, missing template files.
- **Naming:** hook names drop a leading `use`, so `useCart --type hook` writes `useCart.ts`, not `useUseCart.ts`.
- **Analyzer limits:** it reads dependency names and import statements, not real bundle sizes, tree-shaking or code splitting. For ground truth, run `@next/bundle-analyzer` or `vite-bundle-visualizer` on a production build.
- **Versions (November 2026):** Next 16.4, React 19.3, Tailwind 4.3, Vite 8.3. The Next `auth` feature writes `proxy.ts`, which replaced `middleware.ts` in Next 16.
- **Lint and types:** `next lint` is gone, so both templates use ESLint flat config: ESLint 9 for Next (its plugins stop at 9), ESLint 10 for Vite. TypeScript is held at 6.0 because typescript-eslint does not support 7 yet; `manifest.json` (`_pins`) records why.
- **Before a major bump:** read the project's release notes, then run the build once after `npm install`.

## Workflow

1. **Scaffold or open the project [PROVEN].** Run `frontend_scaffolder.py --dry-run --format json` first to see the file list, then scaffold. Read the `Notes` it prints: they list what the scaffold cannot do for you (for `auth`, the login/register route handlers and user store on Next, and a real server behind the Vite guard).
2. **Generate components with tests next to them [PROVEN].** One `component_generator.py` call per component; keep pages and layouts as Server Components and generate `--type client` only for interactive leaves.
3. **Build to the accessibility basics [PROVEN]:** semantic elements, labels, keyboard focus, visible focus states. Check each component by keyboard before moving on.
4. **Check the bundle [RECOMMENDED].** Run `npm run build` and the framework bundle analyzer; use `bundle_analyzer.py --verbose --min-score 80` to spot heavy dependencies worth replacing and to gate CI on the static score.
5. **Done when** the build passes, tests pass, Lighthouse or Web Vitals meet the agreed budget (for example LCP under 2.5 s on a mid-range phone), and no client bundle carries an avoidable heavy dependency.

To change what the scaffolder writes, edit the files under `assets/templates/scaffold/` (and `manifest.json` for paths, features and dependencies) rather than the script.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tooling-guide.md](references/tooling-guide.md)** — full scaffolding / component-generation / bundle-analysis workflows, option tables, generated structure, the per-script flag reference, troubleshooting table, and success criteria. Read when running a tool or wiring up CLI flags.
- **[references/code-patterns.md](references/code-patterns.md)** — inline React patterns (compound components, hooks, render props), Next.js optimization (Server/Client, image, data fetching), accessibility + testing snippets, and the Next.js config / Tailwind / TypeScript quick reference. Read when writing components or optimizing pages.
- **[references/react_patterns.md](references/react_patterns.md)** — deep React patterns library. Read when designing component/state architecture.
- **[references/nextjs_optimization_guide.md](references/nextjs_optimization_guide.md)** — deep Next.js performance and rendering guide. Read when tuning Next.js apps.
- **[references/frontend_best_practices.md](references/frontend_best_practices.md)** — accessibility, testing, and general frontend best-practice guide. Read before shipping a component.

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

### Trusting the Client-Side Guard
**Mistake:** Treating the scaffolded `auth` feature as complete authentication, especially `RequireAuth` in a Vite app.
**Why it happens:** The forms render, the guard hides pages and the project builds, so it looks finished.
**Instead:** The guard and the `proxy.ts` cookie check only steer navigation. Credentials must be checked, and the session verified on every API request, on a server you write (`verifySessionToken()` in Next's `lib/auth.ts`).

## Files

| File | Purpose |
|------|---------|
| `scripts/frontend_scaffolder.py` | Next.js / React + Vite project scaffolder |
| `scripts/component_generator.py` | Component, hook, test and story generator |
| `scripts/bundle_analyzer.py` | Static dependency and import analysis with optional score gate |
| `assets/templates/scaffold/manifest.json` | Project structures, features, dependencies, and the map from content keys to template files |
| `assets/templates/scaffold/files/`, `config/` | Bodies of every generated source and config file (`index.html.tmpl` takes the project name) |
| `assets/templates/component/*.tmpl` | Component, hook, test, story and index templates (`{name}` placeholder) |
| `assets/sample-project-sound/` | Lean Next.js sample — analyzer scores 100, exits 0 with `--min-score 80` |
| `assets/sample-project-flawed/` | Heavy dependencies, misplaced dev packages and bad imports — scores 46, exits 1 with `--min-score 80` |
| `references/bundle_rules.json` | Heavy-package, optimisation-tip, dev-only and import-pattern rule tables |
| `references/*.md` | Code patterns, best practices, Next.js optimisation, React patterns, tooling |

## Scope & Limitations

**What this skill covers:**
- React and Next.js project scaffolding with TypeScript and Tailwind CSS
- Component, hook, test, and Storybook story generation following established patterns
- Static bundle analysis based on `package.json` dependency inspection and import pattern scanning
- Frontend-specific best practices for Server Components, image optimization, data fetching, and accessibility

**What this skill does NOT cover:**
- Choosing a visual direction or design system from a brief -- see **product-team/design-direction**
- Building a marketing site end to end with its finish gate -- see **engineering/marketing-site-builder**
- Refining an existing UI with the generic-pattern detector and named commands -- see **engineering/interface-refinement**
- Grading a finished UI -- see **engineering/design-auditor**; WCAG conformance audits -- see **engineering/a11y-audit**
- Token and component-library design -- see **product-team/ui-design-system**; product UX and flows -- see **product-team/product-designer**
- Backend API development, database schema design, or server infrastructure -- see **senior-backend** and **senior-fullstack**
- End-to-end testing with Cypress or Playwright -- see **senior-qa**
- CI/CD pipeline configuration and Docker deployment -- see **senior-devops**
- Security vulnerability scanning and penetration testing -- see **senior-secops** and **senior-security**

This skill owns the code layer: project skeletons, component files and dependency hygiene.
