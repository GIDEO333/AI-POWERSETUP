#!/usr/bin/env python3
"""LAYER 5: Chaos / Resilience Tests for GLM Bridge MCP Server."""
import json
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(SCRIPT_DIR, "venv/bin/python3")
SERVER_SCRIPT = os.path.join(SCRIPT_DIR, "glm_bridge_server.py")
ZAI_KEY = os.environ.get("ZAI_API_KEY", "")


def run_server(requests, env_overrides=None):
    env = {
        **os.environ,
        "OPENAI_API_KEY": ZAI_KEY,
        "OPENAI_API_BASE": "https://api.z.ai/api/coding/paas/v4",
        "RLM_MODEL": "openai/glm-4.7",
    }
    if env_overrides:
        env.update(env_overrides)

    if isinstance(requests, list):
        input_data = "\n".join(json.dumps(r) if isinstance(r, dict) else r for r in requests) + "\n"
    else:
        input_data = requests + "\n"

    proc = subprocess.run(
        [VENV_PYTHON, SERVER_SCRIPT],
        input=input_data,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    return proc.stdout.strip(), proc.stderr.strip(), proc.returncode


def test_invalid_api_key():
    print("--- Test 5.1: Invalid API Key ---")
    stdout, stderr, code = run_server(
        [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
                "name": "reason", "arguments": {"problem": "test"}
            }}
        ],
        env_overrides={"OPENAI_API_KEY": "invalid-key-12345"}
    )
    lines = [l for l in stdout.split("\n") if l.strip()]
    # Should have init response + error result (not crash)
    crashed = code != 0
    has_error_msg = any("RLM Error" in l or "error" in l.lower() for l in lines)
    if not crashed and len(lines) >= 1:
        print("  ✅ PASS — Server did NOT crash with invalid key")
        for l in lines:
            try:
                d = json.loads(l)
                if "result" in d and "content" in d.get("result", {}):
                    text = d["result"]["content"][0]["text"]
                    print(f"  → Error captured gracefully: {text[:100]}")
            except:
                pass
    else:
        print(f"  ❌ FAIL — Server crashed (exit={code})")
    print()


def test_empty_problem():
    print("--- Test 5.2: Empty Problem String ---")
    stdout, stderr, code = run_server([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "name": "reason", "arguments": {"problem": ""}
        }}
    ])
    crashed = code != 0
    lines = [l for l in stdout.split("\n") if l.strip()]
    if not crashed and len(lines) >= 1:
        print("  ✅ PASS — Server handled empty problem without crash")
    else:
        print(f"  ❌ FAIL — Crashed (exit={code})")
    print()


def test_malformed_json():
    print("--- Test 5.3: Malformed JSON Input ---")
    stdout, stderr, code = run_server("this is not valid json at all")
    crashed = code != 0
    lines = [l for l in stdout.split("\n") if l.strip()]
    if not crashed:
        print("  ✅ PASS — Server did NOT crash on malformed JSON")
        for l in lines:
            try:
                d = json.loads(l)
                if "error" in d:
                    print(f"  → JSON-RPC error returned: code={d['error']['code']}, msg={d['error']['message'][:80]}")
            except:
                pass
    else:
        print(f"  ❌ FAIL — Server crashed on malformed JSON (exit={code})")
    print()


def test_missing_arguments():
    print("--- Test 5.4: Missing Required Arguments ---")
    stdout, stderr, code = run_server([
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "verify", "arguments": {}
        }}
    ])
    crashed = code != 0
    lines = [l for l in stdout.split("\n") if l.strip()]
    if not crashed and len(lines) >= 1:
        print("  ✅ PASS — Server handled missing args without crash")
        for l in lines:
            try:
                d = json.loads(l)
                if "result" in d:
                    print(f"  → Returned a result (graceful handling)")
                elif "error" in d:
                    print(f"  → JSON-RPC error: {d['error']['message'][:80]}")
            except:
                pass
    else:
        print(f"  ❌ FAIL — Crashed (exit={code})")
    print()


def test_invalid_api_base():
    print("--- Test 5.5: Invalid API Base URL ---")
    stdout, stderr, code = run_server(
        [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
                "name": "reason", "arguments": {"problem": "test invalid url"}
            }}
        ],
        env_overrides={"OPENAI_API_BASE": "https://nonexistent.invalid/v1"}
    )
    crashed = code != 0
    lines = [l for l in stdout.split("\n") if l.strip()]
    if not crashed and len(lines) >= 1:
        print("  ✅ PASS — Server did NOT crash with invalid API base")
        for l in lines:
            try:
                d = json.loads(l)
                if "result" in d and "content" in d.get("result", {}):
                    text = d["result"]["content"][0]["text"]
                    print(f"  → Error captured: {text[:120]}")
            except:
                pass
    else:
        print(f"  ❌ FAIL — Crashed (exit={code})")
    print()


if __name__ == "__main__":
    print()
    print("=== LAYER 5: CHAOS / RESILIENCE ===")
    print()
    test_invalid_api_key()
    test_empty_problem()
    test_malformed_json()
    test_missing_arguments()
    test_invalid_api_base()
    print("=== LAYER 5 COMPLETE ===")
