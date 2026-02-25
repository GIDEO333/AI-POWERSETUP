---
name: forge-to-claude
description: Convert existing FORGE skills to Claude Code optimized versions without modifying originals.
  Invoked when user says "convert skill to claude code", "optimize skill for claude", 
  "buat versi claude code dari skill", "konversi skill ke claude code", "claude code version",
  "jadikan skill ini claude code compatible", "export skill for claude".
  Creates a NEW file alongside the original — never overwrites the FORGE SKILL.md.
---

# FORGE → Claude Code Skill Converter

## Kapan Digunakan

- User ingin memakai skill di Claude Code tanpa merusak versi Antigravity
- User ingin mengaktifkan fitur eksklusif Claude Code (subagent, hooks, invocation control)
- User mau export/deploy skill ke project yang menggunakan Claude Code sebagai IDE

## Prinsip Utama (NON-NEGOTIABLE)

1. **NEVER overwrite** file `SKILL.md` original — itu adalah source of truth untuk Antigravity
2. Output selalu ke file BARU bernama `SKILL.claude.md` di folder skill yang sama
3. Jika `SKILL.claude.md` sudah ada, **tanya user dulu** sebelum overwrite
4. Semua FORGE content (instructions, examples, error handling) dipertahankan 100%
5. Claude Code additions adalah **additive only** — tidak ada yang dihapus dari konten asli

## Process (Ikuti Urutan)

### Step 1 — Identifikasi Target

Tanya user: "Skill mana yang ingin dikonversi?"
Opsi input yang diterima:
- Nama skill: `debug-code`, `project-audit`, dll.
- Path lengkap: `~/.agent/skills/skills/debug-code/SKILL.md`
- Keyword: cari skill via `search_skills` MCP tool
- "semua" → batch mode, konversi semua skills sekaligus

### Step 2 — Baca SKILL.md Original

Baca file `SKILL.md` dari `~/.agent/skills/skills/{nama}/SKILL.md`.
Ekstrak:
- `name` dan `description` dari YAML frontmatter
- Seluruh body content (sections, steps, examples, error handling)
- Estimasi panjang body (baris)

### Step 3 — Analisis & Tentukan Claude Code Enhancements

Evaluasi skill berdasarkan karakteristiknya dan tentukan nilai tiap field:

**`disable-model-invocation`** — mencegah Claude auto-trigger tanpa user minta:
- Skill dengan side effects (deploy, push, delete, send) → `disable-model-invocation: true`
- Skill analitik/background knowledge (audit, token-budget) → TIDAK perlu (omit)
- Default jika ragu: omit (biarkan Claude bisa trigger otomatis)

**`user-invocable`** — mengontrol apakah skill bisa dipanggil sebagai slash command oleh user:
- Background knowledge skill (normalize-input, konteks legacy) → `user-invocable: false`
- Skill yang memang untuk user pakai → TIDAK perlu (default true)

**`context: fork`** — jalankan skill di subagent terpisah (isolasi context window):
- Skill body > 50 baris atau melibatkan banyak file reading → `context: fork`
- Skill ringan dan cepat → TIDAK perlu (omit)

**`agent`** — tipe subagent jika `context: fork` aktif:
- Skill yang perlu cari-cari file, grep, explore → `agent: Explore`
- Skill yang perlu plan kompleks → `agent: Plan`
- Default jika `context: fork` tanpa agent spesifik → omit (general-purpose)

**`allowed-tools`** — batasi tools yang bisa dipakai skill:
- Skill read-only (audit, review) → `allowed-tools: Read, Grep, Glob`
- Skill yang perlu jalankan command → `allowed-tools: Bash, Read`
- Skill tanpa batasan → omit

**`hooks`** — event triggers otomatis (HANYA tambahkan jika ada use case jelas):

Syntax yang BENAR untuk hooks di SKILL.md:
```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
  Stop:
    - matcher: ""
      hooks:
        - type: command
          command: "./scripts/notify.sh"
```

Hook events yang tersedia: `SessionStart`, `UserPromptSubmit`, `PreToolUse`,
`PostToolUse`, `Stop`, `SubagentStart`, `SubagentStop`, `TaskCompleted`

Skill yang cocok diberi hooks:
- `git-workflow` → `PostToolUse` matcher "Bash(git commit*)" untuk validasi
- `code-review` → `PreToolUse` matcher "Bash(git push*)" untuk force review dulu
- Skill lain → TIDAK perlu hooks kecuali ada use case sangat jelas

**`$ARGUMENTS` dan Dynamic Context** — fitur eksklusif Claude Code:
- Jika skill original tidak punya parameter → tambahkan `$ARGUMENTS` di instruksi bila relevan
- Dynamic context injection: prefix `!` sebelum bash command di body skill untuk pre-execute:
  ```
  - Current git status: !`git status`
  - Staged changes: !`git diff --staged`
  ```

### Step 4 — Generate SKILL.claude.md

Struktur output yang BENAR:

```markdown
---
name: {nama-sama-dengan-original}
description: {description-sama-dengan-original}
disable-model-invocation: true   # HANYA jika skill punya side effects
user-invocable: false            # HANYA jika background-only skill
context: fork                    # HANYA jika body berat/panjang
agent: Explore                   # HANYA jika context: fork dan perlu exploration
allowed-tools: Read, Grep        # HANYA jika perlu pembatasan tools
hooks:                           # HANYA jika ada use case hooks yang jelas
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/check.sh"
---

{seluruh body SKILL.md original — copy 100% tanpa modifikasi}

{tambahkan $ARGUMENTS dan/atau dynamic context !`command` jika relevan}

---
> *Auto-generated by forge-to-claude converter.*
> *Original FORGE skill: ~/.agent/skills/skills/{nama}/SKILL.md — UNTOUCHED*
> *Enhancements: {list apa yang ditambahkan}*
> *Regenerate: invoke "buat versi claude code dari {nama}"*
```

**PENTING:** Hanya include keys yang memang dibutuhkan. Jangan include key dengan nilai default kosong.

### Step 5 — Cek Konflik

Sebelum menulis:
```
Jika SKILL.claude.md sudah ada:
  → Tampilkan diff ringkas (keys yang akan berubah)
  → Tanya: "SKILL.claude.md sudah ada. Overwrite? (y/n)"
  → Tunggu konfirmasi user
Jika belum ada:
  → Langsung tulis
```

### Step 6 — Tulis File & Tampilkan Deploy Instructions

Tulis ke `~/.agent/skills/skills/{nama}/SKILL.claude.md`.

Lalu tampilkan instruksi deploy opsional:
```bash
# Untuk pakai di Claude Code project (jalankan manual jika diperlukan):
mkdir -p .claude/skills/{nama}
cp ~/.agent/skills/skills/{nama}/SKILL.claude.md .claude/skills/{nama}/SKILL.md
```
Catatan: agent TIDAK auto-copy ke `.claude/` kecuali user minta eksplisit.

### Step 7 — Report Per Skill

## Output Format

```
✅ Converted: {nama-skill}
📄 FORGE original: ~/.agent/skills/skills/{nama}/SKILL.md  ← UNTOUCHED
📄 Claude version: ~/.agent/skills/skills/{nama}/SKILL.claude.md  ← CREATED

Enhancements added:
  • disable-model-invocation: {true / not added}
  • user-invocable: {false / not added}
  • context: {fork / not added}
  • agent: {Explore/Plan / not added}
  • allowed-tools: {list / not added}
  • hooks: {events / none}
  • $ARGUMENTS: {yes / no}
  • Dynamic context (!): {yes / no}

Deploy to Claude Code project:
  cp ~/.agent/skills/skills/{nama}/SKILL.claude.md .claude/skills/{nama}/SKILL.md
```

## Batch Mode

Jika user minta "konversi semua":
1. List semua folder di `~/.agent/skills/skills/`
2. Tanya sekali: "Ada yang sudah punya SKILL.claude.md: [list]. Skip atau overwrite semua?"
3. Konversi satu per satu
4. Summary table:

```
BATCH CONVERSION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Skill              Key Enhancements               Status
─────────────────  ──────────────────────────     ──────
debug-code         context:fork, Explore           ✅ NEW
project-audit      context:fork, Read+Grep+Glob    ✅ NEW
normalize-input    user-invocable:false            ✅ NEW
git-workflow       PostToolUse hook                ✅ NEW
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: {N} converted. All FORGE originals: UNTOUCHED.
```

## Error Handling

- **Skill tidak ditemukan**: Cari via `search_skills`, tampilkan top-3 kandidat, minta konfirmasi
- **YAML frontmatter rusak**: Skip skill, laporkan di summary, lanjut ke berikutnya
- **Skill body > 150 baris**: Tetap konversi, tambahkan note di footer bahwa skill sebaiknya dipecah jadi 2 untuk efisiensi context di Claude Code
- **User bilang "semua" + ada conflict**: Tanya sekali untuk semua (skip/overwrite), jangan tanya per skill
