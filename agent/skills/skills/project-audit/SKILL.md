---
name: project-audit
description: Generate comprehensive project architecture audit, deep-dive documentation, vulnerability scan, and scale-up analysis. Buat laporan lengkap arsitektur project untuk di-review oleh LLM lain, security audit, atau planning scale-up. Audit keamanan, architecture review, system documentation.
category: QA
---

# Project Audit — Deep Dive Generator

## Kapan Digunakan

- User minta audit arsitektur, deep-dive, atau vulnerability check
- User mau bawa dokumentasi ke LLM lain untuk second opinion
- User mau scale-up dan butuh peta lengkap state sekarang
- User minta generate documentation otomatis

## Steps

1. **Scan struktur project** — `find` dan `ls` semua file, folder, config di project root
2. **Baca setiap config file** — parse dan dokumentasikan settings (JSON, YAML, .env, shell)
3. **Identifikasi komponen** — MCP servers, scripts, skills, workflows, dependencies
4. **Analisis alur data** — gambar arsitektur diagram dalam ASCII art atau Mermaid
5. **Cek API & dependencies** — endpoint, billing model, quota, versi library
6. **Hitung resource usage** — token budget, RAM footprint, jumlah proses aktif
7. **Scan vulnerability**:
   - Hardcoded secrets atau API keys di source code
   - Exposed ports atau endpoints tanpa auth
   - Missing input validation
   - Dependencies dengan known CVE
   - File permissions yang terlalu loose
8. **Identifikasi scale-up opportunities** — bottleneck, improvement areas, roadmap
9. **Generate output** dalam format markdown self-contained

## Output Format (Wajib)

Output HARUS self-contained agar bisa langsung di-copy-paste ke LLM lain:

```
# Project Audit: [Nama Project]
Generated: [tanggal & waktu]

## 1. Arsitektur
(ASCII diagram alur data antar komponen)

## 2. Directory Map
(tree lengkap dengan penjelasan tiap file penting)

## 3. Code Deep Dive
(pseudo-code atau summary setiap komponen utama)

## 4. API & Dependencies
(endpoints, billing, quota, library versions)

## 5. Performance & Resource
(token budget, RAM, proses count, latency)

## 6. Security Checklist
⚠️ (daftar temuan vulnerability jika ada)
✅ (daftar yang sudah aman)

## 7. Scale-Up Roadmap
(saran improvement: short/medium/long term)
```

## Prinsip

- **Self-contained** — LLM lain harus bisa paham tanpa akses ke file asli
- **Real-time** — SELALU scan file system saat generate, JANGAN pakai cached data
- **Adaptif** — sesuaikan fokus berdasarkan permintaan user:
  - "audit security" → fokus ke §6
  - "audit performance" → fokus ke §5
  - "audit lengkap" → semua section
- **Actionable** — setiap temuan harus punya saran perbaikan konkret
- **Include code snippets** yang relevan agar reviewer paham context
