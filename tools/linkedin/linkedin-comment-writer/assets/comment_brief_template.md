# Comment Brief

Fill this in before drafting. One brief per post. Leave a field blank rather
than guessing — a blank tells the assistant to ask or to choose a question-led
move; a guess ends up in a public comment.

## The post

- **Author:** <name>
- **Role and company:** <role, company>
- **How I know them:** <stranger | peer | prospect | customer | senior colleague | competitor | friend>
- **Post text (pasted in full):**

  > <paste here>

- **The post's claim, in one sentence:** <…>
- **Does it end on a real question?** <yes: quote it | no>

## Comments already there

Paste the ones worth knowing about. They are reference material only.

| Author | What they said |
|--------|----------------|
| <name> | <text> |
| <name> | <text> |

## What I actually have

Only things I have done, measured, or seen. No estimates dressed as results.

- **What I did or saw:** <…>
- **Scale and setting:** <team size, price point, market, period>
- **What changed, with the number if I have one:** <…>
- **What surprised me:** <…>
- **Where it stops being true:** <…>
- **What it cost:** <…>
- **A question I would genuinely like the author to answer:** <…>

## What I want from this comment

- **Aim:** <be recognised by the author | be useful to their readers | correct something | start a conversation with a peer>
- **How far I am willing to disagree:** <not at all | boundary only | openly>
- **Names the comment must not contain:** <my product, my company, clients>

## Drafts

| Id | Move | Text |
|----|------|------|
| A | <field-report \| boundary \| mechanism \| straight-answer \| price-tag \| open-thread \| counter-case \| translation> | <draft> |
| B | <a different move> | <draft> |
| C | <optional third> | <draft> |

## After the linter passes

- [ ] Every figure and date in the chosen draft is mine and accurate
- [ ] One move, and I can name it
- [ ] Nothing I sell is mentioned
- [ ] I would say it to the author's face
- [ ] I have read it aloud once
- [ ] Pasted by me, on: <date> — log it if I want to track the reply

## JSON skeleton for the linter

Save as a `.json` file and pass it with `--input`.

```json
{
  "post": {
    "author": "<author name>",
    "text": "<full post text; use \\n for line breaks>"
  },
  "commenter": {
    "name": "<my name>",
    "own_brands": ["<product>", "<company>"]
  },
  "existing_comments": [
    {"author": "<name>", "text": "<their comment>"}
  ],
  "drafts": [
    {"id": "A", "move": "<move>", "text": "<draft A>"},
    {"id": "B", "move": "<move>", "text": "<draft B>"}
  ]
}
```
