#!/bin/bash
# ╔══════════════════════════════════════════════════════════╗
# ║  FORGE Stack — Deterministic Bootstrap (macOS)          ║
# ║  Reproduces exact FORGE setup from a fresh Mac          ║
# ║  Usage: git clone <repo> && cd AI-POWERSETUP            ║
# ║         bash bootstrap.sh                               ║
# ╚══════════════════════════════════════════════════════════╝

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

log()  { echo -e "${CYAN}[FORGE]${NC} $1"; }
ok()   { echo -e "${GREEN}  ✅ $1${NC}"; }
warn() { echo -e "${YELLOW}  ⚠️  $1${NC}"; }
fail() { echo -e "${RED}  ❌ $1${NC}"; exit 1; }

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  🪨 FORGE Stack — Bootstrap Installer       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ─── Step 0: Verify macOS ────────────────────────────────────
log "Step 0: Checking OS..."
[[ "$(uname)" == "Darwin" ]] || fail "This bootstrap only works on macOS."
ok "macOS detected"

# ─── Step 1: Check prerequisites ─────────────────────────────
log "Step 1: Checking prerequisites..."
command -v python3 &>/dev/null || fail "python3 not found. Install via: xcode-select --install"
command -v npm &>/dev/null || fail "npm not found. Install Node.js: https://nodejs.org"
command -v git &>/dev/null || fail "git not found. Install via: xcode-select --install"
ok "python3, npm, git found"

# Check switchboard
if ! command -v switchboard &>/dev/null; then
    log "Installing Switchboard (MCP aggregator)..."
    npm install -g @george5562/switchboard
fi
ok "switchboard available"

# ─── Step 2: Load .env (if exists) ──────────────────────────
log "Step 2: Loading environment..."
if [ -f "$REPO_DIR/.env" ]; then
    set -a; source "$REPO_DIR/.env"; set +a
    ok ".env loaded"
else
    warn ".env not found — copy from template:"
    warn "  cp .env.example .env && nano .env"
    warn "Continuing without API keys (some features will be limited)"
fi

# ─── Step 3: Create symlinks ────────────────────────────────
log "Step 3: Creating symlinks..."

# ~/.agent/scripts → repo/agent/scripts
mkdir -p ~/.agent
if [ -L ~/.agent/scripts ]; then rm ~/.agent/scripts; fi
if [ -d ~/.agent/scripts ] && [ ! -L ~/.agent/scripts ]; then
    mv ~/.agent/scripts ~/.agent/scripts.bak.$(date +%s)
    warn "Backed up existing ~/.agent/scripts/"
fi
ln -sf "$REPO_DIR/agent/scripts" ~/.agent/scripts
ok "~/.agent/scripts → repo"

# ~/.agent/skills → repo/agent/skills
if [ -L ~/.agent/skills ]; then rm ~/.agent/skills; fi
if [ -d ~/.agent/skills ] && [ ! -L ~/.agent/skills ]; then
    mv ~/.agent/skills ~/.agent/skills.bak.$(date +%s)
    warn "Backed up existing ~/.agent/skills/"
fi
ln -sf "$REPO_DIR/agent/skills" ~/.agent/skills
ok "~/.agent/skills → repo"

# ~/.openclaw → repo/openclaw
if [ -L ~/.openclaw ]; then rm ~/.openclaw; fi
if [ -d ~/.openclaw ] && [ ! -L ~/.openclaw ]; then
    mv ~/.openclaw ~/.openclaw.bak.$(date +%s)
    warn "Backed up existing ~/.openclaw/"
fi
ln -sf "$REPO_DIR/openclaw" ~/.openclaw
ok "~/.openclaw → repo"

# ~/.switchboard → repo/switchboard
if [ -L ~/.switchboard ]; then rm ~/.switchboard; fi
if [ -d ~/.switchboard ] && [ ! -L ~/.switchboard ]; then
    mv ~/.switchboard ~/.switchboard.bak.$(date +%s)
    warn "Backed up existing ~/.switchboard/"
fi
ln -sf "$REPO_DIR/switchboard" ~/.switchboard
ok "~/.switchboard → repo"

# ─── Step 4: MCP config (needs absolute path injection) ─────
log "Step 4: Generating IDE MCP config..."
mkdir -p ~/.gemini/antigravity
cat > ~/.gemini/antigravity/mcp_config.json << MCPEOF
{
    "mcpServers": {
        "sequential-thinking": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-sequential-thinking"
            ],
            "env": {}
        },
        "skills-search": {
            "command": "python3",
            "args": [
                "$HOME/.agent/scripts/skills-search-server.py"
            ],
            "env": {}
        },
        "switchboard": {
            "command": "bash",
            "args": [
                "$HOME/.agent/scripts/switchboard-wrapper.sh"
            ],
            "env": {}
        }
    }
}
MCPEOF
ok "mcp_config.json generated at ~/.gemini/antigravity/"

# ─── Step 5: Fix switchboard sub-MCP paths ──────────────────
log "Step 5: Patching switchboard sub-MCP paths..."
# Update GLM Bridge .mcp.json with correct absolute path
FLASH_KEY="${ZAI_FLASH_API_KEY:-}"
cat > "$REPO_DIR/switchboard/mcps/glm-bridge/.mcp.json" << GLMEOF
{
  "name": "glm-bridge",
  "description": "glm-bridge MCP",
  "switchboardDescription": "GLM Bridge — Self-Refine LLM proxy to z.ai GLM-4.7",
  "command": {
    "cmd": "$REPO_DIR/glm-bridge/venv/bin/python3 $REPO_DIR/glm-bridge/glm_bridge_server.py",
    "args": [],
    "env": {
      "OPENAI_API_KEY": "${ZAI_API_KEY:-}",
      "OPENAI_API_BASE": "https://api.z.ai/api/coding/paas/v4",
      "GLM_BRIDGE_MODEL": "openai/glm-4.7",
      "GLM_BRIDGE_TIMEOUT": "90",
      "GLM_FLASH_API_KEY": "$FLASH_KEY",
      "GLM_FLASH_API_BASE": "https://api.z.ai/api/paas/v4",
      "GLM_FLASH_MODEL": "glm-4.7-flash",
      "GLM_BRIDGE_SELF_REFINE": "true",
      "GLM_BRIDGE_MAX_REFINE": "1"
    }
  }
}
GLMEOF
ok "GLM Bridge sub-MCP path set"

# ─── Step 6: Python virtual environment ─────────────────────
log "Step 6: Setting up Python venv for GLM Bridge..."
cd "$REPO_DIR/glm-bridge"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    ok "venv created"
else
    ok "venv already exists"
fi

# Install dependencies
if [ -f "requirements.txt" ]; then
    ./venv/bin/pip install -q -r requirements.txt 2>/dev/null
    ok "Dependencies installed from requirements.txt"
else
    ./venv/bin/pip install -q litellm openai 2>/dev/null
    ok "Dependencies installed (litellm, openai)"
fi

cd "$REPO_DIR"

# ─── Step 7: Build skills index ─────────────────────────────
log "Step 7: Building skills index..."
if [ -n "${JINA_API_KEY:-}" ]; then
    python3 "$REPO_DIR/agent/scripts/build-skills-index.py"
    ok "Skills index built (Jina AI)"
else
    JINA_API_KEY="" python3 "$REPO_DIR/agent/scripts/build-skills-index.py"
    ok "Skills index built (local model fallback)"
fi

# ─── Step 8: Verification ───────────────────────────────────
log "Step 8: Running verification..."
bash "$REPO_DIR/verify.sh"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  🪨 FORGE Stack — Bootstrap COMPLETE!       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Fill in API keys:  cp .env.example .env && nano .env"
echo "  2. Re-run bootstrap:  bash bootstrap.sh"
echo "  3. Open Antigravity IDE and refresh MCP servers"
echo ""
