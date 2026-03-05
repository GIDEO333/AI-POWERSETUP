#!/bin/bash
# ==============================================================================
# 🏥 AI PowerSetup Health Check v3.0 — Bulletproof Edition
# ==============================================================================
# Registry-driven. Reads components.json and checks each component.
# To add a new tool: just add an entry to components.json!
#
# v3.0 Fixes:
#   - [F1] Graceful crash on corrupted components.json
#   - [F2] Missing key in component = WARN, not crash
#   - [F3] 0 symlinks in folder = WARN (misleading PASS fixed)
#   - [F4] Python exit code properly propagated to bash
#   - [F5] python3 dependency check before running

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
REGISTRY="$SCRIPT_DIR/../components.json"

echo ""
echo "🏥 AI PowerSetup Health Check v3.0"
echo "========================================"

# [F5] Check python3 dependency
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found. Cannot run health check."
    exit 1
fi

# Check registry exists
if [ ! -f "$REGISTRY" ]; then
    echo "❌ components.json not found at $REGISTRY"
    exit 1
fi

# [F1] Validate JSON before parsing
python3 -c "import json; json.load(open('$REGISTRY'))" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ components.json is corrupted (invalid JSON)"
    exit 1
fi

TOTAL=$(python3 -c "import json; print(len(json.load(open('$REGISTRY'))))")
echo "📋 Checking $TOTAL registered components..."
echo ""

# [F4] Capture Python exit code properly
REGISTRY="$REGISTRY" python3 << 'PYEOF'
import json, os, subprocess, sys

reg = os.environ.get("REGISTRY", "")
with open(reg) as f:
    components = json.load(f)

pass_count = 0
warn_count = 0
fail_count = 0
total = len(components)

for i, comp in enumerate(components, 1):
    name = comp.get("name", f"Unknown Component #{i}")
    check = comp.get("check", "")
    path = os.path.expanduser(comp.get("path", ""))
    idx = f"[{i}/{total}]"

    # [F2] Missing 'check' key = warning, not crash
    if not check:
        print(f"⚠️ {idx} {name}: No 'check' type defined in registry")
        warn_count += 1
        continue

    try:
        if check == "file_exists":
            if os.path.exists(path):
                if path.endswith(".md"):
                    lines = sum(1 for _ in open(path))
                    print(f"✅ {idx} {name}: Found ({lines} lines)")
                else:
                    print(f"✅ {idx} {name}: Found")
                pass_count += 1
            else:
                print(f"❌ {idx} {name}: NOT FOUND at {path}")
                fail_count += 1

        elif check == "dir_exists":
            if os.path.isdir(path):
                print(f"✅ {idx} {name}: Present")
                pass_count += 1
            else:
                print(f"⚠️ {idx} {name}: Directory not found")
                warn_count += 1

        elif check == "command_exists":
            cmd = comp.get("command", "")
            if not cmd:
                print(f"⚠️ {idx} {name}: No 'command' specified in registry")
                warn_count += 1
                continue
            result = subprocess.run(["which", cmd], capture_output=True, text=True)
            if result.returncode == 0:
                ver = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
                version = ver.stdout.strip().split("\n")[0] if ver.returncode == 0 else "installed"
                print(f"✅ {idx} {name}: {version}")
                pass_count += 1
            else:
                print(f"❌ {idx} {name}: '{cmd}' not found in PATH")
                fail_count += 1

        elif check == "git_clean":
            if os.path.isdir(os.path.join(path, ".git")):
                result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=path, timeout=10)
                dirty = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
                if dirty == 0:
                    print(f"✅ {idx} {name}: Git clean")
                    pass_count += 1
                else:
                    print(f"⚠️ {idx} {name}: {dirty} uncommitted file(s)")
                    warn_count += 1
            else:
                print(f"❌ {idx} {name}: Not a git repo at {path}")
                fail_count += 1

        elif check == "symlinks_intact":
            if os.path.isdir(path):
                broken = 0
                total_links = 0
                for f in os.listdir(path):
                    fp = os.path.join(path, f)
                    if os.path.islink(fp):
                        total_links += 1
                        if not os.path.exists(fp):
                            broken += 1
                # [F3] 0 symlinks = warning, not misleading pass
                if total_links == 0:
                    print(f"⚠️ {idx} {name}: No symlinks found in directory")
                    warn_count += 1
                elif broken == 0:
                    print(f"✅ {idx} {name}: {total_links} symlinks intact")
                    pass_count += 1
                else:
                    print(f"❌ {idx} {name}: {broken}/{total_links} broken symlink(s)")
                    fail_count += 1
            else:
                print(f"⚠️ {idx} {name}: Directory not found")
                warn_count += 1

        elif check == "bash_syntax":
            if os.path.exists(path):
                result = subprocess.run(["bash", "-n", path], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ {idx} {name}: Syntax OK")
                    pass_count += 1
                else:
                    print(f"❌ {idx} {name}: Syntax ERROR")
                    fail_count += 1
            else:
                print(f"❌ {idx} {name}: Script not found at {path}")
                fail_count += 1

        elif check == "xml_tag":
            if os.path.exists(path):
                content = open(path).read()
                if "<system_configuration>" in content:
                    print(f"✅ {idx} {name}: XML tag valid")
                    pass_count += 1
                else:
                    print(f"❌ {idx} {name}: Missing <system_configuration> tag")
                    fail_count += 1
            else:
                print(f"❌ {idx} {name}: File not found at {path}")
                fail_count += 1

        elif check == "dir_min_files":
            if os.path.isdir(path):
                count = len([f for f in os.listdir(path) if f.endswith(".md")])
                min_f = comp.get("min_files", 1)
                if count >= min_f:
                    print(f"✅ {idx} {name}: {count} files found")
                    pass_count += 1
                else:
                    print(f"⚠️ {idx} {name}: Only {count} files (expected {min_f}+)")
                    warn_count += 1
            else:
                print(f"❌ {idx} {name}: Directory not found")
                fail_count += 1

        elif check == "json_count":
            if os.path.exists(path):
                try:
                    data = json.load(open(path))
                    print(f"✅ {idx} {name}: {len(data)} items indexed")
                    pass_count += 1
                except:
                    print(f"❌ {idx} {name}: Invalid JSON")
                    fail_count += 1
            else:
                print(f"⚠️ {idx} {name}: Index not found (rebuild needed)")
                warn_count += 1

        else:
            print(f"⚠️ {idx} {name}: Unknown check type '{check}'")
            warn_count += 1

    except Exception as e:
        print(f"❌ {idx} {name}: Unexpected error: {e}")
        fail_count += 1

print("")
print("========================================")
print(f"RESULT: {pass_count} HEALTHY | {warn_count} WARNING | {fail_count} BROKEN")
print("========================================")

if fail_count > 0:
    print("")
    print("💡 Quick fixes:")
    print("   Symlinks:  cd ~/Projects/triple-agent-orchestrator && ./install.sh")
    print("   Skills:    cd ~/Projects/AI-POWERSETUP && python3 agent/scripts/build-skills-index.py")
    sys.exit(1)
sys.exit(0)
PYEOF

# [F4] Propagate Python exit code to bash
exit $?
