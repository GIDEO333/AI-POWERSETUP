#!/bin/bash
# ╔══════════════════════════════════════════════════════╗
# ║  Test GLM-4.7-Flash Free Tier — Quota & Limits     ║
# ║  Usage: bash test_flash_free.sh <FREE_TIER_API_KEY> ║
# ╚══════════════════════════════════════════════════════╝

set -uo pipefail
GREEN='\033[0;32m'; RED='\033[0;31m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'

FREE_KEY="${1:-}"
if [ -z "$FREE_KEY" ]; then
    echo -e "${RED}Usage: bash test_flash_free.sh <YOUR_FREE_TIER_API_KEY>${NC}"
    exit 1
fi

PAAS="https://api.z.ai/api/paas/v4/chat/completions"
CODING="https://api.z.ai/api/coding/paas/v4/chat/completions"

call_api() {
    local endpoint="$1" model="$2" label="$3" tokens="${4:-5}"
    local start=$(date +%s)
    local result=$(curl -s -w "\n%{http_code}" -m 30 -X POST "$endpoint" \
        -H "Authorization: Bearer $FREE_KEY" \
        -H "Content-Type: application/json" \
        -H "Accept-Language: en-US,en" \
        -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hello\"}],\"max_tokens\":$tokens}" 2>/dev/null)
    local end=$(date +%s)
    local elapsed=$((end - start))
    
    local http_code=$(echo "$result" | tail -1)
    local body=$(echo "$result" | head -n -1)
    
    if [ "$http_code" = "200" ]; then
        local used_tokens=$(echo "$body" | python3 -c "import sys,json; print(json.load(sys.stdin)['usage']['total_tokens'])" 2>/dev/null || echo "?")
        echo -e "${GREEN}  ✅ $label — HTTP $http_code | ${elapsed}s | ${used_tokens} tokens${NC}"
    else
        local error=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('message','unknown')[:100])" 2>/dev/null || echo "$body" | head -c 100)
        echo -e "${RED}  ❌ $label — HTTP $http_code | ${elapsed}s | $error${NC}"
    fi
}

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  🔬 GLM Flash Free Tier — Live Test Suite       ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ─── Test 1: Basic connectivity ──────────────────────
echo -e "${CYAN}[TEST 1] Basic Connectivity (Flash on PAAS)${NC}"
call_api "$PAAS" "glm-4.7-flash" "PAAS + glm-4.7-flash"

# ─── Test 2: Flash on Coding endpoint ────────────────
echo -e "\n${CYAN}[TEST 2] Flash on Coding Endpoint${NC}"
call_api "$CODING" "glm-4.7-flash" "CODING + glm-4.7-flash"

# ─── Test 3: GLM-4.5-flash (another free model?) ─────
echo -e "\n${CYAN}[TEST 3] GLM-4.5-Flash${NC}"
call_api "$PAAS" "glm-4.5-flash" "PAAS + glm-4.5-flash"

# ─── Test 4: GLM-4.7 premium (should fail or cost $) ─
echo -e "\n${CYAN}[TEST 4] GLM-4.7 Premium (expect reject on free tier)${NC}"
call_api "$PAAS" "glm-4.7" "PAAS + glm-4.7"

# ─── Test 5: Rapid-fire 5x (concurrency test) ────────
echo -e "\n${CYAN}[TEST 5] Rapid-fire 5 sequential calls (rate limit test)${NC}"
for i in 1 2 3 4 5; do
    call_api "$PAAS" "glm-4.7-flash" "Call #$i"
done

# ─── Test 6: >8K token input (throttle test) ─────────
echo -e "\n${CYAN}[TEST 6] Large context (>8K tokens — throttle test)${NC}"
# Generate ~9000 tokens of input
LONG_TEXT=$(python3 -c "print('Hello world. ' * 3000)")
local_start=$(date +%s)
result=$(curl -s -w "\n%{http_code}" -m 120 -X POST "$PAAS" \
    -H "Authorization: Bearer $FREE_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"model\":\"glm-4.7-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"Summarize: $LONG_TEXT\"}],\"max_tokens\":10}" 2>/dev/null)
local_end=$(date +%s)
local_elapsed=$((local_end - local_start))
http=$(echo "$result" | tail -1)
if [ "$http" = "200" ]; then
    tokens=$(echo "$result" | head -n -1 | python3 -c "import sys,json; print(json.load(sys.stdin)['usage']['total_tokens'])" 2>/dev/null || echo "?")
    echo -e "${YELLOW}  ⚠️ Large context — HTTP $http | ${local_elapsed}s | $tokens tokens (>30s = throttled)${NC}"
else
    echo -e "${RED}  ❌ Large context — HTTP $http | ${local_elapsed}s${NC}"
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  📊 Test Complete                               ║"
echo "║  Check z.ai dashboard to see if quota changed   ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
