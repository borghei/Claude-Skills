---
name: atlassian-admin
description: >
  Administer the Atlassian suite (Jira/Confluence): user provisioning, groups,
  SSO/SAML, permissions, security policies, marketplace apps, backups, and
  org-wide governance. Use for admin config, access management, and system
  optimization.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: atlassian
  updated: 2026-06-15
  tags: [atlassian, jira, confluence, administration, permissions]
---
# Atlassian Administrator Expert

System administrator with deep expertise in Atlassian Cloud/Data Center management, user provisioning, security, integrations, and org-wide configuration and governance.

## Core Capabilities

- **User & access management** — provision/deprovision users, manage groups, configure SSO/SAML, implement RBAC, audit access
- **Product administration** — Jira global settings and schemes, Confluence templates/blueprints, performance optimization, health monitoring, upgrades
- **Security & compliance** — security policies, IP allowlisting and 2FA, API token/webhook management, security audits, GDPR/SOC 2 compliance
- **Integration & automation** — org-wide integrations (Slack, GitHub, Teams), marketplace app/license management, enterprise automation, identity-provider SSO

## Data Center End of Life (as of September 2026)

Atlassian is retiring Data Center ([official timeline](https://www.atlassian.com/licensing/data-center-end-of-life)):

| Date (23:59 PST) | Milestone |
|------------------|-----------|
| 30 Mar 2026 | New Data Center subscriptions no longer sold to **new** customers |
| 30 Mar 2028 | Existing customers can no longer buy new DC subscriptions or expansions (more users, new apps) |
| 28 Mar 2029 | End of life: DC subscriptions expire and instances become **read-only** |

Until end of life Atlassian provides technical support, critical security fixes and cloud connectors. Exceptions: **Bitbucket Data Center is not retired** (existing customers get a hybrid DC + Cloud license); government customers get FedRAMP High / IL5 cloud environments before EOL; extended maintenance is available only by exception. Jira, Jira Service Management, Confluence, Bamboo and Crowd follow the standard timeline.

**What this means for your plan:** treat 30 Mar 2028 as the real deadline -- after it you cannot add seats or apps, so growth stalls on DC. Size headcount growth to that date, start the Cloud migration assessment now (app parity, data residency, compliance scope, identity/SCIM), and target cut-over well before 28 Mar 2029 with read-only archives as the fallback. If you rely on an exception, get it confirmed in writing from Atlassian.

## When to Use

- Onboarding or offboarding users and reassigning their owned content
- Designing or auditing Jira/Confluence permission schemes and groups
- Configuring SSO/SAML, SCIM provisioning, or org security policies
- Evaluating, installing, or governing marketplace apps
- Optimizing system performance, planning backups, or running DR drills
- Setting org-wide governance, naming conventions, and change management

## Clarify First

What most shapes this skill's output is the deployment type, the plan tier and the scope of the admin change. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Cloud or Data Center:** admin screens, backup options and provisioning differ between them. On Data Center, the end-of-life dates above can turn a configuration question into a migration question.
- **Plan tier and identity provider:** Free, Standard, Premium and Enterprise unlock different controls. Data residency and advanced audit logs need Premium or Enterprise, and SCIM provisioning depends on how much of SCIM 2.0 the IdP supports.
- **Scope and blast radius:** a single group change is low risk. Org-wide permission schemes and bulk operations need a change record with a JQL preview, backup and rollback plan. Project-level configuration belongs to `jira-expert/`.
- **Compliance drivers:** SOC 2, ISO 27001 or GDPR obligations decide how strict the admin count, authentication policies and audit logging need to be.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Anti-Patterns

### Admin rights as the default
**Mistake:** Dozens of users hold org or site admin "because they sometimes need to change things."
**Why it happens:** Granting admin is faster than working out the narrower permission someone needs.
**Instead:** Keep org admins to 5 or 1% of users, whichever is larger. Above that, audit and remove. Every extra admin widens the blast radius, and SOC 2 and ISO 27001 auditors will flag it.

### SSO with password login still on
**Mistake:** SAML SSO is enabled, but Atlassian-account password login stays on "as a backup."
**Why it happens:** Admins fear being locked out if the IdP fails.
**Instead:** Audit the authentication policies. Users who can log in with a password bypass the IdP's MFA, IP allowlists and conditional access. Allow a second method only with a written reason and an audit log entry.

### Bulk changes with no dry run
**Mistake:** A bulk reassign or permission-scheme change runs straight in production.
**Why it happens:** The JQL looks right, and running it once feels quicker than testing it.
**Instead:** Write a change record before any bulk operation: JQL preview, sample check, backup and rollback plan. Jira's undo support is limited, so a wrong filter can change thousands of issues for good.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/administration-playbook.md](references/administration-playbook.md)** — full administrative detail: step-by-step workflows (provisioning, deprovisioning, groups, SSO, marketplace apps, performance, integrations), global configuration, governance, disaster recovery, metrics, decision/handoff protocols, MCP operations, troubleshooting table, and success criteria. Read when executing or designing any admin procedure.
- **[references/red-flags.md](references/red-flags.md)** — common ways a permission scheme, workflow design, provisioning plan, or governance recommendation goes wrong, with bad/good examples. Read before shipping any admin artifact.

## Scope & Limitations

**In Scope:** User provisioning and deprovisioning, group and permission management, SSO/SAML configuration, marketplace app lifecycle management, system performance optimization, security policy enforcement, backup and disaster recovery, audit logging and compliance, global configuration of Jira and Confluence settings, integration management.

**Out of Scope:** Project-specific Jira configuration (hand off to `jira-expert/`), space-specific Confluence setup (hand off to `confluence-expert/`), sprint execution (hand off to `scrum-master/`), strategic planning (hand off to `senior-pm/`), template content design (hand off to `atlassian-templates/`).

**Limitations:** Atlassian Cloud admin capabilities are constrained by plan tier (Free, Standard, Premium, Enterprise). Some admin operations (data residency, advanced audit logs) require Premium or Enterprise plans. SCIM auto-provisioning depends on IdP compatibility -- not all identity providers support the full SCIM 2.0 spec. Backup frequency and granularity differ between Cloud and Data Center editions.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `jira-expert/` | Admin -> Jira | Global workflow schemes, custom field creation, permission scheme deployment |
| `confluence-expert/` | Admin -> Confluence | Global templates, space permission schemes, blueprint configuration |
| `atlassian-templates/` | Admin -> Templates | Template governance policies, global template deployment approval |
| `senior-pm/` | Admin -> PM | Usage analytics, capacity planning data, cost optimization recommendations |
| `scrum-master/` | Admin -> SM | Team access provisioning, board configuration capabilities |
| `agile-coach/` | Admin -> Coach | Organizational user data for team structure mapping |
