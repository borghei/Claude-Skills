# Workflow Skills - Claude Code Guidance

Cross-domain **process / meta-skills** that improve how you work with the library,
rather than adding domain knowledge. They are orthogonal to the 16 content domains
and multiply their value.

## Skills (2)

| Skill | Type | Purpose |
|-------|------|---------|
| **handoff/** | user-invoked, generative | Package in-progress work into a self-contained context doc so a teammate or fresh agent can continue. Includes `handoff_context.py` (captures git state) + a fill-in template. |
| **skill-router/** | user-invoked, orchestrator | Match a vague/cross-domain intent against the whole catalog and recommend the best-fit skill(s). Reads `cli/skills.json` via `route_skill.py` (deterministic keyword + phrase scoring, no ML). |

## Design notes

- **Two-tier model:** `skill-router` is an *orchestrator* — it recommends, it does not execute. It routes to the target skill (the discipline) which does the work. Keep that separation.
- **Self-contained where possible:** `handoff` is fully standalone. `skill-router` is a navigation aid that depends on the repo-level catalog (`cli/skills.json`), not on other skills — point `route_skill.py --catalog` at it or regenerate with `scripts/build_manifest.py`.
- **Pattern 11:** both skills carry their own `## Clarify First` gate (dogfooding the library standard).
- **Algorithm over AI:** `route_skill.py` ranks by token + multi-word phrase overlap. No embeddings/LLM calls, per the repo principle.

## Adding a workflow skill

Register the domain in `scripts/build_manifest.py` (`DOMAINS` list already includes `workflow`) and rebuild the manifest. Follow `standards/skill-authoring-standard.md`.

---

**Last Updated:** 2026-06-22
**Skills:** 2 (handoff, skill-router)
