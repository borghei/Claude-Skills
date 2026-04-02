#!/bin/bash
#
# Gemini CLI Installation Script for Claude Skills Library
#
# Copies the .gemini/ directory and GEMINI.md to your project so that
# Google Gemini CLI can discover and use skills from this library.
#
# Usage:
#   ./scripts/gemini-install.sh <target-project-path>
#
# Examples:
#   ./scripts/gemini-install.sh ~/Projects/my-app
#   ./scripts/gemini-install.sh .                    # Install to current directory
#   ./scripts/gemini-install.sh /path/to/project
#
# What gets installed:
#   <target>/.gemini/skills-index.json   -- Full catalog of 203 skills
#   <target>/.gemini/skills/             -- Top 20 skill wrappers
#   <target>/GEMINI.md                   -- Gemini CLI instructions
#
# After installation, Gemini CLI will be able to:
#   1. Browse skills via .gemini/skills-index.json
#   2. Quick-reference top skills via .gemini/skills/*.md
#   3. Follow GEMINI.md for skill activation patterns
#
# Note: The actual skill content (SKILL.md, scripts/, references/) stays
# in this repository. The installed files point back to the skill paths
# relative to this repo. For full functionality, clone this repo and
# reference skills by their paths.
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Show usage
usage() {
    echo "Usage: $0 <target-project-path>"
    echo ""
    echo "Installs Gemini CLI configuration files to your project."
    echo ""
    echo "Arguments:"
    echo "  <target-project-path>  Path to your project directory"
    echo ""
    echo "Examples:"
    echo "  $0 ~/Projects/my-app"
    echo "  $0 ."
    echo "  $0 /path/to/project"
    exit 1
}

# Check arguments
if [ $# -lt 1 ]; then
    print_error "Missing target project path."
    echo ""
    usage
fi

TARGET_DIR="$1"

# Resolve to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
    print_error "Target directory does not exist: $1"
    exit 1
}

# Verify source files exist
if [ ! -d "$REPO_ROOT/.gemini" ]; then
    print_error "Source .gemini/ directory not found at $REPO_ROOT/.gemini"
    exit 1
fi

if [ ! -f "$REPO_ROOT/GEMINI.md" ]; then
    print_error "Source GEMINI.md not found at $REPO_ROOT/GEMINI.md"
    exit 1
fi

echo ""
echo "======================================"
echo "  Gemini CLI Skills Installation"
echo "======================================"
echo ""
print_info "Source: $REPO_ROOT"
print_info "Target: $TARGET_DIR"
echo ""

# Check for existing files
if [ -d "$TARGET_DIR/.gemini" ]; then
    print_warning "Existing .gemini/ directory found -- will be updated"
fi

if [ -f "$TARGET_DIR/GEMINI.md" ]; then
    print_warning "Existing GEMINI.md found -- will be overwritten"
fi

# Create target .gemini directory
mkdir -p "$TARGET_DIR/.gemini/skills"

# Copy .gemini directory contents
print_info "Copying .gemini/skills-index.json..."
cp "$REPO_ROOT/.gemini/skills-index.json" "$TARGET_DIR/.gemini/skills-index.json"
print_success "skills-index.json (203 skills catalog)"

# Copy skill wrappers
SKILL_COUNT=0
for wrapper in "$REPO_ROOT/.gemini/skills/"*.md; do
    if [ -f "$wrapper" ]; then
        cp "$wrapper" "$TARGET_DIR/.gemini/skills/"
        SKILL_COUNT=$((SKILL_COUNT + 1))
    fi
done
print_success "$SKILL_COUNT skill wrappers copied"

# Copy GEMINI.md
print_info "Copying GEMINI.md..."
cp "$REPO_ROOT/GEMINI.md" "$TARGET_DIR/GEMINI.md"
print_success "GEMINI.md installed"

echo ""
echo "======================================"
echo "  Installation Complete"
echo "======================================"
echo ""
print_success "Installed to: $TARGET_DIR"
echo ""
echo "Files installed:"
echo "  $TARGET_DIR/.gemini/skills-index.json"
echo "  $TARGET_DIR/.gemini/skills/ ($SKILL_COUNT wrappers)"
echo "  $TARGET_DIR/GEMINI.md"
echo ""
echo "Next steps:"
echo "  1. Open your project with Gemini CLI"
echo "  2. Gemini will read GEMINI.md for skill activation patterns"
echo "  3. Browse .gemini/skills/ for quick skill references"
echo "  4. Use .gemini/skills-index.json for the full catalog"
echo ""
