---
name: query-scorecard
description: Analisa dan skor performa AI per query dalam satu sesi chat — bandingkan model, mode, dan efisiensi tool calls / Score AI performance per query in a chat session — compare models, modes, and tool call efficiency.
  Invoked when user says "analisa performa AI", "skor query", "evaluasi sesi",
  "query scorecard", "mana yang pintar mana yang bodoh", "review AI performance",
  "bandingkan model per query", "session review", "eval AI di sesi ini".
category: QA
---

# Query Scorecard — Per-Query AI Performance Analyzer

## Kapan Digunakan

- User ingin tahu query mana yang dijawab dengan pintar vs bodoh/sia-sia
- User pakai beberapa model/mode berbeda dalam satu sesi dan ingin bandingkan
- User bilang "analisa performa", "skor query", "review sesi AI", "evaluasi"
- Setelah sesi debugging panjang untuk post-mortem efisiensi

## Scoring Criteria (4 Dimensi)

| Dimensi | Bobot | Skala | Definisi |
|---------|-------|-------|----------|
| **Speed** | 0.20 | ⭐1-5 | Berapa tool call untuk menjawab? (5=0-1 call, 1=10+ call) |
| **Accuracy** | 0.35 | ⭐1-5 | Apakah jawaban/fix-nya benar dan tepat sasaran? |
| **Efficiency** | 0.25 | ⭐1-5 | Ada tool call sia-sia atau redundan? (5=0 waste, 1=mayoritas waste) |
| **Communication** | 0.20 | ⭐1-5 | Apakah AI menjelaskan dengan jelas, tidak bertele-tele? |

**Formula:** `S(Q) = 0.20·Speed + 0.35·Accuracy + 0.25·Efficiency + 0.20·Communication`

## Steps

### Step 1 — Kumpulkan Data Sesi

Dari conversation history, ekstrak untuk setiap query:
1. **Step ID** dari metadata
2. **Query text** (kutip persis dari user)
3. **Model** yang digunakan (dari `USER_SETTINGS_CHANGE` events)
4. **Mode** (Planning ON/OFF, dari setting changes)
5. **Jumlah tool calls** yang dieksekusi sebagai respons
6. **Hasil** (berhasil / gagal / parsial)

### Step 2 — Skor Setiap Query

Untuk setiap query, berikan rating ⭐1-5 per dimensi dengan justifikasi 1 kalimat:

```
Query #4: "coba cek lagi"
- Speed:         ⭐5 — 1 command langsung dapat hasil
- Accuracy:      ⭐5 — Langsung temukan container crash-looping
- Efficiency:    ⭐5 — Tidak ada tool call sia-sia
- Communication: ⭐5 — Penjelasan langsung, terstruktur
- S(Q) = 5.0
```

### Step 3 — Aggregate per Model+Mode

Hitung rata-rata S(Q) per kombinasi model + mode:

```
📊 AGGREGATE SCORECARD
═══════════════════════════════════════════
Combo              Queries  Avg S(Q)  Verdict
───────────────────────────────────────────
Model B + Plan ON     5       4.2     🏆 Best
Model A + Plan OFF    2       4.9     ⚡ Fast
Model A + Plan ON     3       3.9     📊 Mixed
Model B + Plan OFF    2       1.0     ❌ Worst
═══════════════════════════════════════════
```

### Step 4 — Generate Output

Tampilkan 3 bagian:

**Bagian 1:** Tabel per-query lengkap (Step | Query | Model | Mode | Spd | Acc | Eff | Com | S(Q))

**Bagian 2:** Tabel aggregate per model+mode combo

**Bagian 3:** Insight & rekomendasi:
- Model+mode mana terbaik untuk task type apa?
- Pola pemborosan yang terdeteksi
- Rekomendasi setting untuk sesi berikutnya

## Contoh Output

**Input:** "analisa performa AI di sesi ini"

**Output (ringkas):**

```
🎯 QUERY SCORECARD — Sesi Debug OverlayFS
══════════════════════════════════════════════════════════════
#  Query (ringkas)         Model  Mode      Spd Acc Eff Com S(Q)
── ─────────────────────── ────── ───────── ─── ─── ─── ─── ────
1  INI KENAPA JELASKAN     A      Plan ON    5   4   5   4  4.5
2  pakai orbstack bisa?    A      Plan ON    2   3   1   3  2.3
3  looping                 A      Plan ON    5   5   5   4  4.8
4  coba cek lagi           B      Plan ON    5   5   5   5  5.0
5  penyebab masalahnya?    B      Plan ON    5   5   5   5  5.0
9  sudah diperbaiki?       B      Plan OFF   1   1   1   1  1.0
══════════════════════════════════════════════════════════════

🏆 Best Combo:  Model B + Planning ON  (avg 4.2)
❌ Worst Combo: Model B + Planning OFF (avg 1.0)

💡 Insight: Planning mode membantu Model B tetap terstruktur.
   Tanpa planning, Model B kehilangan konteks dan hang.
```

## Behavioral Rules

1. Skor HARUS jujur — jangan inflate score untuk menyenangkan user
2. Jika query user ambigu (misal "ya"), skor berdasarkan RESPONS AI, bukan query
3. Jika model name di-mask (PLACEHOLDER), label sebagai Model A/B/C secara konsisten
4. Simpan scorecard sebagai artifact `.md` agar bisa direferensi di sesi berikutnya

## Error Handling

- **Sesi terlalu pendek (< 3 query):** Tetap jalankan, tapi tambahkan disclaimer bahwa sample size kecil
- **Tidak ada model switch:** Tetap skor per-query, skip bagian aggregate comparison
- **User tidak ingat model mana:** Gunakan label Model A/B/C dari `USER_SETTINGS_CHANGE` metadata
- **Query yang di-cancel user:** Tetap masukkan dengan catatan "cancelled by user", skor Accuracy = N/A
