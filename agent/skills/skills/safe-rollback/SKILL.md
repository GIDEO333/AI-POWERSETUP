---
name: safe-rollback
description: Rollback perubahan file ke kondisi asli setelah sesi brainstorming atau eksekusi eksperimental.
  Invoked when user says "rollback", "revert", "batalkan perubahan", "kembalikan file",
  "undo changes", "reverse back", "balikin ke semula", "clean rollback".
  Destructive-safe file restoration using snapshot comparison.
category: Ops
---

# Safe Rollback — Post-Brainstorm File Restoration

## Kapan Digunakan

- User bilang "rollback", "revert", "batalkan", "kembalikan", "undo", "reverse back"
- Setelah sesi brainstorming/eksperimen di mana file dimodifikasi secara eksploratif
- Setelah eksekusi implementation plan yang dibatalkan sebelum selesai
- User ingin memastikan file kembali ke kondisi sebelum sesi dimulai

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

## Examples

**Input:** "rollback agent_sprint.sh"

**Output:**
```
🔄 ROLLBACK PLAN
File: agent_sprint.sh | Source: Conversation Step #37 (view_file)
Current: 201 lines -> Target: 151 lines
⚠️ Ketik "ya" untuk eksekusi rollback.
```

User: "ya" -> Eksekusi -> Tampilkan `✅ ROLLBACK COMPLETE` tabel.

