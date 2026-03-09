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
     - **Anti-Hanging:** Server/daemon non-terminating MUTLAK dilarang (`npm run dev`, `python -m http.server`, watch mode). TIDAK ADA PENGECUALIAN untuk kategori ini.
     - **Long Command:** Build atau test suite wajib dibungkus timeout: `timeout -k 10s 60s <command>`. Jika exit non-zero atau melebihi 60s → terapkan Escalate Rule.
      - **Escalate Rule:** Gagal kompilasi 3x berturut-turut → STOP, cetak `ESCALATION REQUIRED`, tunggu Team Lead.

## 🏗️ Arsitektur Peran (Role Separation)

Dalam workflow ini, **Antigravity memakai 3 topi** sekaligus:

| Topi | Fungsi | Detail |
|---|---|---|
| 🏠 **Architect** | Perencanaan | Buat `implementation_plan.md`, `CLAUDE.md`, File Ownership Matrix, mode selection, semua artifacts |
| 🚀 **Launcher** | Spawn worker | Launch `claude --dangerously-skip-permissions` dari root project directory |
| 👁️ **Supervisor** (Event-Driven) | Pantau by signal | Hanya intervensi saat `ESCALATION.md` atau `*-DONE.md` muncul di mailbox. **BUKAN polling terminal.**|

**Yang TIDAK dilakukan Antigravity:** Menulis source code proyek secara langsung.

| Peran | Siapa | Tanggung Jawab | TIDAK BOLEH |
|---|---|---|---|
| **Architect + Launcher + Supervisor** | Antigravity (MCP Agent) | Plan, spawn CLI, intervensi by signal, Gather Phase | Menulis source code proyek langsung |
| **Worker / Builder** | Claude Code CLI | Semua coding, testing, file creation, refactoring | Mengubah file di luar project directory |

### Cara Aktivasi Claude Code CLI sebagai Worker

```bash
# Aktifkan Claude Code CLI dengan full autonomous mode:
claude --dangerously-skip-permissions
```

### Workflow Lengkap

```
1. USER → brief proyek ke Antigravity
2. Antigravity [🏠 Architect]:
   → Buat implementation_plan.md, CLAUDE.md (+ sandbox rule + escalation protocol),
     File Ownership Matrix, architecture_plan.md
   → Buat folder .agent-teams/mailbox/
3. Antigravity [🚀 Launcher]:
   → Launch: claude --dangerously-skip-permissions (dari root project dir)
4. Claude Code CLI [Worker]:
   → Auto-load CLAUDE.md → mulai coding berdasarkan plan
   → Jika stuck 3x → tulis ESCALATION.md → STOP
   → Jika selesai → tulis [agent]-DONE.md
5. Antigravity [👁️ Supervisor]:
   → Cek mailbox (event-driven, BUKAN polling):
     - ESCALATION.md ada? → Analisa error, berikan fix, re-spawn jika perlu
     - Semua DONE.md ada? → Lanjut ke Gather Phase (Mode 1) atau final review (Mode 2)
6. Antigravity [🏠 Architect]:
   → Deliver hasil ke user
```

> ⚠️ **PENTING:** Antigravity sebagai Supervisor TIDAK mem-polling terminal setiap 30 detik. Supervisi bersifat **event-driven** — hanya aktif saat ada file signal di `.agent-teams/mailbox/`. Ini menjaga token Antigravity tetap hemat.

## 🔒 Workspace Sandboxing

Claude Code CLI agents **WAJIB hanya bekerja di dalam project directory**. Ini memastikan jika terjadi kesalahan fatal, cukup hapus folder proyek → mulai ulang.

**Aturan Sandboxing:**
1. **Working Directory:** Claude CLI HARUS di-launch dari root project directory.
2. **Cakupan Izin:** Agent hanya boleh membuat/edit/hapus file di dalam `$PROJECT_DIR/` dan subfolder-nya.
3. **DILARANG:** Mengubah file di `~/`, `~/.gemini/`, `/etc/`, `/usr/`, atau direktori sistem lainnya.
4. **CLAUDE.md harus memuat instruksi sandbox + escalation protocol:**
   ```
   ## WORKSPACE SANDBOX
   Kamu HANYA boleh membuat/edit file di dalam folder proyek ini.
   DILARANG KERAS menyentuh file di luar direktori proyek.
   Jika perlu install dependency: gunakan package manager (npm install, pip install)
   yang akan menulis ke node_modules/ atau .venv/ di dalam proyek.

   ## ESCALATION PROTOCOL
   1. Jika error kompilasi/test gagal 3x berturut-turut:
      → Tulis file `.agent-teams/mailbox/ESCALATION.md` dengan isi:
        - Error message terakhir
        - File yang sedang dikerjakan  
        - Apa yang sudah dicoba (3 attempt)
      → STOP SEMUA pekerjaan. Jangan coba lagi. Tunggu instruksi dari Supervisor.

   2. Jika task selesai (semua coding done + test hijau):
      → Tulis file `.agent-teams/mailbox/[nama-agent]-DONE.md` dengan isi:
        - Summary singkat apa yang dibangun
        - File-file yang dibuat/diubah
        - Status test terakhir

   3. Jika butuh output dari agent lain yang belum siap:
      → Tulis request ke `.agent-teams/mailbox/[kamu]-to-[partner].md`
      → Lanjutkan task lain yang tidak bergantung pada output tersebut.
   ```
5. **Recovery plan:** Jika proyek rusak total → `rm -rf $PROJECT_DIR && git clone` atau mulai ulang dari scratch.

## 🎯 Prompt Engineering Guide (WAJIB Sebelum Mode Selection)

Saat skill `claude-agent-teams` diaktifkan, Antigravity **WAJIB interview user dulu** sebelum menentukan mode dan meng-craft prompt. Jangan langsung spawn agent.

### Step 1 — Interview (5 Pertanyaan Kunci)

Antigravity mengajukan pertanyaan berikut satu per satu atau sekaligus (sesuai konteks):

> **1. 🏗️ Apa yang mau dibangun?**
> Jelaskan singkat proyek Anda. (Contoh: "Marketplace untuk AI agent skills")
>
> **2. ⚙️ Stack teknologi apa yang Anda inginkan?**
> Framework, bahasa, database, styling. (Contoh: "Next.js, Supabase, Tailwind, TypeScript")
>
> **3. 🧩 Ada berapa domain/area besar dalam proyek ini?**
> Ini menentukan Mode 1 (Scatter-Gather) vs Mode 2 (Reflection).
> (Contoh: "Frontend + Backend + Parser markdown = 3 domain")
>
> **4. 🎨 Ada requirement khusus untuk UI/UX?**
> Dark mode, premium look, mobile-first, dsb. (Opsional)
>
> **5. 📂 Dari nol atau sudah ada codebase?**
> Jika sudah ada: sebutkan path project directory-nya.

### Step 2 — Antigravity Craft Prompt Otomatis

Setelah interview selesai, Antigravity **meng-generate prompt terstruktur** menggunakan template berikut lalu **langsung eksekusi** tanpa perlu user copy-paste:

```
[TEMPLATE — diisi oleh Antigravity berdasarkan jawaban interview]

Buat {NAMA_PROYEK} dari nol menggunakan skill `claude-agent-teams`.

Kamu adalah Antigravity dengan 3 topi: Architect, Launcher, dan Event-Driven Supervisor.

1. ARCHITECT — ANALISA & MODE:
   Proyek ini memiliki {N} domain: {DAFTAR_DOMAIN}.
   Tentukan Mode 1 (Scatter-Gather) atau Mode 2 (Reflection). Jelaskan pilihanmu.

2. ARCHITECT — FOUNDATION:
   - Buat CLAUDE.md di root proyek: stack ({TECH_STACK}), 4 pilar constraint,
     sandbox rule, escalation protocol, file ownership matrix.
   - Buat src/types/shared.ts: {DAFTAR_TYPE_INTI}.
   - Buat folder .agent-teams/mailbox/.

3. LAUNCHER — SPAWN WORKER:
   Launch: claude --dangerously-skip-permissions (dari root project dir).

4. SUPERVISOR — MONITOR BY SIGNAL:
   Cek .agent-teams/mailbox/ untuk ESCALATION.md dan *-DONE.md.
   Jika Mode 1: spawn Gather Agent di akhir (tsc + eslint + test).

5. ARCHITECT — DELIVER: Setelah clean, deliver ke user.

Fokus UI: {UI_REQUIREMENTS}.
Mulai dari langkah 1 sekarang.
```

### Step 3 — Lanjut ke Mode Selection

Setelah prompt ter-craft, Antigravity langsung masuk ke Mode Selection di bawah:

---

## 🔀 Mode Selection (WAJIB Ditanyakan Sebelum Spawn)

Saat skill ini aktif, **agent WAJIB menanyakan mode** ke user sebelum lanjut ke Execution Steps:

> "Saya deteksi task ini cocok untuk Agent Teams. Ada 2 mode yang tersedia:
>
> **Mode 1 — Scatter-Gather:** N agent coding paralel di domain yang benar-benar berbeda → 1 Gather Agent menyintesis semua output di akhir. Cocok untuk full-stack, multi-service, atau audit paralel.
>
> **Mode 2 — Reflection (Builder + Reviewer):** 1 agent coding, 1 agent testing/review secara real-time loop. Cocok untuk single-domain (frontend-only, backend-only) agar mismatch ~0%.
>
> Mau pakai mode mana? (Saya bisa sarankan berdasarkan kondisi project Anda)"

### Kapan Menyarankan Mode Mana?

| Kondisi | Saran | Keunggulan |
|---|---|---|
| Full-stack (FE + BE + DB) | **Mode 1** | Paralel murni, 2-3x lebih cepat, Gather Agent integrasikan hasil |
| Multi-microservice | **Mode 1** | Tiap service independen → zero mismatch by design |
| Audit paralel (security + perf) | **Mode 1** | Dua perspektif berbeda → report mandiri → Gather Agent gabungkan |
| A/B experiment (coba 2 solusi) | **Mode 1** | Race to green test → pemenang di-merge |
| Frontend-only / Backend-only | **Mode 2** | Shared dependency tinggi → Reviewer tangkap mismatch real-time |
| Refactor + validasi regresi | **Mode 2** | Builder fix → Reviewer cek tidak ada yang rusak → loop |
| Production readiness (audit dulu, fix kemudian) | **Mode 1 → Mode 2** | Fase 1: audit paralel, Fase 2: fix dengan validation loop |

---

## 🛠️ Mode 1 — Scatter-Gather: Langkah Eksekusi

> **Pattern:** N Scatter Agents bekerja paralel → 1 Gather Agent menyintesis semua output di akhir.
> **Cocok untuk:** Multi-domain orthogonal (FE+BE, multi-service, audit paralel, A/B experiment).

### Phase 1 — SCATTER (Paralel Execution)

1. **Validasi orthogonality.** Sebelum spawn, verifikasi bahwa setiap domain tidak memiliki shared source file. Jika ada file yang dikerjakan 2+ agent → pindahkan ke ownership Gather Agent. Threshold: jika >20% file overlap → gunakan Mode 2.
2. **Buat shared foundation dulu.** Team Lead define `src/types/shared.ts`, API contract, dan environment config SEBELUM spawn. Ini satu-satunya pre-work Scatter Agents butuhkan.
3. **Buat `CLAUDE.md`** yang memuat: stack proyek, arsitektur, **4 pilar constraint** (Rule 8), dan tabel File Ownership Matrix:
   ```
   | Agent       | Owns                  | Forbidden            |
   |-------------|-----------------------|----------------------|
   | Agent-FE    | src/components/, src/pages/ | src/api/, src/lib/ |
   | Agent-BE    | src/api/, src/lib/    | src/components/      |
   | Gather Agent| src/types/, package.json | (semua setelah merge)|
   ```
4. **Buat folder `.agent-teams/mailbox/`** di root proyek. Instruksikan tiap Scatter Agent: *"Baca mailbox sebelum mulai task baru. Tulis API contract ke mailbox sebelum coding interface yang akan dikonsumsi agent lain."*
5. **Spawn semua Scatter Agents sekaligus** dengan prompt template:
   > *"You are [ROLE]. You own [FOLDER_LIST]. FORBIDDEN from writing to [FORBIDDEN_LIST]. Before coding: read `.agent-teams/mailbox/`. Write interface contracts to `.agent-teams/mailbox/[you]-to-[partner].md` before implementing. Follow all constraints in CLAUDE.md. When done: write completion signal to `.agent-teams/mailbox/[you]-DONE.md` with summary of what you built."*
6. **Stuck threshold:** Anggap agent stuck jika error yang sama muncul 2x berturut-turut atau diam >3 menit. Intervensi langsung atau spawn ulang.

### Phase 2 — GATHER (Synthesis & Integration)

7. **Tunggu semua Scatter Agent tulis `*-DONE.md`** di mailbox sebelum spawn Gather Agent.
8. **Spawn 1 Gather Agent** dengan instruksi:
   > *"All scatter agents have completed. Your job: (1) Run `timeout -k 10s 60s npx tsc --noEmit` — fix any type errors found. (2) Run `timeout -k 10s 60s npx eslint src/` — fix violations. (3) Run `timeout -k 10s 60s npm test` — fix failing tests. (4) Resolve any file conflicts in git diff. (5) Write `gather-report.md` with: what was integrated, conflicts resolved, final test status."*
9. **Exit condition:** Gather Agent melaporkan `tsc` clean + `eslint` clean + all tests pass + `gather-report.md` tertulis → **Mode 1 selesai, siap merge.**

---

## 🛠️ Mode 2 — Asymmetric (Builder + Reviewer): Langkah Eksekusi

1. **Define shared foundation dulu** — Team Lead buat `src/types/shared.ts` dan `src/styles/tokens.ts` sebelum spawn. Ini satu-satunya pre-work yang wajib.
2. Buat `CLAUDE.md` yang memuat: aturan proyek, arsitektur, **4 pilar constraint**, dan **role assignment**:
   - **Builder:** owns semua `src/**/*.tsx`, `src/**/*.css`, `src/**/*.ts` (kecuali test files)
   - **Reviewer:** owns semua `src/**/*.test.tsx`, `src/**/*.spec.ts`, dan menjalankan type check + lint
3. Spawn 2 agent bersamaan:
   - **Agent-Builder:** Coding semua fitur. 100% ownership source code.
   - **Agent-Reviewer:** Menulis test, menjalankan `timeout -k 10s 60s npx tsc --noEmit`, `timeout -k 10s 60s npx eslint src/`, review konsistensi naming/visual.
4. **Loop paralel:** Builder coding → Reviewer menemukan bug/mismatch → Reviewer tulis temuan di `.agent-teams/mailbox/reviewer-to-builder.md` → Builder fix → Reviewer re-test.
5. **Exit condition:** Reviewer report `tsc` clean + `eslint` clean + all tests pass → Team Lead merge.

### File Ownership Mode 2

```
Agent-Builder  → src/**/*.tsx, src/**/*.css, src/**/*.ts (non-test)
Agent-Reviewer → src/**/*.test.tsx, src/**/*.spec.ts, __tests__/
Team Lead      → CLAUDE.md, package.json, tsconfig.json, src/types/shared.ts
```

### Contoh Penggunaan Mode 2

**Input (User):**
"Build dashboard admin dengan sidebar, cards, dan data table. Frontend only, pakai Agent Teams."

**Output (Agent Process):**
1. Agent mengevaluasi: Frontend-only → **sarankan Mode 2 (Asymmetric)**.
2. Agent tanya user: "Ini single-domain frontend, saya sarankan Mode 2 (Builder + Reviewer) agar mismatch ~0%. Setuju?"
3. User setuju → Agent define `src/types/shared.ts` + design tokens.
4. Agent spawn:
   - **Builder:** "Build Sidebar, DashboardCard, DataTable components di `src/components/`. Import types dari `src/types/shared.ts`. Follow CLAUDE.md constraints."
   - **Reviewer:** "Write tests for all components in `src/__tests__/`. Run `timeout -k 10s 60s npx tsc --noEmit` after each test batch. Report findings to `.agent-teams/mailbox/reviewer-to-builder.md`."
5. Loop sampai Reviewer report clean.

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

## 📌 Contoh Penggunaan Mode 1 (Input / Output Example)

**Input (User):**
"Buat aplikasi cuaca. Gunakan Agent Teams ya, satu urus UI/UX frontend, satu urus backend cuaca."

**Output (Antigravity sebagai Architect):**
1. Antigravity mengevaluasi: ✅ Full-stack → **sarankan Mode 1 (Scatter-Gather)**.
2. Antigravity tanya user: "Ini full-stack, saya sarankan Mode 1 (Scatter-Gather). Setuju?"
3. Antigravity memastikan `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.
4. Antigravity membuat `CLAUDE.md` berisi: stack, arsitektur, **4 pilar constraint**, **sandbox rule**, dan **ownership matrix**.
5. Antigravity menetapkan **File Ownership** di `CLAUDE.md`:
   - Teammate-UI owns: `src/components/`, `src/pages/`, `src/styles/`
   - Teammate-Backend owns: `src/api/`, `src/lib/`, `src/utils/`
   - Shared (`package.json`, `tsconfig.json`): Team Lead only
6. Antigravity membuat folder `.agent-teams/mailbox/`.
7. Antigravity launch worker via terminal:
   ```bash
   claude --dangerously-skip-permissions
   ```
8. Claude Code CLI membaca `CLAUDE.md`, spawn Agent Teams, dan mulai coding.
9. Antigravity memantau, intervensi jika stuck, dan spawn Gather Agent di akhir.

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
- [`sandbox-executor-setup`](file:///Users/gideonthirtytres/.agent/skills/skills/sandbox-executor-setup/SKILL.md) — Timeout guard wrapper untuk shell command otonom (Anti-Hanging Rule)
- [`multi-agent-orchestrator`](file:///Users/gideonthirtytres/.agent/skills/skills/multi-agent-orchestrator/SKILL.md) — Alternatif sekuensial (Architect → Worker → QA)
- [`ai-system-evaluator`](file:///Users/gideonthirtytres/.agent/skills/skills/ai-system-evaluator/SKILL.md) — Evaluasi post-execution kualitas tim
- [`headless-cli-wrapper`](file:///Users/gideonthirtytres/.agent/skills/skills/headless-cli-wrapper/SKILL.md) — Panduan headless spawning
- [**Decision Guide: Mode 1 vs Mode 2**](DECISION_GUIDE.md) — Panduan mendalam untuk arsitektur pemilihan mode
