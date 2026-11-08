# distill — remove what does not earn its place

**Job:** strip a surface to what its visitor needs, so the primary task or message is obvious.

**Run when:** the detector reports `nested-cards`, `chip-soup`, `numbered-section-labels` or
`shape-assembled-illustration`; a
critique says "cluttered", "too many options", or "I don't know where to look".

## By mode

- **Persuade / Showcase:** one message per section, one primary action per viewport.
- **Operate / Read:** one primary action per screen region, progressive disclosure for rare
  options, density kept where experts rely on it.

## Change

- **Containers:** flatten. A card inside a card becomes a section with a heading, a row, or a
  divider. Plain layout uses spacing and alignment, not boxes.
- **Status chips:** keep the one chip that drives a decision (overdue, failed, blocked); print the
  rest as metadata text.
- **Actions:** one primary, a few secondary, the rest in a menu or on the detail view.
- **Repetition:** say each thing once. A heading that restates the intro sentence loses the intro.
- **Variation:** collapse near-duplicate sizes, colours and radii onto the scale.
- **Decoration:** borders, shadows and backgrounds that encode no grouping or state go.

## Do not touch

- Functionality. Simpler is not fewer features; hide rare options, do not delete them without
  the owner's agreement.
- Information people need to decide (price, consequence, deadline).
- Accessibility affordances: labels, focus, landmark structure.
- Domain complexity that is genuinely there. Match the complexity of the task, not a mood board.

## Steps

1. Name the surface's single job from the context file. If it has two, ask which leads.
2. List every element and mark it: essential, supporting, removable, hideable.
3. Remove and hide in one pass; flatten containers last so grouping is decided by spacing.
4. Write down anything removed that someone may miss, with where it now lives.

## Verify

- `ui_slop_detector.py <target> --rules nested-cards,chip-soup,numbered-section-labels` exits 0.
- The squint test: blur the screenshot; the first, second and third things are still in order.
- Every removed option is reachable or the owner agreed to drop it.
- Task time for the primary job is the same or shorter (walk it with the keyboard).

## Hand-off

`layout` if grouping now needs a rhythm pass; otherwise `polish`.
