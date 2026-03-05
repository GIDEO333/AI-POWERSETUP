---
name: powersetup-healthcheck
description: Diagnosa kesehatan seluruh ekosistem AI coding tools — cek symlinks, CLI tools, configs, dan koneksi antar komponen / Health check for entire AI power-up coding ecosystem
category: Ops
---

# PowerSetup Health Check

## Kapan Menggunakan Skill Ini
- User ingin memastikan seluruh tool AI coding mereka berfungsi
- Setelah update Antigravity, macOS, atau install fresh
- Sebelum memulai proyek baru yang membutuhkan Triple Agent pipeline
- Jika ada error/perilaku aneh pada workflow AI

## Prosedur Diagnostik

### Step 1: Jalankan Script Diagnostik
Jalankan script health check yang sudah disediakan:
```bash
sh ~/.agent/skills/skills/powersetup-healthcheck/scripts/healthcheck.sh
```

Script ini akan memeriksa SEMUA komponen berikut secara otomatis:

| # | Komponen | Apa yang Dicek |
|---|----------|----------------|
| 1 | GEMINI.md | Apakah ~/.gemini/GEMINI.md ada dan valid |
| 2 | Symlinks | Apakah semua symlink utuh (tidak broken) |
| 3 | Claude CLI | Apakah `claude` terinstal dan versinya |
| 4 | Triple Agent Repo | Apakah repo git bersih atau ada uncommitted changes |
| 5 | Workflow Files | Apakah ~/.agent/workflows/ berisi file yang benar |
| 6 | Prompt Files | Apakah worker & QA prompt .md berisi tag XML wajib |
| 7 | Skills Index | Apakah skills-index.json ada dan up to date |
| 8 | GLM Bridge | Apakah glm_bridge_server.py ada |
| 9 | Switchboard | Apakah switchboard directory ada |
| 10 | agent_sprint.sh | Bash syntax check |

### Step 2: Baca Output
Script akan menghasilkan output dengan format:
```
✅ = Healthy
⚠️ = Warning (bisa jalan, tapi perlu perhatian)
❌ = BROKEN (harus diperbaiki)
```

### Step 3: Auto-Fix (Jika Ada Error)
Untuk error umum, jalankan:
```bash
# Fix symlinks:
cd ~/Projects/triple-agent-orchestrator && ./install.sh

# Fix skills index:
cd ~/Projects/AI-POWERSETUP && python3 agent/scripts/build-skills-index.py
```

## Contoh Output
**Input:** User mengatakan "cek kesehatan tools saya" atau "health check" atau "ada yang broken gak"
**Output:**
```
🏥 AI PowerSetup Health Check
========================================
✅ [1/10] GEMINI.md: Found (86 lines, 7 rules)
✅ [2/10] Symlinks: All 3 intact
✅ [3/10] Claude CLI: v2.1.59
⚠️ [4/10] Git Status: 2 uncommitted files
✅ [5/10] Workflows: 2 files linked
✅ [6/10] Prompt Files: XML tags valid
✅ [7/10] Skills Index: 36 skills indexed
✅ [8/10] GLM Bridge: Present
✅ [9/10] Switchboard: Present
✅ [10/10] agent_sprint.sh: Syntax OK
========================================
RESULT: 9 HEALTHY | 1 WARNING | 0 BROKEN
```

## AI Management Protocol (PENTING)
Ketika user meminta menambahkan tool baru ke health check:
1. **User cukup bilang** nama tool dan path-nya (contoh: "tambahkan NanoClaw ke health check")
2. **AI (Anda) yang mengedit** file `~/.agent/skills/skills/powersetup-healthcheck/components.json`
3. Tambahkan entry JSON baru dengan `check` type yang sesuai
4. Jalankan health check untuk memverifikasi tool baru terdaftar
5. **JANGAN suruh user edit JSON** — itu tanggung jawab AI sepenuhnya

## Error Handling
- Jika script `healthcheck.sh` tidak ditemukan: buat ulang via `/new-skill`
- Jika seluruh symlink rusak: jalankan `install.sh` dari `triple-agent-orchestrator`
- Jika Claude CLI hilang: install ulang via `npm install -g @anthropic-ai/claude-code`
