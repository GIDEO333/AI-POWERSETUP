---
name: normalize-input
description: Pre-process user input before any other skill. Fix typos, translate to English, clarify intent. Use automatically on every first message from user, especially when input contains typos, abbreviations, mixed Indonesian-English, or unclear intent.
category: Format
---

# Normalize Input

Pre-processing skill — the FIRST step before any other skill is invoked.

## When to Use

- Automatically on **every first message** from user in a session
- When input contains: typos, abbreviations, mixed Indonesian-English, incomplete sentences, or unclear intent
- Before calling `search_skills` — use the normalized result as query

## Process (execute in order)

### Step 0 — Deteksi Konten AI-Generated (PRIORITY CHECK)

**Sebelum langkah lain**, cek apakah input mengandung salah satu penanda ini:
- Logo/header Perplexity: `perplexity.ai`, `pplx-full-logo`, `<img src="...perplexity..."`
- Footnote format Perplexity: `[^1_1]`, `[^2_3]`, pola `[^N_N]`
- Header section ChatGPT/Claude/AI: `# Pertanyaan kamu masuk ke...`, dokumen markdown panjang dari AI lain
- User menempel konten panjang yang jelas dari AI lain (>500 kata dengan struktur numbered sections)

**Jika terdeteksi:**
→ **STOP. Jangan proses lebih lanjut.**
→ Declare: *"Mendeteksi konten dari AI eksternal — menjalankan `brainstorm-refiner` skill untuk memverifikasi fakta dan syntax sebelum melanjutkan."*
→ Invoke `brainstorm-refiner` skill sebagai prioritas pertama.

**Jika tidak terdeteksi:**
→ Lanjutkan ke Step 1.

### Step 1 — Typo & Grammar Fix

Correct all spelling errors silently. Do NOT mention corrections unless they change meaning.

Examples:
- "langusng" → "langsung"
- "karean" → "karena"
- "buatkan sya" → "buatkan saya"
- "atigravity" → "antigravity"

### Step 2 — Language Normalization (ID → EN)

Translate the corrected input fully to English. Preserve technical terms, code snippets, file names, and proper nouns as-is.

Examples:
- "buatkan fungsi untuk login user" → "create a login function for users"
- "kenapa kode ini error?" → "why is this code throwing an error?"
- "rapikan kode di file auth.py" → "refactor the code in auth.py"

### Step 3 — Intent Clarification

Rewrite as a clear, actionable instruction. Add implied context if obviously missing.

Examples:
- "ini error" → "debug this error and explain the root cause"
- "bikin test" → "write unit tests for the current function"
- "lambat" → "analyze and optimize the performance of this code"

### Step 4 — Output Format

Return ONLY this JSON:

```json
{
  "original": "<raw user input>",
  "normalized": "<clean English result>",
  "corrections": ["typo1 → fix1", "typo2 → fix2"],
  "language_detected": "id | en | mixed",
  "confidence": 0.0-1.0
}
```

## Examples

Input: `"buatkan sya fungsi autentikasi pakek jwt, jangan lupa error handlingnya"`

```json
{
  "original": "buatkan sya fungsi autentikasi pakek jwt, jangan lupa error handlingnya",
  "normalized": "create a JWT authentication function with proper error handling",
  "corrections": ["sya → saya", "pakek → pakai"],
  "language_detected": "mixed",
  "confidence": 0.97
}
```

Input: `"knp si klo deploy ke docker selalu gagal"`

```json
{
  "original": "knp si klo deploy ke docker selalu gagal",
  "normalized": "why does deployment to Docker always fail? debug and provide solution",
  "corrections": ["knp → kenapa", "si → sih", "klo → kalau"],
  "language_detected": "id",
  "confidence": 0.94
}
```

## Integration

After normalization, pass `normalized` value to downstream skills:
- `search_skills(query=normalized)`
- All subsequent LLM calls use `normalized` as the user intent
