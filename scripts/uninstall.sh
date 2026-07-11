#!/usr/bin/env bash
# Omics Skills Uninstaller

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# If running from scripts/ directory, go up one level
if [[ "$(basename "$SCRIPT_DIR")" == "scripts" ]]; then
    REPO_ROOT="$(dirname "$SCRIPT_DIR")"
else
    REPO_ROOT="$SCRIPT_DIR"
fi
AGENTS_DIR="$REPO_ROOT/agents"
SKILLS_DIR="$REPO_ROOT/skills"

# Specific agent files
AGENT_FILES=("omics-scientist.md" "literature-expert.md" "science-writer.md" "dataviz-artist.md")

CLAUDE_AGENTS_DIR="$HOME/.claude/agents"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
CODEX_AGENTS_DIR="$HOME/.codex/agents"
CODEX_SKILLS_DIR="$HOME/.codex/skills"
AGENTS_SKILLS_DIR="$HOME/.agents/skills"
AGENTS_CATALOG_DIR="$HOME/.agents/omics-skills"

# Parse arguments
UNINSTALL_TARGET="both"
KEEP_BACKUPS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --claude)
            UNINSTALL_TARGET="claude"
            shift
            ;;
        --codex)
            UNINSTALL_TARGET="codex"
            shift
            ;;
        --keep-backups)
            KEEP_BACKUPS=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --claude         Uninstall from Claude Code only"
            echo "  --codex          Uninstall from Codex CLI only"
            echo "  --keep-backups   Keep backup files (.bak)"
            echo "  --help           Show this help message"
            echo ""
            echo "Default: Uninstall from both platforms and remove backups"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Functions
uninstall_from_claude() {
    echo -e "${BLUE}Uninstalling from Claude Code...${NC}"

    # Remove agents
    for agent in "${AGENT_FILES[@]}"; do
        basename=$(basename "$agent")
        target="$CLAUDE_AGENTS_DIR/$basename"
        if [ -L "$target" ] || [ -f "$target" ]; then
            rm "$target"
            echo -e "  ${GREEN}OK${NC} Removed agent: $basename"
        fi
    done

    # Remove backups if requested
    if [ "$KEEP_BACKUPS" = false ]; then
        for agent in "${AGENT_FILES[@]}"; do
            rm -f "$CLAUDE_AGENTS_DIR/$agent".bak* 2>/dev/null || true
        done
        echo -e "  ${GREEN}OK${NC} Removed omics-skills agent backups"
    fi

    if [ -L "$CLAUDE_SKILLS_DIR" ]; then
        target=$(readlink "$CLAUDE_SKILLS_DIR")
        if [ "$target" = "$AGENTS_SKILLS_DIR" ]; then
            rm "$CLAUDE_SKILLS_DIR"
            echo -e "  ${GREEN}OK${NC} Removed Claude skills link"
        else
            echo -e "  ${YELLOW}INFO${NC} Preserved non-omics Claude skills symlink: $target"
        fi
    fi

    echo -e "${GREEN}OK Claude Code uninstalled${NC}"
}

uninstall_from_codex() {
    echo -e "${BLUE}Uninstalling from Codex CLI...${NC}"

    # Remove agents
    for agent in "${AGENT_FILES[@]}"; do
        name="${agent%.md}"
        for target in "$CODEX_AGENTS_DIR/$name.toml" "$CODEX_AGENTS_DIR/$name.md"; do
            if [ -L "$target" ] || [ -f "$target" ]; then
                rm "$target"
                echo -e "  ${GREEN}OK${NC} Removed agent: $(basename "$target")"
            fi
        done
    done

    # Remove backups if requested
    if [ "$KEEP_BACKUPS" = false ]; then
        for agent in "${AGENT_FILES[@]}"; do
            name="${agent%.md}"
            rm -f "$CODEX_AGENTS_DIR/$name.toml".bak* \
                "$CODEX_AGENTS_DIR/$name.md".legacy.bak* 2>/dev/null || true
        done
        echo -e "  ${GREEN}OK${NC} Removed omics-skills agent backups"
    fi

    if [ -L "$CODEX_SKILLS_DIR" ]; then
        target=$(readlink "$CODEX_SKILLS_DIR")
        if [ "$target" = "$AGENTS_SKILLS_DIR" ]; then
            rm "$CODEX_SKILLS_DIR"
            echo -e "  ${GREEN}OK${NC} Removed Codex skills link"
        else
            echo -e "  ${YELLOW}INFO${NC} Preserved non-omics Codex skills symlink: $target"
        fi
    fi

    echo -e "${GREEN}OK Codex CLI uninstalled${NC}"
}

uninstall_skills() {
    echo -e "${BLUE}Removing shared skills...${NC}"

    for skill in "$SKILLS_DIR"/*; do
        if [ -d "$skill" ]; then
            basename=$(basename "$skill")
            target="$AGENTS_SKILLS_DIR/$basename"
            if [ -L "$target" ] || [ -d "$target" ]; then
                rm -rf "$target"
                echo -e "  ${GREEN}OK${NC} Removed skill: $basename"
            fi
        fi
    done

    if [ "$KEEP_BACKUPS" = false ]; then
        for skill in "$SKILLS_DIR"/*; do
            basename=$(basename "$skill")
            rm -rf "$AGENTS_SKILLS_DIR/$basename".bak* 2>/dev/null || true
        done
        echo -e "  ${GREEN}OK${NC} Removed omics-skills skill backups"
    fi

    if [ -d "$AGENTS_CATALOG_DIR" ]; then
        rm -rf "$AGENTS_CATALOG_DIR"
        echo -e "  ${GREEN}OK${NC} Removed skill catalog"
    fi
}

# Main
echo -e "${BLUE}Omics Skills Uninstaller${NC}"
echo ""

# Confirm uninstallation
if [ "$UNINSTALL_TARGET" = "both" ]; then
    echo -e "${YELLOW}This will remove omics-skills agents and shared skills.${NC}"
elif [ "$UNINSTALL_TARGET" = "claude" ]; then
    echo -e "${YELLOW}This will remove omics-skills Claude agents only.${NC}"
else
    echo -e "${YELLOW}This will remove omics-skills Codex agents only.${NC}"
fi
echo -e "${YELLOW}Are you sure you want to continue? [y/N]${NC}"
read -r confirmation

if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Uninstallation cancelled.${NC}"
    exit 0
fi

echo ""

# Uninstall based on target
if [ "$UNINSTALL_TARGET" = "both" ] || [ "$UNINSTALL_TARGET" = "claude" ]; then
    uninstall_from_claude
    echo ""
fi

if [ "$UNINSTALL_TARGET" = "both" ] || [ "$UNINSTALL_TARGET" = "codex" ]; then
    uninstall_from_codex
    echo ""
fi

if [ "$UNINSTALL_TARGET" = "both" ]; then
    uninstall_skills
    echo ""
fi

echo -e "${GREEN}OK Uninstallation complete!${NC}"

if [ "$KEEP_BACKUPS" = true ]; then
    echo ""
    echo -e "${YELLOW}Note: Backup files (.bak) were preserved${NC}"
    echo "  To remove them later, run: make clean"
fi
