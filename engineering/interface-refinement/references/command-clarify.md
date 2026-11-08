# clarify — interface copy that says what happens

**Job:** rewrite labels, headings, errors, empty states and helper text so people know what
happened, what matters and what to do next, in the product's own terms.

**Run when:** the detector reports `vague-control-label` or `vague-headline`; a critique flags
jargon, generic CTAs or unhelpful errors; before localisation.

## By mode

- **Persuade:** the headline states what the product does for whom; the action names the outcome
  ("Start a free account", "See pricing for 5 seats"), never "Get started" alone.
- **Operate:** labels name verb + object; states and errors are specific and recoverable.
- **Read:** headings answer the reader's question; link text makes sense out of context.

## Change

- **Controls:** verb + object. "Submit" becomes "Send invoice"; "OK" on a delete dialog becomes
  "Delete 3 files". Both the dialog title and the button name the action.
- **Headlines:** replace templates ("Welcome to...", "The all-in-one platform", "Supercharge
  your...") with the product's nouns from the context file's Terms list.
- **Errors:** what failed, why (when known and useful), how to recover. No raw codes as the main
  message; no blame; no jokes when money, data, access or privacy is at stake.
- **Empty states:** tell first use, no results, filtered-out and permission-limited apart, and give
  the next useful action for each.
- **Loading and success:** name the real operation; confirm the outcome briefly; mention a
  consequence only when it changes what the person should do.
- **Forms:** persistent labels (placeholders are examples), requirements stated before submit.

## Do not touch

- Factual claims, legal text, prices and plan names: ask before changing them.
- Domain terms the audience genuinely uses; plain language is not dumbing down.
- Layout and styling. If a rewrite no longer fits, report it to `layout` or `harden`.

## Steps

1. Read the context file's Voice and terms. If there is no glossary, start one with every noun
   and verb the surface uses for the same concept.
2. Walk the whole flow, not isolated strings; copy depends on the moment.
3. For each state decide: the one fact needed now, the next action, context that changes the
   decision, the tone for the stakes.
4. Rewrite. Say each thing once.
5. Keep strings translatable: whole sentences, variables that can move, no concatenated fragments.

## Verify

- Detector `--rules vague-control-label,vague-headline` exits 0 on the target.
- Every button, link and menu item read alone still says what it does.
- Each error string answers what / why / what now.
- German or another long locale (+30%) and 200% zoom do not clip the new strings.
- Accessible names match the visible labels.

## Hand-off

`harden` if strings now overflow at long locales; otherwise `polish`.
