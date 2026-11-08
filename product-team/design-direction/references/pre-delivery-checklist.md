# Pre-Delivery Checklist

The spec is a promise; this list checks the built interface keeps it. Run it on the real
build, on a real phone where the product runs on one, before the work is called done. The
token checker proves the tokens are sound. Only this pass proves the screens use them.

Mark each item pass, fail, or not applicable with a reason. A fail on any **critical** line
blocks delivery.

## 1. Process

- [ ] **critical** The verdict, findings and contrast tables in the spec came from the tool,
      not from memory, and the shipped theme re-checks to exit 0 (`css_token_extractor.py`
      then `design_spec_checker.py`).
- [ ] Every page or screen built maps to a pattern in the spec (`page_patterns`) or has a
      written reason for departing from it.
- [ ] Viewed at 320px, 375px, 768px and 1280px wide, and in landscape on a phone.
- [ ] Viewed with the OS set to reduced motion, to the largest text size, and to dark mode
      (when the spec covers dark).

## 2. Colour and contrast

- [ ] **critical** No component uses a raw hex value; all colour comes from the role tokens.
- [ ] **critical** Text on images, video and translucent panels reaches 4.5:1 over the
      busiest part of the background, measured, not judged.
- [ ] Borders, dividers, disabled controls and placeholder text are visible in both modes.
- [ ] Status (error, warning, success, selected) is carried by text or an icon as well as
      colour.
- [ ] Dialog scrims make the dialog readable over the busiest page behind it.

## 3. Type

- [ ] Only the families in the spec load, in the weights the spec lists.
- [ ] Body copy is at the spec's base size; nothing that must be read is below 12px.
- [ ] Long text wraps at 45-80 characters; headings have no one-word last lines.
- [ ] Numbers in tables and live values use tabular figures.

## 4. Icons and imagery

- [ ] One icon family, at the spec's icon sizes and stroke, one style (outline or filled) per
      level of hierarchy.
- [ ] No emoji used as interface icons.
- [ ] Icon-only buttons have an accessible name; decorative icons are hidden from assistive
      technology.
- [ ] Logos and third-party marks use the owner's artwork and clear space.
- [ ] Every image has width and height (or an aspect ratio) set, and meaningful images have
      alternative text.

## 5. Interaction

- [ ] **critical** Every interactive element shows a visible focus ring from the focus
      tokens, and keyboard order follows visual order.
- [ ] **critical** Touch targets meet the spec's minimum (44px web, 48dp Android, 44pt iOS),
      including icon buttons and links inside text.
- [ ] Every control has default, hover, pressed, focus and disabled states; pressed states do
      not shift layout.
- [ ] Destructive actions confirm or offer undo; async buttons show progress and lock.
- [ ] Back, swipe-back and Escape close sheets and dialogs and return focus to the trigger.
- [ ] Nothing essential depends on hover, drag or a gesture without a button alternative.

## 6. Motion

- [ ] Durations and easing come from the spec's `motion_map` for its tier; exits run faster
      than entries.
- [ ] Only transform and opacity animate; nothing animates width, height or top.
- [ ] Under reduced motion, every row of the motion map shows its listed replacement.
- [ ] Nothing flashes more than three times a second; auto-advancing content can be paused.

## 7. Layout and states

- [ ] No horizontal scroll at 320px; fixed bars leave content reachable (scroll padding).
- [ ] Safe areas respected on phones: nothing under the notch, status bar or home indicator.
- [ ] Each data view has loading, empty, error, partial and offline states designed, not
      left to defaults.
- [ ] Strings 30-40% longer than English do not break layouts; right-to-left mirrors when
      the product supports it.

## 8. Product-specific

- [ ] Every item in the spec's **Avoid** list was checked and is absent.
- [ ] Every item in **Product risks** has a design answer on the relevant screen.
- [ ] Landing pages: the proof the pattern asks for is real and verifiable; no invented
      numbers, timers or testimonials.
