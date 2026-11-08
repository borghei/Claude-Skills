# Repo Research Notes

A repo research note is the smallest member of the dossier family: one technical question,
answered from primary sources, written as a cited markdown file and committed next to the
work it informs. Where a dossier briefs a decision-maker on a company or market, a research
note briefs the next engineer, or the next agent, on a fact the code depends on: how an API
behaves at its limits, what a specification actually requires, which version introduced a
behaviour.

Notes live in the repository because that is where the people and agents who need them will
look, and because a fact the code depends on should be reviewed and versioned with the code.

## When to write one

- A design or ticket depends on external behaviour that is easy to get wrong (rate limits, retry semantics, timezone rules, a standard's edge cases).
- The same question has been answered from memory, differently, more than once.
- An agent is about to implement something against a third-party API or specification.
- The answer took real reading to find and would take as long to find again.

Skip it for facts one command or one official page answers in a minute.

## Run it in the background

The reading is the slow part and rarely needs the person asking. Hand the question to a
separate agent session or sub-agent with fresh context, and keep working. Its brief is short:

1. The question, and the decision it unblocks.
2. Where to look first (the vendor's docs site, the spec, the dependency's source tree at the pinned version).
3. The rules below on sources and citations.
4. Where to save the note, and the template to use.
5. A stop condition: if primary sources do not settle it within the time box, write up what is known and list the gap as an open question rather than filling it with secondary claims.

A fresh context matters: an agent that has been discussing the design will look for evidence
for the design. One that starts from the question looks for the answer.

## Sources: primary first

A primary source is the party that owns the behaviour. Follow every claim back to it.

| Claim about | Primary source | Secondary (corroboration only) |
|-------------|----------------|--------------------------------|
| A third-party API | The provider's API reference, changelog, status/incident pages, official SDK source | Blog posts, Q&A sites, tutorials |
| A standard or protocol | The specification text (RFC, W3C, ISO, the standard body's site) | Summaries, cheat sheets |
| A library's behaviour | Its source code at the version you use, release notes, its own docs | Issue comments by non-maintainers |
| Our own system | The code at a named commit, our ADRs, our runbooks | Recollection, chat threads |
| A regulation | The official legal text and the regulator's guidance | Law-firm summaries |

Rules:

- **Cite the version.** Docs change. Record the access date for web pages, the version for libraries and specs, the commit for code.
- **Quote limits exactly.** "Keys are retained for 24 hours" is a fact; "keys last about a day" is a paraphrase that loses the edge case.
- **Secondary sources only corroborate.** If a secondary source is the only support for a claim, the claim goes to Open questions. If it contradicts the primary source, say so and cite both — a widely repeated wrong claim is worth flagging.
- **Read code when docs are silent.** For open-source dependencies, the source at the pinned version settles what docs leave vague. Cite file and commit.

## Writing the note

Use `assets/research_note_template.md`. The structure keeps facts and conclusions apart, using
the same fact/inference discipline as a full dossier:

- **Answer** comes first and answers the question in a few sentences, each claim cited.
- **Findings** are facts, one per bullet, each cited.
- **Inference** holds conclusions drawn from the findings, with the findings they rest on named. No new facts appear there.
- **Open questions** hold what the sources did not settle, with who could settle it.
- **Sources** is a numbered list; inline citations use `[n]`.

## Where to save it

Match the repository's convention. Look for an existing home first: `docs/research/`,
`docs/notes/`, `docs/adr/` (if notes feed decision records), `research/`, or a `notes` folder
next to the module. If there is none, use `docs/research/<topic-slug>.md` and tell the user
where it went, so the convention starts deliberately. Link the note from the spec, ticket or
PR it informs, and from the code comment at the point where the behaviour matters if the
fact is easy to violate.

## Check before committing

Run `scripts/research_note_checker.py --input <note>`. It fails when claims lack citations
above the threshold, when a citation points at no listed source, when secondary sources
dominate, or when the Question, Answer or Sources section is missing; it warns on sources
without a date, version or commit. It does not fetch links — whether a source says what the
note claims is the reviewer's job, so spot-check the citations behind the Answer section.

## Keeping notes alive

A note is a snapshot. Put the date at the top, and when the dependency is upgraded or the
vendor's docs change, re-check the Answer section and either update it or mark the note as
superseded with a link to its replacement. A stale note with a confident answer is worse than
no note.
