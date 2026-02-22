#!/usr/bin/env python3
"""FORGE — GLM Bridge MCP Server v3.0.0.

LLM proxy with Self-Refine + True RLM capabilities.
- reason(): Peek Gate + Self-Refine (premium + flash)
- verify(): Code review with flash second opinion
- deep_reason(): RLM-style pipeline — REPL exploration + Flash chunks + Premium synthesis

Transport: stdio (JSON-RPC 2.0)
Backend: LiteLLM → z.ai

v3.0.0: True RLM — deep_reason (REPL + Flash sub-calls + Premium synthesis)
v2.0.0: Self-Refine + Peek First Gate
v1.1.0: Argument validation, timeout guard
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
    "deep_reason": ["problem"],
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

def llm_call(messages, max_tokens=2048, use_flash=False, retries=2):
    """Call LLM via LiteLLM with retry on rate limit."""
    import litellm
    import time as _time

    if use_flash and FLASH_API_KEY:
        key = FLASH_API_KEY
        base = FLASH_API_BASE
        model = FLASH_MODEL
    else:
        key = API_KEY
        base = API_BASE
        model = MODEL

    for attempt in range(retries + 1):
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
            estr = str(e).lower()
            # Retry on rate limit (z.ai error 1302)
            if ("rate limit" in estr or "1302" in estr) and attempt < retries:
                _time.sleep(5 * (attempt + 1))  # 5s, 10s backoff
                continue
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


# ── Peek First Gate ──────────────────────────────────────────

def peek_first_gate(problem):
    """Classify problem complexity via Flash (free). Returns 'SIMPLE' or 'COMPLEX'."""
    if not FLASH_API_KEY:
        return "COMPLEX"  # Default to full pipeline if Flash unavailable

    gate_prompt = f"""Classify this coding problem as SIMPLE or COMPLEX.

SIMPLE = one-liner fix, syntax error, simple question, config change, typo
COMPLEX = multi-file debugging, architecture design, algorithm, security audit, refactoring

Problem: {problem[:500]}

Respond with ONLY one word: SIMPLE or COMPLEX"""

    messages = [
        {"role": "system", "content": "Classify coding problems. Reply with one word only."},
        {"role": "user", "content": gate_prompt}
    ]

    try:
        result = llm_call(messages, max_tokens=10, use_flash=True)
        if result and "SIMPLE" in result.upper():
            return "SIMPLE"
        return "COMPLEX"
    except Exception:
        return "COMPLEX"  # Default safe


# ── Tool Functions ───────────────────────────────────────────

SIMPLE_PROMPT = """You are a coding assistant. Answer concisely and directly."""

COMPLEX_PROMPT = """Anda adalah Reasoning Engine untuk coding agent.
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


def reason(problem):
    """Deep analysis with Peek First Gate + Self-Refine."""

    # Step 0: Peek First Gate (Flash, free) — classify complexity
    complexity = peek_first_gate(problem)

    if complexity == "SIMPLE":
        # Simple path: smaller prompt, fewer tokens, no refinement
        messages = [
            {"role": "system", "content": SIMPLE_PROMPT},
            {"role": "user", "content": problem}
        ]
        return llm_call(messages, max_tokens=512)

    # Complex path: full reasoning + Self-Refine
    messages = [
        {"role": "system", "content": COMPLEX_PROMPT},
        {"role": "user", "content": problem}
    ]

    try:
        # Step 1: Generate (premium, 1 quota)
        draft = llm_call(messages, max_tokens=2048)

        if not SELF_REFINE or not FLASH_API_KEY:
            return draft

        # Step 2: Critique via Flash (free, 0 quota)
        for i in range(MAX_REFINE):
            critique = flash_critique(problem, draft)

            if critique is None or "LGTM" in critique.upper():
                break

            # Step 3: Refine (premium, 1 more quota — only if issues found)
            refine_prompt = f"""Your previous answer had these issues:

{critique}

Original problem: {problem[:1000]}

Your previous answer:
{draft[:3000]}

Provide a CORRECTED and IMPROVED answer. Keep the same format."""

            messages_refine = [
                {"role": "system", "content": COMPLEX_PROMPT},
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


# ── Python Sandbox (inline, for RLM) ────────────────────────

def run_python(code, timeout=10):
    """Execute Python code in subprocess, return stdout+stderr."""
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp = f.name

    try:
        r = subprocess.run(
            [sys.executable, tmp],
            capture_output=True, text=True, timeout=timeout,
            cwd=os.path.expanduser("~"),
            env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")}
        )
        out = ""
        if r.stdout:
            out += r.stdout[:6000]
        if r.stderr:
            out += f"\nSTDERR: {r.stderr[:2000]}"
        return out.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return f"[Timeout after {timeout}s]"
    except Exception as e:
        return f"[Error: {e}]"
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


# ── True RLM: deep_reason ────────────────────────────────────

def deep_reason(problem, context=""):
    """RLM-style reasoning: REPL exploration + Flash chunk processing + Premium synthesis.

    Pipeline:
      1. Premium writes Python to explore/filter the context (1 quota)
      2. Subprocess executes the Python code (0 quota)
      3. Flash processes extracted chunks (0 quota, free)
      4. Premium synthesizes final answer from all findings (1 quota)

    Total cost: 2 premium quota + unlimited free Flash calls
    """
    if not FLASH_API_KEY:
        # Fallback to regular reason if Flash not available
        return reason(problem)

    # ── Phase 1: Strategy Generation (Premium, 1 quota) ──────
    strategy_prompt = f"""You are an RLM (Recursive Language Model) Root controller.

PROBLEM: {problem[:2000]}

CONTEXT SIZE: {len(context)} characters (~{len(context)//4} tokens)

Your job: Write a Python script that will explore and extract the most relevant 
parts of the context. The context is available as variable `CONTEXT` in the script.

Rules:
- Print ONLY the relevant extracted portions (max 5000 chars output)
- Use regex, string search, line filtering — NOT LLM calls
- The script must be self-contained Python (no external deps)
- Focus on what's needed to answer the problem
- If context is small (<2000 chars), just print it all

Output ONLY the Python code, nothing else. No markdown fences."""

    if len(context) < 2000:
        # Context is small enough — skip REPL, go straight to reasoning
        combined = f"Problem: {problem}\n\nContext:\n{context}"
        return reason(combined)

    messages = [
        {"role": "system", "content": "You write Python scripts to analyze data. Output only code."},
        {"role": "user", "content": strategy_prompt}
    ]

    strategy_code = llm_call(messages, max_tokens=1024)

    # Clean code (remove markdown fences if model added them)
    strategy_code = strategy_code.strip()
    if strategy_code.startswith("```"):
        lines = strategy_code.split("\n")
        strategy_code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    # Inject the context as a variable
    full_script = f'''CONTEXT = """{context[:50000]}"""\n\n{strategy_code}'''

    # ── Phase 2: Execute Strategy (0 quota) ──────────────────
    repl_output = run_python(full_script, timeout=10)

    if "[Timeout" in repl_output or "[Error" in repl_output:
        # Strategy failed — fallback: just truncate context and reason directly
        combined = f"Problem: {problem}\n\nContext (truncated):\n{context[:4000]}"
        return reason(combined)

    # ── Phase 3: Flash Chunk Processing (FREE) ───────────────
    # If REPL output is large, use Flash to summarize/extract key findings
    if len(repl_output) > 3000:
        chunk_prompt = f"""Extract the key findings relevant to this problem:

PROBLEM: {problem[:500]}

DATA:
{repl_output[:6000]}

List only the most important findings (max 5 bullet points)."""

        chunk_messages = [
            {"role": "system", "content": "Extract key findings concisely."},
            {"role": "user", "content": chunk_prompt}
        ]
        findings = llm_call(chunk_messages, max_tokens=512, use_flash=True)
    else:
        findings = repl_output

    # ── Phase 4: Synthesis (Premium, 1 quota) ────────────────
    synthesis_prompt = f"""Based on the following analysis, provide a complete solution.

ORIGINAL PROBLEM:
{problem[:2000]}

FINDINGS FROM DATA ANALYSIS:
{findings[:4000]}

Provide a comprehensive answer with:
## Analisis
## Root Cause / Komponen
## Solusi
## Kode (if applicable)"""

    synthesis_messages = [
        {"role": "system", "content": COMPLEX_PROMPT},
        {"role": "user", "content": synthesis_prompt}
    ]

    result = llm_call(synthesis_messages, max_tokens=2048)
    return result


# ── MCP Server ───────────────────────────────────────────────

class GLMBridgeServer:
    """MCP Server for GLM Bridge v3 — Self-Refine + True RLM."""

    TOOLS = [
        {
            "name": "reason",
            "description": "Analisis masalah coding via GLM-4.7. Peek Gate → Self-Refine. Untuk pertanyaan umum dan debugging.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Deskripsi masalah yang perlu dianalisis"
                    }
                },
                "required": ["problem"]
            }
        },
        {
            "name": "verify",
            "description": "Verifikasi kode untuk correctness, security, dan best practices.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Kode yang perlu diverifikasi"
                    },
                    "context": {
                        "type": "string",
                        "description": "Konteks tambahan",
                        "default": ""
                    }
                },
                "required": ["code"]
            }
        },
        {
            "name": "deep_reason",
            "description": "RLM-style deep analysis untuk masalah dengan konteks besar. Pipeline: Premium → REPL exploration → Flash chunk processing (free) → Premium synthesis. Gunakan saat ada codebase/log/dokumen besar yang perlu dianalisis.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Masalah yang perlu dianalisis secara mendalam"
                    },
                    "context": {
                        "type": "string",
                        "description": "Konteks besar (codebase, log, dokumen) yang perlu dianalisis",
                        "default": ""
                    }
                },
                "required": ["problem"]
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
                "serverInfo": {
                    "name": "glm-bridge",
                    "version": "3.0.0",
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
            elif tool_name == "deep_reason":
                result = deep_reason(args.get("problem", ""), args.get("context", ""))
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
        mode = "RLM" if (SELF_REFINE and FLASH_API_KEY) else "Single-shot"
        sys.stderr.write(f"[GLM Bridge v3.0] Mode: {mode} | Model: {MODEL}\n")
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
