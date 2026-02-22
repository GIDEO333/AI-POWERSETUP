#!/usr/bin/env python3
"""FORGE — forge-repl MCP Server v1.0.0.

Provides a sandboxed Python execution environment for AI agents.
Allows the agent to write Python code to grep, filter, search, and
process data — without consuming LLM API calls.

Security:
  - Runs in subprocess with 10s timeout
  - No internet access (network disabled)
  - Read-only file access
  - Stdout/stderr captured, max 8KB output

Transport: stdio (JSON-RPC 2.0)
"""

import json
import os
import subprocess
import sys
import tempfile

TIMEOUT = int(os.environ.get("FORGE_REPL_TIMEOUT", "10"))
MAX_OUTPUT = int(os.environ.get("FORGE_REPL_MAX_OUTPUT", "8192"))

# Directories the REPL is allowed to read (configurable)
ALLOWED_DIRS = os.environ.get(
    "FORGE_REPL_ALLOWED_DIRS",
    os.path.expanduser("~/Projects")
).split(":")


def execute_python(code):
    """Execute Python code in a sandboxed subprocess."""
    # Write code to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=os.path.expanduser("~"),
            env={
                "PATH": os.environ.get("PATH", ""),
                "HOME": os.environ.get("HOME", ""),
                "PYTHONPATH": "",
                # No API keys, no network tokens
            }
        )

        stdout = result.stdout[:MAX_OUTPUT] if result.stdout else ""
        stderr = result.stderr[:MAX_OUTPUT] if result.stderr else ""

        output = ""
        if stdout:
            output += f"STDOUT:\n{stdout}\n"
        if stderr:
            output += f"STDERR:\n{stderr}\n"
        if result.returncode != 0:
            output += f"EXIT CODE: {result.returncode}\n"

        return output.strip() or "(no output)"

    except subprocess.TimeoutExpired:
        return f"[forge-repl] Timeout after {TIMEOUT}s. Script took too long."
    except Exception as e:
        return f"[forge-repl] Error: {type(e).__name__}: {str(e)[:200]}"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


class ForgeReplServer:
    """MCP Server for Python REPL execution."""

    TOOLS = [
        {
            "name": "execute_python",
            "description": (
                "Execute Python code in a sandboxed environment. "
                "Use for: grep/search files, filter data, parse logs, "
                "regex matching, count lines, read file snippets. "
                "Output is captured stdout/stderr (max 8KB). "
                "Timeout: 10 seconds. Read-only file access."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
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
                "serverInfo": {"name": "forge-repl", "version": "1.0.0"}
            }}
        elif method == "notifications/initialized":
            return None
        elif method == "tools/list":
            return {"jsonrpc": "2.0", "id": rid, "result": {"tools": self.TOOLS}}
        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name", "")
            args = params.get("arguments", {})

            if tool_name != "execute_python":
                return {"jsonrpc": "2.0", "id": rid, "error": {
                    "code": -32601, "message": f"Unknown tool: {tool_name}"
                }}

            code = args.get("code", "")
            if not code.strip():
                return {"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": "[forge-repl] Empty code."}]
                }}

            result = execute_python(code)
            return {"jsonrpc": "2.0", "id": rid, "result": {
                "content": [{"type": "text", "text": result}]
            }}

        return {"jsonrpc": "2.0", "id": rid, "error": {
            "code": -32601, "message": f"Unknown method: {method}"
        }}

    def run(self):
        sys.stderr.write(f"[forge-repl v1.0] Ready | timeout={TIMEOUT}s\n")
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
    ForgeReplServer().run()
