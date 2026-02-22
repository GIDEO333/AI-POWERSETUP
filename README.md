# 🪨 AI-POWERSETUP — FORGE Stack (macOS)

One-click deterministic setup for the complete FORGE agentic AI stack.

## Quick Start

```bash
git clone https://github.com/GIDEO333/AI-POWERSETUP.git
cd AI-POWERSETUP
cp .env.example .env
# Edit .env — fill in your API keys
bash bootstrap.sh
```

## What `bootstrap.sh` Does

1. ✅ Symlinks `agent/scripts` → `~/.agent/scripts`
2. ✅ Symlinks `agent/skills` → `~/.agent/skills`
3. ✅ Symlinks `openclaw` → `~/.openclaw`
4. ✅ Symlinks `switchboard` → `~/.switchboard`
5. ✅ Generates `~/.gemini/antigravity/mcp_config.json` (absolute paths)
6. ✅ Creates Python venv + installs GLM Bridge dependencies
7. ✅ Builds semantic skills index (Jina AI or local fallback)
8. ✅ Runs 11-point verification audit

## Architecture

```
Antigravity IDE (Gemini)
    ├── skills-search (MCP) ──→ Jina AI semantic RAG
    ├── sequential-thinking (MCP)
    └── switchboard (MCP) ──→ Aggregator Hub
        ├── glm-bridge ──→ GLM-4.7 via z.ai (reason + verify)
        └── exa ──→ Web search (internet awareness)
```

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| Skills Search | `agent/scripts/skills-search-server.py` | Semantic skill matching (11 skills) |
| Embedding Provider | `agent/scripts/embedding_provider.py` | Jina AI + local fallback |
| GLM Bridge | `glm-bridge/glm_bridge_server.py` | Single-shot LLM proxy to z.ai GLM-4.7 |
| Cipher Config | `openclaw/cipher/cipher.yml` | LLM orchestration config |
| 11 Skills | `agent/skills/skills/*/SKILL.md` | Agent SOP library |

## Required API Keys

| Key | Service | Purpose |
|-----|---------|---------|
| `ZAI_API_KEY` | z.ai | GLM-4.7 LLM access |
| `JINA_API_KEY` | Jina AI | Semantic embedding (primary) |
| `EXA_API_KEY` | Exa (optional) | Internet-aware search |

## Verify Installation

```bash
bash verify.sh
```

Expected: `11/11 checks passed 🪨`
