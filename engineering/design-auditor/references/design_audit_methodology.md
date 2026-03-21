# Design Audit Methodology

Expert reference for systematic UI/UX design evaluation. Covers audit approaches, heuristic evaluation, Gestalt principles, critique frameworks, and common anti-patterns.

## Systematic Audit Approach

### Three-Level Audit

Design audits operate at three levels of zoom, each revealing different issues:

**Level 1: Top-Down (Page/Screen Level)**
- First impressions and visual hierarchy
- Content organization and information density
- Overall composition and whitespace usage
- Brand consistency across screens
- Key question: "Does the user know what to do within 5 seconds?"

**Level 2: Component Level**
- Individual component quality and consistency
- Design system adherence
- State completeness (hover, focus, active, disabled, error, empty, loading)
- Spacing and alignment within and between components
- Key question: "Does every component behave predictably?"

**Level 3: Interaction Level**
- User flow continuity across screens
- Transition and animation quality
- Error handling and recovery paths
- Edge cases (empty states, overflow, extreme content lengths)
- Key question: "Can the user complete their task without confusion?"

### Audit Execution Order

1. **Inventory** — Catalog all unique screens, components, and states
2. **Heuristic Pass** — Evaluate against Nielsen's 10 heuristics
3. **Accessibility Pass** — WCAG compliance check
4. **Consistency Pass** — Design system adherence
5. **Flow Pass** — End-to-end user journey evaluation
6. **Polish Pass** — Micro-interactions, animation, and edge cases
7. **Scoring** — Aggregate findings into category scores

## Nielsen's 10 Usability Heuristics

### 1. Visibility of System Status
The system should keep users informed about what is going on through appropriate feedback within reasonable time. Every action should produce a visible, immediate response.

- Loading indicators for operations > 1 second
- Progress bars for multi-step processes
- Success/error confirmations for destructive or important actions
- Real-time validation on form inputs

### 2. Match Between System and Real World
The system should speak the user's language, using familiar words, phrases, and concepts. Follow real-world conventions to make information appear in a natural and logical order.

- Use domain-appropriate terminology (not developer jargon)
- Icons should map to universal or domain-standard metaphors
- Data should be presented in familiar formats (dates, currencies, units)

### 3. User Control and Freedom
Users often make mistakes. Provide clearly marked "emergency exits" to leave unwanted states without requiring extended dialogue.

- Undo/redo for destructive actions
- Clear cancel/back buttons in flows
- Confirmation dialogs for irreversible actions (not for routine ones)
- Easy navigation back to known states

### 4. Consistency and Standards
Users should not have to wonder whether different words, situations, or actions mean the same thing. Follow platform conventions.

- Same interaction pattern for same action types
- Consistent terminology throughout
- Platform-appropriate patterns (mobile vs desktop)
- Design system tokens used consistently

### 5. Error Prevention
Eliminate error-prone conditions or present users with a confirmation option before they commit to an action.

- Disable invalid options rather than allowing invalid selection
- Smart defaults that reduce input errors
- Inline validation before form submission
- Constraint-based inputs (date pickers, dropdowns for fixed options)

### 6. Recognition Rather Than Recall
Minimize user memory load by making objects, actions, and options visible. Do not require the user to remember information across screens.

- Visible navigation showing current location
- Recently used items accessible
- Form fields with labels visible (not just placeholder text)
- Contextual help where needed

### 7. Flexibility and Efficiency of Use
Accelerators for expert users that do not slow down novice users. Allow users to tailor frequent actions.

- Keyboard shortcuts for power users
- Customizable dashboards or workflows
- Bulk actions for repetitive tasks
- Progressive disclosure (simple by default, powerful when needed)

### 8. Aesthetic and Minimalist Design
Dialogues should not contain irrelevant or rarely needed information. Every extra unit of information competes with relevant information.

- Remove decorative elements that do not serve function
- Prioritize content over chrome
- Progressive disclosure for secondary information
- Whitespace used intentionally (not just "more padding")

### 9. Help Users Recognize, Diagnose, and Recover from Errors
Error messages should be expressed in plain language, precisely indicate the problem, and constructively suggest a solution.

- Specific error messages (not "Something went wrong")
- Point to the exact field or action that caused the error
- Suggest a concrete fix or next step
- Maintain user's input on error (do not clear forms)

### 10. Help and Documentation
Even though the system should be usable without documentation, it may be necessary to provide help. Any such information should be easy to search, focused on the user's task, and list concrete steps.

- Contextual tooltips and inline help
- Searchable documentation
- Onboarding for first-time users
- Task-oriented help (not feature-oriented)

## Gestalt Principles Applied to UI

### Proximity
Elements close together are perceived as a group. Use spacing to create logical groupings of related content. The spacing between groups should be noticeably larger than spacing within groups.

**Application:** Form field labels near their inputs, related action buttons grouped together, card content with internal consistency.

### Similarity
Elements that look similar are perceived as part of the same group. Use consistent visual treatment (color, size, shape) for elements with the same function.

**Application:** All primary buttons share the same style, all navigation links look similar, all card components follow the same layout.

### Continuity
The eye follows smooth paths. Align elements along clear axes to create visual flow.

**Application:** Left-aligned text in lists, consistent grid alignment, visual flow from headline through body to CTA.

### Closure
The mind completes incomplete shapes. Implied boundaries (whitespace, subtle dividers) can replace explicit borders.

**Application:** Card layouts without borders (using shadow or whitespace), implied grid structure, icon design using negative space.

### Figure-Ground
Users naturally distinguish foreground elements from background. Use contrast, elevation, and color to establish clear layers.

**Application:** Modal overlays with dimmed backgrounds, active vs inactive tab states, selected vs unselected items.

### Common Fate
Elements moving in the same direction are perceived as grouped. Use consistent animation direction for related elements.

**Application:** List items animating in sequence, related panels sliding together, coordinated micro-interactions.

## Design Critique Frameworks

### The "What/Why/How" Framework
1. **What** is happening in the design? (Objective observation)
2. **Why** is it a problem or strength? (Impact analysis)
3. **How** should it be changed? (Actionable recommendation)

### Severity Rating
- **Critical:** Prevents task completion or causes data loss
- **Major:** Significantly slows users or causes confusion
- **Minor:** Noticeable but does not block task completion
- **Enhancement:** Improvement that adds polish

### Impact vs Effort Matrix
Prioritize fixes by plotting impact (user benefit) against effort (implementation cost):
- **High Impact / Low Effort:** Do first (quick wins)
- **High Impact / High Effort:** Plan for next sprint
- **Low Impact / Low Effort:** Batch together
- **Low Impact / High Effort:** Deprioritize or skip

## Common UI Anti-Patterns

### Navigation
- **Mystery meat navigation** — Icons without labels, unclear affordances
- **Deep nesting** — Content buried more than 3 levels deep
- **Inconsistent back behavior** — Back button behavior varies across screens
- **Hidden navigation** — Hamburger menu on desktop where space is available

### Forms
- **Placeholder-only labels** — Labels disappear when user starts typing
- **Late validation** — Errors shown only after full form submission
- **Ambiguous required fields** — No indication of which fields are required
- **Reset button near submit** — Easy to accidentally lose all input

### Layout
- **False floor** — No indication that content continues below the fold
- **Trapped whitespace** — Inconsistent spacing that creates visual tension
- **Competing CTAs** — Multiple primary-styled buttons competing for attention
- **Content shifting** — Layout moves as elements load asynchronously

### Feedback
- **Silent failures** — Actions fail without informing the user
- **Infinite spinners** — Loading states without timeout or fallback
- **Success amnesia** — No confirmation that an action completed
- **Modal abuse** — Modals for content that should be inline

### Mobile
- **Tiny touch targets** — Interactive elements smaller than 44x44px
- **Hover-dependent features** — Functionality only accessible via hover
- **Pinch-to-read** — Text too small to read without zooming
- **Gesture guessing** — Swipe actions without visual cues
