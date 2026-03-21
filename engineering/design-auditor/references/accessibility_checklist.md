# WCAG 2.1 Accessibility Checklist

Complete checklist covering Level A, Level AA, and Level AAA success criteria. Organized by POUR principles (Perceivable, Operable, Understandable, Robust) with testing methodology and common fixes.

## Level A (Minimum Compliance — 29 Criteria)

Level A criteria represent the absolute minimum for accessibility. Failure means some users cannot access content at all.

### Perceivable

| # | Criterion | Check | Common Violation |
|---|-----------|-------|------------------|
| 1.1.1 | Non-text Content | All images, icons, and media have text alternatives | Missing alt attributes, decorative images without `alt=""` |
| 1.2.1 | Audio-only / Video-only | Pre-recorded audio has transcript; video has audio description or transcript | Podcast without transcript, video without description |
| 1.2.2 | Captions (Pre-recorded) | All pre-recorded video with audio has synchronized captions | Auto-generated captions without review, missing speaker ID |
| 1.2.3 | Audio Description or Alternative | Video has audio description or full text transcript | Complex visual content in video without description |
| 1.3.1 | Info and Relationships | Semantic markup conveys structure (headings, lists, tables, forms) | `<div>` used instead of `<h1>`-`<h6>`, tables without headers |
| 1.3.2 | Meaningful Sequence | Reading order matches visual order in DOM | CSS reordering breaks logical reading sequence |
| 1.3.3 | Sensory Characteristics | Instructions do not rely solely on shape, size, location, or sound | "Click the round button" or "see the red text" |
| 1.4.1 | Use of Color | Color is not the only means of conveying information | Error states indicated only by red color, links only by color |
| 1.4.2 | Audio Control | Audio playing > 3 seconds can be paused or volume controlled | Auto-playing background audio without controls |

### Operable

| # | Criterion | Check | Common Violation |
|---|-----------|-------|------------------|
| 2.1.1 | Keyboard | All functionality available via keyboard | Drag-and-drop only, custom widgets without key handlers |
| 2.1.2 | No Keyboard Trap | Focus can be moved away from any component via keyboard | Modal dialogs that trap focus without escape |
| 2.1.4 | Character Key Shortcuts | Single-character shortcuts can be turned off or remapped | Custom shortcuts conflicting with screen reader commands |
| 2.2.1 | Timing Adjustable | Time limits can be extended or turned off | Session timeout without warning or extension |
| 2.2.2 | Pause, Stop, Hide | Moving/auto-updating content can be paused or stopped | Carousels without pause, auto-scrolling tickers |
| 2.3.1 | Three Flashes | No content flashes more than 3 times per second | Video content, animated backgrounds |
| 2.4.1 | Bypass Blocks | Skip navigation link or landmark regions provided | No skip-to-content link, no ARIA landmarks |
| 2.4.2 | Page Titled | Pages have descriptive, unique titles | "Untitled" or same title across all pages |
| 2.4.3 | Focus Order | Tab order is logical and follows visual layout | Tabindex values creating illogical focus sequence |
| 2.4.4 | Link Purpose (in Context) | Link text describes destination (with context) | "Click here", "Read more" without context |
| 2.5.1 | Pointer Gestures | Multi-point/path gestures have single-pointer alternatives | Pinch-to-zoom only, no button alternative |
| 2.5.2 | Pointer Cancellation | Down-event does not trigger action; up-event can be aborted | Click on mousedown instead of mouseup/click |
| 2.5.3 | Label in Name | Visible label text is contained in accessible name | Button says "Search" but `aria-label` says "Find items" |
| 2.5.4 | Motion Actuation | Motion-triggered actions have UI alternatives | Shake-to-undo without button alternative |

### Understandable

| # | Criterion | Check | Common Violation |
|---|-----------|-------|------------------|
| 3.1.1 | Language of Page | `lang` attribute on `<html>` element | Missing `lang="en"` or incorrect language code |
| 3.2.1 | On Focus | No unexpected changes when element receives focus | Page navigation triggered by focus, auto-expanding menus |
| 3.2.2 | On Input | No unexpected changes when user changes input | Form submission on select change without warning |
| 3.3.1 | Error Identification | Errors are identified and described in text | Form errors shown only by color change |
| 3.3.2 | Labels or Instructions | Input fields have visible labels and necessary instructions | Placeholder-only labels, missing format hints |

### Robust

| # | Criterion | Check | Common Violation |
|---|-----------|-------|------------------|
| 4.1.1 | Parsing | Valid HTML (deprecated in WCAG 2.2 but still good practice) | Duplicate IDs, unclosed tags, malformed ARIA |
| 4.1.2 | Name, Role, Value | Custom UI components have proper ARIA roles and states | Custom dropdown without `role="listbox"`, toggle without `aria-checked` |

## Level AA (Standard Compliance — 20 Criteria)

Level AA is the standard target for most web applications and is required by many regulations (ADA, EN 301 549, Section 508).

### Perceivable

| # | Criterion | Check | Common Violation |
|---|-----------|-------|------------------|
| 1.2.4 | Captions (Live) | Live audio content has real-time captions | Live streams without captioning service |
| 1.2.5 | Audio Description (Pre-recorded) | Pre-recorded video has audio description | Training videos with visual-only instructions |
| 1.3.4 | Orientation | Content not restricted to single display orientation | Mobile app locked to portrait mode |
| 1.3.5 | Identify Input Purpose | Input fields have `autocomplete` attributes for user data | Name, email, address fields without autocomplete |
| 1.4.3 | Contrast (Minimum) | Text has 4.5:1 ratio (normal) or 3:1 (large text) | Gray text on light gray background, low-contrast placeholders |
| 1.4.4 | Resize Text | Text can be resized to 200% without loss of content | Fixed-height containers, text in images, overflow: hidden |
| 1.4.5 | Images of Text | Real text used instead of images of text (with exceptions) | Logo text, headings as images, infographic text |
| 1.4.10 | Reflow | Content reflows at 320px width without horizontal scroll | Fixed-width tables, absolute positioning at small viewports |
| 1.4.11 | Non-text Contrast | UI components and graphical objects have 3:1 contrast | Light gray borders on white inputs, low-contrast icons |
| 1.4.12 | Text Spacing | Content readable with increased text spacing | Containers that clip text when line-height is increased |
| 1.4.13 | Content on Hover/Focus | Hover/focus content is dismissible, hoverable, and persistent | Tooltips that disappear when moving cursor to them |

### Operable

| # | Criterion | Check | Common Violation |
|---|-----------|-------|------------------|
| 2.4.5 | Multiple Ways | Multiple ways to locate pages (search, sitemap, navigation) | Single navigation path only |
| 2.4.6 | Headings and Labels | Headings and labels are descriptive | Generic headings like "Section 1", "Info" |
| 2.4.7 | Focus Visible | Keyboard focus indicator is visible | `outline: none` without replacement focus style |

### Understandable

| # | Criterion | Check | Common Violation |
|---|-----------|-------|------------------|
| 3.1.2 | Language of Parts | Language changes within page are marked | Foreign phrases without `lang` attribute |
| 3.2.3 | Consistent Navigation | Navigation is consistent across pages | Navigation order changes between sections |
| 3.2.4 | Consistent Identification | Same function has same label across pages | "Search" on one page, "Find" on another |
| 3.3.3 | Error Suggestion | Error messages suggest corrections when possible | "Invalid input" without explaining valid format |
| 3.3.4 | Error Prevention (Legal/Financial) | Reversible, verified, or confirmed submissions for important data | Financial transactions without confirmation step |

### Robust

| # | Criterion | Check | Common Violation |
|---|-----------|-------|------------------|
| 4.1.3 | Status Messages | Status updates announced without focus change | Toast notifications not announced by screen readers |

## Level AAA (Enhanced — 28 Criteria)

Level AAA represents the highest level of accessibility. Full AAA compliance is not required for most sites but individual criteria may be targeted.

### Perceivable

| # | Criterion | Check |
|---|-----------|-------|
| 1.2.6 | Sign Language (Pre-recorded) | Sign language interpretation for pre-recorded audio |
| 1.2.7 | Extended Audio Description | Extended audio description for pre-recorded video |
| 1.2.8 | Media Alternative (Pre-recorded) | Full text alternative for all pre-recorded media |
| 1.2.9 | Audio-only (Live) | Text alternative for live audio |
| 1.3.6 | Identify Purpose | Component purpose can be programmatically determined |
| 1.4.6 | Contrast (Enhanced) | 7:1 contrast ratio (normal text), 4.5:1 (large text) |
| 1.4.7 | Low Background Audio | Speech audio has minimal background noise |
| 1.4.8 | Visual Presentation | Configurable foreground/background colors, line width, spacing |
| 1.4.9 | Images of Text (No Exception) | Images of text only used for decoration |

### Operable

| # | Criterion | Check |
|---|-----------|-------|
| 2.1.3 | Keyboard (No Exception) | All functionality keyboard accessible, no exceptions |
| 2.2.3 | No Timing | No time limits at all (except real-time events) |
| 2.2.4 | Interruptions | User can postpone or suppress interruptions |
| 2.2.5 | Re-authenticating | Data preserved when re-authenticating after timeout |
| 2.2.6 | Timeouts | Users warned about inactivity timeout duration |
| 2.3.2 | Three Flashes | No content flashes at all |
| 2.3.3 | Animation from Interactions | Users can disable motion animation |
| 2.4.8 | Location | Current location within site is indicated |
| 2.4.9 | Link Purpose (Link Only) | Link purpose clear from link text alone |
| 2.4.10 | Section Headings | Content organized with section headings |
| 2.5.5 | Target Size | Touch/click targets are at least 44x44px |
| 2.5.6 | Concurrent Input | No restriction on input modality |

### Understandable

| # | Criterion | Check |
|---|-----------|-------|
| 3.1.3 | Unusual Words | Definitions provided for jargon and unusual words |
| 3.1.4 | Abbreviations | Expanded form of abbreviations provided |
| 3.1.5 | Reading Level | Content at lower secondary education reading level |
| 3.1.6 | Pronunciation | Pronunciation provided for ambiguous words |
| 3.2.5 | Change on Request | Changes of context initiated only by user request |
| 3.3.5 | Help | Context-sensitive help available |
| 3.3.6 | Error Prevention (All) | Submissions are reversible, verified, or confirmed |

## Testing Methodology

### Automated Testing (Catches ~30% of Issues)
- Run axe-core, Lighthouse, or WAVE on every page
- Validate HTML with W3C validator
- Check color contrast with automated tools (use `color_contrast_checker.py`)
- Scan for missing alt text, form labels, and ARIA attributes

### Manual Testing (Catches ~50% of Issues)
- **Keyboard navigation:** Tab through entire page, verify focus order and visibility
- **Zoom testing:** Zoom to 200% and verify content reflows without horizontal scroll
- **Text spacing:** Apply WCAG text spacing overrides and verify no content is clipped
- **Color independence:** View in grayscale to verify information not conveyed by color alone
- **Reduced motion:** Enable `prefers-reduced-motion` and verify animations respect it

### Assistive Technology Testing (Catches ~20% of Issues)
- **Screen reader:** Test with VoiceOver (macOS), NVDA (Windows), or TalkBack (Android)
- **Voice control:** Test with Dragon NaturallySpeaking or Voice Control
- **Switch access:** Verify all functionality reachable with switch navigation
- **Magnification:** Test with system magnifier at 4x and higher

### Priority Fixes by Impact

**Highest impact (fix first):**
1. Missing form labels — blocks screen reader users from completing tasks
2. Missing alt text on functional images — hides information and actions
3. No keyboard access to interactive elements — blocks keyboard and switch users
4. Insufficient color contrast — affects low vision users (large population)
5. No focus indicators — keyboard users cannot see where they are

**Medium impact:**
6. Missing heading structure — difficult navigation for screen readers
7. Missing landmarks — cannot skip to content sections
8. Auto-playing media — disorienting for all users, disruptive for screen readers
9. Missing error identification — users cannot correct mistakes
10. Missing language attribute — screen readers use wrong pronunciation

### Common Fixes Reference

| Issue | Fix |
|-------|-----|
| Missing alt text | Add `alt="description"` for informative images, `alt=""` for decorative |
| No form labels | Add `<label for="id">` or `aria-label` to every input |
| Low contrast | Use `color_contrast_checker.py` to find compliant alternatives |
| No focus indicator | Add `:focus-visible` styles with visible outline or ring |
| Missing heading hierarchy | Use `<h1>` through `<h6>` in logical order, no skipped levels |
| Keyboard inaccessible | Add `tabindex="0"` and key event handlers to custom widgets |
| No skip link | Add `<a href="#main" class="skip-link">Skip to content</a>` |
| Missing landmarks | Use `<main>`, `<nav>`, `<header>`, `<footer>`, `<aside>` |
| No ARIA on custom widgets | Add appropriate `role`, `aria-label`, `aria-expanded`, etc. |
| No reduced motion | Add `@media (prefers-reduced-motion: reduce)` to disable animations |
