---
name: design-system-lead
description: Expert design systems leadership covering component libraries, design tokens, documentation, and design-development collaboration.
version: 1.0.0
author: Claude Skills
category: product-design
tags: [design-systems, components, tokens, documentation, figma]
---

# Design System Lead

Expert-level design systems for scalable product design.

## Core Competencies

- Design system architecture
- Component library design
- Design token management
- Documentation strategy
- Design-dev collaboration
- Governance and contribution
- Adoption and training
- Tooling and automation

## Design System Architecture

### System Structure

```
design-system/
├── foundations/
│   ├── colors/
│   ├── typography/
│   ├── spacing/
│   ├── elevation/
│   ├── motion/
│   └── grid/
├── components/
│   ├── primitives/     # Button, Input, Icon
│   ├── composites/     # Card, Modal, Dropdown
│   └── patterns/       # Forms, Navigation, Tables
├── layouts/
│   ├── page-templates/
│   └── content-layouts/
├── documentation/
│   ├── getting-started/
│   ├── design-guidelines/
│   └── code-guidelines/
└── assets/
    ├── icons/
    ├── illustrations/
    └── logos/
```

### Maturity Levels

| Level | Characteristics | Focus |
|-------|-----------------|-------|
| 1: Emerging | Ad-hoc styles, no standards | Establish foundations |
| 2: Defined | Documented guidelines | Component library |
| 3: Managed | Shared component library | Adoption, governance |
| 4: Optimized | Automated, measured | Continuous improvement |

## Design Tokens

### Token Structure

```json
{
  "color": {
    "primitive": {
      "blue": {
        "50": {"value": "#eff6ff"},
        "100": {"value": "#dbeafe"},
        "500": {"value": "#3b82f6"},
        "600": {"value": "#2563eb"},
        "900": {"value": "#1e3a8a"}
      }
    },
    "semantic": {
      "primary": {"value": "{color.primitive.blue.600}"},
      "primary-hover": {"value": "{color.primitive.blue.700}"},
      "background": {"value": "{color.primitive.gray.50}"},
      "text": {"value": "{color.primitive.gray.900}"},
      "text-secondary": {"value": "{color.primitive.gray.600}"}
    },
    "component": {
      "button": {
        "primary": {
          "background": {"value": "{color.semantic.primary}"},
          "text": {"value": "#ffffff"}
        }
      }
    }
  },
  "spacing": {
    "primitive": {
      "1": {"value": "4px"},
      "2": {"value": "8px"},
      "3": {"value": "12px"},
      "4": {"value": "16px"},
      "6": {"value": "24px"},
      "8": {"value": "32px"}
    },
    "semantic": {
      "component-padding": {"value": "{spacing.primitive.4}"},
      "section-gap": {"value": "{spacing.primitive.8}"}
    }
  },
  "typography": {
    "fontFamily": {
      "sans": {"value": "Inter, system-ui, sans-serif"},
      "mono": {"value": "JetBrains Mono, monospace"}
    },
    "fontSize": {
      "xs": {"value": "12px"},
      "sm": {"value": "14px"},
      "base": {"value": "16px"},
      "lg": {"value": "18px"},
      "xl": {"value": "20px"},
      "2xl": {"value": "24px"}
    },
    "lineHeight": {
      "tight": {"value": "1.25"},
      "normal": {"value": "1.5"},
      "relaxed": {"value": "1.75"}
    }
  },
  "borderRadius": {
    "none": {"value": "0"},
    "sm": {"value": "4px"},
    "md": {"value": "8px"},
    "lg": {"value": "12px"},
    "full": {"value": "9999px"}
  },
  "shadow": {
    "sm": {"value": "0 1px 2px 0 rgb(0 0 0 / 0.05)"},
    "md": {"value": "0 4px 6px -1px rgb(0 0 0 / 0.1)"},
    "lg": {"value": "0 10px 15px -3px rgb(0 0 0 / 0.1)"}
  }
}
```

### Token Generation

```javascript
// style-dictionary.config.js
module.exports = {
  source: ['tokens/**/*.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'dist/css/',
      files: [{
        destination: 'variables.css',
        format: 'css/variables'
      }]
    },
    scss: {
      transformGroup: 'scss',
      buildPath: 'dist/scss/',
      files: [{
        destination: '_variables.scss',
        format: 'scss/variables'
      }]
    },
    js: {
      transformGroup: 'js',
      buildPath: 'dist/js/',
      files: [{
        destination: 'tokens.js',
        format: 'javascript/es6'
      }]
    },
    ios: {
      transformGroup: 'ios',
      buildPath: 'dist/ios/',
      files: [{
        destination: 'StyleDictionaryColor.swift',
        format: 'ios-swift/class.swift',
        className: 'StyleDictionaryColor'
      }]
    },
    android: {
      transformGroup: 'android',
      buildPath: 'dist/android/',
      files: [{
        destination: 'colors.xml',
        format: 'android/colors'
      }]
    }
  }
};
```

## Component Library

### Component Anatomy

```markdown
# Button Component

## Anatomy
┌─────────────────────────────┐
│  [Icon]  Label  [Icon]      │
└─────────────────────────────┘
   └──┬──┘  └─┬─┘  └──┬──┘
   Leading  Label  Trailing
    Icon           Icon

## Variants
- Primary: Main action
- Secondary: Supporting action
- Tertiary: Low-emphasis action
- Destructive: Dangerous action

## Sizes
- Small: 32px height
- Medium: 40px height (default)
- Large: 48px height

## States
- Default
- Hover
- Active/Pressed
- Focus
- Disabled
- Loading

## Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | string | 'primary' | Visual style |
| size | string | 'medium' | Button size |
| disabled | boolean | false | Disabled state |
| loading | boolean | false | Loading state |
| leftIcon | ReactNode | - | Leading icon |
| rightIcon | ReactNode | - | Trailing icon |
| onClick | function | - | Click handler |
```

### Component Template

```typescript
// Button.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';

const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        outline: 'border border-input bg-background hover:bg-accent',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
      },
      size: {
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, leftIcon, rightIcon, children, ...props }, ref) => {
    return (
      <button
        className={buttonVariants({ variant, size, className })}
        ref={ref}
        disabled={loading || props.disabled}
        {...props}
      >
        {loading ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : leftIcon ? (
          <span className="mr-2">{leftIcon}</span>
        ) : null}
        {children}
        {rightIcon && !loading && <span className="ml-2">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

## Documentation

### Component Documentation Template

```markdown
# [Component Name]

[Brief description of what the component does and when to use it.]

## Installation

\`\`\`bash
npm install @design-system/components
\`\`\`

## Usage

\`\`\`tsx
import { ComponentName } from '@design-system/components';

function Example() {
  return <ComponentName variant="primary">Label</ComponentName>;
}
\`\`\`

## Examples

### Basic
[Code example with preview]

### With Icons
[Code example with preview]

### Sizes
[Code example with preview]

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| prop1 | type | default | description |

## Accessibility

- [ARIA attributes used]
- [Keyboard interactions]
- [Screen reader considerations]

## Design Guidelines

### Do
- [Best practice 1]
- [Best practice 2]

### Don't
- [Anti-pattern 1]
- [Anti-pattern 2]

## Related Components

- [Related component 1]
- [Related component 2]
```

### Documentation Site Structure

```
docs/
├── getting-started/
│   ├── installation.md
│   ├── usage.md
│   └── contributing.md
├── foundations/
│   ├── colors.md
│   ├── typography.md
│   ├── spacing.md
│   └── icons.md
├── components/
│   ├── button.md
│   ├── input.md
│   ├── select.md
│   └── ...
├── patterns/
│   ├── forms.md
│   ├── navigation.md
│   └── tables.md
└── resources/
    ├── figma.md
    ├── changelog.md
    └── migration.md
```

## Governance

### Contribution Process

```
REQUEST → REVIEW → BUILD → DOCUMENT → RELEASE

1. REQUEST
   - Create RFC (Request for Comments)
   - Describe problem and proposed solution
   - Gather feedback

2. REVIEW
   - Design review (Design System team)
   - Technical review (Engineering)
   - Accessibility review

3. BUILD
   - Figma component
   - Code implementation
   - Unit tests
   - Visual regression tests

4. DOCUMENT
   - API documentation
   - Usage guidelines
   - Storybook stories

5. RELEASE
   - Version bump
   - Changelog update
   - Announcement
```

### Version Strategy

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes
- Component API changes
- Token renaming
- Behavior changes

MINOR: New features
- New components
- New variants
- New tokens

PATCH: Bug fixes
- Style fixes
- Documentation updates
- Performance improvements
```

### Decision Log

| Date | Decision | Rationale | Status |
|------|----------|-----------|--------|
| [Date] | [Decision] | [Why] | Implemented |

## Metrics

### Adoption Metrics

```
COVERAGE
- % of products using design system
- % of components from design system

CONSISTENCY
- Design drift score
- Token compliance rate

EFFICIENCY
- Time to build new features
- Number of custom components

QUALITY
- Accessibility score
- Bug reports on components
```

### Health Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                 Design System Health                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Adoption          Component Usage      Token Compliance     │
│  ████████░░ 82%   ████████░░ 78%       ██████████ 95%       │
│                                                              │
│  Products: 12/15   Components: 45       Overrides: 23        │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Recent Activity                                             │
│  • Button v2.1.0 released (2 days ago)                      │
│  • Modal accessibility fix (1 week ago)                      │
│  • New DatePicker component (2 weeks ago)                    │
└─────────────────────────────────────────────────────────────┘
```

## Reference Materials

- `references/token_architecture.md` - Token system design
- `references/component_patterns.md` - Component best practices
- `references/governance.md` - Contribution guidelines
- `references/figma_setup.md` - Figma library management

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
