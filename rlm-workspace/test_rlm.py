#!/usr/bin/env python3
"""Test suite for RLM MCP Server — verifies JSON-RPC protocol and tool calls."""
import json
import subprocess
import sys
import os

VENV_PYTHON = os.path.expanduser("~/Projects/rlm-workspace/venv/bin/python3")
SERVER_SCRIPT = os.path.expanduser("~/Projects/rlm-workspace/rlm_mcp_server.py")

ENV = {
    **os.environ,
    "OPENAI_API_KEY": os.environ.get("ZAI_API_KEY", ""),
    "OPENAI_API_BASE": "https://api.z.ai/api/coding/paas/v4",
    "RLM_MODEL": "openai/glm-4.7",
}


def send_requests(requests):
    """Send multiple JSON-RPC requests to the server and return parsed responses."""
    input_data = "\n".join(json.dumps(r) for r in requests) + "\n"
    proc = subprocess.run(
        [VENV_PYTHON, SERVER_SCRIPT],
        input=input_data,
        capture_output=True,
        text=True,
        env=ENV,
        timeout=120,
    )
    responses = []
    for line in proc.stdout.strip().split("\n"):
        if line.strip():
            responses.append(json.loads(line))
    return responses


def test_initialize():
    print("=" * 60)
    print("TEST 1: initialize")
    print("=" * 60)
    resps = send_requests([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    ])
    assert len(resps) == 1
    r = resps[0]
    assert r["id"] == 1
    assert r["result"]["serverInfo"]["name"] == "rlm-mcp-server"
    assert r["result"]["protocolVersion"] == "2024-11-05"
    print("✅ PASS — Server initialized correctly")
    print(f"   Server: {r['result']['serverInfo']['name']} v{r['result']['serverInfo']['version']}")
    print()


def test_tools_list():
    print("=" * 60)
    print("TEST 2: tools/list")
    print("=" * 60)
    resps = send_requests([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    ])
    tools_resp = resps[1]
    tools = tools_resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "reason" in tool_names, "Missing 'reason' tool"
    assert "verify" in tool_names, "Missing 'verify' tool"
    print("✅ PASS — Both tools registered")
    for t in tools:
        print(f"   📦 {t['name']}: {t['description'][:60]}...")
    print()


def test_verify_tool():
    print("=" * 60)
    print("TEST 3: tools/call — verify")
    print("=" * 60)
    code = """def add(a, b):
    return a + b

result = add("hello", 5)
"""
    resps = send_requests([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "verify",
                "arguments": {
                    "code": code,
                    "context": "Simple addition function — should handle type mismatch"
                }
            }
        }
    ])
    verify_resp = resps[1]
    assert "result" in verify_resp, f"Expected result, got error: {verify_resp}"
    content = verify_resp["result"]["content"][0]["text"]
    print("✅ PASS — Verify tool returned analysis")
    print(f"   Response preview ({len(content)} chars):")
    # Print first 500 chars
    for line in content[:500].split("\n"):
        print(f"   {line}")
    if len(content) > 500:
        print("   ...")
    print()


def test_unknown_tool():
    print("=" * 60)
    print("TEST 4: tools/call — unknown tool (error handling)")
    print("=" * 60)
    resps = send_requests([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "nonexistent", "arguments": {}}
        }
    ])
    err_resp = resps[1]
    assert "error" in err_resp, f"Expected error, got: {err_resp}"
    assert err_resp["error"]["code"] == -32601
    print("✅ PASS — Unknown tool returns proper error")
    print(f"   Error: {err_resp['error']['message']}")
    print()


def test_unknown_method():
    print("=" * 60)
    print("TEST 5: unknown method (error handling)")
    print("=" * 60)
    resps = send_requests([
        {"jsonrpc": "2.0", "id": 5, "method": "foo/bar", "params": {}}
    ])
    err_resp = resps[0]
    assert "error" in err_resp
    assert err_resp["error"]["code"] == -32601
    print("✅ PASS — Unknown method returns proper error")
    print(f"   Error: {err_resp['error']['message']}")
    print()


if __name__ == "__main__":
    print()
    print("🔬 RLM MCP Server — Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Protocol", test_initialize),
        ("Protocol", test_tools_list),
        ("LLM Integration", test_verify_tool),
        ("Error Handling", test_unknown_tool),
        ("Error Handling", test_unknown_method),
    ]

    passed = 0
    failed = 0
    for category, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ FAIL — {test_fn.__name__}: {e}")
            print()

    print("=" * 60)
    print(f"📊 Results: {passed}/{passed + failed} tests passed")
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    print()
