# ENISA Breach Severity Methodology

Complete reference for the European Union Agency for Cybersecurity (ENISA) personal data breach severity assessment methodology.

---

## Table of Contents

- [Severity Formula](#severity-formula)
- [Data Processing Context (DPC)](#data-processing-context-dpc)
- [Ease of Identification (EI)](#ease-of-identification-ei)
- [Circumstances of Breach (CB)](#circumstances-of-breach-cb)
- [Severity Thresholds](#severity-thresholds)
- [Adjustments](#adjustments)
- [Borderline Guidance](#borderline-guidance)
- [EDPB Case Matching](#edpb-case-matching)
- [Quick Decision Tree](#quick-decision-tree)

---

## Severity Formula

```
SE = (DPC x EI) + CB
```

| Component | Name | Range | Description |
|-----------|------|-------|-------------|
| DPC | Data Processing Context | 1-4 | Nature and sensitivity of the personal data involved |
| EI | Ease of Identification | 0.25-1.00 | How easily the data can be used to identify specific individuals |
| CB | Circumstances of Breach | Additive | Aggregated score of loss type and malicious intent |
| SE | Severity | Calculated | Final severity score determining notification obligations |

**Interpretation:** The formula weights the sensitivity of data (DPC) by how identifiable the data subjects are (EI), then adds circumstantial factors (CB) for the type of loss and attacker intent.

---

## Data Processing Context (DPC)

DPC measures the nature and sensitivity of the personal data compromised.

| Score | Label | Description | Examples |
|-------|-------|-------------|----------|
| 1 | Basic | Simple demographic or contact data that is widely available | Name, email address, phone number, mailing address, job title, employer |
| 2 | Behavioral / Financial | Data revealing behavioral patterns, preferences, or financial information | Purchase history, browsing behavior, location data (non-continuous), bank account number, salary information, tax records |
| 3 | Sensitive Personal | Data that could cause significant harm if disclosed | Social security/national ID number, passport number, driver's license, login credentials, detailed financial records, communication content |
| 4 | Special Category / Highly Sensitive | Art. 9 special category data or data with extreme sensitivity | Health/medical records, genetic data, biometric data, sexual orientation, political opinions, religious beliefs, trade union membership, criminal records, children's data combined with other sensitive data |

### DPC Assessment Guidance

| Factor | Increases DPC | Decreases DPC |
|--------|--------------|---------------|
| Data type | Special category (Art. 9), criminal (Art. 10) | Publicly available information |
| Combination | Multiple data categories combined | Single data element |
| Context | Employment, healthcare, financial services | General consumer context |
| Volume per subject | Comprehensive profile | Minimal data elements |

---

## Ease of Identification (EI)

EI measures how easily the compromised data can be used to identify specific individuals.

| Score | Label | Description | Examples |
|-------|-------|-------------|----------|
| 0.25 | Negligible | Data alone cannot identify individuals; requires significant additional information not available to the recipient | Aggregated statistics, anonymized survey data, encrypted data with key not compromised |
| 0.50 | Limited | Identification requires additional data that may be obtainable but requires effort | Pseudonymized data, partial records, coded identifiers without lookup table |
| 0.75 | Significant | Identification is reasonably achievable using available resources | Email addresses combined with behavioral data, IP addresses with timestamps, device identifiers |
| 1.00 | Maximum | Direct identification possible from the data itself | Full name + SSN, photo ID, biometric data, unambiguous unique identifiers |

### EI Assessment Guidance

| Factor | Increases EI | Decreases EI |
|--------|-------------|-------------|
| Direct identifiers | Name, ID number, photo, biometric | Absent or removed |
| Pseudonymization | Not applied or mapping compromised | Properly applied, mapping secure |
| Data combination | Multiple identifying elements together | Single non-identifying element |
| Public availability | Matching data available publicly | No matching data available |
| Encryption | Not encrypted or key compromised | Properly encrypted, key secure |

---

## Circumstances of Breach (CB)

CB is an additive score combining the type of data loss and circumstances.

### Loss Types

| Component | Score Options | Description |
|-----------|-------------|-------------|
| Confidentiality loss | 0 / 0.25 / 0.5 | Was data disclosed to unauthorized parties? |
| Integrity loss | 0 / 0.25 / 0.5 | Was data altered or corrupted? |
| Availability loss | 0 / 0.25 / 0.5 | Was access to data lost or disrupted? |

**Scoring guidance for each loss type:**

| Score | Confidentiality | Integrity | Availability |
|-------|----------------|-----------|-------------|
| 0 | No unauthorized disclosure | No data alteration | No access disruption |
| 0.25 | Limited disclosure (small number of unauthorized recipients, contained) | Minor alteration (detectable, reversible) | Temporary disruption (<24h, workaround available) |
| 0.5 | Broad disclosure (public exposure, unknown recipients, dark web) | Significant alteration (hard to detect, affects decisions) | Extended disruption (>24h, no workaround, data loss) |

### Malicious Intent

| Condition | Score Addition | Description |
|-----------|---------------|-------------|
| Not malicious | +0.0 | Accidental breach, human error, system failure |
| Malicious | +0.5 | Deliberate attack, insider threat, ransomware, social engineering |

### CB Calculation

```
CB = Confidentiality_loss + Integrity_loss + Availability_loss + Malicious_intent
```

**Practical CB range:** 0 to 2.0

| CB Score | Interpretation |
|----------|---------------|
| 0 | No significant breach circumstances (e.g., encrypted backup loss) |
| 0.25-0.5 | Minor circumstances (single loss type, no malicious intent) |
| 0.5-1.0 | Moderate circumstances (multiple loss types or malicious intent) |
| 1.0-1.5 | Serious circumstances (multiple loss types with malicious intent) |
| 1.5-2.0 | Severe circumstances (full CIA triad loss with malicious intent) |

---

## Severity Thresholds

| Score Range | Verdict | Notification Requirement | Response Level |
|-------------|---------|--------------------------|----------------|
| SE < 2 | **LOW** | No notification to SA or data subjects | Internal documentation in breach register (Art. 33(5)). Monitor for escalation. |
| 2 <= SE < 3 | **MEDIUM** | Notify supervisory authority within 72h (Art. 33) | SA notification. Internal investigation. Containment. |
| 3 <= SE < 4 | **HIGH** | Notify SA within 72h + notify data subjects without undue delay (Art. 34) | SA and subject notification. Response team activation. Remediation plan. |
| SE >= 4 | **VERY HIGH** | SA + data subjects + consider public notice | Crisis management. Executive briefing. Outside counsel. Board notification. Consider public statement. |

### Notification Decision Logic

```
IF SE < 2:
    → Log internally only
    → Retain documentation for accountability
ELIF SE < 3:
    → Notify SA within 72h of T0
    → Document breach and response
    → No data subject notification required
ELIF SE < 4:
    → Notify SA within 72h of T0
    → Notify data subjects without undue delay
    → Describe nature of breach, consequences, measures taken
ELSE:
    → All of the above
    → Consider public communication (Art. 34(3)(c))
    → Activate crisis management protocol
    → Brief executive leadership and board
```

---

## Adjustments

### Encryption Adjustment

| Situation | Effect on SE |
|-----------|-------------|
| Data properly encrypted with AES-256 or equivalent, key NOT compromised | DPC effectively reduced by 1-2 levels (data unintelligible per Art. 34(3)(a)) |
| Data encrypted but key also compromised | No reduction — encryption ineffective |
| Data encrypted with weak algorithm (DES, RC4, short key) | Minimal reduction — regulator may not consider protection adequate |
| Partial encryption (some fields encrypted, others clear) | Assess clear-text fields separately; encrypted fields may reduce EI |

### Pseudonymization Adjustment

| Situation | Effect on SE |
|-----------|-------------|
| Pseudonymized with mapping NOT compromised | EI reduced to 0.25 or 0.50 (depending on reversibility) |
| Pseudonymized but mapping also compromised | No EI reduction |
| Pseudonymized with deterministic method (reversible by recipient) | Minimal EI reduction |

### Volume Adjustment

ENISA methodology does not include volume as a direct formula component, but volume affects notification obligations:

| Volume | Practical Impact |
|--------|-----------------|
| <100 individuals | Individual notification straightforward |
| 100-10,000 | Individual notification required but operationally significant |
| >10,000 | Consider whether individual notification is disproportionate effort; if so, public communication per Art. 34(3)(c) |
| >100,000 | Strong case for public communication in addition to individual notification |

---

## Borderline Guidance

When the severity score falls near a threshold boundary, apply these principles:

| Score Range | Borderline Guidance |
|-------------|-------------------|
| 1.8-2.0 | Conservative: treat as MEDIUM if any uncertainty about DPC or EI scoring. Document the borderline analysis. |
| 2.8-3.0 | Conservative: treat as HIGH. The cost of notifying data subjects when not strictly required is far lower than the risk of not notifying when required. |
| 3.8-4.0 | Conservative: treat as VERY HIGH. Activate crisis management as a precaution. |

**General principle:** When in doubt, notify. Under-notification carries regulatory risk (fines, enforcement action). Over-notification carries minimal risk (slight reputational concern from appearing to have frequent breaches, but regulators view proactive notification favorably).

---

## EDPB Case Matching

Reference cases from EDPB Guidelines 01/2021 on examples regarding personal data breach notification. Use these to validate your severity assessment against similar scenarios.

### Ransomware Cases

| Case | Scenario | Typical DPC | Typical EI | Key Factors | Expected Verdict |
|------|----------|-------------|------------|-------------|-----------------|
| 01 | Ransomware with proper backup, no exfiltration | 2-3 | 0.50-1.00 | Availability loss only; backup restored quickly | LOW-MEDIUM |
| 02 | Ransomware without proper backup | 2-3 | 0.50-1.00 | Availability loss, potential permanent data loss | MEDIUM-HIGH |
| 03 | Ransomware on hospital system with exfiltration | 4 | 1.00 | Health data, malicious, confidentiality + availability | VERY HIGH |
| 04 | Ransomware with exfiltration, no backup | 3-4 | 0.75-1.00 | Full CIA triad loss, malicious intent | HIGH-VERY HIGH |

### Data Exfiltration Cases

| Case | Scenario | Typical DPC | Typical EI | Key Factors | Expected Verdict |
|------|----------|-------------|------------|-------------|-----------------|
| 05 | Exfiltration of hashed passwords | 2 | 0.50 | Hashing reduces EI; depends on hash strength | MEDIUM |
| 06 | Exfiltration of employee HR records | 3 | 1.00 | Sensitive personal, directly identifying | HIGH |
| 07 | Exfiltration of customer financial data | 3-4 | 0.75-1.00 | Financial harm potential, identity theft risk | HIGH-VERY HIGH |

### Internal Human Risk Cases

| Case | Scenario | Typical DPC | Typical EI | Key Factors | Expected Verdict |
|------|----------|-------------|------------|-------------|-----------------|
| 08 | Accidental email to wrong recipient (small dataset) | 1-2 | 1.00 | Limited scope, single recipient, likely recoverable | LOW-MEDIUM |
| 09 | Employee deliberately exfiltrating customer data | 3 | 1.00 | Malicious intent, insider knowledge | HIGH |

### Lost/Stolen Device Cases

| Case | Scenario | Typical DPC | Typical EI | Key Factors | Expected Verdict |
|------|----------|-------------|------------|-------------|-----------------|
| 10 | Encrypted laptop stolen | 2-3 | 0.25 | Encryption effective — EI reduced significantly | LOW |
| 11 | Unencrypted USB with personal data lost | 2-3 | 1.00 | No encryption, portable, unknown finder | MEDIUM-HIGH |
| 12 | Encrypted phone lost, remote wipe successful | 2 | 0.25 | Encryption + remote wipe = minimal risk | LOW |

### Mispostal Cases

| Case | Scenario | Typical DPC | Typical EI | Key Factors | Expected Verdict |
|------|----------|-------------|------------|-------------|-----------------|
| 13 | Wrong person receives utility bill | 1 | 0.75 | Basic data, limited sensitivity | LOW |
| 14 | Medical records sent to wrong patient | 4 | 1.00 | Special category, directly identifying | HIGH |
| 15 | Payslips mixed up between employees | 3 | 1.00 | Financial data, workplace context | MEDIUM-HIGH |
| 16 | Marketing email CC instead of BCC (large list) | 1 | 1.00 | Basic data, large volume, email exposed | LOW-MEDIUM |

### Social Engineering Cases

| Case | Scenario | Typical DPC | Typical EI | Key Factors | Expected Verdict |
|------|----------|-------------|------------|-------------|-----------------|
| 17 | Phishing attack stealing credentials | 2-3 | 0.75-1.00 | Malicious, credential access, potential further compromise | MEDIUM-HIGH |
| 18 | Business email compromise with data exfiltration | 3 | 1.00 | Malicious, targeted, potential financial harm | HIGH |

---

## Quick Decision Tree

For rapid initial assessment when detailed scoring is not yet possible:

```
Was the data encrypted with strong encryption AND the key is NOT compromised?
  → YES → Likely LOW. Confirm with full ENISA scoring.
  → NO → Continue

Is special category data (Art. 9) or criminal data (Art. 10) involved?
  → YES → Likely HIGH or VERY HIGH. Prepare for subject notification.
  → NO → Continue

Are individuals directly identifiable from the compromised data?
  → YES, and data is sensitive (financial, ID numbers, credentials)
     → Likely HIGH. Score formally to confirm.
  → YES, but data is basic (name, email, phone only)
     → Likely MEDIUM. Score formally to confirm.
  → NO (pseudonymized, aggregated, or coded)
     → Likely LOW or MEDIUM. Score formally to confirm.

Was the breach malicious (attack, insider theft, ransomware)?
  → YES → Add 0.5 to CB. Likely increases by one severity level.
  → NO → Score without malicious adjustment.

Was data actually accessed/exfiltrated, or just potentially exposed?
  → Actually accessed → Score confidentiality at 0.25-0.5
  → Potentially exposed but no evidence of access → Score confidentiality at 0-0.25
  → Evidence of exfiltration to dark web → Score confidentiality at 0.5, EI at maximum
```

**In all cases:** Complete the full ENISA severity calculation within 2 hours of T0 to support notification decision-making. The quick decision tree provides initial triage, not a substitute for formal scoring.
