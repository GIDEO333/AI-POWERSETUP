---
name: skills-hunter-session
description: >
  Meta-skill. Analyzes the current session to identify recurring patterns,
  workflows, or domain knowledge that could be codified into reusable skills.
  Run at the end of a productive session to capture institutional knowledge
  before it's lost.
  Trigger: "skills-hunter-session", "cari skill baru dari sesi ini",
  "ada skill yang bisa dibuat?", "skill extraction".
---

# Skills Hunter — Session Edition

## Purpose

Conversations contain hidden patterns. This skill extracts them.

A good skill candidate:
- Solves a **repeatable problem** (not one-time)
- Has a **clear trigger** (user knows when to invoke it)
- Has a **structured process** (not just "think about it")
- Is **scope-bounded** (not too broad, not too narrow)

---

## How to Run

### Step 1 — Session Scan

Review the full conversation and list every:
- **Problem type** that was solved (what category of task?)
- **Process** used to solve it (what steps were followed?)
- **Decision** made with trade-off reasoning
- **External tool** invoked in a structured way

### Step 2 — Candidate Filter

For each item found, score it:

| Criteria | Question | Yes = +1 |
|----------|----------|----------|
| Repeatability | Will this come up again? | |
| Generic | Applicable beyond this specific project? | |
| Structured | Does it have clear steps? | |
| Triggerable | Easy to know when to invoke? | |
| Additive | Not already covered by existing skills? | |

**Score ≥ 3/5 → Worth creating as a skill**

### Step 3 — Draft Skill(s)

For each candidate ≥ 3/5, propose:
```
Skill Name:    [kebab-case]
Trigger:       [natural language phrases]
Description:   [one sentence what it does]
Core Process:  [3-5 bullet steps]
Existing skill overlap: [none / partial with X]
Score: X/5
```

### Step 4 — Present & Wait for Confirmation ⚠️ MANDATORY

**NEVER auto-create skills.** After Step 3, present ALL candidates to the user in this format:

```
## Skills-Hunter Results

Found X candidates:

| # | Skill Name | Score | Description |
|---|-----------|-------|-------------|
| 1 | `name` | 5/5 | one line |
| 2 | `name` | 4/5 | one line |
| 3 | `name` | 3/5 | one line |

**Which ones should I create?** (e.g., "buat 1 dan 2", "semua", "1 saja")
Sisanya otomatis masuk memory queue.
```

**Only after user confirms** → proceed to Step 5.

### Step 5 — Execute (only after confirmation)

For confirmed skills → create `~/.agent/skills/skills/<name>/SKILL.md`
For rejected/unconfirmed → queue to `~/.agent/memory/topics/skills-built.md`:
```markdown
### Candidate: skill-name
- Score: X/5 | Session: YYYY-MM-DD | Promote when: [condition]
```

---

### Step 6 — Universal Skill Log ⚠️ ALWAYS RUN (regardless of user choice)

**After every session scan — no exceptions — append ALL detected candidates to the acquisition log.**
This runs even if the user says "skip all" or "none". It is non-destructive and never creates skill files.

File: `~/.agent/memory/topics/skill-acquisition-log.md`

Format for each entry:
```markdown
| YYYY-MM-DD | `skill-name` | X/5 | installed / queued / rejected | one-line description | trigger phrase |
```

If the file doesn't exist yet, create it with this header first:
```markdown
# Skill Acquisition Log
> All skills ever detected by skills-hunter, regardless of install status.
> Query this to see what skills you could still acquire.

| Date | Skill Name | Score | Status | Description | Trigger |
|------|-----------|-------|--------|-------------|---------|
```

**Status values:**
- `installed` — SKILL.md was created this session
- `queued` — saved to skills-built.md candidate queue
- `rejected` — user explicitly declined
- `duplicate` — already exists as an active skill

**Trigger for querying this log:**
User says: *"skill apa yang bisa saya acquire?"*, *"list semua skill kandidat"*,
*"show skill backlog"*, *"skill yang belum dibuat apa aja?"*
→ Read `skill-acquisition-log.md` and present a filtered table (exclude `installed` and `duplicate` by default, unless user asks for full list).

---

## Naming Convention

```
[verb]-[noun]          # action-oriented: safe-push, deep-research
[domain]-[action]      # domain-first: query-requestout, docker-audit
[noun]-[qualifier]     # noun-first: session-memory, skills-hunter-session
```

---

## Real Example: Session 2026-02-27 (NanoClaw Security Audit)

Running Step 1-3 on this very session:

### Candidates Found:

**A. `docker-security-audit`**
- **Problem:** Any Docker-containerized project has the same security gaps to check (egress, sandbox, secrets, mounts, network)
- **Process:** Check egress → check sandbox (seccomp) → check plaintext secrets → check network restrictions → check volume mounts → score each gap → propose fixes with trade-offs
- **Score: 5/5** → Create now
- **Trigger:** "audit keamanan docker", "docker security check", "docker security gaps"

**B. `proxy-sidecar-setup`**
- **Problem:** Any Docker project may need a logging or filtering egress proxy
- **Process:** Choose logging vs allowlist vs hybrid → select tool (tinyproxy/Squid) → create Dockerfile + config → integrate with container-runtime → test
- **Score: 4/5** → Queue (slightly too NanoClaw-specific in current form)

**C. `db-lifecycle`**
- **Problem:** Any SQLite/embedded DB project needs archiving/purging strategy
- **Process:** Audit for auto-purge → estimate growth rate → choose delete/archive/tiered → implement with configurable retention → document
- **Score: 3/5** → Queue

**D. `perplexity-eval`** → Already captured as `query-requestout` ✅

**E. `safe-push`** → Already created ✅

---

## Skill Candidate Queue Template

When adding to `~/.agent/memory/topics/skills-built.md`:

```markdown
### Candidate: [skill-name]
- Score: X/5
- Trigger: [phrase]
- Core idea: [one line]
- Session source: [YYYY-MM-DD | session topic]
- Promote to skill when: [condition e.g., "used 3+ times"]
```
