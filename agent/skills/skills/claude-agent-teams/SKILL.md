---
name: claude-agent-teams
description: Orkestrasi peer-to-peer Claude Code Agent Teams — spawn teammate, mailbox protocol, file ownership, constraint injection, shared task list untuk coding paralel / Orchestrate Claude Code peer-to-peer Agent Teams with teammate spawning, mailbox protocol, file ownership matrix, and constraint-injected parallel execution
category: AI-Orchestration
---

# 🤖 Claude Code Agent Teams Deployment Skill

## Deskripsi / Description
Skill ini memberikan panduan terstruktur tentang kapan dan bagaimana menggunakan fitur eksperimental Claude Code Agent Teams. Agent Teams memungkinkan eksekusi tugas paralel secara peer-to-peer dengan isolasi konteks (context isolation).
*This skill provides a structured guide on when and how to use the experimental Claude Code Agent Teams feature for peer-to-peer parallel task execution with context isolation.*

## 📋 Aturan Pemakaian (Usage Rules)

1. **Gunakan Agent Teams hanya untuk tugas paralel (Use Agent Teams only for parallel tasks).**
   - Contoh yang benar: Audit keamanan, review kode paralel, pembuatan module frontend & backend sekaligus.
   - Jangan gunakan untuk: Tugas berurutan (sekuensial), perbaikan bug kecil, atau edit satu file sederhana.
2. **Setup Environment Variable Terlebih Dahulu.**
   - Pastikan variabel `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` telah di-set sebelum meluncurkan Claude Code.
3. **Selalu Gunakan Pola "Plan-First" (Always use "Plan-First" pattern).**
   - Wajibkan Team Lead untuk membuat rencana (architecture/implementation plan) dan mendapatkan persetujuan *user* sebelum menulis kode.
4. **Berikan Konteks yang Sangat Kaya (Provide very rich context).**
   - Buat file `CLAUDE.md` di root proyek. File ini akan otomatis di-load oleh semua *teammate*.
   - Berikan *role* spesifik kepada tiap teammate (misal: "UI Designer", "Security Reviewer").
5. **Ukuran Tugas Sedang (Moderate Task Sizing).**
   - Pecah tugas menjadi sekitar 5-6 *tasks* per teammate. Terlalu kecil akan membuang token untuk overhead koordinasi.
6. **Wajibkan Verifikasi Mandiri (Require self-verification).**
   - Instruksikan tiap teammate untuk menguji pekerjaannya sendiri (misal: menjalankan unit test `pytest` atau `npm test`).
7. **Tetapkan Kepemilikan File (Assign File Ownership). [Plan C]**
   - Team Lead WAJIB menetapkan kepemilikan file/folder per teammate **sebelum** spawn.
   - Format penetapan: *"Teammate-UI owns `src/components/`, `src/pages/`"* / *"Teammate-Backend owns `src/api/`, `src/lib/`"*
   - **LARANGAN KERAS:** Dua teammate tidak boleh menulis ke file yang sama. Pelanggaran = race condition & silent data loss.
   - Jika ada *shared file* (misal `package.json`), hanya Team Lead yang boleh mengeditnya setelah semua teammate selesai.
8. **Injeksi Constraint ke Semua Teammate (Inject Constraints). [Plan A]**
   - `CLAUDE.md` WAJIB memuat 4 pilar dari skill `agent-constraint-schema`:
     - **Anti-Bleeding:** Maks 3 kalimat reasoning per aksi. Lebih dari itu = kegagalan sistematis.
     - **Execution First:** Placeholder code `// TODO` = LARANGAN MUTLAK. Konteks hilang → baca filesystem.
     - **Anti-Hanging:** Dilarang menjalankan server/daemon non-terminating (`npm run dev`, `python -m http.server`).
     - **Escalate Rule:** Gagal kompilasi 3x berturut-turut → STOP, cetak `ESCALATION REQUIRED`, tunggu Team Lead.

## 🛠️ Langkah Eksekusi (Execution Steps)

1. Evaluasi permintaan *user*. Jika tugas tersebut berurutan atau kecil, **tolak** penggunaan Agent Teams dan jelaskan alasannya (biaya token tinggi). Arahkan ke `multi-agent-orchestrator` + `agent_sprint.sh` sebagai alternatif sekuensial.
2. Jika *user* setuju, buat `CLAUDE.md` yang memuat: aturan proyek, arsitektur dasar, **dan 4 pilar constraint** (Rule 8).
3. Buat **File Ownership Matrix** — daftar folder/file per teammate (Rule 7). Tuliskan di dalam rencana arsitektur.
4. Buat folder `.agent-teams/mailbox/` di root proyek (lihat Protokol Mailbox di bawah).
5. Instruksikan Claude Code untuk menjalankan tim menggunakan format Role Spesifik + ownership assignment.
6. Pantau jalannya tim. Jika ada *teammate* yang stuck, Anda (Antigravity) wajib proaktif menghentikannya atau memberikan konteks tambahan untuk menyelamatkan token limit.

## 📬 Protokol Mailbox (Mailbox Protocol) [Plan B]

Komunikasi antar teammate menggunakan **file-based mailbox** untuk sinkronisasi interface:

- **Lokasi:** `.agent-teams/mailbox/` di root proyek
- **Format nama file:** `{sender}-to-{receiver}.md` (contoh: `ui-to-backend.md`)
- **Isi:** Interface contract, API schema, shared type definitions, atau dependency requests
- **Aturan:**
  1. Tiap teammate hanya **MENULIS** ke file dengan prefix namanya sendiri sebagai sender
  2. Tiap teammate boleh **MEMBACA** semua file mailbox
  3. Team Lead bertanggung jawab mendeteksi dan menyelesaikan konflik
  4. Pesan dianggap *acknowledged* jika receiver menulis file balasan (contoh: `backend-to-ui.md`)

**Contoh isi mailbox:**
```markdown
# ui-to-backend.md
## API Contract Request
- GET /api/weather?city={string} → { temp: number, condition: string }
- GET /api/forecast?city={string}&days={number} → { days: ForecastDay[] }
```

## 📌 Contoh Penggunaan (Input / Output Example)

**Input (User):**
"Buat aplikasi cuaca. Gunakan Agent Teams ya, satu urus UI/UX frontend, satu urus backend cuaca."

**Output (Agent Process):**
1. Agent mengevaluasi: ✅ Cocok untuk Teams — frontend & backend genuinely independent.
2. Agent memastikan `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.
3. Agent membuat `CLAUDE.md` berisi standar stack + **4 pilar constraint**.
4. Agent menetapkan **File Ownership:**
   - Teammate-UI owns: `src/components/`, `src/pages/`, `src/styles/`
   - Teammate-Backend owns: `src/api/`, `src/lib/`, `src/utils/`
   - Shared (`package.json`, `tsconfig.json`): Team Lead only
5. Agent membuat folder `.agent-teams/mailbox/`.
6. Agent memanggil perintah: "Create an agent team for the weather app. Spawn 1 UI teammate (owns `src/components/`, `src/pages/`, `src/styles/`) and 1 Backend teammate (owns `src/api/`, `src/lib/`, `src/utils/`). Each teammate MUST write API contracts to `.agent-teams/mailbox/` before coding. Follow all constraints in CLAUDE.md."

## ⚠️ Penanganan Kesalahan (Error Handling)

- **Masalah:** Teammate berhenti bekerja setelah error (Teammate stopping on errors)
  - **Identifikasi:** Teammate bingung dengan *output* error terminal.
  - **Tindakan:** Berikan instruksi tambahan secara langsung kepada teammate tersebut atau hentikan teammate itu dan spawn teammate baru untuk melanjutkan tugas.
- **Masalah:** Teammate macet menunggu tugas selesai (Lagging task status)
  - **Identifikasi:** Tugas sudah selesai tapi status di JSON belum di-update.
  - **Tindakan:** Update status JSON secara manual atau instruksikan Lead agent untuk mengingatkan (*nudge*) teammate yang bersangkutan.
- **Masalah:** Token limit tercapai dengan cepat (Token usage scaling wildly)
  - **Identifikasi:** Tim terlalu besar atau tugas terlalu abstrak.
  - **Tindakan:** Beralih ke Claude Code standar atau perkecil jumlah agent di tim tersebut menjadi maksimal 2 teammate.
- **Masalah:** Dua teammate menulis ke file yang sama (File collision)
  - **Identifikasi:** Git diff menunjukkan perubahan dari satu teammate hilang.
  - **Tindakan:** STOP semua teammate. Review File Ownership Matrix. Re-assign dan spawn ulang.

## 🔄 Fallback & Alternatif

- Jika fitur `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` tidak tersedia atau gagal → gunakan **`multi-agent-orchestrator`** + **`agent_sprint.sh`** sebagai pipeline sekuensial (Architect → Worker → QA).
- Jika tim hanya 2 agent dengan dependensi tinggi → pertimbangkan mode sekuensial biasa, token lebih hemat.

## 🔗 Skill Terkait (Related Skills)

- [`agent-constraint-schema`](file:///Users/gideonthirtytres/.agent/skills/skills/agent-constraint-schema/SKILL.md) — 4 pilar constraint yang wajib diinjeksi (Rule 8)
- [`multi-agent-orchestrator`](file:///Users/gideonthirtytres/.agent/skills/skills/multi-agent-orchestrator/SKILL.md) — Alternatif sekuensial (Architect → Worker → QA)
- [`ai-system-evaluator`](file:///Users/gideonthirtytres/.agent/skills/skills/ai-system-evaluator/SKILL.md) — Evaluasi post-execution kualitas tim
- [`headless-cli-wrapper`](file:///Users/gideonthirtytres/.agent/skills/skills/headless-cli-wrapper/SKILL.md) — Panduan headless spawning
