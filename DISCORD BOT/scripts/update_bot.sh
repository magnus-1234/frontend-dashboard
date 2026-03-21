#!/bin/bash
# ============================================================
# WOS Bot — Manual Update Script (run on Oracle VM)
# Usage:
#   ./scripts/update_bot.sh           # Smart update (skip pip if reqs unchanged)
#   ./scripts/update_bot.sh --force   # Force reinstall all dependencies
# ============================================================
set -e

BOT_DIR="$HOME/app/bot"
if [ -d "$BOT_DIR/venv" ]; then
  VENV_DIR="$BOT_DIR/venv"
elif [ -d "$BOT_DIR/bot_venv" ]; then
  VENV_DIR="$BOT_DIR/bot_venv"
else
  VENV_DIR="$BOT_DIR/venv" # Fallback
fi
CACHE_FILE="$HOME/.bot_deps_hash"

cd "$BOT_DIR"

echo "================================================"
echo "🤖 WOS Bot Manual Update — $(date)"
echo "================================================"

# ── Step 0: Ensure swap exists (prevents OOM freeze on 1GB Oracle VM) ────────
setup_swap() {
  local SWAP_FILE="/swapfile"
  local SWAP_SIZE="2G"

  if swapon --show | grep -q "$SWAP_FILE"; then
    echo "✅ Swap already active ($(free -h | awk '/Swap/{print $2}'))"
    return
  fi

  echo "📦 Creating ${SWAP_SIZE} swap file at ${SWAP_FILE}..."
  if [ -f "$SWAP_FILE" ]; then
    sudo swapoff "$SWAP_FILE" 2>/dev/null || true
    sudo rm -f "$SWAP_FILE"
  fi
  sudo fallocate -l "$SWAP_SIZE" "$SWAP_FILE" 2>/dev/null || sudo dd if=/dev/zero of="$SWAP_FILE" bs=1M count=2048 status=progress
  sudo chmod 600 "$SWAP_FILE"
  sudo mkswap "$SWAP_FILE"
  sudo swapon "$SWAP_FILE"

  # Persist across reboots
  if ! grep -q "$SWAP_FILE" /etc/fstab; then
    echo "$SWAP_FILE none swap sw 0 0" | sudo tee -a /etc/fstab
  fi

  # Reduce swappiness so kernel prefers RAM first
  sudo sysctl vm.swappiness=10
  if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
    echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
  fi

  echo "✅ Swap created: $(free -h | awk '/Swap/{print $2}')"
}

setup_swap

# Pull latest code
echo ""
echo "📥 Pulling latest code from GitHub..."
git fetch origin main
OLD_HASH=$(git rev-parse --short HEAD)
git reset --hard origin/main
NEW_HASH=$(git rev-parse --short HEAD)

if [ "$OLD_HASH" = "$NEW_HASH" ]; then
  echo "ℹ️  Already up to date ($(git log -1 --pretty=%s))"
else
  echo "✅ Updated: $OLD_HASH → $NEW_HASH — $(git log -1 --pretty=%s)"
fi

# Check if requirements changed or --force passed
FORCE_INSTALL=false
if [ "$1" = "--force" ]; then
  FORCE_INSTALL=true
  echo ""
  echo "⚠️  --force flag: will reinstall all dependencies"
fi

# Compare requirements hash
CURRENT_HASH=""
if [ -f "requirements.txt" ]; then
  CURRENT_HASH=$(md5sum requirements.txt | awk '{print $1}')
fi

SAVED_HASH=""
if [ -f "$CACHE_FILE" ]; then
  SAVED_HASH=$(cat "$CACHE_FILE")
fi

# Determine if we need to reinstall or recreate the venv
RECREATE_VENV=false
if [ ! -d "$VENV_DIR" ]; then
  RECREATE_VENV=true
else
  # Check if our venv uses 3.11, if not and 3.11 is available, recreate it
  if command -v python3.11 &> /dev/null; then
    VENV_PYTHON_VER=$("$VENV_DIR/bin/python" --version 2>&1 | awk '{print $2}')
    if [[ ! "$VENV_PYTHON_VER" =~ 3.11 ]]; then
      echo "ℹ️  Existing venv uses Python $VENV_PYTHON_VER. Upgrading to 3.11..."
      RECREATE_VENV=true
    fi
  fi
fi

if [ "$RECREATE_VENV" = "true" ]; then
  echo "📦 Creating/Recreating virtual environment..."
  rm -rf "$VENV_DIR"
  if command -v python3.11 &> /dev/null; then
    python3.11 -m venv "$VENV_DIR"
  else
    python3 -m venv "$VENV_DIR"
  fi
  FORCE_INSTALL=true
fi

if [ "$FORCE_INSTALL" = "true" ] || [ "$CURRENT_HASH" != "$SAVED_HASH" ] && [ -n "$CURRENT_HASH" ]; then
  echo ""
  echo "📦 Installing/updating Python dependencies..."
  source "$VENV_DIR/bin/activate"
  pip install --upgrade pip
  pip install --disable-pip-version-check -r requirements.txt
  echo "$CURRENT_HASH" > "$CACHE_FILE"
  echo "✅ Dependencies installed & cache updated"
else
  echo ""
  echo "⚡ Requirements unchanged — skipping pip install"
fi

# ── Step N: Restart with PM2 (always enforce memory limit) ───────────────────
echo ""
echo "🔄 Restarting bot..."
if pm2 describe discordbot > /dev/null 2>&1; then
  # Update memory limit on the existing process then restart
  pm2 restart discordbot \
    --update-env \
    --max-memory-restart 600M
  echo "✅ Bot restarted (mem limit: 600M)"
else
  echo "⚠️  'discordbot' not in PM2, starting fresh..."
  pm2 start app.py \
    --name discordbot \
    --interpreter "$VENV_DIR/bin/python" \
    --max-memory-restart 600M \
    --restart-delay 30000 \
    --max-restarts 5 \
    --time
  pm2 save
fi

echo ""
pm2 list
echo ""
echo "📋 Tail logs: pm2 logs discordbot --lines 30"
echo "================================================"
echo "✅ Update complete!"
echo "================================================"
