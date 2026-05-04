# Student Data Privacy

The regulatory landscape for student data is fragmented: federal (FERPA, COPPA), state (50+ state laws), and international (GDPR for EU students). Edtech companies typically need to navigate several at once.

> **Disclaimer:** Orientation only. Engage edtech / privacy specialist counsel for binding decisions.

---

## FERPA (Family Educational Rights and Privacy Act)

US federal law protecting student education records.

**Applies to:** Educational institutions receiving federal funding (essentially all US public K-12 + most public/private higher ed)

**Coverage:** "Education records" — broadly defined as records directly related to a student maintained by an educational institution

**Edtech relationship:** Edtech is rarely a direct FERPA-regulated entity. It accesses education records under the **"school official" exception**, which allows schools to share records with vendors performing services on the school's behalf.

**Requirements when operating as school official:**
- Use education records only for the purpose specified by the school
- Subject to direct school control over use of records
- Cannot re-disclose education records without consent
- Subject to schools' data security expectations (usually documented in SDPA / DPA)

**FERPA does not require breach notification** at the federal level (state laws may).

---

## COPPA (Children's Online Privacy Protection Act)

US federal law protecting children under 13.

**Applies to:** Operators of commercial websites or online services directed to children under 13, OR that have actual knowledge of collecting personal information from children under 13

**Requirements:**
- Verifiable parental consent before collection
- Notice to parents
- Limited collection (only what's necessary)
- Right to review and delete child's information
- Data retention limited to purpose
- Confidentiality and security

**School-authorization basis:** When operating in a school context, the school can authorize collection for educational purposes — the school stands in for parental consent. This makes K-12 sales easier than D2C consumer products targeting kids.

**FTC enforcement** — fines can reach millions. Several edtech-related COPPA cases settled for tens of millions ($170M for YouTube Kids, $20M for various others).

---

## GDPR (EU General Data Protection Regulation)

Applies to processing of EU residents' personal data, regardless of where the processor is based.

**Special rules for children:**
- Age threshold of valid consent set per member state (13-16)
- Below threshold: parental consent required
- Special protections in marketing and profiling

**Common challenges for edtech in EU:**
- Lawful basis: consent (challenging for children) vs. legitimate interest vs. public task
- Data Protection Impact Assessments (DPIAs) often required for student data processing
- Schrems II / international transfer restrictions for non-EU edtech serving EU students

---

## US State Laws

A non-exhaustive list of significant state student-data laws:

### California — SOPIPA (Student Online Personal Information Protection Act)
- Prohibits targeted advertising based on student data
- Prohibits sale of student data
- Restricts profile creation for non-educational purposes
- One of the most influential state laws (2014, has informed federal proposals)

### New York — Ed Law 2-d ("Parents' Bill of Rights")
- Mandates specific contract clauses with vendors handling student data
- Public posting of vendor list
- Annual training requirement
- Breach-notification obligations to parents

### Illinois — SOPPA (Student Online Personal Protection Act)
- Similar to SOPIPA in restricting use of student data
- Specific contract requirements
- Breach notification

### Connecticut — Public Act 16-189
- Student data contract requirements
- Annual privacy and security training

### Other notable
- Colorado, Texas, Maryland, Massachusetts, Virginia, Washington — varying flavors of student-data restrictions

**Pattern:** Most state laws restrict (1) targeted advertising, (2) data sale, (3) profile creation outside educational purpose. Most require contract terms with school district vendors.

---

## Student Data Privacy Agreements (SDPAs / DPAs)

Most US districts require a signed SDPA before a vendor can touch student data, even in a free pilot.

**Common frameworks:**
- **National Data Privacy Agreement (NDPA)** — multi-state framework supported by SETDA, AASA, A4L
- **California DPA** — California-specific
- **State DPAs** — many states have their own templates
- **District-specific DPAs** — large districts (NYC DOE, LAUSD, Chicago Public Schools) have their own

Most district contracts will reference a state or national DPA framework.

**Typical SDPA terms:**
- Identification of data controller (district) and data processor (vendor)
- Scope of data accessed
- Permitted uses
- Data retention and deletion
- Subprocessor flow-down
- Data location and transfer
- Breach notification
- Audit rights

---

## Common Pitfalls

- **Pilot before SDPA.** "Just a free pilot" is still data processing. Many districts won't allow even a pilot without a signed SDPA.
- **Re-disclosure.** Edtech sometimes shares student data with subprocessors, marketing partners, or in reporting — many of these require explicit district authorization.
- **Targeted advertising.** Several state laws prohibit targeted advertising based on student data — even seemingly-innocuous in-product recommendations can trigger.
- **Profile creation.** Building a student profile for non-educational use is restricted. "Just for analytics" or "we anonymize" are not always sufficient defenses.
- **Breach notification.** State-specific notification rules vary (timeline, content, recipients).
- **Disposing of data.** Many SDPAs require deletion within X days of contract end. Building this into operations from start is much easier than retrofitting.

---

## What to Do Before Launch

1. **Engage edtech / privacy specialist counsel.**
2. **Map your student data flows** — what comes in, from whom, what's stored, where, who sees it.
3. **Pick a baseline SDPA** to operate against (NDPA is a reasonable default for US K-12).
4. **Build SDPA workflow:** template, signature, tracking, renewal.
5. **Ensure subprocessor BAA / DPA flow-down** — your subprocessors must commit to equivalent protection.
6. **Build data deletion workflows** — districts will ask, and SDPAs will require.
7. **Build incident-response process** matching state-specific notification windows.

---

## Resources

- **FERPA:** US Department of Education Privacy Technical Assistance Center (PTAC) — studentprivacy.ed.gov
- **COPPA:** FTC — ftc.gov/business-guidance/privacy-security/childrens-privacy
- **State laws:** Future of Privacy Forum — fpf.org
- **NDPA:** privacy.a4l.org

For binding decisions, engage qualified counsel.
