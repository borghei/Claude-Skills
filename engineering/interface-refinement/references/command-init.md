# init — write the product half of the context file

**Job:** capture durable product truth in `interface-context.md` so every later command decides
from facts instead of guesses. Init records the product; it does not choose a look.

**Run when:** no context file exists and the work is more than a one-line fix; the context file
fails `context_linter.py`; the product changed (new audience, new platform, new surface).

## What belongs in it (product half)

| Section | Holds | Never holds |
|---------|-------|-------------|
| Platform | `web`, `ios`, `android` or `cross-platform` | stack details |
| Users and jobs | who, in what situation, doing which job | personas with invented names and ages |
| Purpose and positioning | what the product is for; the mechanism or claim a neighbour could not truthfully copy | slogans, adjectives |
| Surfaces | `- <surface>: <mode> - <job>` per surface | page layouts |
| Voice and terms | voice in one or two sentences, the glossary of preferred terms | visual adjectives |
| Evidence on hand | real assets with paths; stated absences ("testimonials: none, do not invent") | numbers nobody can source |
| Principles | two to five durable decisions the team can cite ("the overdue list is home") | visual recipes |
| Brand commitments (optional) | name, voice, assets and identity constraints the owner made binding | visual direction nobody confirmed |
| Constraints | accessibility standard, locales, browsers/devices | aesthetic preferences |

The visual half (`## Visual system`) is written by `document` from shipped code, or seeded by the
owner. Keep the halves separate: no hex values or pixel sizes in product sections.

## Change

Only `interface-context.md` (create it from `assets/interface-context-template.md`).

## Do not touch

- Source code, tokens, an existing visual system section.
- Confirmed facts in an existing file: ask what is stale before reopening anything.

## Steps

1. Read what the repository already says: README, marketing copy, routes, roles, package
   metadata, existing docs. Treat it as a hypothesis, not as the owner's approval.
2. Ask at most three questions per round, only about gaps that change decisions. Start with: who is
   the primary user and what job are they doing; what does this product do that a neighbour
   cannot claim; what constraints and evidence must future work respect.
3. Choose each surface's mode from the visitor's success, not the product category: a developer
   tool's landing page is persuade; a fashion brand's help centre is read.
4. Record undecided facts as decisions owed, not as guesses.
5. Run the linter.

## Verify

```bash
python3 scripts/context_linter.py --input interface-context.md
```

Exit 0. Warnings about vague adjectives get rewritten into specifics before the file is shared.

## Hand-off

`document` to capture the visual system if code exists; otherwise the command the request needs.
