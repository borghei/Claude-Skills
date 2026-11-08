# ---- human-step-wizard runtime (embedded by wizard_generate.py; do not edit per wizard) ----
# Requires: WIZARD_TITLE, WIZARD_SLUG, WIZARD_ENV_FILE, WIZARD_VARS, WIZARD_STEP_IDS, WIZARD_STEP_TITLES
# set by the generated header. Values the human types are only ever stored with printf -v and
# compared with [[ =~ ]]; they are never evaluated as code.

WIZARD_STATE_DIR="${WIZARD_STATE_DIR:-.wizard-state}"
WIZARD_STATE_FILE="$WIZARD_STATE_DIR/$WIZARD_SLUG.done"
WIZARD_LOG_FILE="$WIZARD_STATE_DIR/$WIZARD_SLUG.log"
WIZARD_TOTAL="${#WIZARD_STEP_IDS[@]}"

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_BOLD=$'\033[1m'; C_DIM=$'\033[2m'; C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_RESET=$'\033[0m'
else
  C_BOLD=""; C_DIM=""; C_RED=""; C_GREEN=""; C_YELLOW=""; C_RESET=""
fi

w_say()  { printf '%s\n' "$*"; }
w_ok()   { printf '%s  ok  %s%s\n' "$C_GREEN" "$*" "$C_RESET"; }
w_warn() { printf '%s  !   %s%s\n' "$C_YELLOW" "$*" "$C_RESET" >&2; }
w_die()  { printf '%serror: %s%s\n' "$C_RED" "$*" "$C_RESET" >&2; exit 1; }
w_log()  { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$WIZARD_LOG_FILE"; }

w_read_line() {
  # Read one line into the named variable; EOF aborts instead of looping forever.
  local __var="$1" __prompt="$2" __line=""
  printf '%s' "$__prompt"
  if ! IFS= read -r __line; then
    printf '\n'
    w_die "input closed; progress is saved, re-run to resume"
  fi
  printf -v "$__var" '%s' "$__line"
}

w_header() {
  printf '\n%s==== Step %s/%s: %s ====%s\n' "$C_BOLD" "$1" "$WIZARD_TOTAL" "$2" "$C_RESET"
}

w_open_url() {
  local url="$1"
  w_say "  Open: $url"
  if [ "${WIZARD_OPEN_URLS:-0}" = "1" ]; then
    if command -v open >/dev/null 2>&1; then open "$url" >/dev/null 2>&1 || true
    elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$url" >/dev/null 2>&1 || true
    fi
  fi
}

w_pause() {
  local _ignored
  w_read_line _ignored "  ${C_DIM}Press Enter when this is done...${C_RESET} "
}

w_confirm_irreversible() {
  local id="$1" rollback="$2" answer=""
  w_say ""
  w_say "  ${C_RED}${C_BOLD}This step cannot simply be undone.${C_RESET}"
  w_say "  Rollback: $rollback"
  w_read_line answer "  Type '$id' to continue, anything else to stop: "
  if [ "$answer" != "$id" ]; then
    w_log "stopped-before $id"
    w_die "stopped before '$id'; nothing was marked done"
  fi
  w_log "confirmed $id"
}

w_ask() {
  # w_ask NAME PROMPT PATTERN SECRET(0|1)
  local name="$1" prompt="$2" pattern="$3" secret="$4" value="" attempt=1
  while [ "$attempt" -le 3 ]; do
    if [ "$secret" = "1" ]; then
      printf '  %s (hidden): ' "$prompt"
      if ! IFS= read -r -s value; then printf '\n'; w_die "input closed; re-run to resume"; fi
      printf '\n'
    else
      w_read_line value "  $prompt: "
    fi
    if [ -z "$value" ]; then
      w_warn "a value is required"
    elif [ -n "$pattern" ] && ! [[ "$value" =~ $pattern ]]; then
      w_warn "that does not look right (expected to match: $pattern)"
    else
      printf -v "$name" '%s' "$value"
      export "${name?}"
      w_ok "$name captured"
      return 0
    fi
    attempt=$((attempt + 1))
  done
  w_die "no valid value for $name after 3 attempts"
}

w_store_env() {
  # Upsert NAME=value into the env file without sed, so the value is never interpreted.
  local name="$1" value tmp
  value="${!name}"
  mkdir -p "$(dirname "$WIZARD_ENV_FILE")"
  tmp="$(mktemp "${WIZARD_ENV_FILE}.XXXXXX")"
  chmod 600 "$tmp"
  if [ -f "$WIZARD_ENV_FILE" ]; then
    grep -v "^${name}=" "$WIZARD_ENV_FILE" > "$tmp" || true
  fi
  printf '%s=%s\n' "$name" "$value" >> "$tmp"
  mv "$tmp" "$WIZARD_ENV_FILE"
  w_ok "$name saved to $WIZARD_ENV_FILE"
}

w_load_env() {
  # Re-load only the variables this wizard declares; the file is parsed, never sourced.
  local line key val
  [ -f "$WIZARD_ENV_FILE" ] || return 0
  while IFS= read -r line || [ -n "$line" ]; do
    key="${line%%=*}"
    val="${line#*=}"
    case " $WIZARD_VARS " in
      *" $key "*) printf -v "$key" '%s' "$val"; export "${key?}" ;;
    esac
  done < "$WIZARD_ENV_FILE"
}

w_check() {
  # w_check DESCRIPTION COMMAND ALLOW_SKIP(0|1). COMMAND is fixed text from the spec.
  local desc="$1" cmd="$2" allow_skip="$3" choice=""
  while true; do
    if bash -c "$cmd" >/dev/null 2>&1; then
      w_ok "check passed: $desc"
      return 0
    fi
    w_warn "check failed: $desc"
    if [ "$allow_skip" = "1" ]; then
      w_read_line choice "  [r]etry, [s]kip this check, or [a]bort? "
    else
      w_read_line choice "  [r]etry or [a]bort? "
    fi
    case "$choice" in
      r|R|"") continue ;;
      s|S) if [ "$allow_skip" = "1" ]; then w_log "skipped-check $desc"; return 0; fi ;;
      *) w_die "aborted at check: $desc (progress saved)" ;;
    esac
  done
}

w_is_done()   { [ -f "$WIZARD_STATE_FILE" ] && grep -qxF -- "$1" "$WIZARD_STATE_FILE"; }
w_mark_done() { printf '%s\n' "$1" >> "$WIZARD_STATE_FILE"; w_log "done $1"; }

w_list() {
  local i=0 id mark
  w_say "$WIZARD_TITLE"
  for id in "${WIZARD_STEP_IDS[@]}"; do
    if w_is_done "$id"; then mark="done   "; else mark="pending"; fi
    printf '  %2d. [%s] %-24s %s\n' "$((i + 1))" "$mark" "$id" "${WIZARD_STEP_TITLES[$i]}"
    i=$((i + 1))
  done
}

w_forget_from() {
  # Mark the named step and every later step as pending again.
  local from="$1" id seen=0 keep
  keep="$(mktemp "$WIZARD_STATE_DIR/.keep.XXXXXX")"
  for id in "${WIZARD_STEP_IDS[@]}"; do
    [ "$id" = "$from" ] && seen=1
    if [ "$seen" = "0" ] && w_is_done "$id"; then printf '%s\n' "$id" >> "$keep"; fi
  done
  [ "$seen" = "1" ] || { rm -f "$keep"; w_die "unknown step id: $from"; }
  mv "$keep" "$WIZARD_STATE_FILE"
}

w_usage() {
  w_say "Usage: $0 [--list | --reset | --from STEP_ID | --help]"
  w_say "  (no args)   run every pending step, resuming where the last run stopped"
  w_say "  --list      show steps and their status"
  w_say "  --from ID   re-run from step ID onward"
  w_say "  --reset     forget all progress (the env file is kept)"
  w_say "Env: WIZARD_STATE_DIR (default .wizard-state), WIZARD_OPEN_URLS=1 to open links,"
  w_say "     WIZARD_ALLOW_NONINTERACTIVE=1 to read answers from a pipe (testing only)."
}

w_main() {
  mkdir -p "$WIZARD_STATE_DIR"
  chmod 700 "$WIZARD_STATE_DIR" 2>/dev/null || true
  touch "$WIZARD_STATE_FILE"
  case "${1:-}" in
    -h|--help) w_usage; return 0 ;;
    --list) w_list; return 0 ;;
    --reset) : > "$WIZARD_STATE_FILE"; w_log "reset"; w_say "Progress cleared."; return 0 ;;
    --from) [ -n "${2:-}" ] || w_die "--from needs a step id" ;;
    "") ;;
    *) w_usage; return 2 ;;
  esac
  if [ ! -t 0 ] && [ "${WIZARD_ALLOW_NONINTERACTIVE:-0}" != "1" ]; then
    w_die "this wizard needs a human at a terminal (stdin is not a TTY)"
  fi
  if [ "${1:-}" = "--from" ]; then w_forget_from "$2"; fi
  trap 'printf "\nInterrupted. Progress is saved; re-run to resume.\n" >&2; exit 130' INT TERM
  w_load_env
  w_say "${C_BOLD}$WIZARD_TITLE${C_RESET}"
  local i=0 id done_count=0
  for id in "${WIZARD_STEP_IDS[@]}"; do
    i=$((i + 1))
    if w_is_done "$id"; then
      w_say "${C_DIM}  [$i/$WIZARD_TOTAL] $id already done, skipping${C_RESET}"
      done_count=$((done_count + 1))
      continue
    fi
    "step_$i"
    w_mark_done "$id"
    done_count=$((done_count + 1))
  done
  w_say ""
  w_ok "All $done_count/$WIZARD_TOTAL steps complete."
  w_say "  Values saved to: $WIZARD_ENV_FILE (keep it out of version control)"
  w_say "  Audit log:       $WIZARD_LOG_FILE"
}
# ---- end runtime ----
