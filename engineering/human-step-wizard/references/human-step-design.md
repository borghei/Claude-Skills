# Designing Human Steps

How to decide which steps belong to a human, cut them into wizard steps, write
instructions a stranger can follow, and attach checks that catch mistakes while
the human is still in the dashboard.

## Is this step really human-only?

An agent should do everything it can do safely and hand over only what it
cannot. A step is human-only when at least one of these holds:

| Reason | Examples |
|--------|----------|
| **No API, or the API needs the credential being created** | Creating the first admin token, OAuth app registration, enabling an API in a console |
| **Identity proof** | MFA prompts, hardware keys, SSO approval, signing in as a specific person |
| **Authority** | Change approval, DNS cutover sign-off, accepting a contract or terms of service, spending money |
| **Physical or out-of-band** | Plugging in hardware, phoning a registrar, reading a code from an SMS |
| **Deliberately kept manual** | Production cutovers, key revocation, deleting a tenant: policy says a human presses the button |
| **The agent lacks access by design** | Secrets the agent must never see, production consoles behind a bastion |

If none applies, automate it in the agent's own run instead. A wizard that
asks a human to run `npm install` is a wizard that will be skipped.

**Secrets the agent must not see** are a strong reason to use a wizard: the
human types them into hidden prompts, they go straight to the env file with
mode 0600, and the agent only ever learns the variable name.

## Cutting steps

**One step, one outcome [PROVEN].** A step ends with a single verifiable state:
"token exists and is saved", "TTL is 60 s", "record points at the new IP". If a
step needs "and then", split it.

**Order by dependency, then by risk.** Gather everything reversible first
(create tokens, capture addresses, smoke-test), then the irreversible step,
then cleanup. The human should reach the point of no return with every input
already captured and every pre-check green.

**Capture rollback data before the change.** If rolling back needs the old
value (old IP, old secret id, previous plan), capture it in an earlier step and
store it. Rollback text can then say "the OLD_LB_IP saved in .env.cutover"
instead of "whatever it was before".

**Keep it under ~12 steps.** Past that, people lose track and start skimming.
Split into two wizards at a natural pause (e.g. "prepare" today, "cut over"
tomorrow after TTLs expire).

## Writing instructions

| Rule | Weak | Strong |
|------|------|--------|
| Name the exact navigation path | "Go to settings and create a key" | "Profile -> API Tokens -> Create token -> template 'Edit zone DNS'" |
| Say what to copy and what not to | "Copy the address" | "Copy the public IPv4 address (not the private one)" |
| State the scope and lifetime | "Create a token" | "Limit it to the example.com zone, expire in 7 days" |
| Warn about one-time displays | (nothing) | "Copy it once; the dashboard will not show it again" |
| One action per line | A paragraph | 2-4 numbered lines |

Dashboards change. When you do not know the current UI path for certain,
write what you know ("the API tokens page of your profile") and add the link,
rather than inventing menu names that send the human hunting.

## Inputs

| Decision | Rule |
|----------|------|
| Name | `UPPER_SNAKE_CASE`, meaningful in the env file a month later (`NEW_LB_IP`, not `IP2`) |
| Secret | `secret: true` for anything that grants access: tokens, passwords, private keys, webhook secrets. Hidden entry, never echoed, never logged |
| Pattern | Always anchor (`^...$`). Use the provider's real format (`^sk_live_[A-Za-z0-9]{24,}$`) to catch the classic mistake: pasting the publishable key instead of the secret one |
| Store | `env` when a later step, a check or the application needs it; `none` only for values used once and never again |

Patterns are POSIX ERE because bash `[[ =~ ]]` is. Use `[0-9]` instead of
`\d`, `[A-Za-z0-9_]` instead of `\w`, `[[:space:]]` instead of `\s`; no
lookarounds, no non-greedy quantifiers, no `(?:...)`. The validator rejects
PCRE-only syntax because on most systems it silently fails to match and the
human is told their correct value is wrong.

## Checks

A check is a shell command, fixed in the spec, that exits 0 when the step's
outcome is real. Captured values are available as exported environment
variables. Good checks observe the world from outside instead of trusting the
human's Enter key.

| Step outcome | Check |
|--------------|-------|
| Token works | `curl -fsS -H "Authorization: Bearer $TOKEN" https://api.example/v1/whoami` |
| DNS changed | `dig +short host A \| grep -qxF "$NEW_IP"` |
| TTL lowered | `dig +noall +answer host A \| awk 'NR==1{print $2}'` compared with a limit |
| Service healthy behind new address | `curl -fsS --resolve "host:443:$NEW_IP" https://host/healthz` |
| Secret stored in CI | `gh secret list \| grep -q '^DEPLOY_KEY'` |
| File present | `test -s path/to/file` |
| Port open | `nc -z -w 5 "$HOST" 443` |

**Rules for check commands:**

- Quote every expansion: `"$NEW_LB_IP"`. The validator warns on unquoted
  captured values.
- Never `eval` or `source` anything. The validator rejects both.
- Use timeouts (`--max-time`, `-w`) so a hung network call does not freeze the wizard.
- A check may be slow to turn green (DNS propagation). The human chooses
  retry; set `allow_skip: true` only where a failing check is informative
  rather than blocking (e.g. resolver caches you do not control).

## Irreversible steps

Mark a step `irreversible: true` when completing it changes something that a
second run of the wizard cannot put back: DNS cutovers, key revocation,
deleting a resource, sending a notice to customers, charging a card.

The generated script then:

1. Shows the rollback text **before** the instructions.
2. Requires the human to type the step id. A bare Enter or "y" will not do,
   which stops muscle-memory confirmations.
3. Logs the confirmation with a timestamp in the audit log.
4. Requires a pause and runs the step's checks before marking it done.

A rollback text must be actionable: what to change back, where the old value is,
how long recovery takes. "Revert if needed" is rejected by review, even if the
validator cannot tell.

## Resumability

The wizard records each finished step id in `.wizard-state/<slug>.done` and
reloads stored inputs from the env file on restart, so a human can stop for the
day after step 3, or after a failed check, and resume with the same command.

- A step is marked done **only after** all its checks pass. An abort mid-step
  repeats that step on the next run.
- `--list` shows progress, `--from <id>` re-runs from a step onward, `--reset`
  forgets progress but keeps the env file.
- Step ids are the resume keys. Renaming an id in the spec makes that step
  look new; adding steps at the end is safe.

## Handing the wizard to the human

Tell the human, in the agent's reply:

1. The path and the command: `./scripts/cutover-wizard.sh`
2. Roughly how long it takes and whether any step has a waiting period
   (TTL expiry, certificate issuance, approval queue).
3. Which step is irreversible.
4. Where values are saved, and that the env file must stay out of git.
5. What to send back to the agent when done (usually nothing: the agent can read
   the non-secret values from the env file, or run the checks again).
