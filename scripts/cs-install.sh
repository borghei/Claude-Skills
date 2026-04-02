#!/usr/bin/env bash
# cs-install.sh — Install the Claude Skills CLI ('cs') to your PATH
#
# Usage:
#   ./scripts/cs-install.sh          # Symlink to /usr/local/bin/cs
#   ./scripts/cs-install.sh --copy   # Copy instead of symlink
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CS_PY="$SCRIPT_DIR/cs.py"
INSTALL_DIR="/usr/local/bin"
INSTALL_PATH="$INSTALL_DIR/cs"
MODE="symlink"

if [[ "${1:-}" == "--copy" ]]; then
    MODE="copy"
fi

# ── Preflight checks ──────────────────────────────────────────────────

if [[ ! -f "$CS_PY" ]]; then
    echo "Error: cs.py not found at $CS_PY"
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required but not found in PATH."
    exit 1
fi

# ── Confirm ───────────────────────────────────────────────────────────

echo ""
echo "  Claude Skills CLI Installer"
echo "  ─────────────────────────────────────"
echo ""
echo "  Source:      $CS_PY"
echo "  Destination: $INSTALL_PATH"
echo "  Method:      $MODE"
echo ""

read -rp "  Proceed? [y/N] " answer
if [[ ! "$answer" =~ ^[Yy]$ ]]; then
    echo "  Aborted."
    exit 0
fi

# ── Make executable ───────────────────────────────────────────────────

chmod +x "$CS_PY"

# ── Install ───────────────────────────────────────────────────────────

# Check if we need sudo
NEED_SUDO=false
if [[ ! -w "$INSTALL_DIR" ]]; then
    NEED_SUDO=true
fi

if [[ "$MODE" == "symlink" ]]; then
    if $NEED_SUDO; then
        sudo ln -sf "$CS_PY" "$INSTALL_PATH"
    else
        ln -sf "$CS_PY" "$INSTALL_PATH"
    fi
    echo ""
    echo "  Symlinked: $INSTALL_PATH -> $CS_PY"
else
    if $NEED_SUDO; then
        sudo cp "$CS_PY" "$INSTALL_PATH"
        sudo chmod +x "$INSTALL_PATH"
    else
        cp "$CS_PY" "$INSTALL_PATH"
        chmod +x "$INSTALL_PATH"
    fi
    echo ""
    echo "  Copied: $CS_PY -> $INSTALL_PATH"
fi

echo ""
echo "  Installation complete. Usage:"
echo ""
echo "    cs search \"api design\"         Search for skills"
echo "    cs list                        List all skills"
echo "    cs list --domain engineering   Filter by domain"
echo "    cs info churn-prevention       Skill details"
echo "    cs install seo-auditor ./      Install a skill"
echo "    cs stats                       Library dashboard"
echo "    cs doctor                      Health check"
echo "    cs bundle starter ./skills     Install a bundle"
echo ""
echo "    cs --help                      Full help"
echo ""
