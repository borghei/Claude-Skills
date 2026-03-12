---
name: design-system-lead
description: >
  Expert design systems leadership covering component libraries, design tokens, documentation, and design-development collaboration.
  Use when architecting a design token system, building a component library, defining governance and contribution processes, measuring design system adoption, or generating cross-platform tokens (CSS, SCSS, iOS, Android).
version: 1.0.0
author: borghei
category: product-design
tags: [design-systems, components, tokens, documentation, figma]
---

# Design System Lead

The agent operates as a senior design system lead, delivering scalable component libraries, token architectures, governance processes, and adoption strategies for cross-functional product teams.

## Workflow

1. **Assess maturity** - Evaluate current design system maturity (Emerging, Defined, Managed, or Optimized). Audit existing patterns, inconsistencies, and custom components. Checkpoint: maturity level is documented with evidence.
2. **Define token architecture** - Build a three-tier token structure: primitive (raw values), semantic (purpose-based aliases), and component (scoped to specific UI elements). Checkpoint: every semantic token references a primitive; no hardcoded values remain.
3. **Build component library** - Design and implement components starting with primitives (Button, Input, Icon), then composites (Card, Modal, Dropdown), then patterns (Forms, Navigation, Tables). Checkpoint: each component has variants, sizes, states, props table, and accessibility requirements.
4. **Document everything** - Create usage guidelines, code examples, do/don't rules, and accessibility notes for every component. Checkpoint: documentation covers installation, basic usage, all variants, and at least one accessibility note.
5. **Establish governance** - Define the RFC-to-release contribution process. Set versioning strategy (SemVer). Checkpoint: contribution process is published and reviewed by both design and engineering leads.
6. **Measure adoption** - Track coverage (% of products using DS), consistency (token compliance rate), efficiency (time to build), and quality (a11y score, bug reports). Checkpoint: adoption dashboard is updated monthly.

## Design System Maturity Model

| Level | Characteristics | Focus |
|-------|-----------------|-------|
| 1: Emerging | Ad-hoc styles, no standards | Establish foundations |
| 2: Defined | Documented guidelines | Component library |
| 3: Managed | Shared component library | Adoption, governance |
| 4: Optimized | Automated, measured | Continuous improvement |

## Token Architecture

Three-tier token system (primitive -> semantic -> component):

```json
{
  "color": {
    "primitive": {
      "blue": {
        "50": {"value": "#eff6ff"},
        "500": {"value": "#3b82f6"},
        "600": {"value": "#2563eb"},
        "900": {"value": "#1e3a8a"}
      }
    },
    "semantic": {
      "primary": {"value": "{color.primitive.blue.600}"},
      "primary-hover": {"value": "{color.primitive.blue.700}"},
      "background": {"value": "{color.primitive.gray.50}"},
      "text": {"value": "{color.primitive.gray.900}"}
    },
    "component": {
      "button-primary-bg": {"value": "{color.semantic.primary}"},
      "button-primary-text": {"value": "#ffffff"}
    }
  },
  "spacing": {
    "primitive": {"1": {"value": "4px"}, "2": {"value": "8px"}, "4": {"value": "16px"}, "8": {"value": "32px"}},
    "semantic": {"component-padding": {"value": "{spacing.primitive.4}"}, "section-gap": {"value": "{spacing.primitive.8}"}}
  },
  "typography": {
    "fontFamily": {"sans": {"value": "Inter, system-ui, sans-serif"}, "mono": {"value": "JetBrains Mono, monospace"}},
    "fontSize": {"sm": {"value": "14px"}, "base": {"value": "16px"}, "lg": {"value": "18px"}, "xl": {"value": "20px"}}
  }
}
```

## Example: Cross-Platform Token Generation

```javascript
// style-dictionary.config.js
module.exports = {
  source: ['tokens/**/*.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'dist/css/',
      files: [{ destination: 'variables.css', format: 'css/variables' }]
    },
    scss: {
      transformGroup: 'scss',
      buildPath: 'dist/scss/',
      files: [{ destination: '_variables.scss', format: 'scss/variables' }]
    },
    ios: {
      transformGroup: 'ios',
      buildPath: 'dist/ios/',
      files: [{ destination: 'StyleDictionaryColor.swift', format: 'ios-swift/class.swift' }]
    },
    android: {
      transformGroup: 'android',
      buildPath: 'dist/android/',
      files: [{ destination: 'colors.xml', format: 'android/colors' }]
    }
  }
};
```

## Component Library Structure

```
design-system/
+-- foundations/     (colors, typography, spacing, elevation, motion, grid)
+-- components/
|   +-- primitives/  (Button, Input, Icon)
|   +-- composites/  (Card, Modal, Dropdown)
|   +-- patterns/    (Forms, Navigation, Tables)
+-- layouts/         (page templates, content layouts)
+-- documentation/   (getting-started, design guidelines, code guidelines)
+-- assets/          (icons, illustrations, logos)
```

### Component Specification: Button

```markdown
## Variants
- Primary: main action
- Secondary: supporting action
- Tertiary: low-emphasis action
- Destructive: dangerous/irreversible action

## Sizes
- Small: 32px height, 8px/12px padding
- Medium: 40px height (default), 10px/16px padding
- Large: 48px height, 12px/24px padding

## States
Default -> Hover -> Active -> Focus -> Disabled -> Loading

## Props
| Prop      | Type        | Default   | Description      |
|-----------|-------------|-----------|------------------|
| variant   | string      | 'primary' | Visual style     |
| size      | string      | 'medium'  | Button size      |
| disabled  | boolean     | false     | Disabled state   |
| loading   | boolean     | false     | Loading state    |
| leftIcon  | ReactNode   | -         | Leading icon     |
| onClick   | function    | -         | Click handler    |

## Accessibility
- Minimum touch target: 44x44px
- Visible focus ring on keyboard navigation
- aria-label required for icon-only buttons
- aria-busy="true" when loading
```

### Example: Button Implementation (React + CVA)

```typescript
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  }
);
```

## Governance: Contribution Process

```
1. REQUEST  - Create RFC describing problem and proposed component/change
2. REVIEW   - Design review + engineering review + accessibility review
3. BUILD    - Figma component + code implementation + unit tests + visual regression
4. DOCUMENT - API docs + usage guidelines + Storybook stories
5. RELEASE  - SemVer bump + changelog + announcement
```

### Versioning Strategy

| Change Type | Version Bump | Examples |
|-------------|-------------|---------|
| Breaking | MAJOR | Component API change, token rename |
| New feature | MINOR | New component, new variant, new token |
| Bug fix | PATCH | Style fix, docs update, perf improvement |

## Adoption Metrics Dashboard

```
Design System Health
  Adoption: 82% (12/15 products)
  Component Usage: 78% (45 components)
  Token Compliance: 95%
  Overrides: 23 (down from 38)

  Efficiency
  Avg time to build new feature: 3.2 days (was 5.1)
  Custom components created this quarter: 4 (was 12)
```

## Scripts

```bash
# Token generator
python scripts/token_gen.py --source tokens.json --output dist/

# Component scaffolder
python scripts/component_scaffold.py --name DatePicker --category composite

# Adoption analyzer
python scripts/adoption_analyzer.py --repos repos.yaml

# Visual regression test
python scripts/visual_regression.py --baseline main --compare feature/new-button
```

## Reference Materials

- `references/token_architecture.md` - Token system design
- `references/component_patterns.md` - Component best practices
- `references/governance.md` - Contribution guidelines
- `references/figma_setup.md` - Figma library management
