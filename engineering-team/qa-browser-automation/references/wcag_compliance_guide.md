# WCAG 2.1 Compliance Guide

Quick reference for Web Content Accessibility Guidelines 2.1 conformance levels, common violations, and testing techniques.

---

## Level A Requirements (Must Have)

These are the minimum accessibility requirements. Failure to meet Level A means the site has critical barriers for users with disabilities.

### Perceivable

| Criterion | Requirement | Common Violation |
|-----------|-------------|-----------------|
| 1.1.1 Non-text Content | All images, icons, and media have text alternatives | `<img>` without `alt` attribute |
| 1.2.1 Audio/Video (Prerecorded) | Provide alternatives for time-based media | Video without transcript |
| 1.2.2 Captions (Prerecorded) | Synchronized captions for video content | Missing `<track kind="captions">` |
| 1.2.3 Audio Description | Audio description or text alternative for video | No description of visual-only content |
| 1.3.1 Info and Relationships | Structure conveyed through markup, not just visually | Using `<b>` instead of `<strong>`, missing `<label>` |
| 1.3.2 Meaningful Sequence | Reading order matches visual order | CSS reordering breaks logical flow |
| 1.3.3 Sensory Characteristics | Instructions don't rely solely on shape, size, or location | "Click the round button on the left" |
| 1.4.1 Use of Color | Color is not the only means of conveying information | Red text for errors with no icon or text label |
| 1.4.2 Audio Control | Auto-playing audio can be paused or stopped | Background music with no controls |

### Operable

| Criterion | Requirement | Common Violation |
|-----------|-------------|-----------------|
| 2.1.1 Keyboard | All functionality available via keyboard | Custom dropdown only works with mouse |
| 2.1.2 No Keyboard Trap | Users can navigate away from all components | Modal with no keyboard escape |
| 2.2.1 Timing Adjustable | Users can extend time limits | Session timeout with no warning |
| 2.2.2 Pause, Stop, Hide | Moving content can be paused | Auto-scrolling carousel with no pause |
| 2.3.1 Three Flashes | No content flashes more than 3 times per second | Animated banner exceeds flash threshold |
| 2.4.1 Bypass Blocks | Skip navigation mechanism available | No "skip to content" link |
| 2.4.2 Page Titled | Pages have descriptive titles | Generic `<title>Untitled</title>` |
| 2.4.3 Focus Order | Focus order matches logical reading order | `tabindex` values disrupt natural order |
| 2.4.4 Link Purpose | Link purpose determinable from text or context | "Click here" as link text |

### Understandable

| Criterion | Requirement | Common Violation |
|-----------|-------------|-----------------|
| 3.1.1 Language of Page | `lang` attribute on `<html>` | Missing `<html lang="en">` |
| 3.2.1 On Focus | No unexpected context change on focus | Page navigates when element receives focus |
| 3.2.2 On Input | No unexpected context change on input | Form submits on dropdown change |
| 3.3.1 Error Identification | Errors are identified and described | Form shows red border but no text |
| 3.3.2 Labels or Instructions | Inputs have labels or instructions | Placeholder-only inputs |

### Robust

| Criterion | Requirement | Common Violation |
|-----------|-------------|-----------------|
| 4.1.1 Parsing | Valid HTML with unique IDs | Duplicate `id` attributes |
| 4.1.2 Name, Role, Value | Custom components expose name, role, value | Custom checkbox without ARIA attributes |

---

## Level AA Requirements (Should Have)

Level AA is the standard target for most organizations and is required by many accessibility laws (ADA, Section 508, EN 301 549).

| Criterion | Requirement | Common Violation |
|-----------|-------------|-----------------|
| 1.3.4 Orientation | Content not restricted to single display orientation | Landscape-only app |
| 1.3.5 Identify Input Purpose | Input purpose identifiable via `autocomplete` | Missing `autocomplete="email"` on email fields |
| 1.4.3 Contrast (Minimum) | 4.5:1 ratio for normal text, 3:1 for large text (18pt+) | Light gray text on white background |
| 1.4.4 Resize Text | Text resizable to 200% without loss of function | Fixed-size containers clip enlarged text |
| 1.4.5 Images of Text | Use real text instead of images of text | Logo text as image without alt |
| 1.4.10 Reflow | Content reflows at 320px width without horizontal scroll | Fixed-width layouts |
| 1.4.11 Non-text Contrast | 3:1 ratio for UI components and graphics | Low-contrast form borders |
| 1.4.12 Text Spacing | Content usable with increased text spacing | Overflow hidden clips spaced text |
| 1.4.13 Content on Hover/Focus | Hover/focus content dismissible and persistent | Tooltip disappears when hovering over it |
| 2.4.5 Multiple Ways | Multiple ways to find pages (search, sitemap, nav) | Single navigation method only |
| 2.4.6 Headings and Labels | Headings and labels describe topic or purpose | Vague headings like "Section 1" |
| 2.4.7 Focus Visible | Keyboard focus indicator is visible | `outline: none` with no replacement |
| 3.1.2 Language of Parts | Language changes marked in HTML | French quote in English page without `lang="fr"` |
| 3.2.3 Consistent Navigation | Navigation consistent across pages | Nav items reorder between pages |
| 3.2.4 Consistent Identification | Same function has same label everywhere | "Search" on one page, "Find" on another |
| 3.3.3 Error Suggestion | Error messages suggest corrections | "Invalid input" with no hint |
| 3.3.4 Error Prevention (Legal) | Reversible/confirmable for legal/financial | One-click purchase with no confirmation |
| 4.1.3 Status Messages | Status messages announced to assistive tech | Toast notification not in ARIA live region |

---

## Level AAA Requirements (Nice to Have)

Level AAA conformance is aspirational. Full AAA compliance is not typically feasible for entire sites, but individual criteria can be targeted.

| Criterion | Requirement |
|-----------|-------------|
| 1.2.6 Sign Language | Sign language interpretation for audio |
| 1.2.7 Extended Audio Description | Extended audio description for video |
| 1.2.8 Media Alternative | Full text alternative for synchronized media |
| 1.2.9 Audio-only (Live) | Alternative for live audio |
| 1.4.6 Contrast (Enhanced) | 7:1 ratio for normal text, 4.5:1 for large text |
| 1.4.7 Low or No Background Audio | Speech audio has minimal background noise |
| 1.4.8 Visual Presentation | Customizable text presentation (width, spacing, alignment) |
| 1.4.9 Images of Text (No Exception) | Images of text only for pure decoration |
| 2.1.3 Keyboard (No Exception) | All functionality keyboard-operable, no exceptions |
| 2.2.3 No Timing | No time limits at all |
| 2.2.4 Interruptions | User can postpone/suppress interruptions |
| 2.2.5 Re-authenticating | Data preserved after re-authentication |
| 2.3.2 Three Flashes | No content flashes at all |
| 2.4.8 Location | Breadcrumb or indication of location within site |
| 2.4.9 Link Purpose (Link Only) | Link purpose determinable from link text alone |
| 2.4.10 Section Headings | Content organized with headings |
| 3.1.3-3.1.6 | Unusual words, abbreviations, pronunciation, reading level |
| 3.2.5 Change on Request | Context changes only on user request |
| 3.3.5 Help | Context-sensitive help available |
| 3.3.6 Error Prevention (All) | Reversible/confirmable for all user input |

---

## Common Violations and Quick Fixes

### Missing Alt Text
```html
<!-- Violation -->
<img src="hero.jpg">

<!-- Fix: descriptive alt -->
<img src="hero.jpg" alt="Team collaborating around a whiteboard">

<!-- Fix: decorative image -->
<img src="divider.png" alt="" role="presentation">
```

### Missing Form Labels
```html
<!-- Violation -->
<input type="email" placeholder="Email">

<!-- Fix -->
<label for="email">Email address</label>
<input type="email" id="email" placeholder="user@example.com">
```

### Low Color Contrast
```css
/* Violation: 2.5:1 ratio */
color: #999999;
background: #ffffff;

/* Fix: 4.6:1 ratio (meets AA) */
color: #767676;
background: #ffffff;

/* Fix: 7.1:1 ratio (meets AAA) */
color: #595959;
background: #ffffff;
```

### Missing Focus Indicators
```css
/* Violation */
*:focus { outline: none; }

/* Fix */
*:focus-visible {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
}
```

### Missing Skip Navigation
```html
<!-- Add as first element in body -->
<a href="#main-content" class="skip-link">Skip to main content</a>
<!-- ... header/nav ... -->
<main id="main-content">
```

---

## Testing Techniques

### Keyboard Navigation Test
1. Start at the top of the page, press Tab repeatedly.
2. Verify every interactive element receives focus in a logical order.
3. Verify focus is visible on every focused element.
4. Test Enter/Space to activate buttons and links.
5. Test Escape to close modals and popups.
6. Verify no keyboard traps (can always Tab away).

### Screen Reader Quick Check
1. Navigate by headings (H key in NVDA/VoiceOver) — verify logical hierarchy.
2. Navigate by landmarks (D key) — verify main, nav, banner regions exist.
3. Navigate by form elements — verify all inputs are labeled.
4. Navigate by links — verify link text makes sense out of context.

### Contrast Ratio Check
- Normal text (<18pt / <14pt bold): minimum 4.5:1 (AA), 7:1 (AAA)
- Large text (>=18pt / >=14pt bold): minimum 3:1 (AA), 4.5:1 (AAA)
- UI components and graphics: minimum 3:1 (AA)

### Zoom/Reflow Test
1. Zoom browser to 200% — verify no content loss or horizontal scroll.
2. Set viewport to 320px width — verify content reflows properly.
3. Increase text spacing (letter-spacing: 0.12em, word-spacing: 0.16em, line-height: 1.5) — verify no clipping.

---

*Reference for the QA Browser Automation skill. Use with accessibility_auditor.py for automated checks.*
