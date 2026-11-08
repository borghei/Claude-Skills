# Glossary Practice

How to build and keep a project glossary that people actually use: what goes in
it, how to write entries, how to pull candidate terms out of conversations and
code, how to settle synonym fights, and how to handle words that mean different
things in different parts of the system.

## Contents

- [Why a glossary pays for itself](#why-a-glossary-pays-for-itself)
- [What belongs and what does not](#what-belongs-and-what-does-not)
- [Writing an entry](#writing-an-entry)
- [Extracting terms](#extracting-terms)
- [Resolving synonym conflicts](#resolving-synonym-conflicts)
- [Probing a term with scenarios](#probing-a-term-with-scenarios)
- [Several contexts in one system](#several-contexts-in-one-system)
- [Keeping it alive](#keeping-it-alive)

## Why a glossary pays for itself

Most expensive misunderstandings in software are not technical: one person says
"account" meaning the paying organisation, another hears the login. Code then
grows a field, a table and an API around the wrong meaning, and the mistake
surfaces months later as a data migration. A glossary is the cheapest place to
catch this, because arguing about one sentence costs minutes.

The second payoff is naming. When the glossary says **Subscription**, the class,
the table, the API resource, the UI label and the support macro can all say
Subscription, and searches for the concept find every place it lives.

## What belongs and what does not

| Belongs | Does not belong |
|---------|-----------------|
| Nouns the business uses with a specific meaning here: Subscription, Seat, Grace period | Generic engineering words: cache, retry, timeout, queue, DTO |
| States and events that carry rules: Suspended, Cancellation, Renewal | Implementation names: `sub_status_v2`, `InvoiceManagerImpl` |
| Distinctions people get wrong: Pause vs Suspension | Everyday words used in their normal sense |
| Terms whose meaning was argued about and settled | Specifications, acceptance criteria, data formats |

Test for any candidate: would two people in this organisation plausibly mean
different things by it, or would a new hire need it explained? If neither, leave
it out.

## Writing an entry

```markdown
### Grace period
**Definition:** The days after a failed Charge during which the Customer keeps full access while payment is retried.
**Avoid:** Dunning window, Overdue period
**Owner:** Billing product lead
**Related:** Charge, Suspension
**Status:** agreed
```

Rules, each enforced or hinted by `glossary_lint.py`:

- **Definition says what it is**, in business language, in at most two sentences (default budget 45 words). Behaviour and rules can follow from the definition, but storage does not belong: no tables, columns, classes, endpoints or flags.
- **Do not define a term with itself.** "A seat is a seat on a Subscription" teaches nothing.
- **Avoid lists real synonyms**, the ones people say in meetings and type in code. Each alias maps to one canonical term only; an alias that is also a canonical term means two concepts are colliding.
- **Owner is a role** that can settle a dispute — not "everyone", not a team mailing list.
- **Related points only at terms defined here.** A related term that is missing is usually the next entry to write.
- **Status:** `proposed` while still argued, `agreed` once settled, `deprecated` when the concept is retired (keep the entry so old documents can still be read).

## Extracting terms

Sources, in order of yield:

1. **Design conversations and meeting transcripts.** People coin and contest terms out loud.
2. **Support tickets and sales notes.** They show the customer-facing vocabulary — often the source of aliases.
3. **Code identifiers.** Class, table and function names reveal what engineers actually call things.
4. **Existing docs and UI copy.**

Run the extractor over a mix of these:

```bash
python3 scripts/term_extract.py --paths transcripts/ src/billing --glossary GLOSSARY.md
```

Then triage each **new** candidate:

| Decision | When | Action |
|----------|------|--------|
| Add as a term | Domain-specific, recurring, carries a rule or distinction | Draft an entry with status `proposed`; ask the owner to confirm |
| Add as an alias | It is another word for an existing term | Put it under that term's Avoid list |
| Split | One word is being used for two concepts | Create two terms with distinct names; list the shared word as an alias of neither, and note the split in both definitions |
| Ignore | Generic, a person's name, a one-off | Nothing |

Also read the **unused glossary terms** list: a term never used in current
material is either stale (deprecate it) or called something else in practice
(the other name may deserve to win).

## Resolving synonym conflicts

When two words compete for one concept, decide in this order:

1. **Is it really one concept?** Write both definitions. If a scenario exists where one applies and the other does not (a paused Subscription is not suspended), they are two terms.
2. **Which word do customers and contracts use?** External language is the hardest to change; prefer it.
3. **Which word is less overloaded inside the organisation?** "Account" usually loses because it already means login, ledger and customer.
4. **Which word is already in the most code?** Renaming identifiers is cheap per file but expensive across a codebase; it breaks ties, not principles.

Record the result: canonical term as the heading, the losers under Avoid, and —
if the choice was contested and will be questioned again — a short decision
record. Then run `glossary_lint.py --scan` over docs and code to list every
place still using the losing words.

## Probing a term with scenarios

Definitions look fine until an edge case arrives. While settling a term, invent
concrete scenarios that force a boundary decision:

- A Customer pauses, and during the pause a Charge for the previous period fails. Is it a pause, a suspension, or both?
- A Subscription is cancelled on the last day of a period and reinstated the next morning. New Subscription or the same one?
- One Seat is reassigned from one person to another. Is it the same Seat?

Each answer either sharpens a definition or reveals a missing term. When the
answer contradicts what the code does, raise it immediately: either the
language or the code is wrong, and it is cheaper to find out now.

## Several contexts in one system

When one word legitimately means different things in different parts of the
system — "Product" in the catalogue versus "Plan" in billing — do not force a
single definition. Instead:

- Give each context its own `GLOSSARY.md` next to its code.
- Keep a short root `GLOSSARY.md` listing the contexts, where each glossary lives, and the translations between them.
- At the code seam between contexts, translate explicitly (a mapping function or an adapter), so one context's meaning does not leak into the other.

Signals that you need a second context: the same term gets two definitions that
both survive the scenario test, or two teams keep "correcting" each other's use.

## Keeping it alive

- Update the glossary in the same pull request that introduces or renames a concept — not in a later docs pass.
- Add `glossary_lint.py --scan docs/ src/` to the review checklist or a local pre-push hook; exit code 1 means banned aliases slipped in.
- Review `proposed` terms at a fixed cadence (fortnightly is typical) and either agree or drop them.
- Rename code identifiers when you touch a file; do not schedule a big-bang rename unless the old name causes real defects.
