# Frontend Tooling Guide

Read this when scaffolding a project, generating components, analyzing bundles, or you need the full CLI flag reference, troubleshooting table, or success criteria for the three scripts.

## Project Scaffolding

Generate a new Next.js or React project with TypeScript, Tailwind CSS, and best practice configurations.

### Workflow: Create New Frontend Project

1. Run the scaffolder with your project name and template:
   ```bash
   python scripts/frontend_scaffolder.py my-app --template nextjs
   ```

2. Add optional features (auth, api, forms, testing, storybook):
   ```bash
   python scripts/frontend_scaffolder.py dashboard --template nextjs --features auth,api
   ```

3. Navigate to the project and install dependencies:
   ```bash
   cd my-app && npm install
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

### Scaffolder Options

| Option | Description |
|--------|-------------|
| `--template nextjs` | Next.js 16 with App Router and Server Components |
| `--template react` | React + Vite with TypeScript |
| `--features auth` | Next: signed session cookie (`lib/auth.ts`, Web Crypto) + `proxy.ts` + login/register forms. Vite: client token store, `src/components/RequireAuth.tsx` guard + the same forms (real auth still needs a server) |
| `--features api` | Typed `fetch` client (`ApiError`) + React Query client and provider |
| `--features forms` | `useZodForm` (React Hook Form + Zod) + accessible `FormField` |
| `--features testing` | Vitest + Testing Library + jsdom, `renderWithProviders`, `npm test` |
| `--features storybook` | Storybook 10 (`@storybook/nextjs-vite` or `@storybook/react-vite`), `npm run storybook` |
| `--dry-run` | Preview files without creating them |

### Generated Structure (Next.js)

```
my-app/
├── app/
│   ├── layout.tsx        # Root layout with fonts
│   ├── page.tsx          # Home page
│   ├── globals.css       # Tailwind + CSS variables
│   └── api/health/route.ts
├── components/
│   ├── ui/               # Button, Input, Card
│   └── layout/           # Header, Footer, Sidebar
├── hooks/                # useDebounce, useLocalStorage
├── lib/                  # utils (cn), constants
├── types/                # TypeScript interfaces
├── tailwind.config.ts
├── next.config.js
└── package.json
```

### Generated Structure (React + Vite)

```
my-app/
├── src/
│   ├── App.tsx, main.tsx, index.css
│   ├── components/ui/    # Button, Input, Card
│   ├── hooks/ lib/ types/
│   └── (feature files: lib/auth.ts, components/RequireAuth.tsx, providers/, test/ ...)
├── index.html
├── vite.config.ts        # '@' -> ./src
├── tsconfig.json         # references tsconfig.app.json (src) + tsconfig.node.json (configs)
├── eslint.config.js      # ESLint 9 flat config: @eslint/js, typescript-eslint, react-hooks
└── package.json          # "type": "module"; build = tsc -b && vite build
```

Feature files follow each template's layout: Next paths at the project root (`lib/`, `components/`), Vite paths under `src/`. Config files (`vitest.config.ts`, `.storybook/`) sit at the root in both.

---

## Component Generation

Generate React components with TypeScript, tests, and Storybook stories.

### Workflow: Create a New Component

1. Generate a client component:
   ```bash
   python scripts/component_generator.py Button --dir src/components/ui
   ```

2. Generate a server component:
   ```bash
   python scripts/component_generator.py ProductCard --type server
   ```

3. Generate with test and story files:
   ```bash
   python scripts/component_generator.py UserProfile --with-test --with-story
   ```

4. Generate a custom hook:
   ```bash
   python scripts/component_generator.py FormValidation --type hook
   ```

### Generator Options

| Option | Description |
|--------|-------------|
| `--type client` | Client component with 'use client' (default) |
| `--type server` | Async server component |
| `--type hook` | Custom React hook |
| `--with-test` | Include test file |
| `--with-story` | Include Storybook story |
| `--flat` | Create in output dir without subdirectory |
| `--dry-run` | Preview without creating files |

### Generated Component Example

```tsx
'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps {
  className?: string;
  children?: React.ReactNode;
}

export function Button({ className, children }: ButtonProps) {
  return (
    <div className={cn('', className)}>
      {children}
    </div>
  );
}
```

---

## Bundle Analysis

Analyze package.json and project structure for bundle optimization opportunities.

### Workflow: Optimize Bundle Size

1. Run the analyzer on your project:
   ```bash
   python scripts/bundle_analyzer.py /path/to/project
   ```

2. Review the health score and issues:
   ```
   Bundle Health Score: 75/100 (C)

   HEAVY DEPENDENCIES:
     moment (290KB)
       Alternative: date-fns (12KB) or dayjs (2KB)

     lodash (71KB)
       Alternative: lodash-es with tree-shaking
   ```

3. Apply the recommended fixes by replacing heavy dependencies.

4. Re-run with verbose mode to check import patterns:
   ```bash
   python scripts/bundle_analyzer.py . --verbose
   ```

### Bundle Score Interpretation

| Score | Grade | Action |
|-------|-------|--------|
| 90-100 | A | Bundle is well-optimized |
| 80-89 | B | Minor optimizations available |
| 70-79 | C | Replace heavy dependencies |
| 60-69 | D | Multiple issues need attention |
| 0-59 | F | Critical bundle size problems |

### Heavy Dependencies Detected

The analyzer identifies these common heavy packages:

| Package | Size | Alternative |
|---------|------|-------------|
| moment | 290KB | date-fns (12KB) or dayjs (2KB) |
| lodash | 71KB | lodash-es with tree-shaking |
| axios | 14KB | Native fetch or ky (3KB) |
| jquery | 87KB | Native DOM APIs |
| @mui/material | Large | shadcn/ui or Radix UI |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Scaffolder fails with "Directory already exists" | Target project folder already present on disk | Delete or rename the existing directory, or choose a different project name |
| Component generator creates PascalCase name from kebab-case incorrectly | Input contains mixed delimiters (e.g., `my_comp-name`) | Use consistent kebab-case (`my-comp-name`) or PascalCase (`MyCompName`) as input |
| Bundle analyzer reports "No valid package.json found" | Script is pointed at a directory without `package.json` or the file has invalid JSON | Pass the correct project root directory; validate `package.json` syntax with `python -m json.tool package.json` |
| A generated file contains `// TODO: Implement <KEY>` | A feature in `manifest.json` names a content key with no template file | Add the template under `assets/templates/scaffold/files/` and map the key in `contents`; the bundled features all have templates |
| Bundle score unexpectedly low despite few dependencies | Dev-only packages (TypeScript, ESLint, Tailwind) are listed under `dependencies` instead of `devDependencies` | Move build/dev tooling to `devDependencies` in `package.json` |
| Import analysis returns zero files checked | Source code is not in `src/`, `app/`, or `pages/` directories | Run with `--verbose` and ensure your source files live in one of the three expected directories |
| Generated component missing `'use client'` directive | Component was generated with `--type server` instead of the default `client` type | Re-run with `--type client` or add the `'use client'` directive manually at the top of the file |

---

## Success Criteria

- **Lighthouse performance score above 90** on the generated project's production build, indicating Server Components and image optimization are configured correctly.
- **Bundle size under 200KB gzipped** for the initial JavaScript payload, validated by running the bundle analyzer with a grade of A or B.
- **Zero heavy-dependency warnings** from `bundle_analyzer.py` after applying all recommended replacements.
- **Component generation time under 2 seconds** per component, including test and story file creation.
- **All generated TypeScript files pass `tsc --noEmit`** without errors, confirming type-safe scaffolding output.
- **Accessibility audit produces zero critical violations** when running axe-core or Lighthouse accessibility checks against generated components.
- **Test coverage above 80%** for generated components when the `--with-test` flag is used and tests are executed with Vitest.

---

## Tool Reference

### frontend_scaffolder.py

- **Purpose**: Scaffold a complete Next.js or React project with TypeScript, Tailwind CSS, and optional feature modules.
- **Usage**: `python scripts/frontend_scaffolder.py <name> [flags]`
- **Flags**:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `name` | positional | (required unless `--list-*`) | Lowercase npm package name (`my-app`); spaces, capitals, slashes and `..` exit 2 |
| `--dir`, `-d` | string | `.` | Output directory where the project folder is created |
| `--template`, `-t` | choice | `nextjs` | Project template: `nextjs` or `react` |
| `--features`, `-f` | string | (none) | Comma-separated features: `auth`, `api`, `forms`, `testing`, `storybook` |
| `--list-templates` | flag | off | List available project templates and exit |
| `--list-features` | flag | off | List available feature modules and exit |
| `--dry-run` | flag | off | Preview generated file list without writing to disk |
| `--format` | choice | `text` | `text` summary or `json` result |
| `--json` | flag | off | Shorthand for `--format json` (kept for existing scripts) |

- **Example**:
  ```bash
  python scripts/frontend_scaffolder.py dashboard --template nextjs --features auth,api --json
  ```
  ```json
  {
    "name": "dashboard",
    "template": "nextjs",
    "template_name": "Next.js 16 App Router",
    "features": ["auth", "api"],
    "path": "./dashboard",
    "files_created": 28,
    "next_steps": ["cd dashboard", "npm install", "npm run dev"]
  }
  ```
- **Output Formats**: Human-readable summary (default) or JSON (`--format json`).
- **Templates**: every generated file body lives in `assets/templates/scaffold/`; `manifest.json` maps project paths, features and config files to those files. Edit a template there, not in the script. Every bundled feature file has a working template; a key with no template would be written as a `// TODO: Implement <KEY>` stub. The result (and the text summary) carries `notes` for anything the scaffold cannot do for you, such as the server side of `auth`.
- **Version pins** (checked on npm, November 2026): TypeScript `~6.0.0` in both templates because typescript-eslint 8.72 accepts `typescript >=4.8.4 <6.1.0` (TypeScript 7 is out but unsupported). Next keeps ESLint `^9` because eslint-config-next 16.4 bundles eslint-plugin-react, -import and -jsx-a11y, whose peer ranges end at ESLint 9; the Vite template's plugins all accept ESLint 10, so it uses `^10`. `@types/node ^24` in both, as in create-vite's react-ts template.

---

### component_generator.py

- **Purpose**: Generate React/Next.js component files with TypeScript, optional test, and Storybook story.
- **Usage**: `python scripts/component_generator.py <name> [flags]`
- **Flags**:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `name` | positional | (required) | Component name in PascalCase or kebab-case |
| `--dir`, `-d` | string | `src/components` | Output directory for generated files |
| `--type`, `-t` | choice | `client` | Component type: `client`, `server`, or `hook` |
| `--with-test` | flag | off | Generate a `.test.tsx` file with Testing Library boilerplate |
| `--with-story` | flag | off | Generate a `.stories.tsx` file for Storybook |
| `--framework` | choice | `next` | Story imports: `next` (`@storybook/nextjs-vite`) or `vite` (`@storybook/react-vite`), matching what the scaffolder installs |
| `--no-index` | flag | off | Skip generating the `index.ts` barrel export file |
| `--force` | flag | off | Overwrite files that already exist; without it the run exits 2 and writes nothing |
| `--flat` | flag | off | Place files directly in output dir without creating a subdirectory |
| `--dry-run` | flag | off | Preview what would be generated without writing files |
| `--format` | choice | `text` | `text` summary or `json` result (also applies to `--dry-run`) |
| `--verbose`, `-v` | flag | off | Enable verbose output |

- **Example**:
  ```bash
  python scripts/component_generator.py ProductCard --dir src/components/ui --type client --with-test --with-story
  ```
  ```
  ==================================================
  Component Generated: ProductCard
  ==================================================
  Type: client
  Directory: src/components/ui/ProductCard

  Files created:
    - src/components/ui/ProductCard/ProductCard.tsx
    - src/components/ui/ProductCard/ProductCard.test.tsx
    - src/components/ui/ProductCard/ProductCard.stories.tsx
    - src/components/ui/ProductCard/index.ts
  ==================================================
  ```
- **Output Formats**: Human-readable summary (default) or JSON (`--format json`). Templates live in `assets/templates/component/*.tmpl`.

---

### bundle_analyzer.py

- **Purpose**: Analyze `package.json` and project source files for bundle size issues, heavy dependencies, and optimization opportunities. The framework (`next`, `vite` or `other`) is detected from dependencies and reported; `next.config` checks and their 10-point deduction apply to Next projects only.
- **Usage**: `python scripts/bundle_analyzer.py [project_dir] [flags]`
- **Flags**:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `project_dir` | positional | `.` | Project directory containing `package.json` |
| `--format` | choice | `text` | `text` report or `json` analysis |
| `--json` | flag | off | Shorthand for `--format json` |
| `--min-score` | int | (none) | Exit 1 when the health score is below this value; without it the run never fails on score |
| `--verbose`, `-v` | flag | off | Include detailed import pattern analysis across `src/`, `app/`, and `pages/` directories |

- **Example**:
  ```bash
  python scripts/bundle_analyzer.py /path/to/my-app --verbose
  ```
  ```
  ============================================================
  FRONTEND BUNDLE ANALYSIS REPORT
  ============================================================

  Bundle Health Score: 70/100 (C)

  Dependencies: 12 production, 18 dev

  --- HEAVY DEPENDENCIES ---

    moment (290KB)
      Reason: Large locale files bundled by default
      Alternative: date-fns (12KB) or dayjs (2KB)

    lodash (71KB)
      Reason: Full library often imported when only few functions needed
      Alternative: lodash-es with tree-shaking or individual imports (lodash/get)

  --- IMPORT ISSUES ---
    - src/utils/date.ts: Consider replacing moment with date-fns or dayjs

  --- RECOMMENDATIONS ---
    1. Replace heavy dependencies with lighter alternatives
  ============================================================
  ```
- **Output Formats**: Human-readable report (default) or JSON (`--format json`). Rule tables (heavy packages, dev-only patterns, import patterns) live in `references/bundle_rules.json`.
