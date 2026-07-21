---
name: cloud-security
description: >
  Cloud posture security across AWS, Azure, and GCP — IAM least privilege,
  public exposure, encryption, logging coverage, landing-zone guardrails. Use
  when auditing a cloud account, before a production launch, or after a scan.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: cloud-security
  updated: 2026-07-21
  tags: [cloud-security, iam, least-privilege, landing-zone, posture-management]
---

# Cloud Security

Cloud breaches are rarely clever. They are a public bucket, an over-permissive
role, a database on an open security group, and no audit log to reconstruct
what happened. This skill covers **cloud posture** specifically: the
configuration of identity, network exposure, encryption, detection coverage,
and multi-account guardrails across AWS, Azure, and GCP.

**Scope boundary.** This skill is deliberately narrow so it does not overlap
its neighbours in `engineering/`. It does **not** cover application-code
vulnerabilities, dependency CVEs, or compliance-framework mapping — that is
`senior-secops`. It does **not** cover log analysis and intrusion signals —
that is `threat-detection`. It does **not** cover offensive engagement planning
or rules of engagement — that is `red-team`. It does **not** cover prompt
injection, model extraction, or ML-pipeline threats — that is `ai-security`.
What lives here is the posture of the cloud control plane itself: who can do
what, what is reachable, what is encrypted, and what is logged.

## When to use this skill

- A cloud account or subscription is about to hold production customer data for the first time
- An IAM sprawl problem has accumulated and nobody knows which roles are actually admin
- A posture scanner produced hundreds of findings and the team needs a defensible priority order
- A new landing zone or multi-account structure is being designed
- A security questionnaire, SOC 2 audit, or customer due-diligence review asks for cloud evidence
- An incident occurred and the review needs to establish what the exposure was and whether logs exist to prove it

## Inputs the skill expects

- An exported resource inventory per account, covering every region (see `assets/inventory_export_guide.md`)
- An IAM principal export with policy statements, trust policies, and last-used data
- Account/subscription/project settings: audit logging, managed detection, org guardrails, log-archive isolation
- Data classification per store — which resources hold confidential, PCI, PHI, or restricted data
- The organization's account topology and which accounts are production
- The decision the review feeds: launch approval, audit evidence, or remediation backlog

## Clarify First

Before running the review, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which accounts hold production or classified data** — decides review scope and which findings are launch-blocking rather than backlog
- [ ] **Data classification of the stores in scope** — promotes unencrypted and un-logged findings from high to critical; without it every severity is a guess
- [ ] **Whether the exports cover all regions** — a region-scoped export reliably misses the forgotten test database that becomes the incident
- [ ] **What the output feeds** — a launch gate, an audit evidence pack, or a backlog; changes severity strictness and report format

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Audit posture across an account

1. Export the resource inventory for **every region**, normalizing to the
   schema in `assets/inventory_export_guide.md`. Include account-level settings.
2. Populate `tags.data_classification` on data stores before scanning —
   severity depends on it, and an unclassified store defaults to the
   lower band.
3. Run the auditor, reading critical findings before the score.
4. For each critical, answer explicitly: is it reachable from the internet
   right now, and what data sits behind it.
5. Group findings into classes and name the preventive guardrail for each class
   rather than ticketing every instance.

```bash
python3 engineering/cloud-security/scripts/posture_auditor.py \
  --input engineering/cloud-security/assets/sample_inventory.json \
  --min-severity high --fail-on critical
```

### Workflow 2 — Review IAM for least privilege and escalation paths

1. Export principals with their policy statements, trust policies, MFA state,
   and last-used data. Populate `trust.approved` with your own account IDs.
2. Run the review and read the escalation paths first — they convert a
   mid-privilege identity into an admin and outrank raw wildcard counts.
3. Work the principal risk ranking top-down; for each high-tier principal,
   derive the replacement policy from 90 days of actual usage, never from what
   the owning team believes it needs.
4. Disable stale principals for one cycle before deleting, so breakage surfaces
   as a report rather than an outage.

```bash
python3 engineering/cloud-security/scripts/iam_least_privilege.py \
  --input engineering/cloud-security/assets/sample_iam_export.json \
  --stale-days 90 --min-severity high --fail-on critical
```

### Workflow 3 — Convert findings into landing-zone guardrails

1. Run both tools with `--format json` and count findings by class, not by instance.
2. For any class appearing three or more times, stop remediating instances and
   write the preventive control from
   `references/landing-zone-and-guardrails.md` §3.
3. Apply each guardrail to the Dev OU for two weeks before production, with a
   documented exception path and an owner.
4. Re-scan at 30 days and report the **delta**, not the absolute count —
   absolute counts move with inventory growth and demoralize the team.

```bash
python3 engineering/cloud-security/scripts/posture_auditor.py \
  --input engineering/cloud-security/assets/sample_inventory.json \
  --format json > /tmp/posture.json

python3 engineering/cloud-security/scripts/iam_least_privilege.py \
  --input engineering/cloud-security/assets/sample_iam_export.json \
  --format json > /tmp/iam.json
```

## Decision frameworks

### Severity calibration

| Severity | Definition | Examples |
|----------|------------|----------|
| **Critical** | Direct path to data exposure or account takeover, exploitable now | Public store holding classified data; admin port open to the internet; `*:*` on `*`; wildcard role trust; control-plane audit logging off |
| **High** | Significant weakening, exploitable with one further step | Service-wide wildcard grant; unencrypted classified store; no backups on a primary store; log archive not isolated; human without MFA |
| **Medium** | Defence-in-depth or detection gap | Data-plane access logs off; no permission boundary on a privileged principal; provider-managed keys on classified data |
| **Low** | Governance hygiene | Missing owner or classification tags |

Gate on critical **count**, never on the aggregate score. Ten lows can drag a
score below a threshold while one public database sits unremarked.

### Where to spend the next two weeks

| Current state | Highest-return move | Why |
|---------------|--------------------|-----|
| No org-wide audit logging | [PROVEN] Enable it to a separate account first | Nothing else is provable without it; an attacker in the workload account can otherwise erase the evidence |
| Audit logging present, no guardrails | [PROVEN] Deploy the four day-one denies: public storage, log tampering, detection tampering, region restriction | Each one permanently deletes a finding class instead of a finding |
| Guardrails present, static keys everywhere | [RECOMMENDED] Migrate to workload identity federation | Static keys are the most commonly leaked credential and the hardest to rotate under pressure |
| Everything above done | [RECOMMENDED] Data-plane logging on classified stores | Decides whether a breach notification names 12 records or assumes all four million |
| Mature posture | [EXPERIMENTAL] Just-in-time privilege elevation | Removes standing admin entirely; risk is that a broken elevation path blocks incident response, so keep an audited break-glass role |

### Preventive beats detective

| Layer | Latency to protection | Use for |
|-------|-----------------------|---------|
| Preventive (SCP / org policy / deny assignment) | Instant, always | Any finding class seen three or more times |
| Proactive (policy-as-code in CI on the IaC plan) | Minutes | Everything expressible in Terraform, before merge |
| Detective (this skill's scanners, managed detection) | Hours to days | Backstop for console changes and drift |
| Responsive (auto-remediation) | Minutes to hours | Only where the preventive control would be too blunt |

## Anti-Patterns

### Ranking findings by wildcard count
**Mistake:** The IAM review sorts by how many `*` characters appear in each policy, and the team spends a quarter tightening `s3:*` grants on single buckets.
**Why it happens:** Wildcards are trivially greppable, so they become the metric, and tightening them produces a satisfying downward chart.
**Instead:** Hunt privilege-escalation paths first. A tidy-looking policy with 40 scoped actions that happens to include `iam:PassRole` plus `ec2:RunInstances` is full account takeover; a sloppy `s3:*` on one non-sensitive bucket is not. `iam_least_privilege.py` reports escalation paths as critical for exactly this reason.

### Treating the posture score as the gate
**Mistake:** The release check is "posture score above 80," so the team closes twenty low-severity tag findings to clear the bar.
**Why it happens:** A single number is easy to put on a dashboard and easy to trend, and the low findings are genuinely the cheapest to close.
**Instead:** Gate on critical count and on the specific finding classes that map to data exposure. Use the score only to trend across reviews of the same scope. The sample inventory here scores 0/100, and the number that matters is that five criticals include a publicly readable bucket of customer exports.

### Remediating instances instead of writing the guardrail
**Mistake:** Each scan finds new public buckets; each one gets a ticket, gets fixed, and reappears next quarter from a different team.
**Why it happens:** Ticketing an instance takes ten minutes and closing it feels like progress; writing an org policy requires a conversation with every team that might be blocked by it.
**Instead:** The third time a finding class appears, stop remediating and write the preventive control. Public buckets found three times means account-level public access prevention is missing. Apply it to Dev for two weeks with a named exception path, then production.

### Leaving the log archive inside the workload account
**Mistake:** CloudTrail or the diagnostic settings write to a bucket in the same account they monitor.
**Why it happens:** It is the default when you enable logging from the console, and the separation looks like bureaucratic account sprawl.
**Instead:** Put the log archive in a dedicated account with no workload administrators and write-only access from everywhere else. The entire value of audit logging is that it survives the compromise of the thing it audits — an attacker with account admin deletes in-account logs as step two, and your incident timeline starts and ends with "we do not know."

### Scanning one region
**Mistake:** The export script runs against the default region and reports a clean account.
**Why it happens:** Every provider CLI defaults to a single region, and the code that loops over regions is one more thing to write.
**Instead:** Enumerate regions and export all of them, then apply a region-restriction guardrail so the surface stops growing. The forgotten test database in an unused region — unencrypted, unlogged, open to 0.0.0.0/0 because it was "just for a demo" — is the single most common origin of cloud incidents in organizations that otherwise scan diligently.

## Files

| File | Purpose |
|------|---------|
| `scripts/posture_auditor.py` | Audits a normalized cloud inventory for public exposure, open ingress, unencrypted stores, missing logging, absent backups, and account guardrail gaps; severity-scored with provider-specific remediation |
| `scripts/iam_least_privilege.py` | Reviews IAM principals for wildcard grants, privilege-escalation paths, over-broad trust, stale credentials, and missing MFA; ranks principals by risk with an effective-privilege tier |
| `scripts/posture_rules.py` | Rule data behind the posture auditor — severity weights, sensitive-port and data-store vocabularies, account-level guardrail checks, and the provider-specific remediation catalog; `--list-rules` prints them |
| `scripts/iam_rules.py` | Rule data behind the IAM review — severity weights, admin-grant and write-verb vocabularies, the privilege-escalation path catalog, and the policy-flattening and privilege-tier primitives; `--list-rules` prints them |
| `references/cloud-control-catalog.md` | Controls mapped across AWS/Azure/GCP for identity, network, encryption, logging, and resilience, with passing thresholds and severity calibration |
| `references/landing-zone-and-guardrails.md` | Account topology, preventive vs detective controls, the guardrail baseline per provider, and a five-level posture maturity model |
| `assets/sample_inventory.json` | Seven-resource AWS inventory exercising every posture check |
| `assets/sample_iam_export.json` | Six-principal IAM export containing escalation paths, wildcard trust, and stale credentials |
| `assets/posture_review_template.md` | Review report template structured around decisions rather than finding dumps |
| `assets/inventory_export_guide.md` | Export schemas, field semantics, per-provider collection commands, and export hygiene rules |
