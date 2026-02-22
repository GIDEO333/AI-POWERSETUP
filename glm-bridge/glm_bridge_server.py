#!/usr/bin/env python3
"""FORGE — GLM Bridge MCP Server v1.1.0.

Single-shot LLM proxy for Cipher. Uses LiteLLM to call z.ai GLM-4.7
via OpenAI-compatible API for code analysis and debugging.

Transport: stdio (JSON-RPC 2.0)
Backend: LiteLLM → z.ai Coding Plan

NOTE: This is a pass-through bridge to GLM-4.7, NOT a recursive reasoning engine.
For true Recursive Language Model (RLM), see future implementation.

v1.1.0: Added argument validation, timeout guard, specific exception handling.
"""

import json
import os
import sys

# Config from environment (set by cipher.yml)
API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.z.ai/api/coding/paas/v4")
MODEL = os.environ.get("GLM_BRIDGE_MODEL", "openai/glm-4.7")
TIMEOUT = int(os.environ.get("GLM_BRIDGE_TIMEOUT", "15"))

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
            timeout=TIMEOUT,
        )
        return response.choices[0].message.content
    except litellm.Timeout:
        return f"[GLM Bridge] Request timeout (>{TIMEOUT}s). Coba lagi atau periksa koneksi."
    except litellm.AuthenticationError:
        return "[GLM Bridge] API key tidak valid atau kuota habis."
    except Exception as e:
        return f"[GLM Bridge Error] {type(e).__name__}: {str(e)[:200]}"


def reason(problem):
    """Send a complex problem to GLM-4.7 for deep analysis (single-shot)."""
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
        return f"GLM Bridge Error: {str(e)}"


def verify(code, context=""):
    """Verify code for correctness, security, and best practices (single-shot)."""
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
        return f"GLM Bridge Verify Error: {str(e)}"


class GLMBridgeServer:
    """MCP Server for GLM Bridge — communicates via stdin/stdout JSON-RPC 2.0."""

    TOOLS = [
        {
            "name": "reason",
            "description": "Kirim masalah coding kompleks ke GLM-4.7 untuk analisis mendalam. Gunakan untuk debugging sulit atau review arsitektur.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Deskripsi masalah yang perlu dianalisis secara mendalam"
                    }
                },
                "required": ["problem"]
            }
        },
        {
            "name": "verify",
            "description": "Kirim kode ke GLM-4.7 untuk verifikasi correctness, security, dan best practices.",
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
                "serverInfo": {"name": "glm-bridge", "version": "1.1.0"}
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
                    "content": [{"type": "text", "text": f"[GLM Bridge Validation] {error_msg}"}]
                }}

            if tool_name == "reason":
                result = reason(args.get("problem", ""))
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
    GLMBridgeServer().run()
