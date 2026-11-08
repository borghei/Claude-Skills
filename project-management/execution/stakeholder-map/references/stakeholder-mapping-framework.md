# Stakeholder Mapping — Framework Reference

## 1. Power dimensions

Power comes in many forms beyond hierarchy:

### Hierarchical
- Org chart position
- Reporting relationships
- Direct authority over budget / headcount

### Veto power
- Legal: can block on contractual or regulatory grounds
- Security / CISO: can block on risk grounds
- Privacy / DPO: can block on data grounds
- Compliance: can block on policy grounds
- Finance: can block on budget grounds

These often have *less* hierarchy but *more* veto. Don't underestimate.

### Domain expertise power
- The one person who actually understands the system
- The technical lead who'll implement
- The customer-success rep who knows the customers
- They can't fire you but they can sandbag

### Coalition power
- Influences a faction (their direct reports + cross-functional allies)
- Often middle management with strong informal authority

### External legitimacy power
- Analyst relations (Gartner, Forrester contact)
- Customer reference
- Partner relationship
- Regulator contact

### Information power
- Owns the data others need
- Controls the narrative (PR, comms, IR)
- Has the relationship history (CSM)

## 2. Interest dimensions

Interest = how much the stakeholder cares:

### Outcome impact
- Does it move their team's KPIs?
- Does it affect their P&L?

### Personal stake
- Career risk / reward
- Compensation impact
- Ego / reputation

### Resource impact
- Does it touch their headcount / budget?

### Public visibility
- Will their name be associated?
- Reputational risk?

## 3. Support spectrum

Beyond power × interest, position on:

- **Champion** — actively advocates; rallies others
- **Supporter** — positive; passive support
- **Neutral** — undecided; convertible
- **Skeptic** — has concerns; needs evidence
- **Blocker** — actively opposes; will fight

Champion + Supporter = need to nurture
Neutral = convertible
Skeptic + Blocker = need conversion strategy

## 4. The 2x2 in action

### Quadrant A — Manage closely (HP/HI)
**Profile:** key decision-makers + engaged advocates and skeptics

**Engagement:**
- Weekly 1:1 (you bring updates + asks)
- Co-author key documents
- Veto power respected; used carefully
- They're the "first call" before big moves

**Risks:**
- Over-engaging blockers can paralyze you
- Under-engaging champions wastes leverage

### Quadrant B — Keep satisfied (HP/LI)
**Profile:** powerful but not engaged

**Engagement:**
- Monthly executive briefing
- Pre-brief before major decisions
- Make engagement low-friction (5-min asks)
- Don't surprise

**Risks:**
- Sleeping authority wakes up late and vetoes
- "I would have flagged that if anyone asked" is a common failure

### Quadrant C — Keep informed (LP/HI)
**Profile:** advocates, detractors, implementers, users

**Engagement:**
- Email updates + newsletters
- Open forums (AMA, Slack channel)
- Surface their concerns publicly to show responsiveness

**Risks:**
- Detractors here can build coalitions
- Advocates here can be undervalued

### Quadrant D — Monitor (LP/LI)
**Profile:** tangential parties

**Engagement:**
- Quarterly newsletter; no proactive
- Inclusion in broad announcements

**Risks:**
- Letting position shift unnoticed (LP → HP)

## 5. Engagement cadence templates

| Cadence | Forum | Output |
|---------|-------|--------|
| Daily | Slack channel updates | Status |
| Weekly | 1:1 (HP/HI), team standup, Slack digest | Decisions, blockers |
| Bi-weekly | Steering committee | Decisions, escalations |
| Monthly | Exec brief (HP/LI) | Strategic update |
| Quarterly | Board / all-hands | High-level recap, asks |

## 6. The blocker conversion playbook

For each blocker:

### Step 1 — Understand the actual objection
Stated objections often hide real ones:
- "It's too expensive" → actually "I lose budget control"
- "We tried that before" → actually "I championed the old way; new way embarrasses me"
- "The data doesn't support it" → actually "I don't trust your team"

Probe carefully (often via someone neutral).

### Step 2 — Find evidence that addresses it
- Customer references
- Pilot data
- Industry analyst reports
- Peer company examples

### Step 3 — Find the right messenger
- Their peer (lateral influence)
- Their superior (vertical influence)
- An external authority (analyst, board member)
- A customer they trust

### Step 4 — Time the move
- Pre-brief in 1:1 before public
- Address objection at the right forum (not in front of their boss; not via email)
- Give them a graceful path to support

### Step 5 — Lock in support visibly
- Get explicit verbal agreement
- Note in writing (meeting notes; never quote without permission)
- Surface their support to others

## 7. DACI / RACI cross-cut

After stakeholder mapping, apply decision-rights:

| Role | Definition |
|------|------------|
| **D**river | Owns getting the decision made (often you) |
| **A**pprover | Has authority to approve (1-2 max) |
| **C**ontributor | Provides input; doesn't decide |
| **I**nformed | Notified after decision |

A clean DACI prevents:
- 7 approvers (paralysis)
- 0 approvers (drift)
- Surprised informed parties

See `project-management/execution/daci-framework`.

## 8. Stakeholder map by initiative type

### Product launch
- Eng (build), Design (UX), PM (drive), Marketing (launch), Sales (sell),
  CS (onboard), Support (help), Legal (review), Security (review), Exec
  (approve), Customers (use)

### Pricing change
- Sales (executes), Marketing (positioning), Finance (modeling), Legal
  (contracts), CS (customer comms), Exec (approval), Existing customers
  (impact), Prospects (perception)

### Re-organization
- Affected employees (every one), People Ops (process), Legal, Finance,
  Exec, Department heads, Adjacent teams, External (customers,
  partners), Communications

### Enterprise deal
- Economic buyer, Technical buyer, End users, Executive sponsor, IT,
  Security, Procurement, Legal, Champion (internal advocate)

## 9. Refresh cadence

Stakeholder maps go stale fast:
- Per-initiative: refresh at each phase
- Per-org: review quarterly
- Per major event: re-org, exec hire, pivot — refresh immediately

## 10. Stakeholder map artifacts

For each initiative:

- **Map (2x2 with names)**
- **Engagement plan (per stakeholder; cadence + owner)**
- **Blocker conversion plan (per blocker)**
- **Decision log (DACI per decision)**
- **Communications schedule (what / when / to whom)**

These artifacts live as long as the initiative.

## Appendix: engagement patterns by stakeholder type

_Moved from SKILL.md._

**For executive sponsor (HP/HI):**
- Weekly 1:1 (you bring updates + asks)
- Co-author the strategic narrative
- Defend at board level
- Veto power to be used selectively

**For powerful skeptic (HP/HI, low support):**
- Discover the actual objection (often different than stated)
- Find evidence that addresses it
- Pre-brief before big decisions
- Make their support visible to their peers

**For powerless advocate (LP/HI, high support):**
- Use them to influence others
- Amplify their voice publicly
- Don't burn them with surprise asks

**For powerful absent leader (HP/LI):**
- Don't let them tune in late and veto
- Pre-brief before key decisions
- Make engagement low-friction (5-min readouts)
