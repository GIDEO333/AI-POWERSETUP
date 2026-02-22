#!/usr/bin/env python3
"""FORGE Stack — Production-Level QA Test Suite.

Author mindset: Skeptical Senior Engineer. Trust nothing, verify everything.
Every assertion has a reason. Every edge case is probed.

Run:
  cd ~/Projects/AI-POWERSETUP && source .env && python3 test_setup.py

Categories:
  [ENV]   Environment & Config — are all moving parts wired correctly?
  [UNIT]  Unit Tests — does each function work in isolation?
  [EDGE]  Edge Cases — what happens with garbage input?
  [FAIL]  Failure Modes — does it degrade gracefully?
  [SEC]   Security — no credential leaks, no path traversal?
  [MCP]   Protocol Compliance — does JSON-RPC work correctly?
  [LIVE]  Live API — does the actual z.ai API respond? (costs 0-1 quota)
  [IDEM]  Idempotency — can we run setup twice safely?
"""

import os
import sys
import json
import time
import ast
import subprocess
import tempfile

# ── Formatting ───────────────────────────────────────────────
G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; C = "\033[96m"
B = "\033[1m"; D = "\033[2m"; NC = "\033[0m"

REPO = os.path.dirname(os.path.abspath(__file__))
VENV_PY = os.path.join(REPO, "glm-bridge/venv/bin/python3")
GLM_PY = os.path.join(REPO, "glm-bridge/glm_bridge_server.py")

results = {"pass": 0, "fail": 0, "skip": 0, "tests": []}
current_category = ""


def category(name):
    global current_category
    current_category = name
    print(f"\n{B}{C}── {name} ──{NC}")


def test(name, func, skip_if=None):
    """Run test. Never crash the suite — catch everything."""
    if skip_if:
        results["skip"] += 1
        results["tests"].append(("SKIP", current_category, name, skip_if, 0))
        print(f"  {Y}SKIP{NC}  {name} — {skip_if}")
        return
    try:
        t0 = time.time()
        passed, detail = func()
        elapsed = time.time() - t0
        if passed:
            results["pass"] += 1
            results["tests"].append(("PASS", current_category, name, detail, elapsed))
            print(f"  {G}PASS{NC}  {name} ({elapsed:.1f}s)")
        else:
            results["fail"] += 1
            results["tests"].append(("FAIL", current_category, name, detail, elapsed))
            print(f"  {R}FAIL{NC}  {name} — {detail}")
    except Exception as e:
        results["fail"] += 1
        results["tests"].append(("FAIL", current_category, name, str(e), 0))
        print(f"  {R}FAIL{NC}  {name} — EXCEPTION: {e}")


# ═══════════════════════════════════════════════════════════════
# [ENV] Environment & Configuration
# ═══════════════════════════════════════════════════════════════

def test_zai_key_format():
    key = os.environ.get("ZAI_API_KEY", "")
    if not key:
        return False, "ZAI_API_KEY not set"
    # z.ai keys are typically 32+ chars with a dot separator
    if len(key) < 20:
        return False, f"Key suspiciously short ({len(key)} chars)"
    return True, f"{key[:8]}...{key[-4:]} ({len(key)} chars)"


def test_flash_key_format():
    key = os.environ.get("ZAI_FLASH_API_KEY", "")
    if not key:
        return False, "ZAI_FLASH_API_KEY not set"
    if len(key) < 20:
        return False, f"Key suspiciously short ({len(key)} chars)"
    # Ensure flash key != premium key (common misconfiguration)
    if key == os.environ.get("ZAI_API_KEY", ""):
        return False, "Flash key is SAME as premium key — likely wrong"
    return True, f"{key[:8]}...{key[-4:]} ({len(key)} chars)"


def test_env_file_not_in_git():
    """Security: .env must be in .gitignore."""
    gitignore = os.path.join(REPO, ".gitignore")
    if not os.path.exists(gitignore):
        return False, ".gitignore missing"
    with open(gitignore) as f:
        content = f.read()
    if ".env" not in content:
        return False, ".env not in .gitignore — CREDENTIAL LEAK RISK"
    return True, ".env is gitignored"


def test_env_example_exists():
    path = os.path.join(REPO, ".env.example")
    if not os.path.exists(path):
        return False, "No .env.example for new users"
    with open(path) as f:
        content = f.read()
    # .env.example must NOT contain real keys
    if "izBz1nm9" in content or "SIhN979" in content:
        return False, ".env.example contains REAL API keys!"
    return True, "Exists, no real keys"


def test_symlinks():
    links = {
        "~/.agent/scripts": os.path.join(REPO, "agent/scripts"),
        "~/.agent/skills": os.path.join(REPO, "agent/skills"),
        "~/.switchboard": os.path.join(REPO, "switchboard"),
    }
    broken = []
    for link, expected_target in links.items():
        expanded = os.path.expanduser(link)
        if not os.path.islink(expanded):
            broken.append(f"{link} NOT a symlink")
        elif not os.path.exists(expanded):
            broken.append(f"{link} DANGLING (target deleted?)")
    if broken:
        return False, "; ".join(broken)
    return True, f"3/3 symlinks valid"


def test_no_stale_symlinks():
    """After cleanup, ~/.openclaw should NOT exist."""
    stale = []
    for path in ["~/.openclaw"]:
        if os.path.exists(os.path.expanduser(path)) or os.path.islink(os.path.expanduser(path)):
            stale.append(path)
    if stale:
        return False, f"Stale symlink(s) still exist: {', '.join(stale)}"
    return True, "No stale symlinks"


# ═══════════════════════════════════════════════════════════════
# [UNIT] Unit Tests — GLM Bridge Functions
# ═══════════════════════════════════════════════════════════════

def _run_in_venv(code, timeout=30):
    """Execute Python code inside GLM Bridge venv."""
    env = {**os.environ, "PATH": os.environ.get("PATH", "")}
    r = subprocess.run(
        [VENV_PY, "-c", code],
        capture_output=True, text=True, timeout=timeout,
        cwd=REPO, env=env
    )
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def test_validate_args_valid():
    code = """
import sys; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import validate_args
assert validate_args('reason', {'problem': 'test'}) is None
assert validate_args('verify', {'code': 'x=1'}) is None
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_validate_args_missing():
    code = """
import sys; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import validate_args
result = validate_args('reason', {})
assert result is not None, 'Should reject empty args'
assert 'problem' in result.lower(), f'Should mention missing field, got: {result}'
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_validate_args_unknown_tool():
    code = """
import sys; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import validate_args
result = validate_args('nonexistent_tool', {'x': 1})
assert result is not None, 'Should reject unknown tool'
assert 'unknown' in result.lower() or 'nonexistent' in result.lower()
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_validate_args_whitespace_only():
    """Edge: args with only whitespace should be rejected."""
    code = """
import sys; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import validate_args
result = validate_args('reason', {'problem': '   '})
assert result is not None, 'Whitespace-only should be rejected'
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


# ═══════════════════════════════════════════════════════════════
# [EDGE] Edge Cases
# ═══════════════════════════════════════════════════════════════

def test_empty_string_handling():
    code = """
import sys; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import validate_args
# Empty string
assert validate_args('reason', {'problem': ''}) is not None
# None-like
assert validate_args('verify', {'code': ''}) is not None
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_unicode_input():
    code = """
import sys; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import validate_args
# Unicode, emoji, special chars — should NOT crash
assert validate_args('reason', {'problem': '🔥 日本語テスト émojis'}) is None
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_huge_input_doesnt_crash():
    """Sending 100K chars shouldn't crash validate_args."""
    code = """
import sys; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import validate_args
big = 'x' * 100000
assert validate_args('reason', {'problem': big}) is None
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


# ═══════════════════════════════════════════════════════════════
# [MCP] JSON-RPC Protocol Compliance
# ═══════════════════════════════════════════════════════════════

def test_mcp_initialize():
    code = """
import sys, json; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import GLMBridgeServer
s = GLMBridgeServer()
resp = s.handle({"jsonrpc":"2.0","id":1,"method":"initialize","params":{}})
assert resp['id'] == 1
assert 'protocolVersion' in resp['result']
assert resp['result']['serverInfo']['name'] == 'glm-bridge'
assert '3.2' in resp['result']['serverInfo']['version']
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_mcp_tools_list():
    code = """
import sys, json; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import GLMBridgeServer
s = GLMBridgeServer()
resp = s.handle({"jsonrpc":"2.0","id":2,"method":"tools/list"})
tools = resp['result']['tools']
names = [t['name'] for t in tools]
assert 'reason' in names, f'Missing reason, got: {names}'
assert 'verify' in names, f'Missing verify, got: {names}'
# These should NOT exist anymore (removed in v3.1+)
assert 'deep_reason' not in names, 'deep_reason should be removed!'
assert 'peek_first_gate' not in names, 'peek_first_gate should be removed!'
assert len(tools) == 2, f'Expected 2 tools, got {len(tools)}'
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_mcp_unknown_method():
    code = """
import sys, json; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import GLMBridgeServer
s = GLMBridgeServer()
resp = s.handle({"jsonrpc":"2.0","id":3,"method":"admin/shutdown"})
assert 'error' in resp, 'Should return error for unknown method'
assert resp['error']['code'] == -32601
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_mcp_unknown_tool():
    code = """
import sys, json; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import GLMBridgeServer
s = GLMBridgeServer()
resp = s.handle({"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"hack","arguments":{}}})
# Should return validation error, not crash
assert 'result' in resp or 'error' in resp
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_mcp_validation_error_format():
    """Validation errors should use result.content, not error field."""
    code = """
import sys, json; sys.path.insert(0,'glm-bridge')
from glm_bridge_server import GLMBridgeServer
s = GLMBridgeServer()
resp = s.handle({"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"reason","arguments":{}}})
# Empty problem should return validation message, not crash
assert 'result' in resp, f'Expected result, got: {json.dumps(resp)[:200]}'
text = resp['result']['content'][0]['text']
assert 'Validation' in text or 'wajib' in text.lower()
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


# ═══════════════════════════════════════════════════════════════
# [FAIL] Failure Modes — Graceful Degradation
# ═══════════════════════════════════════════════════════════════

def test_wrong_api_key_doesnt_crash():
    """Bad API key should return error message, not exception."""
    code = """
import sys, os; sys.path.insert(0,'glm-bridge')
os.environ['OPENAI_API_KEY'] = 'invalid_key_12345'
os.environ['OPENAI_API_BASE'] = 'https://api.z.ai/api/coding/paas/v4'
os.environ['GLM_BRIDGE_MODEL'] = 'openai/glm-4.7'
os.environ['GLM_BRIDGE_TIMEOUT'] = '10'
os.environ['GLM_FLASH_API_KEY'] = ''
os.environ['GLM_BRIDGE_SELF_REFINE'] = 'false'
from glm_bridge_server import reason
result = reason('test')
# Should return error string, not crash
assert isinstance(result, str), f'Expected string, got {type(result)}'
assert 'error' in result.lower() or 'Error' in result, f'Expected error in: {result[:100]}'
print('OK')
"""
    rc, out, err = _run_in_venv(code, timeout=20)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_flash_unavailable_fallback():
    """When Flash key is empty, Self-Refine should be skipped gracefully."""
    code = """
import sys, os; sys.path.insert(0,'glm-bridge')
os.environ['GLM_FLASH_API_KEY'] = ''
os.environ['GLM_BRIDGE_SELF_REFINE'] = 'true'
from glm_bridge_server import flash_critique
result = flash_critique('test problem', 'test draft')
assert result is None, f'Should return None when Flash unavailable, got: {result}'
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


def test_timeout_config():
    code = """
import sys, os; sys.path.insert(0,'glm-bridge')
os.environ['GLM_BRIDGE_TIMEOUT'] = '90'
from glm_bridge_server import TIMEOUT
assert TIMEOUT == 90, f'Expected 90, got {TIMEOUT}'
print('OK')
"""
    rc, out, err = _run_in_venv(code)
    return rc == 0 and "OK" in out, f"rc={rc}, out={out}, err={err[:100]}"


# ═══════════════════════════════════════════════════════════════
# [SEC] Security
# ═══════════════════════════════════════════════════════════════

def test_no_hardcoded_keys():
    """Source code must NOT contain API keys."""
    with open(GLM_PY) as f:
        source = f.read()
    # Check for common key patterns
    suspicious = []
    for pattern in ["izBz1nm9", "SIhN979", "sk-", "Bearer "]:
        if pattern in source:
            suspicious.append(pattern)
    if suspicious:
        return False, f"Hardcoded credential patterns found: {suspicious}"
    return True, "No hardcoded credentials"


def test_git_not_tracking_env():
    """git ls-files should NOT list .env."""
    r = subprocess.run(
        ["git", "ls-files", ".env"],
        capture_output=True, text=True, cwd=REPO
    )
    if r.stdout.strip() == ".env":
        return False, ".env is TRACKED by git — credential leak!"
    return True, ".env not tracked"


def test_no_dead_code_references():
    """Verify no references to removed functions remain."""
    with open(GLM_PY) as f:
        source = f.read()
    dead_refs = []
    for name in ["deep_reason", "peek_first_gate", "SIMPLE_PROMPT", "COMPLEX_PROMPT",
                  "run_python", "forge_repl"]:
        if name in source:
            dead_refs.append(name)
    if dead_refs:
        return False, f"Dead references found: {dead_refs}"
    return True, "No dead code references"


# ═══════════════════════════════════════════════════════════════
# [LIVE] Live API Tests (⚠️ costs 0-1 GLM quota)
# ═══════════════════════════════════════════════════════════════

def test_flash_api_connectivity():
    """Live call to Flash (free, 0 quota)."""
    code = """
import sys, os; sys.path.insert(0,'glm-bridge')
os.environ.setdefault('OPENAI_API_KEY', os.environ.get('ZAI_API_KEY',''))
os.environ.setdefault('OPENAI_API_BASE', 'https://api.z.ai/api/coding/paas/v4')
os.environ.setdefault('GLM_BRIDGE_MODEL', 'openai/glm-4.7')
os.environ.setdefault('GLM_BRIDGE_TIMEOUT', '30')
os.environ.setdefault('GLM_FLASH_API_KEY', os.environ.get('ZAI_FLASH_API_KEY',''))
os.environ.setdefault('GLM_FLASH_API_BASE', 'https://api.z.ai/api/paas/v4')
os.environ.setdefault('GLM_FLASH_MODEL', 'glm-4.7-flash')
from glm_bridge_server import llm_call
result = llm_call([{"role":"user","content":"Reply with only: PONG"}], max_tokens=10, use_flash=True)
if not result:
    print('FAIL:empty')
elif 'Error' in result:
    print(f'FAIL:{result[:80]}')
else:
    print(f'OK:{result[:30]}')
"""
    rc, out, err = _run_in_venv(code, timeout=30)
    if "OK:" in out:
        return True, f"Flash responded: {out.split('OK:')[1][:30]}"
    return False, f"{out} | {err[:80]}"


def test_self_refine_critique():
    """Test that flash_critique returns something (not None) with valid Flash key."""
    flash_key = os.environ.get("ZAI_FLASH_API_KEY", "")
    if not flash_key:
        return False, "No Flash key to test"
    code = """
import sys, os; sys.path.insert(0,'glm-bridge')
os.environ.setdefault('GLM_FLASH_API_KEY', os.environ.get('ZAI_FLASH_API_KEY',''))
os.environ.setdefault('GLM_FLASH_API_BASE', 'https://api.z.ai/api/paas/v4')
os.environ.setdefault('GLM_FLASH_MODEL', 'glm-4.7-flash')
os.environ.setdefault('OPENAI_API_KEY', os.environ.get('ZAI_API_KEY',''))
os.environ.setdefault('OPENAI_API_BASE', 'https://api.z.ai/api/coding/paas/v4')
os.environ.setdefault('GLM_BRIDGE_MODEL', 'openai/glm-4.7')
os.environ.setdefault('GLM_BRIDGE_TIMEOUT', '30')
from glm_bridge_server import flash_critique
result = flash_critique('Fix a null pointer bug', 'Check if variable is None before using it.')
if result is None:
    print('FAIL:returned None')
elif 'Error' in result:
    print(f'FAIL:{result[:80]}')
elif len(result) > 0:
    has_lgtm = 'LGTM' in result.upper()
    print(f'OK:len={len(result)},lgtm={has_lgtm},preview={result[:40]}')
else:
    print('FAIL:empty')
"""
    rc, out, err = _run_in_venv(code, timeout=30)
    if "OK:" in out:
        return True, out.split("OK:")[1][:60]
    return False, f"{out} | {err[:80]}"


# ═══════════════════════════════════════════════════════════════
# [IDEM] Idempotency — Can bootstrap run twice?
# ═══════════════════════════════════════════════════════════════

def test_skills_index_consistent():
    """Index should have exactly 11 entries, no duplicates."""
    path = os.path.join(REPO, "agent/skills/skills-index.json")
    with open(path) as f:
        idx = json.load(f)
    names = [item.get("name", "") for item in idx]
    dupes = [n for n in names if names.count(n) > 1]
    if dupes:
        return False, f"Duplicate skills: {set(dupes)}"
    if len(idx) != 11:
        return False, f"Expected 11, got {len(idx)}"
    return True, f"11 unique skills"


def test_mcp_config_valid_json():
    path = os.path.expanduser("~/.gemini/antigravity/mcp_config.json")
    if not os.path.exists(path):
        return False, "File missing"
    with open(path) as f:
        cfg = json.load(f)
    servers = cfg.get("mcpServers", {})
    # Must have skills-search and switchboard at minimum
    expected = {"skills-search", "switchboard"}
    actual = set(servers.keys())
    missing = expected - actual
    if missing:
        return False, f"Missing servers: {missing}"
    return True, f"Servers: {', '.join(sorted(actual))}"


# ═══════════════════════════════════════════════════════════════
# [STATIC] Code Quality — What a reviewer would check
# ═══════════════════════════════════════════════════════════════

def test_glm_bridge_syntax():
    with open(GLM_PY) as f:
        source = f.read()
    ast.parse(source)
    lines = source.count("\n") + 1
    if lines > 400:
        return False, f"{lines} lines — too bloated for 2 tools"
    return True, f"{lines} lines"


def test_no_debug_prints():
    """Production code shouldn't have print() statements (use stderr)."""
    with open(GLM_PY) as f:
        source = f.read()
    lines = source.split("\n")
    debug_prints = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("print(") and not stripped.startswith("#"):
            # Allow if inside __main__ or test blocks
            debug_prints.append(f"L{i}: {stripped[:50]}")
    if debug_prints:
        return False, f"Debug prints: {debug_prints[:3]}"
    return True, "No debug prints"


def test_all_functions_have_docstrings():
    with open(GLM_PY) as f:
        source = f.read()
    tree = ast.parse(source)
    missing = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)):
                missing.append(node.name)
    if missing:
        return False, f"Missing docstrings: {missing}"
    return True, "All functions documented"


def test_version_consistency():
    """Version in serverInfo should match docstring."""
    with open(GLM_PY) as f:
        source = f.read()
    # Check docstring version
    if "v3.2" not in source[:300]:
        return False, "Docstring doesn't mention v3.2"
    if '"3.2' not in source:
        return False, "serverInfo version doesn't match"
    return True, "v3.2 consistent"


# ═══════════════════════════════════════════════════════════════
# Runner
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n{B}{'='*60}")
    print(f"  🔬 FORGE Stack — Production QA Suite")
    print(f"  Skeptical Senior Engineer Mode: ON")
    print(f"{'='*60}{NC}")

    has_flash = bool(os.environ.get("ZAI_FLASH_API_KEY", ""))

    # ── ENV ──
    category("[ENV] Environment & Configuration")
    test("ZAI_API_KEY format", test_zai_key_format)
    test("ZAI_FLASH_API_KEY format", test_flash_key_format)
    test(".env not in git", test_env_file_not_in_git)
    test(".env.example safe", test_env_example_exists)
    test("Symlinks valid (3/3)", test_symlinks)
    test("No stale symlinks", test_no_stale_symlinks)

    # ── UNIT ──
    category("[UNIT] Unit Tests — validate_args")
    test("Valid args accepted", test_validate_args_valid)
    test("Missing args rejected", test_validate_args_missing)
    test("Unknown tool rejected", test_validate_args_unknown_tool)
    test("Whitespace-only rejected", test_validate_args_whitespace_only)

    # ── EDGE ──
    category("[EDGE] Edge Cases")
    test("Empty string rejected", test_empty_string_handling)
    test("Unicode input accepted", test_unicode_input)
    test("100K char input survives", test_huge_input_doesnt_crash)

    # ── MCP ──
    category("[MCP] JSON-RPC Protocol")
    test("initialize response", test_mcp_initialize)
    test("tools/list (2 tools only)", test_mcp_tools_list)
    test("Unknown method → error", test_mcp_unknown_method)
    test("Unknown tool → handled", test_mcp_unknown_tool)
    test("Validation error format", test_mcp_validation_error_format)

    # ── FAIL ──
    category("[FAIL] Failure Modes")
    test("Wrong API key → error msg", test_wrong_api_key_doesnt_crash)
    test("Flash unavailable → skip refine", test_flash_unavailable_fallback)
    test("Timeout config respected", test_timeout_config)

    # ── SEC ──
    category("[SEC] Security")
    test("No hardcoded API keys", test_no_hardcoded_keys)
    test(".env not tracked by git", test_git_not_tracking_env)
    test("No dead code references", test_no_dead_code_references)

    # ── STATIC ──
    category("[STATIC] Code Quality")
    test("GLM Bridge syntax valid", test_glm_bridge_syntax)
    test("No debug prints", test_no_debug_prints)
    test("All functions documented", test_all_functions_have_docstrings)
    test("Version consistency", test_version_consistency)

    # ── IDEM ──
    category("[IDEM] Idempotency & Config")
    test("Skills index (11, no dupes)", test_skills_index_consistent)
    test("MCP config valid JSON", test_mcp_config_valid_json)

    # ── LIVE ──
    category("[LIVE] Live API (⚠️ ~20s, free Flash call)")
    test("Flash API connectivity", test_flash_api_connectivity,
         skip_if="No Flash key" if not has_flash else None)
    test("Self-Refine critique works", test_self_refine_critique,
         skip_if="No Flash key" if not has_flash else None)

    # ── Summary ──
    total = results["pass"] + results["fail"] + results["skip"]
    print(f"\n{B}{'='*60}")
    color = G if results["fail"] == 0 else R
    print(f"  {color}{results['pass']} passed, {results['fail']} failed, {results['skip']} skipped ({total} total){NC}")
    if results["fail"] == 0:
        print(f"  {G}🏭 PRODUCTION READY{NC}")
    else:
        print(f"  {R}⚠️ FIX FAILURES BEFORE DEPLOY{NC}")
        print(f"\n  Failures:")
        for status, cat, name, detail, _ in results["tests"]:
            if status == "FAIL":
                print(f"    {R}✗{NC} [{cat}] {name}: {detail}")
    print(f"{'='*60}{NC}\n")
