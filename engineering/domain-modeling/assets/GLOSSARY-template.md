# Glossary — <Context name>

<One or two sentences: which part of the business this language covers and who
uses it. Headings are the canonical terms; anything listed under Avoid should not
appear in new docs, tickets, UI copy or identifiers.>

<!--
Rules for editing this file
- One `### Term` block per concept. The heading is the word everyone should use.
- Definition: what the thing IS, in at most two sentences, in business language.
  No tables, columns, classes, endpoints or flags — those change; the concept does not.
- Avoid: the synonyms people actually say, comma-separated. Each alias maps to exactly one term.
- Owner: the role that settles disputes about the meaning.
- Related: other terms in this file that a reader should look at next.
- Status: agreed | proposed | deprecated. Proposed terms are still being argued about.
- Only terms specific to this domain. Generic engineering words do not belong here.
- Group terms under `## Group` headings once there are more than about ten.
Check with: python3 scripts/glossary_lint.py --glossary GLOSSARY.md --scan docs/ src/
-->

## <Group>

### <Term>
**Definition:** <What it is, in one or two sentences.>
**Avoid:** <Synonym one>, <Synonym two>
**Owner:** <Role>
**Related:** <Other term>
**Status:** proposed

### Order
**Definition:** A Customer's confirmed request to buy one or more products at agreed prices, which can be fulfilled in several Shipments.
**Avoid:** Purchase, Basket, Transaction
**Owner:** Commerce product lead
**Related:** Customer, Shipment
**Status:** agreed

<!--
Multiple contexts: when one word means different things in different parts of the
system (a "Product" in the catalogue vs in billing), give each context its own
GLOSSARY.md next to its code, and keep a short root GLOSSARY.md that lists the
contexts, where each glossary lives, and how terms translate between them:

## Contexts
- Catalogue — src/catalogue/GLOSSARY.md — what is sold and how it is described
- Billing — src/billing/GLOSSARY.md — what is charged and when

## Translations
- Catalogue "Product" -> Billing "Plan" (one Product can be sold as several Plans)
-->
