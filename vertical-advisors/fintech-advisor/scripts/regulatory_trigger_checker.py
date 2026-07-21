#!/usr/bin/env python3
"""
Regulatory Trigger Checker — scan a fintech business description for keywords
that map to US and EU regulatory regimes. Produces a candidate-trigger list,
NOT a legal opinion.

Usage:
    python regulatory_trigger_checker.py description.txt
    python regulatory_trigger_checker.py description.txt --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Each rule: keyword patterns -> regulatory regime -> what it likely triggers
RULES = [
    {
        "name": "Money transmission (US)",
        "regulator": "FinCEN + state banking commissioners",
        "patterns": [
            r"\b(send|transfer|remit|move|pay)(?:ring|ing)? (?:money|funds|cash|payment|payments)\b",
            r"\b(money transmitter|remittance|remittances|cross[- ]border (?:payment|transfer))\b",
            r"\b(p2p (?:payment|transfer)|peer[- ]to[- ]peer payment)\b",
            r"\bhold(?:ing)? customer (?:funds|balances|deposits)\b",
        ],
        "implication": "Likely requires money transmitter licenses (state-by-state US) OR a sponsor-bank / BaaS partner that holds the licenses.",
    },
    {
        "name": "Lending (US)",
        "regulator": "CFPB + state lending licenses",
        "patterns": [
            r"\b(lend|lending|lender|loan|loans|credit line|line of credit|financ(?:e|ing|ed)|advance|advances)\b",
            r"\b(consumer credit|installment|BNPL|buy now pay later)\b",
            r"\b(usury|interest rate|APR|annual percentage rate)\b",
            r"\b(merchant cash advance|invoice (?:financ|factor))\b",
        ],
        "implication": "Likely requires lending licenses (varies by state in US) and CFPB compliance. Many fintechs partner with bank originators (rent-a-charter) to access national lending.",
    },
    {
        "name": "Securities (US)",
        "regulator": "SEC + FINRA + state securities regulators",
        "patterns": [
            r"\b(stock|stocks|equit(?:y|ies)|bond|bonds|treasury|treasuries|ETF|ETFs|mutual fund)\b",
            r"\b(invest(?:ment)?|portfolio|advisory|advisor|RIA|broker[- ]dealer)\b",
            r"\b(security|securities token|tokenize|tokenization|fractional share|fractional shares)\b",
            r"\b(robo[- ]advisor|wealth management|wealth tech)\b",
        ],
        "implication": "Likely requires SEC registration as broker-dealer or RIA, FINRA member, state notice filings. Custody adds Investment Company Act considerations.",
    },
    {
        "name": "Banking / deposit-taking (US)",
        "regulator": "OCC + FDIC + state banking commissioners",
        "patterns": [
            r"\b(deposit|deposits|FDIC|FDIC[- ]insured|checking account|savings account|demand deposit)\b",
            r"\b(bank charter|national bank|state bank|industrial loan company|ILC)\b",
            r"\b(neobank|challenger bank|digital bank)\b",
        ],
        "implication": "Direct deposit-taking requires a bank charter. Most neobanks operate as a non-bank with a sponsor-bank partner that holds deposits FDIC-insured under the bank's charter.",
    },
    {
        "name": "Card issuing / acquiring",
        "regulator": "Card networks (Visa, Mastercard) + sponsor bank + state regulators",
        "patterns": [
            r"\b(card|cards|debit card|credit card|prepaid card|virtual card|card issuing|issuance)\b",
            r"\b(merchant acquir|payment process|payment processing|card present|card not present)\b",
            r"\b(interchange|chargeback|PCI[- ]DSS)\b",
        ],
        "implication": "Card programs require BIN sponsor (issuing bank) or processor relationship. PCI-DSS compliance scope depends on whether you touch the PAN.",
    },
    {
        "name": "Cryptocurrency / digital assets",
        "regulator": "FinCEN MSB + NYDFS BitLicense + SEC + state regulators",
        "patterns": [
            r"\b(crypto|cryptocurrency|bitcoin|BTC|ethereum|ETH|stablecoin|USDC|USDT)\b",
            r"\b(token|tokens|NFT|defi|decentralized finance|web3|wallet|self[- ]custody)\b",
            r"\b(exchange|on[- ]ramp|off[- ]ramp|fiat to crypto)\b",
        ],
        "implication": "Crypto businesses typically need FinCEN MSB registration and NYDFS BitLicense for NY operations. State money transmitter laws often apply. SEC may treat tokens as securities. EU MiCA applies in Europe.",
    },
    {
        "name": "Payment services (EU)",
        "regulator": "EBA + national competent authorities (FCA UK, BaFin DE, ACPR FR, etc.)",
        "patterns": [
            r"\b(PSD2|PSD3|payment services directive|payment institution|PI)\b",
            r"\b(open banking|account information|payment initiation|AISP|PISP)\b",
            r"\b(SEPA|euro payment|euro transfer|EUR)\b",
            r"\b(EMI|electronic money institution|e[- ]money)\b",
        ],
        "implication": "EU operations triggering PSD2 require PI or EMI authorization in a member state, with passporting across EU. UK requires separate FCA authorization post-Brexit.",
    },
    {
        "name": "EU MiCA (Markets in Crypto-Assets)",
        "regulator": "ESMA + national competent authorities",
        "patterns": [
            r"\b(MiCA|crypto[- ]asset service provider|CASP)\b",
            r"\b(stablecoin|asset[- ]referenced token|e[- ]money token|EMT)\b",
        ],
        "implication": "EU MiCA applies to crypto-asset issuers and service providers operating in the EU. Authorization required from a member-state regulator.",
    },
    {
        "name": "Custody of customer assets",
        "regulator": "Varies — banking, securities, or both",
        "patterns": [
            r"\b(custod(?:y|ial|ian)|safekeep|safekeeping)\b",
            r"\b(hold (?:assets|securities|crypto|tokens|funds))\b",
        ],
        "implication": "Holding customer assets adds custody-specific obligations (Investment Advisers Act custody rule for securities, separate banking custody for fiat, qualified custodian rules for crypto).",
    },
    {
        "name": "Consumer protection (US CFPB)",
        "regulator": "CFPB",
        "patterns": [
            r"\b(consumer|retail customer|individual user|natural person)\b",
            r"\b(EFTA|electronic fund transfer|Reg E|Reg Z|Reg DD|TILA|truth in lending)\b",
            r"\b(unfair|deceptive|abusive|UDAAP)\b",
        ],
        "implication": "Consumer-facing financial products are subject to CFPB oversight. UDAAP (unfair, deceptive, abusive acts and practices) standards apply broadly.",
    },
    {
        "name": "Data protection (financial PII)",
        "regulator": "GLBA (US) + GDPR (EU) + state laws (CCPA, etc.)",
        "patterns": [
            r"\b(financial data|account data|transaction history|consumer financial information)\b",
            r"\b(SSN|social security|tax ID|EIN)\b",
        ],
        "implication": "Financial data triggers Gramm-Leach-Bliley Act (GLBA) safeguards rule in US and GDPR special-category considerations in EU. CCPA applies in California regardless of regulated-entity status.",
    },
]


def detect(text):
    found = []
    text_lower = text.lower()
    for rule in RULES:
        matched_patterns = []
        for pattern in rule["patterns"]:
            m = re.search(pattern, text_lower, re.IGNORECASE)
            if m:
                matched_patterns.append(m.group(0))
        if matched_patterns:
            found.append({
                "trigger": rule["name"],
                "regulator": rule["regulator"],
                "matched_terms": list(set(matched_patterns))[:5],
                "implication": rule["implication"],
            })
    return found


def render_human(triggers, description_excerpt):
    lines = []
    lines.append("Regulatory trigger scan")
    lines.append("=" * 60)
    if description_excerpt:
        lines.append(f'Description: "{description_excerpt[:120]}…"')
        lines.append("")
    if not triggers:
        lines.append("No clear triggers detected from keyword scan.")
        lines.append("This does NOT mean the business has no regulatory exposure —")
        lines.append("it means none of this tool's keyword patterns matched.")
        lines.append("Always validate with specialist fintech counsel.")
        return "\n".join(lines)
    lines.append(f"Detected {len(triggers)} candidate trigger(s):")
    lines.append("")
    for i, t in enumerate(triggers, 1):
        lines.append(f"{i}. {t['trigger']}")
        lines.append(f"   Regulator(s): {t['regulator']}")
        lines.append(f"   Matched terms: {', '.join(t['matched_terms'])}")
        lines.append(f"   Implication: {t['implication']}")
        lines.append("")
    lines.append("=" * 60)
    lines.append("REMINDER: This is a keyword scan, not legal advice.")
    lines.append("Engage fintech-specialist counsel for any binding decisions.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scan a fintech business description for regulatory triggers.")
    parser.add_argument("description", help="Path to a text file describing the business")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.description)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    triggers = detect(text)

    if args.json:
        print(json.dumps({
            "description_excerpt": text[:200].strip(),
            "triggers": triggers,
            "disclaimer": "Keyword scan only. Not legal advice. Engage specialist counsel.",
        }, indent=2))
    else:
        print(render_human(triggers, text[:200]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
