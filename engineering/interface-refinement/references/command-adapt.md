# adapt — rethink for another device, input or medium

**Job:** make a surface work in a context it was not designed for: phone, tablet, wide screen,
touch, print, email, or another platform. Adaptation is restructuring, not scaling.

**Run when:** a critique or audit finds overflow, cramped touch targets or desktop-only patterns;
before shipping a web app to mobile; when porting between iOS, Android and web.

## Change (web)

- **Phone:** one column; primary action reachable by thumb; navigation collapses into a menu or a
  bottom bar of 3-5 sections; tables become stacked rows or a horizontal scroller with a sticky
  first column; touch targets 44px comfortable (24px is the WCAG minimum with spacing).
- **Tablet:** two panes (list and detail) where the task has both; popovers instead of full sheets.
- **Wide screens:** cap the reading measure; use the width for side-by-side work, not stretched
  cards.
- **Input:** detect hover and pointer (`@media (hover: hover) and (pointer: fine)`) rather than
  screen width; never hide a function behind hover alone.
- **Safe areas:** `env(safe-area-inset-*)` padding for fixed bars on notched devices.
- **Images:** `srcset` and `sizes`; art direction with `<picture>` when the crop must change.
- **Print / email:** print stylesheet that drops navigation and expands links; email layouts in
  tables with inline styles and a 600px body.

## Change (native, and between platforms)

Follow `native-platforms.md`. Translate idioms; never transplant them: tab bar to navigation
bar or rail, edge-swipe back to the system back gesture, segmented control to chips, SF Symbols
to Material Symbols, Dynamic Type to sp. Drive layout from size classes / window size classes,
never from device model checks.

## Do not touch

- Function. Do not hide a core feature on small screens; make it work there.
- The visual identity; the brand's expressive layer is carried through the target's theming.
- Orientation locks used to dodge a layout bug.

## Steps

1. Name the source assumptions (desktop, mouse, portrait, one platform) and the target context
   (device class, input, posture, platform).
2. List what breaks: navigation, tables, hover affordances, fixed widths, gestures.
3. Restructure by priority for the target; then fix details.

## Verify

- Screenshots at 360px, 768px and 1280px (web) or on each shipped device class (native), both
  orientations where supported.
- No horizontal page scroll at 360px; text at 200% zoom still fits.
- Every control reachable by touch with a target of at least 44px (iOS 44pt, Android 48dp).
- Say which evidence came from emulation and which from hardware; gestures and performance need
  hardware.

## Hand-off

`polish`.
