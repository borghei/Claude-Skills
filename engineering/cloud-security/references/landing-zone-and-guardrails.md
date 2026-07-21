# Landing Zone and Preventive Guardrails

Posture findings are symptoms. The landing zone is the structure that decides
how many of them you generate per quarter. This reference covers account
topology, preventive versus detective controls, guardrail patterns per
provider, and a maturity model for deciding what to build next.

---

## 1. Detective controls do not scale; preventive controls do

Every finding your auditor produces is work someone has to do. A team that
only runs scanners is on a treadmill: engineers create exposure at the rate
they ship, and security removes it at the rate it can nag.

| Control type | Mechanism | Latency to protection | Where it fails |
|--------------|-----------|-----------------------|----------------|
| **Preventive** | Org policy / SCP / deny assignment blocks the action | Instant, always | Blunt — over-broad denials block legitimate work |
| **Proactive** | Policy-as-code in CI on the IaC plan | Minutes | Bypassed by console changes |
| **Detective** | Posture scanner, config rules, managed detection | Hours to days | Finds it after it exists |
| **Responsive** | Auto-remediation on the finding | Minutes to hours | Fights the deploy pipeline that keeps recreating it |

**[PROVEN] Move each recurring finding class up one layer.** The rule: the
third time the same finding class appears, stop remediating instances and write
the preventive control. Public buckets found three times means the org-level
public-access-prevention setting is missing — fix that once and the finding
class disappears permanently.

---

## 2. Account topology

The single-account-with-tags model fails at the first incident, because there
is no boundary to contain a compromise and no way to give a team autonomy
without giving it everything.

**[RECOMMENDED] Separate by blast radius, then by environment, then by team.**

```
Organization root
├── Security OU
│   ├── log-archive          (write-only from everywhere; no workload admins)
│   ├── security-tooling     (scanners, SIEM forwarders, break-glass)
│   └── audit                (read-only cross-account role into everything)
├── Infrastructure OU
│   ├── network-hub          (transit gateway / firewall / DNS)
│   └── shared-services      (CI runners, artifact registries, golden images)
├── Workloads OU
│   ├── Prod OU              (one account per product, per region group)
│   ├── Staging OU
│   └── Dev OU               (looser guardrails, hard spend caps)
└── Sandbox OU               (auto-nuked on a schedule; no data, no VPN peering)
```

Provider mapping: AWS Organizations OUs and accounts; Azure management groups
and subscriptions; GCP folders and projects. The topology is the same.

Rules that make the topology worth having:

1. **The log archive account has no workload administrators.** This is the whole
   point. If the team that can be phished can also delete the evidence, the
   separation is decorative.
2. **Production is a separate account from staging, always.** Not a separate
   VPC, not a separate namespace. Shared IAM in one account means a staging
   credential leak is a production incident.
3. **Sandbox has an expiry.** Untracked sandbox accounts are where the public
   buckets and the forgotten open databases live.
4. **Cross-account access is by role assumption with an external ID for
   vendors** — never by shared static credentials.

---

## 3. The guardrail baseline

These preventive controls should exist before the first workload lands. They
are cheap, they almost never break legitimate work, and each one deletes a
whole finding class.

| Guardrail | AWS (SCP) | Azure (Policy) | GCP (Org Policy) |
|-----------|-----------|----------------|------------------|
| Prevent public object storage | Deny `s3:PutBucketPublicAccessBlock` removal | Deny public blob access | `storage.publicAccessPrevention` |
| Prevent audit-log tampering | Deny `cloudtrail:StopLogging`, `DeleteTrail` | Deny diagnostic-setting deletion | Deny `logging.sinks.delete` on org sink |
| Prevent disabling detection | Deny `guardduty:Delete*`, `config:Delete*` | Deny Defender plan downgrade | Deny SCC service disablement |
| Restrict regions | Deny outside approved regions | Allowed locations policy | `gcp.resourceLocations` |
| Require encryption | Deny unencrypted volume/store creation | Deny unencrypted resources | `constraints/compute.requireOsLogin` + CMEK policy |
| Block root/global-admin use | Deny all actions by root except break-glass | Conditional Access on break-glass | Restrict org admin membership |
| Prevent VPC/network deletion by workloads | Deny network mutation outside network account | Deny NSG changes outside hub | Deny firewall changes outside host project |
| Prevent external service-account keys | — | Deny key creation | `iam.disableServiceAccountKeyCreation` |

**[RECOMMENDED] Deploy the first four on day one, even before the topology is
finished.** They are the ones that map to the finding classes that generate the
most work: public storage, log tampering, detection tampering, and region
sprawl.

### The guardrail failure mode

A guardrail that blocks legitimate work and has no exception path gets removed
in an incident and never comes back. Every deny needs:

- A documented reason tied to a risk, not a framework citation
- A named exception path with an owner and an SLA measured in hours
- A pre-production test — apply to Dev OU for two weeks before Prod

---

## 4. Multi-cloud reality

Most organizations end up with two providers, usually by acquisition rather
than strategy. Two rules:

1. **Do not build a lowest-common-denominator abstraction over both.** The
   control planes are genuinely different, and the abstraction will express
   neither well. Normalize the *findings*, not the *controls* — which is why
   this skill's auditor consumes a normalized inventory and emits
   provider-specific remediation.
2. **Centralize identity, not tooling.** One IdP federating into both providers
   is worth more than one scanner covering both. Identity sprawl across clouds
   is the failure that turns two clouds into two independent breach surfaces.

---

## 5. Posture maturity model

| Level | Identity | Network | Detection | Guardrails | Typical signature |
|-------|----------|---------|-----------|------------|-------------------|
| **0 — Ad hoc** | Shared root credentials, static keys | Flat VPC, admin ports open | None | None | One account, everything in it |
| **1 — Aware** | Individual users, some MFA | Security groups reviewed manually | Managed detection on in one region | None | A spreadsheet of findings nobody closes |
| **2 — Managed** | Federated humans, roles for workloads | Private data stores, bastion-brokered access | Detection all regions, central logging | Baseline denies on public storage and log tampering | Quarterly scan, ticketed remediation |
| **3 — Engineered** | Zero static keys, permission boundaries, access-analyzer-derived policies | Egress controlled, private endpoints everywhere | Data-plane logging on classified stores, findings routed with SLA | Full guardrail baseline, policy-as-code in CI | Findings prevented at PR time; posture scan is a backstop |
| **4 — Continuous** | Just-in-time elevation, session recording | Identity-aware proxy, no standing network trust | Detection tuned to org, mean-time-to-detect measured | Guardrails versioned, tested, and exception-tracked | Posture is an SLO with an error budget |

**Most organizations that believe they are at level 3 are at level 2** — the
distinguishing test is whether a developer can create a public bucket in
production right now. If they can and you would only find out on the next scan,
you are at level 2 regardless of how good the scan is.

### Where to invest next, by level

| Currently at | Highest-return next move |
|--------------|--------------------------|
| 0 | Enable org-wide audit logging to a separate account. Nothing else matters if you cannot reconstruct what happened. |
| 1 | Split production into its own account and federate human identity. |
| 2 | Deploy the four day-one guardrails and eliminate static access keys. |
| 3 | Data-plane logging on classified stores and just-in-time elevation for admin roles. |

---

## 6. Running a posture review that people act on

A review that produces 400 findings produces zero remediation. Structure it so
the output is a short list of decisions.

1. **Scope by blast radius, not by account count.** Review production and the
   accounts holding classified data first.
2. **Export inventory and IAM the same day** so findings correlate — a public
   bucket matters more when a wildcard role can also write to it.
3. **Gate on criticals, rank the rest.** Ship the critical list to engineering
   as incidents with owners; put highs into the normal backlog with dates.
4. **Group findings into classes and name the preventive control for each
   class.** "Twelve unencrypted volumes" is one guardrail, not twelve tickets.
5. **Re-run at 30 days and report the delta, not the absolute count.** Absolute
   counts move with inventory growth and demoralize the team; the delta is the
   only number that reflects the work done.
6. **Track exceptions with expiry dates.** An exception without an expiry is a
   silent policy change.
