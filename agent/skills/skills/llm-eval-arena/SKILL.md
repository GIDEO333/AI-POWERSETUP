---
name: llm-eval-arena
description: Evaluate and rank multiple mental models or context engineering strategies on any prompt using agent-native LLM-as-judge scoring E(A) = Σ wᵢ fᵢ(A). Zero API key, zero external script — the agent generates AND scores all outputs directly.
  Invoked when user says "bandingkan mental model", "mental model mana terbaik",
  "eval arena", "llm eval arena", "test context strategy", "ranking prompt strategy",
  "uji mental model", "mana yang lebih bagus", "compare reasoning strategy",
  "jalankan eval", "scoring mental model", "context engineering benchmark".
category: QA
---

# LLM Eval Arena — Agent-Native Mental Model Benchmark

## Kapan Digunakan

- User ingin tahu mental model mana yang menghasilkan output terbaik untuk suatu pertanyaan
- User ingin membandingkan context engineering strategies secara objektif dan deterministik
- User ingin menjalankan evaluasi LLM **tanpa API key / library eksternal** — cukup via chat

## Prinsip Inti

Agent bertindak sebagai **generator sekaligus judge**:
1. **Generate:** Jawab prompt dengan setiap mental model sebagai system context
2. **Score:** Evaluasi setiap jawaban menggunakan 4 kriteria formal
3. **Rank:** Hitung E(A) = Σ wᵢ fᵢ(A) dan tampilkan ranking

Tidak ada API call eksternal. Tidak ada script Python. Agent = executor + evaluator.

## Default Mental Models (bisa diganti user)

| ID | Nama | System Context | Fungsi |
|----|------|----------------|--------|
| M1 | Chain of Thought | "Think step-by-step. Break into sub-problems, solve each, synthesize." | SOP / Eksekusi |
| M2 | First Principles | "Deconstruct to axioms only. Ignore assumptions. Build reasoning upward." | Fondasi / Simplifikasi |
| M3 | Inversion | "Invert: ask what causes failure first. Reason backward to solution." | Risk Detection |
| M4 | MECE | "Structure using Mutually Exclusive Collectively Exhaustive categories." | Coverage / Pemetaan |
| M5 | Second-Order Thinking | "Don't stop at the first consequence. Ask 'And then what?' repeatedly. Map cascading effects." | Dampak Jangka Panjang |
| M6 | Pre-Mortem | "Imagine we already implemented this and it FAILED 6 months later. Reconstruct the failure timeline." | Failure Narrative |
| M7 | Occam's Razor | "From all possible solutions, choose the simplest one that still solves the core problem. Eliminate unnecessary complexity." | Pengerem / Anti Over-Engineering |

## Evaluation Criteria & Weights

| Kriteria | Bobot (wᵢ) | Definisi |
|----------|------------|---------|
| LogicalConsistency (C) | 0.30 | Bebas kontradiksi internal |
| DeductiveValidity (V) | 0.25 | Setiap langkah valid dari premis |
| InformationEfficiency (I) | 0.25 | Informatif tanpa redundansi |
| Coherence (K) | 0.20 | Struktur mengalir logis, tanpa lompatan |

**Formula:** `E(A) = 0.30·C + 0.25·V + 0.25·I + 0.20·K` (skala 0.0–1.0)

## Steps

### Step 1 — Klarifikasi Input

Pastikan user sudah berikan **prompt/pertanyaan** yang ingin diuji.
Jika belum, tanya: *"Pertanyaan apa yang ingin kamu bandingkan antar mental model?"*

Tanya juga apakah user ingin **custom mental model** atau pakai default (M1–M7).

### Step 2 — Generate Jawaban per Mental Model

Untuk setiap mental model, jawab prompt dengan **mengadopsi system context** tersebut secara eksplisit. Format:

```
## [M1] Chain of Thought
[Jawaban dengan gaya CoT]

## [M2] First Principles
[Jawaban dengan gaya First Principles]
...
```

Tandai dengan header jelas agar mudah dibedakan saat scoring.

### Step 3 — Score Setiap Jawaban

Untuk setiap jawaban, evaluasi 4 kriteria secara independen (skala 0.0–1.0):

- **C (LogicalConsistency):** Apakah ada kontradiksi internal antara klaim?
- **V (DeductiveValidity):** Apakah kesimpulan benar-benar follow dari argumen?
- **I (InformationEfficiency):** Apakah kalimat-kalimatnya padat informasi atau boros?
- **K (Coherence):** Apakah alurnya mengalir dari awal ke akhir tanpa lompatan?

Berikan justifikasi 1 kalimat per kriteria, lalu skor numerik.

### Step 4 — Hitung E(A) dan Tampilkan Ranking

Hitung: `E(A) = 0.30·C + 0.25·V + 0.25·I + 0.20·K`

Tampilkan tabel final:

```
📊 RANKING MENTAL MODELS (7 Perspectives)
═══════════════════════════════════════════════════════════════
Mental Model          C     V     I     K    E(A)   Verdict
──────────────────────────────────────────────────────────────
First_Principles      0.91  0.88  0.85  0.90  0.888  🥇
Pre_Mortem            0.89  0.87  0.86  0.88  0.876  🥈
Chain_of_Thought      0.87  0.90  0.80  0.86  0.859  🥉
Second_Order          0.85  0.84  0.83  0.87  0.848
MECE                  0.83  0.82  0.88  0.84  0.843
Occams_Razor          0.82  0.80  0.91  0.83  0.841
Inversion             0.74  0.71  0.81  0.78  0.762
═══════════════════════════════════════════════════════════════
Winner: [Nama mental model] dengan E(A) = X.XXX
Insight: [1 kalimat kenapa mental model ini menang untuk prompt ini]
```

### Step 5 — Insight (Proaktif)

Tambahkan 2–3 kalimat insight:
- Kenapa pemenang unggul untuk konteks prompt ini?
- Kapan runner-up lebih baik dipakai?
- Rekomendasi: mental model mana untuk task serupa ke depannya?

## Common Patterns

- Prompt teknis/analitis → First Principles biasanya unggul di V
- Prompt kreatif/open-ended → CoT biasanya unggul di K
- Prompt problem-solving → Inversion sering unggul di I
- Prompt comprehensive/audit → MECE unggul di coverage
- Prompt strategis / long-term → Second-Order Thinking unggul di cascading effects
- Prompt arsitektur / pre-build → Pre-Mortem unggul di failure detection
- Prompt yg cenderung over-engineered → Occam's Razor unggul sebagai pengerem kompleksitas

## Error Handling

- **User tidak kasih prompt:** Tanya dulu, jangan generate dummy
- **User minta custom mental model:** Tambahkan ke tabel, skor dengan kriteria sama
- **Skor subyektif / user ragu:** Jelaskan bahwa E(A) = guided LLM judgment, bukan oracle — bisa diulang 3x lalu rata-rata untuk distribusi lebih stabil
- **Prompt terlalu pendek/ambigu:** Minta user perjelas sebelum mulai, karena kualitas prompt mempengaruhi validitas perbandingan
