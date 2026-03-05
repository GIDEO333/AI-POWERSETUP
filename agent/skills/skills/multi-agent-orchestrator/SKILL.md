---
name: multi-agent-orchestrator
description: Template framework Shell-script (Bash) untuk merancang orkestrasi serah terima estafet multi-agent berbasis profil JSON, memisahkan agen Pemikir, Pekerja, dan Penguji secara rapi.
category: AI-Orchestration
---

# Multi-Agent Orchestrator Framework

## Tujuan
Memisahkan sistem dari desain *monolithic agent* (satu AI mengerjakan semua dari awal hingga akhir) menuju perakitan *pipeline* estafet multi-agent, di mana setiap bot memiliki *constraint* spesifik.

## Komponen Meta-Architektur (Universal)

Arsitektur ini dapat digunakan terlepas dari apakah agen CLI yang dipakai adalah Claude Code, Aider, atau kustom skrip Python yang memanggil OpenAI API. Syarat satu-satunya: **Sistem harus berorientasi pada Artefak (*Artifact-driven*)**.

### 1. The Architect (Sang Pemikir)
- **Tugas:** Menganalisa *source_seed*, melakukan *root cause analysis*, lalu memecah solusi menjadi perintah imperatif yang mutlak dan kaku.
- **Output:** Menghasilkan dokumen Markdown perencanaan contoh: `architecture_plan.md`. Tidak pernah menyentuh *source code* sasaran secara langsung.

### 2. The Worker (Sang Kuli)
- **Tugas:** Mesin pengetik. Ia dipanggil secara "Headless" untuk memakan *output* dari Sang Pemikir (`architecture_plan.md`).
- **Prinsip Utama:** Ia tidak perlu paham konteks bisnis, dilarang menjalankan *test suite*, dan dipaksa untuk *exit* (mati) secepat mungkin segera setelah ia berhasil melakukan penyuntingan *file*.

### 3. The QA Tester (Sang Penjamin)
- **Tugas:** Ia dipanggil SETELAH Kuli selesai dan mati. Ia membaca `architecture_plan.md` pada bagian verifikasi, dan satu-satunya tugasnya adalah memanggil linter/unit test.
- **Prinsip Utama:** Ia diizinkan membaca *log error*, namun DILARANG MEMPERBAIKI KODE. Ia hanya bertugas merangkum *error* yang ditemukan ke dalam `qa_report.md` untuk diumpankan kembali ke The Architect di putaran selanjutnya.

## Desain Skrip Manager (The Handoff)
Orkestrasi selalu diikat oleh satu skrip koordinator `manager.sh` yang melakukan modifikasi pada file profil agen (menukar "otak" si agen):

```bash
# Ilustrasi Logika Universal
cp .configs/worker_brain.json .agent_config
ai-cli "Execute $PLAN"

cp .configs/qa_brain.json .agent_config
ai-cli "Verify and run test suite"
```
