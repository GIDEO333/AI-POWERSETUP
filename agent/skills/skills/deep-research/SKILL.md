---
name: deep-research
description: Conduct systematic deep-dive research on any technology by prioritizing
  its official GitHub repository, applying mental models for structured understanding,
  and producing an objective analysis with identified research gaps.
  Invoked when user says "deep dive", "pelajari mendalam", "riset mendalam",
  "analisis teknologi", "research this", "deep research", "pahami arsitektur",
  "cari tau tentang", "investigate", "study documentation".
  Technology research, architecture analysis, security audit, source code analysis.
category: Research
---

# Deep Research Skill

## Kapan Digunakan
- User ingin memahami sebuah teknologi atau library secara mendalam
- User memberikan nama teknologi + URL GitHub resmi sebagai input
- User ingin analisis arsitektur, security model, atau trade-off dari suatu sistem

## Steps

### Step 1 — Collect Input
Kumpulkan dari user (atau infer dari konteks):
- **Nama teknologi** yang akan diteliti
- **URL GitHub resmi** (prioritas tertinggi, wajib ada)
- **Fokus opsional**: security, performance, architecture, comparison

### Step 2 — Fetch Primary Sources (Priority Order)
Fetch dalam urutan ini, jalankan paralel sebanyak mungkin:

1. **GitHub README.md** → Overview, purpose, quick start
   `https://raw.githubusercontent.com/{owner}/{repo}/main/README.md`
2. **GitHub docs/** → Arsitektur, security model, API design
   `https://raw.githubusercontent.com/{owner}/{repo}/main/docs/SECURITY.md` (dan file docs lain)
3. **Source code entry point** → `src/`, `lib/`, atau `index.ts/py`
   `https://github.com/{owner}/{repo}/tree/main/src`
4. **Dockerfile / docker-compose.yml** → Runtime constraints, dependencies
5. **GitHub Issues (open)** → Known bugs, limitations, community feedback
   `https://github.com/{owner}/{repo}/issues`
6. **Web search** → Validasi eksternal, perbandingan, tulisan komunitas (sebagai pelengkap)

### Step 3 — Extract + Validate (Fact vs Unverified)
Dari semua sources, identifikasi dan **pisahkan secara eksplisit**:

**Ekstraksi:**
- **Core problem** yang diselesaikan teknologi ini
- **Architecture decisions** dan alasannya (Why, bukan hanya What)
- **Security model** jika ada (trust boundaries, attack surface)
- **Known limitations** yang diakui maintainer
- **Dependencies** kritis

**Validasi (prinsip dari brainstorm-refiner):**
- **✅ Verified** → Klaim yang bersumber langsung dari GitHub repo resmi, source code aktual, atau official docs.
- **⚠️ Unverified** → Klaim dari web/blog/artikel komunitas yang belum dicocokkan ke primary source.
- **❌ Likely Hallucination** → Syntax, nama fungsi, atau parameter yang *tidak ditemukan* di source code/docs resmi.

> **Prinsip:** Anggap semua klaim dari sumber sekunder (artikel, Medium, Stack Overflow) sebagai *hipotesis* sampai diverifikasi ke primary source (GitHub repo resmi).

### Step 4 — Apply Mental Models
Analisis menggunakan minimal 3 dari 7 mental model berikut (pilih yang paling relevan):

| Model | Pertanyaan Kunci |
|-------|-----------------|
| **First Principles** | Apa masalah fundamental yang dipecahkan? Apakah ini solusi minimal? |
| **Occam's Razor** | Apakah ini solusi paling sederhana? Atau ada overhead yang tidak perlu? |
| **Second-Order Thinking** | Apa konsekuensi dari konsekuensi keputusan ini? |
| **Pre-Mortem** | Jika sistem ini gagal, bagaimana skenario kegagalannya? |
| **MECE** | Apakah boundary sistem ini lengkap dan tidak tumpang tindih? |
| **First Mover vs Fast Follower** | Apakah solusi ini pioneer atau perbaikan dari yang ada? |
| **Inversion** | Apa yang harus TIDAK dilakukan agar sistem ini berhasil? |

### Step 5 — Objective Self-Critique
Setelah analisis selesai, lakukan kritik terhadap analisis sendiri:
- **Coverage**: Data source apa yang belum dibaca?
- **Assumptions**: Asumsi apa yang belum tervalidasi?
- **Bias**: Apakah ada framing yang terlalu positif/negatif?
- **Score**: Berikan skor objektif 1-10 dengan justifikasi

### Step 6 — Identify Research Gaps
Buat daftar terstruktur pencarian lanjutan yang masih diperlukan:
- 🔴 **Prioritas Tinggi** → Gap kritis yang mempengaruhi keamanan/keputusan
- 🟡 **Prioritas Menengah** → Memperdalam pemahaman
- 🟢 **Prioritas Rendah** → Nice-to-know

## Output Format
Output harus berisi 6 bagian:
1. **Overview** — 3 kalimat: apa, untuk siapa, masalah yang diselesaikan
2. **Mental Model Analysis** — Minimal 3 model, masing-masing dengan temuan konkret
3. **Key Findings** — Bullet points: architecture decisions, gotchas, limitations
4. **Fact Check Report** — Dua kolom: ✅ Verified (primary source) vs ⚠️/❌ Unverified/Hallucination
5. **Objective Critique** — Penilaian jujur terhadap analisis + skor 1-10
6. **Research Gaps** — Daftar terstruktur dengan prioritas (🔴🟡🟢)

> **Komposisi:** Jika user membawa dump dari AI lain (ChatGPT/Perplexity) tentang topik yang sama, gunakan `brainstorm-refiner` untuk memproses dump tersebut, lalu gunakan output `deep-research` sebagai *ground truth* untuk verifikasi.

## Error Handling
- **GitHub repo tidak ditemukan**: Fallback ke web search + official docs website
- **README sangat pendek (< 50 baris)**: Langsung ke source code — README belum lengkap
- **Source code terlalu besar**: Prioritaskan entry point, `index`, atau file terbesar
- **Tidak ada URL resmi**: Tanya user sebelum mulai — riset tanpa primary source tidak valid
