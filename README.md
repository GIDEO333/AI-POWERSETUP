# 🪨 AI-POWERSETUP — FORGE Stack v3.0 (macOS)

Deterministic bootstrap for an agentic AI coding stack with **True RLM** (Recursive Language Model) capabilities.

## Quick Start

```bash
git clone https://github.com/GIDEO333/AI-POWERSETUP.git
cd AI-POWERSETUP
cp .env.example .env    # Fill in API keys
bash bootstrap.sh       # 13/13 checks = ready
```

## Architecture

```
Antigravity IDE (Gemini)
    ├── skills-search (MCP) ──→ Semantic RAG (11 skills, Jina AI)
    ├── sequential-thinking (MCP)
    └── switchboard (MCP) ──→ Aggregator Hub
        ├── glm-bridge v3.0 ──→ z.ai GLM-4.7
        │     ├── reason     → Peek Gate + Self-Refine
        │     ├── verify     → Code review + Flash second opinion
        │     └── deep_reason → True RLM pipeline ★
        ├── forge-repl v1.0 ──→ Sandboxed Python execution
        └── exa (optional) ──→ Web search
```

## GLM Bridge v3.0 — Pipeline

```
Request masuk
    │
    ▼
🚦 Peek First Gate (Flash, FREE)
    │ Classify: SIMPLE / COMPLEX
    │
    ├─ SIMPLE ──→ GLM-4.7 jawab langsung (1 quota, 512 tokens)
    │
    └─ COMPLEX ──→ Full Self-Refine pipeline:
         │
         ├─ GLM-4.7 generate answer ──→ 1 quota
         ├─ Flash critique (FREE) ──→ LGTM? selesai
         └─ GLM-4.7 refine jika ada issue ──→ +1 quota
```

### deep_reason (True RLM)

```
Problem + Large Context (codebase/log)
    │
    ▼
Phase 1: GLM-4.7 writes Python exploration strategy   ← 1 quota
Phase 2: Python subprocess executes (grep/filter)     ← 0 quota
Phase 3: Flash processes extracted chunks              ← 0 quota (FREE)
Phase 4: GLM-4.7 synthesizes final answer              ← 1 quota
    │
    ▼
Total: 2 premium quota + unlimited free Flash
```

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| GLM Bridge v3.0 | `glm-bridge/glm_bridge_server.py` | Self-Refine + True RLM proxy |
| forge-repl v1.0 | `forge-repl/forge_repl_server.py` | Sandboxed Python execution (10s timeout) |
| Skills Search | `agent/scripts/skills-search-server.py` | Semantic skill matching (11 skills) |
| Cipher Config | `openclaw/cipher/cipher.yml` | LLM orchestration config |
| 11 Skills | `agent/skills/skills/*/SKILL.md` | Agent SOP library |

## Required API Keys

| Key | Service | Required? | Purpose |
|-----|---------|-----------|---------|
| `ZAI_API_KEY` | z.ai (coding plan) | ✅ Yes | GLM-4.7 premium reasoning |
| `ZAI_FLASH_API_KEY` | z.ai (free tier) | ✅ Yes | Flash critique + Peek Gate (free) |
| `JINA_API_KEY` | Jina AI | Optional | Semantic embedding (has local fallback) |
| `EXA_API_KEY` | Exa | Optional | Web search |

## What `bootstrap.sh` Does

1. Creates 4 symlinks (`~/.agent/scripts`, `~/.agent/skills`, `~/.openclaw`, `~/.switchboard`)
2. Generates `~/.gemini/antigravity/mcp_config.json` with absolute paths
3. Patches 3 switchboard sub-MCP configs (glm-bridge, exa, forge-repl)
4. Creates Python venv + installs GLM Bridge dependencies
5. Builds semantic skills index (Jina AI or local model fallback)
6. Runs 13-point verification audit

## Verify

```bash
bash verify.sh
# Expected: 13/13 checks passed 🪨
```

## Resilience

- **Flash key not set?** → Self-Refine disabled, works as single-shot
- **Flash rate limited?** → Auto-retry with 5s/10s backoff
- **Jina API down?** → Falls back to local embedding model
- **REPL script fails?** → deep_reason falls back to truncated context + regular reason
- **Timeout?** → 90s limit, returns error instead of hanging
