---
name: brainstorm-refiner
description: Process raw AI-generated brainstorming or tutorials (e.g., from Perplexity/ChatGPT), identify technical hallucinations, and verify syntax/architecture using primary sources.
  Invoked when user says "verifikasi draft ini", "olah hasil perplexity", 
  "cek halusinasi", "refine brainstorming", "verify ai output", 
  "filter fakta dari dump", "buat spek dari draft AI", "validasi tutorial ini".
category: Format
---

# Brainstorm Refiner & Fact Checker

## Kapan Digunakan

- User melakukan copy-paste panjang (dump) dari hasil obrolan dengan AI lain (ChatGPT/Claude/Perplexity).
- User membawa ide arsitektur/kode yang belum diverifikasi.
- User butuh draft/ide kasar diubah menjadi *Technical Specification* atau *Action Plan* yang 100% valid secara sintaks dan sesuai dengan kondisi project (AI-POWERSETUP / Quant stack) saat ini.

## Prinsip Utama

1. **Skeptisisme Default:** Anggap semua *exact syntax*, nama library, dan *code snippet* dari input user berpotensi halusinasi atau *outdated*.
2. **Verifikasi Primer:** HANYA percaya pada dokumentasi resmi terbaru atau source code aktual yang ada di *workspace* user.
3. **Pemisahan Konsep vs Implementasi:** Ambil *konsep/ide dasar* dari input, tapi buang *implementasi palsu* dan ganti dengan implementasi yang terbukti valid.

## Process (Ikuti Urutan)

### Step 1 — Ekstraksi & Kategorisasi Ide

Baca input user secara keseluruhan. Pisahkan menjadi 3 kategori di dalam pikiran (thought process):
1. **Konsep/Goal Utama:** Apa tujuan akhirnya? (e.g., "Membuat trailing stop", "Menyiapkan HFT backtest").
2. **Klaim Teknis / Syntax:** API atau fungsi spesifik yang disebutkan (e.g., "Gunakan `hftbacktest.run()`").
3. **Arsitektur/Struktur:** Pola desain file & folder yang disarankan.

### Step 2 — Audit Validitas (Fact-Checking)

Sebelum menulis kode atau *plan* final, agen **WAJIB** melakukan investigasi:

- **Jika input membahas library eksternal (Hyperliquid, Pandas, dsb):**
  Gunakan tool `search_web` atau `read_url_content` untuk mencari dokumentasi resmi TERBARU. Cocokkan syntax dari input user dengan dokumentasi asli.
- **Jika input membahas internal arsitektur (Skills, RLM, Switchboard):**
  Gunakan tool `grep_search` atau `list_dir` untuk mengecek direktori project user (contoh: `~/Projects/AI-POWERSETUP`).
- **Jika input menyertakan Code Snippet:**
  Cari apakah ada snippet serupa di project user saat ini. Apakah *function signature*-nya sama?

### Step 3 — Mapping: Fakta vs Halusinasi

Buat daftar internal:
- **✅ Fakta Valid:** Bagian dari input yang setelah di-crosscheck ternyata benar dan bisa dipakai.
- **❌ Halusinasi/Outdated:** Syntax atau asumsi yang salah, usang, atau tidak kompatibel dengan *current environment*.

### Step 4 — Generate Refined Specification

Buat *output* terstruktur untuk disajikan ke user:

1. **Ringkasan Konsep:** Konfirmasi pemahaman tujuan utama.
2. **Analisis Bias/Halusinasi:** Tunjukkan kepada user mana bagian dari input awal yang salah atau tidak bisa diterapkan, dan jelaskan alasannya bedasarkan sumber asli yang baru saja kamu cek.
3. **Verified Action Plan:** Berikan langkah-langkah implementasi (Atau Code Specs) yang sudah 100% diverifikasi, menggunakan tools dan arsitektur yang benar.

## Output Format

```markdown
# 🛡️ Verified Action Plan & Fact Check

## 🎯 Goal
[Ringkasan singkat dari ide/draft asli yang diinginkan user]

## 🚨 Hallucination / Outdated Alert
- ❌ **Klaim di draft:** [Klaim salah]
  ✅ **Fakta sebenarnya:** [Sintaks/cara yang benar berdasarkan dokumentasi/source code]
- ❌ [Klaim salah lainnya]
  ✅ [Fakta sebenarnya]

*(Tampilkan hanya jika ada kesalahan/halusinasi)*

## 🛠️ Verified Technical Strategy
[Penjelasan langkah demi langkah arsitektur atau kode yang SUDAH DIVERIFIKASI dan siap untuk diimplementasikan di environment user saat ini]

## 📝 Rekomendasi Prompt Selanjutnya
[Berikan 1 slash command atau kalimat untuk memulai eksekusi. Contoh: "Ketik `/task Mulai implementasi sesuai Verified Plan` untuk memulai coding."]
```

## Error Handling

- **Sumber tidak bisa diverifikasi (Web diblokir/dokumentasi hilang):** Beritahu user dengan pesan peringatan: "⚠️ *WARNING*: Sebagian ide ini membutuhkan library X, tapi saya tidak bisa menemukan dokumentasi resminya secara online. Implementasi mungkin *trial-and-error*."
- **Input user terlalu abstrak/filosofis:** Minta user memberikan contoh konkret: "Konsep ini bagus, tapi saya butuh contoh use-case spesifik di project ini agar saya bisa memverifikasi *tools* apa yang paling cocok."
