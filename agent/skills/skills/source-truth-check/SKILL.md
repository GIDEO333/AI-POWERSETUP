---
name: source-truth-check
description: >
  Verifies external claims (from articles, other AIs, docs, handoff notes)
  against the actual source code or config files of the current project.
  Produces a verdict (confirmed / different / partially true) with exact file evidence.
  Trigger: "cek apakah benar...", "verify klaim ini", "beneran gak?",
  "cek saja tak perlu ubah", "source truth check", "fact check ini".
category: QA
---

# Source-Truth-Check

## Purpose

External claims about how a system works (from articles, AI assistants,
documentation, handoff notes) can be stale, wrong, or specific to a different
version. This skill cuts through assumptions and delivers a verdict grounded
in the actual code — not opinion.

---

## How to Run

### Step 1 — Extract the Claim

Identify the **single, specific claim** being checked. Write it in one sentence:

> *"NanoClaw uses Apple's native micro-VM framework to sandbox agents."*

### Step 2 — Identify the Key Files

Based on the claim's domain, determine **which file(s)** are the ground truth.
Do NOT scan the whole codebase — go directly to the most relevant layer:

| Claim Domain | Where to look first |
|---|---|
| Container / runtime | `container-runtime.ts`, `Dockerfile`, `docker-compose.yml` |
| Auth / secrets | `*.env`, config files, secret-handling modules |
| API / model backend | config, client init files, `.env` keys |
| Network / security | firewall configs, proxy setup, network flags |
| Feature flag / behavior | config constants, feature flag files |

### Step 3 — Read & Compare

Read only the relevant sections. Look for:
- The **exact setting, binary, or API** being referenced
- Any **constants or defaults** that confirm or contradict the claim

### Step 4 — Deliver Verdict

Report with one of three verdicts, plus evidence:

| Verdict | Meaning |
|---|---|
| ✅ **Confirmed** | Code does exactly what was claimed |
| ❌ **Different** | Code does something else — explain what it actually does |
| ⚠️ **Partially True** | Some parts match, some don't — specify each |

**Format:**
```
Claim: [one sentence]
Verdict: ✅ / ❌ / ⚠️
Evidence: [file:line or key code snippet]
Gap (if any): [what's different / missing]
Note: [optional — e.g., "this could change with version X"]
```

---

## When NOT to Use

- When the claim is about a **third-party library** (check their docs/GitHub instead)
- When the user wants to **change** something (use a different skill for implementation)
- When the claim is so vague it can't be traced to a specific file

---

## Example Run

**Input claim:** *"NanoClaw uses Apple's native micro-VM to isolate agents."*

**Step 2:** Container runtime claim → check `src/container-runtime.ts`

**Step 3:** Found:
```typescript
export const CONTAINER_RUNTIME_BIN = 'docker';
```

**Step 4 — Verdict:**
```
Claim: NanoClaw uses Apple's native micro-VM to isolate agents.
Verdict: ❌ Different
Evidence: src/container-runtime.ts line 10 — CONTAINER_RUNTIME_BIN = 'docker'
Gap: NanoClaw uses standard Docker as its container runtime, not Apple Containers.
Note: The abstraction layer (container-runtime.ts) makes migration feasible
      with minimal changes if Apple Containers matures.
```
