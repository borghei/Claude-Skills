# WCAG 2.1 Guidelines Reference

## Conformance Levels

### Level A (Minimum)
Must-fix issues. Failure means content is inaccessible to some users.

| Criterion | Title | Key Requirement |
|-----------|-------|-----------------|
| 1.1.1 | Non-text Content | All images have alt text |
| 1.2.1 | Audio-only / Video-only | Provide alternatives |
| 1.3.1 | Info and Relationships | Use semantic HTML (headings, lists, tables) |
| 1.3.2 | Meaningful Sequence | Reading order matches visual order |
| 1.3.3 | Sensory Characteristics | Don't rely on shape/color alone for instructions |
| 1.4.1 | Use of Color | Color is not the only means of conveying info |
| 1.4.2 | Audio Control | Auto-playing audio can be paused/stopped |
| 2.1.1 | Keyboard | All functionality keyboard accessible |
| 2.1.2 | No Keyboard Trap | Users can tab away from all components |
| 2.4.1 | Bypass Blocks | Provide skip navigation |
| 2.4.2 | Page Titled | Pages have descriptive titles |
| 2.4.3 | Focus Order | Focus order is logical |
| 2.4.4 | Link Purpose | Link text is descriptive |
| 3.1.1 | Language of Page | html lang attribute set |
| 3.3.1 | Error Identification | Errors are clearly described |
| 3.3.2 | Labels or Instructions | Form inputs have labels |
| 4.1.1 | Parsing | Valid HTML |
| 4.1.2 | Name, Role, Value | Custom widgets have proper ARIA |

### Level AA (Standard)
Industry standard. Required by most accessibility regulations.

| Criterion | Title | Key Requirement |
|-----------|-------|-----------------|
| 1.4.3 | Contrast (Minimum) | 4.5:1 for normal text, 3:1 for large |
| 1.4.4 | Resize Text | Text resizable to 200% without loss |
| 1.4.5 | Images of Text | Use real text instead of images |
| 1.4.11 | Non-text Contrast | 3:1 for UI components |
| 2.4.5 | Multiple Ways | More than one way to reach pages |
| 2.4.6 | Headings and Labels | Descriptive headings and labels |
| 2.4.7 | Focus Visible | Keyboard focus indicator visible |
| 3.1.2 | Language of Parts | Identify language changes |
| 3.2.3 | Consistent Navigation | Navigation consistent across pages |
| 3.3.3 | Error Suggestion | Suggest corrections for errors |

### Level AAA (Enhanced)
Best practice target. Not typically required by regulation.

| Criterion | Title | Key Requirement |
|-----------|-------|-----------------|
| 1.4.6 | Contrast (Enhanced) | 7:1 for normal text, 4.5:1 for large |
| 2.4.9 | Link Purpose (Link Only) | Link text alone is descriptive |
| 2.4.10 | Section Headings | Content organized with headings |

## Contrast Requirements

### Relative Luminance Formula
```
L = 0.2126 * R + 0.7152 * G + 0.0722 * B

where R, G, B are linearized:
  if sRGB <= 0.04045: linear = sRGB / 12.92
  else: linear = ((sRGB + 0.055) / 1.055) ^ 2.4

Contrast Ratio = (L1 + 0.05) / (L2 + 0.05)
  where L1 is lighter, L2 is darker
```

### Thresholds
| Context | AA | AAA |
|---------|-----|-----|
| Normal text (< 18pt) | 4.5:1 | 7:1 |
| Large text (>= 18pt, or >= 14pt bold) | 3:1 | 4.5:1 |
| UI components and graphical objects | 3:1 | 3:1 |

## Common Fixes

### Images
```html
<!-- Informative image -->
<img src="chart.png" alt="Sales increased 25% from Q1 to Q2">

<!-- Decorative image -->
<img src="divider.png" alt="" role="presentation">

<!-- Complex image -->
<img src="diagram.png" alt="Network architecture" aria-describedby="diagram-desc">
<div id="diagram-desc">Detailed description of the network architecture...</div>
```

### Forms
```html
<!-- Explicit label -->
<label for="email">Email address</label>
<input type="email" id="email" name="email">

<!-- Implicit label -->
<label>
  Phone number
  <input type="tel" name="phone">
</label>

<!-- ARIA label (when visual label not possible) -->
<input type="search" aria-label="Search products">
```

### Headings
```html
<!-- Correct hierarchy -->
<h1>Page Title</h1>
  <h2>Section</h2>
    <h3>Subsection</h3>
  <h2>Another Section</h2>

<!-- Wrong: skips h2 -->
<h1>Page Title</h1>
  <h3>Subsection</h3>  <!-- Should be h2 -->
```

### Navigation
```html
<!-- Skip link -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<!-- Landmarks -->
<header role="banner">...</header>
<nav aria-label="Main navigation">...</nav>
<main id="main-content">...</main>
<footer role="contentinfo">...</footer>
```

## Testing Checklist

1. Tab through entire page - all interactive elements reachable?
2. Can you complete all tasks with keyboard only?
3. Do all images have appropriate alt text?
4. Are heading levels sequential?
5. Do all form fields have labels?
6. Is color contrast sufficient?
7. Does the page work at 200% zoom?
8. Is the page title descriptive?
9. Do links make sense out of context?
10. Are error messages clear and helpful?
