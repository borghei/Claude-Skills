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
| `--features auth` | Add NextAuth.js authentication |
| `--features api` | Add React Query + API client |
| `--features forms` | Add React Hook Form + Zod validation |
| `--features testing` | Add Vitest + Testing Library |
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
| `--dry-run` shows files but `--features` content is listed as TODO | Feature file content keys are not mapped in `FILE_CONTENTS` dictionary | This is expected for some add-on features; implement the placeholder files manually after scaffolding |
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
| `name` | positional | (required) | Project name, kebab-case recommended |
| `--dir`, `-d` | string | `.` | Output directory where the project folder is created |
| `--template`, `-t` | choice | `nextjs` | Project template: `nextjs` or `react` |
| `--features`, `-f` | string | (none) | Comma-separated features: `auth`, `api`, `forms`, `testing`, `storybook` |
| `--list-templates` | flag | off | List available project templates and exit |
| `--list-features` | flag | off | List available feature modules and exit |
| `--dry-run` | flag | off | Preview generated file list without writing to disk |
| `--json` | flag | off | Output result as JSON instead of human-readable summary |

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
- **Output Formats**: Human-readable summary (default) or JSON (`--json`).

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
| `--no-index` | flag | off | Skip generating the `index.ts` barrel export file |
| `--flat` | flag | off | Place files directly in output dir without creating a subdirectory |
| `--dry-run` | flag | off | Preview what would be generated without writing files |
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
- **Output Formats**: Human-readable summary only.

---

### bundle_analyzer.py

- **Purpose**: Analyze `package.json` and project source files for bundle size issues, heavy dependencies, and optimization opportunities.
- **Usage**: `python scripts/bundle_analyzer.py [project_dir] [flags]`
- **Flags**:

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `project_dir` | positional | `.` | Project directory containing `package.json` |
| `--json` | flag | off | Output full analysis as JSON |
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
- **Output Formats**: Human-readable report (default) or JSON (`--json`).
