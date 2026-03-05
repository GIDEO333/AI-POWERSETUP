#!/usr/bin/env python3
"""FORGE — Skills Search MCP Server (Semantic Search).
Uses embedding_provider (Jina AI primary, local multilingual fallback).
"""

import json, os, sys
import numpy as np

# Add scripts dir to path for embedding_provider import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from embedding_provider import get_embedding, get_provider_name

INDEX_PATH = os.path.expanduser("~/.agent/skills/skills-index.json")


class SemanticSearch:
    def __init__(self, documents):
        self.docs = documents
        # Pre-load corpus embeddings as numpy array for fast cosine similarity
        self.corpus_embeddings = np.array(
            [d["embedding"] for d in documents if "embedding" in d],
            dtype=np.float32,
        )
        # Normalize for fast cosine similarity via dot product
        norms = np.linalg.norm(self.corpus_embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # avoid division by zero
        self.corpus_embeddings = self.corpus_embeddings / norms

    def search(self, query, top_k=5):
        # Encode query via embedding_provider (Jina or local)
        query_emb = np.array(get_embedding(query), dtype=np.float32)
        query_emb = query_emb / (np.linalg.norm(query_emb) or 1)

        # Cosine similarity via dot product (vectors are normalized)
        scores = self.corpus_embeddings @ query_emb

        # Get top_k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for i in top_indices:
            score = float(scores[i])
            if score > 0.25:  # threshold: lowered for cross-lingual matching
                doc = self.docs[i]
                results.append({
                    "id": doc["id"],
                    "name": doc["name"],
                    "description": doc["description"],
                    "path": doc["path"],
                    "score": round(score, 3)
                })
        return results


SEARCH_TOOL = {
    "name": "search_skills",
    "description": "Semantic search for agent skills by meaning. Returns relevant skills with path and similarity score. Supports Indonesian and English queries.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Natural language search query"},
            "top_k": {"type": "integer", "default": 3}
        },
        "required": ["query"]
    }
}

SWITCH_TOOL = {
    "name": "switch_embedding_provider",
    "description": "Switch embedding provider between 'jina' (API, multilingual) and 'local' (offline, multilingual). Use when Jina API quota is exhausted or unavailable.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "provider": {"type": "string", "description": "'jina' or 'local'"}
        },
        "required": ["provider"]
    }
}

SHOW_WORKFLOWS_TOOL = {
    "name": "show_all_workflows",
    "description": "Show all available workflows, their descriptions, and value ratings.",
    "inputSchema": {
        "type": "object",
        "properties": {}
    }
}

LIST_SKILLS_TOOL = {
    "name": "list_skills",
    "description": "List all 39+ agent skills. Categories: Dev (api-design, create-project, database-query, refactor-code, write-tests), Debug (debug-code, optimize-performance), Ops (docker-security-audit, docker-setup, git-workflow, headless-cli-wrapper, powersetup-healthcheck, safe-push, safe-rollback, sandbox-executor-setup), AI-Orchestration (agent-constraint-schema, claude-agent-teams, multi-agent-orchestrator), QA (ai-system-evaluator, code-review, llm-eval-arena, project-audit, query-scorecard, source-truth-check), Memory (recall-memory, session-export, session-memory), Format (brainstorm-refiner, normalize-input), Research (deep-research, query-requestout), Meta (forge-to-claude, gemini-rules-toggle, meta-levelup, skill-creator, skills-hunter-session, token-budget, workflow-guide), App-Specific (nanoclaw-login). Call for full catalog.",
    "inputSchema": {
        "type": "object",
        "properties": {}
    }
}


class Server:
    def __init__(self):
        self.index = json.load(open(INDEX_PATH)) if os.path.exists(INDEX_PATH) else []
        has_embeddings = self.index and "embedding" in self.index[0]
        self.search_engine = SemanticSearch(self.index) if has_embeddings else None

    def handle(self, req):
        m = req.get("method", "")
        rid = req.get("id")

        if m == "initialize":
            provider = get_provider_name()
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "skills-search",
                    "version": "3.0.0",
                    "embeddingProvider": provider,
                }
            }}
        elif m == "notifications/initialized":
            return None
        elif m == "tools/list":
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "tools": [SEARCH_TOOL, SWITCH_TOOL, SHOW_WORKFLOWS_TOOL, LIST_SKILLS_TOOL]
            }}
        elif m == "tools/call":
            p = req.get("params", {})
            tool_name = p.get("name", "")
            a = p.get("arguments", {})

            if tool_name == "search_skills":
                query = a.get("query", "").strip()
                if not query:
                    return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps({
                        "error": "Query cannot be empty."
                    })}]}}
                if not self.search_engine:
                    return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps({
                        "error": "No embeddings found. Run build-skills-index.py first."
                    })}]}}
                results = self.search_engine.search(query, a.get("top_k", 3))
                return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": json.dumps({
                    "query": query, "count": len(results),
                    "results": results,
                    "hint": "Use view_file on the path to read full SKILL.md"
                }, indent=2)}]}}

            elif tool_name == "switch_embedding_provider":
                import embedding_provider
                provider = a.get("provider", "").lower()
                if provider == "local":
                    embedding_provider.JINA_API_KEY = ""
                    return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text":
                        f"✅ Switched to LOCAL embedding ({embedding_provider.LOCAL_MODEL_NAME}). "
                        f"Note: query embeddings will now use local model. "
                        f"Index embeddings remain from build time — rebuild if needed."
                    }]}}
                elif provider == "jina":
                    # Re-read key from environment
                    key = os.environ.get("JINA_API_KEY", "")
                    if not key:
                        return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text":
                            "❌ JINA_API_KEY not found in environment. Cannot switch to Jina."
                        }]}}
                    embedding_provider.JINA_API_KEY = key
                    return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text":
                        f"✅ Switched to JINA AI ({embedding_provider.JINA_MODEL}). Key: ...{key[-6:]}"
                    }]}}
                else:
                    return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text":
                        "❌ Provider must be 'jina' or 'local'."
                    }]}}

            elif tool_name == "show_all_workflows":
                workflow_dir = os.path.expanduser("~/.agent/workflows")
                results = []
                if os.path.exists(workflow_dir):
                    for fname in os.listdir(workflow_dir):
                        if fname.endswith(".md"):
                            path = os.path.join(workflow_dir, fname)
                            cmd = f"/{fname[:-3]}"
                            desc = ""
                            val = ""
                            try:
                                with open(path, "r", encoding="utf-8") as f:
                                    in_frontmatter = False
                                    for line in f:
                                        sline = line.strip()
                                        if sline == "---":
                                            in_frontmatter = not in_frontmatter
                                            continue
                                        if in_frontmatter:
                                            if sline.startswith("description:"):
                                                desc = sline.partition("description:")[2].strip()
                                            elif sline.startswith("value:"):
                                                val = sline.partition("value:")[2].strip()
                            except Exception:
                                pass
                            results.append({"command": cmd, "description": desc, "value": val})
                
                md = "### Available Workflows\n\n| Workflow Command | Value | Description |\n|---|---|---|\n"
                for r in sorted(results, key=lambda x: x["command"]):
                    md += f"| `{r['command']}` | {r['value']} | {r['description']} |\n"
                
                if not results:
                    md = "No workflows found in ~/.agent/workflows/"
                    
                return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": md}]}}

            elif tool_name == "list_skills":
                if not self.index:
                    return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text":
                        "No skills indexed. Run build-skills-index.py first."
                    }]}}
                lines = [f"📦 {len(self.index)} Skills Available:"]
                for doc in sorted(self.index, key=lambda x: x.get("name", "")):
                    name = doc.get("name", doc.get("id", "unknown"))
                    desc = doc.get("description", "").strip()
                    # Truncate to first sentence or 80 chars for token efficiency
                    if len(desc) > 80:
                        desc = desc[:77] + "..."
                    lines.append(f"- {name}: {desc}")
                lines.append("\nUse `search_skills(query)` for semantic match or `view_file` on skill path for full instructions.")
                return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": "\n".join(lines)}]}}

        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"Unknown: {m}"}}

    def run(self):
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                resp = self.handle(json.loads(line))
                if resp:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    Server().run()
