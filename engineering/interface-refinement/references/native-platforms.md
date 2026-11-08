# Native platforms: iOS and Android

Use this when the context file's platform is `ios`, `android` or `cross-platform`. On native, the
platform's conventions govern structure, navigation and interaction in every mode; the brand
expresses through what the platform leaves open (tint, type in display moments, motion
character, content). The web detector does not read Swift, Kotlin or Dart; it applies to
React Native or Flutter web output only. Never report its empty result on native code as clean.

## The trust test

Would a fluent user of this platform trust the app, or pause at a control that behaves wrongly?
The tell on iOS is "a website in a wrapper": custom navigation bars, a broken back swipe, web-shaped
buttons, hover affordances. The tell on Android is "an iPhone app in disguise": bottom-only
navigation on a tablet, a back arrow that ignores system Back, Cupertino switches and dialogs.

## Checks

| Area | iOS / iPadOS | Android |
|------|--------------|---------|
| Layout | content inside safe-area insets; nothing under the notch, Dynamic Island or home indicator | edge-to-edge with window insets for status bar, navigation bar, cutout and keyboard |
| Navigation | tab bar for 2-5 top-level sections, navigation stack for depth, sheets for self-contained tasks | navigation bar (3-5 destinations) on compact width; rail or drawer on expanded width |
| Back | left-edge swipe always works; never overlaid or disabled | predictive Back gesture and Back button always work; never trap the user |
| Titles | large titles on top-level screens collapsing on scroll | top app bar carries screen context; one FAB for the single primary action |
| Touch targets | 44 x 44 pt minimum with room between | 48 x 48 dp minimum, 8 dp apart |
| Type | system text styles so Dynamic Type works; 11 pt floor, Body 17 pt; brand face only in display moments | Material type roles (display, headline, title, body, label); `sp` units so font scale works |
| Colour | semantic system colours (label, secondaryLabel, systemBackground, tint); one tint drives interaction | Material colour roles (primary, on-primary, surface, outline, error); Dynamic Color where it fits |
| Dark | Dark Mode designed and tested, not inverted | dark theme designed and tested; tonal elevation, not arbitrary shadows |
| Controls | system switch, segmented control, pickers, action sheets, context menus, swipe actions | Material buttons (filled/tonal/outlined/text), chips, switches, snackbars, bottom sheets, dialogs |
| Icons | SF Symbols, weight matched to text | Material Symbols |
| Motion | push, sheet and dismiss transitions from the system; Reduce Motion swaps slides for crossfades | container transform, shared axis, fade through; Remove animations gives a crossfade or cut |

## Native audit dimensions (replace the web five)

1. **Accessibility:** VoiceOver / TalkBack labels and traits on every control, logical focus
   order, Dynamic Type / font scale to the largest size without truncation, increased contrast.
2. **Performance:** dropped frames on scroll and transitions, main-thread work on launch, image
   decoding off the main thread.
3. **Appearance:** light and dark, increased contrast, tint and colour roles instead of literals.
4. **Platform conformance:** navigation model, back behaviour, native controls, targets, modality.
5. **Adaptivity:** size classes / window size classes, orientation, split view and multi-window,
   foldable postures.

## Translating between platforms

Translate idioms, never transplant them:

| iOS | Android | Web |
|-----|---------|-----|
| tab bar | navigation bar / rail / drawer | top nav or side rail |
| edge-swipe back, back chevron | predictive Back | browser back, breadcrumb |
| segmented control | chips or segmented button | tabs or radio group |
| action sheet | bottom sheet or dialog | menu or dialog |
| SF Symbols, SF Pro, Dynamic Type | Material Symbols, Roboto, sp | one icon set, the product's faces, rem |
| system materials | tonal elevation | shadow tokens |

Carry the brand's expressive layer (palette intent, type accent, motion personality) through each
platform's theming system.

## Evidence

Screenshots come from the simulator or emulator or a device, never from a browser preview of
native code. iOS: `xcrun simctl io booted screenshot <path>`; flip appearance with
`xcrun simctl ui booted appearance dark`. Android: `adb exec-out screencap -p > <path>`; dark theme
with `adb shell cmd uimode night yes`; font scale with `adb shell settings put system font_scale 1.3`
(read and restore the original values). Capture every device class the app ships to. Simulators
give breadth; gestures, refresh rate and performance need hardware. Say which produced the evidence.
