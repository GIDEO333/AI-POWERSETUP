#!/bin/bash
# FORGE Stack — Post-Bootstrap Verification (11 Audits)
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

echo "=== FORGE Verification (11 Checks) ==="

# 1-4: Symlinks exist and point to repo
check "~/.agent/scripts symlink"    "[ -L ~/.agent/scripts ]"
check "~/.agent/skills symlink"     "[ -L ~/.agent/skills ]"
check "~/.openclaw symlink"         "[ -L ~/.openclaw ]"
check "~/.switchboard symlink"      "[ -L ~/.switchboard ]"

# 5: MCP config exists
check "mcp_config.json exists"      "[ -f ~/.gemini/antigravity/mcp_config.json ]"

# 6: RLM server file exists
check "rlm_mcp_server.py exists"    "[ -f $REPO_DIR/rlm-workspace/rlm_mcp_server.py ]"

# 7: Python venv exists
check "Python venv setup"           "[ -f $REPO_DIR/rlm-workspace/venv/bin/python3 ]"

# 8: litellm installed
check "litellm installed in venv"   "$REPO_DIR/rlm-workspace/venv/bin/python3 -c 'import litellm' 2>/dev/null"

# 9: Skills index exists and has 11 entries
check "skills-index.json (11 skills)" "python3 -c \"import json; idx=json.load(open('$REPO_DIR/agent/skills/skills-index.json')); exit(0 if len(idx)==11 else 1)\""

# 10: All 11 SKILL.md files present
check "11 SKILL.md files on disk"   "[ \$(find $REPO_DIR/agent/skills/skills -name 'SKILL.md' | wc -l | tr -d ' ') -eq 11 ]"

# 11: Switchboard sub-MCPs registered
check "Switchboard has rlm + exa"   "[ -f $REPO_DIR/switchboard/mcps/rlm/.mcp.json ] && [ -f $REPO_DIR/switchboard/mcps/exa/.mcp.json ]"

echo ""
echo "=== Result: $PASS passed, $FAIL failed (out of 11) ==="
[ $FAIL -eq 0 ] && echo -e "${GREEN}🪨 ALL CHECKS PASSED${NC}" || echo -e "${RED}⚠️ SOME CHECKS FAILED${NC}"
