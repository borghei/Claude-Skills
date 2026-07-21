# Tour Construction

Stop selection, ordering models, note-writing patterns, and audience variants. Load
this while authoring a tour; load `tour-maintenance.md` when one has rotted.

---

## 1. Start from the question, not the codebase

A tour without a question has no ordering principle, so it defaults to directory order,
which teaches nothing. Before selecting a single stop, write the question in one line.

Good tour questions are traceable through the code:

- "How does an inbound request become a persisted row?"
- "What happens between a user clicking pay and money moving?"
- "Where would I add a new notification channel?"
- "Why does this service have two caches?"
- "What runs on a deploy, in what order, and what can fail?"

Bad tour questions have no path through the system:

- "How does the codebase work?" — no ordering, no end state
- "What are our architectural patterns?" — a document, not a tour
- "What does each service do?" — a directory listing with prose

The question also gives you a stopping rule. When the reader can answer it, the tour is
over, regardless of how much code remains unvisited.

---

## 2. Selecting stops

`tour_propose.py` ranks candidates by role and fan-in. It finds structure; it cannot
find significance. Expect to keep roughly half its suggestions and add two or three it
could never have seen.

### What the analyzer finds well

| Signal | How | Reliability |
|--------|-----|-------------|
| Entry points | Filename matching (`main.py`, `index.ts`, `cli.py`) | High |
| Config and manifests | Filename matching | High |
| Boundaries | Path and filename tokens (`routes`, `handler`, `client`, `schema`) | Medium |
| Python fan-in | AST import graph | High |
| Other-language fan-in | Filename-reference counting | Low — a ranked shortlist, not a verdict |

### What it cannot find, and you must add

1. **The surprising workaround.** The retry loop that exists because a vendor API
   lies about its status codes. Highest-value stop in most tours, invisible to any
   analyzer.
2. **The load-bearing simplicity.** The module that looks like it could be deleted and
   cannot. Low fan-in, high consequence.
3. **The deliberate absence.** Where a reasonable abstraction was rejected. Explaining
   why prevents the reader from helpfully adding it in month two.
4. **The trap.** The function that looks pure and writes to a global, the config value
   read at import time. These are where new engineers lose a day.
5. **The historical seam.** Where the old system meets the new one, which explains
   half the apparent inconsistency in the codebase.

### What to cut

- Files you can only describe, not explain
- Anything generated, vendored, or mechanically derived
- Tests, unless a test *is* the specification for a subtle behaviour
- Utility modules with no surprising decisions
- Anything the reader will meet naturally in their first task

The cut test: write the note first. If the note comes out as a description of what the
code does, the stop does not belong in the tour.

---

## 3. Ordering models

Three orderings work. Pick one and hold it — mixed ordering is why tours feel
disorienting even when every stop is well chosen.

### Execution order [PROVEN]

Follow one real request, command, or job from entry to completion. The reader's mental
model builds along the same path the data takes, and each stop is verifiable against
the last.

Best for: "how does it work", most onboarding, most services.
Weak for: event-driven systems with no single path, and batch systems where the
interesting behaviour is in the scheduling rather than the processing.

### Constraint-first order [RECOMMENDED]

Start with the thing the system cannot change — an external contract, a schema, a
regulatory requirement, a latency budget — then show how the code accommodates it.

Best for: "why is it designed this way", handoffs of systems whose design looks wrong
without context, and any codebase where the reader's first instinct will be to simplify
something load-bearing.
Weak for: greenfield systems with few real constraints, where it reads as ceremony.

### Change-shaped order [RECOMMENDED]

Walk the files that a representative recent change touched, in the order the author
touched them. The reader learns the codebase as a place where work happens.

Best for: "how do I add a feature like X", contractors, and anyone whose first task is
already known.
Weak for: understanding the system as a whole — it teaches the path, not the map.

### Ordering test

After each stop, could the reader predict roughly what the next file does? If not, a
stop is missing before it — usually the abstraction that connects them.

---

## 4. Writing the note

Each note answers at least one of three questions. Notes answering none are the most
common tour defect.

| Question | What it gives the reader |
|----------|-------------------------|
| Why does this exist? | Purpose that is not derivable from the code |
| Why this way and not the obvious alternative? | Prevents a well-intentioned regression |
| What breaks if you change it? | Blast radius, which is what they actually need before editing |

### The rewrite pattern

**What-only:** "This function validates the incoming payload and returns a normalized
record with defaults applied."

The reader can see all of that. It costs 20 words and teaches nothing.

**Why:** "Normalization happens here rather than at the API boundary because three
different entry points feed this path, and two of them predate the API. Moving it to
the boundary is the obvious cleanup and it silently breaks the batch importer, which
does not go through the boundary at all."

Same length, and it prevents a specific regression that would otherwise take an
afternoon to diagnose.

### Length and shape

- 50-80 words is the working range. Under 20 cannot carry reasoning; over 120 stops
  being read.
- Lead with the decision, not the context. "Normalization happens here rather than at
  the boundary because…" beats three sentences of setup.
- Name the alternative that was rejected. A decision without its rejected alternative
  reads as arbitrary.
- Use plain causal language — because, rather than, otherwise, which prevents. The
  audit looks for exactly this, because its absence reliably indicates a description
  rather than an explanation.

### Questions and gotchas

The `question` field forces engagement: something the reader can only answer by looking
at the code. "What happens to existing IDs if someone renames a heading?" makes them
trace a function. "Do you understand the parser?" does not.

The `gotcha` field carries the thing that surprises everyone — the silent skip, the
import-time side effect, the parameter that looks optional and is not. One per stop at
most, and only when it is genuinely surprising.

---

## 5. Audience variants

The same system needs different tours for different readers. Rather than one tour with
optional sections, write two short ones.

| Audience | First stop | Emphasis | Stops |
|----------|-----------|----------|-------|
| Junior engineer | Entry point, execution order | Vocabulary, where things live, how to run it | 7-10, smaller steps |
| Senior engineer, new to the team | The constraint or the boundary | Decisions, trade-offs, historical seams | 4-6, larger steps |
| Contractor with a scoped task | The most similar recent change | The path they will touch, and its blast radius | 3-5, narrow |
| SRE or on-call | The observability seam | Failure modes, retries, timeouts, what pages | 5-7 |
| Returning author | The diff since they left | What changed and why | 3-4 |

The senior-engineer tour is the one most often written badly, because authors default
to explaining the basics. A senior reader needs the surprising decisions and can infer
the rest; giving them a vocabulary tour wastes the only hour of attention you get.

---

## 6. Verifying the tour before shipping it

1. **Audit the notes.** `tour_render.py --audit-only --min-why-ratio 0.8`. Fix or cut
   every weak stop.
2. **Validate the anchors.** `tour_validate.py` must report zero broken stops.
3. **Walk it yourself, cold.** Open only the files the tour names, in order, reading
   only the notes. Any point where you rely on knowledge the tour never gave is a gap.
4. **Have someone unfamiliar walk it.** Watch where they scroll away from the stop —
   that is where a stop is missing or a note is too thin.
5. **Check the ending.** Can the reader now answer the tour's question? If not, the
   tour is unfinished regardless of how many stops it has.

Step 4 is the one worth protecting. Every author is blind to their own tour's gaps,
because the missing context is precisely what they already know.
