# Information Architecture Patterns

How to structure an internal knowledge base so people find things. The failure most
organisations experience is not missing content — it is content that exists and cannot be
found, which is indistinguishable from missing content but costs more to maintain.

---

## The three IA models

### 1. Team-mirrored (structure follows the org chart)

Spaces named after teams: Platform, Growth, Finance, People.

**Works when:** the KB is mostly internal-to-team operating docs and readers already know
which team owns what.

**Fails when:** the org reorganises, which it does. Every reorg orphans a space, and the
content inside becomes unfindable because the readers who need it never learn the new
owner's name. Team-mirrored KBs accumulate archaeological layers named after teams that
no longer exist.

**Verdict:** [RECOMMENDED] only for team-private operating docs. Never for anything a
reader outside the team needs.

### 2. Task-oriented (structure follows what a reader is trying to do)

Top-level sections named as verbs or situations: Onboarding, Shipping a change,
Handling an incident, Getting access, Leaving.

**Works when:** most reads are people trying to complete a task, which describes most
internal knowledge bases most of the time.

**Fails when:** a document serves multiple tasks and has to live in one place. This is
manageable — put it under the dominant task and link from the others.

**Verdict:** [PROVEN] This is the default. If you are choosing an IA and have no strong
reason otherwise, choose this one. It survives reorgs, because tasks change far more slowly
than org charts.

### 3. Lifecycle-oriented (structure follows a process stage)

Sections named for stages: Plan, Build, Ship, Operate, Retire.

**Works when:** the org has one dominant workflow that most people participate in — common
in engineering-heavy or manufacturing organisations.

**Fails when:** functions outside the main workflow (finance, people, legal) have nowhere
natural to sit and end up in a "General" section, which becomes a dumping ground.

**Verdict:** [RECOMMENDED] for engineering-specific sub-spaces inside a task-oriented top level.

---

## Hub-and-spoke structure [PROVEN]

The single structural pattern that most improves findability.

**A hub** is a curated index page for a domain. It is not an auto-generated page tree; it is
a hand-written page that says "here are the eight things you might be trying to do, and the
page for each." It carries a named owner and the Critical freshness SLA.

**Spokes** are the actual content pages. Every spoke is linked from exactly one hub, its
canonical parent, and may be cross-linked from others.

### Rules

1. **Every page has exactly one canonical hub.** A page linked from four hubs and owned by
   none is how duplication starts.
2. **A hub links to 5-12 spokes.** Under 5, the hub is not earning its existence — fold it
   upward. Over 12, readers scan and miss things — split it.
3. **Hubs are maximum two levels deep.** Top-level hub → domain hub → spokes. A third level
   of hub means the taxonomy is doing work the search box should do.
4. **Hub pages get named owners.** They are the highest-traffic, highest-leverage pages in
   the KB and the most commonly unowned.

### Detecting a broken hub structure

Run the orphan detector. If connectivity is under 60%, the hub layer is missing or stale —
pages exist but are not indexed by anything. If a single page has 20+ inbound links, it is an
accidental hub that grew by accretion and probably needs splitting.

---

## Naming

Page titles are the primary search surface. Most search failures are naming failures.

| Rule | Bad | Good |
|------|-----|------|
| Name for the reader's question, not the author's topic | "VPN Architecture" | "Reset your VPN certificate" |
| Front-load the distinguishing word | "Guide to deploying services" | "Deploying services: guide" |
| Never use internal project codenames alone | "Project Halyard" | "Billing migration (Project Halyard)" |
| Avoid "Overview", "Guide", "Documentation" as the whole title | "Overview" | "Payments system overview" |
| One canonical name per concept | "Sev-1" / "P1" / "Critical incident" | Pick one, alias the others |

### The codename tax

Internal codenames are the most expensive naming decision an organisation makes and the one
made most casually. A newcomer cannot search for a codename they have never heard. Every
codenamed page needs the plain-English term in the title, not just in the body — search
weights titles far more heavily than body text.

---

## Designing for how people actually search

Three behaviours, in descending order of frequency:

1. **Known-item search (60-70%).** The reader knows the page exists and is retrieving it.
   Optimised by stable titles and stable URLs. This is why redirecting rather than deleting
   matters — a moved page breaks every bookmark and every past chat link.

2. **Exploratory search (20-30%).** The reader knows their problem but not the page.
   Optimised by hub pages and by titles phrased as questions or tasks.

3. **Browse (5-15%).** The reader is navigating the tree. Optimised by the IA itself. This is
   the rarest behaviour and the one organisations spend the most time optimising — an
   inversion worth correcting.

### Practical consequences

- **Exclude archives from the search index.** This is usually the single largest search-quality
  improvement available, and it costs a configuration change.
- **Never let two live pages carry the same title.** The engine cannot rank between them
  meaningfully, and the reader cannot tell which is current.
- **Put the answer in the first 200 words.** Search result snippets come from the top of the
  page; a page that opens with background context shows a useless snippet.
- **Date-stamp visibly at the top.** Readers use the date to decide whether to trust the page
  before they read it. A page with a visible recent date gets trusted; the same content
  undated gets verified in chat instead.

---

## Page-level structure

The template that works across doc types:

1. **Title** — the reader's question
2. **Status line** — owner, last reviewed, tier. Visible, at the top, not in a footer
3. **Answer / summary** — 2-4 sentences. What this page tells you, resolved immediately
4. **Prerequisites**, if any
5. **Body** — steps, or the explanation
6. **When this does not apply** — the section most often omitted and most often needed
7. **Related pages** — 3-5 links, curated, not auto-generated

The "when this does not apply" section is what converts a page from a recipe into usable
knowledge. Its absence is why readers ask in chat even when the page exists: they cannot tell
whether their situation is the one the page covers.

---

## Migration between platforms

When moving wikis, the temptation is a lift-and-shift because it is fast and lossless. Do not.

A migration is the only moment when deleting large volumes of content is politically free —
"it did not come across" carries none of the accountability that "I deleted it" does. Use it.

**Migration filter:** carry over any page with (a) inbound links from a hub, or (b) non-trivial
traffic in the last 180 days, or (c) a compliance retention requirement. Everything else stays
behind, with the old wiki kept read-only for two quarters. In practice this moves 30-50% of
pages and no one notices the rest are gone — which is itself the strongest possible evidence
they should not have been carried.

---

## Permissions and visibility

Access control is an IA decision that gets made as a security decision, usually by defaulting
to restrictive, and it silently destroys findability.

### The default

**Open by default within the company; restrict by exception.** A page nobody outside the owning
team can see is a page that will be rewritten by another team who could not find it — this is a
primary mechanism by which duplication is created.

### Genuine exceptions

Compensation and individual performance data; pre-announcement M&A and restructuring material;
security incident detail during an active incident; customer data under contractual restriction;
material non-public information at listed companies; some regulated records.

That list is short, and most organisations restrict five to ten times more than it justifies.

### The findability failure restriction causes

A restricted page is invisible in search results for people without access — which is correct
security behaviour and terrible IA behaviour, because the reader cannot tell the difference
between "does not exist" and "exists but is not for me." They conclude the former and write
their own version.

**Fix:** where the platform supports it, show restricted pages in search as a title plus a
request-access route. Where it does not, keep a visible stub page in the open space naming
the restricted material and who to ask. The existence of a document is very rarely the secret.

### Permission decay

Access granted for a project outlives the project. Review group membership on restricted spaces
annually — it belongs in the same cycle as the access review in your security tier. Spaces whose
membership only ever grows are functionally open with extra friction, which is the worst of both
arrangements.

---

## Renaming and restructuring safely

Retitling and moving pages improves findability and breaks every bookmark and chat link
pointing at them. Both are true, and the second is what stops teams doing the first.

### Rules

1. **Always redirect.** A 404 on a bookmarked page costs more trust than the bad title did.
   If the platform cannot redirect, leave a stub with a link and a date.
2. **Never rename and move in the same change.** If something breaks you will not know which
   action caused it, and the recovery is much harder.
3. **Rename in batches by domain**, announced to that domain, rather than continuously. A
   quiet rolling rename programme feels to users like the wiki is unstable.
4. **Retire stubs after two quarters**, not sooner. Traffic to a redirect stub tells you
   whether anyone still holds the old link; retiring while that traffic is non-trivial breaks
   real users.

### Handling codename migrations

Moving from a codename to a plain-English title is the highest-value rename available and the
one that generates the most objection, because the codename is what the building team calls it.

Resolve with a compound title: **"Billing migration (Project Halyard)"**. Both populations
search successfully, the plain term carries the search weight, and nobody has to give up their
vocabulary. This is worth doing even when the team insists the codename is universally known —
it is universally known to the people already in the room.
