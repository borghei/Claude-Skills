# Red Team Methodology Reference

## Frameworks

### MITRE ATT&CK
Industry standard framework mapping adversary tactics, techniques, and procedures (TTPs):

| Tactic | Description | Example Techniques |
|--------|-------------|-------------------|
| Reconnaissance | Gathering target information | Active scanning, search open databases |
| Resource Development | Building attack infrastructure | Acquire infrastructure, develop capabilities |
| Initial Access | Gaining foothold | Phishing, exploit public-facing app, valid accounts |
| Execution | Running adversary code | Command-line interface, scripting, user execution |
| Persistence | Maintaining access | Account creation, scheduled tasks, registry keys |
| Privilege Escalation | Gaining higher permissions | Exploit vulnerability, token manipulation |
| Defense Evasion | Avoiding detection | Obfuscation, disabling security tools |
| Credential Access | Stealing credentials | Brute force, credential dumping, keylogging |
| Discovery | Learning the environment | Network scanning, account discovery |
| Lateral Movement | Moving through network | Remote services, pass-the-hash |
| Collection | Gathering target data | Data from information repositories |
| Exfiltration | Stealing data | Exfiltration over C2 channel, web service |
| Impact | Disrupting operations | Data destruction, defacement |

### OWASP Testing Guide
For web application testing:
- Information Gathering
- Configuration and Deployment Management Testing
- Identity Management Testing
- Authentication Testing
- Authorization Testing
- Session Management Testing
- Input Validation Testing
- Error Handling Testing
- Cryptography Testing
- Business Logic Testing
- Client-Side Testing
- API Testing

### PTES (Penetration Testing Execution Standard)
1. Pre-engagement Interactions
2. Intelligence Gathering
3. Threat Modeling
4. Vulnerability Analysis
5. Exploitation
6. Post-Exploitation
7. Reporting

## Rules of Engagement (ROE)

### Required Elements
- **Scope**: Exact systems, networks, and applications in scope
- **Out of Scope**: Explicitly excluded targets
- **Authorized Actions**: What testers are allowed to do
- **Prohibited Actions**: Actions that are never acceptable
- **Testing Windows**: When testing can occur
- **Emergency Contacts**: Who to call if things go wrong
- **Legal Authorization**: Signed permission documentation
- **Data Handling**: How discovered data/credentials are handled

### Common Prohibitions
- Denial of service attacks against production systems
- Social engineering of non-consenting individuals
- Physical security testing without explicit authorization
- Modification or deletion of production data
- Accessing systems outside the defined scope
- Sharing findings with unauthorized parties

## Engagement Phases

### Phase 1: Planning (10-15% of engagement)
- Scope definition and ROE agreement
- Target enumeration
- Methodology selection
- Tool preparation
- Communication plan

### Phase 2: Reconnaissance (15-20%)
- OSINT gathering
- Network mapping
- Service enumeration
- Vulnerability identification

### Phase 3: Exploitation (30-40%)
- Vulnerability exploitation
- Payload development
- Initial access achievement
- Privilege escalation

### Phase 4: Post-Exploitation (15-20%)
- Lateral movement
- Persistence establishment
- Data collection
- Objective completion

### Phase 5: Reporting (10-15%)
- Finding documentation
- Risk scoring
- Remediation recommendations
- Executive summary
- Technical detail appendix

## Deliverables Checklist

- [ ] Executive summary (1-2 pages)
- [ ] Methodology description
- [ ] Scope confirmation
- [ ] Finding inventory with severity ratings
- [ ] Attack narrative/kill chain
- [ ] Evidence (screenshots, logs)
- [ ] Remediation recommendations (prioritized)
- [ ] Re-test plan
- [ ] Raw data appendix
