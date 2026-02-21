#!/usr/bin/env python3
"""FORGE — Embedding Provider (Jina AI primary, local fallback).
Used by skills-search-server.py and build-skills-index.py.
"""

import os, sys, warnings

warnings.filterwarnings("ignore")

# ── Configuration ────────────────────────────────────────────
JINA_API_KEY = os.environ.get("JINA_API_KEY", "")
JINA_MODEL = "jina-embeddings-v3"
JINA_ENDPOINT = "https://api.jina.ai/v1/embeddings"
LOCAL_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

_local_model = None  # lazy load


def _log(msg):
    """Log to stderr so it doesn't interfere with JSON-RPC stdout."""
    print(f"[Embedding] {msg}", file=sys.stderr, flush=True)


def _load_local_model():
    """Load local model only when needed (lazy loading)."""
    global _local_model
    if _local_model is None:
        _log(f"Loading local model: {LOCAL_MODEL_NAME}...")
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer(LOCAL_MODEL_NAME)
        _log(f"Local model loaded (dim={_local_model.get_sentence_embedding_dimension()})")
    return _local_model


def get_embeddings(texts, task="text-matching"):
    """Embed a list of texts. Primary: Jina AI. Fallback: local multilingual model.

    Args:
        texts: List of strings to embed.
        task: Jina task type (text-matching, retrieval.query, etc.)

    Returns:
        List of embedding vectors (list of floats).
    """
    # ── Try Jina AI first ────────────────────────────────────
    if JINA_API_KEY:
        try:
            import requests
            resp = requests.post(
                JINA_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {JINA_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": JINA_MODEL,
                    "input": texts,
                    "task": task,
                },
                timeout=10,
            )
            data = resp.json()

            if "data" in data:
                dim = len(data["data"][0]["embedding"])
                _log(f"✅ Jina AI — {len(texts)} texts, dim={dim}")
                return [item["embedding"] for item in data["data"]]
            else:
                error = data.get("detail", data.get("message", str(data)))
                _log(f"⚠️ Jina error: {error} — falling back to local")

        except Exception as e:
            _log(f"⚠️ Jina unavailable ({type(e).__name__}: {e}) — falling back to local")
    else:
        _log("⚠️ JINA_API_KEY not set — using local model")

    # ── Fallback to local model ──────────────────────────────
    model = _load_local_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    _log(f"✅ Local model — {len(texts)} texts, dim={len(embeddings[0])}")
    return embeddings.tolist()


def get_embedding(text, task="text-matching"):
    """Shortcut for embedding a single text."""
    return get_embeddings([text], task=task)[0]


def get_provider_name():
    """Return the name of the currently active provider (for health checks)."""
    if not JINA_API_KEY:
        return "local"
    try:
        import requests
        resp = requests.post(
            JINA_ENDPOINT,
            headers={"Authorization": f"Bearer {JINA_API_KEY}"},
            json={"model": JINA_MODEL, "input": ["ping"], "task": "text-matching"},
            timeout=5,
        )
        return "jina" if "data" in resp.json() else "local"
    except Exception:
        return "local"
