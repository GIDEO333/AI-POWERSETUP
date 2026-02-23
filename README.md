# 🪨 AI-POWERSETUP — FORGE Stack v3.3 (macOS)

Deterministic bootstrap for an agentic AI coding stack with **Self-Refine** via GLM-4.7.

## Quick Start

```bash
git clone https://github.com/GIDEO333/AI-POWERSETUP.git
cd AI-POWERSETUP
cp .env.example .env    # Fill in API keys (see table below)
bash bootstrap.sh       # 9/9 checks = ready
```

Then open **Antigravity IDE** → Refresh MCP servers → start coding.

> **New to this repo?** Just tell the AI agent: *"bantu saya setup project ini"* — it will read this README and guide you step-by-step.

## Architecture

```
Antigravity IDE (Gemini 2.5 Pro)
    ├── sequential-thinking (MCP) ──→ Chain-of-Thought reasoning
    ├── skills-search (MCP) ──→ Semantic RAG (14 skills, Jina AI 1024-dim)
    │       ├── search_skills        → find relevant skills
    │       ├── switch_embedding     → jina ↔ local fallback
    │       └── show_all_workflows   → list all slash commands
    └── switchboard (MCP) ──→ Aggregator Hub (4 sub-MCPs)
            ├── glm-bridge  ──→ z.ai GLM-4.7 (Self-Refine reasoning)
            ├── fetch       ──→ Web scraper
            ├── puppeteer   ──→ Headless browser automation
            └── sqlite      ──→ Database access (Quant)
```

## GLM Bridge — Self-Refine Pipeline

```
Request → GLM-4.7 generates answer (1 quota)
            │
            ▼
       Flash critique (FREE, glm-4.7-flash)
            │
            ├── LGTM → done ✅
            └── Issues found → GLM-4.7 refines (+1 quota)
```

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| GLM Bridge v3.2 | `glm-bridge/glm_bridge_server.py` | Self-Refine LLM proxy |
| Skills Search | `agent/scripts/skills-search-server.py` | Semantic skill matching (14 skills) |
| 14 Skills | `agent/skills/skills/*/SKILL.md` | Agent SOP library |
| 3 Workflows | `.agent/workflows/*.md` | Slash command automations |
| Bootstrap | `bootstrap.sh` | One-command deterministic setup |
| Verify | `verify.sh` | 9-check post-install verifier |

## Workflows (Slash Commands)

| Command | Value | Description |
|---------|:-----:|-------------|
| `/safe-push` | ⭐⭐⭐ | Scan secrets + verify before git push |
| `/new-skill` | ⭐⭐⭐ | Create skill + auto rebuild search index |
| `/deep-reason` | ⭐⭐ | Deep analysis via GLM Bridge Self-Refine |

## Skills (14)

`api-design` · `code-review` · `create-project` · `database-query` · `debug-code` · `docker-setup` · `git-workflow` · `normalize-input` · `optimize-performance` · `project-audit` · `refactor-code` · `token-budget` · `workflow-guide` · `write-tests`

## Required API Keys

| Key | Required? | Get from | Purpose |
|-----|:---------:|----------|---------|
| `ZAI_API_KEY` | ✅ Yes | [z.ai](https://z.ai/manage-apikey) | GLM-4.7 premium reasoning |
| `ZAI_FLASH_API_KEY` | ✅ Yes | [z.ai](https://z.ai/manage-apikey) (free tier) | Flash critique |
| `JINA_API_KEY` | Optional | [jina.ai](https://jina.ai) | Semantic embedding (has local fallback) |

## Verify

```bash
bash verify.sh
# Expected: 9/9 checks passed 🪨
```

## Resilience

- **Flash key not set?** → Self-Refine disabled, works as single-shot
- **Flash rate limited?** → Auto-retry with 5s/10s backoff
- **Jina API down?** → Falls back to local embedding model (384-dim)
- **Timeout?** → 90s limit, returns error instead of hanging

## Token Efficiency

Stack overhead: **~1,080 tokens/prompt** (0.53% of 202K context window).
Switchboard aggregation saves ~82% vs registering all tools directly.
