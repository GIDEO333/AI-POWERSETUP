---
name: session-export
description: >
  Exports the full agentic coding session — including chat decisions, terminal 
  commands & outputs, multi-agent orchestration logs (Worker/QA sprint results),
  files created/modified, and test results — into a structured Markdown file.
  Trigger: "export session", "cetak sesi", "print session log", "bikin log 
  lengkap", "save full session", "session to markdown".
category: Memory
---

# Session Export: Full Agentic Trace to Markdown

## Kapan Digunakan
- Di akhir sesi coding yang produktif dan user ingin dokumentasi lengkap
- User ingin bukti tertulis dari seluruh proses AI-assisted development
- Setelah menjalankan Triple Agent sprint dan ingin merekam hasilnya
- Untuk arsip, handoff ke tim, atau referensi masa depan

## Perbedaan dengan session-memory

| | session-memory | session-export |
|---|---|---|
| Output | Max 10 baris ringkasan | Full chronological log |
| Isi | Keputusan & insight saja | Chat + terminal + agent logs + files + tests |
| Lokasi | `~/.agent/memory/session-log.md` | `<project-dir>/session-export-YYYY-MM-DD.md` |
| Tujuan | Memori AI lintas sesi | Dokumentasi manusia |

## Prosedur Export

### Step 1: Kumpulkan Data
Scan seluruh konteks sesi saat ini dan kumpulkan:
1. **Timeline**: Urutan kronologis semua aksi utama
2. **Terminal Commands**: Setiap command yang dieksekusi dan output-nya
3. **Files Touched**: Daftar file yang dibuat, dimodifikasi, atau dihapus
4. **Keputusan**: Trade-off yang diambil dan alasannya
5. **Test Results**: Semua output verifikasi (exit codes, test results)
6. **Errors & Fixes**: Bug yang ditemukan dan cara perbaikannya

### Step 2: Kumpulkan Data Multi-Agent Orchestration (Jika Ada)
Jika sesi ini melibatkan Triple Agent pipeline (`agent_sprint.sh`), WAJIB capture:

1. **architecture_plan.md** — Baca dari project directory yang di-sprint
2. **Sprint Log** — Output terminal dari agent_sprint.sh:
   - Attempt number (1/3, 2/3, 3/3)
   - Worker exit code
   - QA exit code
   - Final status (PASS/FAIL)
3. **qa_report.md** — Baca dari project directory:
   - STATUS: PASS atau FAIL
   - Daftar test commands yang dijalankan QA
   - Hasil per test
4. **Worker Output** — Apa yang Worker agent hasilkan (files, code)
5. **Retry History** — Jika ada retry, catat alasan dan hasil tiap attempt

Format section orchestration:
```markdown
## 🤖 Multi-Agent Orchestration Log

### Sprint Config
| Setting | Value |
|---------|-------|
| Script | agent_sprint.sh v2.1 |
| Worker Prompt | claude_glm47_worker_prompt.md |
| QA Prompt | claude_glm47_qa_prompt.md |
| Max Attempts | 3 |

### Architecture Plan
> [Ringkasan isi architecture_plan.md]

### Sprint Execution
#### Attempt 1
- **Worker Phase**: [output ringkasan]
  - Exit Code: [0/1]
  - Files Created: [list]
- **QA Phase**: [output ringkasan]
  - Exit Code: [0/1]
  - Tests Run: [N]
  - Result: [PASS/FAIL]

#### Attempt 2 (jika ada retry)
- **Reason**: [kenapa retry]
- ...

### QA Report Summary
| Test | Command | Result |
|------|---------|--------|
| ... | ... | ✅/❌ |

**Final Verdict:** STATUS: PASS ✅ (Attempt X of Y)
```

### Step 3: Susun Markdown Lengkap
Tulis ke file dengan struktur berikut:

```markdown
# 📜 Session Export: [Judul Sesi]
**Tanggal:** YYYY-MM-DD
**Model:** [model yang dipakai]
**Durasi:** [estimasi dari timestamp pertama ke terakhir]

---

## ⏱️ Timeline Kronologis

### HH:MM — [Aksi/Milestone]
- Apa yang dikerjakan
- Terminal command:
  ```bash
  $ command
  output
  ```
- Hasil: ✅/❌

---

## 🤖 Multi-Agent Orchestration Log
[Section ini HANYA muncul jika sprint dijalankan di sesi ini]
[Format: lihat Step 2 di atas]

---

## 📁 Files Touched
| File | Action | Lines |
|------|--------|-------|
| path/to/file | Created/Modified/Deleted | N |

---

## 🧪 Test & Verification Results
| Test | Command | Result | Exit Code |
|------|---------|--------|-----------|
| ... | ... | PASS/FAIL | 0/1 |

---

## 🧠 Keputusan & Trade-offs
1. **[Keputusan]** — Karena [alasan]

---

## 🐛 Bugs Found & Fixed
| # | Bug | Severity | Fix |
|---|-----|----------|-----|
| 1 | ... | 🔴/🟡/🟢 | ... |

---

## 📊 Session Scorecard
| Metric | Value |
|--------|-------|
| Files Created | N |
| Files Modified | N |
| Tests Run | N |
| Bugs Fixed | N |
| Sprints Executed | N |
| Sprint Attempts | N |
| Sprint Final Status | PASS/FAIL |
```

### Step 4: Simpan File
Simpan ke direktori proyek yang sedang dikerjakan:
```bash
<project-dir>/session-export-YYYY-MM-DD.md
```

Jika user tidak sedang di project tertentu, simpan ke:
```bash
~/.agent/memory/exports/session-export-YYYY-MM-DD.md
```

### Step 5: Konfirmasi ke User
```
✅ Session exported ke: <path>
📊 Isi: X milestones, Y terminal commands, Z files touched
🤖 Orchestration: N sprint(s) captured
```

## AI Management Protocol
- AI yang menyusun seluruh isi file, user TIDAK perlu menulis apapun
- Jangan tanya user apa yang harus ditulis — scan konteks sendiri
- Jika sesi sangat panjang, kelompokkan aksi ke phase/milestone
- Terminal output yang terlalu panjang (>20 baris) harus diringkas
- Sertakan screenshot/recording paths jika ada (dari browser subagent)
- Untuk multi-agent data: baca `architecture_plan.md` dan `qa_report.md` langsung dari project dir
- Jika sprint dijalankan background (`&`), ambil data dari command_status output

## Error Handling
- Jika folder exports belum ada: `mkdir -p ~/.agent/memory/exports`
- Jika tidak ada terminal commands di sesi: skip bagian Terminal
- Jika sesi sangat pendek (<3 aksi): sarankan user pakai `session-memory` saja
- Jika `qa_report.md` tidak ditemukan tapi sprint dijalankan: catat sebagai "QA report missing"
- Jika `architecture_plan.md` tidak ada: catat "Sprint ran without plan (anomaly)"
