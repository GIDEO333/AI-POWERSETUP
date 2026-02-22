# 🪨 AI-POWERSETUP — FORGE Stack v3.1 (macOS)

Deterministic bootstrap for an agentic AI coding stack with **Self-Refine** via GLM-4.7.

## Quick Start

```bash
git clone https://github.com/GIDEO333/AI-POWERSETUP.git
cd AI-POWERSETUP
cp .env.example .env    # Fill in API keys
bash bootstrap.sh       # 9/9 checks = ready
```

## Architecture

```
Antigravity IDE (Gemini)
    ├── skills-search (MCP) ──→ Semantic RAG (11 skills, Jina AI)
    ├── sequential-thinking (MCP)
    └── switchboard (MCP) ──→ Aggregator Hub
        └── glm-bridge v3.1 ──→ z.ai GLM-4.7 (Second Brain)
              ├── reason  → Deep analysis + Flash Self-Refine
              └── verify  → Code review + Flash second opinion
```

## GLM Bridge — Self-Refine Pipeline

```
Request → GLM-4.7 generates answer (1 quota)
            │
            ▼
       Flash critique (FREE)
            │
            ├── LGTM → done ✅
            └── Issues found → GLM-4.7 refines (+1 quota)
```

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| GLM Bridge v3.1 | `glm-bridge/glm_bridge_server.py` | Self-Refine LLM proxy |
| Skills Search | `agent/scripts/skills-search-server.py` | Semantic skill matching (11 skills) |
| 11 Skills | `agent/skills/skills/*/SKILL.md` | Agent SOP library |

## Required API Keys

| Key | Required? | Purpose |
|-----|-----------|---------|
| `ZAI_API_KEY` | ✅ Yes | GLM-4.7 premium reasoning |
| `ZAI_FLASH_API_KEY` | ✅ Yes | Flash critique (free tier) |
| `JINA_API_KEY` | Optional | Semantic embedding (has local fallback) |

## Verify

```bash
bash verify.sh
# Expected: 9/9 checks passed 🪨
```

## Resilience

- **Flash key not set?** → Self-Refine disabled, works as single-shot
- **Flash rate limited?** → Auto-retry with 5s/10s backoff
- **Jina API down?** → Falls back to local embedding model
- **Timeout?** → 90s limit, returns error instead of hanging
