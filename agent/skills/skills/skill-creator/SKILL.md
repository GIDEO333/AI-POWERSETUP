---
name: skill-creator
description: Generate a new Agent Skill SKILL.md following the FORGE quality standard.
  Invoked when user says "buat skill baru", "tambah skill", "bikin skill untuk",
  "buat skill yang bisa", "create new skill", "generate skill", "I need a skill that",
  "tambah kemampuan agent", "buat SOP otomatis", "new skill", "saya mau buat skill".
  Outputs cross-compatible SKILL.md valid for Antigravity and Claude Code.
---

# Skill Creator — FORGE Quality Standard Generator

## Kapan Digunakan

- User minta membuat skill baru untuk task yang berulang
- User ingin mengotomatiskan SOP atau workflow tertentu
- User bilang "buat skill", "tambah skill untuk X", "bikin skill"
- Dipanggil oleh workflow `/new-skill` untuk mengisi konten SKILL.md

## Aturan NON-NEGOTIABLE (Cross-Platform Compatibility)

1. YAML frontmatter HANYA boleh punya 2 key: `name` dan `description`
2. FORBIDDEN keys: `context`, `user-invocable`, `claude-invocable`, `subagent`, `fork`
3. `name`: lowercase, hyphen-separated, max 64 karakter
4. `description`: bilingual trigger (ID + EN keywords) — ini yang dibaca semantic router
5. Semua instruksi POSITIF: tulis "Lakukan X di file Y", BUKAN "Jangan ubah Z"
6. Panjang SKILL.md maksimal 150 baris — kalau lebih, pecah jadi 2 skill atomic

## Process (Ikuti Urutan)

### Step 1 — Tanya User (1 pertanyaan saja)

Tanyakan:
> "Deskripsikan tugas yang ingin diautomatisasi. Berikan 1 contoh konkret: input apa yang kamu berikan, output apa yang kamu harapkan?"

Tunggu jawaban sebelum lanjut.

### Step 2 — Classify Skill

Dari jawaban user, tentukan:

**Kategori:**
- DevOps / Trading / Code / Writing / Data / Analysis / Other

**Pola Template** (pilih 1):
- **Pola A — Procedural/SOP**: Tugas linear dengan langkah berurutan (debug, deploy, commit)
- **Pola B — Reference/Cheatsheet**: Lookup cepat, tabel command, checklist (review, commands)
- **Pola C — Contextual Analysis**: Analisis kondisi + output terstruktur (audit, budget, normalize)

**Freedom Level:**
- HIGH: kreatif/analisis → instruksi plain English, biarkan model eksekusi
- MEDIUM: code review/refactor → pseudocode atau parameter
- LOW: destructive ops (delete, deploy, drop DB) → exact command + verification step wajib

### Step 3 — Draft Frontmatter

Tulis `name` dan `description` dulu. Verifikasi:
- [ ] `name` lowercase-hyphen, max 64 char?
- [ ] `description` mengandung keyword ID + EN trigger?
- [ ] Tidak ada forbidden YAML keys?

Template description yang baik:
```
description: [Apa yang dilakukan skill ini dalam 1 kalimat]. 
  Invoked when user says "[trigger EN]", "[trigger ID]", atau "[variasi]".
  [2-3 keyword domain spesifik].
```

### Step 4 — Generate Body SKILL.md

Susun sesuai pola yang dipilih di Step 2:

**Pola A — Procedural:**
```markdown
## Steps
1. Langkah pertama (konkret, bukan abstrak)
2. Langkah kedua
...

## Common Patterns  (opsional)
- Kondisi X → lakukan Y
- Kondisi Z → lakukan W

## Proactive Behavior  (opsional)
- Tanpa diminta, selalu lakukan...
```

**Pola B — Reference:**
```markdown
## [Nama Kategori Utama]
| Task | Command/Action |
|------|---------------|
| ... | ... |

## Checklist  (jika relevan)
- [ ] Item A
- [ ] Item B

## Output Format
- Format output yang diharapkan
```

**Pola C — Contextual Analysis:**
```markdown
## Kapan Digunakan
- Kondisi A → trigger skill ini
- Kondisi B → trigger skill ini

## Steps
### Step 1 — [Nama]
[Detail + code block jika perlu]

### Step 2 — [Nama]
...

## Output Format  (WAJIB untuk pola ini)
Output harus berisi:
1. Item A
2. Item B

## Examples  (minimal 1)
Input: "..."
Output: "..."
```

### Step 5 — Self-Review Checklist

Sebelum output final, verifikasi SEMUA:

**Compatibility ✅**
- [ ] YAML hanya `name` dan `description`
- [ ] Tidak ada forbidden keys
- [ ] Panjang ≤ 150 baris
- [ ] Semua instruksi positif (bukan larangan)

**Kualitas ✅**
- [ ] Description ada keyword ID + EN
- [ ] Ada minimal 1 contoh input/output
- [ ] Ada section Error Handling (minimal 2 kasus)
- [ ] Freedom level sesuai risiko task

### Step 6 — Output + Lanjutkan ke /new-skill

Tampilkan SKILL.md lengkap, lalu langsung eksekusi:

```bash
# 1. Buat direktori
mkdir -p ~/.agent/skills/skills/{nama-skill}

# 2. Tulis SKILL.md (sudah di-generate di step sebelumnya)

# 3. Rebuild index (via workflow /new-skill step 3)
cd ~/Projects/AI-POWERSETUP && python3 agent/scripts/build-skills-index.py

# 4. Verify
python3 -c "import json; d=json.load(open('agent/skills/skills-index.json')); print(f'✅ {len(d)} skills indexed')"
```

## Error Handling

- **User request terlalu vague**: Tanya 1 contoh konkret (input → output), jangan generate dulu
- **Skill > 150 baris**: Pecah jadi 2 skill atomic, beri nama `{nama}-part1` dan `{nama}-part2`
- **Nama skill sudah ada**: Tanya user: "Skill `{nama}` sudah ada. Update atau buat baru dengan nama lain?"
- **Index rebuild gagal**: Cek path `~/Projects/AI-POWERSETUP` ada, lalu coba `python3 ~/.agent/scripts/build-skills-index.py`
- **Task butuh destructive action**: Tambah `## Confirmation Required` sebagai step pertama di SKILL.md yang dibuat

## Output Format (Laporan Akhir)

```
✅ Skill berhasil dibuat
📁 Path: ~/.agent/skills/skills/{nama-skill}/SKILL.md
🎯 Pola: [A/B/C] — [Procedural/Reference/Contextual Analysis]
🔍 Trigger keywords: [daftar kata yang akan memicu skill ini]
📊 Total skills aktif: [N] skills
```
