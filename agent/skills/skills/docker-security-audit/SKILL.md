---
name: docker-security-audit
description: >
  Systematic security audit for any Docker-containerized project.
  Checks 6 attack surfaces: egress, sandbox, secrets, mounts, network,
  and data-at-rest. Produces a scored gap list with fix options and
  trade-offs. Use before deploying any Docker-based project.
  Trigger: "docker security audit", "audit keamanan container",
  "docker security gaps", "cek keamanan docker project".
category: Ops
---

# Docker Security Audit

## The 6 Attack Surfaces

For each surface: identify gap → score severity → propose fix with trade-off.

---

### Surface 1 — Secrets Management

**Check:**
- Are secrets passed via env vars OR via stdin/file?
- Can subprocesses (bash, child_process) inherit secrets?
- Any hardcoded credentials in source?

```bash
# Quick secret scan
grep -rE "(api_key|secret|password|token)\s*=\s*['\"][^'\"]{8,}" src/ --include="*.ts" --include="*.js"
```

**Severity levels:**
- 🔴 Secrets in env vars visible to all child processes
- 🟡 Secrets in env vars but sanitized before subprocess calls
- 🟢 Secrets via stdin/file, deleted after read (NanoClaw pattern)

**Best practice:** Pass via stdin, delete temp file immediately. Add `PreToolUse` hook to unset before Bash.

---

### Surface 2 — Network Egress

**Check:**
- Any `--network` restriction on `docker run`?
- Can the container reach any external IP?
- Is there a proxy or egress filter?

**Severity levels:**
- 🔴 No restriction — full internet access
- 🟡 Logging proxy only (know what goes out, can't block)
- 🟢 Allowlist proxy + `--network internal` (only whitelisted domains)

**Options (with trade-offs):**

| Option | Blocks Exfiltration | Breaks Free Browsing | macOS Compatible |
|--------|--------------------|--------------------|-----------------|
| tinyproxy (logging) | ❌ No | ✅ No | ✅ Yes |
| tinyproxy (allowlist) | ✅ Yes | ❌ Yes | ✅ Yes |
| Squid + SSL bump | ✅ Yes | ❌ Yes | ✅ Yes |
| iptables DOCKER-USER | ✅ Yes | ⚠️ Partial | ❌ No (OrbStack/Docker Desktop) |

---

### Surface 3 — Container Sandbox (Chromium / Browser)

**Check (only if container runs a browser):**
- Is `--no-sandbox` flag used? (BAD)
- Is `--cap-add=SYS_ADMIN` used? (BAD — nicknamed "new root")
- Is a custom seccomp profile in use?

```bash
# Check docker run args for dangerous flags
grep -r "no-sandbox\|SYS_ADMIN\|privileged" src/ container/
```

**Fix:**
```typescript
// container-runtime.ts — add to buildContainerArgs():
args.push('--security-opt', 'seccomp=/path/to/chrome.json');
// Never add: --cap-add=SYS_ADMIN or --no-sandbox
```

Download `chrome.json`: https://github.com/nicholasgasior/gsfmt/blob/master/chrome.json

---

### Surface 4 — Volume Mounts

**Check:**
- Are docker socket (`/var/run/docker.sock`) ever mounted? (NEVER do this)
- Are host paths validated before mounting?
- Are symlinks resolved before mount validation?
- Is there an allowlist for additional mounts?

**Severity levels:**
- 🔴 Docker socket mounted → container has host root access
- 🔴 Unvalidated user-controlled paths → path traversal
- 🟡 Validated paths, symlinks not resolved
- 🟢 Allowlist + symlink resolution + restricted container paths

---

### Surface 5 — Container Privilege

**Check:**
```bash
# In Dockerfile:
grep -E "USER|privileged|cap-add" container/Dockerfile
```

**Checklist:**
- [ ] Container runs as non-root (`USER node` or similar)
- [ ] `--privileged` NOT used
- [ ] `--cap-add=ALL` NOT used
- [ ] Resource limits set (`--memory`, `--cpus`)

---

### Surface 6 — Data at Rest

**Check:**
- Is the database encrypted? (SQLite = plaintext by default)
- Are session/auth files encrypted?
- Are archives/backups encrypted?
- What are file permissions on sensitive data dirs?

**Options:**
```bash
# Minimum: restrict permissions
chmod 600 store/messages.db
chmod -R 700 data/auth/

# Better: encrypted overlay (transparent to app)
# gocryptfs on macOS (needs MacFUSE)
brew install macfuse gocryptfs
gocryptfs -init ~/project-cipher/
gocryptfs ~/project-cipher/ ~/project-plain/
```

---

## Audit Output Template

```
## Docker Security Audit — [Project Name]
Date: YYYY-MM-DD

| Surface | Status | Severity | Fix Applied |
|---------|--------|----------|-------------|
| Secrets | ✅ stdin+unset hook | ✅ Low | Yes |
| Network egress | ⚠️ logging proxy only | 🟡 Medium | Partial |
| Browser sandbox | ⚠️ no seccomp profile | 🟡 Medium | No |
| Volume mounts | ✅ allowlist + symlink resolve | ✅ Low | Yes |
| Container privilege | ✅ USER node, no --privileged | ✅ Low | Yes |
| Data at rest | ❌ SQLite plaintext | 🔴 High | No |

Overall Security Score: X/10
Priority fix: [highest severity unfixed item]
```
