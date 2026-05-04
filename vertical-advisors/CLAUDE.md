# Vertical Advisors Domain

Strategic vertical advisors — industry-specific orientation, regulatory landscape, GTM patterns, and business-model frameworks for founders and operators in regulated or specialized industries.

This domain is **frameworks-heavy** by design. Strategic vertical questions are usually judgment calls informed by regulatory, market, and economic context — not calculations. The Python tools in each skill provide *categorization* and *triage*, not authoritative answers.

## Skills in This Domain

| Skill | Folder | Tool | Use For |
|-------|--------|------|---------|
| Fintech | `fintech/` | `regulatory_trigger_checker.py` | US/EU regulatory triggers, license vs partner, KYC/AML |
| Healthtech | `healthtech/` | `phi_scope_checker.py` | HIPAA scope, FDA SaMD, payor/provider/employer GTM, VBC |
| Edtech | `edtech/` | `student_data_compliance_checker.py` | FERPA/COPPA/state laws, K-12 vs higher ed vs corporate L&D |
| Ecommerce | `ecommerce/` | `ecom_unit_economics_calculator.py` | Unit economics, fulfillment models, channel strategy |
| Proptech | `proptech/` | `market_segment_classifier.py` | Real-estate segments, MLS / brokerage, RESPA / fair housing |
| Climate-Tech | `climate-tech/` | `carbon_impact_estimator.py` | Categories, GHG accounting, IRA / DOE / VC funding stack |
| Marketplace | `marketplace/` | `marketplace_health_scorer.py` | Liquidity, take rate, chicken-and-egg, network effects |

## Disclaimer

Frameworks and orientation only. Each domain requires specialist counsel for binding decisions:
- Fintech, healthtech, edtech, proptech: licensed counsel for regulatory matters
- Climate-tech: GHG specialists and verifiers
- All: tax / legal / financial advisors as appropriate to the question

## Cross-Domain Integration

| If you need… | Pair with |
|--------------|-----------|
| Implementation-level medical-device compliance | `ra-qm-team/` |
| Contract / DPA / BAA review | `legal/` |
| Strategic security alignment | `agents/compliance/cs-ciso-advisor` |
| Investor-facing materials | `personal-productivity/investor-update-generator`, `pitch-deck-reviewer` |
| Document handoff hygiene | `documents/` (docx, pdf, pptx, xlsx auditors) |
| Board / executive coordination | `c-level-advisor/` skills + `agents/c-level/` agents |

## Adding a New Vertical Skill

1. Create `vertical-advisors/<vertical>/`
2. Add `SKILL.md` with frontmatter (name, description, keywords, disclaimer)
3. Implement Python tool in `scripts/` — stdlib only, dual JSON + human output
4. Write 2-3 references in `references/` (regulatory landscape, GTM patterns, business model patterns)
5. Provide 1 user-facing template in `assets/`
6. Create matching `agents/vertical/cs-<vertical>-advisor.md`
7. Add row to the table above
