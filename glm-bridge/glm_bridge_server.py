#!/usr/bin/env python3
"""FORGE — GLM Bridge MCP Server v2.0.0.

LLM proxy with Self-Refine capability. Uses GLM-4.7 (premium) for generation
and GLM-4.7-Flash (free) for self-critique, reducing hallucinations without
burning quota.

Transport: stdio (JSON-RPC 2.0)
Backend: LiteLLM → z.ai

v2.0.0: Self-Refine — generate (premium) → critique (flash/free) → refine
v1.1.0: Added argument validation, timeout guard, specific exception handling
"""

import json
import os
import sys
import logging

# Suppress LiteLLM noise
logging.getLogger("LiteLLM").setLevel(logging.WARNING)

# ── Config ───────────────────────────────────────────────────
# Premium model (uses coding plan quota)
API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.z.ai/api/coding/paas/v4")
MODEL = os.environ.get("GLM_BRIDGE_MODEL", "openai/glm-4.7")

# Flash model (free tier — separate key, PAAS endpoint)
FLASH_API_KEY = os.environ.get("GLM_FLASH_API_KEY", "")
FLASH_API_BASE = os.environ.get("GLM_FLASH_API_BASE", "https://api.z.ai/api/paas/v4")
FLASH_MODEL = os.environ.get("GLM_FLASH_MODEL", "glm-4.7-flash")

# Self-Refine settings
SELF_REFINE = os.environ.get("GLM_BRIDGE_SELF_REFINE", "true").lower() == "true"
MAX_REFINE = int(os.environ.get("GLM_BRIDGE_MAX_REFINE", "1"))  # max critique rounds
TIMEOUT = int(os.environ.get("GLM_BRIDGE_TIMEOUT", "30"))

# ── Argument validation ─────────────────────────────────────
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
    return None


# ── LLM Calls ────────────────────────────────────────────────

def llm_call(messages, max_tokens=2048, use_flash=False):
    """Call LLM via LiteLLM. use_flash=True routes to free Flash model."""
    import litellm

    if use_flash and FLASH_API_KEY:
        key = FLASH_API_KEY
        base = FLASH_API_BASE
        model = FLASH_MODEL
    else:
        key = API_KEY
        base = API_BASE
        model = MODEL

    try:
        response = litellm.completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            api_key=key,
            api_base=base,
            extra_headers={"Accept-Language": "en-US,en"},
            timeout=TIMEOUT,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        etype = type(e).__name__
        return f"[GLM Bridge Error] {etype}: {str(e)[:200]}"


def flash_critique(original_problem, draft_answer):
    """Send draft to Flash (free) for critique. Returns critique or None."""
    if not FLASH_API_KEY:
        return None  # Flash not configured, skip refinement

    critique_prompt = f"""Review this AI-generated answer for a coding problem.

PROBLEM:
{original_problem[:2000]}

DRAFT ANSWER:
{draft_answer[:4000]}

Your task: Identify ONLY genuine errors, bugs, or missing critical steps.
If the answer is already good, respond with exactly: LGTM
If there are real issues, list them as bullet points (max 3).
Be concise. Do NOT rewrite the solution."""

    messages = [
        {"role": "system", "content": "You are a code reviewer. Be concise and precise. Only flag real issues."},
        {"role": "user", "content": critique_prompt}
    ]

    try:
        result = llm_call(messages, max_tokens=512, use_flash=True)
        if not result or "[GLM Bridge Error]" in result:
            return None
        return result
    except Exception:
        return None  # Flash failed, proceed without refinement


# ── Tool Functions ───────────────────────────────────────────

def reason(problem):
    """Deep analysis with optional Self-Refine via Flash critique."""
    system_prompt = """Anda adalah Reasoning Engine untuk coding agent.
Tugas Anda: Analisis masalah secara SISTEMATIS:
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
        # Step 1: Generate (premium, 1 quota)
        draft = llm_call(messages, max_tokens=2048)

        if not SELF_REFINE or not FLASH_API_KEY:
            return draft  # No refinement, return as-is

        # Step 2: Critique via Flash (free, 0 quota)
        for i in range(MAX_REFINE):
            critique = flash_critique(problem, draft)

            if critique is None or "LGTM" in critique.upper():
                break  # Flash says it's good, or Flash unavailable

            # Step 3: Refine (premium, 1 more quota — only if real issues found)
            refine_prompt = f"""Your previous answer had these issues identified by a reviewer:

{critique}

Original problem: {problem[:1000]}

Your previous answer:
{draft[:3000]}

Please provide a CORRECTED and IMPROVED answer. Keep the same format."""

            messages_refine = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": refine_prompt}
            ]
            draft = llm_call(messages_refine, max_tokens=2048)

        return draft

    except Exception as e:
        return f"GLM Bridge Error: {str(e)}"


def verify(code, context=""):
    """Verify code with optional Flash double-check."""
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

        # Optional: Flash second opinion (free)
        if SELF_REFINE and FLASH_API_KEY:
            critique = flash_critique(
                f"Verify this code: {context}",
                result
            )
            if critique and "LGTM" not in critique.upper():
                result += f"\n\n---\n### 🔍 Second Opinion (Flash)\n{critique}"

        return result
    except Exception as e:
        return f"GLM Bridge Verify Error: {str(e)}"


# ── MCP Server ───────────────────────────────────────────────

class GLMBridgeServer:
    """MCP Server for GLM Bridge v2 — Self-Refine enabled."""

    TOOLS = [
        {
            "name": "reason",
            "description": "Analisis mendalam masalah coding via GLM-4.7 dengan Self-Refine. Generate → Flash critique (free) → Refine jika ada issue.",
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
            "description": "Verifikasi kode untuk correctness, security, dan best practices. Termasuk Flash second opinion.",
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
            refine_status = "enabled" if (SELF_REFINE and FLASH_API_KEY) else "disabled"
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "glm-bridge",
                    "version": "2.0.0",
                }
            }}
        elif method == "notifications/initialized":
            return None
        elif method == "tools/list":
            return {"jsonrpc": "2.0", "id": rid, "result": {"tools": self.TOOLS}}
        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name", "")
            args = params.get("arguments", {})

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
        # Log startup info to stderr (not stdout, which is for JSON-RPC)
        mode = "Self-Refine ON" if (SELF_REFINE and FLASH_API_KEY) else "Single-shot"
        sys.stderr.write(f"[GLM Bridge v2.0] Mode: {mode} | Model: {MODEL}\n")
        sys.stderr.flush()

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
