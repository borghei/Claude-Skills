# Interface context: Ledgerly

## Platform

web

## Users and jobs

- Primary: owners of two-to-ten person service businesses who invoice clients themselves, usually at a laptop on Friday afternoon after the week's work is done.
- Job: find who has not paid, chase them without sounding rude, and raise next week's invoices in under ten minutes.
- Secondary: a part-time bookkeeper who exports the ledger once a month and needs the numbers to match the bank.

## Purpose and positioning

- Purpose: get a small business paid for work already done, with as little admin as possible.
- Positioning: reminders are drafted from the client's own payment history, so the first chase is polite and the third is firm without the owner writing either.

## Surfaces

- /invoices: operate - scan open and overdue invoices and send reminders in bulk
- /invoices/new: operate - raise a correct invoice from a saved client in one pass
- / (marketing home): persuade - show a sole trader that chasing money takes minutes, then start a free account
- /help: read - answer one billing question per page without making people call support

## Voice and terms

- Voice: plain and calm, like a good bookkeeper. Money is never a joke; overdue is stated as days, not shamed.
- Terms: invoice (never "bill"), client (never "customer"), reminder (never "dunning"), draft, sent, paid, overdue.
- Numbers: currency code before the amount (EUR 1,240.00); dates as 3 Oct, never 10/03.

## Evidence on hand

- Product screenshots of the invoice list and new-invoice form: assets/screens/
- Pricing table agreed with finance: docs/pricing-2026.md
- Testimonials: none yet, do not invent quotes or logos.
- Usage numbers: none published; do not show counts of users or invoices sent.

## Principles

- The overdue list is the home screen; everything else is one step away from it.
- Never make the owner retype what the ledger already knows.
- Money and dates are exact; friendliness lives in the words around them.

## Constraints

- Accessibility: WCAG 2.2 AA on every surface, keyboard-complete invoice flow.
- Locales: English and German at launch; German labels run roughly 30% longer.
- Browsers: current and previous major versions of Chrome, Safari, Firefox, Edge; 360px phones upward.

## Visual system

### Palette roles

- surface: #ffffff
- surface-sunken: #f3f5f7
- text: #1b2430
- text-muted: #4d5a6a
- action: #0b5cad
- action-text: #ffffff
- danger: #a3261b
- rule: #d5dbe2
- selection: #cfe3f7

### Type roles

- body: Source Sans 3, 16px/1.55, 400
- heading: Source Sans 3, 28px/1.2, 600
- subheading: Source Sans 3, 20px/1.3, 600
- label: Source Sans 3, 14px/1.4, 600
- figures: Source Sans 3 with tabular numerals, 16px/1.4, 400

### Spacing scale

- steps: 4, 8, 12, 16, 24, 40, 64

### Radius

- control: 6px
- container: 8px

### Elevation

- resting: none; rows and panels sit flat and are separated by the rule colour
- raised: 0 2px 8px rgba(27, 36, 48, 0.12) for menus and the date picker only

### Layout

- content width: 72rem, prose capped at 65ch
- grid: one column under 720px, list plus detail panel above it

### Components

- button: 6px radius, action fill for the one primary action per view, outline for the rest
- table: tabular numerals, amounts right-aligned, status as a coloured word, never a dot alone
- field: label above, hint below, error replaces the hint in the danger colour

### Motion

- durations: 150ms, 250ms, 400ms
- easing: cubic-bezier(0.2, 0.8, 0.2, 1)
- reduced motion: crossfade only, no movement

### Named rules

- **The Ledger Rule.** Money is set in tabular numerals, right-aligned, with the currency code.
- **The One Red Rule.** Red appears only for overdue and destructive actions, never for emphasis.

### Refusals

- side-stripe-border
- nested-cards
- kicker-above-heading
- gradient-text
- chip-soup
