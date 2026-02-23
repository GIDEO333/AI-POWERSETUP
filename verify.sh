#!/bin/bash
# FORGE Stack — Post-Bootstrap Verification (9 Audits)
# macOS compatible — no GNU timeout needed.
set -uo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
PASS=0; FAIL=0

check() {
    if eval "$2" &>/dev/null; then
        echo -e "${GREEN}  ✅ $1${NC}"; ((PASS++))
    else
        echo -e "${RED}  ❌ $1${NC}"; ((FAIL++))
    fi
}

echo "=== FORGE Verification (9 Checks) ==="

# 1-3: Symlinks exist
check "~/.agent/scripts symlink"    "[ -L ~/.agent/scripts ]"
check "~/.agent/skills symlink"     "[ -L ~/.agent/skills ]"
check "~/.switchboard symlink"      "[ -L ~/.switchboard ]"

# 4: MCP config exists
check "mcp_config.json exists"      "[ -f ~/.gemini/antigravity/mcp_config.json ]"

# 5: GLM Bridge server file exists + syntax valid
check "glm_bridge_server.py OK"     "python3 -c \"import ast; ast.parse(open('$REPO_DIR/glm-bridge/glm_bridge_server.py').read())\""

# 6: Python venv exists
check "Python venv setup"           "[ -f $REPO_DIR/glm-bridge/venv/bin/python3 ]"

# 7: litellm installed
check "litellm installed in venv"   "$REPO_DIR/glm-bridge/venv/bin/python3 -c 'import litellm' 2>/dev/null"

# 8: Skills index exists and has 11 entries
check "skills-index.json (≥11 skills)" "python3 -c \"import json; idx=json.load(open('$REPO_DIR/agent/skills/skills-index.json')); exit(0 if len(idx)>=11 else 1)\""

# 9: All 11 SKILL.md files present
check "≥11 SKILL.md files on disk"   "[ \$(find $REPO_DIR/agent/skills/skills -name 'SKILL.md' | wc -l | tr -d ' ') -ge 11 ]"

echo ""
echo "=== Result: $PASS passed, $FAIL failed (out of 9) ==="
[ $FAIL -eq 0 ] && echo -e "${GREEN}🪨 ALL CHECKS PASSED${NC}" || echo -e "${RED}⚠️ SOME CHECKS FAILED${NC}"
