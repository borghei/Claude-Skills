#!/usr/bin/env python3
"""Claude Code PreToolUse hook that blocks destructive git commands.

Claude Code pipes the pending tool call to this script as JSON on stdin. For a
Bash call, the command string is split into shell segments (``;``, ``&&``,
``||``, ``|``, subshells, ``bash -c`` bodies) and every ``git`` invocation is
checked against the rules below.

Exit codes (the hook contract):
  0  allow - the command runs normally
  2  block - the reason on stderr is shown to the agent, the command never runs

Policy (optional JSON, merged over DEFAULT_POLICY):
  $GIT_GUARDRAILS_POLICY, else $CLAUDE_PROJECT_DIR/.claude/git-guardrails.json
Escape hatch for the human only: export GIT_GUARDRAILS_DISABLE=1 before
starting Claude Code. A variable set inside the command string has no effect.

Manual check:  python3 git_guardrails_hook.py --check "git push -f origin main"
Stdlib only, no network. The only subprocess is a local ``git symbolic-ref``.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

EXIT_ALLOW, EXIT_BLOCK = 0, 2
DEFAULT_POLICY: Dict[str, object] = {
    "protected_branches": ["main", "master", "develop", "trunk", "production", "prod", "release/*"],
    "allow_force_with_lease": True,
    "disabled_rules": [],
    "extra_block_regex": [],
}
WRAPPERS = {"sudo", "command", "nohup", "time", "env", "exec", "xargs", "nice", "doas", "timeout", "stdbuf", "ionice"}
# Wrapper flags that consume the next token, so ``sudo -u bob git ...`` resolves to git.
WRAPPER_VALUE_FLAGS = {
    "sudo": {"-u", "-g", "-h", "-p", "-C", "-U", "-r", "-t", "-D", "--user", "--group", "--host", "--prompt", "--chdir"},
    "doas": {"-u", "-C"},
    "env": {"-u", "--unset", "-C", "--chdir"},
    "nice": {"-n", "--adjustment"},
    "xargs": {"-I", "-n", "-L", "-P", "-s", "-d", "-E", "-a", "--max-args", "--max-procs", "--delimiter", "--arg-file"},
    "timeout": {"-s", "--signal", "-k", "--kill-after"},
    "stdbuf": {"-i", "-o", "-e"},
    "ionice": {"-c", "-n", "-p"},
    "time": {"-f", "-o", "--format", "--output"},
}
# Long options the rules inspect; git accepts any unambiguous prefix of a long option.
LONG_OPTS = ("--hard", "--delete", "--force", "--force-with-lease", "--force-if-includes", "--mirror",
             "--no-verify", "--move", "--onto", "--all", "--staged", "--worktree", "--discard-changes")
SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "eval"}
GIT_OPTS_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}
BROAD_PATHSPECS = {".", "./", ":/", ":/.", "*", ":(top)", "-A", "--all"}
Verdict = Tuple[str, str]  # (rule id, human reason)


def load_policy() -> Dict[str, object]:
    """Merge the optional policy file over the defaults; a broken file keeps the defaults."""
    policy = dict(DEFAULT_POLICY)
    path = os.environ.get("GIT_GUARDRAILS_POLICY")
    if not path:
        root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
        path = str(Path(root) / ".claude" / "git-guardrails.json")
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            policy.update({k: v for k, v in data.items() if k in DEFAULT_POLICY})
    except (OSError, ValueError):
        pass
    return policy


def split_segments(command: str) -> List[List[str]]:
    """Split a shell command into token lists, one per simple command."""
    flat = command.replace("\n", " ; ").replace("$(", " ; ").replace("`", " ; ")
    flat = flat.replace("(", " ; ").replace(")", " ; ")
    try:
        lex = shlex.shlex(flat, posix=True, punctuation_chars=";&|")
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        tokens = flat.split()
    segments: List[List[str]] = [[]]
    for tok in tokens:
        if tok and set(tok) <= set(";&|"):
            segments.append([])
        else:
            segments[-1].append(tok)
    return [s for s in segments if s]


def strip_wrappers(tokens: List[str]) -> List[str]:
    """Drop env assignments and wrapper commands (sudo, env, xargs ...) in front of the real command."""
    i, wrapper = 0, None
    while i < len(tokens):
        tok = tokens[i]
        if wrapper and tok.startswith("-"):
            i += 2 if tok in WRAPPER_VALUE_FLAGS.get(wrapper, ()) else 1
        elif re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tok):
            i += 1
        elif wrapper == "timeout" and re.fullmatch(r"[0-9.]+[smhd]?", tok):
            i += 1
        elif os.path.basename(tok) in WRAPPERS:
            wrapper = os.path.basename(tok)
            i += 1
        else:
            break
    return tokens[i:]


def expand_long(arg: str) -> str:
    """Expand an unambiguous abbreviation (``--har``) to the long option git would resolve it to."""
    if not arg.startswith("--") or arg == "--":
        return arg
    name, eq, val = arg.partition("=")
    if name in LONG_OPTS:
        return arg
    hits = [o for o in LONG_OPTS if o.startswith(name)]
    return hits[0] + eq + val if len(hits) == 1 and len(name) > 3 else arg


def short_flags(args: List[str]) -> str:
    """Return every single-dash short flag letter, so -fd and -f -d look the same."""
    return "".join(a[1:] for a in args if a.startswith("-") and not a.startswith("--") and len(a) > 1)


def positionals(args: List[str]) -> List[str]:
    """Return arguments that are not options (everything after ``--`` counts)."""
    out: List[str] = []
    after_dashdash = False
    for a in args:
        if a == "--" and not after_dashdash:
            after_dashdash = True
        elif after_dashdash or not a.startswith("-"):
            out.append(a)
    return out


class Checker:
    """Evaluates git invocations against the policy."""

    def __init__(self, policy: Dict[str, object], cwd: str) -> None:
        self.policy = policy
        self.cwd = cwd

    def protected(self, branch: Optional[str]) -> bool:
        """True when a branch name matches a protected pattern."""
        if not branch:
            return False
        name = re.sub(r"^refs/heads/", "", branch)
        return any(fnmatch.fnmatch(name, str(p)) for p in self.policy["protected_branches"])  # type: ignore[union-attr]

    def current_branch(self, git_dir: Optional[str]) -> Optional[str]:
        """Resolve the checked-out branch, honouring an override for tests."""
        override = os.environ.get("GIT_GUARDRAILS_CURRENT_BRANCH")
        if override is not None:
            return override or None
        where = os.path.join(self.cwd, git_dir) if git_dir else self.cwd
        try:
            res = subprocess.run(["git", "-C", where, "symbolic-ref", "--short", "-q", "HEAD"],
                                 capture_output=True, text=True, timeout=3)
            return res.stdout.strip() or None
        except (OSError, subprocess.SubprocessError):
            return None

    def check_git(self, args: List[str]) -> Optional[Verdict]:
        """Parse global options, then dispatch on the git subcommand."""
        i, git_dir = 0, None
        while i < len(args) and args[i].startswith("-"):
            if args[i] in GIT_OPTS_WITH_ARG and i + 1 < len(args):
                if args[i] == "-C":
                    git_dir = args[i + 1]
                i += 2
            else:
                i += 1
        if i >= len(args):
            return None
        sub, rest = args[i], [expand_long(a) for a in args[i + 1:]]
        handler = getattr(self, "rule_" + sub.replace("-", "_"), None)
        return handler(rest, git_dir) if handler else None

    def rule_push(self, a: List[str], git_dir: Optional[str]) -> Optional[Verdict]:
        """Force pushes, deletes, mirrors, hook bypass and pushes to protected branches."""
        flags, pos = short_flags(a), positionals(a)
        if "--no-verify" in a:
            return "no-verify", "--no-verify skips the repository's own safety hooks"
        if "--mirror" in a:
            return "push-mirror", "push --mirror overwrites and deletes every remote ref"
        refspecs = pos[1:]
        targets = [r.lstrip("+").split(":")[-1] for r in refspecs if r.lstrip("+").split(":")[-1]]
        if "--delete" in a or "d" in flags or any(r.startswith(":") for r in refspecs):
            return "push-delete", "deleting a remote branch or tag cannot be undone from this machine"
        if "n" in flags or "--dry-run" in a:
            return None
        if not refspecs or "HEAD" in targets:
            current = self.current_branch(git_dir)
            targets = [t for t in targets if t != "HEAD"] + ([current] if current else [])
        hits_protected = any(self.protected(t) for t in targets) or "--all" in a
        if "--force" in a or "f" in flags or any(r.startswith("+") for r in refspecs):
            return "push-force", "force push rewrites remote history that other people may have pulled"
        if any(x.startswith(("--force-with-lease", "--force-if-includes")) for x in a):
            if hits_protected or not self.policy["allow_force_with_lease"]:
                return "push-force-with-lease", "force-with-lease is still a history rewrite on a shared branch"
            return None
        if hits_protected:
            return "push-protected", "direct push to a protected branch; open a pull request instead"
        return None

    def rule_reset(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        if "--hard" in a:
            return "reset-hard", "reset --hard discards uncommitted work with no undo"
        return None

    def rule_clean(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        flags = short_flags(a)
        if "n" in flags or "--dry-run" in a:
            return None
        if "f" in flags or "--force" in a:
            return "clean-force", "clean -f deletes untracked files permanently (they were never in git)"
        return None

    def rule_branch(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        flags = short_flags(a)
        forced = "f" in flags or "--force" in a
        if "D" in flags or (forced and ("d" in flags or "--delete" in a)):
            return "branch-force-delete", "branch -D deletes a branch even if its commits are unmerged"
        if "M" in flags or "C" in flags or (forced and ("m" in flags or "--move" in a)):
            return "branch-force-rename", "forced rename/copy overwrites an existing branch"
        pos = positionals(a)
        if forced and pos and self.protected(pos[0]):
            return "branch-force-move", "branch -f moves a protected branch to another commit"
        return None

    def rule_checkout(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        if "--force" in a or "f" in short_flags(a):
            return "checkout-discard", "checkout --force throws away local modifications"
        paths = a[a.index("--") + 1:] if "--" in a else positionals(a)
        if any(p in BROAD_PATHSPECS for p in paths):
            return "checkout-discard", "checkout of '.' overwrites every uncommitted change in the tree"
        return None

    def rule_restore(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        flags = short_flags(a)
        staged_only = ("--staged" in a or "S" in flags) and not ("--worktree" in a or "W" in flags)
        if not staged_only and any(p in BROAD_PATHSPECS for p in positionals(a)):
            return "restore-discard", "restore of '.' discards every uncommitted change in the tree"
        return None

    def rule_switch(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        if "--discard-changes" in a or "--force" in a or "f" in short_flags(a):
            return "switch-discard", "switch --discard-changes throws away local modifications"
        return None

    def rule_rebase(self, a: List[str], git_dir: Optional[str]) -> Optional[Verdict]:
        if any(x in a for x in ("--abort", "--continue", "--skip", "--quit", "--edit-todo", "--show-current-patch")):
            return None
        skip = {a[i + 1] for i, x in enumerate(a[:-1]) if x == "--onto"}
        pos = [p for p in positionals(a) if p not in skip]
        branch = pos[1] if len(pos) > 1 else self.current_branch(git_dir)
        if self.protected(branch):
            return "rebase-shared", f"rebasing protected branch '{branch}' rewrites shared history"
        return None

    def rule_filter_branch(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        return "history-rewrite", "filter-branch rewrites every commit hash in the repository"

    def rule_filter_repo(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        return "history-rewrite", "filter-repo rewrites every commit hash in the repository"

    def rule_reflog(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        if a[:1] == ["delete"] or (a[:1] == ["expire"] and any(x.endswith(("=now", "=all")) for x in a)):
            return "reflog-destroy", "expiring the reflog removes the last way to recover lost commits"
        return None

    def rule_gc(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        if any(x in ("--prune=now", "--prune=all") for x in a):
            return "gc-prune-now", "gc --prune=now deletes unreachable commits immediately"
        return None

    def rule_stash(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        if a[:1] == ["clear"]:
            return "stash-clear", "stash clear drops every stash entry at once"
        return None

    def rule_update_ref(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        if "-d" in a or "--delete" in a:
            return "update-ref-delete", "update-ref -d deletes a ref without any safety check"
        return None

    def rule_worktree(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        if a[:1] == ["remove"] and ("--force" in a or "f" in short_flags(a)):
            return "worktree-force-remove", "worktree remove --force deletes uncommitted work in that tree"
        return None

    def rule_commit(self, a: List[str], _: Optional[str]) -> Optional[Verdict]:
        if "--no-verify" in a or "n" in short_flags(a):
            return "no-verify", "--no-verify skips the repository's own safety hooks"
        return None


def evaluate(command: str, policy: Dict[str, object], cwd: str, depth: int = 0) -> Optional[Verdict]:
    """Return the first enabled rule violated by any segment of the command."""
    disabled = set(policy.get("disabled_rules") or [])  # type: ignore[arg-type]
    for pattern in policy.get("extra_block_regex") or []:  # type: ignore[union-attr]
        try:
            if re.search(str(pattern), command) and "extra-pattern" not in disabled:
                return "extra-pattern", f"matches the policy pattern {pattern!r}"
        except re.error:
            continue
    checker = Checker(policy, cwd)
    for seg in split_segments(command):
        tokens = strip_wrappers(seg)
        if not tokens:
            continue
        name = os.path.basename(tokens[0])
        if name == "cd" and len(tokens) > 1:
            checker.cwd = os.path.join(checker.cwd, os.path.expanduser(tokens[1]))
            continue
        verdict: Optional[Verdict] = None
        if name in SHELLS and depth < 3:
            body = " ".join(tokens[1:]) if name == "eval" else ""
            for j in range(1, len(tokens) - 1):
                # -c alone or inside a short-flag cluster: bash -lc, sh -xc, bash -ec ...
                if name != "eval" and re.fullmatch(r"-[A-Za-z]*c[A-Za-z]*", tokens[j]):
                    body = tokens[j + 1]
                    break
            verdict = evaluate(body, policy, checker.cwd, depth + 1) if body else None
        elif name == "git":
            verdict = checker.check_git(tokens[1:])
        if verdict and verdict[0] not in disabled:
            return verdict
    return None


def block_message(rule: str, reason: str, command: str) -> str:
    """Format the stderr text the agent sees when a command is blocked."""
    return (f"BLOCKED by git-guardrails [{rule}]: {reason}.\n"
            f"  command: {command.strip()[:300]}\n"
            "  Do not retry or work around this. If the operation is really intended, "
            "explain why and ask the user to run it in their own terminal.")


def main() -> int:
    """Hook entry point: read the tool call, decide, exit 0 or 2."""
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        verdict = evaluate(sys.argv[2], load_policy(), os.getcwd())
        print(json.dumps({"decision": "block" if verdict else "allow",
                          "rule": verdict[0] if verdict else None,
                          "reason": verdict[1] if verdict else None}))
        return EXIT_BLOCK if verdict else EXIT_ALLOW
    if os.environ.get("GIT_GUARDRAILS_DISABLE") == "1":
        return EXIT_ALLOW
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return EXIT_ALLOW
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return EXIT_ALLOW
    command = (payload.get("tool_input") or {}).get("command") or ""
    if "git" not in command:
        return EXIT_ALLOW
    verdict = evaluate(command, load_policy(), str(payload.get("cwd") or os.getcwd()))
    if verdict:
        sys.stderr.write(block_message(verdict[0], verdict[1], command) + "\n")
        return EXIT_BLOCK
    return EXIT_ALLOW


if __name__ == "__main__":
    sys.exit(main())
