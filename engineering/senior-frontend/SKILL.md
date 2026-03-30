---
name: senior-frontend
description: >
  Frontend development skill for React, Next.js, TypeScript, and Tailwind CSS
  applications. Use when building React components, optimizing Next.js
  performance, analyzing bundle sizes, scaffolding frontend projects,
  implementing accessibility, or reviewing frontend code quality.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: frontend
  updated: 2026-03-31
  tags: [react, typescript, accessibility, performance, state-management]
---
# Senior Frontend

Frontend development patterns, performance optimization, and automation tools for React/Next.js applications.

## Table of Contents

- [Project Scaffolding](#project-scaffolding)
- [Component Generation](#component-generation)
- [Bundle Analysis](#bundle-analysis)
- [React Patterns](#react-patterns)
- [Next.js Optimization](#nextjs-optimization)
- [Accessibility and Testing](#accessibility-and-testing)

---

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
| `--template nextjs` | Next.js 14+ with App Router and Server Components |
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

## React Patterns

Reference: `references/react_patterns.md`

### Compound Components

Share state between related components:

```tsx
const Tabs = ({ children }) => {
  const [active, setActive] = useState(0);
  return (
    <TabsContext.Provider value={{ active, setActive }}>
      {children}
    </TabsContext.Provider>
  );
};

Tabs.List = TabList;
Tabs.Panel = TabPanel;

// Usage
<Tabs>
  <Tabs.List>
    <Tabs.Tab>One</Tabs.Tab>
    <Tabs.Tab>Two</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel>Content 1</Tabs.Panel>
  <Tabs.Panel>Content 2</Tabs.Panel>
</Tabs>
```

### Custom Hooks

Extract reusable logic:

```tsx
function useDebounce<T>(value: T, delay = 500): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Usage
const debouncedSearch = useDebounce(searchTerm, 300);
```

### Render Props

Share rendering logic:

```tsx
function DataFetcher({ url, render }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(url).then(r => r.json()).then(setData).finally(() => setLoading(false));
  }, [url]);

  return render({ data, loading });
}

// Usage
<DataFetcher
  url="/api/users"
  render={({ data, loading }) =>
    loading ? <Spinner /> : <UserList users={data} />
  }
/>
```

---

## Next.js Optimization

Reference: `references/nextjs_optimization_guide.md`

### Server vs Client Components

Use Server Components by default. Add 'use client' only when you need:
- Event handlers (onClick, onChange)
- State (useState, useReducer)
- Effects (useEffect)
- Browser APIs

```tsx
// Server Component (default) - no 'use client'
async function ProductPage({ params }) {
  const product = await getProduct(params.id);  // Server-side fetch

  return (
    <div>
      <h1>{product.name}</h1>
      <AddToCartButton productId={product.id} />  {/* Client component */}
    </div>
  );
}

// Client Component
'use client';
function AddToCartButton({ productId }) {
  const [adding, setAdding] = useState(false);
  return <button onClick={() => addToCart(productId)}>Add</button>;
}
```

### Image Optimization

```tsx
import Image from 'next/image';

// Above the fold - load immediately
<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority
/>

// Responsive image with fill
<div className="relative aspect-video">
  <Image
    src="/product.jpg"
    alt="Product"
    fill
    sizes="(max-width: 768px) 100vw, 50vw"
    className="object-cover"
  />
</div>
```

### Data Fetching Patterns

```tsx
// Parallel fetching
async function Dashboard() {
  const [user, stats] = await Promise.all([
    getUser(),
    getStats()
  ]);
  return <div>...</div>;
}

// Streaming with Suspense
async function ProductPage({ params }) {
  return (
    <div>
      <ProductDetails id={params.id} />
      <Suspense fallback={<ReviewsSkeleton />}>
        <Reviews productId={params.id} />
      </Suspense>
    </div>
  );
}
```

---

## Accessibility and Testing

Reference: `references/frontend_best_practices.md`

### Accessibility Checklist

1. **Semantic HTML**: Use proper elements (`<button>`, `<nav>`, `<main>`)
2. **Keyboard Navigation**: All interactive elements focusable
3. **ARIA Labels**: Provide labels for icons and complex widgets
4. **Color Contrast**: Minimum 4.5:1 for normal text
5. **Focus Indicators**: Visible focus states

```tsx
// Accessible button
<button
  type="button"
  aria-label="Close dialog"
  onClick={onClose}
  className="focus-visible:ring-2 focus-visible:ring-blue-500"
>
  <XIcon aria-hidden="true" />
</button>

// Skip link for keyboard users
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>
```

### Testing Strategy

```tsx
// Component test with React Testing Library
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('button triggers action on click', async () => {
  const onClick = vi.fn();
  render(<Button onClick={onClick}>Click me</Button>);

  await userEvent.click(screen.getByRole('button'));
  expect(onClick).toHaveBeenCalledTimes(1);
});

// Test accessibility
test('dialog is accessible', async () => {
  render(<Dialog open={true} title="Confirm" />);

  expect(screen.getByRole('dialog')).toBeInTheDocument();
  expect(screen.getByRole('dialog')).toHaveAttribute('aria-labelledby');
});
```

---

## Quick Reference

### Common Next.js Config

```js
// next.config.js
const nextConfig = {
  images: {
    remotePatterns: [{ hostname: 'cdn.example.com' }],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizePackageImports: ['lucide-react', '@heroicons/react'],
  },
};
```

### Tailwind CSS Utilities

```tsx
// Conditional classes with cn()
import { cn } from '@/lib/utils';

<button className={cn(
  'px-4 py-2 rounded',
  variant === 'primary' && 'bg-blue-500 text-white',
  disabled && 'opacity-50 cursor-not-allowed'
)} />
```

### TypeScript Patterns

```tsx
// Props with children
interface CardProps {
  className?: string;
  children: React.ReactNode;
}

// Generic component
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map(renderItem)}</ul>;
}
```

---

## Resources

- React Patterns: `references/react_patterns.md`
- Next.js Optimization: `references/nextjs_optimization_guide.md`
- Best Practices: `references/frontend_best_practices.md`

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

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **senior-fullstack** | Scaffolded frontend projects connect to fullstack project scaffolder for API layer setup | Frontend project structure feeds into `project_scaffolder.py` which adds backend, Docker, and CI/CD layers |
| **senior-backend** | Components consuming API data follow patterns defined by backend skill's REST/GraphQL conventions | Backend API response types imported into frontend `types/` directory generated by this skill |
| **senior-qa** | Generated test files (`--with-test`) use the same Testing Library conventions that the QA skill's test strategies build upon | Component test files hand off to QA skill for integration and E2E test coverage expansion |
| **senior-devops** | Bundle analyzer output informs build pipeline optimization decisions | Bundle health score and dependency warnings feed into CI quality gates configured by DevOps skill |
| **senior-secops** | Dependency analysis identifies packages that need security audit | Heavy/outdated dependency warnings from `bundle_analyzer.py` trigger security review workflows |
| **code-reviewer** | Generated components follow patterns that the code reviewer skill validates | Code reviewer checks generated components against React/TypeScript best practices defined in this skill's references |

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
    "template_name": "Next.js 14+ App Router",
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
