---
name: safe-push
description: >
  Pre-push safety gate for any project. Run before every `git push` to a
  new or existing repo. Covers three layers: (1) secrets scan — nothing
  sensitive leaking, (2) recoverability audit — a fresh clone on a new
  machine can reach 100% working state with minimum effort, (3) git
  workflow — clean branch, conventional commit, push.
  Trigger: "safe push", "push ke github", "siap push", "push project baru".
category: Ops
---

# Safe Push Skill

## When to invoke
- Before `git push` on **any** project (new or existing)
- When the user says: "push ke github", "safe push", "siap push project"
- After significant changes that may affect setup/recovery

---

## Layer 1 — Security Scan

Run these checks **before staging anything**:

### 1a. Secrets leak scan
```bash
# Check for accidental secrets in staged/untracked files
git diff --cached | grep -iE "(api_key|secret|password|token|private_key)\s*=\s*['\"]?.{8,}"
# Or use gitleaks if installed:
gitleaks detect --source . --no-git 2>/dev/null || echo "gitleaks not installed"
```

### 1b. .env not staged
```bash
git status | grep "\.env$" && echo "⚠️ .env is staged — remove it!" || echo "✓ .env not staged"
```

### 1c. .gitignore covers sensitive paths
Verify these are in `.gitignore`:
- `.env` — secrets
- `store/` — database
- `data/` — auth/sessions
- `node_modules/`
- `*.keys.json`, `*.pem`, `*.p12`, `auth.json`

---

## Layer 2 — Recoverability Audit (0 → 100% on New Machine)

This is the critical layer. Ask: **"If someone clones this repo fresh, can they reach full working state?"**

### Gap Checklist — run through each:

| Gap | Check | Fix |
|-----|-------|-----|
| **Env vars** | `.env.example` exists and has ALL required vars with comments? | Update `.env.example` to mirror real `.env` keys (not values) |
| **System deps** | Node version documented? (`.nvmrc` or README) | Add `.nvmrc` with `node --version` output |
| **Package deps** | `npm install` works cleanly from scratch? | Verify `package-lock.json` committed |
| **Build step** | `npm run build` documented or in setup script? | Add to `setup.sh` or `Makefile` |
| **Docker images** | Can all images be built from repo? (Dockerfile present?) | Ensure `docker build` command in setup |
| **External config** | Config files OUTSIDE project root documented? | Add to README + setup script |
| **One-command setup** | Is there a `setup.sh` or `Makefile` that handles all of above? | Create/update setup script |
| **First-run instructions** | Does README clearly explain steps 1→N? | Update README with exact commands |
| **State/DB** | Database migrations run automatically? | Add migration call to startup |
| **Third-party accounts** | External services (WhatsApp, Stripe, etc.) documented? | Add to README — cannot automate |

### Effort Score
After the checklist, rate the gap effort:
- **0-2 manual steps after clone** → ✅ Seamless
- **3-4 manual steps** → ⚠️ Acceptable but document them
- **5+ manual steps** → ❌ Fix before pushing — add automation

### Auto-fixable gaps (do these now if found):
```bash
# Sync .env.example with actual .env keys (strips values)
grep -E "^[A-Z_]+=.*" .env | sed 's/=.*/=/' > .env.example.new
# Then manually add comments and placeholder values
```

---

## Layer 3 — Git Workflow

### Standard flow:
```bash
# 1. Check current branch (never push directly to main)
git branch --show-current

# 2. Stage selectively (not git add .)
git add -p   # review each change

# 3. Commit with conventional format
git commit -m "type(scope): short description

- bullet: what changed and why
- bullet: any breaking changes or migrations needed"

# 4. Push
git push origin <branch-name>
```

### Commit types:
| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `chore` | Tooling, deps, setup scripts |
| `security` | Security hardening |
| `refactor` | Restructure without behavior change |

---

## Output to User

After completing all layers, report:

```
## Safe Push Report

### 🔒 Security
✓ No secrets in staged files
✓ .env gitignored
⚠️ [any issues found]

### 🔄 Recoverability (0 → 100% New Machine)
✓ .env.example complete
✓ setup.sh handles deps + build + docker
⚠️ Missing: [gap name] — [suggested fix]
Effort score: X manual steps → [Seamless / Acceptable / Fix needed]

### 📦 Git
Branch: feat/xxx
Commit: [hash] "type(scope): description"
Pushed to: origin/personal/xxx

---
Overall: ✅ Safe to push / ⚠️ Fix before push
```
