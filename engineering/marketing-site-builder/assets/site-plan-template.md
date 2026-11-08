# Site Plan

Fill this in before writing markup. Lines marked with angle brackets are prompts; replace them.

## 1. Kind and offer

- Kind: <tech | product | service | place>
- What is sold, in one plain sentence: <...>
- Who buys it, and who should look elsewhere: <...>
- The one main action (the transaction): <Book a room | Start a free trial | Order a cake>
- Material in hand: logo <y/n>, photographs <count>, screenshots <count>, prices <y/n>, address <y/n>, hours <y/n>

## 2. Fact sheet

| Field | From the brief (word for word) |
|---|---|
| What it is | |
| For whom / not for whom | |
| What buyers do today instead | |
| The true difference and its proof | |
| Customer words | |
| Numbers and their sources | |
| Odd true details | |
| One limit | |
| The offer | |

Empty fields stay empty. List them here as the client's to supply: <...>

## 3. Voice card

- Register: <technical-dry | plain-service | editorial | local-direct | confident-retail | formal-assured>
- Fences: <exact, not cold>; <sure, not loud>
- Person: <"you" for what the buyer gets, "we" for the work>
- Sentences: <mostly 8 to 16 words; one longer one per section>

## 4. The system

- Spacing scale: <4, 8, 12, 16, 24, 32, 48, 64, 96>
- Radii: <2px controls, 4px frames>
- Ink / muted / grounds / hairline / accent: <#...>
- Display face / text face: <...> / <...>
- Button pair: <primary filled, secondary outline>

## 5. Screens

One line per section: id, its one idea, its picture and the picture's kind (object, use, parts,
people, place, interface, diagram, type, slot), its height in screens (1 or 2; add the tablet count
when it differs), and any motion with its purpose. Three object lines at most; no layout more than
twice; two picture-less sections never side by side.

| # | id | One idea | Picture | Visual kind | Screens | Motion and why |
|---|---|---|---|---|---|---|
| 1 | hero | <category + buyer/place + one hard fact> | <the work itself> | object | 1 | entrance: the name arrives, then the action |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | close + footer | <the main action again, the legal row> | | | 1 | |

## 6. Still to come from the client

- Assumed facts (each marked `data-assumed` on the page): <price, hour, ...>
- Stand-in photographs and client-asset slots: <slot, the file it waits for, the stand-in used>
- Form address (stand-in until supplied): <...>
- Canonical domain: <...>

## 7. Gate log

Run `python3 scripts/finish_gate.py index.html --state .site-gate.json` after each fix round.

| Round | GATE line | FAIL left | Fixed this round |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

Waivers (in `site-waivers.json`): <check, target, reason>
Browser checklist run at: <widths>
