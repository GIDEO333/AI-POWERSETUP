#!/usr/bin/env python3
"""FORGE — RLM (Reasoning Layer Module) MCP Server v1.1.0.

Multi-step reasoning engine for Cipher. Uses LiteLLM to call z.ai GLM-4.7
via OpenAI-compatible API for deep code analysis and complex debugging.

Transport: stdio (JSON-RPC 2.0)
Backend: LiteLLM → z.ai Coding Plan

v1.1.0: Added argument validation, timeout guard, specific exception handling.
"""

import json
import os
import sys

# Config from environment (set by cipher.yml)
API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.z.ai/api/coding/paas/v4")
MODEL = os.environ.get("RLM_MODEL", "openai/glm-4.7")
MAX_ITERATIONS = int(os.environ.get("RLM_MAX_ITERATIONS", "10"))

# ── Argument validation schema ───────────────────────────────
REQUIRED_ARGS = {
    "reason": ["problem"],
    "verify": ["code"],
}


def validate_args(tool_name, args):
    """Return error message if args are invalid, None if valid."""
    required = REQUIRED_ARGS.get(tool_name)
    if required is None:
        return f"Unknown tool: '{tool_name}'"
    for field in required:
        val = args.get(field, "")
        if not str(val).strip():
            return f"Argumen '{field}' wajib diisi dan tidak boleh kosong."
    return None  # valid


def llm_call(messages, max_tokens=2048):
    """Call LLM via LiteLLM (supports OpenAI-compatible endpoints)."""
    import litellm
    litellm.api_key = API_KEY
    litellm.api_base = API_BASE

    try:
        response = litellm.completion(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            api_key=API_KEY,
            api_base=API_BASE,
            extra_headers={"Accept-Language": "en-US,en"},
            timeout=15,
        )
        return response.choices[0].message.content
    except litellm.Timeout:
        return "[RLM] Request timeout (>15s). Coba lagi atau periksa koneksi."
    except litellm.AuthenticationError:
        return "[RLM] API key tidak valid atau kuota habis."
    except Exception as e:
        return f"[RLM Error] {type(e).__name__}: {str(e)[:200]}"


def reason(problem, max_steps=None):
    """Multi-step reasoning: break down a complex problem into steps."""
    steps = max_steps or MAX_ITERATIONS
    
    system_prompt = """Anda adalah Reasoning Engine untuk coding agent.
Tugas Anda: Analisis masalah secara SISTEMATIS menggunakan langkah-langkah berikut:
1. Pahami masalah — apa yang diminta?
2. Identifikasi komponen yang terlibat
3. Analisis kemungkinan penyebab (jika debugging)
4. Buat plan solusi step-by-step
5. Berikan implementasi konkret

Format output:
## Analisis
(pemahaman masalah)

## Root Cause / Komponen
(identifikasi akar masalah atau komponen utama)

## Solusi
(langkah-langkah konkret)

## Kode
(implementasi jika diminta)"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": problem}
    ]

    try:
        result = llm_call(messages, max_tokens=2048)
        return result
    except Exception as e:
        return f"RLM Error: {str(e)}"


def verify(code, context=""):
    """Verify code for correctness, security, and best practices."""
    system_prompt = """Anda adalah Code Verifier. Review kode berikut dan berikan:
1. ✅ Apa yang sudah benar
2. ⚠️ Potensi masalah (bug, security, performance)
3. 🔧 Saran perbaikan konkret
Format output dalam markdown."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context: {context}\n\nKode:\n```\n{code}\n```"}
    ]

    try:
        result = llm_call(messages, max_tokens=1024)
        return result
    except Exception as e:
        return f"RLM Verify Error: {str(e)}"


class RLMServer:
    """MCP Server for RLM — communicates via stdin/stdout JSON-RPC 2.0."""

    TOOLS = [
        {
            "name": "reason",
            "description": "Melakukan reasoning mendalam terhadap masalah coding kompleks. Gunakan untuk analisis bug sulit, debugging multi-step, atau review arsitektur.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Deskripsi masalah yang perlu dianalisis secara mendalam"
                    },
                    "max_steps": {
                        "type": "integer",
                        "description": "Maksimal iterasi reasoning (default: 10)",
                        "default": 10
                    }
                },
                "required": ["problem"]
            }
        },
        {
            "name": "verify",
            "description": "Verifikasi kode untuk correctness, security, dan best practices. Gunakan setelah implementasi untuk memastikan kualitas.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Kode yang perlu diverifikasi"
                    },
                    "context": {
                        "type": "string",
                        "description": "Konteks tambahan (apa tujuan kode ini)",
                        "default": ""
                    }
                },
                "required": ["code"]
            }
        }
    ]

    def handle(self, req):
        method = req.get("method", "")
        rid = req.get("id")

        if method == "initialize":
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "rlm-mcp-server", "version": "1.0.0"}
            }}
        elif method == "notifications/initialized":
            return None
        elif method == "tools/list":
            return {"jsonrpc": "2.0", "id": rid, "result": {"tools": self.TOOLS}}
        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name", "")
            args = params.get("arguments", {})

            # Validate arguments before calling LLM
            error_msg = validate_args(tool_name, args)
            if error_msg:
                return {"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": f"[RLM Validation] {error_msg}"}]
                }}

            if tool_name == "reason":
                result = reason(args.get("problem", ""), args.get("max_steps"))
            elif tool_name == "verify":
                result = verify(args.get("code", ""), args.get("context", ""))
            else:
                return {"jsonrpc": "2.0", "id": rid, "error": {
                    "code": -32601, "message": f"Unknown tool: {tool_name}"
                }}

            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": result}]
            }}

        return {"jsonrpc": "2.0", "id": rid, "error": {
            "code": -32601, "message": f"Unknown method: {method}"
        }}

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
                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0", "id": None,
                    "error": {"code": -32603, "message": str(e)}
                }) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    RLMServer().run()
