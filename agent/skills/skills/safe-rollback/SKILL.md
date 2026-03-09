---
name: safe-rollback
description: Rollback perubahan file ke kondisi asli setelah sesi brainstorming atau eksekusi eksperimental.
  Invoked when user says "rollback", "revert", "batalkan perubahan", "kembalikan file",
  "undo changes", "reverse back", "balikin ke semula", "clean rollback",
  "clean up project", "hapus project", "delete project", "buang project ini".
  Destructive-safe file restoration using snapshot comparison.
  Includes Project Clean Up mode for full project directory removal with multi-gate confirmation.
category: Ops
---

# Safe Rollback — Post-Brainstorm File Restoration

## Kapan Digunakan

- User bilang "rollback", "revert", "batalkan", "kembalikan", "undo", "reverse back"
- Setelah sesi brainstorming/eksperimen di mana file dimodifikasi secara eksploratif
- Setelah eksekusi implementation plan yang dibatalkan sebelum selesai
- User ingin memastikan file kembali ke kondisi sebelum sesi dimulai
- User bilang "clean up project", "hapus project", "delete project" → aktifkan **Mode B: Project Clean Up**

## Confirmation Required

Skill ini MEMODIFIKASI file. Sebelum eksekusi rollback, SELALU tampilkan ringkasan
perubahan yang akan di-revert dan TUNGGU user mengatakan "ya" / "yes" / "lanjut".

## Steps

### Step 1 — Identifikasi File yang Dimodifikasi

Kumpulkan daftar file yang diubah selama sesi aktif menggunakan SALAH SATU metode
(pilih berdasarkan konteks, prioritas dari atas):

**Metode A — Git (jika repo):**
```bash
cd <project_dir> && git diff --name-only
```

**Metode B — Conversation History (jika bukan repo):**
Scan seluruh conversation history. Cari semua tool calls `replace_file_content`,
`multi_replace_file_content`, `write_to_file` yang berhasil. Ekstrak path file unik
dari setiap call.

**Metode C — User menyebutkan langsung:**
User menyebut file spesifik (misal: "rollback agent_sprint.sh"). Gunakan path itu.

Output Step 1: Daftar `MODIFIED_FILES[]` dengan path absolut.

### Step 2 — Capture Kondisi Saat Ini (Pre-Rollback Snapshot)

Untuk setiap file di `MODIFIED_FILES[]`:
1. Baca isi file saat ini menggunakan `view_file`
2. Catat jumlah baris (`Total Lines`) dan ukuran (`Total Bytes`)

Output Step 2: Tabel ringkasan kondisi saat ini.

### Step 3 — Tentukan Target Rollback

Tentukan versi target rollback menggunakan SALAH SATU sumber (prioritas dari atas):

**Sumber A — Git (jika repo):**
```bash
git show HEAD:<relative_path>
```
Ini mengembalikan isi file dari commit terakhir (sebelum perubahan uncommitted).

**Sumber B — Conversation History:**
Cari tool call `view_file` PERTAMA untuk file tersebut di conversation ini.
Konten yang ditampilkan itu adalah kondisi asli sebelum modifikasi.

**Sumber C — User menyediakan backup:**
User menyebutkan path file backup atau versi yang benar.

Output Step 3: Konten target rollback untuk setiap file.

### Step 4 — Tampilkan Rollback Plan (WAJIB)

Tampilkan ringkasan ke user dalam format:

```
🔄 ROLLBACK PLAN
════════════════════════════════════════
File: <path>
  Current : <line_count> lines, <byte_count> bytes
  Target  : <target_line_count> lines, <target_byte_count> bytes
  Source  : <Git HEAD / Conversation Step X / User backup>
────────────────────────────────────────
[Ulangi untuk setiap file]
════════════════════════════════════════
⚠️ Ketik "ya" untuk eksekusi rollback.
```

TUNGGU konfirmasi user. JANGAN lanjut tanpa konfirmasi eksplisit.

### Step 5 — Eksekusi Rollback

Untuk setiap file di `MODIFIED_FILES[]`:

**Jika menggunakan Git:**
```bash
git checkout HEAD -- <relative_path>
```

**Jika menggunakan Conversation History / manual:**
Gunakan tool `write_to_file` dengan `Overwrite: true` dan isi konten dari Step 3.

### Step 6 — Verifikasi & Laporan Akhir

Untuk SETIAP file, verifikasi via git diff (harus kosong) atau cocokan `Total Lines` dengan Step 3. Tampilkan:

```
✅ ROLLBACK COMPLETE
════════════════════════════════════════
File                     Status   Lines
─────────────────────────────────────────
<basename>               ✅ OK    <n>
<basename>               ❌ FAIL  <n>
════════════════════════════════════════
Total files reverted: <N> | Metode: <Git/Manual>
```

## Error Handling

- **File tidak ditemukan**: Skip, laporkan `⚠️ SKIPPED`
- **Git dirty / Staged changes**: Warning, tanya user mau stash dulu?
- **No history / Fresh session**: Minta path backup atau tolak
- **New File**: Tanya mau dihapus? (jangan auto-delete)
- **Partial Failure**: Lanjut file lain, list yang gagal di akhir

---

## Mode B: Project Clean Up — Full Project Removal

Sub-kemampuan untuk menghapus **seluruh folder project** yang dibuat dari nol dalam sesi
aktif. Dirancang untuk skenario di mana `create-next-app`, `create-vite`, scaffold, atau
tool serupa membuat project baru yang kemudian user ingin batalkan sepenuhnya.

### Kapan Aktif

- User mengatakan "clean up project", "hapus project", "delete project", "buang project ini"
- Project yang dimaksud **dibuat dari nol di sesi ini** (bukan project existing yang diedit)
- Folder project sebelumnya **tidak ada** sebelum sesi dimulai

### ⛔ LARANGAN MUTLAK

- DILARANG menghapus folder yang **sudah ada sebelum sesi dimulai**
- DILARANG menghapus folder di luar workspace user (misal: `/usr/`, `/etc/`, `$HOME` root)
- DILARANG menjalankan `rm -rf` tanpa melewati SEMUA gate konfirmasi di bawah

### Step B1 — Identifikasi Project Target

Scan conversation history untuk menemukan `run_command` yang berisi perintah scaffold
(misal: `npx create-next-app`, `npx create-vite`, `mkdir`, dll). Ekstrak:
- **Path absolut** folder project yang dibuat
- **Tool/command** yang membuat folder tersebut
- **Timestamp/Step** kapan folder dibuat

Output Step B1: `PROJECT_DIR` (path absolut), `CREATED_BY` (command), `STEP_ID`.

### Step B2 — Inventory Scan

Jalankan inventory untuk memberikan gambaran lengkap kepada user:
```bash
du -sh <PROJECT_DIR>                    # total ukuran
find <PROJECT_DIR> -type f | wc -l      # jumlah file
find <PROJECT_DIR> -type d | wc -l      # jumlah folder
ls -la <PROJECT_DIR>/                   # isi root-level
```

Periksa juga:
- Apakah ada **uncommitted work** yang mungkin berharga: `cd <PROJECT_DIR> && git status`
- Apakah ada file di **luar** `PROJECT_DIR` yang terkait (misal: artifact di `.gemini/brain/`)

Output Step B2: Ringkasan ukuran, jumlah file, dan status git.

### Step B3 — Tampilkan Impact Summary (WAJIB, Gate 1)

Tampilkan ke user:
```
🗑️ PROJECT CLEAN UP — IMPACT SUMMARY
════════════════════════════════════════════════
Project    : <project_name>
Path       : <PROJECT_DIR>
Created by : <CREATED_BY> (Step #<N>)
Size       : <size>
Files      : <file_count> files in <dir_count> directories
Git status : <clean / N uncommitted changes>
════════════════════════════════════════════════

⚠️  PERINGATAN: Aksi ini akan MENGHAPUS PERMANEN seluruh folder
     di atas beserta semua isinya. Tidak bisa di-undo.

📌 Related artifacts yang juga akan dibersihkan:
   - .gemini/brain/<session>/task.md
   - .gemini/brain/<session>/implementation_plan.md

════════════════════════════════════════════════
❓ Apakah Anda yakin ingin menghapus project ini?
   Ketik: "HAPUS <project_name>" untuk melanjutkan.
   Ketik apapun selain itu untuk membatalkan.
```

**TUNGGU respons user. JANGAN lanjut tanpa respons.**

### Step B4 — Verifikasi Konfirmasi (Gate 2)

User HARUS mengetik PERSIS: `HAPUS <project_name>` (case-sensitive pada nama project).

Jika user mengetik:
- ✅ `HAPUS <project_name>` → lanjut ke Step B5
- ❌ Teks lain apapun ("ya", "yes", "ok", "hapus", typo) → **BATALKAN**, tampilkan:
  ```
  ✖ Clean up dibatalkan. Project tidak dihapus.
  ```

### Step B5 — Eksekusi Clean Up

Jalankan penghapusan:
```bash
rm -rf <PROJECT_DIR>
```

Jika ada related artifacts (task.md, implementation_plan.md di `.gemini/brain/<session>/`):
- Tanyakan: "Mau hapus juga artifact sesi ini (task.md, implementation_plan.md)? (ya/tidak)"
- Jika ya → hapus artifact files
- Jika tidak → biarkan

### Step B6 — Verifikasi & Laporan Akhir

Verifikasi folder sudah tidak ada:
```bash
ls <PROJECT_DIR> 2>&1  # harus error "No such file or directory"
```

Tampilkan:
```
✅ PROJECT CLEAN UP COMPLETE
════════════════════════════════════════════════
Project    : <project_name>
Path       : <PROJECT_DIR> — DELETED
Files      : <file_count> files removed
Artifacts  : <cleaned / retained>
════════════════════════════════════════════════
Workspace kembali ke kondisi sebelum sesi ini.
```

### Error Handling (Mode B)

- **Folder tidak ditemukan**: Laporkan `⚠️ Folder sudah tidak ada, skip`
- **Permission denied**: Laporkan error, jangan retry
- **Folder bukan milik sesi ini**: TOLAK, tampilkan warning bahwa hanya project yang dibuat di sesi aktif yang boleh dihapus
- **User salah ketik konfirmasi**: Batalkan secara otomatis, tampilkan pesan pembatalan

---

## Examples

### Example 1 — File Rollback (Mode A)

**Input:** "rollback agent_sprint.sh"

**Output:**
```
🔄 ROLLBACK PLAN
File: agent_sprint.sh | Source: Conversation Step #37 (view_file)
Current: 201 lines -> Target: 151 lines
⚠️ Ketik "ya" untuk eksekusi rollback.
```

User: "ya" -> Eksekusi -> Tampilkan `✅ ROLLBACK COMPLETE` tabel.

### Example 2 — Project Clean Up (Mode B)

**Input:** "clean up project skillforge-marketplace"

**Output:**
```
🗑️ PROJECT CLEAN UP — IMPACT SUMMARY
════════════════════════════════════════════════
Project    : skillforge-marketplace
Path       : /Users/user/Projects/skillforge-marketplace
Created by : npx create-next-app (Step #44)
Size       : 187MB
Files      : 384 files in 52 directories
Git status : 20 uncommitted changes
════════════════════════════════════════════════

⚠️  PERINGATAN: Aksi ini akan MENGHAPUS PERMANEN seluruh folder
     di atas beserta semua isinya. Tidak bisa di-undo.
════════════════════════════════════════════════
❓ Ketik: "HAPUS skillforge-marketplace" untuk melanjutkan.
```

User: "HAPUS skillforge-marketplace" -> Eksekusi -> Tampilkan `✅ PROJECT CLEAN UP COMPLETE`.
User: "ya" -> ✖ Dibatalkan (harus ketik PERSIS "HAPUS nama_project").

