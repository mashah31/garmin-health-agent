#!/usr/bin/env bash
# install.sh — copies the /garmin skill into Claude Code's global commands directory.
# Run this once after cloning, and again whenever you update the skill.

set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RESET='\033[0m'
ok()   { echo -e "${GREEN}✔${RESET} $1"; }
warn() { echo -e "${YELLOW}⚠${RESET} $1"; }

SKILL_DIR="$HOME/.claude/commands"
GARMIN_DIR="$HOME/.claude/garmin"

mkdir -p "$SKILL_DIR" "$GARMIN_DIR"

# Copy skill (slash command)
cp garmin.md "$SKILL_DIR/garmin.md"
ok "Skill installed → ~/.claude/commands/garmin.md"

# Copy scripts
cp scripts/fetch_health.py "$GARMIN_DIR/fetch_health.py"
cp scripts/setup.py        "$GARMIN_DIR/setup.py"
ok "Scripts installed → ~/.claude/garmin/"

# Copy .env.example only — never overwrite an existing .env
if [[ ! -f "$GARMIN_DIR/.env" ]]; then
  cp .env.example "$GARMIN_DIR/.env"
  warn "Credentials file created → ~/.claude/garmin/.env"
  warn "Open it and add your Garmin email + password before continuing."
else
  ok "Credentials file already exists → skipping"
fi

echo ""
echo "Done. Next steps:"
if grep -q "your@email.com" "$GARMIN_DIR/.env" 2>/dev/null; then
  echo "  1. Edit ~/.claude/garmin/.env — add your Garmin email + password"
  echo "  2. uv run --with garminconnect python ~/.claude/garmin/setup.py"
  echo "  3. Type /garmin in Claude Code"
else
  echo "  1. uv run --with garminconnect python ~/.claude/garmin/setup.py  (first time only)"
  echo "  2. Type /garmin in Claude Code"
fi
