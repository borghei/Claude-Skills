---
name: apple-hig-expert
description: >
  Apple Human Interface Guidelines expert across iOS, iPadOS, macOS, watchOS,
  tvOS, and visionOS. Use when designing or reviewing an Apple-platform app,
  auditing for HIG compliance, picking native components, or validating
  accessibility.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: product-team
  domain: design
  updated: 2026-05-27
  tags: [apple, hig, ios, macos, watchos, visionos, design, accessibility]
---

# Apple Human Interface Guidelines (HIG) Expert

A skill focused on shipping apps that feel native on Apple platforms.
Covers the underlying HIG principles, platform-specific patterns, native
component selection, and accessibility expectations.

This skill is opinionated about **native conventions**. It's not the
right skill if your goal is to maximize cross-platform UX uniformity over
native fit (see web design guides for that).

## When to use this skill

- Designing or reviewing an iOS / iPadOS / macOS / watchOS / tvOS / visionOS app
- Auditing an existing app for HIG compliance
- Picking the right native component (sheet vs popover vs full-screen)
- Adapting an app from one Apple platform to another
- Reviewing typography, color, spacing, and motion against HIG
- Auditing accessibility against Apple's accessibility expectations
- Onboarding a designer or PM new to Apple-platform design

## Inputs the advisor expects

- Target platform(s) and version range (iOS 17+, macOS 14+, etc.)
- App type (utility, productivity, social, games, media)
- Current designs / screenshots (described or referenced)
- Stack: SwiftUI vs UIKit / AppKit, recent or legacy codebase
- Accessibility maturity (WCAG audit done; VoiceOver tested)

## Clarify First

What most shapes this skill's output is the target platform and how much of the actual app you can show. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Platform and OS version:** component behavior differs by platform. A popover on compact iPhone becomes a sheet, inspectors belong to macOS and iPadOS, and the version range decides which APIs are available. `component_pattern_lookup.py` takes `--platform` for this reason.
- **Screens or designs:** the compliance and accessibility audits run on a screen inventory. Without screenshots or a description of each screen, the result is general guidance rather than findings.
- **Stack:** SwiftUI or UIKit/AppKit, new or legacy code, changes which fixes are cheap and how semantic colors and Dynamic Type get applied.
- **Accessibility baseline:** whether VoiceOver testing or a WCAG audit has already happened decides whether `accessibility_auditor.py` is a first pass or a check against known gaps.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflows

### Workflow 1 — Audit screens for HIG compliance

1. Describe or reference each screen.
2. Run `hig_compliance_checker.py` with the screen inventory.
3. Address findings by category (navigation, typography, controls, spacing, motion).

```bash
python3 apple-hig-expert/scripts/hig_compliance_checker.py \
  --input screens.json --format markdown
```

### Workflow 2 — Pick the right component for a flow

1. Describe the interaction goal.
2. Use `component_pattern_lookup.py` to surface candidate patterns,
   trade-offs, and platform-specific guidance.

```bash
python3 apple-hig-expert/scripts/component_pattern_lookup.py \
  --platform ios --goal "show options without leaving context" --format markdown
```

### Workflow 3 — Audit accessibility against Apple expectations

1. Capture screen inventory + accessibility attributes (labels, hints, traits).
2. Run `accessibility_auditor.py` to surface gaps.
3. Use Apple Accessibility Inspector to validate.

```bash
python3 apple-hig-expert/scripts/accessibility_auditor.py \
  --input a11y_state.json --format markdown
```

## Decision frameworks

### Sheets vs popovers vs full-screen

| Pattern | When to use | Platform |
|---------|-------------|----------|
| Sheet (medium / large) | Modal task with clear escape | iOS, iPadOS, macOS, visionOS |
| Popover | Context-anchored options, brief | iPadOS (compact: replaced with sheet), macOS |
| Full-screen cover | Immersive task, e.g., photo editing | iOS |
| Push (navigation stack) | Hierarchical drill-in | iOS, iPadOS |
| Inspector | Persistent secondary content | macOS, iPadOS |
| Toolbar item | Quick action on current context | All |

Common mistake: popover on compact iPhone (it becomes a sheet automatically;
design for both).

### When to use SwiftUI vs UIKit

- **SwiftUI** — new apps, simple-to-moderate complexity, multi-platform from one codebase
- **UIKit** — legacy code, complex interactions not yet ergonomic in SwiftUI, performance-sensitive
- **Mixed** — common; embed SwiftUI in UIKit hosts or vice versa

The trend (2026) is SwiftUI-first for new development; UIKit retains
strength in performance-sensitive lists and complex gesture handling.

### Color and dark mode

- Use **semantic colors** (`systemBackground`, `secondaryLabel`) — they
  adapt to light/dark mode automatically
- Avoid hardcoded hex values for system-feeling content
- Test in both light + dark mode + increased contrast settings
- Brand colors: assess contrast in both modes; use Asset Catalog with
  separate light/dark variants

### Typography

- Use **Dynamic Type** styles (`largeTitle`, `body`, `caption`) — they
  scale with user accessibility settings
- Don't hardcode font sizes for body text
- Custom fonts: still respect Dynamic Type through `UIFontMetrics` /
  SwiftUI `dynamicTypeSize`
- Test at largest Dynamic Type setting; design must remain usable

## Common engagements

### "Help me adapt our iPhone app for iPad"
1. Identify navigation: sidebar (NavigationSplitView) vs tabs at iPad sizes
2. Use Inspector for secondary content
3. Convert sheets to popovers where appropriate
4. Adapt to multitasking (split view, slide over)
5. Add hardware support: Pencil, keyboard shortcuts, pointer interactions

### "Our app feels un-Apple-y. What's wrong?"
1. Check typography — using Dynamic Type styles, not hardcoded sizes?
2. Check colors — semantic colors, dark mode parity?
3. Check spacing — multiples of 4 or 8; not custom every-screen
4. Check controls — using native ones, not custom toggles/buttons?
5. Check navigation — does back gesture work? Does state persist correctly?

### "Make our app accessible"
1. Every interactive element has a label
2. Decorative images marked `accessibilityHidden`
3. Focus order makes sense for VoiceOver
4. Custom controls have correct `accessibilityTraits`
5. Touch targets ≥44pt × 44pt
6. Color isn't the only way information is conveyed
7. Reduced motion respected
8. Test with VoiceOver, Voice Control, Switch Control, Dynamic Type max

## Anti-patterns to avoid

- **Custom UI for things iOS already provides.** Use native; users expect it.
- **Hardcoded font sizes.** Breaks Dynamic Type; breaks accessibility.
- **Same UI across all Apple platforms.** Each platform has different conventions.
- **Hamburger menu on iOS.** Tab bar is more discoverable.
- **Modal-heavy navigation.** Apple's nav stack is the primary pattern.
- **Custom navigation bar.** Use the system one; users know how it works.
- **Ignoring safe area insets.** Content gets clipped behind notches and home indicators.
- **No haptic feedback on iOS.** Apps that use it feel premium.
- **No keyboard support on iPad.** Power users will leave.

## Scope & Limitations

**In Scope:**
- HIG compliance audits of a screen inventory with `hig_compliance_checker.py` (navigation type, Dynamic Type, semantic colors, safe areas, touch targets, native components, SF Symbols)
- Native component suggestions for a stated UX goal on iOS, iPadOS, macOS, watchOS, tvOS or visionOS with `component_pattern_lookup.py`
- Accessibility gap checks with `accessibility_auditor.py`: labels, hints, traits, touch targets, color-only information, Dynamic Type, Reduce Motion and VoiceOver focus order
- Decision guidance on sheets versus popovers, SwiftUI versus UIKit, color and dark mode, typography, and adapting an app across Apple platforms

**Out of Scope:**
- Web accessibility and WCAG audits of HTML (see `engineering/a11y-audit/`)
- Writing the SwiftUI, UIKit or AppKit implementation (see `engineering/senior-mobile/`)
- Building a design system or component library (see `product-team/ui-design-system/`)
- App Store listing and ranking work (see `marketing/app-store-optimization/`)
- Android and Material Design guidance

**Important Caveats:**
- The auditors read a JSON inventory that the user fills in, mostly true or false flags per screen. They do not inspect screenshots, design files, source code or a running app.
- `component_pattern_lookup.py` matches keywords in the goal text against a fixed pattern catalog, so an unusual phrasing can return no match or a weak one.
- Apple revises the HIG and platform behavior with each OS release, so the guidance can go stale. Findings still need checking with Accessibility Inspector and VoiceOver on a device.

## References

- `references/hig-fundamentals.md` — principles, design language, foundational patterns
- `references/ios-component-patterns.md` — sheets, navigation, controls, gestures, lists
- `references/cross-platform-considerations.md` — iPad, Mac, Watch, TV, Vision differences

## Related skills

- `product-team/product-designer` — broader product design
- `product-team/ui-design-system` — design system construction
- `product-team/ux-researcher-designer` — research informing design
- `engineering/senior-frontend` — implementation
