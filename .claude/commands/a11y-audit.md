---
description: Run an accessibility audit on the current project for WCAG compliance.
---

Perform a comprehensive WCAG 2.1 accessibility audit:

1. **Scan source files** — find all HTML, JSX, TSX, Vue, and Svelte files in the project.
2. **Check each file for violations:**
   - Missing `alt` attributes on images
   - Missing `aria-label` or `aria-labelledby` on interactive elements
   - Heading hierarchy violations (skipped levels, e.g. h1 → h3)
   - Form inputs without associated `<label>` or `aria-label`
   - Missing `lang` attribute on `<html>`
   - Empty links or buttons (no text content or aria-label)
   - Missing skip-navigation links
   - Color contrast issues (check inline styles for contrast ratios < 4.5:1)
   - Keyboard navigation: `tabindex` > 0 (anti-pattern), missing focus indicators
   - ARIA role misuse (e.g., `role="button"` without keyboard handler)
3. **Classify findings** by severity:
   - **Critical**: blocks assistive technology users entirely
   - **Serious**: significantly impairs usability
   - **Moderate**: creates friction but has workarounds
   - **Minor**: best practice violation
4. **Output a report** with: file path, line number, violation, severity, and suggested fix.
5. **Summarize** total violations by severity and recommend top 5 highest-impact fixes.
