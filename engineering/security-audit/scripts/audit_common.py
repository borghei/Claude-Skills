#!/usr/bin/env python3
"""Shared contracts for the security-audit tools.

Holds the vocabularies (unit statuses, verdicts, breadth tiers, run profiles),
the identity rules (agent IDs, fingerprints, coverage IDs), and the input
guards every other script in this folder relies on. Run it directly to print
the contracts an orchestrating agent must honour.

Usage:
    python3 audit_common.py
    python3 audit_common.py --format json
"""

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

MAX_INPUT_BYTES = 5 * 1024 * 1024
MAX_ERRORS = 100

SEVERITIES = ["informational", "low", "medium", "high", "critical"]
VERDICTS = ["confirmed", "needs_validation", "rejected"]
UNIT_STATUSES = ["planned", "in_progress", "covered", "candidate", "blocked",
                 "deferred", "out_of_scope", "not_applicable"]
ORIGINS = ["none", "new", "carried_confirmed", "revalidate_confirmed",
           "carried_needs_validation", "reopened_gap", "recheck_covered",
           "critic"]
PROFILES = ["quick", "standard", "deep"]
REF_KEYS = ["surface", "boundary", "subsystem", "attack_class"]

CORE_FILE = "attack-classes.md"
FOCUSED_COMPANIONS = ["web-protocol-and-auth.md", "ai-and-llm.md",
                      "supply-chain-and-release.md", "cloud-and-deployment.md"]
ALL_COMPANIONS = FOCUSED_COMPANIONS + [
    "client-side.md", "data-isolation-and-lifecycle.md",
    "desktop-mobile-and-local-ipc.md", "memory-safety-and-binary.md",
    "protocols-rpc-and-messaging.md", "resource-exhaustion-and-availability.md"]
TIERS: Dict[str, List[str]] = {"core": [], "focused": FOCUSED_COMPANIONS,
                               "full": ALL_COMPANIONS}

AGENT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
FINGERPRINT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,199}$")
BLOCK_RE = re.compile(r"^([a-z0-9-]+\.md)#(\S.*)$")
RESERVED_IDS = {"con", "prn", "aux", "nul"} | {
    f"{stem}{n}" for stem in ("com", "lpt") for n in range(1, 10)}


class AuditInputError(Exception):
    """Raised when an input file cannot be read as the expected document."""


def load_json(path: Path) -> Any:
    """Read a JSON document, refusing oversized or malformed input."""
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise AuditInputError(f"cannot read {path}: {exc.strerror}") from exc
    if size > MAX_INPUT_BYTES:
        raise AuditInputError(f"{path} is {size} bytes; limit is {MAX_INPUT_BYTES}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AuditInputError(
            f"{path} is not valid JSON (line {exc.lineno}): {exc.msg}") from exc
    except (OSError, UnicodeDecodeError, RecursionError) as exc:
        raise AuditInputError(f"{path} is not readable JSON: {exc}") from exc


def is_text(value: Any) -> bool:
    """True for a string with visible content and no control characters."""
    if not isinstance(value, str) or not value.strip():
        return False
    return not any(unicodedata.category(ch) in ("Cc", "Cf", "Cs", "Zl", "Zp")
                   and ch not in "\n\t" for ch in value)


def is_repo_path(value: Any) -> bool:
    """True for a relative POSIX path that cannot leave the repository."""
    if not is_text(value) or "\n" in value or "\\" in value:
        return False
    if value.startswith(("/", "~")) or re.match(r"^[A-Za-z]:", value):
        return False
    parts = value.split("/")
    return all(part not in ("", ".", "..") for part in parts)


def is_agent_id(value: Any) -> bool:
    """True for a lowercase agent ID that is safe as a directory name."""
    return (isinstance(value, str) and bool(AGENT_ID_RE.match(value))
            and value not in RESERVED_IDS)


def is_fingerprint(value: Any) -> bool:
    """True for a stable root-cause fingerprint."""
    return isinstance(value, str) and bool(FINGERPRINT_RE.match(value))


def coverage_id(refs: Dict[str, Any]) -> str:
    """Derive the deterministic ID of a coverage unit from its references.

    The ID depends only on the source-derived references, so the same unit
    gets the same ID in every run regardless of wave, owner, or outcome.
    """
    parts = [unicodedata.normalize("NFC", str(refs.get(key, ""))) for key in REF_KEYS]
    parts.append(unicodedata.normalize("NFC", str(refs.get("lifecycle", ""))))
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()
    return f"cu-{digest[:20]}"


def parse_block(ref: Any) -> Optional[Tuple[str, str]]:
    """Split a `file.md#Heading` block reference into its two halves."""
    if not isinstance(ref, str):
        return None
    match = BLOCK_RE.match(ref)
    return (match.group(1), match.group(2).strip()) if match else None


def references_dir() -> Path:
    """Location of the skill's reference files relative to this script."""
    return Path(__file__).resolve().parent.parent / "references"


def load_block_index(directory: Path) -> Dict[str, Set[str]]:
    """Map each reference file to the set of headings usable as blocks."""
    index: Dict[str, Set[str]] = {}
    if not directory.is_dir():
        return index
    for path in sorted(directory.glob("*.md")):
        headings: Set[str] = set()
        fenced = False
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("```"):
                fenced = not fenced
            elif not fenced and re.match(r"^#{2,3} \S", line):
                headings.add(line.lstrip("#").strip())
        index[path.name] = headings
    return index


def emit(report: Dict[str, Any], fmt: str) -> None:
    """Print a validation report as JSON or as a short readable summary."""
    if fmt == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    verdict = "VALID" if report.get("valid") else "INVALID"
    print(f"{verdict}: {report.get('file', '')}")
    for key, value in sorted((report.get("stats") or {}).items()):
        print(f"  {key}: {value}")
    errors = report.get("errors") or []
    for message in errors[:MAX_ERRORS]:
        print(f"  - {message}")
    if len(errors) > MAX_ERRORS:
        print(f"  ... {len(errors) - MAX_ERRORS} more error(s) not shown")


def contracts() -> Dict[str, Any]:
    """The vocabularies and identity rules shared by every audit tool."""
    return {
        "verdicts": VERDICTS,
        "severities": SEVERITIES,
        "unit_statuses": UNIT_STATUSES,
        "unit_origins": ORIGINS,
        "profiles": PROFILES,
        "tiers": {name: [CORE_FILE] + files for name, files in TIERS.items()},
        "agent_id_pattern": AGENT_ID_RE.pattern,
        "fingerprint_pattern": FINGERPRINT_RE.pattern,
        "coverage_id": "cu- + first 20 hex of sha256 over surface, boundary, "
                       "subsystem, attack_class, lifecycle joined by U+001F",
        "max_input_bytes": MAX_INPUT_BYTES,
    }


def main() -> None:
    """Print the shared contracts."""
    parser = argparse.ArgumentParser(
        description="Print the vocabularies and identity rules shared by the "
                    "security-audit tools.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    args = parser.parse_args()
    data = contracts()
    if args.format == "json":
        print(json.dumps(data, indent=2))
        return
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for name, files in value.items():
                print(f"  {name}: {', '.join(files)}")
        elif isinstance(value, list):
            print(f"{key}: {', '.join(value)}")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
