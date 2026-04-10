# Legal Canned Response Templates

Complete template library for 7 legal response categories with sub-types, variables, and follow-up actions.

## Table of Contents

- [Template Standards](#template-standards)
- [Category 1: Data Subject Requests](#category-1-data-subject-requests)
- [Category 2: Discovery and Litigation Holds](#category-2-discovery-and-litigation-holds)
- [Category 3: Privacy Inquiries](#category-3-privacy-inquiries)
- [Category 4: Vendor Legal Questions](#category-4-vendor-legal-questions)
- [Category 5: NDA Requests](#category-5-nda-requests)
- [Category 6: Subpoena and Legal Process](#category-6-subpoena-and-legal-process)
- [Category 7: Insurance Notifications](#category-7-insurance-notifications)
- [Template Lifecycle](#template-lifecycle)

## Template Standards

| Standard | Requirement |
|----------|-------------|
| Tone | Professional, neutral, legally precise |
| Caveats | Include appropriate legal disclaimers where needed |
| Variables | All organization-specific details use {variable_name} placeholders |
| Privilege | Discovery and subpoena templates marked PRIVILEGED AND CONFIDENTIAL |
| Review | All templates require periodic counsel review |
| Versioning | Track template version and last review date |

## Category 1: Data Subject Requests

### 1.1 Acknowledgment

| Field | Value |
|-------|-------|
| Use case | New data subject request received |
| Required variables | requestor_name, request_date, request_type, ref_number |
| Follow-up | Verify identity within 5 business days; set 30-day deadline |
| Escalation triggers | Minor, litigation hold conflict, special category data |

**Template:**

> Dear {requestor_name},
>
> We acknowledge receipt of your data subject request submitted on {request_date}. Your request for {request_type} has been logged and assigned reference number {ref_number}.
>
> We will respond within the timeframe required by applicable data protection law (generally 30 days from receipt). If we require additional time, we will notify you of any extension and the reasons for it.
>
> Before processing, we may need to verify your identity. If so, we will contact you with further instructions.
>
> Regards, {sender_name}

### 1.2 Verification

| Field | Value |
|-------|-------|
| Use case | Identity verification needed before processing |
| Required variables | requestor_name, ref_number, verification_method |
| Follow-up | Track 14-day verification deadline; pause response timeline |

### 1.3 Fulfillment

| Field | Value |
|-------|-------|
| Use case | Request completed and data/action being communicated |
| Required variables | requestor_name, request_type, ref_number, data_description |
| Follow-up | Close request in tracker; archive for audit trail |

### 1.4 Denial

| Field | Value |
|-------|-------|
| Use case | Request denied with lawful reason |
| Required variables | requestor_name, request_type, ref_number, denial_reason |
| Follow-up | Document rationale; prepare for potential supervisory authority complaint |

### 1.5 Extension

| Field | Value |
|-------|-------|
| Use case | Additional time needed to fulfill request |
| Required variables | requestor_name, request_type, ref_number, extension_reason, new_deadline |
| Follow-up | Update tracking system; set new deadline reminder |

## Category 2: Discovery and Litigation Holds

All discovery templates are marked **PRIVILEGED AND CONFIDENTIAL** and **ATTORNEY-CLIENT COMMUNICATION**.

### 2.1 Initial Hold Notice

| Field | Value |
|-------|-------|
| Use case | New litigation hold issued to custodians |
| Required variables | matter_name, custodians, notice_date, data_types |
| Follow-up | Track custodian acknowledgments; 7-day reminder; document scope |
| Privilege | YES |

**Template:**

> PRIVILEGED AND CONFIDENTIAL
> ATTORNEY-CLIENT COMMUNICATION
>
> TO: {custodians}
> RE: Litigation Hold - {matter_name}
>
> This notice requires you to preserve all documents, communications, and data related to {matter_name}. This includes emails, documents, calendar entries, voicemails, and all ESI.
>
> YOU MUST: (1) Cease routine deletion, (2) Suspend auto-delete policies, (3) Preserve all relevant documents, (4) Notify team members with relevant information.
>
> DO NOT delete, modify, or move any potentially relevant documents.

### 2.2 Hold Reminder

| Field | Value |
|-------|-------|
| Use case | Periodic reminder of active hold obligations |
| Required variables | matter_name, reminder_number |
| Follow-up | Log reminder; track acknowledgments; schedule next |
| Privilege | YES |

### 2.3 Hold Modification

| Field | Value |
|-------|-------|
| Use case | Scope of hold changed (expanded or narrowed) |
| Required variables | matter_name, modification_description |
| Follow-up | Update scope documentation; track acknowledgments |
| Privilege | YES |

### 2.4 Hold Release

| Field | Value |
|-------|-------|
| Use case | Hold no longer required; custodians may resume normal policies |
| Required variables | matter_name, release_date |
| Follow-up | Close hold in tracker; verify no other active holds |
| Privilege | YES |

## Category 3: Privacy Inquiries

### 3.1 Cookies

| Field | Value |
|-------|-------|
| Use case | General inquiry about cookie practices |
| Required variables | requestor_name, cookie_policy_url |
| Follow-up | Log inquiry for privacy metrics |

### 3.2 Data Sharing

| Field | Value |
|-------|-------|
| Use case | Question about who receives personal data |
| Required variables | requestor_name, sharing_details, privacy_notice_url |
| Follow-up | Log inquiry; review if suggests process gap |

### 3.3 Children's Privacy

| Field | Value |
|-------|-------|
| Use case | Concern about data collection from children |
| Required variables | requestor_name, age_threshold, privacy_email |
| Follow-up | Investigate if specific child data concern raised |
| Escalation | ALWAYS escalate if specific child identified |

### 3.4 International Transfers

| Field | Value |
|-------|-------|
| Use case | Question about cross-border data transfers |
| Required variables | requestor_name, origin_jurisdiction, transfer_mechanism |
| Follow-up | Log inquiry; verify transfer mechanisms current |

## Category 4: Vendor Legal Questions

### 4.1 Contract Status

| Field | Value |
|-------|-------|
| Use case | Internal inquiry about vendor contract status |
| Required variables | requestor_name, vendor_name, contract_status, contract_ref |
| Follow-up | Update contract tracking if needed |

### 4.2 Amendments

| Field | Value |
|-------|-------|
| Use case | Request to amend existing vendor agreement |
| Required variables | requestor_name, vendor_name, contract_ref, amendment_description, review_timeline |
| Follow-up | Assign to contract attorney; set review deadline |

### 4.3 Certifications

| Field | Value |
|-------|-------|
| Use case | Request for vendor compliance certifications |
| Required variables | requestor_name, vendor_name, certification_details, submission_email, deadline |
| Follow-up | Track submission deadline; verify upon receipt |

### 4.4 Audit

| Field | Value |
|-------|-------|
| Use case | Scheduling contractual audit of vendor |
| Required variables | requestor_name, vendor_name, contract_ref, audit_scope, audit_dates |
| Follow-up | Confirm audit dates; prepare checklist |

## Category 5: NDA Requests

### 5.1 Standard Form

| Field | Value |
|-------|-------|
| Use case | Sending standard NDA for execution |
| Required variables | requestor_name, counterparty, purpose, nda_type, term |
| Follow-up | Track execution; set signature deadline |

### 5.2 Counterparty Markup

| Field | Value |
|-------|-------|
| Use case | Responding to counterparty's changes to NDA |
| Required variables | requestor_name, counterparty, markup_comments |
| Follow-up | Schedule negotiation if needed; track versions |

### 5.3 Decline

| Field | Value |
|-------|-------|
| Use case | Declining to enter NDA |
| Required variables | requestor_name, counterparty, decline_reason |
| Follow-up | Document reason; notify business stakeholder |

### 5.4 Renewal

| Field | Value |
|-------|-------|
| Use case | NDA approaching expiration |
| Required variables | requestor_name, counterparty, nda_ref, expiry_date |
| Follow-up | Track renewal decision; set expiry reminder |

## Category 6: Subpoena and Legal Process

**ALL subpoena templates are marked FOR COUNSEL REVIEW ONLY and ALWAYS require escalation.**

### 6.1 Acknowledgment

| Field | Value |
|-------|-------|
| Use case | Subpoena received and logged |
| Required variables | requestor_name, matter_name, service_date, response_deadline, issuing_party |
| Follow-up | IMMEDIATE route to counsel; calendar deadline; identify responsive docs |
| Escalation | ALWAYS |
| Privilege | YES |

### 6.2 Objection

| Field | Value |
|-------|-------|
| Use case | Raising objections to subpoena |
| Required variables | matter_name, objection_grounds |
| Follow-up | Counsel review mandatory; file by deadline |
| Escalation | ALWAYS |
| Privilege | YES |

### 6.3 Extension

| Field | Value |
|-------|-------|
| Use case | Requesting more time to respond |
| Required variables | matter_name, current_deadline, requested_deadline, extension_reason |
| Follow-up | Counsel approval required; track response |
| Escalation | ALWAYS |
| Privilege | YES |

### 6.4 Compliance

| Field | Value |
|-------|-------|
| Use case | Producing responsive documents |
| Required variables | matter_name, production_summary, privilege_status |
| Follow-up | Counsel approval mandatory; prepare privilege log |
| Escalation | ALWAYS |
| Privilege | YES |

## Category 7: Insurance Notifications

### 7.1 Initial Claim

| Field | Value |
|-------|-------|
| Use case | First notification to insurance carrier |
| Required variables | requestor_name, claim_type, occurrence_date, claim_description, policy_number |
| Follow-up | Track carrier acknowledgment; gather supporting docs |

### 7.2 Supplemental Information

| Field | Value |
|-------|-------|
| Use case | Providing additional information on existing claim |
| Required variables | requestor_name, claim_number, supplemental_details |
| Follow-up | Log submission; track carrier response |

### 7.3 Reservation of Rights

| Field | Value |
|-------|-------|
| Use case | Responding to carrier's reservation of rights letter |
| Required variables | requestor_name, claim_number, ror_date |
| Follow-up | Route to counsel immediately; review coverage |
| Escalation | Route to counsel for coverage position review |

## Template Lifecycle

| Stage | Actions | Owner | Frequency |
|-------|---------|-------|-----------|
| Creation | Draft template for recurring inquiry type | Legal Ops | As needed |
| Review | Counsel reviews for accuracy and compliance | Counsel | Before publication |
| Publication | Add to system with metadata and variables | Legal Ops | After approval |
| Use | Select, populate, review, and send | Staff | Ongoing |
| Feedback | Track usage, collect effectiveness feedback | Legal Ops | Monthly |
| Update | Revise based on feedback, legal changes | Counsel | Quarterly |
| Retirement | Archive no-longer-applicable templates | Legal Ops | Annually |

### Template Metadata Requirements

| Field | Description | Example |
|-------|-------------|---------|
| Template ID | Unique identifier | DSR-ACK-001 |
| Version | Semantic version | 1.2.0 |
| Created | Creation date | 2026-01-15 |
| Last Reviewed | Most recent counsel review | 2026-04-01 |
| Next Review | Scheduled review date | 2026-07-01 |
| Author | Original author | Legal Operations |
| Reviewer | Approving counsel | General Counsel |
| Status | Active, Draft, Retired | Active |
