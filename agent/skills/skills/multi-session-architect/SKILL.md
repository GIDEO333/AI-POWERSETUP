---
name: multi-session-architect
description: Metodologi perencanaan proyek kompleks — pecah ke N sesi independen dengan trade-off analysis, model recommendation per sesi, architecture reference file, synergy analysis, dan ready-to-paste prompts / Plan complex projects by splitting into N independent sessions with trade-off analysis, per-session model recommendations, architecture references, and copy-paste prompts
category: AI-Orchestration
---

# 🏗️ Multi-Session Architect Skill

## Deskripsi / Description

Skill ini mendefinisikan metodologi **bagaimana Antigravity merencanakan proyek kompleks** yang terlalu besar untuk satu sesi. Alih-alih langsung coding, Antigravity bertindak sebagai **Project Architect** — menganalisa opsi, memecah pekerjaan, dan menyiapkan semua yang dibutuhkan agar setiap new session bisa langsung produktif tanpa kehilangan konteks.

*This skill defines the methodology for planning complex projects too large for a single session. Instead of jumping into code, Antigravity acts as a Project Architect — analyzing options, splitting work, and preparing everything so each new session is immediately productive without context loss.*

## 🎯 Kapan Skill Ini Aktif (Trigger Conditions)

Aktifkan skill ini ketika **salah satu** kondisi berikut terpenuhi:

- Proyek membutuhkan **> 3 file source code baru**
- Estimasi token: satu sesi **tidak cukup** untuk keseluruhan pekerjaan
- Proyek melibatkan **multi-domain** (frontend + backend + infrastructure)
- User meminta pembuatan **MCP server, CLI tool, atau library**
- User meminta sesuatu yang punya **lebih dari 1 pendekatan arsitektur**

## 📋 Metodologi (6 Phase)

### Phase 1 — Landscape Research 🔍

Sebelum membuat rencana, Antigravity **WAJIB riset dulu**:

1. **Web search** untuk solusi existing (jangan re-invent the wheel)
2. **Validasi** setiap temuan — jangan percaya mentah-mentah
3. **Map feature list** dari yang dibutuhkan user
4. **Identifikasi** library/SDK/tool yang sudah ada

> ⚠️ Tiap informasi dari web search HARUS divalidasi dengan minimal 2 sumber atau 1 sumber resmi (dokumentasi, GitHub repo, blog official).

**Output Phase 1:** Ringkasan temuan riset tervalidasi.

---

### Phase 2 — Trade-Off Analysis ⚖️

Antigravity **WAJIB menyajikan minimal 2 opsi arsitektur** (idealnya 3) kepada user. **DILARANG** langsung memilih satu pendekatan tanpa menunjukkan alternatif.

**Format wajib:**

```
| Kriteria        | Option A         | Option B         | Option C         |
|-----------------|:----------------:|:----------------:|:----------------:|
| Nama            | [nama deskriptif]| [nama deskriptif]| [nama deskriptif]|
| Fitur X         | ✅ / ❌ / ⚠️      | ✅ / ❌ / ⚠️      | ✅ / ❌ / ⚠️      |
| Build Time      | [estimasi]       | [estimasi]       | [estimasi]       |
| Complexity      | Low / Med / High | Low / Med / High | Low / Med / High |
| Rekomendasi     | [kapan cocok]    | ⭐ [jika ini best]| [kapan cocok]   |
```

**Aturan Trade-Off:**
1. Setiap opsi harus punya **nama yang deskriptif** (bukan "Option A/B/C")
2. Berikan **analisa pro/kontra** per opsi (minimal 2 pro, 2 kontra)
3. Berikan **rekomendasi** dengan alasan, tapi **biarkan user memilih**
4. Jelaskan **upgrade path** jika ada (misal: mulai dengan B, upgrade ke C nanti)

**Output Phase 2:** Tabel perbandingan + rekomendasi + user memilih.

---

### Phase 3 — Synergy Analysis 🔗

Setelah arsitektur dipilih, Antigravity **analisa sinergi** dengan ekosistem existing:

1. **Baca skill terkait** di `/agent/skills/skills/` yang mungkin terintegrasi
2. **Map setiap section/fitur** skill existing → fitur proyek baru
3. **Identifikasi GAP** — apa yang skill existing bilang tapi tidak bisa dilakukan tanpa proyek baru
4. **Tulis design recommendations** spesifik berdasarkan GAP analysis

**Format GAP Analysis:**

```
### GAP [N]: [Nama Gap]

**Skill X bilang (baris Y):** [kutipan]
**Realita sekarang:** [apa yang terjadi]
**Proyek baru menyelesaikan ini:** [bagaimana]
> Sinergi: [KRITIS ⭐⭐⭐⭐⭐ / TINGGI ⭐⭐⭐⭐ / SEDANG ⭐⭐⭐]
```

**Output Phase 3:** Synergy analysis document.

---

### Phase 4 — Session Splitting 📐

Pecah implementasi menjadi **N sesi independen** (idealnya 2-4 sesi). Setiap sesi harus:

**Aturan Splitting:**
1. **Self-contained:** Setiap sesi harus bisa berjalan di new session tanpa konteks sesi sebelumnya, KECUALI file-file yang sudah di-generate
2. **Testable:** Setiap sesi harus punya deliverable yang bisa diverifikasi
3. **Incremental:** Sesi N+1 harus build di atas deliverable sesi N
4. **Max 45 menit:** Jangan lebih dari 45 menit estimasi per sesi (jaga context window)
5. **Session Terakhir = Integration & Test:** WAJIB selalu ada sesi akhir khusus untuk validasi lintas sesi. Jangan gabungkan dengan sesi coding.

**Format Session Card:**

```
## Session [N]: [Nama] (~[estimasi] menit)

**Prerequisite:** [Session N-1 selesai / None]
**Goal:** [1 kalimat tujuan]
**Deliverables:**
- [file/komponen 1]
- [file/komponen 2]
**Verification:** [cara cek sesi ini berhasil]
```

### 🧪 Session Terakhir WAJIB: Integration & Test (~20-30 menit)

Sesi ini selalu hadir di akhir, setelah semua sesi coding selesai. Formatnya mengikuti **Test Pyramid 3 Layer**:

```
Layer 3: E2E Test — sistem dipakai dari entry point nyata (IDE, terminal, API)
          ↑
Layer 2: Integration Test — setiap komponen dipanggil, return response valid
          ↑
Layer 1: Build Integrity — compile clean, imports resolved, server/app start
```

**Format Integration Session Card:**

```
## Session [N] (TERAKHIR): Integration & Test (~25 menit)

**Prerequisite:** Semua sesi coding selesai.
**Goal:** Validasi bahwa semua komponen dari sesi 1-N terhubung dan bekerja end-to-end.

**Layer 1 — Build Integrity:**
- [command: npx tsc --noEmit / mvn compile / go build]
- [command: list output directory untuk konfirmasi semua file ada]
- [command: start server/app — pastikan tidak crash]

**Layer 2 — Integration Test (per komponen):**
- Test [komponen 1]: [perintah / input / expected output]
- Test [komponen 2]: [perintah / input / expected output]
- ...

**Layer 3 — E2E Test:**
- [cara pakai dari entry point nyata — IDE, curl, browser, CLI]
- [expected behavior]

**✅ Definition of Done:**
- Layer 1: exit code 0
- Layer 2: semua tool/API return response valid
- Layer 3: fitur utama berjalan dari sisi user
```

**Output Phase 4:** Session cards + Integration & Test session card.

---

### Phase 5 — Model Recommendation per Session 🤖

Antigravity **WAJIB merekomendasikan model LLM terbaik** untuk setiap sesi berdasarkan tipe pekerjaan:

**Panduan Pemilihan Model:**

| Tipe Pekerjaan | Model Terbaik | Alasan |
|---|---|---|
| Scaffolding, boilerplate, config | **Gemini 3.1 Pro** | Cepat, murah, straightforward |
| Complex logic, TypeScript strict | **Claude Sonnet 4.6** | Presisi tinggi, jarang buat placeholder |
| Security-critical code | **Claude Opus 4.6** | Paling teliti untuk edge cases |
| Rapid prototyping | **Gemini 3 Flash** | Paling cepat, biaya terendah |
| Multi-file refactoring | **Claude Sonnet 4.6** | Paling disiplin soal file boundaries |
| UI/Frontend generation | **Gemini 3.1 Pro** | Kuat di frontend + CSS |
| **Integration & Test** | **Gemini 3.1 Pro** | Menulis test commands, membaca output, debug — tidak butuh model mahal |

**Format Rekomendasi:**

```
| Session | Model | Alasan |
|---------|-------|--------|
| Session 1 | Gemini 3.1 Pro | [alasan spesifik] |
| Session 2 | Claude Sonnet 4.6 | [alasan spesifik] |
| Session N (Integration & Test) | Gemini 3.1 Pro | Eksekusi test, baca output, fix ringan |
```

> 💡 **Aturan:** Ini REKOMENDASI, bukan keharusan. User bebas pakai model apapun.

**Output Phase 5:** Tabel model recommendation.

---

### Phase 6 — Prompt Engineering + Reference Files 📝

Untuk setiap sesi, Antigravity harus menyiapkan **2 hal**:

#### A. Architecture Reference File

Buat **1 file `architecture_plan.md`** di root proyek yang menjadi **single source of truth**. File ini:
- Di-`@mention` oleh setiap prompt sesi
- Berisi: tech stack, file structure, interfaces, tool specifications
- Model-agnostic (bisa dibaca oleh model LLM apapun)
- Immutable selama build (tidak berubah antar sesi)

#### B. Per-Session Prompt

Format wajib untuk setiap prompt:

```
[Konteks proyek — 1-2 kalimat]

Baca file referensi ini dulu:
1. @[path/to/architecture_plan.md]
2. @[path/to/related-skill/SKILL.md] (jika ada)
3. @[path/to/src/existing-files] (jika session 2+)

INI ADALAH SESSION [N] dari [TOTAL]. Fokus session ini:

1. [Instruksi spesifik langkah 1]
2. [Instruksi spesifik langkah 2]
...

Pastikan semua code LENGKAP, TIDAK ADA placeholder // TODO.
Jalankan [verification command] untuk verifikasi.
```

**Aturan Prompt:**
1. Setiap prompt HARUS `@mention` file `architecture_plan.md`
2. Session 2+ HARUS `@mention` file yang sudah dibuat di sesi sebelumnya
3. Sertakan nomor sesi: "INI ADALAH SESSION N dari TOTAL"
4. Akhiri dengan instruksi verifikasi eksplisit (`npx tsc`, `npm test`, dll)
5. Tambahkan reminder: "TIDAK ADA placeholder // TODO"

**Output Phase 6:** 
1. File `architecture_plan.md` di root proyek
2. File `session_prompts.md` di Downloads (kumpulan semua prompt + prompt Integration & Test)

#### C. Integration & Test Prompt Template

Prompt sesi terakhir ini mempunyai format khusus:

```
Semua sesi coding [nama proyek] sudah selesai.

Baca file referensi:
1. @[path/to/architecture_plan.md]
2. @[path/to/src/] (semua source file yang sudah dibuat)
3. @[path/to/walkthrough.md] (jika ada)

INI ADALAH SESSION TERAKHIR: Integration & Test.

**Layer 1 — Build Integrity:**
1. Jalankan [compile command] — harus exit code 0
2. List [output directory] — pastikan semua file ada
3. Start [server/app] — pastikan tidak crash

**Layer 2 — Integration Test:**
4. Test [tool/komponen 1]: [perintah eksplisit]
5. Test [tool/komponen 2]: [perintah eksplisit]
...

**Layer 3 — E2E Test:**
[N+1]. [Test dari entry point nyata]

Jika ada yang gagal: identifikasi penyebab, fix, re-test.
Jika semua pass: buat file integration_report.md berisi hasil test.
```

---

## 📦 Deliverables Akhir (Checklist)

Setelah Phase 6 selesai, file-file berikut HARUS sudah tersedia:

- [ ] `~/Projects/[nama-proyek]/architecture_plan.md` — blueprint teknis
- [ ] `~/Downloads/[nama-proyek]_session_prompts.md` — semua prompt termasuk Integration & Test
- [ ] Synergy analysis artifact (di conversation artifacts)
- [ ] Trade-off comparison (di conversation atau artifact)

## 📌 Contoh Penggunaan (Input / Output Example)

**Input (User):**
"Saya mau buat MCP server supaya Antigravity bisa pakai Claude Code CLI."

**Output (Antigravity sebagai Multi-Session Architect):**
1. Phase 1: Riset → temukan `steipete/claude-code-mcp`, `claude mcp serve`, Claude Agent SDK
2. Phase 2: Trade-off → sajikan 3 opsi (Fork, Bridge, Hybrid) → user pilih Bridge
3. Phase 3: Synergy → map SKILL.md claude-agent-teams → temukan 5 GAP
4. Phase 4: Split → Session 1 (Foundation), Session 2 (Core Tools), Session 3 (Deploy), **Session 4 (Integration & Test)**
5. Phase 5: Model → Gemini scaffolding, Claude complex logic, **Gemini lagi untuk Integration Test**
6. Phase 6: Prompt → buat `architecture_plan.md` + `session_prompts.md` (4 prompts)

User buka Session 1 → Session 2 → Session 3 → **Session 4 validasi semua terhubung** → ✅ done.

## 🔗 Skill Terkait (Related Skills)

- [`claude-agent-teams`](../claude-agent-teams/SKILL.md) — Untuk proyek yang butuh Agent Teams spawning
- [`create-project`](../create-project/SKILL.md) — Untuk inisialisasi proyek sederhana (1 sesi)
- [`deep-research`](../deep-research/SKILL.md) — Untuk Phase 1 (Landscape Research)
- [`workflow-guide`](../workflow-guide/SKILL.md) — Panduan workflow umum
- [`token-budget`](../token-budget/SKILL.md) — Estimasi token per sesi
