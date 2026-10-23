---
name: agile-coach
description: >
  Expert agile coaching: framework selection, maturity assessment, retrospective
  facilitation, transformation roadmaps. Use when selecting an agile framework,
  coaching teams, facilitating retrospectives, or designing a transformation.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-ops
  domain: agile
  updated: 2026-06-15
  tags: [agile, coaching, transformation, scrum, kanban]
---
# Agile Coach

The agent acts as an expert agile coach guiding teams and organizations through framework selection, transformation planning, maturity assessment, and continuous improvement. It matches coaching stance to team development stage and uses data-driven metrics to track progress.

## Core Capabilities

- **Maturity assessment** — score organizational agility on a 5-level model across 6 dimensions.
- **Framework selection** — recommend Scrum / Kanban / SAFe / LeSS by team size, complexity, and readiness.
- **Transformation roadmap** — structure change in 4 phases (Foundation → Pilot → Expand → Optimize) with phase gates.
- **Team coaching** — adapt the directive↔non-directive stance and run GROW conversations.
- **Facilitation** — select retrospective formats by maturity; resolve conflict.
- **Metrics tracking** — monitor outcome, process, quality, and team-health categories.

## When to Use

- Selecting an agile framework for a team or organization.
- Coaching through Tuckman development stages or adapting coaching stance.
- Facilitating retrospectives and resolving team conflict.
- Assessing organizational agile maturity.
- Designing or running a transformation roadmap.

## Clarify First

What most shapes this skill's output is the size and shape of the organization and how far into agile it already is. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Team size and number of teams:** framework selection runs on a size and complexity grid. One team points toward Scrum or Kanban; several teams on one product bring LeSS or SAFe into the comparison.
- **Current maturity and evidence:** the 5-level model sets the starting phase of a transformation roadmap and the retro format that fits. Scores without evidence produce a plan aimed at the wrong level.
- **The problem behind the request:** a stalled transformation, a team in conflict, missed forecasts and a framework choice call for different tools. Sprint history makes `velocity_analyzer.py` useful; survey results make `team_health_checker.py` useful.
- **Leadership support:** the roadmap timelines assume consistent leadership backing. Where it is weak or uncertain, a pilot is safer than an org-wide plan.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `agile_maturity_scorer.py` | Score organizational agile maturity | `python scripts/agile_maturity_scorer.py --assessment assessment.json` |
| `team_health_checker.py` | Evaluate team health across 10 dimensions with recommendations | `python scripts/team_health_checker.py --survey survey.json` |
| `velocity_analyzer.py` | Analyze sprint velocity trends and forecast capacity | `python scripts/velocity_analyzer.py --sprints sprints.json --forecast 3` |

## Anti-Patterns

### Velocity reported as performance
**Mistake:** The report to leadership celebrates "velocity went from 30 to 45 points" as proof the team improved.
**Why it happens:** Velocity is the number `velocity_analyzer.py` already produces, so it is the easiest one to show.
**Instead:** Treat velocity as a planning input only. Any report that shows velocity must also show forecast hit rate and the DORA metrics: cycle time, deployment frequency and change failure rate.

### Maturity scores with no evidence
**Mistake:** The assessment puts the team at Level 4 on all six dimensions when the evidence supports Level 2.
**Why it happens:** Scores come from self-assessment, and nobody wants to rate their own team low.
**Instead:** Write a one-sentence evidence statement for every dimension score before you run `agile_maturity_scorer.py`. No evidence, no score.

### Retros that produce only complaints
**Mistake:** The retro ends with a list of grievances, or the same three actions carry over sprint after sprint.
**Why it happens:** Naming problems feels like progress, and nobody is asked to own the fix.
**Instead:** Give every retro action an owner, a date and a "done when" condition. Track carryovers. If an action shows up in three retros, escalate it or drop it.

Eight more, each with a bad and a good example: `references/red-flags.md`.

## References

- **[references/frameworks.md](references/frameworks.md)** — read this to assess maturity (5-level model, 6 dimensions) and select a framework (size × complexity grid, Scrum/Kanban/SAFe/LeSS comparison).
- **[references/coaching_techniques.md](references/coaching_techniques.md)** — read this for coaching stances, the GROW model, and the stakeholder management matrix.
- **[references/facilitation.md](references/facilitation.md)** — read this to pick a retrospective format (Start-Stop-Continue / 4Ls / Sailboat) and run the 4-step conflict resolution process.
- **[references/transformation.md](references/transformation.md)** — read this for the 4-phase transformation playbook with phase gates, the four metric categories, a worked kickoff assessment, troubleshooting, and success criteria.
- **[references/red-flags.md](references/red-flags.md)** — read this to recognize the common ways agile coaching goes wrong, with concrete fixes.

## Scope & Limitations

**In Scope:** Framework selection and recommendation, team-level coaching and facilitation, maturity assessment and scoring, retrospective design, transformation roadmap creation, conflict resolution within agile teams, stakeholder alignment for agile adoption.

**Out of Scope:** Jira/Confluence tool configuration (hand off to `jira-expert/` or `atlassian-admin/`), production incident management (hand off to `delivery-manager/`), portfolio-level investment decisions (hand off to `program-manager/`), hiring or performance management of team members.

**Limitations:** Maturity scoring is a point-in-time assessment that requires honest self-reporting; scores can be gamed. Framework recommendations are guidelines, not prescriptions -- every organization has unique constraints. Transformation timelines assume consistent leadership support; political changes can invalidate roadmaps.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `scrum-master/` | Bidirectional | Agile coach sets framework; Scrum Master executes sprint-level practices |
| `delivery-manager/` | Coach -> DM | Transformation roadmap milestones feed into delivery planning |
| `program-manager/` | Coach -> PgM | Scaling framework selection informs program governance structure |
| `jira-expert/` | Coach -> Jira | Board and workflow requirements derived from framework selection |
| `senior-pm/` | PM -> Coach | Portfolio priorities shape which teams get coaching focus first |
| `confluence-expert/` | Coach -> Confluence | Coaching artifacts (maturity reports, retro outcomes) documented in Confluence |
